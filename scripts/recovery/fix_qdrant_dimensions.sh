#!/bin/bash
# fix_qdrant_dimensions.sh - Reconstruct Qdrant with correct 384 dimensions
# Purpose: Delete incompatible collections (768 dims) and recreate with 384 dims
# Impact: This will DELETE all data in: omnimind_consciousness, omnimind_episodes, omnimind_narratives, omnimind_memories

set -e

echo "🔧 OmniMind Qdrant Dimension Fix"
echo "=================================="
echo ""
echo "⚠️  DANGER: This script will DELETE existing collections with incorrect dimensions!"
echo "   Collections to be deleted and recreated:"
echo "      • omnimind_consciousness (768→384 dims)"
echo "      • omnimind_episodes (768→384 dims)"
echo "      • omnimind_narratives (768→384 dims)"
echo "      • omnimind_memories (768→384 dims)"
echo ""
echo "   Collections with correct dims (384) will be preserved:"
echo "      • omnimind_embeddings"
echo "      • omnimind_system"
echo "      • orchestrator_semantic_cache"
echo ""

# Ask for confirmation
read -p "Continue? Type 'yes' to proceed: " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ Aborted."
    exit 1
fi

echo ""
echo "📋 Step 1: Checking Qdrant connectivity..."

# Start Qdrant if not running
if ! docker ps | grep -q qdrant; then
    echo "⏳ Starting Qdrant container..."
    docker-compose -f deploy/docker-compose.yml up -d qdrant 2>/dev/null || {
        echo "⚠️  docker-compose failed. Trying direct docker..."
        docker run -d \
            --name qdrant \
            -p 6333:6333 \
            -v /home/fahbrain/projects/omnimind/data/qdrant:/qdrant/storage \
            qdrant/qdrant:latest 2>/dev/null || {
            echo "❌ Failed to start Qdrant"
            exit 1
        }
    }
    sleep 3
fi

# Test connection
if ! curl -s http://localhost:6333/health | grep -q "ok"; then
    echo "❌ Qdrant not responding at http://localhost:6333"
    exit 1
fi

echo "✅ Qdrant is running"
echo ""

# Create Python script to fix dimensions
cat > /tmp/fix_qdrant.py << 'PYTHON_SCRIPT'
#!/usr/bin/env python3
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

try:
    client = QdrantClient(url="http://localhost:6333")

    # Collections with WRONG dimensions (768 -> 384)
    WRONG_DIMS = {
        "omnimind_consciousness": 768,
        "omnimind_episodes": 768,
        "omnimind_narratives": 768,
        "omnimind_memories": 768,
    }

    # Collections with CORRECT dimensions (keep as is)
    CORRECT_DIMS = {
        "omnimind_embeddings": 384,
        "omnimind_system": 384,
        "orchestrator_semantic_cache": 384,
    }

    print("📊 Current collections:")
    collections = client.get_collections()
    for coll in collections.collections:
        info = client.get_collection(coll.name)
        vector_size = info.config.params.vectors.size if hasattr(info.config.params, 'vectors') else "?"
        print(f"   • {coll.name}: {info.points_count} points, {vector_size} dims")

    print("\n🗑️  Deleting collections with wrong dimensions...")

    for name in WRONG_DIMS:
        try:
            client.delete_collection(name)
            print(f"   ✅ Deleted: {name} (was {WRONG_DIMS[name]} dims)")
        except Exception as e:
            print(f"   ⚠️  {name}: {e}")

    print("\n🔨 Recreating with correct 384 dimensions...")

    # Recreate with 384 dims
    for name in WRONG_DIMS:
        try:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=384,  # Correct dimension
                    distance=Distance.COSINE
                ),
            )
            print(f"   ✅ Created: {name} (384 dims)")
        except Exception as e:
            print(f"   ❌ Failed to create {name}: {e}")
            sys.exit(1)

    print("\n✅ Verifying all collections...")
    collections = client.get_collections()
    for coll in collections.collections:
        info = client.get_collection(coll.name)
        vector_size = info.config.params.vectors.size if hasattr(info.config.params, 'vectors') else "?"
        print(f"   • {coll.name}: {info.points_count} points, {vector_size} dims")

    print("\n✅ Dimension fix complete!")
    print("   Next: Restart OmniMind services")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo "📊 Step 2: Fixing Qdrant dimensions..."
python3 /tmp/fix_qdrant.py

if [ $? -ne 0 ]; then
    echo "❌ Dimension fix failed"
    exit 1
fi

echo ""
echo "🎉 SUCCESS!"
echo "=================================="
echo "Next steps:"
echo "  1. Verify Qdrant status: curl http://localhost:6333/health"
echo "  2. Restart OmniMind: sudo systemctl restart omnimind-backend"
echo "  3. Check logs: tail -f /var/log/omnimind/omnimind.log"
echo "  4. Run tests: ./scripts/run_tests_parallel.sh smoke"

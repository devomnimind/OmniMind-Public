#!/bin/bash

# 📋 STEP 1: Initialize Qdrant Collections
# Cria todas as 7 coleções necessárias para o OmniMind
# Status: READY FOR EXECUTION

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
PYTHON_CMD="python3"

echo -e "\033[0;36m📋 Step 1: Initialize Qdrant Collections\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

# Verify Qdrant is running
echo "Checking Qdrant..."
if ! curl -s --max-time 2 http://localhost:6333/healthz > /dev/null 2>&1; then
    echo -e "\033[0;31m❌ Qdrant not running. Start it with:\033[0m"
    echo "   docker-compose -f $PROJECT_ROOT/deploy/docker-compose.yml up -d qdrant"
    exit 1
fi
echo -e "\033[0;32m✅ Qdrant is running\033[0m"
echo ""

# Execute Python script
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

$PYTHON_CMD << 'PYTHON_END'
import sys
sys.path.insert(0, "/home/fahbrain/projects/omnimind/src")
sys.path.insert(0, "/home/fahbrain/projects/omnimind")

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

client = QdrantClient(url="http://localhost:6333")

# Define all 7 collections
# CRÍTICO: All use 384 dims para ser consistente com all-MiniLM-L6-v2
COLLECTIONS = {
    "omnimind_consciousness": {
        "vector_size": 384,  # Atualizado: consistent com embedding model
        "distance": Distance.COSINE,
        "description": "Consciência e estados mentais"
    },
    "omnimind_episodes": {
        "vector_size": 384,  # Atualizado: consistent com embedding model (estava 768)
        "distance": Distance.COSINE,
        "description": "Memória episódica"
    },
    "omnimind_embeddings": {
        "vector_size": 384,
        "distance": Distance.COSINE,
        "description": "Embeddings de código (all-MiniLM-L6-v2)"
    },
    "omnimind_narratives": {
        "vector_size": 384,  # Atualizado: consistent com embedding model (estava 768)
        "distance": Distance.COSINE,
        "description": "Narrativas e histórias"
    },
    "omnimind_system": {
        "vector_size": 384,
        "distance": Distance.COSINE,
        "description": "Metadados do sistema"
    },
    "omnimind_memories": {
        "vector_size": 384,  # Atualizado: consistent com embedding model (estava 768)
        "distance": Distance.COSINE,
        "description": "Memórias gerais"
    },
    "orchestrator_semantic_cache": {
        "vector_size": 384,
        "distance": Distance.COSINE,
        "description": "Cache semântico do orchestrator"
    }
}

print("🚀 Creating Qdrant collections...\n")

for name, config in COLLECTIONS.items():
    try:
        # Check if collection exists
        existing = client.get_collections()
        exists = any(c.name == name for c in existing.collections)

        if exists:
            print(f"✅ {name}: Already exists")
        else:
            # Create collection
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=config["vector_size"],
                    distance=config["distance"]
                ),
            )
            print(f"✅ {name}: Created ({config['vector_size']} dims, {config['description']})")
    except Exception as e:
        print(f"⚠️  {name}: {e}")

print("\n✅ All collections initialized!")
print("\n📊 Final status:")
collections = client.get_collections()
for coll in collections.collections:
    try:
        info = client.get_collection(coll.name)
        print(f"   • {coll.name}: {info.points_count} vectors")
    except:
        pass

PYTHON_END

echo ""
echo -e "\033[0;32m✅ Step 1 Complete: Qdrant collections ready\033[0m"
echo ""

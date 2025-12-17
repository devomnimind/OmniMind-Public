#!/bin/bash

# 🎓 STEP 2: Train Embeddings (44k vectors)
# Indexa todo o código do sistema e treina embeddings
# Status: READY FOR EXECUTION

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
PYTHON_CMD="python3"

echo -e "\033[0;36m🎓 Step 2: Train Embeddings (44k vectors)\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

# Set CUDA environment
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"
export TORCH_USE_CUDA_DSA=1
export CUDA_LAUNCH_BLOCKING=1
export PYTORCH_DISABLE_DYNAMO=1

echo "🎯 Configuration:"
echo "   • Project: $PROJECT_ROOT"
echo "   • GPU: CUDA_LAUNCH_BLOCKING=1"
echo "   • Batch size: 64"
echo "   • Workers: 2"
echo ""

# Run indexing
export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_ROOT/logs/indexing/train_embeddings_${TIMESTAMP}.log"

mkdir -p "$PROJECT_ROOT/logs/indexing"

echo "📊 Training embeddings (logging to $LOG_FILE)..."
echo ""

$PYTHON_CMD << 'PYTHON_END'
import sys
import os
from pathlib import Path

# Setup path
PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Import embedding system
from embeddings.code_embeddings import OmniMindEmbeddings

# Initialize
logger.info("Initializing embedding system...")
embeddings = OmniMindEmbeddings(
    qdrant_url="http://localhost:6333",
    collection_name="omnimind_embeddings",
    gpu_memory_threshold_mb=1000,
    batch_size_embeddings=64,
    enable_async_execution=True,
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

logger.info("Starting system indexing...")

# Index all source code
def index_directory(root_path, max_files=None, description=""):
    total_chunks = 0
    files_processed = 0

    if not os.path.exists(root_path):
        logger.warning(f"Path not found: {root_path}")
        return 0

    logger.info(f"Indexing {description}: {root_path}")

    for root, dirs, files in os.walk(root_path):
        # Skip excluded dirs
        dirs[:] = [d for d in dirs if d not in [
            'node_modules', '__pycache__', '.git', '.vscode', '.idea',
            'cache', 'caches', '.cache', '.pytest_cache', '.mypy_cache',
            '.venv', 'venv', 'env', '.env', '.virtualenv'
        ]]

        for file in files:
            if max_files and files_processed >= max_files:
                break

            filepath = os.path.join(root, file)

            # Skip large files
            try:
                if os.path.getsize(filepath) > 100 * 1024 * 1024:  # 100MB
                    continue
            except:
                continue

            # Skip binary files
            if filepath.endswith(('.pyc', '.pyo', '.so', '.o', '.exe', '.bin', '.jar', '.class')):
                continue

            try:
                chunks = embeddings.index_file(filepath)
                total_chunks += chunks
                files_processed += 1

                if files_processed % 100 == 0:
                    logger.info(f"  Progress: {files_processed} files, {total_chunks} chunks")
            except Exception as e:
                logger.debug(f"  Skipped {filepath}: {e}")
                continue

    logger.info(f"✅ {description}: {files_processed} files, {total_chunks} chunks")
    return total_chunks

# Index main areas
areas = [
    (str(PROJECT_ROOT / "src"), None, "Source Code"),
    (str(PROJECT_ROOT / "tests"), None, "Tests"),
    (str(PROJECT_ROOT / "scripts"), None, "Scripts"),
    (str(PROJECT_ROOT / "config"), None, "Config"),
    (str(PROJECT_ROOT / "docs"), None, "Documentation"),
]

total_all_chunks = 0
for path, max_files, desc in areas:
    try:
        chunks = index_directory(path, max_files, desc)
        total_all_chunks += chunks
    except Exception as e:
        logger.error(f"Error indexing {desc}: {e}")

logger.info(f"\n✅ INDEXING COMPLETE: {total_all_chunks} total chunks trained")

# Verify collection
from qdrant_client import QdrantClient
client = QdrantClient(url="http://localhost:6333")
info = client.get_collection("omnimind_embeddings")
logger.info(f"📊 Qdrant omnimind_embeddings: {info.points_count} vectors")

PYTHON_END

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m✅ Step 2 Complete: Embeddings trained\033[0m"
    echo ""
else
    echo ""
    echo -e "\033[0;31m❌ Step 2 Failed (exit code: $EXIT_CODE)\033[0m"
    echo ""
    exit 1
fi

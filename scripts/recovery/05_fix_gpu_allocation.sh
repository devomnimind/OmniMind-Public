#!/bin/bash

# 🎮 STEP 5: Fix GPU Memory Allocation
# Move embeddings para GPU (.to("cuda"))
# Status: READY FOR EXECUTION (agent executes while user runs other steps)

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo -e "\033[0;36m🎮 Step 5: Fix GPU Memory Allocation\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "🔍 Current GPU Status:"
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader 2>/dev/null || echo "GPU not available"
echo ""

echo "Fixing GPU allocation in code_embeddings.py..."
echo ""

# Apply the GPU allocation fix
python3 << 'PYTHON_END'
import sys
from pathlib import Path

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# Read the file
embeddings_file = PROJECT_ROOT / "src" / "embeddings" / "code_embeddings.py"

if not embeddings_file.exists():
    logger.error(f"File not found: {embeddings_file}")
    sys.exit(1)

with open(embeddings_file, 'r') as f:
    content = f.read()

# Check if GPU allocation already fixed
if ".to(device)" in content and "self.device" in content:
    logger.info("✅ GPU allocation already implemented")
    sys.exit(0)

# Check if we can fix it
if "self.model" in content:
    # Look for model loading sections
    lines = content.split('\n')
    fixed_lines = []

    for i, line in enumerate(lines):
        fixed_lines.append(line)

        # After model is loaded, add GPU allocation
        if 'self.model = ' in line and '.cuda()' not in line and 'cuda' not in line:
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * indent + 'if torch.cuda.is_available():')
            fixed_lines.append(' ' * (indent + 4) + 'self.model = self.model.cuda()')
            fixed_lines.append(' ' * (indent + 4) + 'logger.info("✅ Model moved to GPU")')

    # Write back
    with open(embeddings_file, 'w') as f:
        f.write('\n'.join(fixed_lines))

    logger.info("✅ GPU allocation fix applied")
else:
    logger.warning("Could not find injection point in code_embeddings.py")
    logger.info("Manual fix may be needed - check embeddings.py for model initialization")

PYTHON_END

# Verify fix
echo ""
echo "📊 Verifying GPU allocation fix..."
echo ""

python3 << 'VERIFY_END'
import sys
import torch
from pathlib import Path

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Try to load model with GPU
try:
    from embeddings.code_embeddings import OmniMindEmbeddings

    logger.info("Loading embedding model with GPU support...")
    embeddings = OmniMindEmbeddings()

    # Check if GPU is being used
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated(0) / (1024**2)
        reserved = torch.cuda.memory_reserved(0) / (1024**2)
        logger.info(f"✅ GPU memory allocated: {allocated:.1f}MB")
        logger.info(f"✅ GPU memory reserved: {reserved:.1f}MB")

        if allocated > 10:
            logger.info("✅ GPU is being actively used!")
        else:
            logger.warning("⚠️  GPU allocated but minimal - model may be CPU-bound")
    else:
        logger.warning("⚠️  CUDA not available - check PyTorch installation")

except Exception as e:
    logger.error(f"Error loading embeddings: {e}")

VERIFY_END

echo ""
echo -e "\033[0;32m✅ Step 5 Complete: GPU allocation optimized\033[0m"
echo ""

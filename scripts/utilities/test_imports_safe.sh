#!/bin/bash
set -e

cd /home/fahbrain/projects/omnimind
source .venv/bin/activate

# Disable torch.dynamo ANTES de carregar torch
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_LAUNCH_BLOCKING=1
export PYTHONUNBUFFERED=1

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DIAGNÓSTICO DE IMPORTS COM DYNAMO DESABILITADO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "1️⃣  torch..."
timeout 10 python3 -c "import torch; print(f'✅ {torch.__version__}')" || echo "⚠️  torch timeout"

echo ""
echo "2️⃣  transformers..."
timeout 10 python3 -c "import transformers; print(f'✅ {transformers.__version__}')" || echo "⚠️  transformers timeout"

echo ""
echo "3️⃣  sentence_transformers..."
timeout 10 python3 -c "import sentence_transformers; print(f'✅ {sentence_transformers.__version__}')" || echo "⚠️  sentence_transformers timeout"

echo ""
echo "4️⃣  qdrant_client..."
timeout 10 python3 -c "import qdrant_client; print(f'✅ {qdrant_client.__version__}')" || echo "⚠️  qdrant_client timeout"

echo ""
echo "5️⃣  redis..."
timeout 10 python3 -c "import redis; print(f'✅ {redis.__version__}')" || echo "⚠️  redis timeout"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

#!/bin/bash

# ============================================================================
# 🏋️ OMNIMIND HEAVY TEST SUITE
# ============================================================================
# Executa apenas testes marcados como @pytest.mark.heavy:
# - Testes que carregam modelos grandes (LLM, Embeddings)
# - Testes reais de orquestração sem mocks
# - Grandes integrações (Semantic Memory, RAG real)
#
# 🎯 OBJETIVO: Rodar isoladamente para evitar OOM quando a IDE e Produção estão ativos.
# ============================================================================

set -e

cd /home/fahbrain/projects/omnimind

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="data/test_reports"
mkdir -p "$LOG_DIR"

OUTPUT_LOG="$LOG_DIR/output_heavy_${TIMESTAMP}.log"

echo "🏋️  OMNIMIND HEAVY TEST SUITE"
echo "======================================"
echo "⏱️  Timestamp: $TIMESTAMP"
echo "🛡️  Modo: Apenas PESADOS (GPU/VRAM Intensive)"
echo "======================================"
echo ""

# Executa pytest apenas com marcador heavy
CUDA_HOME=/usr/local/cuda-12.1 \
CUDA_VISIBLE_DEVICES=0 \
LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH \
OMNIMIND_GPU=true \
OMNIMIND_FORCE_GPU=true \
OMNIMIND_DEBUG=true \
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128 \
pytest tests/ \
  -vv \
  -m "heavy" \
  --log-cli-level=INFO \
  -s \
  2>&1 | tee "$OUTPUT_LOG"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "======================================"
echo "✅ TESTES PESADOS FINALIZADOS"
echo "======================================"
echo "📋 Log salvo em: $OUTPUT_LOG"
echo ""

exit $EXIT_CODE

#!/bin/bash
# ===================================================================
# Setup de Modelos Offline para OmniMind
# Configura variáveis de ambiente e verifica modelos
# ===================================================================

set -e

echo "🔧 Configurando ambiente OFFLINE para OmniMind..."

# Diretório dos modelos
MODELS_DIR="/opt/models/sentence-transformers"
export MODELS_DIR

# Variáveis de ambiente obrigatórias para modo offline
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_HOME="/opt/hf_cache"

echo "📋 Variáveis de ambiente:"
echo "   TRANSFORMERS_OFFLINE=$TRANSFORMERS_OFFLINE"
echo "   HF_HUB_OFFLINE=$HF_HUB_OFFLINE"
echo "   HF_HOME=$HF_HOME"

# Verificar modelos
echo ""
echo "🔍 Verificando modelos em $MODELS_DIR:"

if [ ! -d "$MODELS_DIR" ]; then
    echo "❌ Diretório $MODELS_DIR não existe!"
    exit 1
fi

TOTAL_SIZE=0
for model in "$MODELS_DIR"/*; do
    if [ -d "$model" ]; then
        model_name=$(basename "$model")
        size=$(du -sh "$model" | cut -f1)
        echo "   ✅ $model_name: $size"

        # Somar tamanho (aproximado) - usando awk ao invés de bc
        size_mb=$(du -sb "$model" | awk '{print $1/1024/1024}')
        TOTAL_SIZE=$(awk "BEGIN {print $TOTAL_SIZE + $size_mb}")
    fi
done

echo ""
echo "📦 Tamanho total: $(awk "BEGIN {printf \"%.1f\", $TOTAL_SIZE / 1024}") GB"

echo ""
echo "✅ Ambiente offline configurado! Use assim:"
echo ""
echo "  # No shell, antes de rodar o backend:"
echo "  source scripts/setup_offline_models.sh"
echo "  python web/backend/main.py"
echo ""
echo "  # Ou em Python:"
echo "  import os"
echo "  os.environ['TRANSFORMERS_OFFLINE'] = '1'"
echo "  os.environ['HF_HUB_OFFLINE'] = '1'"
echo "  from sentence_transformers import SentenceTransformer"
echo "  model = SentenceTransformer('/opt/models/sentence-transformers/all-MiniLM-L6-v2')"

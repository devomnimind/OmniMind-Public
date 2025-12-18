#!/bin/bash
# Script para baixar modelos Hugging Face locais quantizados
# Uso: ./scripts/download_hf_model.sh <model_id> [quant_type]

set -e

MODEL_ID=${1:-"microsoft/Phi-3.5-mini-instruct"}
QUANT_TYPE=${2:-"none"}  # none, gguf, awq, gptq

echo "📥 Baixando modelo: $MODEL_ID"
echo "🔧 Tipo de quantização: $QUANT_TYPE"

# Criar diretório
MODEL_DIR="models/$(basename $MODEL_ID)"
mkdir -p "$MODEL_DIR"

if [ "$QUANT_TYPE" = "gguf" ]; then
    # Para GGUF, usar modelo específico
    GGUF_MODEL="${MODEL_ID}-GGUF"
    echo "🔍 Procurando versão GGUF..."
    hf download "$GGUF_MODEL" --local-dir "$MODEL_DIR" --include "*.gguf" "*.json" "*.txt"
elif [ "$QUANT_TYPE" = "awq" ]; then
    AWQ_MODEL="${MODEL_ID}-AWQ"
    hf download "$AWQ_MODEL" --local-dir "$MODEL_DIR"
elif [ "$QUANT_TYPE" = "gptq" ]; then
    GPTQ_MODEL="${MODEL_ID}-GPTQ"
    hf download "$GPTQ_MODEL" --local-dir "$MODEL_DIR"
else
    # Download padrão
    hf download "$MODEL_ID" --local-dir "$MODEL_DIR"
fi

echo "✅ Modelo baixado em: $MODEL_DIR"
echo "📊 Tamanho: $(du -sh $MODEL_DIR | cut -f1)"

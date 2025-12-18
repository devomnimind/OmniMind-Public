#!/bin/bash
# Script para forçar inicialização do Backend com GPU habilitada
# Evita erros de "CUDA initialized before setting env vars"

# 1. Configurações Críticas de Ambiente (ANTES do Python iniciar)
export CUDA_HOME="/usr/local/cuda-12.4"
export CUDA_VISIBLE_DEVICES="0"
export CUDA_PATH="/usr/local/cuda-12.4"
export LD_LIBRARY_PATH="/usr/local/cuda-12.4/lib64:$LD_LIBRARY_PATH"
export PYTORCH_CUDA_ALLOC_CONF="backend:cudaMallocAsync"
# export CUDA_LAUNCH_BLOCKING="1" # Descomente para debug, mas deixa lento

# 2. Diagnóstico Rápido
echo "=== GPU Initialization Check ==="
if command -v nvidia-smi &> /dev/null; then
    echo "✅ Driver NVIDIA detectado:"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
else
    echo "❌ nvidia-smi não encontrado! Verifique drivers."
fi

# 3. Iniciar Aplicação
echo "=== Starting OmniMind Backend ==="
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Adiciona o diretório raiz ao PYTHONPATH para encontrar 'web' e 'src'
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Ativa venv (ajuste para caminho correto se necessário, mas PYTHONPATH resolve import)
source "$PROJECT_ROOT/omnimind/.venv/bin/activate" 2>/dev/null || source "$PROJECT_ROOT/.venv/bin/activate"

# Executa uvicorn via python module para garantir sys.path correto
exec python -m uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --log-level info


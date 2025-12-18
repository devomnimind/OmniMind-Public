#!/bin/bash
# Wrapper script para executar run_500_cycles_scientific_validation.py
# Garante que variáveis de ambiente CUDA sejam exportadas ANTES do Python iniciar
# Autor: Fabrício da Silva + assistência de IA
# Data: 2025-12-10

set -euo pipefail

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Calcular PROJECT_ROOT
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Ativar venv
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
else
    echo -e "${YELLOW}⚠️  Venv não encontrado em $PROJECT_ROOT/.venv${NC}"
    echo "   Tentando continuar sem venv..."
fi

# Configurar variáveis CUDA ANTES do Python iniciar (CRÍTICO)
export CUDA_HOME="${CUDA_HOME:-/usr}"
export CUDA_PATH="${CUDA_PATH:-/usr}"
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"

# Configurações CUDA para evitar erros silenciosos
export CUDA_LAUNCH_BLOCKING="${CUDA_LAUNCH_BLOCKING:-1}"  # Padrão: 1 (síncrono)
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-max_split_size_mb:128}"

# Limitar threads OpenMP/Qiskit
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export GOTO_NUM_THREADS="${GOTO_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-4}"
export QISKIT_NUM_THREADS="${QISKIT_NUM_THREADS:-4}"

echo -e "${GREEN}🔧 Variáveis de ambiente configuradas:${NC}"
echo "   CUDA_LAUNCH_BLOCKING=$CUDA_LAUNCH_BLOCKING"
echo "   PYTORCH_CUDA_ALLOC_CONF=$PYTORCH_CUDA_ALLOC_CONF"
echo "   OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "   MKL_NUM_THREADS=$MKL_NUM_THREADS"
echo ""

# Executar script Python
echo -e "${GREEN}🚀 Executando validação científica (500 ciclos)...${NC}"
echo ""
exec python3 "$PROJECT_ROOT/scripts/run_500_cycles_scientific_validation.py" "$@"


#!/bin/bash
# Script para configurar ambiente CUDA para testes estáveis
# Evita fragmentação de memória GPU durante execução assíncrona

echo "🔧 Configurando ambiente CUDA para testes estáveis..."

# Configurações críticas para evitar fragmentação de memória
export CUDA_LAUNCH_BLOCKING="${CUDA_LAUNCH_BLOCKING:-1}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-max_split_size_mb:16,garbage_collection_threshold:0.6}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"

# Configurações adicionais para estabilidade
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export TORCH_USE_CUDA_DSA="${TORCH_USE_CUDA_DSA:-1}"
export PYTORCH_NO_CUDA_MEMORY_CACHING="${PYTORCH_NO_CUDA_MEMORY_CACHING:-1}"

echo "✅ Configurações aplicadas:"
echo "  CUDA_LAUNCH_BLOCKING=$CUDA_LAUNCH_BLOCKING"
echo "  PYTORCH_CUDA_ALLOC_CONF=$PYTORCH_CUDA_ALLOC_CONF"
echo "  OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "  MKL_NUM_THREADS=$MKL_NUM_THREADS"
echo "  NUMEXPR_NUM_THREADS=$NUMEXPR_NUM_THREADS"
echo ""

# Se foi passado um comando como argumento, executa no mesmo ambiente
if [ $# -gt 0 ]; then
    echo "🚀 Executando comando no ambiente configurado: $@"
    exec "$@"
else
    echo "💡 Para usar: source scripts/setup_cuda_test_env.sh && python -m pytest ..."
    echo "💡 Ou: ./scripts/setup_cuda_test_env.sh python -m pytest ..."
fi

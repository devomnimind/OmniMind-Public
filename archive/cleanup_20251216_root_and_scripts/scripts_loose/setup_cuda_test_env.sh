#!/bin/bash
# Script para configurar ambiente CUDA para testes estáveis no Ubuntu
# Configurações otimizadas para Ubuntu 24.04 com CUDA 12.8

echo "🔧 Configurando ambiente CUDA para Ubuntu 24.04..."

# Configurações para Ubuntu - menos restritivas que Kali
export CUDA_LAUNCH_BLOCKING="${CUDA_LAUNCH_BLOCKING:-0}"  # Permitir execução assíncrona
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-max_split_size_mb:512,garbage_collection_threshold:0.8}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"  # Usar múltiplas threads
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-4}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-4}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-4}"

# Configurações adicionais para estabilidade no Ubuntu
export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0}"
export TORCH_USE_CUDA_DSA="${TORCH_USE_CUDA_DSA:-1}"
export PYTORCH_NO_CUDA_MEMORY_CACHING="${PYTORCH_NO_CUDA_MEMORY_CACHING:-0}"  # Habilitar cache

echo "✅ Configurações aplicadas para Ubuntu:"
echo "  CUDA_LAUNCH_BLOCKING=$CUDA_LAUNCH_BLOCKING (assíncrono)"
echo "  PYTORCH_CUDA_ALLOC_CONF=$PYTORCH_CUDA_ALLOC_CONF"
echo "  OMP_NUM_THREADS=$OMP_NUM_THREADS (múltiplas threads)"
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

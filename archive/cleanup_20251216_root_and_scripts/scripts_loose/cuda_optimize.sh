#!/bin/bash
# Script de otimização CUDA para Ubuntu - OmniMind
# Compatível com NVIDIA Driver 580.95.05 e CUDA 13.0

set -e

echo "🎯 Otimizando CUDA para Ubuntu - GTX 1650"

# Verificar se estamos no ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Ative o ambiente virtual primeiro:"
    echo "   source .venv/bin/activate"
    exit 1
fi

# Configurações de ambiente CUDA otimizadas para Ubuntu
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512,garbage_collection_threshold:0.8"
export TORCH_USE_CUDA_DSA=1
export CUDA_LAUNCH_BLOCKING=0

# Configurações específicas para GTX 1650
export TF_FORCE_GPU_ALLOW_GROWTH=true
export CUDA_CACHE_DISABLE=0
export CUDA_CACHE_PATH="$HOME/.cache/cuda"

# Criar diretório de cache se não existir
mkdir -p "$HOME/.cache/cuda"

echo "✅ Configurações CUDA aplicadas:"
echo "   • CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
echo "   • PYTORCH_CUDA_ALLOC_CONF: $PYTORCH_CUDA_ALLOC_CONF"
echo "   • CUDA_CACHE_PATH: $CUDA_CACHE_PATH"

# Verificar GPU
echo ""
echo "🔍 Verificando GPU..."
nvidia-smi --query-gpu=name,memory.total,memory.free,driver_version --format=csv,noheader,nounits

# Testar PyTorch CUDA
echo ""
echo "🧪 Testando PyTorch CUDA..."
python -c "
import torch
import sys

print('PyTorch:', torch.__version__)
print('CUDA disponível:', torch.cuda.is_available())

if torch.cuda.is_available():
    print('CUDA versão:', torch.version.cuda)
    print('GPU:', torch.cuda.get_device_name(0))
    print('Memória total:', torch.cuda.get_device_properties(0).total_memory / 1024**3, 'GB')

    # Configurações otimizadas
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True

    print('cuDNN benchmark:', torch.backends.cudnn.benchmark)
    print('TF32 habilitado:', torch.backends.cuda.matmul.allow_tf32)

    # Teste rápido
    x = torch.randn(100, 100, device='cuda')
    y = torch.randn(100, 100, device='cuda')
    z = torch.mm(x, y)
    print('✅ Teste CUDA passou!')
else:
    print('❌ CUDA não disponível')
    sys.exit(1)
"

echo ""
echo "🎉 CUDA otimizado para Ubuntu!"
echo "💡 Use: source scripts/cuda_optimize.sh"

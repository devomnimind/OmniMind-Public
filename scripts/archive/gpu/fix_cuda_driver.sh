#!/bin/bash
# Script para corrigir CUDA e reinicializar driver NVIDIA

set -e

echo "=== CUDA Driver Recovery ==="
echo "1. Verificando GPU status..."
nvidia-smi

echo -e "\n2. Limpando cache CUDA..."
# Nenhum processo Python usando GPU, podemos limpar
sudo rm -rf /tmp/pytorch_* 2>/dev/null || true

echo -e "\n3. Testando PyTorch..."
python << 'PYEOF'
import torch
import sys

print(f"PyTorch: {torch.__version__}")
print(f"CUDA disponível (antes): {torch.cuda.is_available()}")

# Tentar inicializar forçadamente
try:
    # Forçar importação de libcuda
    import ctypes
    ctypes.CDLL("libcuda.so.1")
    print("✅ libcuda.so.1 carregada")
except Exception as e:
    print(f"⚠️  Erro ao carregar libcuda: {e}")

# Re-verificar
print(f"CUDA disponível (depois): {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print(f"✅ Compute Capability: {torch.cuda.get_device_capability(0)}")
    sys.exit(0)
else:
    print("❌ CUDA ainda não disponível - tente reinicializar o sistema")
    sys.exit(1)
PYEOF

exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo -e "\n✅ CUDA funcional!"
else
    echo -e "\n❌ CUDA ainda com problemas - possível reinicialização necessária"
fi

exit $exit_code

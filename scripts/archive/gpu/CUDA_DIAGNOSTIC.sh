#!/bin/bash
set -e

echo "================================"
echo "CUDA 12.4 + GTX 1650 - DIAGNÓSTICO COMPLETO"
echo "================================"
echo ""

echo "=== 1. Status NVIDIA-SMI ==="
nvidia-smi
echo ""

echo "=== 2. Módulos Kernel NVIDIA ==="
lsmod | grep -i nvidia || echo "❌ Nenhum módulo nvidia carregado!"
echo ""

echo "=== 3. CUDA Version do Driver ==="
nvidia-smi | grep "CUDA Version"
echo ""

echo "=== 4. Device Nodes ==="
ls -l /dev/nvidia* 2>/dev/null || echo "❌ Device nodes ausentes!"
echo ""

echo "=== 5. PyTorch Status ==="
source .venv/bin/activate
python << 'PYEOF'
import torch
import os

print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Version (PyTorch): {torch.version.cuda}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Device Count: {torch.cuda.device_count()}")

# Verificar LD_LIBRARY_PATH
print(f"\nLD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'NOT SET')}")
print(f"CUDA_HOME: {os.environ.get('CUDA_HOME', 'NOT SET')}")

# Verificar libcuda
try:
    import ctypes
    ctypes.CDLL("libcuda.so.1")
    print("\n✅ libcuda.so.1: Carregada")
except Exception as e:
    print(f"\n❌ libcuda.so.1: Erro - {e}")
PYEOF
echo ""

echo "=== 6. Logs do Sistema (últimos erros nvidia) ==="
sudo journalctl -xe --grep=nvidia -n 20 2>/dev/null | tail -10 || echo "Sem erros recentes"
echo ""

echo "=== 7. dmesg (últimos erros nvidia) ==="
sudo dmesg | grep -i nvidia | tail -10 || echo "Sem erros no dmesg"
echo ""

echo "=== 8. Verificar nvidia-modprobe ==="
which nvidia-modprobe && echo "✅ nvidia-modprobe instalado" || echo "❌ nvidia-modprobe NÃO instalado"
echo ""

echo "=== 9. Linux Headers ==="
uname -r
dpkg -l | grep linux-headers | grep $(uname -r) && echo "✅ Headers OK" || echo "⚠️  Headers pode não estar instalado"
echo ""

echo "=== 10. Secure Boot ==="
mokutil --sb-state 2>/dev/null || echo "⚠️  mokutil não disponível"
echo ""

echo "================================"
echo "FIM DO DIAGNÓSTICO"
echo "================================"

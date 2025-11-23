#!/bin/bash

echo "================================"
echo "VALIDAÇÃO FINAL - CUDA FUNCIONAL"
echo "================================"
echo ""

echo "=== 1. nvidia-smi ==="
nvidia-smi -q | head -20
echo ""

echo "=== 2. Módulos Kernel ==="
lsmod | grep -E "nvidia|uvm"
echo ""

echo "=== 3. Device Files ==="
ls -la /dev/nvidia*
echo ""

echo "=== 4. PyTorch CUDA Completo ==="
python << 'PYEOF'
import torch
import subprocess

print("Version:", torch.__version__)
print("CUDA Available:", torch.cuda.is_available())
print("Device Count:", torch.cuda.device_count())

if torch.cuda.is_available():
    props = torch.cuda.get_device_properties(0)
    print(f"GPU: {props.name}")
    print(f"Compute Capability: {props.major}.{props.minor}")
    print(f"Total Memory: {props.total_memory / (1024**3):.2f} GB")
    
    # Teste de performance
    import time
    x = torch.randn(1000, 1000, device='cuda')
    y = torch.randn(1000, 1000, device='cuda')
    
    start = time.time()
    for _ in range(10):
        z = torch.mm(x, y)
    cuda_time = time.time() - start
    
    # CPU comparison
    x_cpu = x.cpu()
    y_cpu = y.cpu()
    start = time.time()
    for _ in range(10):
        z = torch.mm(x_cpu, y_cpu)
    cpu_time = time.time() - start
    
    speedup = cpu_time / cuda_time
    print(f"GPU vs CPU Speedup: {speedup:.2f}x")
    print("✅ CUDA TOTALMENTE FUNCIONAL")
else:
    print("❌ CUDA NÃO DISPONÍVEL")
PYEOF

echo ""
echo "=== 5. Verificar Persistência ==="
cat /etc/modules-load.d/nvidia.conf 2>/dev/null | grep nvidia-uvm && echo "✅ nvidia-uvm vai carregar no boot" || echo "⚠️  verificar initramfs"

echo ""
echo "================================"
echo "FIM DA VALIDAÇÃO"
echo "================================"

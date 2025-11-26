#!/bin/bash
set -euo pipefail
echo "=== NVIDIA GPU Setup Verification ==="
echo ""

echo "1. NVIDIA Drivers:"
nvidia-smi --query-gpu=driver_version,name,memory.total --format=csv,noheader

echo ""
echo "2. CUDA Toolkit:"
if command -v nvcc >/dev/null 2>&1; then
  nvcc --version
else
  echo "   ❌ CUDA not found"
fi

echo ""
echo "3. cuDNN:"
if ldconfig -p | grep -q cudnn; then
  ldconfig -p | grep cudnn
else
  echo "   ❌ cuDNN not found"
fi

echo ""
echo "4. PyTorch GPU Support:"
python3 -c "import torch; print(f'   GPU Available: {torch.cuda.is_available()}'); print(f'   Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')" || echo "   ❌ PyTorch check failed"

echo ""
echo "5. TensorFlow GPU Support:"
python3 -c "import tensorflow as tf; print(f'   GPU Available: {len(tf.config.list_physical_devices(\"GPU\")) > 0}'); print(f'   Devices: {[d.name for d in tf.config.list_physical_devices(\"GPU\")]}')" || echo "   ❌ TensorFlow check failed"

echo ""
echo "6. GPU Memory:"
nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader

echo ""
echo "=== Setup Complete ==="


#!/bin/bash
echo "🔧 Attempting to fix NVIDIA Driver state..."

if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (sudo)"
  exit 1
fi

echo "1. Reloading UVM module..."
rmmod nvidia_uvm 2>/dev/null
modprobe nvidia_uvm

echo "2. Loading other kernel modules..."
modprobe nvidia
modprobe nvidia-modeset

echo "3. Creating device nodes..."
if command -v nvidia-modprobe &> /dev/null; then
    nvidia-modprobe -u -c=0
    echo "✅ nvidia-modprobe executed"
else
    echo "⚠️ nvidia-modprobe not found"
fi

echo "3. Checking persistence daemon..."
if command -v nvidia-persistenced &> /dev/null; then
    nvidia-persistenced --persistence-mode
    echo "✅ Persistence mode enabled"
fi

echo "4. Verifying..."
nvidia-smi

echo "✅ Done. Try running the application now."

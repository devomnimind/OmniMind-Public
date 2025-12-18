#!/bin/bash
echo "🔧 Reloading NVIDIA UVM module..."

if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (sudo)"
  exit 1
fi

rmmod nvidia_uvm
if [ $? -eq 0 ]; then
    echo "✅ Unloaded nvidia_uvm"
else
    echo "⚠️ Failed to unload nvidia_uvm (might not be loaded or in use)"
fi

modprobe nvidia_uvm
if [ $? -eq 0 ]; then
    echo "✅ Loaded nvidia_uvm"
else
    echo "❌ Failed to load nvidia_uvm"
    exit 1
fi

# Re-create device node just in case
rm -f /dev/nvidia-uvm
nvidia-modprobe -u -c=0
echo "✅ Refreshed /dev/nvidia-uvm"

echo "Done."

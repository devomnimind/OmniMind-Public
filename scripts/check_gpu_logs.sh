#!/bin/bash
echo "--- Kernel Logs (NVRM) ---"
dmesg | grep -i "nvidia" | tail -n 20

echo "\n--- Persistence Daemon ---"
ps aux | grep nvidia-persistenced

echo "\n--- Loaded Modules ---"
lsmod | grep nvidia

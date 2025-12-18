import os
import sys

import torch

print(f"Python: {sys.version}")
print(f"PyTorch: {torch.__version__}")
print(f"CUDA_VISIBLE_DEVICES (env): {os.environ.get('CUDA_VISIBLE_DEVICES')}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device Count: {torch.cuda.device_count()}")
    print(f"Current Device: {torch.cuda.current_device()}")
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA NOT AVAILABLE. Diagnostics:")
    # Tenta forçar inicialização para ver erro
    try:
        torch.cuda.init()
    except Exception as e:
        print(f"Init Error: {e}")

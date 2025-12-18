import os

# Try Lazy Loading trick
os.environ["CUDA_MODULE_LOADING"] = "LAZY"
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

print("--- Environment LAZY ---")
print(f"CUDA_MODULE_LOADING: {os.environ.get('CUDA_MODULE_LOADING')}")

import torch

print("\n--- Torch Initialization ---")
print(f"Torch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Device Count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
    x = torch.tensor([1.0, 2.0]).cuda()
    print(f"Tensor on GPU: {x}")
else:
    print("❌ CUDA still not available.")
    # Try to diagnose
    try:
        torch.cuda.init()
    except Exception as e:
        print(f"Init Error: {e}")
        print(f"Init Error: {e}")

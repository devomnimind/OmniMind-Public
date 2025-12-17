import ctypes
import os
import sys


def force_cuda_initialization():
    """
    Attempt to manually initialize CUDA driver using ctypes.
    This can sometimes bypass PyTorch's lazy initialization issues.
    """
    try:
        # Try to find libcuda.so
        lib_names = [
            "libcuda.so",
            "libcuda.so.1",
            "/usr/lib/x86_64-linux-gnu/libcuda.so.1",
            "/usr/lib/x86_64-linux-gnu/libcuda.so",
        ]

        libcuda = None
        for name in lib_names:
            try:
                libcuda = ctypes.CDLL(name)
                print(f"✅ Loaded {name}")
                break
            except OSError:
                continue

        if not libcuda:
            print("❌ Could not load libcuda.so")
            return False

        # Try to call cuInit(0)
        try:
            # cuInit returns 0 on success
            result = libcuda.cuInit(0)
            if result == 0:
                print("✅ cuInit(0) successful!")
                return True
            else:
                print(f"❌ cuInit(0) failed with error code: {result}")
                return False
        except AttributeError:
            print("❌ cuInit not found in library")
            return False

    except Exception as e:
        print(f"❌ Error during manual CUDA init: {e}")
        return False


if __name__ == "__main__":
    print("--- Manual CUDA Initialization Check ---")
    success = force_cuda_initialization()

    print("\n--- PyTorch Check ---")
    import torch

    print(f"Torch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(f"Device Count: {torch.cuda.device_count()}")
    print(f"Device Count: {torch.cuda.device_count()}")

#!/usr/bin/env python3
"""
GPU Status Verification Script
================================
Verifica se GPU está realmente disponível e forçada corretamente
Usado antes de rodar testes para diagnóstico

Usage:
  python scripts/verify_gpu_status.py
  or: ./scripts/verify_gpu_status.py (if executable)
"""

import os
import sys


def verify_gpu():
    """Verify GPU availability with all detection methods."""

    print("=" * 70)
    print("🔍 GPU STATUS VERIFICATION")
    print("=" * 70)
    print()

    # Check environment variables
    print("📋 ENVIRONMENT VARIABLES:")
    print(f"  OMNIMIND_GPU: {os.getenv('OMNIMIND_GPU', 'NOT SET')}")
    print(f"  OMNIMIND_FORCE_GPU: {os.getenv('OMNIMIND_FORCE_GPU', 'NOT SET')}")
    print(f"  PYTEST_FORCE_GPU: {os.getenv('PYTEST_FORCE_GPU', 'NOT SET')}")
    print(f"  CUDA_VISIBLE_DEVICES: {os.getenv('CUDA_VISIBLE_DEVICES', 'NOT SET (auto)')}")
    print(f"  PYTORCH_CUDA_ALLOC_CONF: {os.getenv('PYTORCH_CUDA_ALLOC_CONF', 'NOT SET')}")
    print()

    # Check torch
    print("📦 PyTorch Detection:")
    try:
        import torch

        print(f"  torch version: {torch.__version__}")
        print(f"  torch.cuda.is_available(): {torch.cuda.is_available()}")
        print(f"  torch.cuda.device_count(): {torch.cuda.device_count()}")

        if torch.cuda.device_count() > 0:
            print(f"  torch.cuda.get_device_name(0): {torch.cuda.get_device_name(0)}")
            print(f"  torch.cuda.get_device_capability(0): {torch.cuda.get_device_capability(0)}")

        print()
    except Exception as e:
        print(f"  ❌ Error checking torch: {e}")
        print()

    # Check Quantum Backend detection
    print("🧠 Quantum Backend Detection:")
    try:
        sys.path.insert(0, "/home/fahbrain/projects/omnimind/src")
        from quantum_consciousness.quantum_backend import QuantumBackend

        qb = QuantumBackend()
        print(f"  Backend Mode: {qb.mode}")
        print(f"  use_gpu flag: {qb.use_gpu}")
        print(f"  Provider: {qb.provider}")
        print()

        if "GPU" in qb.mode:
            print("✅ GPU IS ACTIVE IN QUANTUM BACKEND")
        else:
            print(f"⚠️ GPU NOT ACTIVE - using {qb.mode}")

    except Exception as e:
        print(f"  ❌ Error loading Quantum Backend: {e}")
        print()

    # Summary
    print("=" * 70)
    force_gpu_env = os.getenv("OMNIMIND_FORCE_GPU", "").lower() in ("true", "1", "yes")
    cuda_available = torch.cuda.is_available()
    device_count = torch.cuda.device_count()

    if force_gpu_env and device_count > 0:
        print("✅ GPU FORCING IS CONFIGURED CORRECTLY")
        print(f"   - OMNIMIND_FORCE_GPU={force_gpu_env} ✓")
        print(f"   - CUDA devices available: {device_count} ✓")
    elif cuda_available:
        print("✅ GPU AVAILABLE (standard detection)")
    else:
        print("❌ GPU NOT AVAILABLE OR NOT FORCED")
        print(f"   - torch.cuda.is_available(): {cuda_available}")
        print(f"   - device_count: {device_count}")
        print(f"   - OMNIMIND_FORCE_GPU: {force_gpu_env}")

    print("=" * 70)
    print()


if __name__ == "__main__":
    verify_gpu()

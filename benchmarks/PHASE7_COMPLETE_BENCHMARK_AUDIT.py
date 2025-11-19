#!/usr/bin/env python3
"""
Phase 7 Complete Benchmark and Audit Report
GPU/CUDA Environment Validation with Performance Metrics
"""

import torch
import subprocess
import json
import psutil
import platform
from datetime import datetime

def get_system_info():
    """Get comprehensive system information."""
    return {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.system(),
        "release": platform.release(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(logical=False),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "total_memory_gb": psutil.virtual_memory().total / (1024**3),
        "available_memory_gb": psutil.virtual_memory().available / (1024**3),
    }

def get_gpu_info():
    """Get GPU information from PyTorch."""
    return {
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
        "cudnn_version": torch.backends.cudnn.version(),
        "gpu_count": torch.cuda.device_count(),
        "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None,
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "device_capability": torch.cuda.get_device_capability(0) if torch.cuda.is_available() else None,
        "total_memory_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3) if torch.cuda.is_available() else None,
        "pytorch_version": torch.__version__,
    }

def benchmark_cpu():
    """CPU benchmark with matrix multiplication."""
    try:
        import time
        size = 5000
        A = torch.randn(size, size)
        B = torch.randn(size, size)
        
        start = time.time()
        C = torch.matmul(A, B)
        elapsed = time.time() - start
        
        flops = (2 * size**3) / (elapsed * 1e9)  # in GFLOPS
        
        return {
            "status": "success",
            "matrix_size": size,
            "time_ms": elapsed * 1000,
            "throughput_gflops": flops,
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def benchmark_gpu():
    """GPU benchmark with matrix multiplication."""
    if not torch.cuda.is_available():
        return {"status": "skipped", "reason": "CUDA not available"}
    
    try:
        import time
        size = 5000
        A = torch.randn(size, size, device='cuda')
        B = torch.randn(size, size, device='cuda')
        
        # Warmup
        torch.cuda.synchronize()
        start = time.time()
        C = torch.matmul(A, B)
        torch.cuda.synchronize()
        elapsed = time.time() - start
        
        flops = (2 * size**3) / (elapsed * 1e9)  # in GFLOPS
        
        return {
            "status": "success",
            "device": str(torch.cuda.get_device_name(0)),
            "matrix_size": size,
            "time_ms": elapsed * 1000,
            "throughput_gflops": flops,
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def benchmark_memory():
    """Memory bandwidth benchmark."""
    try:
        import time
        size = 100_000_000
        a = torch.randn(size)
        
        start = time.time()
        b = a.clone()
        elapsed = time.time() - start
        
        bandwidth_gbs = (size * 8 / (1024**3)) / elapsed
        
        return {
            "status": "success",
            "size_elements": size,
            "time_ms": elapsed * 1000,
            "bandwidth_gbs": bandwidth_gbs,
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def get_driver_info():
    """Get NVIDIA driver information."""
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return {"driver_version": result.stdout.strip(), "nvidia_smi": "available"}
        else:
            return {"error": "nvidia-smi failed"}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 80)
    print("PHASE 7 COMPLETE BENCHMARK AND AUDIT REPORT")
    print("=" * 80)
    print()
    
    report = {
        "session_date": datetime.now().isoformat(),
        "system": get_system_info(),
        "gpu": get_gpu_info(),
        "driver": get_driver_info(),
        "benchmarks": {
            "cpu": benchmark_cpu(),
            "gpu": benchmark_gpu(),
            "memory": benchmark_memory(),
        }
    }
    
    # Print formatted report
    print("SYSTEM INFORMATION")
    print("-" * 80)
    for key, value in report["system"].items():
        print(f"  {key:.<40} {value}")
    print()
    
    print("GPU/CUDA INFORMATION")
    print("-" * 80)
    for key, value in report["gpu"].items():
        print(f"  {key:.<40} {value}")
    print()
    
    print("DRIVER INFORMATION")
    print("-" * 80)
    for key, value in report["driver"].items():
        print(f"  {key:.<40} {value}")
    print()
    
    print("BENCHMARK RESULTS")
    print("-" * 80)
    print("CPU Benchmark (Matrix Multiplication):")
    cpu_bench = report["benchmarks"]["cpu"]
    if cpu_bench["status"] == "success":
        print(f"  ✅ Time: {cpu_bench['time_ms']:.2f} ms")
        print(f"  ✅ Throughput: {cpu_bench['throughput_gflops']:.2f} GFLOPS")
    else:
        print(f"  ❌ {cpu_bench.get('error', 'Unknown error')}")
    print()
    
    print("GPU Benchmark (Matrix Multiplication):")
    gpu_bench = report["benchmarks"]["gpu"]
    if gpu_bench["status"] == "success":
        print(f"  ✅ Device: {gpu_bench['device']}")
        print(f"  ✅ Time: {gpu_bench['time_ms']:.2f} ms")
        print(f"  ✅ Throughput: {gpu_bench['throughput_gflops']:.2f} GFLOPS")
    elif gpu_bench["status"] == "skipped":
        print(f"  ⚠️  {gpu_bench['reason']}")
    else:
        print(f"  ❌ {gpu_bench.get('error', 'Unknown error')}")
    print()
    
    print("Memory Bandwidth:")
    mem_bench = report["benchmarks"]["memory"]
    if mem_bench["status"] == "success":
        print(f"  ✅ Bandwidth: {mem_bench['bandwidth_gbs']:.2f} GB/s")
    else:
        print(f"  ❌ {mem_bench.get('error', 'Unknown error')}")
    print()
    
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    cuda_status = "✅ AVAILABLE" if report["gpu"]["cuda_available"] else "❌ NOT AVAILABLE"
    print(f"CUDA Status: {cuda_status}")
    print(f"PyTorch: {report['gpu']['pytorch_version']}")
    print(f"Python: {report['system']['python_version']}")
    print(f"GPU: {report['gpu']['device_name']}")
    print()
    
    # Save JSON report
    with open("logs/PHASE7_BENCHMARK_REPORT.json", "w") as f:
        json.dump(report, f, indent=2)
    print("Report saved to: logs/PHASE7_BENCHMARK_REPORT.json")
    print("=" * 80)

if __name__ == "__main__":
    main()

import json
import os
import time

try:
    import torch
except ImportError:
    torch = None


def run_gpu_benchmark() -> dict:
    if not torch or not torch.cuda.is_available():
        return {
            "status": "N/A",
            "reason": "torch.cuda unavailable or torch not installed",
        }

    results = {}
    device = torch.device("cuda")
    start = time.perf_counter()
    torch.cuda.init()
    results["init_ms"] = (time.perf_counter() - start) * 1000

    size = 10_000_000
    cpu_tensor = torch.randn(size, device="cpu")
    start = time.perf_counter()
    gpu_tensor = cpu_tensor.to(device, non_blocking=True)
    torch.cuda.synchronize()
    results["cpu_to_gpu_ms"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    _ = torch.mm(gpu_tensor[:1000].reshape(1, -1), gpu_tensor[:1000].reshape(-1, 1))
    torch.cuda.synchronize()
    results["matrix_mult_ms"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    _ = gpu_tensor.to("cpu", non_blocking=True)
    torch.cuda.synchronize()
    results["gpu_to_cpu_ms"] = (time.perf_counter() - start) * 1000

    results["status"] = "OK"
    return results


def main() -> None:
    os.makedirs("docs/reports/benchmarks", exist_ok=True)
    results = run_gpu_benchmark()
    with open("docs/reports/benchmarks/gpu_benchmark.json", "w", encoding="utf-8") as stream:
        json.dump(results, stream, indent=2)


if __name__ == "__main__":
    main()

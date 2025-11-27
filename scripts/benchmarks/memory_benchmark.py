import json
import os
import time

import psutil

SIZES = [100 * 1024**2, 1024**3]


def memory_throughput(size: int) -> float:
    arr = bytearray(size)
    start = time.perf_counter()
    for i in range(0, size, 4096):
        arr[i] = (arr[i] + 1) % 256
    throughput = size / (time.perf_counter() - start) / (1024**2)
    return throughput


def main() -> None:
    os.makedirs("docs/reports/benchmarks", exist_ok=True)
    results = {
        "memory_total": psutil.virtual_memory().total,
        "memory_throughput_mb_s": [memory_throughput(size) for size in SIZES],
        "timestamp": time.time(),
    }
    with open("docs/reports/benchmarks/memory_benchmark.json", "w", encoding="utf-8") as stream:
        json.dump(results, stream, indent=2)


if __name__ == "__main__":
    main()

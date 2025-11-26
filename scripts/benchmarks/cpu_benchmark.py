import json
import math
import os
import time

import hashlib
import zlib

LOOP_COUNT = 1_000_000
REPEATS = 3


def timed(func):
    def wrapper(*args, **kwargs):
        durations = []
        for _ in range(REPEATS):
            start = time.perf_counter()
            func(*args, **kwargs)
            durations.append((time.perf_counter() - start) * 1000)
        return sum(durations) / len(durations)

    return wrapper


@timed
def loop_benchmark():
    total = 0
    for i in range(LOOP_COUNT):
        total += i
    return total


@timed
def math_benchmark():
    s = 0.0
    for i in range(1, LOOP_COUNT // 10):
        s += math.sqrt(i) + math.sin(i) + math.cos(i) + math.pow(i, 0.5)
    return s


@timed
def hash_benchmark():
    data = ("omnimind" * 1024).encode("utf-8")
    digest = hashlib.sha256()
    for _ in range(10000):
        digest.update(data)
    return digest.hexdigest()


@timed
def compression_benchmark():
    data = os.urandom(1_000_000)
    comp = zlib.compress(data)
    zlib.decompress(comp)


def main() -> None:
    os.makedirs("docs/reports/benchmarks", exist_ok=True)
    results = {
        "loop_ms": loop_benchmark(),
        "math_ms": math_benchmark(),
        "hash_ms": hash_benchmark(),
        "compression_ms": compression_benchmark(),
        "timestamp": time.time(),
    }
    with open(
        "docs/reports/benchmarks/cpu_benchmark.json", "w", encoding="utf-8"
    ) as stream:
        json.dump(results, stream, indent=2)


if __name__ == "__main__":
    main()

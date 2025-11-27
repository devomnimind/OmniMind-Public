import json
import os
import random
import time

TEST_FILE = "docs/reports/benchmarks/disk_test.bin"
SIZE = 100 * 1024**2
RANDOM_ACCESS = 1000


def write_seq() -> float:
    data = os.urandom(1024 * 1024)
    start = time.perf_counter()
    with open(TEST_FILE, "wb") as stream:
        for _ in range(SIZE // len(data)):
            stream.write(data)
    os.sync()
    return SIZE / (time.perf_counter() - start) / (1024**2)


def read_seq() -> float:
    start = time.perf_counter()
    with open(TEST_FILE, "rb") as stream:
        while stream.read(1024 * 1024):
            pass
    return SIZE / (time.perf_counter() - start) / (1024**2)


def random_access() -> float:
    start = time.perf_counter()
    with open(TEST_FILE, "rb") as stream:
        for _ in range(RANDOM_ACCESS):
            offset = random.randint(0, SIZE - 4096)
            stream.seek(offset)
            stream.read(4096)
    return (RANDOM_ACCESS * 4096) / (time.perf_counter() - start) / (1024**2)


def main() -> None:
    os.makedirs("docs/reports/benchmarks", exist_ok=True)
    results = {
        "write_throughput_mb_s": write_seq(),
        "read_throughput_mb_s": read_seq(),
        "random_access_mb_s": random_access(),
        "timestamp": time.time(),
    }
    with open("docs/reports/benchmarks/disk_benchmark.json", "w", encoding="utf-8") as stream:
        json.dump(results, stream, indent=2)


def cleanup() -> None:
    try:
        os.remove(TEST_FILE)
    except FileNotFoundError:
        pass


if __name__ == "__main__":
    import os

    main()
    cleanup()

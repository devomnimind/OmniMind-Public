"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

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

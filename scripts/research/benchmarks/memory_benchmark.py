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

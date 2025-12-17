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

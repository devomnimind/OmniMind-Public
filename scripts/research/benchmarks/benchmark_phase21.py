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

import asyncio
import json
import logging
import time
from pathlib import Path

from src.optimization.benchmarking import PerformanceBenchmark, RegressionDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("phase21_benchmark")


async def run_production_benchmark():
    """
    Executes the full Phase 21 production benchmark session.
    This benchmark tests the integrated system:
    - Native Backend (FastAPI)
    - Database Interactions (Qdrant/Redis via Backend)
    - System Resource Monitoring
    """
    logger.info("Starting Phase 21 Production Benchmark Session")

    benchmark = PerformanceBenchmark(benchmark_dir=Path("data/benchmarks/phase21"))
    detector = RegressionDetector(history_dir=Path("data/benchmarks/history"))

    results = {}

    # 1. Backend API Benchmark (Native)
    logger.info("Benchmarking Native Backend API...")
    import os

    import httpx

    # Detect environment and set appropriate backend URL
    if os.path.exists("/.dockerenv") or os.environ.get("DOCKER_CONTAINER", "").lower() == "true":
        backend_url = "http://backend:8000"
        environment = "docker_container"
    else:
        backend_url = "http://localhost:8000"
        environment = "systemd_native"

    async def backend_workload():
        async with httpx.AsyncClient() as http_client:
            # 1. Health Check
            await http_client.get(f"{backend_url}/health")
            # 2. Root Endpoint
            await http_client.get(f"{backend_url}/")
            # Add more endpoints as needed

    def sync_backend_workload():
        # Hack: Use a new loop in a new thread to simulate sync execution for the benchmark tool
        import threading

        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(backend_workload())
            loop.close()

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

    backend_result = benchmark.run_benchmark(
        name="phase21_backend_api",
        workload=sync_backend_workload,
        iterations=50,
        warmup_iterations=5,
    )

    backend_regression = detector.detect_regressions("phase21_backend_api", backend_result)
    results["backend"] = {
        "metrics": {
            "mean_time_ms": backend_result.mean_time_ms,
            "mean_memory_mb": backend_result.mean_memory_mb,
            "mean_cpu_percent": backend_result.mean_cpu_percent,
        },
        "regression": backend_regression,
    }

    # 2. System Resource Baseline
    logger.info("Capturing System Resource Baseline...")
    import psutil

    system_metrics = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
    }
    results["system"] = system_metrics

    # Save consolidated report
    report_path = Path("data/benchmarks/phase21_production_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    final_report = {
        "timestamp": time.time(),
        "phase": "21",
        "environment": environment,
        "results": results,
    }

    with open(report_path, "w") as f:
        json.dump(final_report, f, indent=2)

    logger.info(f"Phase 21 Benchmark Complete. Report saved to {report_path}")
    print(json.dumps(final_report, indent=2))


if __name__ == "__main__":
    try:
        asyncio.run(run_production_benchmark())
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        exit(1)

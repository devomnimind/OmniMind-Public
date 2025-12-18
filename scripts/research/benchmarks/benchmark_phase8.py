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

"""Benchmark Phase 8 services: MCP server + D-Bus."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from time import perf_counter
from typing import Dict, List, Tuple

from src.integrations import DBusSystemController, MCPClient, MCPConfig, MCPServer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _measure_operation(func) -> Tuple[float, Dict[str, object]]:
    start = perf_counter()
    info: Dict[str, object] = {"success": False}
    try:
        result = func()
        info.update({"success": True, "result": result})
    except Exception as exc:  # pragma: no cover - bench helper
        info.update({"error": str(exc)})
    duration = perf_counter() - start
    return duration, info


def run_benchmark() -> Dict[str, object]:
    project_root = Path(__file__).resolve().parent
    bench_dir = project_root / "tmp_bench"
    bench_dir.mkdir(exist_ok=True)
    server = MCPServer(
        config=MCPConfig.load(),
        allowed_roots=[str(project_root), str(bench_dir)],
    )
    server.start()
    client = MCPClient(server.url)
    file_path = bench_dir / "phase8_mcp.txt"
    metrics: Dict[str, object] = {"mcp": {}, "dbus": {}}
    try:
        operations: List[Dict[str, object]] = []
        for name, function in [
            (
                "write",
                lambda: client.write_file(
                    str(file_path), "phase8 benchmark payload", encoding="utf-8"
                ),
            ),
            ("read", lambda: client.read_file(str(file_path))),
            ("list", lambda: client.list_dir(str(bench_dir))),
            ("stat", lambda: client.stat(str(file_path))),
        ]:
            duration, info = _measure_operation(function)
            operations.append({"name": name, "duration": duration, **info})
        metrics["mcp"]["operations"] = operations
        duration, info = _measure_operation(lambda: client.get_metrics())
        metrics["mcp"]["metrics_call"] = {"duration": duration, **info}
    finally:
        server.stop()
    dbus_controller = DBusSystemController()
    dbus_ops: List[Dict[str, object]] = []
    for label, function in [
        ("network", dbus_controller.get_network_status),
        ("power", dbus_controller.get_power_status),
    ]:
        duration, info = _measure_operation(function)
        dbus_ops.append({"name": label, "duration": duration, **info})
    metrics["dbus"]["operations"] = dbus_ops
    benchmark_file = project_root / "logs" / "phase8_benchmark.json"
    benchmark_file.parent.mkdir(parents=True, exist_ok=True)
    benchmark_file.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info("Benchmark complete. Metrics written to %s", benchmark_file)
    return metrics


if __name__ == "__main__":
    report = run_benchmark()
    logger.info("Phase 8 benchmark summary: %s", json.dumps(report, indent=2))

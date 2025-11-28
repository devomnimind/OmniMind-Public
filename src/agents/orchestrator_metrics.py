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

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from statistics import mean
from typing import Any, Dict


@dataclass
class OperationMetrics:
    count: int = 0
    errors: int = 0
    latencies: deque[float] = field(default_factory=lambda: deque(maxlen=256))

    def record(self, latency: float, success: bool) -> None:
        self.count += 1
        if not success:
            self.errors += 1
        self.latencies.append(latency)

    @property
    def avg_latency(self) -> float:
        return mean(self.latencies) if self.latencies else 0.0


class OrchestratorMetricsCollector:
    def __init__(self) -> None:
        self.operations: Dict[str, OperationMetrics] = {}
        self.total_requests: int = 0
        self.total_errors: int = 0

    def record(self, name: str, latency: float, success: bool) -> None:
        op = self.operations.setdefault(name, OperationMetrics())
        op.record(latency, success)
        self.total_requests += 1
        if not success:
            self.total_errors += 1

    def summary(self) -> Dict[str, Any]:
        ops = {}
        for name, op in self.operations.items():
            ops[name] = {
                "count": op.count,
                "errors": op.errors,
                "avg_latency": round(op.avg_latency, 3),
            }
        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "operations": ops,
        }

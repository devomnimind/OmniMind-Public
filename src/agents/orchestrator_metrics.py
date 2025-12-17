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

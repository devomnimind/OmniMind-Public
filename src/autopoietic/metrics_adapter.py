"""Adapters for collecting real system metrics to drive the autopoietic cycle."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import psutil

logger = logging.getLogger(__name__)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


@dataclass(frozen=True)
class MetricSample:
    """Normalized metrics used by the architecture evolution strategy."""

    timestamp: float
    error_rate: float
    cpu_usage: float
    latency_ms: float
    source: str
    raw_metrics: Dict[str, Any]

    def strategy_inputs(self) -> Dict[str, float]:
        """Return the dictionary expected by ArchitectureEvolution."""
        return {
            "error_rate": self.error_rate,
            "cpu_usage": self.cpu_usage,
            "latency_ms": self.latency_ms,
        }


class MetricsAdapter:
    """Adapter to convert RealConsciousnessMetrics to MetricSample for AutopoieticManager."""

    @staticmethod
    def adapt(real_metrics: Any) -> MetricSample:
        """
        Converts RealConsciousnessMetrics (or dict) to MetricSample.
        """
        # Extract values whether it's an object or dict
        if isinstance(real_metrics, dict):
            phi = float(real_metrics.get("phi", 0.5))
            anxiety = float(real_metrics.get("anxiety", 0.2))
            flow = float(real_metrics.get("flow", 0.5))
            entropy = float(real_metrics.get("entropy", 0.4))
        else:
            phi = float(getattr(real_metrics, "phi", 0.5))
            anxiety = float(getattr(real_metrics, "anxiety", 0.2))
            flow = float(getattr(real_metrics, "flow", 0.5))
            entropy = float(getattr(real_metrics, "entropy", 0.4))

        # Calculate synthetic system metrics from consciousness metrics
        error_rate = _clamp(max(1.0 - phi, anxiety), 0.0, 1.0)
        latency_ms = max(50.0, (1.2 - flow) * 400.0 + entropy * 150.0)

        try:
            # CORREÇÃO (2025-12-09): interval=None retorna 0.0% na primeira chamada
            # Usar interval=0.1 para leitura imediata precisa
            cpu_usage = float(psutil.cpu_percent(interval=0.1) or 0.0)
        except Exception as exc:
            logger.warning("psutil.cpu_percent failed: %s", exc)
            cpu_usage = 50.0 + (anxiety * 30.0)

        return MetricSample(
            timestamp=time.time(),
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            latency_ms=latency_ms,
            source="real_consciousness_metrics",
            raw_metrics={"phi": phi, "anxiety": anxiety, "flow": flow},
        )


def collect_metrics(
    real_metrics_path: str = "data/monitor/real_metrics.json",
) -> MetricSample:
    """Collect real metrics combining consciousness data and system telemetry."""

    timestamp = time.time()
    real_metrics = _read_real_metrics(Path(real_metrics_path))

    try:
        cpu_usage = float(psutil.cpu_percent(interval=0.05))
    except Exception as exc:
        logger.warning("psutil.cpu_percent (collect_metrics) failed: %s", exc)
        cpu_usage = 0.0

    if real_metrics:
        phi = float(real_metrics.get("phi", 0.5))
        anxiety = float(real_metrics.get("anxiety", 0.2))
        entropy = float(real_metrics.get("entropy", 0.4))
        flow = float(real_metrics.get("flow", 0.5))
        source = "real_metrics+psutil"
    else:
        phi = 0.5
        anxiety = 0.3
        entropy = 0.5
        flow = 0.4
        source = "psutil_fallback"

    error_rate = _clamp(max(1.0 - phi, anxiety), 0.0, 1.0)
    latency_ms = max(50.0, (1.2 - flow) * 400.0 + entropy * 150.0)

    sample = MetricSample(
        timestamp=timestamp,
        error_rate=error_rate,
        cpu_usage=cpu_usage,
        latency_ms=latency_ms,
        source=source,
        raw_metrics=real_metrics or {},
    )

    logger.debug(
        "Metric sample collected: source=%s error=%.3f cpu=%.1f latency=%.1fms",
        sample.source,
        sample.error_rate,
        sample.cpu_usage,
        sample.latency_ms,
    )
    return sample


def _read_real_metrics(path: Path) -> Optional[Dict[str, Any]]:
    try:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except json.JSONDecodeError as exc:
        logger.warning("Failed to parse real metrics file %s: %s", path, exc)
        return None

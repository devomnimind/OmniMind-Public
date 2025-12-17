import json
from types import SimpleNamespace

import pytest

from src.metrics.dashboard_metrics import DashboardMetricsAggregator
from src.metrics.real_consciousness_metrics import RealConsciousnessMetrics
from src.metrics.real_system_health import SystemHealthStatus


class DummyCollector:
    async def collect_real_metrics(self) -> RealConsciousnessMetrics:
        metrics = RealConsciousnessMetrics(
            phi=1.2,
            ici=0.85,
            prs=0.62,
            anxiety=0.22,
            flow=0.73,
            entropy=0.31,
        )
        metrics.history["phi"] = [1.0, 1.1]
        metrics.history["ici"] = [0.8, 0.82]
        metrics.history["prs"] = [0.58, 0.6]
        metrics.history["anxiety"] = [0.2, 0.21]
        metrics.history["flow"] = [0.7, 0.72]
        metrics.history["entropy"] = [0.29, 0.3]
        return metrics


class DummyModuleTracker:
    def get_all_module_activities(self):
        return {"orchestrator": 82.0, "consciousness": 91.0}


class DummyHealthAnalyzer:
    async def analyze_system_health(self, consciousness_metrics, module_activity, error_rates=None):
        return SystemHealthStatus(
            overall="STABLE",
            integration="RISING",
            coherence="GOOD",
            anxiety="CALM",
            flow="FLUENT",
            audit="CLEAN",
            details={"phi_value": consciousness_metrics.get("phi", 0.0)},
        )


class DummyBaselineSystem:
    def __init__(self):
        self.records = []

    def record_metric(self, metric_name, value):
        self.records.append((metric_name, value))

    def compare_with_baseline(self, metric_name, current_value):
        return SimpleNamespace(
            metric_name=metric_name,
            current_value=current_value,
            baseline_value=current_value,
            change=0.0,
            change_type="stable",
            significance="low",
        )


@pytest.mark.asyncio
async def test_dashboard_snapshot_includes_all_sections():
    aggregator = DashboardMetricsAggregator(
        consciousness_collector=DummyCollector(),  # type: ignore[arg-type]
        module_tracker=DummyModuleTracker(),  # type: ignore[arg-type]
        health_analyzer=DummyHealthAnalyzer(),  # type: ignore[arg-type]
        baseline_system=DummyBaselineSystem(),  # type: ignore[arg-type]
        system_metrics_fn=lambda: {
            "cpu_percent": 42.0,
            "memory_percent": 58.0,
            "disk_percent": 61.0,
        },
        cache_ttl_seconds=0,
    )

    snapshot = await aggregator.collect_snapshot()

    assert snapshot["system_metrics"]["cpu_percent"] == 42.0
    assert snapshot["module_activity"]["orchestrator"] == 82.0
    assert snapshot["consciousness_metrics"]["phi"] == pytest.approx(1.2)
    assert snapshot["baseline_comparison"]["phi"]["current"] == pytest.approx(1.2)
    assert snapshot["system_health"]["overall"] == "STABLE"
    assert snapshot["errors"] == []


@pytest.mark.asyncio
async def test_lightweight_snapshot_skips_consciousness():
    aggregator = DashboardMetricsAggregator(
        system_metrics_fn=lambda: {
            "cpu_percent": 10.0,
            "memory_percent": 20.0,
            "disk_percent": 30.0,
        },
        cache_ttl_seconds=0,
    )

    snapshot = await aggregator.collect_snapshot(include_consciousness=False)

    assert snapshot["system_metrics"]["cpu_percent"] == 10.0
    assert snapshot["consciousness_metrics"] is None


@pytest.mark.asyncio
async def test_persisted_metrics_used_when_live_unavailable(tmp_path, monkeypatch):
    aggregator = DashboardMetricsAggregator(
        consciousness_collector=None,
        system_metrics_fn=lambda: {
            "cpu_percent": 5.0,
            "memory_percent": 15.0,
            "disk_percent": 25.0,
        },
        cache_ttl_seconds=0,
    )

    persist_file = tmp_path / "data" / "monitor" / "real_metrics.json"
    persist_file.parent.mkdir(parents=True, exist_ok=True)
    persist_file.write_text(
        json.dumps(
            {
                "phi": 1.2,
                "ici": 0.85,
                "prs": 0.64,
                "anxiety": 0.22,
                "flow": 0.71,
                "entropy": 0.33,
                "ici_components": {"temporal_coherence": 0.8},
                "prs_components": {"avg_micro_entropy": 0.2},
                "history": {"phi": [1.1, 1.2], "ici": [0.82, 0.85]},
                "timestamp": "2025-12-04T12:00:00Z",
            }
        ),
        encoding="utf-8",
    )

    aggregator._persisted_metrics_file = persist_file

    snapshot = await aggregator.collect_snapshot()

    assert snapshot["consciousness_metrics"]["phi"] == pytest.approx(1.2)
    assert snapshot["consciousness_metrics"]["ICI"] == pytest.approx(0.85)
    assert snapshot["errors"][-1].startswith("consciousness_metrics: usando snapshot persistido")

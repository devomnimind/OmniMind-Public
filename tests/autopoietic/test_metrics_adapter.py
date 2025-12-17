import json

import src.autopoietic.metrics_adapter as metrics_adapter


class DummyPsutil:
    @staticmethod
    def cpu_percent(interval: float = 0.0):
        return 42.0


def test_collect_metrics_from_real_file(tmp_path, monkeypatch):
    real_metrics = {"phi": 0.8, "flow": 0.7, "anxiety": 0.1, "entropy": 0.3}
    metrics_path = tmp_path / "real_metrics.json"
    metrics_path.write_text(json.dumps(real_metrics), encoding="utf-8")

    monkeypatch.setattr(metrics_adapter, "psutil", DummyPsutil())

    sample = metrics_adapter.collect_metrics(real_metrics_path=str(metrics_path))

    assert sample.source == "real_metrics+psutil"
    assert 0.0 <= sample.error_rate <= 0.3
    assert sample.cpu_usage == 42.0
    assert sample.raw_metrics["phi"] == 0.8


def test_collect_metrics_fallback(monkeypatch):
    monkeypatch.setattr(metrics_adapter, "psutil", DummyPsutil())
    sample = metrics_adapter.collect_metrics(real_metrics_path="nonexistent.json")

    assert sample.source == "psutil_fallback"
    assert sample.cpu_usage == 42.0
    assert sample.raw_metrics == {}

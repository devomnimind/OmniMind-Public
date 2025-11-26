"""Tests for observability modules.

Tests distributed tracing, metrics export, log aggregation, and profiling tools.
"""

import json
import time
from pathlib import Path

import pytest

from src.observability.distributed_tracing import (
    DistributedTracer,
    SpanKind,
    SpanStatus,
    TraceConfig,
)
from src.observability.log_aggregator import (
    AlertSeverity,
    LogAggregator,
    LogConfig,
    LogLevel,
    LogPattern,
)
from src.observability.metrics_exporter import (
    CustomMetricsExporter,
    MetricsConfig,
    MetricType,
    MLMetrics,
)
from src.observability.profiling_tools import (
    ContinuousProfiler,
    FlameGraphGenerator,
    ProfilingConfig,
)


class TestDistributedTracing:
    """Tests for distributed tracing."""

    def test_trace_config_creation(self):
        """Test trace configuration creation."""
        config = TraceConfig(
            service_name="test-service",
            sample_rate=0.5,
        )
        assert config.service_name == "test-service"
        assert config.sample_rate == 0.5
        assert config.enabled is True

    def test_tracer_initialization(self):
        """Test tracer initialization."""
        config = TraceConfig(service_name="test")
        tracer = DistributedTracer(config)
        assert tracer.config.service_name == "test"
        assert tracer.get_active_traces_count() == 0

    def test_create_span_context(self):
        """Test span context creation."""
        config = TraceConfig()
        tracer = DistributedTracer(config)

        # Create root context
        context = tracer.create_context()
        assert context.trace_id is not None
        assert context.span_id is not None
        assert context.parent_span_id is None

        # Create child context
        child_context = tracer.create_context(parent=context)
        assert child_context.trace_id == context.trace_id
        assert child_context.parent_span_id == context.span_id

    def test_start_span(self):
        """Test span creation."""
        config = TraceConfig()
        tracer = DistributedTracer(config)

        span = tracer.start_span("test_operation")
        assert span.name == "test_operation"
        assert span.kind == SpanKind.INTERNAL
        assert span.status == SpanStatus.UNSET
        assert tracer.get_total_spans_count() == 1

    def test_trace_context_manager(self):
        """Test trace context manager."""
        config = TraceConfig()
        tracer = DistributedTracer(config)

        with tracer.trace("operation") as span:
            span.set_attribute("key", "value")
            span.add_event("test_event")

        assert span.status == SpanStatus.OK
        assert span.end_time is not None
        assert "key" in span.attributes

    def test_trace_error_handling(self):
        """Test trace error handling."""
        config = TraceConfig()
        tracer = DistributedTracer(config)

        with pytest.raises(ValueError):
            with tracer.trace("error_operation") as span:
                raise ValueError("test error")

        assert span.status == SpanStatus.ERROR
        assert "exception.type" in span.attributes

    def test_span_attributes(self):
        """Test span attributes."""
        config = TraceConfig()
        tracer = DistributedTracer(config)

        span = tracer.start_span("test", attributes={"initial": "value"})
        span.set_attribute("custom", "data")
        span.set_attribute("number", 42)

        assert span.attributes["initial"] == "value"
        assert span.attributes["custom"] == "data"
        assert span.attributes["number"] == 42

    def test_span_events(self):
        """Test span events."""
        config = TraceConfig()
        tracer = DistributedTracer(config)

        span = tracer.start_span("test")
        span.add_event("event1", {"detail": "info"})
        span.add_event("event2")

        assert len(span.events) == 2
        assert span.events[0]["name"] == "event1"

    def test_export_traces(self):
        """Test trace export."""
        config = TraceConfig(service_name="test")
        tracer = DistributedTracer(config)

        with tracer.trace("operation"):
            time.sleep(0.01)

        tracer.export_traces()
        # Verify trace file was created
        traces_dir = Path.home() / ".omnimind" / "traces"
        assert traces_dir.exists()

    def test_disabled_tracing(self):
        """Test disabled tracing."""
        config = TraceConfig(enabled=False)
        tracer = DistributedTracer(config)

        with tracer.trace("operation"):
            pass

        tracer.export_traces()
        # Should not create any traces
        assert tracer.get_active_traces_count() == 0


class TestMetricsExporter:
    """Tests for custom metrics exporter."""

    def test_metrics_config_creation(self):
        """Test metrics configuration."""
        config = MetricsConfig(
            prometheus_port=9090,
            export_format="prometheus",
        )
        assert config.prometheus_port == 9090
        assert config.enabled is True

    def test_exporter_initialization(self):
        """Test exporter initialization."""
        config = MetricsConfig()
        exporter = CustomMetricsExporter(config)
        assert exporter.get_metrics_count() > 0  # ML metrics auto-initialized

    def test_register_metric(self):
        """Test metric registration."""
        config = MetricsConfig(include_ml_metrics=False)
        exporter = CustomMetricsExporter(config)

        exporter.register_metric(
            "test_metric",
            MetricType.COUNTER,
            "Test metric",
            "count",
        )

        metric = exporter.get_metric("test_metric")
        assert metric is not None
        assert metric.name == "test_metric"
        assert metric.type == MetricType.COUNTER

    def test_record_counter(self):
        """Test counter metric recording."""
        config = MetricsConfig(include_ml_metrics=False)
        exporter = CustomMetricsExporter(config)

        exporter.record_counter("requests_total", 1)
        exporter.record_counter("requests_total", 1)

        metric = exporter.get_metric("requests_total")
        assert metric.get_latest_value() == 2.0

    def test_record_gauge(self):
        """Test gauge metric recording."""
        config = MetricsConfig(include_ml_metrics=False)
        exporter = CustomMetricsExporter(config)

        exporter.record_gauge("temperature", 25.5)
        exporter.record_gauge("temperature", 26.0)

        metric = exporter.get_metric("temperature")
        assert metric.get_latest_value() == 26.0

    def test_record_histogram(self):
        """Test histogram metric recording."""
        config = MetricsConfig(include_ml_metrics=False)
        exporter = CustomMetricsExporter(config)

        exporter.record_histogram("latency", 10.5)
        exporter.record_histogram("latency", 12.3)

        metric = exporter.get_metric("latency")
        assert len(metric.values) == 2

    def test_ml_metrics(self):
        """Test ML-specific metrics."""
        config = MetricsConfig()
        exporter = CustomMetricsExporter(config)

        ml_metrics = MLMetrics(
            model_inference_latency_ms=50.0,
            model_throughput_requests_per_sec=100.0,
            gpu_utilization_percent=75.0,
        )

        exporter.record_ml_metrics(ml_metrics)

        assert exporter.get_metric("model_inference_latency_ms") is not None
        assert exporter.get_metric("gpu_utilization") is not None

    def test_prometheus_export(self):
        """Test Prometheus format export."""
        config = MetricsConfig(include_ml_metrics=False)
        exporter = CustomMetricsExporter(config)

        exporter.record_counter("test_counter", 42)

        prometheus_text = exporter.export_prometheus()
        assert "test_counter" in prometheus_text
        assert "# TYPE" in prometheus_text
        assert "# HELP" in prometheus_text

    def test_json_export(self):
        """Test JSON format export."""
        config = MetricsConfig(include_ml_metrics=False)
        exporter = CustomMetricsExporter(config)

        exporter.record_gauge("test_gauge", 100.0)

        json_text = exporter.export_json()
        data = json.loads(json_text)
        assert "metrics" in data
        assert "test_gauge" in data["metrics"]

    def test_metric_labels(self):
        """Test metrics with labels."""
        config = MetricsConfig(include_ml_metrics=False)
        exporter = CustomMetricsExporter(config)

        exporter.record_counter("http_requests", 1, {"method": "GET"})
        exporter.record_counter("http_requests", 1, {"method": "POST"})

        metric = exporter.get_metric("http_requests")
        assert len(metric.values) == 2


class TestLogAggregator:
    """Tests for log aggregation."""

    def test_log_config_creation(self):
        """Test log configuration."""
        config = LogConfig(
            log_level=LogLevel.DEBUG,
            enable_pattern_detection=True,
        )
        assert config.log_level == LogLevel.DEBUG
        assert config.enabled is True

    def test_aggregator_initialization(self):
        """Test aggregator initialization."""
        config = LogConfig()
        aggregator = LogAggregator(config)
        assert aggregator.config.enabled is True

    def test_log_entry(self):
        """Test log entry creation."""
        config = LogConfig()
        aggregator = LogAggregator(config)

        aggregator.log(LogLevel.INFO, "Test message", "test_logger")

        logs = aggregator.get_logs()
        assert len(logs) == 1
        assert logs[0].message == "Test message"

    def test_log_pattern_detection(self):
        """Test pattern detection."""
        config = LogConfig()
        aggregator = LogAggregator(config)

        aggregator.log(LogLevel.ERROR, "Critical error occurred")

        alerts = aggregator.get_alerts()
        assert len(alerts) > 0
        # Should match "critical_error" pattern

    def test_custom_pattern(self):
        """Test custom pattern."""
        config = LogConfig()
        aggregator = LogAggregator(config)

        pattern = LogPattern(
            name="custom_pattern",
            regex=r"custom.*error",
            severity=AlertSeverity.HIGH,
            description="Custom error pattern",
        )
        aggregator.add_pattern(pattern)

        aggregator.log(LogLevel.ERROR, "custom test error")

        alerts = aggregator.get_alerts(severity=AlertSeverity.HIGH)
        assert any(a.pattern_name == "custom_pattern" for a in alerts)

    def test_log_analytics(self):
        """Test log analytics."""
        config = LogConfig()
        aggregator = LogAggregator(config)

        aggregator.log(LogLevel.INFO, "Info message 1")
        aggregator.log(LogLevel.INFO, "Info message 2")
        aggregator.log(LogLevel.ERROR, "Error message")

        analytics = aggregator.analyze()
        distribution = analytics.get_level_distribution()

        assert distribution["INFO"] == 2
        assert distribution["ERROR"] == 1

    def test_log_export(self):
        """Test log export."""
        config = LogConfig()
        aggregator = LogAggregator(config)

        aggregator.log(LogLevel.INFO, "Test")

        json_export = aggregator.export_logs("json")
        data = json.loads(json_export)
        assert "logs" in data
        assert len(data["logs"]) == 1


class TestProfilingTools:
    """Tests for profiling tools."""

    def test_profiling_config_creation(self):
        """Test profiling configuration."""
        config = ProfilingConfig(
            sample_interval_seconds=30,
            max_samples=500,
        )
        assert config.sample_interval_seconds == 30
        assert config.enabled is True

    def test_profiler_initialization(self):
        """Test profiler initialization."""
        config = ProfilingConfig()
        profiler = ContinuousProfiler(config)
        assert profiler.config.enabled is True

    def test_profile_decorator(self):
        """Test profile decorator."""
        config = ProfilingConfig()
        profiler = ContinuousProfiler(config)

        @profiler.profile
        def test_function():
            time.sleep(0.01)
            return "result"

        result = test_function()
        assert result == "result"

        samples = profiler.get_samples()
        assert len(samples) > 0

    def test_start_stop_profiling(self):
        """Test start/stop profiling."""
        config = ProfilingConfig()
        profiler = ContinuousProfiler(config)

        profiler.start()
        time.sleep(0.01)
        profiler.stop()

        samples = profiler.get_samples()
        assert len(samples) > 0

    def test_top_functions(self):
        """Test top functions."""
        config = ProfilingConfig()
        profiler = ContinuousProfiler(config)

        @profiler.profile
        def slow_function():
            time.sleep(0.02)

        @profiler.profile
        def fast_function():
            pass

        slow_function()
        fast_function()

        top = profiler.get_top_functions(limit=2)
        assert len(top) <= 2

    def test_flamegraph_generation(self):
        """Test flame graph generation."""
        config = ProfilingConfig()
        profiler = ContinuousProfiler(config)

        @profiler.profile
        def test_func():
            time.sleep(0.01)

        test_func()

        generator = FlameGraphGenerator()
        samples = profiler.get_samples()

        if samples:
            flame_graph = generator.generate(samples)
            assert flame_graph is not None
            assert flame_graph.name == "root"

    def test_flamegraph_json_export(self):
        """Test flame graph JSON export."""
        config = ProfilingConfig()
        profiler = ContinuousProfiler(config)

        @profiler.profile
        def test_func():
            pass

        test_func()

        generator = FlameGraphGenerator()
        samples = profiler.get_samples()

        if samples:
            flame_graph = generator.generate(samples)
            json_output = generator.to_json(flame_graph)
            data = json.loads(json_output)
            assert "name" in data
            assert "value" in data

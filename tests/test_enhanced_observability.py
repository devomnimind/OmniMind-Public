"""Tests for enhanced observability modules.

Tests OpenTelemetry integration, performance analyzer, and enhanced features.
"""

import time

import pytest

from src.observability.opentelemetry_integration import (
    OpenTelemetryConfig,
    OpenTelemetryIntegration,
)
from src.observability.performance_analyzer import (
    BottleneckCategory,
    BottleneckSeverity,
    PerformanceAnalyzer,
)
from src.observability.profiling_tools import ProfileSample


class TestOpenTelemetryIntegration:
    """Tests for OpenTelemetry integration."""

    def test_config_creation(self) -> None:
        """Test OpenTelemetry configuration creation."""
        config = OpenTelemetryConfig(
            service_name="test-service",
            environment="testing",
            enable_console_export=True,
        )
        assert config.service_name == "test-service"
        assert config.environment == "testing"
        assert config.enable_console_export is True

    def test_integration_initialization(self) -> None:
        """Test OpenTelemetry integration initialization."""
        config = OpenTelemetryConfig(service_name="test")
        otel = OpenTelemetryIntegration(config)
        assert otel.config.service_name == "test"
        assert not otel._initialized

    def test_integration_lifecycle(self) -> None:
        """Test OpenTelemetry initialization and shutdown."""
        config = OpenTelemetryConfig(
            service_name="test",
            enable_console_export=True,
        )
        otel = OpenTelemetryIntegration(config)

        # Initialize
        otel.initialize()
        assert otel._initialized

        # Get tracer
        tracer = otel.get_tracer("test")
        assert tracer is not None

        # Get meter
        meter = otel.get_meter("test")
        assert meter is not None

        # Shutdown
        otel.shutdown()
        assert not otel._initialized

    def test_get_status(self) -> None:
        """Test status reporting."""
        config = OpenTelemetryConfig(
            service_name="test",
            enable_console_export=True,
            enable_jaeger_export=True,
        )
        otel = OpenTelemetryIntegration(config)
        otel.initialize()

        status = otel.get_status()
        assert status["initialized"] is True
        assert status["service_name"] == "test"
        assert "console" in status["exporters"]
        assert "jaeger" in status["exporters"]

        otel.shutdown()

    def test_tracer_before_initialization(self) -> None:
        """Test that getting tracer before initialization raises error."""
        config = OpenTelemetryConfig()
        otel = OpenTelemetryIntegration(config)

        with pytest.raises(RuntimeError, match="not initialized"):
            otel.get_tracer()


class TestPerformanceAnalyzer:
    """Tests for performance bottleneck analyzer."""

    def test_analyzer_initialization(self) -> None:
        """Test analyzer initialization."""
        analyzer = PerformanceAnalyzer()
        assert analyzer._reports_dir.exists()

    def test_analyze_empty_samples(self) -> None:
        """Test analyzing with no samples."""
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze([])

        assert report.sample_count == 0
        assert report.total_execution_time_ms == 0.0
        assert len(report.bottlenecks) == 0
        assert "No profiling data" in report.summary

    def test_analyze_with_samples(self) -> None:
        """Test analyzing with sample data."""
        analyzer = PerformanceAnalyzer()

        # Create mock samples
        samples = [
            ProfileSample(
                timestamp=time.time(),
                function_name="slow_function",
                filename="test.py",
                line_number=10,
                call_count=100,
                total_time_ms=500.0,
                cumulative_time_ms=800.0,
            ),
            ProfileSample(
                timestamp=time.time(),
                function_name="fast_function",
                filename="test.py",
                line_number=20,
                call_count=1000,
                total_time_ms=50.0,
                cumulative_time_ms=50.0,
            ),
        ]

        report = analyzer.analyze(samples, min_percentage=1.0)

        assert report.sample_count == 2
        assert report.total_execution_time_ms > 0
        assert len(report.bottlenecks) > 0
        assert len(report.recommendations) > 0

    def test_categorize_io_bottleneck(self) -> None:
        """Test I/O bottleneck categorization."""
        analyzer = PerformanceAnalyzer()

        sample = ProfileSample(
            timestamp=time.time(),
            function_name="read_file",
            filename="io.py",
            line_number=10,
            call_count=10,
            total_time_ms=500.0,
            cumulative_time_ms=500.0,
        )

        category = analyzer._categorize_bottleneck(sample)
        assert category == BottleneckCategory.IO_BOUND

    def test_categorize_network_bottleneck(self) -> None:
        """Test network bottleneck categorization."""
        analyzer = PerformanceAnalyzer()

        sample = ProfileSample(
            timestamp=time.time(),
            function_name="http_request",
            filename="api.py",
            line_number=10,
            call_count=10,
            total_time_ms=1000.0,
            cumulative_time_ms=1000.0,
        )

        category = analyzer._categorize_bottleneck(sample)
        assert category == BottleneckCategory.NETWORK_BOUND

    def test_determine_severity_critical(self) -> None:
        """Test critical severity determination."""
        analyzer = PerformanceAnalyzer()

        sample = ProfileSample(
            timestamp=time.time(),
            function_name="critical_func",
            filename="test.py",
            line_number=10,
            call_count=10,
            total_time_ms=5000.0,
            cumulative_time_ms=5000.0,
        )

        # 100% of total time
        severity = analyzer._determine_severity(100.0, sample)
        assert severity == BottleneckSeverity.CRITICAL

    def test_determine_severity_low(self) -> None:
        """Test low severity determination."""
        analyzer = PerformanceAnalyzer()

        sample = ProfileSample(
            timestamp=time.time(),
            function_name="minor_func",
            filename="test.py",
            line_number=10,
            call_count=100,
            total_time_ms=10.0,
            cumulative_time_ms=10.0,
        )

        # 2% of total time
        severity = analyzer._determine_severity(2.0, sample)
        assert severity == BottleneckSeverity.LOW

    def test_save_report(
        self, tmp_path: pytest.TempPathFactory  # type: ignore[name-defined]
    ) -> None:
        """Test saving performance report."""
        analyzer = PerformanceAnalyzer()
        analyzer._reports_dir = tmp_path  # type: ignore[assignment]

        report = analyzer.analyze([])
        analyzer.save_report(report, "test_report.json")

        assert tmp_path.joinpath("test_report.json").exists()  # type: ignore[arg-type]

    def test_report_to_dict(self) -> None:
        """Test report serialization."""
        analyzer = PerformanceAnalyzer()
        report = analyzer.analyze([])

        report_dict = report.to_dict()
        assert "timestamp" in report_dict
        assert "datetime" in report_dict
        assert "bottlenecks" in report_dict
        assert "summary" in report_dict
        assert "recommendations" in report_dict

    def test_bottleneck_to_dict(self) -> None:
        """Test bottleneck serialization."""
        analyzer = PerformanceAnalyzer()

        sample = ProfileSample(
            timestamp=time.time(),
            function_name="test_func",
            filename="test.py",
            line_number=10,
            call_count=100,
            total_time_ms=500.0,
            cumulative_time_ms=500.0,
        )

        bottlenecks = analyzer._identify_bottlenecks([sample], 1000.0, 1.0)
        assert len(bottlenecks) > 0

        bottleneck_dict = bottlenecks[0].to_dict()
        assert "function" in bottleneck_dict
        assert "category" in bottleneck_dict
        assert "severity" in bottleneck_dict
        assert "recommendation" in bottleneck_dict

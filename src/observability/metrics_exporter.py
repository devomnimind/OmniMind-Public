"""Custom Metrics Exporter Module.

Implements business and ML-specific metrics exporters with Prometheus compatibility.
Exports custom metrics for machine learning workloads, model performance, and system health.

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 8.2
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class MetricType(Enum):
    """Metric types following Prometheus model."""

    COUNTER = "counter"  # Monotonically increasing value
    GAUGE = "gauge"  # Value that can go up or down
    HISTOGRAM = "histogram"  # Distribution of values
    SUMMARY = "summary"  # Similar to histogram with percentiles


@dataclass
class MetricValue:
    """Single metric measurement.

    Attributes:
        value: The metric value
        timestamp: When the measurement was taken
        labels: Additional labels for the metric
    """

    value: float
    timestamp: float = field(default_factory=time.time)
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
        }


@dataclass
class Metric:
    """Represents a single metric with its metadata.

    Attributes:
        name: Metric name (should be snake_case)
        type: Metric type
        help_text: Description of what this metric measures
        unit: Unit of measurement (e.g., 'seconds', 'bytes')
        values: List of metric values
    """

    name: str
    type: MetricType
    help_text: str
    unit: str = ""
    values: List[MetricValue] = field(default_factory=list)

    def add_value(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Add a new value to the metric.

        Args:
            value: The metric value
            labels: Optional labels for this value
        """
        metric_value = MetricValue(value=value, labels=labels or {})
        self.values.append(metric_value)

    def get_latest_value(self) -> Optional[float]:
        """Get the most recent value."""
        if not self.values:
            return None
        return self.values[-1].value

    def to_prometheus_format(self) -> str:
        """Export metric in Prometheus text format.

        Returns:
            Prometheus-formatted metric string
        """
        lines = []

        # Help text
        lines.append(f"# HELP {self.name} {self.help_text}")

        # Type
        lines.append(f"# TYPE {self.name} {self.type.value}")

        # Values
        for metric_value in self.values:
            if metric_value.labels:
                labels_str = ",".join(
                    f'{k}="{v}"' for k, v in metric_value.labels.items()
                )
                lines.append(
                    f"{self.name}{{{labels_str}}} {metric_value.value} "
                    f"{int(metric_value.timestamp * 1000)}"
                )
            else:
                lines.append(
                    f"{self.name} {metric_value.value} "
                    f"{int(metric_value.timestamp * 1000)}"
                )

        return "\n".join(lines)


@dataclass
class MLMetrics:
    """ML-specific metrics container.

    Attributes:
        model_inference_latency_ms: Inference time in milliseconds
        model_throughput_requests_per_sec: Requests processed per second
        model_accuracy: Model accuracy score
        model_loss: Training/validation loss
        gpu_utilization_percent: GPU utilization percentage
        gpu_memory_used_mb: GPU memory usage in MB
        batch_size: Current batch size
        tokens_per_second: Token generation rate
        cache_hit_rate: Model cache hit rate
    """

    model_inference_latency_ms: float = 0.0
    model_throughput_requests_per_sec: float = 0.0
    model_accuracy: float = 0.0
    model_loss: float = 0.0
    gpu_utilization_percent: float = 0.0
    gpu_memory_used_mb: float = 0.0
    batch_size: int = 0
    tokens_per_second: float = 0.0
    cache_hit_rate: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_inference_latency_ms": self.model_inference_latency_ms,
            "model_throughput_requests_per_sec": self.model_throughput_requests_per_sec,
            "model_accuracy": self.model_accuracy,
            "model_loss": self.model_loss,
            "gpu_utilization_percent": self.gpu_utilization_percent,
            "gpu_memory_used_mb": self.gpu_memory_used_mb,
            "batch_size": self.batch_size,
            "tokens_per_second": self.tokens_per_second,
            "cache_hit_rate": self.cache_hit_rate,
        }


@dataclass
class MetricsConfig:
    """Configuration for metrics exporter.

    Attributes:
        enabled: Whether metrics export is enabled
        export_interval_seconds: Interval between exports
        prometheus_port: Port for Prometheus metrics endpoint
        export_format: Export format (prometheus, json, both)
        retention_hours: How long to keep metrics in memory
        include_ml_metrics: Whether to include ML-specific metrics
    """

    enabled: bool = True
    export_interval_seconds: int = 15
    prometheus_port: int = 9090
    export_format: str = "prometheus"  # prometheus, json, both
    retention_hours: int = 24
    include_ml_metrics: bool = True


class CustomMetricsExporter:
    """Custom metrics exporter for ML workloads.

    Provides Prometheus-compatible metrics export with ML-specific business metrics.
    Supports multiple export formats and automatic metric collection.

    Example:
        >>> config = MetricsConfig(prometheus_port=9090)
        >>> exporter = CustomMetricsExporter(config)
        >>> exporter.record_counter("requests_total", 1, {"endpoint": "/api/task"})
        >>> exporter.record_gauge("gpu_utilization", 85.5)
        >>> metrics = exporter.export_metrics()
    """

    def __init__(self, config: MetricsConfig):
        """Initialize the metrics exporter.

        Args:
            config: Metrics configuration
        """
        self.config = config
        self._metrics: Dict[str, Metric] = {}
        self._ml_metrics_history: List[MLMetrics] = []
        self._metrics_dir = Path.home() / ".omnimind" / "metrics"
        self._metrics_dir.mkdir(parents=True, exist_ok=True)

        # Initialize standard ML metrics if enabled
        if config.include_ml_metrics:
            self._initialize_ml_metrics()

        logger.info(
            "metrics_exporter_initialized",
            port=config.prometheus_port,
            format=config.export_format,
        )

    def _initialize_ml_metrics(self) -> None:
        """Initialize standard ML metrics."""
        ml_metric_definitions = [
            (
                "model_inference_latency_ms",
                MetricType.HISTOGRAM,
                "Model inference latency",
                "milliseconds",
            ),
            (
                "model_throughput_rps",
                MetricType.GAUGE,
                "Model throughput",
                "requests/second",
            ),
            ("model_accuracy", MetricType.GAUGE, "Model accuracy score", "percentage"),
            ("model_loss", MetricType.GAUGE, "Model training/validation loss", ""),
            ("gpu_utilization", MetricType.GAUGE, "GPU utilization", "percentage"),
            ("gpu_memory_used_mb", MetricType.GAUGE, "GPU memory usage", "megabytes"),
            ("batch_size", MetricType.GAUGE, "Current batch size", ""),
            (
                "tokens_per_second",
                MetricType.GAUGE,
                "Token generation rate",
                "tokens/second",
            ),
            ("cache_hit_rate", MetricType.GAUGE, "Model cache hit rate", "percentage"),
        ]

        for name, metric_type, help_text, unit in ml_metric_definitions:
            self.register_metric(name, metric_type, help_text, unit)

    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        help_text: str,
        unit: str = "",
    ) -> None:
        """Register a new metric.

        Args:
            name: Metric name (snake_case)
            metric_type: Type of metric
            help_text: Description of the metric
            unit: Unit of measurement
        """
        if name in self._metrics:
            logger.warning("metric_already_registered", name=name)
            return

        metric = Metric(
            name=name,
            type=metric_type,
            help_text=help_text,
            unit=unit,
        )
        self._metrics[name] = metric

        logger.debug("metric_registered", name=name, type=metric_type.value)

    def record_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a counter metric (monotonically increasing).

        Args:
            name: Metric name
            value: Value to add (default 1.0)
            labels: Optional labels
        """
        if name not in self._metrics:
            self.register_metric(name, MetricType.COUNTER, f"Counter: {name}")

        metric = self._metrics[name]
        if metric.type != MetricType.COUNTER:
            logger.warning("metric_type_mismatch", name=name, expected="counter")
            return

        # For counters, we accumulate the value
        current_value = metric.get_latest_value() or 0.0
        metric.add_value(current_value + value, labels)

    def record_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a gauge metric (can go up or down).

        Args:
            name: Metric name
            value: Current value
            labels: Optional labels
        """
        if name not in self._metrics:
            self.register_metric(name, MetricType.GAUGE, f"Gauge: {name}")

        metric = self._metrics[name]
        if metric.type != MetricType.GAUGE:
            logger.warning("metric_type_mismatch", name=name, expected="gauge")
            return

        metric.add_value(value, labels)

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a histogram metric (distribution of values).

        Args:
            name: Metric name
            value: Observed value
            labels: Optional labels
        """
        if name not in self._metrics:
            self.register_metric(name, MetricType.HISTOGRAM, f"Histogram: {name}")

        metric = self._metrics[name]
        if metric.type != MetricType.HISTOGRAM:
            logger.warning("metric_type_mismatch", name=name, expected="histogram")
            return

        metric.add_value(value, labels)

    def record_ml_metrics(self, ml_metrics: MLMetrics) -> None:
        """Record ML-specific metrics.

        Args:
            ml_metrics: ML metrics container
        """
        if not self.config.include_ml_metrics:
            return

        # Record individual metrics
        self.record_histogram(
            "model_inference_latency_ms", ml_metrics.model_inference_latency_ms
        )
        self.record_gauge(
            "model_throughput_rps", ml_metrics.model_throughput_requests_per_sec
        )
        self.record_gauge("model_accuracy", ml_metrics.model_accuracy)
        self.record_gauge("model_loss", ml_metrics.model_loss)
        self.record_gauge("gpu_utilization", ml_metrics.gpu_utilization_percent)
        self.record_gauge("gpu_memory_used_mb", ml_metrics.gpu_memory_used_mb)
        self.record_gauge("batch_size", float(ml_metrics.batch_size))
        self.record_gauge("tokens_per_second", ml_metrics.tokens_per_second)
        self.record_gauge("cache_hit_rate", ml_metrics.cache_hit_rate)

        # Store in history
        self._ml_metrics_history.append(ml_metrics)

        # Cleanup old metrics
        self._cleanup_old_metrics()

    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name.

        Args:
            name: Metric name

        Returns:
            Metric if found, None otherwise
        """
        return self._metrics.get(name)

    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all registered metrics.

        Returns:
            Dictionary of all metrics
        """
        return self._metrics.copy()

    def export_prometheus(self) -> str:
        """Export all metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []
        for metric in self._metrics.values():
            lines.append(metric.to_prometheus_format())
            lines.append("")  # Empty line between metrics

        return "\n".join(lines)

    def export_json(self) -> str:
        """Export all metrics in JSON format.

        Returns:
            JSON-formatted metrics string
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                name: {
                    "type": metric.type.value,
                    "help": metric.help_text,
                    "unit": metric.unit,
                    "values": [v.to_dict() for v in metric.values],
                }
                for name, metric in self._metrics.items()
            },
        }
        return json.dumps(data, indent=2)

    def export_metrics(self) -> Dict[str, str]:
        """Export metrics in configured format(s).

        Returns:
            Dictionary with exported metrics (format -> content)
        """
        if not self.config.enabled:
            return {}

        result = {}

        if self.config.export_format in ("prometheus", "both"):
            result["prometheus"] = self.export_prometheus()

        if self.config.export_format in ("json", "both"):
            result["json"] = self.export_json()

        return result

    def save_metrics(self) -> None:
        """Save metrics to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.config.export_format in ("prometheus", "both"):
            filename = self._metrics_dir / f"metrics_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(self.export_prometheus())
            logger.info("prometheus_metrics_saved", filename=str(filename))

        if self.config.export_format in ("json", "both"):
            filename = self._metrics_dir / f"metrics_{timestamp}.json"
            with open(filename, "w") as f:
                f.write(self.export_json())
            logger.info("json_metrics_saved", filename=str(filename))

    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period."""
        cutoff_time = time.time() - (self.config.retention_hours * 3600)

        for metric in self._metrics.values():
            metric.values = [v for v in metric.values if v.timestamp >= cutoff_time]

        # Cleanup ML metrics history
        self._ml_metrics_history = [
            m
            for m in self._ml_metrics_history
            if hasattr(m, "timestamp") or True  # Keep all for now
        ]

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        for metric in self._metrics.values():
            metric.values.clear()
        self._ml_metrics_history.clear()
        logger.info("metrics_reset")

    def get_metrics_count(self) -> int:
        """Get number of registered metrics."""
        return len(self._metrics)

    def get_total_values_count(self) -> int:
        """Get total number of metric values across all metrics."""
        return sum(len(m.values) for m in self._metrics.values())

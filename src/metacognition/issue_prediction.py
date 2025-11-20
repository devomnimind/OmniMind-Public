"""Proactive issue prediction using ML-based failure prediction.

This module implements predictive analytics for system health:
- Time-series analysis of system metrics
- Anomaly detection using statistical methods
- Resource exhaustion prediction
- Failure probability estimation
"""

from __future__ import annotations

import logging
import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics to track."""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_LATENCY = "network_latency"
    REQUEST_RATE = "request_rate"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"


class PredictionSeverity(str, Enum):
    """Severity levels for predictions."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricDataPoint:
    """Single data point for a metric."""

    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IssuePrediction:
    """Predicted issue with probability and timeline."""

    metric_type: MetricType
    severity: PredictionSeverity
    probability: float  # 0.0 to 1.0
    predicted_time: Optional[datetime]
    description: str
    recommended_actions: List[str]
    confidence: float  # 0.0 to 1.0
    supporting_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metric_type": self.metric_type.value,
            "severity": self.severity.value,
            "probability": self.probability,
            "predicted_time": (
                self.predicted_time.isoformat() if self.predicted_time else None
            ),
            "description": self.description,
            "recommended_actions": self.recommended_actions,
            "confidence": self.confidence,
            "supporting_data": self.supporting_data,
        }


class TimeSeriesAnalyzer:
    """Analyzes time-series data for trend detection and prediction."""

    def __init__(self, window_size: int = 100) -> None:
        """Initialize time-series analyzer.

        Args:
            window_size: Number of recent data points to keep
        """
        self.window_size = window_size
        self._data: Dict[MetricType, Deque[MetricDataPoint]] = {}
        for metric in MetricType:
            self._data[metric] = deque(maxlen=window_size)

    def add_data_point(
        self,
        metric_type: MetricType,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a data point to the time series.

        Args:
            metric_type: Type of metric
            value: Metric value
            metadata: Optional metadata
        """
        data_point = MetricDataPoint(
            timestamp=datetime.now(),
            value=value,
            metadata=metadata or {},
        )
        self._data[metric_type].append(data_point)
        logger.debug(f"Added data point for {metric_type.value}: {value}")

    def get_trend(self, metric_type: MetricType) -> Optional[float]:
        """Calculate trend slope using linear regression.

        Args:
            metric_type: Type of metric

        Returns:
            Trend slope (positive = increasing, negative = decreasing)
        """
        data = self._data.get(metric_type, deque())
        if len(data) < 2:
            return None

        # Simple linear regression
        n = len(data)
        x = np.arange(n)
        y = np.array([point.value for point in data])

        # Calculate slope: (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
        x_sum = np.sum(x)
        y_sum = np.sum(y)
        xy_sum = np.sum(x * y)
        x2_sum = np.sum(x * x)

        denominator = n * x2_sum - x_sum * x_sum
        if denominator == 0:
            return 0.0

        slope = (n * xy_sum - x_sum * y_sum) / denominator
        return float(slope)

    def detect_anomaly(
        self, metric_type: MetricType, threshold: float = 2.0
    ) -> Tuple[bool, float]:
        """Detect anomalies using Z-score method.

        Args:
            metric_type: Type of metric
            threshold: Z-score threshold for anomaly detection

        Returns:
            Tuple of (is_anomaly, z_score)
        """
        data = self._data.get(metric_type, deque())
        if len(data) < 3:
            return False, 0.0

        values = [point.value for point in data]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        if stdev == 0:
            return False, 0.0

        # Check the most recent value
        current_value = values[-1]
        z_score = abs(current_value - mean) / stdev

        return z_score > threshold, z_score

    def predict_resource_exhaustion(
        self, metric_type: MetricType, threshold: float = 95.0
    ) -> Optional[datetime]:
        """Predict when a resource will be exhausted.

        Args:
            metric_type: Type of metric (should be percentage-based)
            threshold: Exhaustion threshold (e.g., 95%)

        Returns:
            Predicted exhaustion time or None
        """
        data = self._data.get(metric_type, deque())
        if len(data) < 10:
            return None

        trend = self.get_trend(metric_type)
        if trend is None or trend <= 0:
            return None

        # Get current value
        current_value = data[-1].value
        if current_value >= threshold:
            return datetime.now()

        # Calculate time to exhaustion
        remaining = threshold - current_value
        points_to_exhaustion = remaining / trend

        if points_to_exhaustion <= 0:
            return None

        # Assume 1 minute per data point (configurable)
        minutes_to_exhaustion = points_to_exhaustion
        return datetime.now() + timedelta(minutes=minutes_to_exhaustion)

    def get_statistics(self, metric_type: MetricType) -> Dict[str, float]:
        """Get statistical summary of a metric.

        Args:
            metric_type: Type of metric

        Returns:
            Dictionary with statistical measures
        """
        data = self._data.get(metric_type, deque())
        if not data:
            return {}

        values = [point.value for point in data]
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
            "min": min(values),
            "max": max(values),
            "current": values[-1],
            "trend": self.get_trend(metric_type) or 0.0,
        }


class IssuePredictionEngine:
    """Engine for predicting potential issues before they occur."""

    def __init__(self, window_size: int = 100) -> None:
        """Initialize issue prediction engine.

        Args:
            window_size: Number of data points to keep for analysis
        """
        self.analyzer = TimeSeriesAnalyzer(window_size=window_size)
        self._thresholds = {
            MetricType.CPU_USAGE: 85.0,
            MetricType.MEMORY_USAGE: 90.0,
            MetricType.DISK_USAGE: 85.0,
            MetricType.ERROR_RATE: 5.0,
        }
        self._predictions: List[IssuePrediction] = []
        self._prediction_history: List[IssuePrediction] = []

    def update_metric(
        self,
        metric_type: MetricType,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update metric value and trigger prediction analysis.

        Args:
            metric_type: Type of metric
            value: Metric value
            metadata: Optional metadata
        """
        self.analyzer.add_data_point(metric_type, value, metadata)

        # Trigger prediction after each update
        predictions = self.predict_issues()
        if predictions:
            logger.info(f"Generated {len(predictions)} new predictions")

    def predict_issues(self) -> List[IssuePrediction]:
        """Predict potential issues based on current metrics.

        Returns:
            List of predicted issues
        """
        predictions: List[IssuePrediction] = []

        for metric_type in MetricType:
            # Check for resource exhaustion
            if metric_type in self._thresholds:
                exhaustion_pred = self._predict_resource_exhaustion(metric_type)
                if exhaustion_pred:
                    predictions.append(exhaustion_pred)

            # Check for anomalies
            anomaly_pred = self._predict_anomaly(metric_type)
            if anomaly_pred:
                predictions.append(anomaly_pred)

            # Check for performance degradation
            degradation_pred = self._predict_performance_degradation(metric_type)
            if degradation_pred:
                predictions.append(degradation_pred)

        self._predictions = predictions
        self._prediction_history.extend(predictions)
        return predictions

    def _predict_resource_exhaustion(
        self, metric_type: MetricType
    ) -> Optional[IssuePrediction]:
        """Predict resource exhaustion for a metric."""
        threshold = self._thresholds.get(metric_type)
        if threshold is None:
            return None

        predicted_time = self.analyzer.predict_resource_exhaustion(
            metric_type, threshold
        )
        if predicted_time is None:
            return None

        time_until_exhaustion = predicted_time - datetime.now()
        hours_until = time_until_exhaustion.total_seconds() / 3600

        # Only warn if exhaustion is within 24 hours
        if hours_until > 24:
            return None

        severity = (
            PredictionSeverity.CRITICAL
            if hours_until < 1
            else PredictionSeverity.WARNING
        )
        probability = min(0.9, 0.5 + (24 - hours_until) / 48)

        stats = self.analyzer.get_statistics(metric_type)

        return IssuePrediction(
            metric_type=metric_type,
            severity=severity,
            probability=probability,
            predicted_time=predicted_time,
            description=(
                f"{metric_type.value.replace('_', ' ').title()} "
                f"predicted to exceed {threshold}% in {hours_until:.1f} hours"
            ),
            recommended_actions=[
                f"Monitor {metric_type.value} closely",
                "Consider scaling resources",
                "Review recent changes that may have caused increase",
                "Prepare emergency capacity expansion",
            ],
            confidence=0.7 if hours_until < 2 else 0.5,
            supporting_data={
                "current_value": stats.get("current", 0.0),
                "trend": stats.get("trend", 0.0),
                "threshold": threshold,
                "hours_until_exhaustion": hours_until,
            },
        )

    def _predict_anomaly(self, metric_type: MetricType) -> Optional[IssuePrediction]:
        """Predict anomaly-based issues."""
        is_anomaly, z_score = self.analyzer.detect_anomaly(metric_type, threshold=2.5)

        if not is_anomaly:
            return None

        severity = (
            PredictionSeverity.CRITICAL if z_score > 4.0 else PredictionSeverity.WARNING
        )
        probability = min(0.95, z_score / 5.0)

        stats = self.analyzer.get_statistics(metric_type)

        return IssuePrediction(
            metric_type=metric_type,
            severity=severity,
            probability=probability,
            predicted_time=datetime.now(),
            description=(
                f"Anomaly detected in {metric_type.value.replace('_', ' ').title()} "
                f"(Z-score: {z_score:.2f})"
            ),
            recommended_actions=[
                "Investigate recent system changes",
                "Check for unusual workload patterns",
                "Review logs for errors or warnings",
                "Consider rollback if issue correlates with recent deployment",
            ],
            confidence=0.8,
            supporting_data={
                "z_score": z_score,
                "current_value": stats.get("current", 0.0),
                "mean": stats.get("mean", 0.0),
                "stdev": stats.get("stdev", 0.0),
            },
        )

    def _predict_performance_degradation(
        self, metric_type: MetricType
    ) -> Optional[IssuePrediction]:
        """Predict performance degradation."""
        # Only applicable to performance metrics
        if metric_type not in [MetricType.RESPONSE_TIME, MetricType.NETWORK_LATENCY]:
            return None

        stats = self.analyzer.get_statistics(metric_type)
        trend = stats.get("trend", 0.0)

        # Check if performance is degrading (increasing response time/latency)
        if trend <= 0:
            return None

        # Check if trend is significant
        mean = stats.get("mean", 0.0)
        if mean == 0 or abs(trend / mean) < 0.05:  # Less than 5% change
            return None

        probability = min(0.9, abs(trend / mean))
        severity = PredictionSeverity.WARNING

        return IssuePrediction(
            metric_type=metric_type,
            severity=severity,
            probability=probability,
            predicted_time=None,
            description=(
                f"Performance degradation detected in "
                f"{metric_type.value.replace('_', ' ').title()} "
                f"(trending {trend:.2f}ms/min upward)"
            ),
            recommended_actions=[
                "Review system performance metrics",
                "Check for resource bottlenecks",
                "Investigate recent code or configuration changes",
                "Consider performance profiling",
            ],
            confidence=0.6,
            supporting_data={
                "trend": trend,
                "current_value": stats.get("current", 0.0),
                "mean": mean,
                "change_rate": abs(trend / mean) if mean > 0 else 0.0,
            },
        )

    def get_current_predictions(self) -> List[IssuePrediction]:
        """Get current active predictions.

        Returns:
            List of active predictions
        """
        return self._predictions.copy()

    def get_prediction_history(self) -> List[IssuePrediction]:
        """Get all historical predictions.

        Returns:
            List of all predictions
        """
        return self._prediction_history.copy()

    def clear_predictions(self) -> None:
        """Clear current predictions (keeps history)."""
        self._predictions.clear()

    def get_metrics_summary(self) -> Dict[str, Dict[str, float]]:
        """Get statistical summary of all metrics.

        Returns:
            Dictionary mapping metric types to their statistics
        """
        summary = {}
        for metric_type in MetricType:
            stats = self.analyzer.get_statistics(metric_type)
            if stats:
                summary[metric_type.value] = stats
        return summary

"""Self-Optimization Engine with A/B testing and automated performance tuning.

This module implements automated system optimization:
- A/B testing framework for configuration changes
- Automated performance tuning
- Configuration optimization based on metrics
- Safe rollback mechanisms
"""

from __future__ import annotations

import logging
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class OptimizationStrategy(str, Enum):
    """Optimization strategies."""

    AB_TEST = "ab_test"
    GRADIENT_DESCENT = "gradient_descent"
    HILL_CLIMBING = "hill_climbing"
    BAYESIAN = "bayesian"


class ExperimentStatus(str, Enum):
    """Status of optimization experiment."""

    PLANNING = "planning"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Configuration:
    """Represents a system configuration."""

    config_id: str
    name: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "config_id": self.config_id,
            "name": self.name,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for a configuration."""

    timestamp: datetime
    response_time_ms: float
    throughput_rps: float  # requests per second
    error_rate: float  # 0.0 to 1.0
    cpu_usage: float  # 0.0 to 100.0
    memory_usage: float  # 0.0 to 100.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def get_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted score.

        Args:
            weights: Optional weights for each metric

        Returns:
            Overall performance score (higher is better)
        """
        if weights is None:
            weights = {
                "response_time": 0.3,
                "throughput": 0.3,
                "error_rate": 0.2,
                "resource_usage": 0.2,
            }

        # Normalize metrics (0-1 scale, higher is better)
        norm_response_time = max(0, 1 - (self.response_time_ms / 1000))  # < 1s is good
        norm_throughput = min(1, self.throughput_rps / 100)  # 100 RPS is excellent
        norm_error_rate = 1 - self.error_rate
        norm_resource = 1 - ((self.cpu_usage + self.memory_usage) / 200)

        score = (
            norm_response_time * weights["response_time"]
            + norm_throughput * weights["throughput"]
            + norm_error_rate * weights["error_rate"]
            + norm_resource * weights["resource_usage"]
        )

        return max(0, min(1, score))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "response_time_ms": self.response_time_ms,
            "throughput_rps": self.throughput_rps,
            "error_rate": self.error_rate,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "custom_metrics": self.custom_metrics,
            "score": self.get_score(),
        }


@dataclass
class ABTest:
    """Represents an A/B test experiment."""

    test_id: str
    name: str
    control_config: Configuration
    treatment_config: Configuration
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: ExperimentStatus = ExperimentStatus.PLANNING
    control_metrics: List[PerformanceMetrics] = field(default_factory=list)
    treatment_metrics: List[PerformanceMetrics] = field(default_factory=list)
    traffic_split: float = 0.5  # 0.0 to 1.0 (percentage to treatment)
    min_samples: int = 100
    confidence_threshold: float = 0.95

    def add_control_metric(self, metrics: PerformanceMetrics) -> None:
        """Add metrics from control group."""
        self.control_metrics.append(metrics)

    def add_treatment_metric(self, metrics: PerformanceMetrics) -> None:
        """Add metrics from treatment group."""
        self.treatment_metrics.append(metrics)

    def has_sufficient_data(self) -> bool:
        """Check if we have enough data to analyze."""
        return (
            len(self.control_metrics) >= self.min_samples
            and len(self.treatment_metrics) >= self.min_samples
        )

    def get_results(self) -> Dict[str, Any]:
        """Analyze test results.

        Returns:
            Dictionary with analysis results
        """
        if not self.has_sufficient_data():
            return {
                "status": "insufficient_data",
                "control_samples": len(self.control_metrics),
                "treatment_samples": len(self.treatment_metrics),
                "min_samples": self.min_samples,
            }

        control_scores = [m.get_score() for m in self.control_metrics]
        treatment_scores = [m.get_score() for m in self.treatment_metrics]

        control_mean = statistics.mean(control_scores)
        treatment_mean = statistics.mean(treatment_scores)

        improvement = (
            (treatment_mean - control_mean) / control_mean if control_mean > 0 else 0
        )

        # Simple statistical test (t-test would be better, but requires scipy)
        (
            statistics.stdev(control_scores) if len(control_scores) > 1 else 0
        )
        (
            statistics.stdev(treatment_scores) if len(treatment_scores) > 1 else 0
        )

        # Calculate confidence (simplified)
        confidence = min(0.99, 0.5 + abs(improvement) * 0.5)

        winner = "treatment" if treatment_mean > control_mean else "control"
        is_significant = (
            confidence >= self.confidence_threshold and abs(improvement) > 0.05
        )

        return {
            "status": "complete",
            "winner": winner if is_significant else "tie",
            "control_mean": control_mean,
            "treatment_mean": treatment_mean,
            "improvement": improvement,
            "confidence": confidence,
            "is_significant": is_significant,
            "control_samples": len(self.control_metrics),
            "treatment_samples": len(self.treatment_metrics),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "name": self.name,
            "control_config": self.control_config.to_dict(),
            "treatment_config": self.treatment_config.to_dict(),
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status.value,
            "traffic_split": self.traffic_split,
            "results": self.get_results() if self.has_sufficient_data() else None,
        }


class SelfOptimizationEngine:
    """Engine for automated system optimization."""

    def __init__(self, metric_weights: Optional[Dict[str, float]] = None) -> None:
        """Initialize optimization engine.

        Args:
            metric_weights: Optional weights for performance scoring
        """
        self._metric_weights = metric_weights
        self._active_tests: Dict[str, ABTest] = {}
        self._completed_tests: List[ABTest] = []
        self._current_config: Optional[Configuration] = None
        self._baseline_metrics: List[PerformanceMetrics] = []
        self._optimization_history: List[Dict[str, Any]] = []

    def set_baseline_configuration(self, config: Configuration) -> None:
        """Set the baseline configuration.

        Args:
            config: Baseline configuration
        """
        self._current_config = config
        logger.info(f"Set baseline configuration: {config.config_id}")

    def create_ab_test(
        self,
        test_id: str,
        name: str,
        treatment_config: Configuration,
        traffic_split: float = 0.5,
        min_samples: int = 100,
    ) -> ABTest:
        """Create a new A/B test.

        Args:
            test_id: Unique test identifier
            name: Test name
            treatment_config: Configuration to test
            traffic_split: Percentage of traffic to treatment (0.0-1.0)
            min_samples: Minimum samples needed

        Returns:
            Created AB test
        """
        if self._current_config is None:
            raise ValueError("No baseline configuration set")

        test = ABTest(
            test_id=test_id,
            name=name,
            control_config=self._current_config,
            treatment_config=treatment_config,
            started_at=datetime.now(),
            traffic_split=traffic_split,
            min_samples=min_samples,
            status=ExperimentStatus.PLANNING,
        )

        self._active_tests[test_id] = test
        logger.info(f"Created A/B test: {test_id}")

        return test

    def start_test(self, test_id: str) -> None:
        """Start an A/B test.

        Args:
            test_id: Test to start
        """
        test = self._active_tests.get(test_id)
        if not test:
            raise ValueError(f"Test not found: {test_id}")

        test.status = ExperimentStatus.RUNNING
        test.started_at = datetime.now()
        logger.info(f"Started A/B test: {test_id}")

    def record_metrics(
        self,
        test_id: str,
        metrics: PerformanceMetrics,
        is_treatment: bool,
    ) -> None:
        """Record performance metrics for a test.

        Args:
            test_id: Test ID
            metrics: Performance metrics
            is_treatment: True if from treatment group
        """
        test = self._active_tests.get(test_id)
        if not test:
            raise ValueError(f"Test not found: {test_id}")

        if is_treatment:
            test.add_treatment_metric(metrics)
        else:
            test.add_control_metric(metrics)

        logger.debug(
            f"Recorded metrics for {test_id} ({'treatment' if is_treatment else 'control'})"
        )

    def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """Analyze test results.

        Args:
            test_id: Test to analyze

        Returns:
            Analysis results
        """
        test = self._active_tests.get(test_id)
        if not test:
            raise ValueError(f"Test not found: {test_id}")

        test.status = ExperimentStatus.ANALYZING
        results = test.get_results()

        if results.get("status") == "complete":
            test.status = ExperimentStatus.COMPLETED
            test.ended_at = datetime.now()

            # Record optimization history
            self._optimization_history.append(
                {
                    "test_id": test_id,
                    "timestamp": datetime.now().isoformat(),
                    "results": results,
                }
            )

        logger.info(f"Analyzed test {test_id}: {results.get('winner', 'unknown')} won")
        return results

    def apply_winner(self, test_id: str) -> Configuration:
        """Apply the winning configuration.

        Args:
            test_id: Test ID

        Returns:
            Applied configuration
        """
        test = self._active_tests.get(test_id)
        if not test:
            raise ValueError(f"Test not found: {test_id}")

        if test.status != ExperimentStatus.COMPLETED:
            raise ValueError("Test must be completed before applying winner")

        results = test.get_results()
        winner = results.get("winner")

        if winner == "treatment" and results.get("is_significant"):
            self._current_config = test.treatment_config
            logger.info(f"Applied treatment configuration from test {test_id}")
        else:
            logger.info(f"Kept control configuration (test {test_id})")

        # Move to completed tests
        self._completed_tests.append(test)
        del self._active_tests[test_id]

        return self._current_config

    def rollback(self, test_id: str) -> Configuration:
        """Rollback a test to control configuration.

        Args:
            test_id: Test to rollback

        Returns:
            Control configuration
        """
        test = self._active_tests.get(test_id)
        if not test:
            # Check completed tests
            test = next(
                (t for t in self._completed_tests if t.test_id == test_id), None
            )
            if not test:
                raise ValueError(f"Test not found: {test_id}")

        test.status = ExperimentStatus.ROLLED_BACK
        self._current_config = test.control_config

        logger.info(f"Rolled back test {test_id} to control configuration")
        return self._current_config

    def auto_tune_parameter(
        self,
        parameter_name: str,
        current_value: Any,
        value_range: Tuple[Any, Any],
        step_size: Any,
        samples_per_value: int = 50,
    ) -> Tuple[Any, float]:
        """Automatically tune a single parameter using hill climbing.

        Args:
            parameter_name: Parameter to tune
            current_value: Current value
            value_range: (min, max) range
            step_size: Step size for search
            samples_per_value: Metrics samples per value

        Returns:
            Tuple of (best_value, best_score)
        """
        if self._current_config is None:
            raise ValueError("No baseline configuration set")

        best_value = current_value
        best_score = 0.0

        # Try values in range
        min_val, max_val = value_range
        current = min_val

        logger.info(
            f"Auto-tuning parameter {parameter_name} in range [{min_val}, {max_val}]"
        )

        value_scores: List[Tuple[Any, float]] = []

        while current <= max_val:
            # This is a simplified version - in reality, you'd need to:
            # 1. Apply the configuration
            # 2. Collect metrics
            # 3. Calculate score
            # For now, we'll simulate this

            # Placeholder score (in real implementation, collect actual metrics)
            score = 0.5  # Would be calculated from real metrics

            value_scores.append((current, score))

            if score > best_score:
                best_score = score
                best_value = current

            current += step_size

        self._optimization_history.append(
            {
                "type": "auto_tune",
                "parameter": parameter_name,
                "timestamp": datetime.now().isoformat(),
                "best_value": best_value,
                "best_score": best_score,
                "value_scores": value_scores,
            }
        )

        logger.info(
            f"Auto-tuned {parameter_name}: best value={best_value}, score={best_score}"
        )

        return best_value, best_score

    def get_current_configuration(self) -> Optional[Configuration]:
        """Get current active configuration.

        Returns:
            Current configuration or None
        """
        return self._current_config

    def get_active_tests(self) -> List[ABTest]:
        """Get all active tests.

        Returns:
            List of active tests
        """
        return list(self._active_tests.values())

    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history.

        Returns:
            List of optimization events
        """
        return self._optimization_history.copy()

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary.

        Returns:
            Performance summary
        """
        if not self._baseline_metrics:
            return {"status": "no_data"}

        recent_metrics = self._baseline_metrics[-100:]  # Last 100 samples
        scores = [m.get_score(self._metric_weights) for m in recent_metrics]

        return {
            "current_config": (
                self._current_config.config_id if self._current_config else None
            ),
            "avg_score": statistics.mean(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "total_optimizations": len(self._optimization_history),
            "active_tests": len(self._active_tests),
        }

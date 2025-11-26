"""Performance Bottleneck Analyzer Module.

Provides automated analysis of performance bottlenecks from profiling data.
Generates actionable insights and recommendations for optimization.

Reference: Problem Statement - FRENTE 4: Performance Profiling
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog

from src.observability.profiling_tools import ProfileSample

logger = structlog.get_logger(__name__)


class BottleneckSeverity(Enum):
    """Severity levels for performance bottlenecks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BottleneckCategory(Enum):
    """Categories of performance bottlenecks."""

    CPU_INTENSIVE = "cpu_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    IO_BOUND = "io_bound"
    NETWORK_BOUND = "network_bound"
    INEFFICIENT_ALGORITHM = "inefficient_algorithm"
    FREQUENT_CALLS = "frequent_calls"
    LONG_RUNNING = "long_running"


@dataclass
class PerformanceBottleneck:
    """Represents a detected performance bottleneck.

    Attributes:
        function_name: Name of the function
        filename: File containing the function
        category: Bottleneck category
        severity: Bottleneck severity
        cumulative_time_ms: Total time spent in function
        call_count: Number of times function was called
        per_call_time_ms: Average time per call
        percentage_of_total: Percentage of total execution time
        recommendation: Optimization recommendation
        details: Additional details
    """

    function_name: str
    filename: str
    category: BottleneckCategory
    severity: BottleneckSeverity
    cumulative_time_ms: float
    call_count: int
    per_call_time_ms: float
    percentage_of_total: float
    recommendation: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "function": self.function_name,
            "file": self.filename,
            "category": self.category.value,
            "severity": self.severity.value,
            "cumulative_time_ms": self.cumulative_time_ms,
            "call_count": self.call_count,
            "per_call_time_ms": self.per_call_time_ms,
            "percentage_of_total": self.percentage_of_total,
            "recommendation": self.recommendation,
            "details": self.details,
        }


@dataclass
class PerformanceReport:
    """Performance analysis report.

    Attributes:
        timestamp: Report generation timestamp
        total_execution_time_ms: Total execution time analyzed
        sample_count: Number of samples analyzed
        bottlenecks: List of detected bottlenecks
        summary: Executive summary
        recommendations: Top recommendations
    """

    timestamp: float
    total_execution_time_ms: float
    sample_count: int
    bottlenecks: List[PerformanceBottleneck]
    summary: str
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "total_execution_time_ms": self.total_execution_time_ms,
            "sample_count": self.sample_count,
            "bottleneck_count": len(self.bottlenecks),
            "bottlenecks": [b.to_dict() for b in self.bottlenecks],
            "summary": self.summary,
            "recommendations": self.recommendations,
        }


class PerformanceAnalyzer:
    """Performance bottleneck analyzer.

    Analyzes profiling data to identify performance bottlenecks and
    generate optimization recommendations.

    Example:
        >>> from src.observability.profiling_tools import ContinuousProfiler
        >>> profiler = ContinuousProfiler(ProfilingConfig())
        >>> # ... run application with profiling ...
        >>> samples = profiler.get_samples()
        >>> analyzer = PerformanceAnalyzer()
        >>> report = analyzer.analyze(samples)
        >>> print(report.summary)
    """

    def __init__(self) -> None:
        """Initialize performance analyzer."""
        self._reports_dir = Path.home() / ".omnimind" / "performance_reports"
        self._reports_dir.mkdir(parents=True, exist_ok=True)

        logger.info("performance_analyzer_initialized")

    def analyze(
        self,
        samples: List[ProfileSample],
        min_percentage: float = 1.0,
    ) -> PerformanceReport:
        """Analyze profiling samples for bottlenecks.

        Args:
            samples: List of profiling samples
            min_percentage: Minimum percentage of total time to report

        Returns:
            Performance analysis report
        """
        if not samples:
            logger.warning("no_samples_to_analyze")
            return PerformanceReport(
                timestamp=datetime.now().timestamp(),
                total_execution_time_ms=0.0,
                sample_count=0,
                bottlenecks=[],
                summary="No profiling data available for analysis.",
            )

        # Calculate total execution time
        total_time = sum(s.cumulative_time_ms for s in samples)

        # Identify bottlenecks
        bottlenecks = self._identify_bottlenecks(samples, total_time, min_percentage)

        # Sort by severity and impact
        bottlenecks.sort(
            key=lambda b: (
                self._severity_weight(b.severity),
                b.percentage_of_total,
            ),
            reverse=True,
        )

        # Generate summary and recommendations
        summary = self._generate_summary(bottlenecks, total_time, len(samples))
        recommendations = self._generate_recommendations(bottlenecks)

        report = PerformanceReport(
            timestamp=datetime.now().timestamp(),
            total_execution_time_ms=total_time,
            sample_count=len(samples),
            bottlenecks=bottlenecks,
            summary=summary,
            recommendations=recommendations,
        )

        logger.info(
            "performance_analysis_complete",
            bottleneck_count=len(bottlenecks),
            total_time_ms=total_time,
        )

        return report

    def _identify_bottlenecks(
        self,
        samples: List[ProfileSample],
        total_time: float,
        min_percentage: float,
    ) -> List[PerformanceBottleneck]:
        """Identify performance bottlenecks from samples.

        Args:
            samples: Profiling samples
            total_time: Total execution time
            min_percentage: Minimum percentage threshold

        Returns:
            List of bottlenecks
        """
        bottlenecks: List[PerformanceBottleneck] = []

        for sample in samples:
            percentage = (
                (sample.cumulative_time_ms / total_time * 100) if total_time > 0 else 0
            )

            if percentage < min_percentage:
                continue

            # Categorize bottleneck
            category = self._categorize_bottleneck(sample)

            # Determine severity
            severity = self._determine_severity(percentage, sample)

            # Generate recommendation
            recommendation = self._generate_recommendation(category, sample)

            bottleneck = PerformanceBottleneck(
                function_name=sample.function_name,
                filename=sample.filename,
                category=category,
                severity=severity,
                cumulative_time_ms=sample.cumulative_time_ms,
                call_count=sample.call_count,
                per_call_time_ms=sample.per_call_time_ms,
                percentage_of_total=percentage,
                recommendation=recommendation,
                details={
                    "line_number": sample.line_number,
                    "total_time_ms": sample.total_time_ms,
                },
            )

            bottlenecks.append(bottleneck)

        return bottlenecks

    def _categorize_bottleneck(self, sample: ProfileSample) -> BottleneckCategory:
        """Categorize a bottleneck based on sample characteristics.

        Args:
            sample: Profile sample

        Returns:
            Bottleneck category
        """
        # Heuristics for categorization
        function_lower = sample.function_name.lower()

        # I/O operations
        if any(
            keyword in function_lower
            for keyword in ["read", "write", "open", "close", "file", "io"]
        ):
            return BottleneckCategory.IO_BOUND

        # Network operations
        if any(
            keyword in function_lower
            for keyword in ["request", "http", "socket", "network", "fetch"]
        ):
            return BottleneckCategory.NETWORK_BOUND

        # Frequent calls (high call count, low per-call time)
        if sample.call_count > 1000 and sample.per_call_time_ms < 1.0:
            return BottleneckCategory.FREQUENT_CALLS

        # Long running (low call count, high per-call time)
        if sample.call_count < 10 and sample.per_call_time_ms > 100:
            return BottleneckCategory.LONG_RUNNING

        # Memory operations
        if any(
            keyword in function_lower
            for keyword in ["alloc", "memory", "cache", "buffer"]
        ):
            return BottleneckCategory.MEMORY_INTENSIVE

        # Default to CPU intensive
        return BottleneckCategory.CPU_INTENSIVE

    def _determine_severity(
        self, percentage: float, sample: ProfileSample
    ) -> BottleneckSeverity:
        """Determine bottleneck severity.

        Args:
            percentage: Percentage of total time
            sample: Profile sample

        Returns:
            Severity level
        """
        if percentage >= 30 or sample.per_call_time_ms > 1000:
            return BottleneckSeverity.CRITICAL
        elif percentage >= 15 or sample.per_call_time_ms > 500:
            return BottleneckSeverity.HIGH
        elif percentage >= 5 or sample.per_call_time_ms > 100:
            return BottleneckSeverity.MEDIUM
        else:
            return BottleneckSeverity.LOW

    def _generate_recommendation(
        self, category: BottleneckCategory, sample: ProfileSample
    ) -> str:
        """Generate optimization recommendation.

        Args:
            category: Bottleneck category
            sample: Profile sample

        Returns:
            Recommendation text
        """
        recommendations = {
            BottleneckCategory.CPU_INTENSIVE: (
                f"Consider optimizing algorithm in {sample.function_name}. "
                "Look for opportunities to reduce computational complexity or use caching."
            ),
            BottleneckCategory.IO_BOUND: (
                f"I/O operations in {sample.function_name} are blocking. "
                "Consider using async I/O, buffering, or batch operations."
            ),
            BottleneckCategory.NETWORK_BOUND: (
                f"Network operations in {sample.function_name} are slow. "
                "Consider connection pooling, request batching, or caching responses."
            ),
            BottleneckCategory.FREQUENT_CALLS: (
                f"{sample.function_name} is called {sample.call_count} times. "
                "Consider memoization, reducing call frequency, or batch processing."
            ),
            BottleneckCategory.LONG_RUNNING: (
                f"{sample.function_name} takes {sample.per_call_time_ms:.2f}ms per call. "
                "Consider breaking into smaller operations or running asynchronously."
            ),
            BottleneckCategory.MEMORY_INTENSIVE: (
                f"Memory operations in {sample.function_name} may be inefficient. "
                "Consider using generators, reducing allocations, or optimizing data structures."
            ),
            BottleneckCategory.INEFFICIENT_ALGORITHM: (
                f"Algorithm in {sample.function_name} may be inefficient. "
                "Review algorithmic complexity and consider alternative approaches."
            ),
        }

        return recommendations.get(
            category,
            f"Optimize {sample.function_name} to reduce execution time.",
        )

    def _generate_summary(
        self,
        bottlenecks: List[PerformanceBottleneck],
        total_time: float,
        sample_count: int,
    ) -> str:
        """Generate executive summary.

        Args:
            bottlenecks: List of bottlenecks
            total_time: Total execution time
            sample_count: Number of samples

        Returns:
            Summary text
        """
        if not bottlenecks:
            return "No significant performance bottlenecks detected."

        critical_count = sum(
            1 for b in bottlenecks if b.severity == BottleneckSeverity.CRITICAL
        )
        high_count = sum(
            1 for b in bottlenecks if b.severity == BottleneckSeverity.HIGH
        )

        top_bottleneck = bottlenecks[0]

        summary = (
            f"Performance analysis of {sample_count} samples ({total_time:.2f}ms total). "
            f"Found {len(bottlenecks)} bottlenecks: "
            f"{critical_count} critical, {high_count} high severity. "
            f"Top bottleneck: {top_bottleneck.function_name} "
            f"({top_bottleneck.percentage_of_total:.1f}% of total time)."
        )

        return summary

    def _generate_recommendations(
        self, bottlenecks: List[PerformanceBottleneck]
    ) -> List[str]:
        """Generate top recommendations.

        Args:
            bottlenecks: List of bottlenecks

        Returns:
            List of recommendations
        """
        recommendations = []

        # Top 5 bottlenecks
        for bottleneck in bottlenecks[:5]:
            recommendations.append(
                f"[{bottleneck.severity.value.upper()}] {bottleneck.recommendation}"
            )

        return recommendations

    def save_report(
        self, report: PerformanceReport, filename: Optional[str] = None
    ) -> str:
        """Save performance report to file.

        Args:
            report: Performance report
            filename: Optional filename

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.fromtimestamp(report.timestamp).strftime(
                "%Y%m%d_%H%M%S"
            )
            filename = f"performance_report_{timestamp}.json"

        filepath = self._reports_dir / filename

        with open(filepath, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

        logger.info("performance_report_saved", filename=str(filepath))
        return str(filepath)

    @staticmethod
    def _severity_weight(severity: BottleneckSeverity) -> int:
        """Get numeric weight for severity."""
        weights = {
            BottleneckSeverity.CRITICAL: 4,
            BottleneckSeverity.HIGH: 3,
            BottleneckSeverity.MEDIUM: 2,
            BottleneckSeverity.LOW: 1,
        }
        return weights.get(severity, 0)

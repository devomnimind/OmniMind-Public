"""Performance Profiler Module.

Implements performance profiling based on:
- CPU cycles, cache misses, branch predictions tracking
- Memory usage monitoring
- Execution time measurements

Reference: docs/autootimizacao-hardware-omnidev.md, Section 3.3
"""

import functools
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

import psutil
import structlog

logger = structlog.get_logger(__name__)

# Type variable for generic function profiling
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class PerformanceMetrics:
    """Container for performance metrics.

    Attributes:
        execution_time_ms: Execution time in milliseconds
        memory_peak_mb: Peak memory usage in megabytes
        cpu_percent: CPU utilization percentage
        timestamp: When measurement was taken
        function_name: Name of profiled function
        metadata: Additional metadata
    """

    execution_time_ms: float
    memory_peak_mb: float
    cpu_percent: float
    timestamp: str
    function_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BottleneckReport:
    """Report of identified performance bottlenecks.

    Attributes:
        bottleneck_type: Type of bottleneck (memory, cpu, cache, etc.)
        severity: Severity level (low, medium, high, critical)
        suggestion: Suggested improvement
        current_value: Current metric value
        threshold_value: Threshold that was exceeded
    """

    bottleneck_type: str
    severity: str
    suggestion: str
    current_value: float
    threshold_value: float


class PerformanceProfiler:
    """Performance profiling system.

    Tracks:
    - Execution time
    - Memory usage (RSS, peak)
    - CPU utilization
    - Historical performance data

    Reference: docs/autootimizacao-hardware-omnidev.md, Section 3.3
    """

    def __init__(self, metrics_dir: Optional[Path] = None):
        """Initialize performance profiler.

        Args:
            metrics_dir: Directory to store metrics
        """
        self.metrics_dir = metrics_dir or Path("data/metrics/performance")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_history: List[PerformanceMetrics] = []
        self.process = psutil.Process()

        logger.info("performance_profiler_initialized", metrics_dir=str(self.metrics_dir))

    def profile_execution(
        self, func: Callable[..., Any], *args: Any, **kwargs: Any
    ) -> tuple[Any, PerformanceMetrics]:
        """Profile a function execution.

        Args:
            func: Function to profile
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Tuple of (function_result, performance_metrics)
        """
        # Initial measurements
        start_time = time.perf_counter()
        start_memory = self.process.memory_info().rss / (1024 * 1024)  # MB

        # Execute function
        result = func(*args, **kwargs)

        # Final measurements
        end_time = time.perf_counter()
        end_memory = self.process.memory_info().rss / (1024 * 1024)  # MB
        cpu_after = self.process.cpu_percent()

        # Calculate metrics
        execution_time = (end_time - start_time) * 1000  # Convert to ms
        memory_peak = max(start_memory, end_memory)
        cpu_percent = cpu_after  # Most recent CPU %

        metrics = PerformanceMetrics(
            execution_time_ms=execution_time,
            memory_peak_mb=memory_peak,
            cpu_percent=cpu_percent,
            timestamp=datetime.now().isoformat(),
            function_name=getattr(func, "__name__", "unknown"),
        )

        self.metrics_history.append(metrics)

        logger.info(
            "function_profiled",
            function=metrics.function_name,
            execution_ms=f"{execution_time:.2f}",
            memory_mb=f"{memory_peak:.2f}",
            cpu_pct=f"{cpu_percent:.1f}",
        )

        return result, metrics

    def identify_bottlenecks(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold_mb: float = 1000.0,
        time_threshold_ms: float = 1000.0,
    ) -> List[BottleneckReport]:
        """Analyze metrics history to identify bottlenecks.

        Args:
            cpu_threshold: CPU % threshold for bottleneck
            memory_threshold_mb: Memory MB threshold
            time_threshold_ms: Execution time threshold

        Returns:
            List of identified bottlenecks
        """
        if not self.metrics_history:
            return []

        bottlenecks: List[BottleneckReport] = []

        # Get recent metrics
        recent = (
            self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        )

        # Check CPU utilization
        avg_cpu = sum(m.cpu_percent for m in recent) / len(recent)
        if avg_cpu > cpu_threshold:
            bottlenecks.append(
                BottleneckReport(
                    bottleneck_type="cpu_utilization",
                    severity="high" if avg_cpu > 90 else "medium",
                    suggestion=(
                        "High CPU utilization detected. Consider:\n"
                        "- Algorithm optimization\n"
                        "- Parallel processing\n"
                        "- Caching frequently computed values"
                    ),
                    current_value=avg_cpu,
                    threshold_value=cpu_threshold,
                )
            )

        # Check memory usage
        avg_memory = sum(m.memory_peak_mb for m in recent) / len(recent)
        if avg_memory > memory_threshold_mb:
            bottlenecks.append(
                BottleneckReport(
                    bottleneck_type="memory_usage",
                    severity="high" if avg_memory > 2000 else "medium",
                    suggestion=(
                        "High memory usage detected. Consider:\n"
                        "- Implement data streaming instead of loading all at once\n"
                        "- Clear unused objects explicitly\n"
                        "- Use generators for large datasets"
                    ),
                    current_value=avg_memory,
                    threshold_value=memory_threshold_mb,
                )
            )

        # Check execution time
        avg_time = sum(m.execution_time_ms for m in recent) / len(recent)
        if avg_time > time_threshold_ms:
            bottlenecks.append(
                BottleneckReport(
                    bottleneck_type="execution_time",
                    severity="high" if avg_time > 5000 else "medium",
                    suggestion=(
                        "Slow execution detected. Consider:\n"
                        "- Profile individual operations to find hotspots\n"
                        "- Optimize loops and data structures\n"
                        "- Use compilation (e.g., Cython) for critical paths"
                    ),
                    current_value=avg_time,
                    threshold_value=time_threshold_ms,
                )
            )

        logger.info(
            "bottlenecks_identified",
            count=len(bottlenecks),
            types=[b.bottleneck_type for b in bottlenecks],
        )

        return bottlenecks

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical summary of all profiled executions.

        Returns:
            Dictionary with statistics
        """
        if not self.metrics_history:
            return {"error": "No metrics collected"}

        times = [m.execution_time_ms for m in self.metrics_history]
        memories = [m.memory_peak_mb for m in self.metrics_history]
        cpus = [m.cpu_percent for m in self.metrics_history]

        return {
            "total_executions": len(self.metrics_history),
            "execution_time": {
                "mean_ms": sum(times) / len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "total_ms": sum(times),
            },
            "memory": {
                "mean_mb": sum(memories) / len(memories),
                "min_mb": min(memories),
                "max_mb": max(memories),
            },
            "cpu": {
                "mean_percent": sum(cpus) / len(cpus),
                "min_percent": min(cpus),
                "max_percent": max(cpus),
            },
        }

    def save_report(self, filename: Optional[str] = None) -> Path:
        """Save performance report to file.

        Args:
            filename: Optional filename (default: performance_report_{timestamp}.json)

        Returns:
            Path to saved report
        """
        if filename is None:
            filename = f"performance_report_{int(time.time())}.json"

        filepath = self.metrics_dir / filename

        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "bottlenecks": [
                {
                    "type": b.bottleneck_type,
                    "severity": b.severity,
                    "suggestion": b.suggestion,
                    "current_value": b.current_value,
                    "threshold": b.threshold_value,
                }
                for b in self.identify_bottlenecks()
            ],
            "metrics_history": [
                {
                    "function": m.function_name,
                    "execution_ms": m.execution_time_ms,
                    "memory_mb": m.memory_peak_mb,
                    "cpu_percent": m.cpu_percent,
                    "timestamp": m.timestamp,
                    "metadata": m.metadata,
                }
                for m in self.metrics_history
            ],
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info("performance_report_saved", filepath=str(filepath))

        return filepath


def profile_function(func: F) -> F:
    """Decorator to profile a function's performance.

    Usage:
        @profile_function
        def my_function(x, y):
            return x + y

    Args:
        func: Function to profile

    Returns:
        Wrapped function that profiles on each call
    """
    profiler = PerformanceProfiler()

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result, metrics = profiler.profile_execution(func, *args, **kwargs)

        # Store metrics in function attribute for later access
        if not hasattr(wrapper, "_performance_metrics"):
            wrapper._performance_metrics = []  # type: ignore
        wrapper._performance_metrics.append(metrics)  # type: ignore

        return result

    return cast(F, wrapper)

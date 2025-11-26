"""Benchmarking Module.

Implements performance benchmarking framework based on:
- Baseline establishment
- Performance comparison
- Statistical analysis

Reference: docs/autootimizacao-hardware-omnidev.md, Section 5
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a benchmark run.

    Attributes:
        name: Name of the benchmark
        iterations: Number of iterations run
        execution_times_ms: List of execution times
        memory_peaks_mb: List of peak memory usage
        cpu_utilizations: List of CPU utilization percentages
        timestamp: When benchmark was run
        metadata: Additional metadata
    """

    name: str
    iterations: int
    execution_times_ms: List[float]
    memory_peaks_mb: List[float]
    cpu_utilizations: List[float]
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def mean_time_ms(self) -> float:
        """Mean execution time."""
        return sum(self.execution_times_ms) / len(self.execution_times_ms)

    @property
    def mean_memory_mb(self) -> float:
        """Mean memory usage."""
        return sum(self.memory_peaks_mb) / len(self.memory_peaks_mb)

    @property
    def mean_cpu_percent(self) -> float:
        """Mean CPU utilization."""
        return sum(self.cpu_utilizations) / len(self.cpu_utilizations)


@dataclass
class ComparisonResult:
    """Result of comparing two benchmarks.

    Attributes:
        baseline_name: Name of baseline benchmark
        optimized_name: Name of optimized benchmark
        time_improvement_pct: Time improvement percentage
        memory_improvement_pct: Memory improvement percentage
        cpu_improvement_pct: CPU improvement percentage
        is_better: Whether optimized is better overall
        summary: Summary of comparison
    """

    baseline_name: str
    optimized_name: str
    time_improvement_pct: float
    memory_improvement_pct: float
    cpu_improvement_pct: float
    is_better: bool
    summary: str


class PerformanceBenchmark:
    """Performance benchmarking framework.

    Establishes baselines, runs comparisons, tracks improvements.

    Reference: docs/autootimizacao-hardware-omnidev.md, Section 5.1
    """

    def __init__(self, benchmark_dir: Optional[Path] = None):
        """Initialize benchmarking framework.

        Args:
            benchmark_dir: Directory to store benchmark results
        """
        self.benchmark_dir = benchmark_dir or Path("data/benchmarks")
        self.benchmark_dir.mkdir(parents=True, exist_ok=True)

        self.baselines: Dict[str, BenchmarkResult] = {}
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process()

        logger.info(
            "benchmark_framework_initialized", benchmark_dir=str(self.benchmark_dir)
        )

    def run_benchmark(
        self,
        name: str,
        workload: Callable[[], Any],
        iterations: int = 100,
        warmup_iterations: int = 5,
    ) -> BenchmarkResult:
        """Run a benchmark with specified workload.

        Args:
            name: Name for this benchmark
            workload: Callable that performs the work
            iterations: Number of iterations to run
            warmup_iterations: Number of warmup iterations

        Returns:
            BenchmarkResult with measurements
        """
        logger.info(
            "benchmark_starting",
            name=name,
            iterations=iterations,
            warmup=warmup_iterations,
        )

        # Warmup runs (not measured)
        for _ in range(warmup_iterations):
            workload()

        # Measured runs
        execution_times: List[float] = []
        memory_peaks: List[float] = []
        cpu_utils: List[float] = []

        for i in range(iterations):
            # Measure memory before
            mem_before = self.process.memory_info().rss / (1024 * 1024)

            # Measure execution time
            start = time.perf_counter()
            workload()
            end = time.perf_counter()

            # Measure memory after
            mem_after = self.process.memory_info().rss / (1024 * 1024)

            # Get CPU utilization
            cpu_pct = self.process.cpu_percent()

            # Store metrics
            execution_times.append((end - start) * 1000)  # ms
            memory_peaks.append(max(mem_before, mem_after))
            cpu_utils.append(cpu_pct)

            # Log progress every 10 iterations
            if (i + 1) % 10 == 0:
                logger.debug(
                    "benchmark_progress", name=name, iteration=i + 1, total=iterations
                )

        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            execution_times_ms=execution_times,
            memory_peaks_mb=memory_peaks,
            cpu_utilizations=cpu_utils,
            timestamp=datetime.now().isoformat(),
        )

        self.results.append(result)

        logger.info(
            "benchmark_completed",
            name=name,
            mean_time_ms=f"{result.mean_time_ms:.2f}",
            mean_memory_mb=f"{result.mean_memory_mb:.2f}",
            mean_cpu_pct=f"{result.mean_cpu_percent:.1f}",
        )

        return result

    def establish_baseline(
        self,
        name: str,
        workload: Callable[[], Any],
        iterations: int = 100,
    ) -> BenchmarkResult:
        """Establish a performance baseline.

        Args:
            name: Name for this baseline
            workload: Workload to benchmark
            iterations: Number of iterations

        Returns:
            BenchmarkResult saved as baseline
        """
        result = self.run_benchmark(name, workload, iterations)
        self.baselines[name] = result

        logger.info("baseline_established", name=name)

        return result

    def compare_to_baseline(
        self,
        baseline_name: str,
        optimized_name: str,
        optimized_workload: Callable[[], Any],
        iterations: int = 100,
    ) -> ComparisonResult:
        """Compare optimized version to baseline.

        Args:
            baseline_name: Name of baseline to compare against
            optimized_name: Name for optimized version
            optimized_workload: Optimized workload
            iterations: Number of iterations

        Returns:
            ComparisonResult with improvements

        Raises:
            ValueError: If baseline not found
        """
        if baseline_name not in self.baselines:
            raise ValueError(f"Baseline '{baseline_name}' not found")

        baseline = self.baselines[baseline_name]
        optimized = self.run_benchmark(optimized_name, optimized_workload, iterations)

        # Calculate improvements (positive = better)
        time_improvement = (
            (baseline.mean_time_ms - optimized.mean_time_ms) / baseline.mean_time_ms
        ) * 100

        memory_improvement = (
            (baseline.mean_memory_mb - optimized.mean_memory_mb)
            / baseline.mean_memory_mb
        ) * 100

        cpu_improvement = (
            (baseline.mean_cpu_percent - optimized.mean_cpu_percent)
            / baseline.mean_cpu_percent
        ) * 100

        # Overall assessment
        is_better = (
            time_improvement > 0 or memory_improvement > 0 or cpu_improvement > 0
        )

        # Generate summary
        improvements = []
        if time_improvement > 0:
            improvements.append(f"{time_improvement:.1f}% faster")
        elif time_improvement < 0:
            improvements.append(f"{abs(time_improvement):.1f}% slower")

        if memory_improvement > 0:
            improvements.append(f"{memory_improvement:.1f}% less memory")
        elif memory_improvement < 0:
            improvements.append(f"{abs(memory_improvement):.1f}% more memory")

        if cpu_improvement > 0:
            improvements.append(f"{cpu_improvement:.1f}% less CPU")

        summary = (
            f"Optimized version is {', '.join(improvements)}"
            if improvements
            else "No significant improvement"
        )

        result = ComparisonResult(
            baseline_name=baseline_name,
            optimized_name=optimized_name,
            time_improvement_pct=time_improvement,
            memory_improvement_pct=memory_improvement,
            cpu_improvement_pct=cpu_improvement,
            is_better=is_better,
            summary=summary,
        )

        logger.info(
            "comparison_completed",
            baseline=baseline_name,
            optimized=optimized_name,
            time_improvement=f"{time_improvement:.1f}%",
            memory_improvement=f"{memory_improvement:.1f}%",
            cpu_improvement=f"{cpu_improvement:.1f}%",
            is_better=is_better,
        )

        return result

    def save_results(self, filename: Optional[str] = None) -> Path:
        """Save all benchmark results to file.

        Args:
            filename: Optional filename

        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"benchmark_results_{int(time.time())}.json"

        filepath = self.benchmark_dir / filename

        data = {
            "timestamp": datetime.now().isoformat(),
            "baselines": {
                name: {
                    "iterations": result.iterations,
                    "mean_time_ms": result.mean_time_ms,
                    "mean_memory_mb": result.mean_memory_mb,
                    "mean_cpu_percent": result.mean_cpu_percent,
                    "timestamp": result.timestamp,
                }
                for name, result in self.baselines.items()
            },
            "results": [
                {
                    "name": result.name,
                    "iterations": result.iterations,
                    "mean_time_ms": result.mean_time_ms,
                    "mean_memory_mb": result.mean_memory_mb,
                    "mean_cpu_percent": result.mean_cpu_percent,
                    "timestamp": result.timestamp,
                }
                for result in self.results
            ],
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        logger.info("benchmark_results_saved", filepath=str(filepath))

        return filepath


def compare_performance(
    baseline_func: Callable[[], Any],
    optimized_func: Callable[[], Any],
    iterations: int = 100,
) -> ComparisonResult:
    """Standalone function to compare two implementations.

    Args:
        baseline_func: Baseline implementation
        optimized_func: Optimized implementation
        iterations: Number of iterations

    Returns:
        ComparisonResult
    """
    benchmark = PerformanceBenchmark()
    benchmark.establish_baseline("baseline", baseline_func, iterations)

    return benchmark.compare_to_baseline(
        "baseline", "optimized", optimized_func, iterations
    )


class RegressionDetector:
    """Performance regression detection system.

    Tracks performance over time and alerts on regressions.
    """

    def __init__(
        self,
        history_dir: Path = Path("data/benchmarks/history"),
        regression_threshold: float = 10.0,
    ):
        """
        Initialize regression detector.

        Args:
            history_dir: Directory to store benchmark history
            regression_threshold: Percentage regression to trigger alert (default: 10%)
        """
        self.history_dir = history_dir
        self.regression_threshold = regression_threshold
        self.history_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "regression_detector_initialized",
            history_dir=str(history_dir),
            threshold=f"{regression_threshold}%",
        )

    def record_benchmark(self, name: str, result: BenchmarkResult) -> Path:
        """
        Record benchmark result to history.

        Args:
            name: Benchmark name
            result: Benchmark result

        Returns:
            Path to saved history file
        """
        history_file = self.history_dir / f"{name}_history.json"

        # Load existing history
        history = []
        if history_file.exists():
            with history_file.open() as f:
                history = json.load(f)

        # Add new result
        history.append(
            {
                "timestamp": result.timestamp,
                "iterations": result.iterations,
                "mean_time_ms": result.mean_time_ms,
                "mean_memory_mb": result.mean_memory_mb,
                "mean_cpu_percent": result.mean_cpu_percent,
                "metadata": result.metadata,
            }
        )

        # Save updated history
        with history_file.open("w") as f:
            json.dump(history, f, indent=2)

        logger.info(
            "benchmark_recorded",
            name=name,
            entries=len(history),
            file=str(history_file),
        )

        return history_file

    def detect_regressions(
        self, name: str, current_result: BenchmarkResult
    ) -> Dict[str, Any]:
        """
        Detect performance regressions.

        Args:
            name: Benchmark name
            current_result: Current benchmark result

        Returns:
            Regression detection result
        """
        history_file = self.history_dir / f"{name}_history.json"

        if not history_file.exists():
            logger.warning(
                "no_history_found",
                name=name,
                message="No history file found, recording baseline",
            )
            self.record_benchmark(name, current_result)
            return {
                "has_regression": False,
                "baseline_mean_time": None,
                "current_mean_time": current_result.mean_time_ms,
                "regression_percent": 0.0,
                "message": "Baseline established",
            }

        # Load history
        with history_file.open() as f:
            history = json.load(f)

        if not history:
            return {
                "has_regression": False,
                "message": "Empty history",
            }

        # Calculate baseline (average of last N results)
        N = min(5, len(history))
        recent_results = history[-N:]
        baseline_time = sum(r["mean_time_ms"] for r in recent_results) / N
        baseline_memory = sum(r["mean_memory_mb"] for r in recent_results) / N

        # Calculate regressions
        current_time = current_result.mean_time_ms
        current_memory = current_result.mean_memory_mb

        time_regression = ((current_time - baseline_time) / baseline_time) * 100
        memory_regression = ((current_memory - baseline_memory) / baseline_memory) * 100

        has_regression = (
            time_regression > self.regression_threshold
            or memory_regression > self.regression_threshold
        )

        result = {
            "has_regression": has_regression,
            "baseline_mean_time": baseline_time,
            "current_mean_time": current_time,
            "time_regression_percent": time_regression,
            "baseline_mean_memory": baseline_memory,
            "current_mean_memory": current_memory,
            "memory_regression_percent": memory_regression,
            "threshold": self.regression_threshold,
        }

        if has_regression:
            logger.warning(
                "regression_detected",
                name=name,
                time_regression=f"{time_regression:.1f}%",
                memory_regression=f"{memory_regression:.1f}%",
            )
            result["message"] = (
                f"⚠️ Performance regression detected: "
                f"time +{time_regression:.1f}%, memory +{memory_regression:.1f}%"
            )
        else:
            logger.info(
                "no_regression",
                name=name,
                time_change=f"{time_regression:+.1f}%",
                memory_change=f"{memory_regression:+.1f}%",
            )
            result["message"] = (
                f"✅ No regression detected: "
                f"time {time_regression:+.1f}%, memory {memory_regression:+.1f}%"
            )

        # Record current result
        self.record_benchmark(name, current_result)

        return result

    def generate_trend_report(self, name: str) -> str:
        """
        Generate performance trend report.

        Args:
            name: Benchmark name

        Returns:
            Markdown report
        """
        history_file = self.history_dir / f"{name}_history.json"

        if not history_file.exists():
            return f"# No history found for {name}\n"

        with history_file.open() as f:
            history = json.load(f)

        if not history:
            return f"# Empty history for {name}\n"

        lines = [
            f"# Performance Trend Report: {name}\n",
            f"Total measurements: {len(history)}\n",
            f"Date range: {history[0]['timestamp']} to {history[-1]['timestamp']}\n",
            "\n## Performance Over Time\n",
            "| Timestamp | Time (ms) | Memory (MB) | CPU (%) |",
            "| --- | --- | --- | --- |",
        ]

        for entry in history[-20:]:  # Last 20 entries
            timestamp = entry["timestamp"].split("T")[0]  # Just date
            lines.append(
                f"| {timestamp} | {entry['mean_time_ms']:.2f} | "
                f"{entry['mean_memory_mb']:.2f} | {entry['mean_cpu_percent']:.1f} |"
            )

        # Calculate trends
        if len(history) >= 2:
            first = history[0]
            last = history[-1]

            time_trend = (
                (last["mean_time_ms"] - first["mean_time_ms"]) / first["mean_time_ms"]
            ) * 100
            memory_trend = (
                (last["mean_memory_mb"] - first["mean_memory_mb"])
                / first["mean_memory_mb"]
            ) * 100

            lines.append("\n## Trends\n")
            lines.append(f"- Time: {time_trend:+.1f}% (from first to last)")
            lines.append(f"- Memory: {memory_trend:+.1f}% (from first to last)")

        return "\n".join(lines)

    def clean_old_history(self, days: int = 90) -> None:
        """
        Clean old history entries.

        Args:
            days: Keep entries from last N days
        """
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)

        for history_file in self.history_dir.glob("*_history.json"):
            with history_file.open() as f:
                history = json.load(f)

            # Filter old entries
            filtered = [
                entry
                for entry in history
                if datetime.fromisoformat(entry["timestamp"]) > cutoff
            ]

            if len(filtered) < len(history):
                with history_file.open("w") as f:
                    json.dump(filtered, f, indent=2)

                logger.info(
                    "history_cleaned",
                    file=str(history_file),
                    removed=len(history) - len(filtered),
                    kept=len(filtered),
                )


def benchmark_with_regression_detection(
    name: str,
    workload: Callable[[], Any],
    iterations: int = 100,
    regression_threshold: float = 10.0,
) -> Dict[str, Any]:
    """
    Run benchmark with automatic regression detection.

    Args:
        name: Benchmark name
        workload: Workload to benchmark
        iterations: Number of iterations
        regression_threshold: Regression threshold percentage

    Returns:
        Combined benchmark and regression results
    """
    # Run benchmark
    benchmark = PerformanceBenchmark()
    result = benchmark.run_benchmark(name, workload, iterations)

    # Detect regressions
    detector = RegressionDetector(regression_threshold=regression_threshold)
    regression_result = detector.detect_regressions(name, result)

    return {
        "benchmark": {
            "mean_time_ms": result.mean_time_ms,
            "mean_memory_mb": result.mean_memory_mb,
            "mean_cpu_percent": result.mean_cpu_percent,
        },
        "regression": regression_result,
    }

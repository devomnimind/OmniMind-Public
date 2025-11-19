"""Optimization module for hardware and compiler optimization.

This module implements optimization metrics from the hardware auto-optimization
documentation (docs/autootimizacao-hardware-omnidev.md).

Modules:
    performance_profiler: CPU/memory/performance profiling
    benchmarking: Performance comparison framework
"""

from src.optimization.performance_profiler import (
    PerformanceMetrics,
    PerformanceProfiler,
    profile_function,
)
from src.optimization.benchmarking import (
    BenchmarkResult,
    PerformanceBenchmark,
    compare_performance,
)

__all__ = [
    "PerformanceMetrics",
    "PerformanceProfiler",
    "profile_function",
    "BenchmarkResult",
    "PerformanceBenchmark",
    "compare_performance",
]

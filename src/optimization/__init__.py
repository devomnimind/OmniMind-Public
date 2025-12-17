"""Optimization module for hardware and compiler optimization.

This module implements optimization metrics from the hardware auto-optimization
documentation (docs/autootimizacao-hardware-omnidev.md).

Modules:
    performance_profiler: CPU/memory/performance profiling
    benchmarking: Performance comparison framework
    memory_optimization: Memory management and optimization
"""

from src.optimization.benchmarking import (
    BenchmarkResult,
    PerformanceBenchmark,
    compare_performance,
)
from src.optimization.memory_optimization import (
    AllocationStats,
    MemoryAllocator,
    MemoryLeakDetector,
    MemoryOptimizer,
    MemoryPool,
    MemoryProfiler,
    MemoryUsageSnapshot,
)
from src.optimization.performance_profiler import (
    PerformanceMetrics,
    PerformanceProfiler,
    profile_function,
)

__all__ = [
    # Performance profiling
    "PerformanceMetrics",
    "PerformanceProfiler",
    "profile_function",
    # Benchmarking
    "BenchmarkResult",
    "PerformanceBenchmark",
    "compare_performance",
    # Memory optimization
    "MemoryOptimizer",
    "MemoryAllocator",
    "MemoryPool",
    "MemoryProfiler",
    "MemoryLeakDetector",
    "MemoryUsageSnapshot",
    "AllocationStats",
]

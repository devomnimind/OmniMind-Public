"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

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

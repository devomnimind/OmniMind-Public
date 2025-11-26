"""
Memory Optimization Module for OmniMind.

This module provides memory management optimizations:
- Custom memory allocators for frequent allocations
- Memory pooling for object reuse
- Memory profiling tools
- Memory leak detection
- Usage optimization and monitoring
"""

from __future__ import annotations

import gc
import logging
import weakref
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

import psutil

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class MemoryUsageSnapshot:
    """Snapshot of memory usage at a point in time."""

    timestamp: datetime
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    percent: float  # Memory percentage
    available_mb: float  # System available memory
    objects_count: int  # Number of tracked objects
    gc_stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "rss_mb": self.rss_mb,
            "vms_mb": self.vms_mb,
            "percent": self.percent,
            "available_mb": self.available_mb,
            "objects_count": self.objects_count,
            "gc_stats": self.gc_stats,
        }


@dataclass
class AllocationStats:
    """Statistics about memory allocations."""

    total_allocations: int = 0
    total_deallocations: int = 0
    current_live_objects: int = 0
    peak_live_objects: int = 0
    total_bytes_allocated: int = 0
    bytes_in_use: int = 0
    peak_bytes_in_use: int = 0

    def get_utilization(self) -> float:
        """Get current memory utilization ratio."""
        if self.total_bytes_allocated == 0:
            return 0.0
        return self.bytes_in_use / self.total_bytes_allocated


class MemoryPool(Generic[T]):
    """Memory pool for object reuse to reduce allocation overhead.

    This pool pre-allocates objects and reuses them instead of creating
    new instances, reducing GC pressure and allocation time.
    """

    def __init__(
        self,
        factory: Callable[[], T],
        initial_size: int = 10,
        max_size: int = 100,
        reset_func: Optional[Callable[[T], None]] = None,
    ):
        """Initialize memory pool.

        Args:
            factory: Function to create new objects
            initial_size: Initial pool size
            max_size: Maximum pool size
            reset_func: Optional function to reset object state
        """
        self.factory = factory
        self.max_size = max_size
        self.reset_func = reset_func
        self.pool: deque[T] = deque(maxlen=max_size)
        self.stats = AllocationStats()

        # Pre-allocate initial objects
        for _ in range(initial_size):
            self.pool.append(factory())
            self.stats.total_allocations += 1

        logger.info(f"MemoryPool initialized: initial={initial_size}, max={max_size}")

    def acquire(self) -> T:
        """Acquire an object from the pool.

        Returns:
            Object from pool or newly created
        """
        if self.pool:
            obj = self.pool.popleft()
            self.stats.current_live_objects += 1
            self.stats.peak_live_objects = max(
                self.stats.peak_live_objects, self.stats.current_live_objects
            )
            return obj

        # Pool empty, create new
        obj = self.factory()
        self.stats.total_allocations += 1
        self.stats.current_live_objects += 1
        self.stats.peak_live_objects = max(
            self.stats.peak_live_objects, self.stats.current_live_objects
        )
        return obj

    def release(self, obj: T) -> None:
        """Release an object back to the pool.

        Args:
            obj: Object to return to pool
        """
        if len(self.pool) < self.max_size:
            # Reset object state if reset function provided
            if self.reset_func:
                self.reset_func(obj)

            self.pool.append(obj)
            self.stats.total_deallocations += 1
            self.stats.current_live_objects -= 1

    def get_stats(self) -> AllocationStats:
        """Get pool statistics.

        Returns:
            Allocation statistics
        """
        return self.stats

    def clear(self) -> None:
        """Clear the pool and reset stats."""
        self.pool.clear()
        self.stats = AllocationStats()


class MemoryAllocator:
    """Custom memory allocator with tracking and pooling."""

    def __init__(self) -> None:
        """Initialize memory allocator."""
        self.pools: Dict[str, MemoryPool[Any]] = {}
        self.stats_by_type: Dict[str, AllocationStats] = defaultdict(AllocationStats)

    def create_pool(
        self,
        name: str,
        factory: Callable[[], Any],
        initial_size: int = 10,
        max_size: int = 100,
    ) -> MemoryPool[Any]:
        """Create a named memory pool.

        Args:
            name: Pool identifier
            factory: Object factory function
            initial_size: Initial pool size
            max_size: Maximum pool size

        Returns:
            Created memory pool
        """
        if name in self.pools:
            logger.warning(f"Pool '{name}' already exists, returning existing")
            return self.pools[name]

        pool = MemoryPool(factory, initial_size, max_size)
        self.pools[name] = pool
        logger.info(f"Created memory pool: {name}")
        return pool

    def get_pool(self, name: str) -> Optional[MemoryPool[Any]]:
        """Get a named memory pool.

        Args:
            name: Pool identifier

        Returns:
            Memory pool or None if not found
        """
        return self.pools.get(name)

    def get_all_stats(self) -> Dict[str, AllocationStats]:
        """Get statistics for all pools.

        Returns:
            Dictionary of pool stats
        """
        return {name: pool.get_stats() for name, pool in self.pools.items()}

    def clear_all_pools(self) -> None:
        """Clear all memory pools."""
        for pool in self.pools.values():
            pool.clear()
        logger.info("Cleared all memory pools")


class MemoryLeakDetector:
    """Detects potential memory leaks by tracking object lifetimes."""

    def __init__(self, check_interval: int = 100):
        """Initialize leak detector.

        Args:
            check_interval: Number of allocations between checks
        """
        self.check_interval = check_interval
        self.tracked_objects: Dict[int, weakref.ref[Any]] = {}
        self.object_creation_count: Dict[type, int] = defaultdict(int)
        self.allocation_count = 0
        self.potential_leaks: List[Dict[str, Any]] = []

    def track_object(self, obj: Any) -> None:
        """Start tracking an object for leaks.

        Args:
            obj: Object to track
        """
        try:
            obj_id = id(obj)
            self.tracked_objects[obj_id] = weakref.ref(obj, self._on_object_deleted)
            self.object_creation_count[type(obj)] += 1
            self.allocation_count += 1

            # Periodic check
            if self.allocation_count % self.check_interval == 0:
                self.check_for_leaks()
        except TypeError:
            # Some built-in types don't support weak references
            # Just count them
            self.object_creation_count[type(obj)] += 1
            self.allocation_count += 1

    def _on_object_deleted(self, weak_ref: weakref.ref[Any]) -> None:
        """Callback when tracked object is deleted.

        Args:
            weak_ref: Weak reference to deleted object
        """
        # Clean up tracking
        for obj_id, ref in list(self.tracked_objects.items()):
            if ref == weak_ref:
                del self.tracked_objects[obj_id]
                break

    def check_for_leaks(self) -> List[Dict[str, Any]]:
        """Check for potential memory leaks.

        Returns:
            List of potential leak reports
        """
        gc.collect()  # Force collection

        leaks = []

        # Count live objects by type
        live_objects: Dict[type, int] = defaultdict(int)
        for obj_ref in self.tracked_objects.values():
            obj = obj_ref()
            if obj is not None:
                live_objects[type(obj)] += 1

        # Identify types with high retention
        for obj_type, count in live_objects.items():
            created = self.object_creation_count[obj_type]
            if created > 10:  # Only check if we've created enough
                retention_rate = count / created
                if retention_rate > 0.8:  # >80% still alive
                    leak = {
                        "type": obj_type.__name__,
                        "live_count": count,
                        "created_count": created,
                        "retention_rate": retention_rate,
                    }
                    leaks.append(leak)

        if leaks:
            self.potential_leaks.extend(leaks)
            logger.warning(f"Potential memory leaks detected: {len(leaks)} types")

        return leaks

    def get_leak_report(self) -> Dict[str, Any]:
        """Get comprehensive leak report.

        Returns:
            Leak detection report
        """
        return {
            "total_tracked": len(self.tracked_objects),
            "allocations_checked": self.allocation_count,
            "potential_leaks": self.potential_leaks,
            "live_objects_by_type": {
                obj_type.__name__: count
                for obj_type, count in self.object_creation_count.items()
            },
        }


class MemoryProfiler:
    """Advanced memory profiler with detailed tracking."""

    def __init__(self, snapshot_interval: int = 60):
        """Initialize memory profiler.

        Args:
            snapshot_interval: Seconds between automatic snapshots
        """
        self.snapshot_interval = snapshot_interval
        self.snapshots: deque[MemoryUsageSnapshot] = deque(maxlen=1000)
        self.process = psutil.Process()
        self.baseline: Optional[MemoryUsageSnapshot] = None

    def take_snapshot(self) -> MemoryUsageSnapshot:
        """Take a memory usage snapshot.

        Returns:
            Memory usage snapshot
        """
        mem_info = self.process.memory_info()
        virtual_mem = psutil.virtual_memory()

        # Get GC stats
        gc_stats: Dict[str, Any] = {
            f"generation_{i}": {
                "count": gc.get_count()[i],
                "threshold": gc.get_threshold()[i],
            }
            for i in range(3)
        }
        gc_stats["collected"] = gc.collect()

        snapshot = MemoryUsageSnapshot(
            timestamp=datetime.now(),
            rss_mb=mem_info.rss / (1024 * 1024),
            vms_mb=mem_info.vms / (1024 * 1024),
            percent=self.process.memory_percent(),
            available_mb=virtual_mem.available / (1024 * 1024),
            objects_count=len(gc.get_objects()),
            gc_stats=gc_stats,
        )

        self.snapshots.append(snapshot)

        # Set baseline if not set
        if self.baseline is None:
            self.baseline = snapshot
            logger.info(f"Memory baseline set: {snapshot.rss_mb:.2f} MB RSS")

        return snapshot

    def get_memory_growth(self) -> float:
        """Get memory growth since baseline.

        Returns:
            Memory growth in MB
        """
        if not self.baseline or not self.snapshots:
            return 0.0

        current = self.snapshots[-1]
        return current.rss_mb - self.baseline.rss_mb

    def detect_memory_spike(self, threshold_mb: float = 100.0) -> bool:
        """Detect sudden memory spike.

        Args:
            threshold_mb: Spike threshold in MB

        Returns:
            True if spike detected
        """
        if len(self.snapshots) < 2:
            return False

        prev = self.snapshots[-2]
        current = self.snapshots[-1]

        growth = current.rss_mb - prev.rss_mb

        if growth > threshold_mb:
            logger.warning(
                f"Memory spike detected: {growth:.2f} MB increase "
                f"({prev.rss_mb:.2f} -> {current.rss_mb:.2f} MB)"
            )
            return True

        return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics.

        Returns:
            Statistics dictionary
        """
        if not self.snapshots:
            return {}

        rss_values = [s.rss_mb for s in self.snapshots]
        current = self.snapshots[-1]

        return {
            "current_rss_mb": current.rss_mb,
            "current_vms_mb": current.vms_mb,
            "current_percent": current.percent,
            "available_mb": current.available_mb,
            "objects_count": current.objects_count,
            "min_rss_mb": min(rss_values),
            "max_rss_mb": max(rss_values),
            "avg_rss_mb": sum(rss_values) / len(rss_values),
            "growth_since_baseline_mb": self.get_memory_growth(),
            "snapshots_count": len(self.snapshots),
        }


class MemoryOptimizer:
    """Integrated memory optimization system."""

    def __init__(self) -> None:
        """Initialize memory optimizer."""
        self.allocator = MemoryAllocator()
        self.profiler = MemoryProfiler()
        self.leak_detector = MemoryLeakDetector()
        self.optimizations_applied: List[str] = []

        logger.info("MemoryOptimizer initialized")

    def optimize_gc(self) -> None:
        """Optimize garbage collection settings."""
        # Tune GC thresholds for less frequent collections
        # (700, 10, 10) are default thresholds
        gc.set_threshold(1000, 15, 15)
        self.optimizations_applied.append("gc_threshold_tuned")
        logger.info("GC thresholds optimized")

    def create_object_pool(
        self, name: str, factory: Callable[[], Any], size: int = 50
    ) -> MemoryPool[Any]:
        """Create an object pool for frequently allocated objects.

        Args:
            name: Pool name
            factory: Object factory
            size: Pool size

        Returns:
            Memory pool
        """
        pool = self.allocator.create_pool(name, factory, size, size * 2)
        self.optimizations_applied.append(f"pool_{name}_created")
        return pool

    def track_for_leaks(self, obj: Any) -> None:
        """Track object for potential leaks.

        Args:
            obj: Object to track
        """
        self.leak_detector.track_object(obj)

    def take_snapshot(self) -> MemoryUsageSnapshot:
        """Take memory snapshot.

        Returns:
            Memory snapshot
        """
        return self.profiler.take_snapshot()

    def get_optimization_report(self) -> Dict[str, Any]:
        """Get comprehensive optimization report.

        Returns:
            Optimization report
        """
        return {
            "optimizations_applied": self.optimizations_applied,
            "memory_stats": self.profiler.get_statistics(),
            "pool_stats": self.allocator.get_all_stats(),
            "leak_report": self.leak_detector.get_leak_report(),
        }

    def suggest_optimizations(self) -> List[str]:
        """Suggest memory optimizations based on current state.

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        # Check memory usage
        stats = self.profiler.get_statistics()
        if stats:
            growth = stats.get("growth_since_baseline_mb", 0)
            if growth > 200:
                suggestions.append(
                    f"High memory growth detected ({growth:.1f} MB). "
                    "Consider implementing object pooling."
                )

            percent = stats.get("current_percent", 0)
            if percent > 75:
                suggestions.append(
                    f"High memory usage ({percent:.1f}%). "
                    "Review and optimize data structures."
                )

        # Check for leaks
        leak_report = self.leak_detector.get_leak_report()
        if leak_report["potential_leaks"]:
            suggestions.append(
                f"Potential memory leaks detected in {len(leak_report['potential_leaks'])} types. "
                "Review object lifecycle management."
            )

        # Check GC
        if "gc_threshold_tuned" not in self.optimizations_applied:
            suggestions.append(
                "Consider optimizing GC thresholds for better performance"
            )

        return suggestions

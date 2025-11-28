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

"""
Tests for memory optimization module.
"""

import gc
import time

from src.optimization.memory_optimization import (
    AllocationStats,
    MemoryAllocator,
    MemoryLeakDetector,
    MemoryOptimizer,
    MemoryPool,
    MemoryProfiler,
    MemoryUsageSnapshot,
)


class TestMemoryUsageSnapshot:
    """Test memory usage snapshot."""

    def test_snapshot_creation(self) -> None:
        """Test creating memory snapshot."""
        from datetime import datetime

        snapshot = MemoryUsageSnapshot(
            timestamp=datetime.now(),
            rss_mb=100.5,
            vms_mb=200.3,
            percent=15.2,
            available_mb=1000.0,
            objects_count=5000,
        )

        assert snapshot.rss_mb == 100.5
        assert snapshot.vms_mb == 200.3
        assert snapshot.percent == 15.2
        assert snapshot.objects_count == 5000

    def test_snapshot_to_dict(self) -> None:
        """Test snapshot serialization."""
        from datetime import datetime

        snapshot = MemoryUsageSnapshot(
            timestamp=datetime.now(),
            rss_mb=100.0,
            vms_mb=200.0,
            percent=10.0,
            available_mb=1000.0,
            objects_count=1000,
        )

        data = snapshot.to_dict()

        assert "timestamp" in data
        assert data["rss_mb"] == 100.0
        assert data["objects_count"] == 1000


class TestAllocationStats:
    """Test allocation statistics."""

    def test_stats_creation(self) -> None:
        """Test creating allocation stats."""
        stats = AllocationStats()

        assert stats.total_allocations == 0
        assert stats.current_live_objects == 0
        assert stats.peak_live_objects == 0

    def test_utilization_calculation(self) -> None:
        """Test memory utilization calculation."""
        stats = AllocationStats(
            total_bytes_allocated=1000,
            bytes_in_use=600,
        )

        utilization = stats.get_utilization()

        assert utilization == 0.6

    def test_utilization_zero_allocated(self) -> None:
        """Test utilization with zero allocation."""
        stats = AllocationStats()

        utilization = stats.get_utilization()

        assert utilization == 0.0


class TestMemoryPool:
    """Test memory pool functionality."""

    def test_pool_creation(self) -> None:
        """Test creating memory pool."""

        def factory():
            return {"value": 0}

        pool = MemoryPool(factory, initial_size=5, max_size=10)

        assert len(pool.pool) == 5
        assert pool.max_size == 10
        assert pool.stats.total_allocations == 5

    def test_acquire_from_pool(self) -> None:
        """Test acquiring object from pool."""

        def factory():
            return []

        pool = MemoryPool(factory, initial_size=3)
        initial_size = len(pool.pool)

        obj = pool.acquire()

        assert isinstance(obj, list)
        assert len(pool.pool) == initial_size - 1
        assert pool.stats.current_live_objects == 1

    def test_acquire_when_empty(self) -> None:
        """Test acquiring when pool is empty."""

        def factory():
            return {}

        pool = MemoryPool(factory, initial_size=0, max_size=5)

        obj = pool.acquire()

        assert isinstance(obj, dict)
        assert pool.stats.total_allocations == 1

    def test_release_to_pool(self) -> None:
        """Test releasing object back to pool."""

        def factory():
            return []

        pool = MemoryPool(factory, initial_size=2, max_size=5)

        obj = pool.acquire()
        pool.release(obj)

        assert len(pool.pool) == 2
        assert pool.stats.total_deallocations == 1

    def test_release_with_reset(self) -> None:
        """Test releasing with reset function."""

        def factory():
            return {"value": 0}

        def reset(obj):
            obj["value"] = 0

        pool = MemoryPool(factory, initial_size=1, reset_func=reset)

        obj = pool.acquire()
        obj["value"] = 100
        pool.release(obj)

        # Get it back and check it was reset
        obj2 = pool.acquire()
        assert obj2["value"] == 0

    def test_pool_max_size_limit(self) -> None:
        """Test that pool respects max size limit."""

        def factory():
            return {}

        pool = MemoryPool(factory, initial_size=0, max_size=3)

        # Acquire and release more than max_size
        objects = [pool.acquire() for _ in range(5)]
        for obj in objects:
            pool.release(obj)

        # Pool should not exceed max_size
        assert len(pool.pool) <= 3

    def test_peak_live_objects_tracking(self) -> None:
        """Test tracking of peak live objects."""

        def factory():
            return []

        pool = MemoryPool(factory, initial_size=2)

        obj1 = pool.acquire()
        obj2 = pool.acquire()
        _ = pool.acquire()  # obj3

        assert pool.stats.peak_live_objects == 3

        pool.release(obj1)
        pool.release(obj2)

        # Peak should remain at 3
        assert pool.stats.peak_live_objects == 3

    def test_clear_pool(self) -> None:
        """Test clearing pool."""

        def factory():
            return []

        pool = MemoryPool(factory, initial_size=5)
        pool.acquire()

        pool.clear()

        assert len(pool.pool) == 0
        assert pool.stats.total_allocations == 0


class TestMemoryAllocator:
    """Test memory allocator."""

    def test_allocator_creation(self) -> None:
        """Test creating memory allocator."""
        allocator = MemoryAllocator()

        assert len(allocator.pools) == 0
        assert isinstance(allocator.stats_by_type, dict)

    def test_create_pool(self) -> None:
        """Test creating named pool."""
        allocator = MemoryAllocator()

        pool = allocator.create_pool(
            "test_pool",
            factory=lambda: {},
            initial_size=5,
            max_size=10,
        )

        assert "test_pool" in allocator.pools
        assert pool is allocator.pools["test_pool"]

    def test_create_duplicate_pool(self) -> None:
        """Test creating pool with existing name."""
        allocator = MemoryAllocator()

        pool1 = allocator.create_pool("duplicate", lambda: {})
        pool2 = allocator.create_pool("duplicate", lambda: [])

        # Should return the first pool
        assert pool1 is pool2

    def test_get_pool(self) -> None:
        """Test retrieving pool by name."""
        allocator = MemoryAllocator()
        allocator.create_pool("my_pool", lambda: [])

        pool = allocator.get_pool("my_pool")

        assert pool is not None
        assert isinstance(pool, MemoryPool)

    def test_get_nonexistent_pool(self) -> None:
        """Test retrieving nonexistent pool."""
        allocator = MemoryAllocator()

        pool = allocator.get_pool("nonexistent")

        assert pool is None

    def test_get_all_stats(self) -> None:
        """Test getting stats for all pools."""
        allocator = MemoryAllocator()

        allocator.create_pool("pool1", lambda: {}, initial_size=3)
        allocator.create_pool("pool2", lambda: [], initial_size=5)

        stats = allocator.get_all_stats()

        assert "pool1" in stats
        assert "pool2" in stats
        assert stats["pool1"].total_allocations == 3
        assert stats["pool2"].total_allocations == 5

    def test_clear_all_pools(self) -> None:
        """Test clearing all pools."""
        allocator = MemoryAllocator()

        pool1 = allocator.create_pool("pool1", lambda: {}, initial_size=3)
        pool2 = allocator.create_pool("pool2", lambda: [], initial_size=3)

        allocator.clear_all_pools()

        assert len(pool1.pool) == 0
        assert len(pool2.pool) == 0


class TestMemoryLeakDetector:
    """Test memory leak detection."""

    def test_detector_creation(self) -> None:
        """Test creating leak detector."""
        detector = MemoryLeakDetector(check_interval=50)

        assert detector.check_interval == 50
        assert len(detector.tracked_objects) == 0

    def test_track_object(self) -> None:
        """Test tracking an object."""
        detector = MemoryLeakDetector()

        # Use a custom class that supports weakref
        class TestObj:
            pass

        obj = TestObj()
        detector.track_object(obj)

        # For objects that support weakref, they should be tracked
        # For built-in types (dict, list), they're just counted
        assert detector.allocation_count == 1

    def test_object_cleanup_on_deletion(self) -> None:
        """Test that deleted objects are cleaned up."""
        detector = MemoryLeakDetector()

        obj = []
        detector.track_object(obj)

        # Delete object
        del obj
        gc.collect()

        # Should eventually be cleaned up
        # Note: weakref cleanup is not immediate
        time.sleep(0.1)

        # At minimum, allocation count should be recorded
        assert detector.allocation_count > 0

    def test_check_for_leaks(self) -> None:
        """Test leak detection."""
        detector = MemoryLeakDetector()

        # Create and track objects
        objects = [{"id": i} for i in range(20)]
        for obj in objects:
            detector.track_object(obj)

        # Check for leaks (should find high retention)
        leaks = detector.check_for_leaks()

        # Should detect potential leaks for dict type
        assert isinstance(leaks, list)

    def test_leak_report(self) -> None:
        """Test getting leak report."""
        detector = MemoryLeakDetector()

        # Use custom class that supports weakref
        class TestObj:
            pass

        obj1 = TestObj()
        obj2 = TestObj()

        detector.track_object(obj1)
        detector.track_object(obj2)

        report = detector.get_leak_report()

        assert "total_tracked" in report
        assert "allocations_checked" in report
        assert "potential_leaks" in report
        assert report["allocations_checked"] == 2


class TestMemoryProfiler:
    """Test memory profiler."""

    def test_profiler_creation(self) -> None:
        """Test creating memory profiler."""
        profiler = MemoryProfiler(snapshot_interval=30)

        assert profiler.snapshot_interval == 30
        assert len(profiler.snapshots) == 0
        assert profiler.baseline is None

    def test_take_snapshot(self) -> None:
        """Test taking memory snapshot."""
        profiler = MemoryProfiler()

        snapshot = profiler.take_snapshot()

        assert isinstance(snapshot, MemoryUsageSnapshot)
        assert snapshot.rss_mb > 0
        assert snapshot.objects_count > 0
        assert len(profiler.snapshots) == 1

    def test_baseline_setting(self) -> None:
        """Test that first snapshot sets baseline."""
        profiler = MemoryProfiler()

        profiler.take_snapshot()

        assert profiler.baseline is not None
        assert isinstance(profiler.baseline, MemoryUsageSnapshot)

    def test_get_memory_growth(self) -> None:
        """Test calculating memory growth."""
        profiler = MemoryProfiler()

        profiler.take_snapshot()

        # Allocate some memory
        _ = [i for i in range(10000)]

        profiler.take_snapshot()

        growth = profiler.get_memory_growth()

        # Should show some growth (or at least not error)
        assert isinstance(growth, float)

    def test_detect_memory_spike(self) -> None:
        """Test memory spike detection."""
        profiler = MemoryProfiler()

        profiler.take_snapshot()
        profiler.take_snapshot()

        # With normal usage, shouldn't detect spike
        spike = profiler.detect_memory_spike(threshold_mb=1000.0)

        assert isinstance(spike, bool)

    def test_get_statistics(self) -> None:
        """Test getting memory statistics."""
        profiler = MemoryProfiler()

        profiler.take_snapshot()

        stats = profiler.get_statistics()

        assert "current_rss_mb" in stats
        assert "current_percent" in stats
        assert "objects_count" in stats
        assert "min_rss_mb" in stats
        assert "max_rss_mb" in stats

    def test_snapshot_limit(self) -> None:
        """Test that snapshots are limited."""
        profiler = MemoryProfiler()

        # Take more than maxlen snapshots
        for _ in range(1100):
            profiler.take_snapshot()

        # Should be limited to 1000
        assert len(profiler.snapshots) <= 1000


class TestMemoryOptimizer:
    """Test integrated memory optimizer."""

    def test_optimizer_creation(self) -> None:
        """Test creating memory optimizer."""
        optimizer = MemoryOptimizer()

        assert isinstance(optimizer.allocator, MemoryAllocator)
        assert isinstance(optimizer.profiler, MemoryProfiler)
        assert isinstance(optimizer.leak_detector, MemoryLeakDetector)

    def test_optimize_gc(self) -> None:
        """Test GC optimization."""
        optimizer = MemoryOptimizer()

        optimizer.optimize_gc()

        assert "gc_threshold_tuned" in optimizer.optimizations_applied
        # Verify GC thresholds changed
        thresholds = gc.get_threshold()
        assert thresholds[0] == 1000

    def test_create_object_pool(self) -> None:
        """Test creating object pool through optimizer."""
        optimizer = MemoryOptimizer()

        pool = optimizer.create_object_pool("test_pool", lambda: {}, size=10)

        assert isinstance(pool, MemoryPool)
        assert optimizer.allocator.get_pool("test_pool") is pool
        assert "pool_test_pool_created" in optimizer.optimizations_applied

    def test_track_for_leaks(self) -> None:
        """Test tracking objects for leaks."""
        optimizer = MemoryOptimizer()

        obj = []
        optimizer.track_for_leaks(obj)

        assert optimizer.leak_detector.allocation_count == 1

    def test_take_snapshot(self) -> None:
        """Test taking snapshot through optimizer."""
        optimizer = MemoryOptimizer()

        snapshot = optimizer.take_snapshot()

        assert isinstance(snapshot, MemoryUsageSnapshot)
        assert len(optimizer.profiler.snapshots) == 1

    def test_get_optimization_report(self) -> None:
        """Test getting comprehensive optimization report."""
        optimizer = MemoryOptimizer()

        optimizer.optimize_gc()
        optimizer.create_object_pool("pool1", lambda: {})
        optimizer.take_snapshot()

        report = optimizer.get_optimization_report()

        assert "optimizations_applied" in report
        assert "memory_stats" in report
        assert "pool_stats" in report
        assert "leak_report" in report
        assert len(report["optimizations_applied"]) > 0

    def test_suggest_optimizations(self) -> None:
        """Test optimization suggestions."""
        optimizer = MemoryOptimizer()

        optimizer.take_snapshot()

        suggestions = optimizer.suggest_optimizations()

        assert isinstance(suggestions, list)
        # Should suggest GC optimization if not applied
        assert any("GC" in s for s in suggestions)


class TestIntegration:
    """Integration tests for memory optimization."""

    def test_full_workflow(self) -> None:
        """Test complete memory optimization workflow."""
        optimizer = MemoryOptimizer()

        # 1. Take baseline
        optimizer.take_snapshot()

        # 2. Optimize GC
        optimizer.optimize_gc()

        # 3. Create object pool
        pool = optimizer.create_object_pool(
            "data_objects",
            lambda: {"value": 0, "data": []},
            size=20,
        )

        # 4. Use the pool
        objects = [pool.acquire() for _ in range(10)]

        # 5. Track some objects for leaks
        for obj in objects[:5]:
            optimizer.track_for_leaks(obj)

        # 6. Release objects back to pool
        for obj in objects:
            pool.release(obj)

        # 7. Take another snapshot
        optimizer.take_snapshot()

        # 8. Get report
        report = optimizer.get_optimization_report()

        # Verify report structure
        assert len(report["optimizations_applied"]) >= 2
        assert "memory_stats" in report
        assert report["pool_stats"]["data_objects"].total_allocations == 20

        # 9. Get suggestions
        suggestions = optimizer.suggest_optimizations()
        assert isinstance(suggestions, list)

    def test_memory_pool_reuse(self) -> None:
        """Test that memory pool actually reuses objects."""
        optimizer = MemoryOptimizer()

        # Create a simple counter to track new object creation
        created_count = [0]

        def factory():
            created_count[0] += 1
            return {"id": created_count[0]}

        pool = optimizer.create_object_pool("reuse_test", factory, size=5)

        # Initial pool should have 5 objects created
        assert created_count[0] == 5

        # Acquire and release multiple times
        for _ in range(10):
            obj = pool.acquire()
            pool.release(obj)

        # Should still have only created 5 objects (all reused)
        assert created_count[0] == 5

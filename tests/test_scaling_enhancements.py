"""Tests for scaling infrastructure modules.

Tests GPU resource pooling, database connection pooling, and multi-level caching.
"""

import pytest
import time

from src.scaling.gpu_resource_pool import (
    GPUDevice,
    GPUResourcePool,
    GPUPoolConfig,
    GPUStatus,
    GPUTask,
)
from src.scaling.database_connection_pool import (
    ConnectionInfo,
    ConnectionStatus,
    DatabaseConnectionPool,
    PoolConfig,
)
from src.scaling.multi_level_cache import (
    CacheConfig,
    CacheLevel,
    CacheLayer,
    EvictionPolicy,
    MultiLevelCache,
)


class TestGPUResourcePool:
    """Tests for GPU resource pool."""

    def test_gpu_device_creation(self):
        """Test GPU device creation."""
        gpu = GPUDevice(
            device_id=0,
            name="Test GPU",
            total_memory_mb=4096,
            compute_capability="7.5",
        )
        assert gpu.device_id == 0
        assert gpu.is_available()
        assert gpu.has_capacity(2048)

    def test_gpu_pool_config(self):
        """Test GPU pool configuration."""
        config = GPUPoolConfig(
            auto_discover_gpus=False,
            enable_load_balancing=True,
        )
        assert config.enable_load_balancing is True
        assert config.auto_discover_gpus is False

    def test_pool_initialization(self):
        """Test pool initialization."""
        config = GPUPoolConfig(auto_discover_gpus=False)
        pool = GPUResourcePool(config)
        assert pool.get_pool_stats()["total_gpus"] == 0

    def test_add_gpu(self):
        """Test adding GPU to pool."""
        config = GPUPoolConfig(auto_discover_gpus=False)
        pool = GPUResourcePool(config)
        
        gpu = GPUDevice(
            device_id=0,
            name="Test GPU",
            total_memory_mb=4096,
            compute_capability="7.5",
        )
        pool.add_gpu(gpu)
        
        assert pool.get_pool_stats()["total_gpus"] == 1
        assert len(pool.get_available_gpus()) == 1

    def test_allocate_gpu(self):
        """Test GPU allocation."""
        config = GPUPoolConfig(auto_discover_gpus=False)
        pool = GPUResourcePool(config)
        
        gpu = GPUDevice(
            device_id=0,
            name="Test GPU",
            total_memory_mb=4096,
            compute_capability="7.5",
        )
        pool.add_gpu(gpu)
        
        task = GPUTask(task_id="task1", required_memory_mb=2048)
        device_id = pool.allocate_gpu(task)
        
        assert device_id == 0
        assert task.is_assigned()
        assert len(pool.get_available_gpus()) == 0

    def test_release_gpu(self):
        """Test GPU release."""
        config = GPUPoolConfig(auto_discover_gpus=False)
        pool = GPUResourcePool(config)
        
        gpu = GPUDevice(
            device_id=0,
            name="Test GPU",
            total_memory_mb=4096,
            compute_capability="7.5",
        )
        pool.add_gpu(gpu)
        
        task = GPUTask(task_id="task1", required_memory_mb=2048)
        pool.allocate_gpu(task)
        pool.release_gpu(task.task_id)
        
        assert len(pool.get_available_gpus()) == 1
        assert task.is_completed()

    def test_gpu_load_balancing(self):
        """Test GPU load balancing."""
        config = GPUPoolConfig(
            auto_discover_gpus=False,
            enable_load_balancing=True,
        )
        pool = GPUResourcePool(config)
        
        # Add two GPUs with different utilization
        gpu1 = GPUDevice(0, "GPU1", 4096, "7.5")
        gpu1.current_utilization_percent = 50.0
        
        gpu2 = GPUDevice(1, "GPU2", 4096, "7.5")
        gpu2.current_utilization_percent = 20.0
        
        pool.add_gpu(gpu1)
        pool.add_gpu(gpu2)
        
        task = GPUTask(task_id="task1", required_memory_mb=1024)
        device_id = pool.allocate_gpu(task)
        
        # Should allocate to GPU with lower utilization (GPU2)
        assert device_id == 1

    def test_gpu_task_queueing(self):
        """Test task queueing when no GPU available."""
        config = GPUPoolConfig(auto_discover_gpus=False)
        pool = GPUResourcePool(config)
        
        gpu = GPUDevice(0, "GPU", 4096, "7.5")
        pool.add_gpu(gpu)
        
        task1 = GPUTask(task_id="task1", required_memory_mb=2048)
        task2 = GPUTask(task_id="task2", required_memory_mb=2048)
        
        # Allocate first task
        device_id = pool.allocate_gpu(task1)
        assert device_id == 0
        
        # Second task should be queued
        device_id = pool.allocate_gpu(task2)
        assert device_id is None
        
        stats = pool.get_pool_stats()
        assert stats["queued_tasks"] == 1

    def test_update_gpu_stats(self):
        """Test updating GPU statistics."""
        config = GPUPoolConfig(auto_discover_gpus=False)
        pool = GPUResourcePool(config)
        
        gpu = GPUDevice(0, "GPU", 4096, "7.5")
        pool.add_gpu(gpu)
        
        pool.update_gpu_stats(0, utilization_percent=75.0, memory_used_mb=2048)
        
        updated_gpu = pool.get_gpu(0)
        assert updated_gpu.current_utilization_percent == 75.0
        assert updated_gpu.current_memory_used_mb == 2048


class TestDatabaseConnectionPool:
    """Tests for database connection pool."""

    def test_pool_config_creation(self):
        """Test pool configuration."""
        config = PoolConfig(
            pool_size=10,
            max_overflow=5,
        )
        assert config.pool_size == 10
        assert config.max_overflow == 5

    def test_pool_initialization(self):
        """Test pool initialization."""
        config = PoolConfig(pool_size=3)
        pool = DatabaseConnectionPool("postgresql://test", config)
        
        stats = pool.get_stats()
        assert stats["pool_size"] <= 3

    def test_get_connection(self):
        """Test getting connection from pool."""
        config = PoolConfig(pool_size=2)
        pool = DatabaseConnectionPool("postgresql://test", config)
        
        with pool.get_connection() as conn:
            assert conn is not None

    def test_connection_reuse(self):
        """Test connection reuse."""
        config = PoolConfig(pool_size=2)
        pool = DatabaseConnectionPool("postgresql://test", config)
        
        with pool.get_connection() as conn1:
            conn1_id = conn1.conn_id
        
        with pool.get_connection() as conn2:
            # Should reuse the same connection
            assert conn2.conn_id == conn1_id

    def test_connection_overflow(self):
        """Test connection overflow."""
        config = PoolConfig(pool_size=1, max_overflow=2)
        pool = DatabaseConnectionPool("postgresql://test", config)
        
        # Get connections beyond pool size
        conns = []
        for i in range(3):
            conn = pool.get_connection()
            conns.append(conn)
            conn.__enter__()
        
        stats = pool.get_stats()
        # Should have overflow connections
        assert stats["overflow_size"] > 0
        
        # Clean up
        for conn in conns:
            conn.__exit__(None, None, None)

    def test_connection_stats(self):
        """Test connection pool statistics."""
        config = PoolConfig(pool_size=2)
        pool = DatabaseConnectionPool("postgresql://test", config)
        
        with pool.get_connection():
            stats = pool.get_stats()
            assert stats["total_created"] > 0

    def test_close_all_connections(self):
        """Test closing all connections."""
        config = PoolConfig(pool_size=2)
        pool = DatabaseConnectionPool("postgresql://test", config)
        
        pool.close_all()
        
        stats = pool.get_stats()
        assert stats["pool_size"] == 0


class TestMultiLevelCache:
    """Tests for multi-level caching."""

    def test_cache_config_creation(self):
        """Test cache configuration."""
        config = CacheConfig(
            max_size_bytes=1024 * 1024,
            eviction_policy=EvictionPolicy.LRU,
        )
        assert config.max_size_bytes == 1024 * 1024
        assert config.eviction_policy == EvictionPolicy.LRU

    def test_cache_layer_creation(self):
        """Test cache layer creation."""
        config = CacheConfig()
        layer = CacheLayer(CacheLevel.L1, config)
        assert layer.level == CacheLevel.L1

    def test_cache_set_get(self):
        """Test basic cache set/get."""
        config = CacheConfig()
        layer = CacheLayer(CacheLevel.L1, config)
        
        layer.set("key1", "value1")
        value = layer.get("key1")
        
        assert value == "value1"

    def test_cache_miss(self):
        """Test cache miss."""
        config = CacheConfig()
        layer = CacheLayer(CacheLevel.L1, config)
        
        value = layer.get("nonexistent")
        assert value is None

    def test_cache_ttl_expiration(self):
        """Test TTL expiration."""
        config = CacheConfig(default_ttl_seconds=1)
        layer = CacheLayer(CacheLevel.L1, config)
        
        layer.set("key1", "value1")
        time.sleep(1.1)
        
        value = layer.get("key1")
        assert value is None  # Should be expired

    def test_cache_eviction_lru(self):
        """Test LRU eviction."""
        config = CacheConfig(
            max_entries=2,
            eviction_policy=EvictionPolicy.LRU,
        )
        layer = CacheLayer(CacheLevel.L1, config)
        
        layer.set("key1", "value1")
        layer.set("key2", "value2")
        layer.set("key3", "value3")  # Should evict key1
        
        assert layer.get("key1") is None
        assert layer.get("key2") is not None
        assert layer.get("key3") is not None

    def test_cache_stats(self):
        """Test cache statistics."""
        config = CacheConfig()
        layer = CacheLayer(CacheLevel.L1, config)
        
        layer.set("key1", "value1")
        layer.get("key1")  # Hit
        layer.get("key2")  # Miss
        
        stats = layer.get_stats()
        assert stats.hits == 1
        assert stats.misses == 1
        assert stats.hit_rate() == 0.5

    def test_multi_level_cache_creation(self):
        """Test multi-level cache creation."""
        l1_config = CacheConfig(max_size_bytes=1024)
        l2_config = CacheConfig(max_size_bytes=10240)
        l3_config = CacheConfig(max_size_bytes=102400)
        
        cache = MultiLevelCache(l1_config, l2_config, l3_config)
        assert cache is not None

    def test_multi_level_cache_set_get(self):
        """Test multi-level cache set/get."""
        l1_config = CacheConfig()
        l2_config = CacheConfig()
        l3_config = CacheConfig()
        
        cache = MultiLevelCache(l1_config, l2_config, l3_config)
        
        cache.set("key1", "value1")
        value = cache.get("key1")
        
        assert value == "value1"

    def test_cache_promotion(self):
        """Test cache promotion from L2 to L1."""
        l1_config = CacheConfig()
        l2_config = CacheConfig()
        l3_config = CacheConfig()
        
        cache = MultiLevelCache(l1_config, l2_config, l3_config)
        
        # Set in L2 only
        cache._l2.set("key1", "value1")
        cache._l1.delete("key1")  # Ensure not in L1
        
        # Get should promote to L1
        value = cache.get("key1")
        assert value == "value1"
        assert cache._l1.get("key1") == "value1"

    def test_cache_delete_all_levels(self):
        """Test deletion from all cache levels."""
        l1_config = CacheConfig()
        l2_config = CacheConfig()
        l3_config = CacheConfig()
        
        cache = MultiLevelCache(l1_config, l2_config, l3_config)
        
        cache.set("key1", "value1")
        cache.delete("key1")
        
        assert cache._l1.get("key1") is None
        assert cache._l2.get("key1") is None
        assert cache._l3.get("key1") is None

    def test_cache_decorator(self):
        """Test cache decorator."""
        l1_config = CacheConfig()
        l2_config = CacheConfig()
        l3_config = CacheConfig()
        
        cache = MultiLevelCache(l1_config, l2_config, l3_config)
        
        call_count = 0
        
        @cache.cache_decorator()
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)
        
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Should only call once, second is cached

    def test_cache_clear(self):
        """Test clearing all cache levels."""
        l1_config = CacheConfig()
        l2_config = CacheConfig()
        l3_config = CacheConfig()
        
        cache = MultiLevelCache(l1_config, l2_config, l3_config)
        
        cache.set("key1", "value1")
        cache.clear()
        
        assert cache.get("key1") is None

    def test_cache_stats_multi_level(self):
        """Test statistics across all cache levels."""
        l1_config = CacheConfig()
        l2_config = CacheConfig()
        l3_config = CacheConfig()
        
        cache = MultiLevelCache(l1_config, l2_config, l3_config)
        
        cache.set("key1", "value1")
        cache.get("key1")  # L1 hit
        cache.get("key2")  # Miss all levels
        
        stats = cache.get_stats()
        assert stats["total_hits"] >= 1
        assert stats["total_misses"] >= 1

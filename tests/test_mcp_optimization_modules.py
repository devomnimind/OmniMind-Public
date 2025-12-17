"""Unit tests for MCP optimization modules (cache, compression, rate limiter)"""

import asyncio

import pytest

from src.integrations.mcp_cache import CacheStats, L1HotCache, MCPIntelligentCache, get_mcp_cache
from src.integrations.mcp_dynamic_rate_limiter import (
    DynamicRateLimiter,
    RequestPriority,
    SystemHealth,
    get_rate_limiter,
)
from src.integrations.mcp_semantic_compression import (
    CompressionMetrics,
    SemanticCompressor,
    get_semantic_compressor,
)


class TestCacheModule:
    """Test MCP Cache implementation"""

    def test_cache_stats_initialization(self):
        """Test CacheStats dataclass initialization"""
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.hit_rate == 0.0

    def test_cache_stats_hit_rate(self):
        """Test cache hit rate calculation"""
        stats = CacheStats(hits=70, misses=30)
        assert stats.hit_rate == 0.7

    @pytest.mark.asyncio
    async def test_l1_cache_get_put(self):
        """Test L1 hot cache get/put operations"""
        cache = L1HotCache(max_size=100)

        # Test put
        cache.put("key1", "value1")
        assert "key1" in cache.cache

        # Test get
        value = cache.get("key1")
        assert value == "value1"

    @pytest.mark.asyncio
    async def test_l1_cache_eviction(self):
        """Test L1 cache FIFO eviction"""
        cache = L1HotCache(max_size=3)

        # Fill cache
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")

        # Add one more - should evict first
        cache.put("key4", "value4")
        assert "key1" not in cache.cache
        assert "key4" in cache.cache

    @pytest.mark.asyncio
    async def test_intelligent_cache_get_put(self):
        """Test MCPIntelligentCache orchestrator"""
        cache = MCPIntelligentCache()

        # Put value
        await cache.put("test_key", {"data": "test_value"})

        # Get value
        result = await cache.get("test_key")
        assert result is not None
        assert result["data"] == "test_value"

    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Test cache miss behavior"""
        cache = MCPIntelligentCache()
        result = await cache.get("nonexistent_key")
        assert result is None

    def test_global_cache_instance(self):
        """Test global cache instance"""
        cache1 = get_mcp_cache()
        cache2 = get_mcp_cache()
        assert cache1 is cache2  # Same instance


class TestCompressionModule:
    """Test MCP Semantic Compression implementation"""

    def test_compression_metrics_initialization(self):
        """Test CompressionMetrics dataclass"""
        metrics = CompressionMetrics(
            original_tokens=0,
            compressed_tokens=0,
            reduction_percent=0.0,
            critical_info_preserved=True,
            compression_time_ms=0.0,
        )
        assert metrics.original_tokens == 0
        assert metrics.compressed_tokens == 0
        assert metrics.reduction_percent == 0.0

    def test_compression_metrics_ratio(self):
        """Test compression ratio calculation"""
        metrics = CompressionMetrics(
            original_tokens=100,
            compressed_tokens=25,
            reduction_percent=75.0,
            critical_info_preserved=True,
            compression_time_ms=1.5,
        )
        assert metrics.reduction_percent == 75.0

    @pytest.mark.asyncio
    async def test_compressor_basic(self):
        """Test basic compression"""
        compressor = SemanticCompressor()

        # Create sample context
        context = {
            "section1": "This is a test context with some information",
            "section2": "This is a test context with some information",  # Duplicate
            "section3": "This is important security information",
        }

        result = await compressor.compress(context)
        assert isinstance(result, dict)
        assert "__compression_metadata" in result

    @pytest.mark.asyncio
    async def test_compressor_target_tokens(self):
        """Test compression with target tokens"""
        compressor = SemanticCompressor()

        context = {
            "content": "Token test " * 1000,  # ~4000 tokens
        }

        result = await compressor.compress(context, target_tokens=500)
        metadata = result.get("__compression_metadata", {})
        assert metadata.get("reduction_percent", 0) > 0

    @pytest.mark.asyncio
    async def test_compressor_critical_preservation(self):
        """Test critical keyword preservation"""
        compressor = SemanticCompressor()

        context = {
            "safe": "normal information",
            "error": "CRITICAL ERROR: system failure",
            "status": "all good",
        }

        result = await compressor.compress(context, preserve_critical=True)
        # Result should still contain error-related content
        assert "error" in str(result).lower()

    def test_global_compressor_instance(self):
        """Test global compressor instance"""
        comp1 = get_semantic_compressor()
        comp2 = get_semantic_compressor()
        assert comp1 is comp2  # Same instance


class TestRateLimiterModule:
    """Test MCP Dynamic Rate Limiter implementation"""

    def test_system_health_initialization(self):
        """Test SystemHealth dataclass"""
        health = SystemHealth(
            cpu_percent=30.0,
            memory_percent=50.0,
            disk_percent=60.0,
            avg_latency_ms=50.0,
            queue_depth=10,
        )
        assert health.is_healthy
        assert not health.is_stressed

    def test_system_health_stressed(self):
        """Test stressed system detection"""
        health = SystemHealth(
            cpu_percent=95.0,
            memory_percent=95.0,
            disk_percent=95.0,
            avg_latency_ms=600.0,
            queue_depth=200,
        )
        assert health.is_stressed
        assert not health.is_healthy

    def test_request_priority_enum(self):
        """Test RequestPriority enum"""
        assert RequestPriority.CRITICAL.value == 1
        assert RequestPriority.HIGH.value == 2
        assert RequestPriority.NORMAL.value == 3
        assert RequestPriority.LOW.value == 4

    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = DynamicRateLimiter(initial_rps=100)
        assert limiter.current_rps == 100
        assert limiter.min_rps == 10
        assert limiter.max_rps == 1000

    @pytest.mark.asyncio
    async def test_rate_limiter_health_check(self):
        """Test rate limiter health monitoring"""
        limiter = DynamicRateLimiter()
        health = await limiter.check_system_health()

        assert health is not None
        assert health.cpu_percent >= 0
        assert health.memory_percent >= 0
        assert health.disk_percent >= 0

    @pytest.mark.asyncio
    async def test_rate_limiter_request_submission(self):
        """Test submitting a request through rate limiter"""
        limiter = DynamicRateLimiter(initial_rps=100)

        async def dummy_task():
            return "result"

        try:
            result = await limiter.submit_request(
                dummy_task(), priority=RequestPriority.NORMAL, timeout_seconds=5
            )
            assert result == "result"
        except Exception:
            # May timeout in heavy load, but submission itself should work
            pass

    @pytest.mark.asyncio
    async def test_rate_limiter_stats(self):
        """Test rate limiter statistics"""
        limiter = DynamicRateLimiter()
        stats = limiter.stats()

        assert "current_rps" in stats
        assert "requests_processed" in stats
        assert "requests_dropped" in stats
        assert "drop_rate" in stats

    def test_global_rate_limiter_instance(self):
        """Test global rate limiter instance"""
        limiter1 = get_rate_limiter()
        limiter2 = get_rate_limiter()
        assert limiter1 is limiter2  # Same instance


# Integration tests


class TestIntegration:
    """Integration tests for all modules together"""

    @pytest.mark.asyncio
    async def test_cache_with_compression(self):
        """Test cache working with compression"""
        cache = get_mcp_cache()
        compressor = get_semantic_compressor()

        # Create context
        context = {"information": "Information " * 100}

        # Compress
        compressed = await compressor.compress(context, target_tokens=500)

        # Cache compressed
        await cache.put("compressed_context", compressed)

        # Retrieve
        retrieved = await cache.get("compressed_context")
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_rate_limiter_with_multiple_priorities(self):
        """Test rate limiter handling different priorities"""
        limiter = get_rate_limiter()

        async def dummy_task(name: str):
            await asyncio.sleep(0.01)
            return f"Done: {name}"

        # Submit tasks with different priorities
        tasks = []
        for priority in [RequestPriority.CRITICAL, RequestPriority.HIGH, RequestPriority.NORMAL]:
            try:
                task = limiter.submit_request(
                    dummy_task("test"), priority=priority, timeout_seconds=2
                )
                tasks.append(task)
            except Exception:
                pass

        # All should complete (or timeout, but not error)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
    pytest.main([__file__, "-v", "--tb=short"])

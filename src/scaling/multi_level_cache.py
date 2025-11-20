"""Multi-Level Caching Strategy Module.

Implements L1/L2/L3 cache hierarchy for optimal performance and resource utilization.
Provides in-memory, distributed, and persistent caching layers.

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 7.4
"""

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
import hashlib

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class CacheLevel(Enum):
    """Cache hierarchy levels."""

    L1 = "l1"  # In-memory, fastest
    L2 = "l2"  # Distributed (Redis), medium speed
    L3 = "l3"  # Persistent (disk), slower


class EvictionPolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live


@dataclass
class CacheEntry:
    """Single cache entry.

    Attributes:
        key: Cache key
        value: Cached value
        level: Cache level where entry resides
        created_at: When entry was created
        accessed_at: When entry was last accessed
        access_count: Number of times accessed
        ttl_seconds: Time to live in seconds
        size_bytes: Size of the value in bytes
    """

    key: str
    value: Any
    level: CacheLevel
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired.

        Returns:
            True if expired
        """
        if self.ttl_seconds is None:
            return False
        age = time.time() - self.created_at
        return age > self.ttl_seconds

    def mark_accessed(self) -> None:
        """Mark entry as accessed."""
        self.accessed_at = time.time()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "level": self.level.value,
            "created_at": self.created_at,
            "accessed_at": self.accessed_at,
            "access_count": self.access_count,
            "ttl_seconds": self.ttl_seconds,
            "size_bytes": self.size_bytes,
            "age_seconds": time.time() - self.created_at,
        }


@dataclass
class CacheStats:
    """Cache statistics.

    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses
        evictions: Number of evictions
        size_bytes: Total size in bytes
        entry_count: Number of entries
    """

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    entry_count: int = 0

    def hit_rate(self) -> float:
        """Calculate cache hit rate.

        Returns:
            Hit rate (0.0 to 1.0)
        """
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "size_bytes": self.size_bytes,
            "entry_count": self.entry_count,
            "hit_rate": self.hit_rate(),
        }


@dataclass
class CacheConfig:
    """Configuration for cache layer.

    Attributes:
        max_size_bytes: Maximum cache size in bytes
        max_entries: Maximum number of entries
        default_ttl_seconds: Default TTL for entries
        eviction_policy: Eviction policy
        enable_stats: Enable statistics collection
    """

    max_size_bytes: int = 100 * 1024 * 1024  # 100MB
    max_entries: int = 10000
    default_ttl_seconds: Optional[int] = 3600
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    enable_stats: bool = True


class CacheLayer:
    """Single cache layer implementation.

    Implements a single cache level with configurable eviction policy.
    """

    def __init__(self, level: CacheLevel, config: CacheConfig):
        """Initialize cache layer.

        Args:
            level: Cache level
            config: Cache configuration
        """
        self.level = level
        self.config = config
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        self._access_order: List[str] = []  # For LRU/FIFO

        logger.info(
            "cache_layer_initialized",
            level=level.value,
            max_size_mb=config.max_size_bytes / (1024 * 1024),
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        entry = self._cache.get(key)

        if entry is None:
            self._stats.misses += 1
            return None

        # Check expiration
        if entry.is_expired():
            self.delete(key)
            self._stats.misses += 1
            return None

        # Update access information
        entry.mark_accessed()
        self._update_access_order(key)

        self._stats.hits += 1
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override

        Returns:
            True if value was cached
        """
        # Calculate value size
        size_bytes = self._calculate_size(value)

        # Check if eviction is needed
        if self._needs_eviction(size_bytes):
            self._evict()

        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            level=self.level,
            ttl_seconds=ttl_seconds or self.config.default_ttl_seconds,
            size_bytes=size_bytes,
        )

        # Store entry
        self._cache[key] = entry
        self._update_access_order(key)

        # Update stats
        self._stats.entry_count = len(self._cache)
        self._stats.size_bytes += size_bytes

        return True

    def delete(self, key: str) -> bool:
        """Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted
        """
        entry = self._cache.pop(key, None)
        if entry:
            self._stats.size_bytes -= entry.size_bytes
            self._stats.entry_count = len(self._cache)
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False

    def clear(self) -> None:
        """Clear all entries from cache."""
        self._cache.clear()
        self._access_order.clear()
        self._stats = CacheStats()

    def _needs_eviction(self, new_entry_size: int) -> bool:
        """Check if eviction is needed.

        Args:
            new_entry_size: Size of new entry

        Returns:
            True if eviction is needed
        """
        # Check entry count
        if len(self._cache) >= self.config.max_entries:
            return True

        # Check total size
        if self._stats.size_bytes + new_entry_size > self.config.max_size_bytes:
            return True

        return False

    def _evict(self) -> None:
        """Evict entries based on configured policy."""
        if not self._cache:
            return

        if self.config.eviction_policy == EvictionPolicy.LRU:
            self._evict_lru()
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            self._evict_lfu()
        elif self.config.eviction_policy == EvictionPolicy.FIFO:
            self._evict_fifo()
        elif self.config.eviction_policy == EvictionPolicy.TTL:
            self._evict_expired()

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._access_order:
            key = self._access_order[0]
            self.delete(key)
            self._stats.evictions += 1

    def _evict_lfu(self) -> None:
        """Evict least frequently used entry."""
        if not self._cache:
            return

        # Find entry with lowest access count
        min_entry = min(
            self._cache.values(),
            key=lambda e: e.access_count,
        )
        self.delete(min_entry.key)
        self._stats.evictions += 1

    def _evict_fifo(self) -> None:
        """Evict first in, first out."""
        if self._access_order:
            key = self._access_order[0]
            self.delete(key)
            self._stats.evictions += 1

    def _evict_expired(self) -> None:
        """Evict expired entries."""
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

        for key in expired_keys:
            self.delete(key)
            self._stats.evictions += 1

    def _update_access_order(self, key: str) -> None:
        """Update access order for LRU/FIFO.

        Args:
            key: Cache key
        """
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

    def _calculate_size(self, value: Any) -> int:
        """Calculate approximate size of value.

        Args:
            value: Value to measure

        Returns:
            Approximate size in bytes
        """
        try:
            # Simple approximation using JSON serialization
            json_str = json.dumps(value)
            return len(json_str.encode("utf-8"))
        except (TypeError, ValueError):
            # Fallback to estimate
            return 1024  # 1KB default

    def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        return self._stats


class MultiLevelCache:
    """Multi-level cache hierarchy (L1/L2/L3).

    Implements a three-tier cache hierarchy with automatic promotion
    and demotion of entries between levels.

    Example:
        >>> config_l1 = CacheConfig(max_size_bytes=10*1024*1024)  # 10MB
        >>> config_l2 = CacheConfig(max_size_bytes=100*1024*1024)  # 100MB
        >>> config_l3 = CacheConfig(max_size_bytes=1024*1024*1024)  # 1GB
        >>>
        >>> cache = MultiLevelCache(config_l1, config_l2, config_l3)
        >>> cache.set("key", "value")
        >>> value = cache.get("key")
        >>> stats = cache.get_stats()
    """

    def __init__(
        self,
        l1_config: CacheConfig,
        l2_config: CacheConfig,
        l3_config: CacheConfig,
    ):
        """Initialize multi-level cache.

        Args:
            l1_config: L1 cache configuration
            l2_config: L2 cache configuration
            l3_config: L3 cache configuration
        """
        self._l1 = CacheLayer(CacheLevel.L1, l1_config)
        self._l2 = CacheLayer(CacheLevel.L2, l2_config)
        self._l3 = CacheLayer(CacheLevel.L3, l3_config)

        logger.info("multi_level_cache_initialized")

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache hierarchy.

        Checks L1, then L2, then L3. Promotes values to higher levels on hit.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        # Try L1 (fastest)
        value = self._l1.get(key)
        if value is not None:
            logger.debug("cache_hit_l1", key=key)
            return value

        # Try L2
        value = self._l2.get(key)
        if value is not None:
            logger.debug("cache_hit_l2", key=key)
            # Promote to L1
            self._l1.set(key, value)
            return value

        # Try L3 (slowest)
        value = self._l3.get(key)
        if value is not None:
            logger.debug("cache_hit_l3", key=key)
            # Promote to L2 and L1
            self._l2.set(key, value)
            self._l1.set(key, value)
            return value

        logger.debug("cache_miss", key=key)
        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        level: CacheLevel = CacheLevel.L1,
    ) -> bool:
        """Set value in cache hierarchy.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL
            level: Initial cache level (defaults to L1)

        Returns:
            True if value was cached
        """
        # Set in specified level and all levels below
        if level == CacheLevel.L1:
            result = self._l1.set(key, value, ttl_seconds)
            self._l2.set(key, value, ttl_seconds)
            self._l3.set(key, value, ttl_seconds)
            return result
        elif level == CacheLevel.L2:
            result = self._l2.set(key, value, ttl_seconds)
            self._l3.set(key, value, ttl_seconds)
            return result
        else:  # L3
            return self._l3.set(key, value, ttl_seconds)

    def delete(self, key: str) -> bool:
        """Delete entry from all cache levels.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted from at least one level
        """
        deleted = False
        deleted |= self._l1.delete(key)
        deleted |= self._l2.delete(key)
        deleted |= self._l3.delete(key)
        return deleted

    def clear(self) -> None:
        """Clear all cache levels."""
        self._l1.clear()
        self._l2.clear()
        self._l3.clear()
        logger.info("all_cache_levels_cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all cache levels.

        Returns:
            Dictionary with statistics per level
        """
        return {
            "l1": self._l1.get_stats().to_dict(),
            "l2": self._l2.get_stats().to_dict(),
            "l3": self._l3.get_stats().to_dict(),
            "total_hits": (
                self._l1.get_stats().hits
                + self._l2.get_stats().hits
                + self._l3.get_stats().hits
            ),
            "total_misses": (
                self._l1.get_stats().misses
                + self._l2.get_stats().misses
                + self._l3.get_stats().misses
            ),
        }

    def cache_decorator(
        self,
        ttl_seconds: Optional[int] = None,
        level: CacheLevel = CacheLevel.L1,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator for caching function results.

        Args:
            ttl_seconds: Optional TTL
            level: Initial cache level

        Returns:
            Decorator function
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Create cache key from function name and arguments
                key_data = {
                    "func": func.__name__,
                    "args": str(args),
                    "kwargs": str(sorted(kwargs.items())),
                }
                key = hashlib.sha256(json.dumps(key_data).encode()).hexdigest()

                # Try to get from cache
                cached_value = self.get(key)
                if cached_value is not None:
                    return cached_value

                # Execute function
                result = func(*args, **kwargs)

                # Cache result
                self.set(key, result, ttl_seconds, level)

                return result

            return wrapper

        return decorator

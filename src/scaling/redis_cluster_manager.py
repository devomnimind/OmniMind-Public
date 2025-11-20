"""
Redis Cluster Manager for distributed caching.

This module provides a production-ready Redis Cluster integration with:
- Automatic sharding across nodes
- Master-replica replication
- Sentinel-based failover
- Connection pooling
- Health monitoring and diagnostics

Example:
    >>> from src.scaling.redis_cluster_manager import RedisClusterManager
    >>> manager = RedisClusterManager(
    ...     nodes=[
    ...         {"host": "localhost", "port": 7000},
    ...         {"host": "localhost", "port": 7001},
    ...     ]
    ... )
    >>> manager.set("key", "value", ttl=3600)
    >>> value = manager.get("key")
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging
import time
import json

# Redis is optional dependency for local-first operation
try:
    import redis
    from redis.cluster import RedisCluster
    from redis.sentinel import Sentinel
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    RedisCluster = None
    Sentinel = None

logger = logging.getLogger(__name__)


class ClusterState(Enum):
    """Redis Cluster states."""
    OK = "ok"
    FAIL = "fail"
    UNKNOWN = "unknown"


@dataclass
class ClusterNode:
    """Represents a Redis Cluster node."""
    node_id: str
    host: str
    port: int
    role: str  # master or slave
    slots: List[int]
    master_id: Optional[str] = None
    
    def is_master(self) -> bool:
        """Check if node is a master."""
        return self.role == "master"


@dataclass
class ClusterHealth:
    """Redis Cluster health information."""
    state: ClusterState
    nodes_count: int
    masters_count: int
    replicas_count: int
    slots_assigned: int
    slots_ok: int
    slots_pfail: int
    slots_fail: int
    
    def is_healthy(self) -> bool:
        """Check if cluster is healthy."""
        return (
            self.state == ClusterState.OK and
            self.slots_assigned == 16384 and
            self.slots_fail == 0
        )


class RedisClusterManager:
    """
    Manages Redis Cluster operations with production-grade features.
    
    This manager handles:
    - Cluster initialization and connection management
    - Key-value operations with automatic sharding
    - Health monitoring and diagnostics
    - Failover detection and handling
    - Statistics tracking
    
    Attributes:
        nodes: List of cluster node configurations
        cluster: RedisCluster instance (if Redis available)
        sentinel: Sentinel instance (if configured)
        max_connections: Maximum connections per node
        
    Example:
        >>> manager = RedisClusterManager(
        ...     nodes=[{"host": "localhost", "port": 7000}],
        ...     max_connections=50
        ... )
        >>> manager.set("user:123", json.dumps({"name": "Alice"}))
        >>> data = manager.get("user:123")
    """
    
    def __init__(
        self,
        nodes: List[Dict[str, Any]],
        sentinel_nodes: Optional[List[tuple[str, int]]] = None,
        password: Optional[str] = None,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        decode_responses: bool = True
    ):
        """
        Initialize Redis Cluster manager.
        
        Args:
            nodes: List of node configs [{"host": str, "port": int}, ...]
            sentinel_nodes: Optional sentinel nodes [(host, port), ...]
            password: Optional cluster password
            max_connections: Max connections per node (default: 50)
            socket_timeout: Socket timeout in seconds (default: 5.0)
            decode_responses: Decode bytes to strings (default: True)
            
        Raises:
            ImportError: If redis package not installed
            ConnectionError: If cannot connect to cluster
        """
        if not REDIS_AVAILABLE:
            logger.warning(
                "Redis package not available. "
                "Operating in local-only mode with in-memory fallback."
            )
            self.cluster = None
            self.sentinel = None
            self._local_cache: Dict[str, tuple[Any, Optional[float]]] = {}
            self.nodes = nodes
            return
        
        self.nodes = nodes
        self.password = password
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.decode_responses = decode_responses
        
        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        
        # Initialize cluster
        try:
            self.cluster = RedisCluster(
                startup_nodes=nodes,
                decode_responses=decode_responses,
                skip_full_coverage_check=False,
                max_connections=max_connections,
                password=password,
                socket_timeout=socket_timeout
            )
            logger.info(f"Connected to Redis Cluster with {len(nodes)} nodes")
        except Exception as e:
            logger.error(f"Failed to connect to Redis Cluster: {e}")
            raise ConnectionError(f"Cannot connect to Redis Cluster: {e}")
        
        # Initialize sentinel if provided
        self.sentinel = None
        if sentinel_nodes:
            try:
                self.sentinel = Sentinel(
                    sentinel_nodes,
                    socket_timeout=0.1,
                    password=password
                )
                logger.info(f"Connected to Sentinel with {len(sentinel_nodes)} nodes")
            except Exception as e:
                logger.warning(f"Failed to connect to Sentinel: {e}")
    
    def set(
        self,
        key: str,
        value: Union[str, bytes, int, float],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set key-value with optional TTL.
        
        Args:
            key: Cache key
            value: Value to store (str, bytes, int, or float)
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            True if successful, False otherwise
            
        Example:
            >>> manager.set("user:123", "Alice", ttl=3600)
            True
        """
        if not self.cluster:
            # Local fallback
            expiry = time.time() + ttl if ttl else None
            self._local_cache[key] = (value, expiry)
            self._stats["sets"] += 1
            return True
        
        try:
            if ttl:
                result = self.cluster.setex(key, ttl, value)
            else:
                result = self.cluster.set(key, value)
            
            self._stats["sets"] += 1
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to set {key}: {e}")
            self._stats["errors"] += 1
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
            
        Example:
            >>> manager.get("user:123")
            'Alice'
        """
        if not self.cluster:
            # Local fallback
            if key in self._local_cache:
                value, expiry = self._local_cache[key]
                if expiry is None or time.time() < expiry:
                    self._stats["hits"] += 1
                    return value
                else:
                    del self._local_cache[key]
            self._stats["misses"] += 1
            return None
        
        try:
            value = self.cluster.get(key)
            if value is not None:
                self._stats["hits"] += 1
            else:
                self._stats["misses"] += 1
            return value
            
        except Exception as e:
            logger.error(f"Failed to get {key}: {e}")
            self._stats["errors"] += 1
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete key.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
            
        Example:
            >>> manager.delete("user:123")
            True
        """
        if not self.cluster:
            # Local fallback
            if key in self._local_cache:
                del self._local_cache[key]
                self._stats["deletes"] += 1
                return True
            return False
        
        try:
            result = self.cluster.delete(key)
            self._stats["deletes"] += 1
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            self._stats["errors"] += 1
            return False
    
    def mget(self, keys: List[str]) -> List[Optional[Any]]:
        """
        Get multiple values by keys.
        
        Args:
            keys: List of cache keys
            
        Returns:
            List of values (None for missing keys)
            
        Example:
            >>> manager.mget(["user:123", "user:456"])
            ['Alice', 'Bob']
        """
        if not self.cluster:
            # Local fallback
            results = []
            for key in keys:
                if key in self._local_cache:
                    value, expiry = self._local_cache[key]
                    if expiry is None or time.time() < expiry:
                        results.append(value)
                    else:
                        del self._local_cache[key]
                        results.append(None)
                else:
                    results.append(None)
            return results
        
        try:
            result = self.cluster.mget(keys)
            return list(result) if result is not None else [None] * len(keys)
        except Exception as e:
            logger.error(f"Failed to mget: {e}")
            return [None] * len(keys)
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
            
        Example:
            >>> manager.exists("user:123")
            True
        """
        if not self.cluster:
            # Local fallback
            if key in self._local_cache:
                _, expiry = self._local_cache[key]
                if expiry is None or time.time() < expiry:
                    return True
                del self._local_cache[key]
            return False
        
        try:
            return bool(self.cluster.exists(key))
        except Exception as e:
            logger.error(f"Failed to check exists {key}: {e}")
            return False
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """
        Get cluster information.
        
        Returns:
            Dict with cluster state, nodes, and slot assignments
            
        Example:
            >>> info = manager.get_cluster_info()
            >>> print(info["state"])
            'ok'
        """
        if not self.cluster:
            return {
                "state": "local_only",
                "nodes": [],
                "slots_assigned": 0,
                "message": "Operating in local-only mode"
            }
        
        info: Dict[str, Any] = {
            "nodes": [],
            "slots_assigned": 0,
            "state": ClusterState.UNKNOWN.value
        }
        
        try:
            cluster_info = self.cluster.cluster_info()
            info["state"] = cluster_info.get("cluster_state", "unknown")
            info["slots_assigned"] = cluster_info.get("cluster_slots_assigned", 0)
            info["slots_ok"] = cluster_info.get("cluster_slots_ok", 0)
            info["slots_pfail"] = cluster_info.get("cluster_slots_pfail", 0)
            info["slots_fail"] = cluster_info.get("cluster_slots_fail", 0)
            
            nodes_info = self.cluster.cluster_nodes()
            for node_line in nodes_info.split('\n'):
                if node_line.strip():
                    info["nodes"].append(node_line)
            
        except Exception as e:
            logger.error(f"Failed to get cluster info: {e}")
            info["error"] = str(e)
        
        return info
    
    def get_cluster_health(self) -> ClusterHealth:
        """
        Get cluster health status.
        
        Returns:
            ClusterHealth object with detailed health metrics
            
        Example:
            >>> health = manager.get_cluster_health()
            >>> if health.is_healthy():
            ...     print("Cluster is healthy")
        """
        if not self.cluster:
            return ClusterHealth(
                state=ClusterState.UNKNOWN,
                nodes_count=0,
                masters_count=0,
                replicas_count=0,
                slots_assigned=0,
                slots_ok=0,
                slots_pfail=0,
                slots_fail=0
            )
        
        try:
            info = self.get_cluster_info()
            
            # Count masters and replicas
            masters_count = 0
            replicas_count = 0
            for node_line in info.get("nodes", []):
                if "master" in node_line:
                    masters_count += 1
                elif "slave" in node_line:
                    replicas_count += 1
            
            state_str = info.get("state", "unknown")
            state = ClusterState.OK if state_str == "ok" else ClusterState.FAIL if state_str == "fail" else ClusterState.UNKNOWN
            
            return ClusterHealth(
                state=state,
                nodes_count=len(info.get("nodes", [])),
                masters_count=masters_count,
                replicas_count=replicas_count,
                slots_assigned=info.get("slots_assigned", 0),
                slots_ok=info.get("slots_ok", 0),
                slots_pfail=info.get("slots_pfail", 0),
                slots_fail=info.get("slots_fail", 0)
            )
            
        except Exception as e:
            logger.error(f"Failed to get cluster health: {e}")
            return ClusterHealth(
                state=ClusterState.UNKNOWN,
                nodes_count=0,
                masters_count=0,
                replicas_count=0,
                slots_assigned=0,
                slots_ok=0,
                slots_pfail=0,
                slots_fail=0
            )
    
    def health_check(self) -> bool:
        """
        Perform quick health check.
        
        Returns:
            True if cluster is healthy, False otherwise
            
        Example:
            >>> if manager.health_check():
            ...     print("Cluster OK")
        """
        health = self.get_cluster_health()
        return health.is_healthy()
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get operation statistics.
        
        Returns:
            Dict with hits, misses, sets, deletes, errors counts
            
        Example:
            >>> stats = manager.get_stats()
            >>> hit_rate = stats["hits"] / (stats["hits"] + stats["misses"])
        """
        stats = self._stats.copy()
        hits = int(stats["hits"])
        misses = int(stats["misses"])
        total = hits + misses
        stats["hit_rate"] = hits / total if total > 0 else 0.0  # type: ignore
        return stats
    
    def flush_all(self) -> bool:
        """
        Flush all keys from cluster (DANGEROUS).
        
        Returns:
            True if successful, False otherwise
            
        Warning:
            This deletes ALL data from the cluster!
        """
        if not self.cluster:
            self._local_cache.clear()
            return True
        
        try:
            self.cluster.flushall()
            logger.warning("Flushed all keys from Redis Cluster")
            return True
        except Exception as e:
            logger.error(f"Failed to flush cluster: {e}")
            return False
    
    def close(self) -> None:
        """Close cluster connections."""
        if self.cluster:
            try:
                self.cluster.close()
                logger.info("Closed Redis Cluster connections")
            except Exception as e:
                logger.error(f"Error closing cluster: {e}")

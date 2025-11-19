"""Scaling infrastructure for OmniMind.

Multi-node scaling, load balancing, distributed transactions, and resource pooling.
"""

# Multi-tenant isolation (new module)
from src.scaling.multi_tenant_isolation import (
    MultiTenantIsolationManager,
    TenantConfig,
    TenantStatus,
    ResourceType,
    ResourceQuota,
    create_tenant,
    get_tenant,
    get_isolation_manager,
)

from src.scaling.intelligent_load_balancer import (
    IntelligentLoadBalancer,
    NodePerformanceMetrics,
    WorkloadPrediction,
)
from src.scaling.multi_node import (
    ClusterCoordinator,
    DistributedTask,
    LoadBalancer,
    NodeInfo,
    NodeStatus,
    TaskStatus,
)
from src.scaling.node_failure_recovery import (
    FailoverCoordinator,
    LogEntry,
    LogEntryType,
    NodeRole,
    RaftNode,
    RaftState,
)
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
from src.scaling.redis_cluster_manager import (
    RedisClusterManager,
    ClusterState,
    ClusterNode,
    ClusterHealth,
)

__all__ = [
    # Multi-Tenant Isolation (NEW)
    "MultiTenantIsolationManager",
    "TenantConfig",
    "TenantStatus",
    "ResourceType",
    "ResourceQuota",
    "create_tenant",
    "get_tenant",
    "get_isolation_manager",
    # Cluster Management
    "ClusterCoordinator",
    "DistributedTask",
    "FailoverCoordinator",
    "IntelligentLoadBalancer",
    "LoadBalancer",
    "LogEntry",
    "LogEntryType",
    "NodeInfo",
    "NodePerformanceMetrics",
    "NodeRole",
    "NodeStatus",
    "RaftNode",
    "RaftState",
    "TaskStatus",
    "WorkloadPrediction",
    # GPU Resource Pooling
    "GPUDevice",
    "GPUResourcePool",
    "GPUPoolConfig",
    "GPUStatus",
    "GPUTask",
    # Database Connection Pooling
    "ConnectionInfo",
    "ConnectionStatus",
    "DatabaseConnectionPool",
    "PoolConfig",
    # Multi-Level Caching
    "CacheConfig",
    "CacheLevel",
    "CacheLayer",
    "EvictionPolicy",
    "MultiLevelCache",
    # Redis Cluster (NEW)
    "RedisClusterManager",
    "ClusterState",
    "ClusterNode",
    "ClusterHealth",
]

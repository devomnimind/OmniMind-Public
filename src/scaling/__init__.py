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

"""Scaling infrastructure for OmniMind.

Multi-node scaling, load balancing, distributed transactions, and resource pooling.
"""

from src.scaling.database_connection_pool import (
    ConnectionInfo,
    ConnectionStatus,
    DatabaseConnectionPool,
    PoolConfig,
)
from src.scaling.gpu_resource_pool import (
    GPUDevice,
    GPUPoolConfig,
    GPUResourcePool,
    GPUStatus,
    GPUTask,
)
from src.scaling.intelligent_load_balancer import (
    IntelligentLoadBalancer,
    NodePerformanceMetrics,
    WorkloadPrediction,
)
from src.scaling.multi_level_cache import (
    CacheConfig,
    CacheLayer,
    CacheLevel,
    EvictionPolicy,
    MultiLevelCache,
)
from src.scaling.multi_node import (
    ClusterCoordinator,
    DistributedTask,
    LoadBalancer,
    NodeInfo,
    NodeStatus,
    TaskStatus,
)

# Multi-tenant isolation (new module)
from src.scaling.multi_tenant_isolation import (
    MultiTenantIsolationManager,
    ResourceQuota,
    ResourceType,
    TenantConfig,
    TenantStatus,
    create_tenant,
    get_isolation_manager,
    get_tenant,
)
from src.scaling.node_failure_recovery import (
    FailoverCoordinator,
    LogEntry,
    LogEntryType,
    NodeRole,
    RaftNode,
    RaftState,
)
from src.scaling.redis_cluster_manager import (
    ClusterHealth,
    ClusterNode,
    ClusterState,
    RedisClusterManager,
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

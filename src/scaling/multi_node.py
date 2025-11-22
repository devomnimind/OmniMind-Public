"""Multi-node scaling configuration for OmniMind.

This module provides distributed task execution capabilities:
- Task distribution across multiple nodes
- Load balancing
- Health monitoring of nodes
- Automatic failover
- Node discovery and registration
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class NodeStatus(str, Enum):
    """Node status states."""

    ACTIVE = "active"
    BUSY = "busy"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class NodeInfo:
    """Information about a cluster node."""

    node_id: str
    hostname: str
    ip_address: str
    port: int
    status: NodeStatus = NodeStatus.ACTIVE
    cpu_cores: int = 1
    memory_gb: float = 1.0
    max_concurrent_tasks: int = 4
    current_tasks: int = 0
    total_tasks_completed: int = 0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    capabilities: Set[str] = field(default_factory=set)

    def get_load_factor(self) -> float:
        """Calculate current load factor (0.0 to 1.0)."""
        if self.max_concurrent_tasks == 0:
            return 1.0
        return self.current_tasks / self.max_concurrent_tasks

    def can_accept_task(self) -> bool:
        """Check if node can accept new tasks."""
        return (
            self.status == NodeStatus.ACTIVE
            and self.current_tasks < self.max_concurrent_tasks
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "node_id": self.node_id,
            "hostname": self.hostname,
            "ip_address": self.ip_address,
            "port": self.port,
            "status": self.status.value,
            "cpu_cores": self.cpu_cores,
            "memory_gb": self.memory_gb,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "current_tasks": self.current_tasks,
            "total_tasks_completed": self.total_tasks_completed,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "load_factor": self.get_load_factor(),
            "capabilities": list(self.capabilities),
        }


@dataclass
class DistributedTask:
    """Represents a task to be executed on the cluster."""

    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 5
    status: TaskStatus = TaskStatus.PENDING
    assigned_node: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority,
            "status": self.status.value,
            "assigned_node": self.assigned_node,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


class LoadBalancer:
    """Load balancer for distributing tasks across nodes."""

    def __init__(self, strategy: str = "least_loaded") -> None:
        """Initialize load balancer."""
        self.strategy = strategy
        self._round_robin_index = 0

    def _select_least_loaded_node(self, available_nodes: List[NodeInfo]) -> NodeInfo:
        """Select the least loaded node from available nodes."""
        return min(available_nodes, key=lambda n: n.get_load_factor())

    def _select_round_robin_node(self, available_nodes: List[NodeInfo]) -> NodeInfo:
        """Select node using round-robin strategy."""
        node = available_nodes[self._round_robin_index % len(available_nodes)]
        self._round_robin_index += 1
        return node

    def select_node(
        self, nodes: List[NodeInfo], task: Optional[DistributedTask] = None
    ) -> Optional[NodeInfo]:
        """Select best node for task execution."""
        available_nodes = [n for n in nodes if n.can_accept_task()]

        if not available_nodes:
            return None

        if task and task.task_type:
            capable_nodes = [
                n for n in available_nodes if task.task_type in n.capabilities
            ]
            if capable_nodes:
                available_nodes = capable_nodes

        if self.strategy == "least_loaded":
            return self._select_least_loaded_node(available_nodes)
        elif self.strategy == "round_robin":
            return self._select_round_robin_node(available_nodes)
        elif self.strategy == "random":
            import random

            return random.choice(available_nodes)
        else:
            return self._select_least_loaded_node(available_nodes)


class ClusterCoordinator:
    """Coordinator for multi-node cluster management."""

    def __init__(
        self,
        node_id: str,
        load_balancing_strategy: str = "least_loaded",
        heartbeat_interval: float = 10.0,
        heartbeat_timeout: float = 30.0,
    ) -> None:
        """Initialize cluster coordinator."""
        self.node_id = node_id
        self.nodes: Dict[str, NodeInfo] = {}
        self.tasks: Dict[str, DistributedTask] = {}
        self.load_balancer = LoadBalancer(strategy=load_balancing_strategy)
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        self._task_callbacks: Dict[str, Callable[[DistributedTask], Any]] = {}
        self._running = False
        self._heartbeat_task: Optional[asyncio.Task[None]] = None

    def register_node(self, node: NodeInfo) -> None:
        """Register a new node in the cluster."""
        self.nodes[node.node_id] = node
        logger.info(f"Registered node {node.node_id} ({node.hostname})")

    def unregister_node(self, node_id: str) -> None:
        """Unregister a node from the cluster."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            logger.info(f"Unregistered node {node_id}")

    def update_node_heartbeat(self, node_id: str) -> None:
        """Update node heartbeat timestamp."""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = datetime.now()

    def get_node_status(self, node_id: str) -> Optional[NodeStatus]:
        """Get status of a specific node."""
        node = self.nodes.get(node_id)
        return node.status if node else None

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status."""
        total_nodes = len(self.nodes)
        active_nodes = sum(
            1 for n in self.nodes.values() if n.status == NodeStatus.ACTIVE
        )
        total_capacity = sum(n.max_concurrent_tasks for n in self.nodes.values())
        current_load = sum(n.current_tasks for n in self.nodes.values())

        return {
            "coordinator_node_id": self.node_id,
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "offline_nodes": total_nodes - active_nodes,
            "total_capacity": total_capacity,
            "current_load": current_load,
            "load_percentage": (
                (current_load / total_capacity * 100) if total_capacity > 0 else 0
            ),
            "pending_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.PENDING
            ),
            "running_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING
            ),
            "nodes": [node.to_dict() for node in self.nodes.values()],
        }

    def submit_task(self, task: DistributedTask) -> bool:
        """Submit a task for execution."""
        available_nodes = list(self.nodes.values())
        selected_node = self.load_balancer.select_node(available_nodes, task)

        if not selected_node:
            logger.warning(f"No available node for task {task.task_id}")
            return False

        task.assigned_node = selected_node.node_id
        task.status = TaskStatus.PENDING
        self.tasks[task.task_id] = task
        selected_node.current_tasks += 1

        logger.info(f"Task {task.task_id} assigned to node {selected_node.node_id}")
        return True

    def complete_task(
        self, task_id: str, result: Dict[str, Any], error: Optional[str] = None
    ) -> None:
        """Mark a task as completed."""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return

        task = self.tasks[task_id]
        task.completed_at = datetime.now()
        task.result = result
        task.error = error
        task.status = TaskStatus.COMPLETED if not error else TaskStatus.FAILED

        if task.assigned_node and task.assigned_node in self.nodes:
            node = self.nodes[task.assigned_node]
            node.current_tasks = max(0, node.current_tasks - 1)
            if not error:
                node.total_tasks_completed += 1

        logger.info(f"Task {task_id} completed with status {task.status.value}")

    async def _check_heartbeats(self) -> None:
        """Check node heartbeats and mark offline nodes."""
        while self._running:
            now = datetime.now()
            for node in self.nodes.values():
                time_since_heartbeat = (now - node.last_heartbeat).total_seconds()
                if time_since_heartbeat > self.heartbeat_timeout:
                    if node.status != NodeStatus.OFFLINE:
                        logger.warning(
                            f"Node {node.node_id} marked offline "
                            f"(last heartbeat {time_since_heartbeat:.1f}s ago)"
                        )
                        node.status = NodeStatus.OFFLINE

            await asyncio.sleep(self.heartbeat_interval)

    async def start(self) -> None:
        """Start the cluster coordinator."""
        self._running = True
        self._heartbeat_task = asyncio.create_task(self._check_heartbeats())
        logger.info(f"Cluster coordinator started (node_id={self.node_id})")

    async def stop(self) -> None:
        """Stop the cluster coordinator."""
        self._running = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        logger.info("Cluster coordinator stopped")

    def register_task_callback(
        self, task_type: str, callback: Callable[[DistributedTask], Any]
    ) -> None:
        """Register a callback for a specific task type."""
        self._task_callbacks[task_type] = callback
        logger.info(f"Registered callback for task type: {task_type}")

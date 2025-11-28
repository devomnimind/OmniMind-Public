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

"""Tests for multi-node scaling infrastructure."""

import asyncio

import pytest

from src.scaling.multi_node import (
    ClusterCoordinator,
    DistributedTask,
    LoadBalancer,
    NodeInfo,
    NodeStatus,
    TaskStatus,
)


def test_node_info_creation() -> None:
    """Test NodeInfo creation and properties."""
    node = NodeInfo(
        node_id="node-1",
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8000,
        cpu_cores=4,
        memory_gb=8.0,
        max_concurrent_tasks=10,
        capabilities={"cpu_tasks", "io_tasks"},
    )

    assert node.node_id == "node-1"
    assert node.status == NodeStatus.ACTIVE
    assert node.get_load_factor() == 0.0
    assert node.can_accept_task() is True


def test_node_load_factor() -> None:
    """Test node load factor calculation."""
    node = NodeInfo(
        node_id="node-1",
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8000,
        max_concurrent_tasks=10,
    )

    assert node.get_load_factor() == 0.0

    node.current_tasks = 5
    assert node.get_load_factor() == 0.5

    node.current_tasks = 10
    assert node.get_load_factor() == 1.0


def test_node_can_accept_task() -> None:
    """Test node task acceptance logic."""
    node = NodeInfo(
        node_id="node-1",
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8000,
        max_concurrent_tasks=5,
    )

    # Active node with capacity
    assert node.can_accept_task() is True

    # Active node at capacity
    node.current_tasks = 5
    assert node.can_accept_task() is False

    # Offline node
    node.current_tasks = 0
    node.status = NodeStatus.OFFLINE
    assert node.can_accept_task() is False


def test_node_to_dict() -> None:
    """Test NodeInfo serialization."""
    node = NodeInfo(
        node_id="node-1",
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8000,
        cpu_cores=4,
        memory_gb=8.0,
        capabilities={"cpu_tasks"},
    )

    data = node.to_dict()

    assert data["node_id"] == "node-1"
    assert data["hostname"] == "worker-1"
    assert data["status"] == "active"
    assert data["cpu_cores"] == 4
    assert data["memory_gb"] == 8.0
    assert "cpu_tasks" in data["capabilities"]


def test_distributed_task_creation() -> None:
    """Test DistributedTask creation."""
    task = DistributedTask(
        task_id="task-1",
        task_type="cpu_intensive",
        payload={"data": "test"},
        priority=3,
    )

    assert task.task_id == "task-1"
    assert task.status == TaskStatus.PENDING
    assert task.assigned_node is None
    assert task.retry_count == 0


def test_distributed_task_to_dict() -> None:
    """Test DistributedTask serialization."""
    task = DistributedTask(
        task_id="task-1",
        task_type="cpu_intensive",
        payload={"data": "test"},
    )

    data = task.to_dict()

    assert data["task_id"] == "task-1"
    assert data["task_type"] == "cpu_intensive"
    assert data["status"] == "pending"
    assert data["payload"] == {"data": "test"}


def test_load_balancer_least_loaded() -> None:
    """Test least loaded load balancing strategy."""
    lb = LoadBalancer(strategy="least_loaded")

    nodes = [
        NodeInfo(
            "node-1",
            "worker-1",
            "192.168.1.10",
            8000,
            current_tasks=5,
            max_concurrent_tasks=10,
        ),
        NodeInfo(
            "node-2",
            "worker-2",
            "192.168.1.11",
            8000,
            current_tasks=2,
            max_concurrent_tasks=10,
        ),
        NodeInfo(
            "node-3",
            "worker-3",
            "192.168.1.12",
            8000,
            current_tasks=8,
            max_concurrent_tasks=10,
        ),
    ]

    selected = lb.select_node(nodes)
    assert selected is not None
    assert selected.node_id == "node-2"  # Least loaded


def test_load_balancer_round_robin() -> None:
    """Test round robin load balancing strategy."""
    lb = LoadBalancer(strategy="round_robin")

    nodes = [
        NodeInfo("node-1", "worker-1", "192.168.1.10", 8000),
        NodeInfo("node-2", "worker-2", "192.168.1.11", 8000),
        NodeInfo("node-3", "worker-3", "192.168.1.12", 8000),
    ]

    # Should cycle through nodes
    selected1 = lb.select_node(nodes)
    selected2 = lb.select_node(nodes)
    selected3 = lb.select_node(nodes)
    selected4 = lb.select_node(nodes)

    assert selected1 is not None
    assert selected2 is not None
    assert selected3 is not None
    assert selected4 is not None
    assert selected1.node_id == selected4.node_id  # Should cycle back


def test_load_balancer_capability_filtering() -> None:
    """Test load balancer filters by task capabilities."""
    lb = LoadBalancer(strategy="least_loaded")

    nodes = [
        NodeInfo(
            "node-1",
            "worker-1",
            "192.168.1.10",
            8000,
            capabilities={"cpu_tasks"},
        ),
        NodeInfo(
            "node-2",
            "worker-2",
            "192.168.1.11",
            8000,
            capabilities={"gpu_tasks"},
        ),
    ]

    task = DistributedTask(task_id="task-1", task_type="gpu_tasks", payload={})

    selected = lb.select_node(nodes, task)
    assert selected is not None
    assert selected.node_id == "node-2"


@pytest.mark.asyncio
async def test_cluster_coordinator_initialization() -> None:
    """Test ClusterCoordinator initialization."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    assert coordinator.node_id == "coordinator-1"
    assert len(coordinator.nodes) == 0
    assert len(coordinator.tasks) == 0


@pytest.mark.asyncio
async def test_cluster_coordinator_register_node() -> None:
    """Test node registration."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    node = NodeInfo("node-1", "worker-1", "192.168.1.10", 8000)
    coordinator.register_node(node)

    assert len(coordinator.nodes) == 1
    assert "node-1" in coordinator.nodes


@pytest.mark.asyncio
async def test_cluster_coordinator_unregister_node() -> None:
    """Test node unregistration."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    node = NodeInfo("node-1", "worker-1", "192.168.1.10", 8000)
    coordinator.register_node(node)
    coordinator.unregister_node("node-1")

    assert len(coordinator.nodes) == 0


@pytest.mark.asyncio
async def test_cluster_coordinator_submit_task() -> None:
    """Test task submission."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    # Register node
    node = NodeInfo("node-1", "worker-1", "192.168.1.10", 8000)
    coordinator.register_node(node)

    # Submit task
    task = DistributedTask(task_id="task-1", task_type="test", payload={"data": "test"})
    success = coordinator.submit_task(task)

    assert success is True
    assert task.assigned_node == "node-1"
    assert task.status == TaskStatus.PENDING
    assert coordinator.nodes["node-1"].current_tasks == 1


@pytest.mark.asyncio
async def test_cluster_coordinator_complete_task() -> None:
    """Test task completion."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    # Register node and submit task
    node = NodeInfo("node-1", "worker-1", "192.168.1.10", 8000)
    coordinator.register_node(node)

    task = DistributedTask(task_id="task-1", task_type="test", payload={})
    coordinator.submit_task(task)

    # Complete task
    coordinator.complete_task("task-1", {"result": "success"})

    assert task.status == TaskStatus.COMPLETED
    assert task.result == {"result": "success"}
    assert coordinator.nodes["node-1"].current_tasks == 0
    assert coordinator.nodes["node-1"].total_tasks_completed == 1


@pytest.mark.asyncio
async def test_cluster_coordinator_complete_task_with_error() -> None:
    """Test task completion with error."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    node = NodeInfo("node-1", "worker-1", "192.168.1.10", 8000)
    coordinator.register_node(node)

    task = DistributedTask(task_id="task-1", task_type="test", payload={})
    coordinator.submit_task(task)

    # Complete with error
    coordinator.complete_task("task-1", {}, error="Task failed")

    assert task.status == TaskStatus.FAILED
    assert task.error == "Task failed"
    assert coordinator.nodes["node-1"].total_tasks_completed == 0


@pytest.mark.asyncio
async def test_cluster_coordinator_get_cluster_status() -> None:
    """Test cluster status retrieval."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    # Register multiple nodes
    coordinator.register_node(
        NodeInfo("node-1", "worker-1", "192.168.1.10", 8000, max_concurrent_tasks=5)
    )
    coordinator.register_node(
        NodeInfo("node-2", "worker-2", "192.168.1.11", 8000, max_concurrent_tasks=5)
    )

    status = coordinator.get_cluster_status()

    assert status["coordinator_node_id"] == "coordinator-1"
    assert status["total_nodes"] == 2
    assert status["active_nodes"] == 2
    assert status["total_capacity"] == 10
    assert status["current_load"] == 0
    assert status["pending_tasks"] == 0


@pytest.mark.asyncio
async def test_cluster_coordinator_heartbeat() -> None:
    """Test heartbeat monitoring."""
    coordinator = ClusterCoordinator(
        node_id="coordinator-1",
        heartbeat_interval=0.1,
        heartbeat_timeout=0.2,
    )

    node = NodeInfo("node-1", "worker-1", "192.168.1.10", 8000)
    coordinator.register_node(node)

    # Start coordinator
    await coordinator.start()

    # Wait for heartbeat timeout
    await asyncio.sleep(0.3)

    # Node should be marked offline
    assert coordinator.nodes["node-1"].status == NodeStatus.OFFLINE

    await coordinator.stop()


@pytest.mark.asyncio
async def test_cluster_coordinator_update_heartbeat() -> None:
    """Test heartbeat update keeps node alive."""
    coordinator = ClusterCoordinator(
        node_id="coordinator-1",
        heartbeat_interval=0.1,
        heartbeat_timeout=0.5,
    )

    node = NodeInfo("node-1", "worker-1", "192.168.1.10", 8000)
    coordinator.register_node(node)

    await coordinator.start()

    # Keep updating heartbeat
    for _ in range(5):
        coordinator.update_node_heartbeat("node-1")
        await asyncio.sleep(0.1)

    # Node should still be active
    assert coordinator.nodes["node-1"].status == NodeStatus.ACTIVE

    await coordinator.stop()


@pytest.mark.asyncio
async def test_submit_task_no_available_nodes() -> None:
    """Test task submission with no available nodes."""
    coordinator = ClusterCoordinator(node_id="coordinator-1")

    task = DistributedTask(task_id="task-1", task_type="test", payload={})
    success = coordinator.submit_task(task)

    assert success is False
    assert task.assigned_node is None


@pytest.mark.asyncio
async def test_load_balancer_no_available_nodes() -> None:
    """Test load balancer with no available nodes."""
    lb = LoadBalancer()

    # All nodes offline
    nodes = [
        NodeInfo(
            "node-1",
            "worker-1",
            "192.168.1.10",
            8000,
            status=NodeStatus.OFFLINE,
        ),
    ]

    selected = lb.select_node(nodes)
    assert selected is None

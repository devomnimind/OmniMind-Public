"""Tests for the agent monitoring system."""

import asyncio

import pytest

from web.backend.monitoring.agent_monitor import AgentMonitor
from web.backend.routes.enums import AgentStatus, AgentType


@pytest.fixture
def agent_monitor():
    """Create a fresh agent monitor instance."""
    return AgentMonitor()


@pytest.mark.asyncio
async def test_agent_registration(agent_monitor):
    """Test agent registration."""
    agent_id = "test-agent-1"
    agent_type = AgentType.CODE

    agent_monitor.register_agent(agent_id, agent_type)

    metrics = agent_monitor.get_agent_metrics(agent_id)
    assert metrics is not None
    assert metrics["agent_id"] == agent_id
    assert metrics["agent_type"] == agent_type.value
    assert metrics["status"] == AgentStatus.IDLE.value


@pytest.mark.asyncio
async def test_agent_status_update(agent_monitor):
    """Test updating agent status."""
    agent_id = "test-agent-2"
    agent_monitor.register_agent(agent_id, AgentType.ORCHESTRATOR)

    agent_monitor.update_agent_status(agent_id, AgentStatus.ACTIVE, "Processing task")

    metrics = agent_monitor.get_agent_metrics(agent_id)
    assert metrics["status"] == AgentStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_task_completion_tracking(agent_monitor):
    """Test task completion recording."""
    agent_id = "test-agent-3"
    agent_monitor.register_agent(agent_id, AgentType.CODE)

    # Record successful task
    agent_monitor.record_task_completion(agent_id, success=True, duration=1.5)

    metrics = agent_monitor.get_agent_metrics(agent_id)
    assert metrics["tasks_completed"] == 1
    assert metrics["tasks_failed"] == 0
    assert metrics["avg_task_duration"] > 0

    # Record failed task
    agent_monitor.record_task_completion(agent_id, success=False, duration=0.5)

    metrics = agent_monitor.get_agent_metrics(agent_id)
    assert metrics["tasks_completed"] == 1
    assert metrics["tasks_failed"] == 1
    assert metrics["error_rate"] == 50.0


@pytest.mark.asyncio
async def test_health_score_calculation(agent_monitor):
    """Test health score calculation."""
    agent_id = "test-agent-4"
    agent_monitor.register_agent(agent_id, AgentType.DEBUG)

    # Initially healthy
    health = agent_monitor._calculate_health_score(agent_id)
    assert health == 100.0

    # Simulate errors
    for _ in range(10):
        agent_monitor.record_task_completion(agent_id, success=False, duration=0.1)

    health = agent_monitor._calculate_health_score(agent_id)
    assert health < 100.0  # Health should decrease due to errors


@pytest.mark.asyncio
async def test_throughput_calculation(agent_monitor):
    """Test throughput calculation."""
    agent_id = "test-agent-5"
    agent_monitor.register_agent(agent_id, AgentType.REVIEWER)

    # Record multiple tasks
    for _ in range(5):
        agent_monitor.record_task_completion(agent_id, success=True, duration=0.1)

    agent_monitor._calculate_throughput(agent_id)

    metrics = agent_monitor.get_agent_metrics(agent_id)
    assert metrics["throughput"] > 0


@pytest.mark.asyncio
async def test_task_history(agent_monitor):
    """Test task history tracking."""
    agent_id = "test-agent-6"
    agent_monitor.register_agent(agent_id, AgentType.ARCHITECT)

    # Record tasks
    for i in range(10):
        agent_monitor.record_task_completion(agent_id, success=(i % 2 == 0), duration=0.1 * i)

    history = agent_monitor.get_task_history(agent_id, limit=5)
    assert len(history) == 5


@pytest.mark.asyncio
async def test_get_all_metrics(agent_monitor):
    """Test getting metrics for all agents."""
    # Register multiple agents
    for i in range(3):
        agent_monitor.register_agent(f"agent-{i}", AgentType.CODE)

    all_metrics = agent_monitor.get_all_metrics()
    assert len(all_metrics) == 3


@pytest.mark.asyncio
async def test_monitoring_lifecycle(agent_monitor):
    """Test monitoring start/stop lifecycle."""
    await agent_monitor.start()
    assert agent_monitor._running is True

    # Let it run for a short time
    await asyncio.sleep(0.5)

    await agent_monitor.stop()
    assert agent_monitor._running is False


@pytest.mark.asyncio
async def test_metrics_not_found(agent_monitor):
    """Test getting metrics for non-existent agent."""
    metrics = agent_monitor.get_agent_metrics("non-existent")
    assert metrics is None


@pytest.mark.asyncio
async def test_error_rate_calculation(agent_monitor):
    """Test error rate calculation."""
    agent_id = "test-agent-7"
    agent_monitor.register_agent(agent_id, AgentType.SECURITY)

    # 7 successful, 3 failed = 30% error rate
    for _ in range(7):
        agent_monitor.record_task_completion(agent_id, success=True, duration=0.1)
    for _ in range(3):
        agent_monitor.record_task_completion(agent_id, success=False, duration=0.1)

    metrics = agent_monitor.get_agent_metrics(agent_id)
    assert metrics["error_rate"] == 30.0

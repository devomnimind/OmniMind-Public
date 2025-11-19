"""Tests for the performance tracker system."""

import asyncio
import time

import pytest

from web.backend.monitoring.performance_tracker import PerformanceTracker


@pytest.fixture
def performance_tracker():
    """Create a fresh performance tracker instance."""
    return PerformanceTracker()


def test_start_task(performance_tracker):
    """Test starting a task."""
    task_id = "task-1"
    performance_tracker.start_task(task_id)

    perf = performance_tracker.get_task_performance(task_id)
    assert perf is not None
    assert perf["task_id"] == task_id
    assert perf["status"] == "running"


def test_complete_task(performance_tracker):
    """Test completing a task."""
    task_id = "task-2"
    performance_tracker.start_task(task_id)

    # Simulate some work
    time.sleep(0.1)

    performance_tracker.complete_task(task_id, status="completed")

    perf = performance_tracker.get_task_performance(task_id)
    assert perf is not None
    assert perf["status"] == "completed"
    assert perf["duration"] > 0


def test_add_checkpoint(performance_tracker):
    """Test adding checkpoints to a task."""
    task_id = "task-3"
    performance_tracker.start_task(task_id)

    performance_tracker.add_checkpoint(task_id, "step1", {"data": "value1"})
    performance_tracker.add_checkpoint(task_id, "step2", {"data": "value2"})

    perf = performance_tracker.get_task_performance(task_id)
    assert len(perf["checkpoints"]) == 2
    assert perf["checkpoints"][0]["name"] == "step1"
    assert perf["checkpoints"][1]["name"] == "step2"


def test_record_operations(performance_tracker):
    """Test recording operations within a task."""
    task_id = "task-4"
    performance_tracker.start_task(task_id)

    # Record successful operations
    for _ in range(5):
        performance_tracker.record_operation(task_id, success=True)

    # Record failed operations
    for _ in range(2):
        performance_tracker.record_operation(task_id, success=False)

    perf = performance_tracker.get_task_performance(task_id)
    assert perf["operations_count"] == 7
    assert perf["errors_count"] == 2


def test_get_active_tasks(performance_tracker):
    """Test getting active tasks."""
    # Start multiple tasks
    for i in range(3):
        performance_tracker.start_task(f"task-{i}")

    active = performance_tracker.get_active_tasks()
    assert len(active) == 3


def test_get_completed_tasks(performance_tracker):
    """Test getting completed tasks."""
    # Start and complete tasks
    for i in range(5):
        task_id = f"task-{i}"
        performance_tracker.start_task(task_id)
        performance_tracker.complete_task(task_id)

    completed = performance_tracker.get_completed_tasks(limit=3)
    assert len(completed) == 3


def test_performance_summary(performance_tracker):
    """Test performance summary generation."""
    # Complete some tasks with different durations
    for i in range(3):
        task_id = f"task-{i}"
        performance_tracker.start_task(task_id)
        time.sleep(0.05 * (i + 1))
        performance_tracker.complete_task(task_id)

    summary = performance_tracker.get_performance_summary()
    assert summary["completed_tasks"] == 3
    assert summary["avg_duration"] > 0
    assert summary["success_rate"] == 100.0


def test_task_not_found(performance_tracker):
    """Test getting performance for non-existent task."""
    perf = performance_tracker.get_task_performance("non-existent")
    assert perf is None


def test_complete_unknown_task(performance_tracker):
    """Test completing a task that was never started."""
    # Should log a warning but not crash
    performance_tracker.complete_task("unknown-task")

    perf = performance_tracker.get_task_performance("unknown-task")
    assert perf is None


def test_checkpoint_unknown_task(performance_tracker):
    """Test adding checkpoint to unknown task."""
    # Should log a warning but not crash
    performance_tracker.add_checkpoint("unknown-task", "checkpoint")


def test_completed_tasks_limit(performance_tracker):
    """Test that completed tasks are limited."""
    performance_tracker._max_completed = 10

    # Complete more tasks than the limit
    for i in range(20):
        task_id = f"task-{i}"
        performance_tracker.start_task(task_id)
        performance_tracker.complete_task(task_id)

    # Should only keep the last 10
    assert len(performance_tracker._completed_tasks) == 10


def test_elapsed_time_calculation(performance_tracker):
    """Test elapsed time calculation for active tasks."""
    task_id = "task-elapsed"
    performance_tracker.start_task(task_id)

    time.sleep(0.1)

    perf = performance_tracker.get_task_performance(task_id)
    assert perf["elapsed"] >= 0.1


def test_checkpoint_elapsed_time(performance_tracker):
    """Test that checkpoints record elapsed time."""
    task_id = "task-checkpoint-time"
    performance_tracker.start_task(task_id)

    time.sleep(0.05)
    performance_tracker.add_checkpoint(task_id, "checkpoint1")

    time.sleep(0.05)
    performance_tracker.add_checkpoint(task_id, "checkpoint2")

    perf = performance_tracker.get_task_performance(task_id)
    cp1 = perf["checkpoints"][0]
    cp2 = perf["checkpoints"][1]

    assert cp1["elapsed"] >= 0.05
    assert cp2["elapsed"] >= 0.1
    assert cp2["elapsed"] > cp1["elapsed"]


@pytest.mark.asyncio
async def test_tracker_lifecycle(performance_tracker):
    """Test performance tracker lifecycle."""
    await performance_tracker.start()
    assert performance_tracker._running is True

    # Let it run for a short time
    await asyncio.sleep(0.5)

    await performance_tracker.stop()
    assert performance_tracker._running is False


def test_mixed_success_failure_summary(performance_tracker):
    """Test summary with mixed success/failure."""
    # 6 successful, 2 failed
    for i in range(8):
        task_id = f"task-{i}"
        performance_tracker.start_task(task_id)
        status = "completed" if i < 6 else "failed"
        performance_tracker.complete_task(task_id, status=status)

    summary = performance_tracker.get_performance_summary()
    assert summary["completed_tasks"] == 8
    assert summary["success_rate"] == 75.0

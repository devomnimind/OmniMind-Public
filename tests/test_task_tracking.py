"""Tests for enhanced task progress tracking."""

import pytest

# We'll create a simple test app for testing
from fastapi import FastAPI
from fastapi.testclient import TestClient

from web.backend.routes import tasks


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    app = FastAPI()
    app.include_router(tasks.router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_task(client):
    """Create a sample task for testing."""
    response = client.post(
        "/api/tasks/",
        json={
            "description": "Test task",
            "priority": "medium",
            "max_iterations": 3,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_create_task_with_analytics(client):
    """Test that creating a task initializes analytics."""
    response = client.post(
        "/api/tasks/",
        json={
            "description": "Analytics test task",
            "priority": "high",
        },
    )

    assert response.status_code == 200
    data = response.json()
    task_id = data["task_id"]

    # Check that analytics were initialized
    assert task_id in tasks._task_analytics
    assert task_id in tasks._task_execution_history


def test_update_task_progress_tracking(client, sample_task):
    """Test that updating progress is tracked."""
    task_id = sample_task["task_id"]

    # Update to running
    response = client.post(
        f"/api/tasks/{task_id}/progress",
        json={
            "task_id": task_id,
            "progress": 50.0,
            "status": "running",
            "message": "Processing",
        },
    )

    assert response.status_code == 200

    # Check history was recorded
    history = tasks._task_execution_history.get(task_id, [])
    assert len(history) > 0
    assert any(e["event"] == "task_started" for e in history)


def test_task_checkpoint(client, sample_task):
    """Test adding checkpoints to a task."""
    task_id = sample_task["task_id"]

    # Start the task first
    client.post(
        f"/api/tasks/{task_id}/progress",
        json={
            "task_id": task_id,
            "progress": 10.0,
            "status": "running",
        },
    )

    # Add checkpoint
    response = client.post(
        f"/api/tasks/{task_id}/checkpoint",
        params={"name": "step1", "data": {"info": "test"}},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "checkpoint_added"
    assert data["checkpoint"]["name"] == "step1"

    # Verify checkpoint in analytics
    analytics = tasks._task_analytics.get(task_id, {})
    assert len(analytics["checkpoints"]) > 0


def test_record_task_operation(client, sample_task):
    """Test recording operations within a task."""
    task_id = sample_task["task_id"]

    # Record successful operation
    response = client.post(
        f"/api/tasks/{task_id}/operation",
        params={"success": True},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    # Record failed operation
    response = client.post(
        f"/api/tasks/{task_id}/operation",
        params={"success": False, "error": "Test error"},
    )

    assert response.status_code == 200

    # Check analytics
    analytics = tasks._task_analytics.get(task_id, {})
    assert analytics["operations_count"] == 2
    assert analytics["errors_count"] == 1


def test_get_task_analytics(client, sample_task):
    """Test getting task analytics."""
    task_id = sample_task["task_id"]

    # Record some operations
    for _ in range(5):
        client.post(f"/api/tasks/{task_id}/operation", params={"success": True})
    client.post(f"/api/tasks/{task_id}/operation", params={"success": False})

    # Get analytics
    response = client.get(f"/api/tasks/{task_id}/analytics")

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id
    assert data["operations_count"] == 6
    assert data["errors_count"] == 1
    assert data["success_rate"] > 0


def test_get_task_history_enhanced(client, sample_task):
    """Test getting enhanced task history."""
    task_id = sample_task["task_id"]

    # Update task progress multiple times
    client.post(
        f"/api/tasks/{task_id}/progress",
        json={"task_id": task_id, "progress": 25.0, "status": "running"},
    )
    client.post(
        f"/api/tasks/{task_id}/progress",
        json={"task_id": task_id, "progress": 75.0, "status": "running"},
    )
    client.post(
        f"/api/tasks/{task_id}/progress",
        json={"task_id": task_id, "progress": 100.0, "status": "completed"},
    )

    # Get history
    response = client.get(f"/api/tasks/{task_id}/history")

    assert response.status_code == 200
    data = response.json()
    assert "execution_history" in data
    assert len(data["execution_history"]) > 0


def test_tasks_analytics_summary(client):
    """Test getting overall analytics summary."""
    # Create multiple tasks
    for i in range(5):
        client.post(
            "/api/tasks/",
            json={"description": f"Task {i}", "priority": "medium"},
        )

    response = client.get("/api/tasks/analytics/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] >= 5
    assert "by_status" in data
    assert "success_rate" in data
    assert "avg_duration" in data


def test_task_completion_tracking(client, sample_task):
    """Test that task completion is properly tracked."""
    task_id = sample_task["task_id"]

    # Start task
    client.post(
        f"/api/tasks/{task_id}/progress",
        json={"task_id": task_id, "progress": 0.0, "status": "running"},
    )

    # Complete task
    client.post(
        f"/api/tasks/{task_id}/progress",
        json={"task_id": task_id, "progress": 100.0, "status": "completed"},
    )

    # Check history for completion event
    history = tasks._task_execution_history.get(task_id, [])
    completion_events = [e for e in history if e["event"] == "task_completed"]
    assert len(completion_events) > 0
    assert "duration" in completion_events[0]


def test_multiple_checkpoints(client, sample_task):
    """Test adding multiple checkpoints to a task."""
    task_id = sample_task["task_id"]

    # Start task
    client.post(
        f"/api/tasks/{task_id}/progress",
        json={"task_id": task_id, "progress": 0.0, "status": "running"},
    )

    # Add multiple checkpoints
    checkpoints = ["init", "processing", "validation", "finalize"]
    for checkpoint in checkpoints:
        response = client.post(
            f"/api/tasks/{task_id}/checkpoint",
            params={"name": checkpoint},
        )
        assert response.status_code == 200

    # Verify all checkpoints
    analytics = tasks._task_analytics.get(task_id, {})
    assert len(analytics["checkpoints"]) == len(checkpoints)


def test_task_error_tracking(client, sample_task):
    """Test error tracking in task operations."""
    task_id = sample_task["task_id"]

    # Record multiple errors
    errors = ["Error 1", "Error 2", "Error 3"]
    for error in errors:
        client.post(
            f"/api/tasks/{task_id}/operation",
            params={"success": False, "error": error},
        )

    # Check error count
    analytics = tasks._task_analytics.get(task_id, {})
    assert analytics["errors_count"] == len(errors)

    # Check history contains error events
    history = tasks._task_execution_history.get(task_id, [])
    error_events = [e for e in history if e["event"] == "operation" and not e["success"]]
    assert len(error_events) == len(errors)

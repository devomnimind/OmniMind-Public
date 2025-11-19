"""API routes for task management and progress tracking."""

from __future__ import annotations

import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query  # noqa: F401
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Import performance tracking
try:
    from web.backend.monitoring import performance_tracker

    TRACKING_ENABLED = True
except ImportError:
    TRACKING_ENABLED = False
    logger.warning("Performance tracking not available")


class TaskStatus(str, Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreate(BaseModel):
    """Request model for creating a task."""

    description: str = Field(..., description="Task description")
    priority: TaskPriority = Field(
        TaskPriority.MEDIUM, description="Task priority level"
    )
    max_iterations: int = Field(3, ge=1, le=10, description="Maximum iterations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Task metadata")


class TaskResponse(BaseModel):
    """Response model for task information."""

    task_id: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    progress: float = Field(ge=0.0, le=100.0, description="Progress percentage")
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskProgressUpdate(BaseModel):
    """Progress update for a task."""

    task_id: str
    progress: float = Field(ge=0.0, le=100.0)
    status: TaskStatus
    message: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


# In-memory task storage (would be replaced with database in production)
_tasks: Dict[str, Dict[str, Any]] = {}
_task_execution_history: Dict[str, List[Dict[str, Any]]] = {}
_task_analytics: Dict[str, Dict[str, Any]] = {}


def _get_task(task_id: str) -> Dict[str, Any]:
    """Get task by ID or raise 404."""
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return _tasks[task_id]


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate) -> TaskResponse:
    """Create a new task."""
    task_id = str(uuid.uuid4())
    task_data = {
        "task_id": task_id,
        "description": task.description,
        "status": TaskStatus.PENDING,
        "priority": task.priority,
        "progress": 0.0,
        "created_at": time.time(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
        "metadata": task.metadata,
        "max_iterations": task.max_iterations,
    }
    _tasks[task_id] = task_data

    # Initialize execution history and analytics
    _task_execution_history[task_id] = []
    _task_analytics[task_id] = {
        "checkpoints": [],
        "operations_count": 0,
        "errors_count": 0,
        "retries_count": 0,
    }

    logger.info(f"Created task {task_id}: {task.description}")

    # Broadcast task creation via WebSocket
    from web.backend.websocket_manager import MessageType, ws_manager

    await ws_manager.broadcast(
        MessageType.TASK_UPDATE,
        {"event": "task_created", "task": task_data},
        channel="tasks",
    )

    return TaskResponse(**task_data)


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
) -> List[TaskResponse]:
    """List all tasks with optional filtering."""
    tasks = list(_tasks.values())

    # Apply filters
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if priority:
        tasks = [t for t in tasks if t["priority"] == priority]

    # Sort by created_at descending
    tasks.sort(key=lambda t: t["created_at"], reverse=True)

    # Apply limit
    tasks = tasks[:limit]

    return [TaskResponse(**t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    """Get task details by ID."""
    task = _get_task(task_id)
    return TaskResponse(**task)


@router.get("/{task_id}/progress", response_model=TaskProgressUpdate)
async def get_task_progress(task_id: str) -> TaskProgressUpdate:
    """Get current progress for a task."""
    task = _get_task(task_id)
    return TaskProgressUpdate(
        task_id=task_id,
        progress=task["progress"],
        status=task["status"],
        message=None,
        timestamp=time.time(),
    )


@router.post("/{task_id}/progress")
async def update_task_progress(
    task_id: str, progress: TaskProgressUpdate
) -> Dict[str, Any]:
    """Update task progress (internal use)."""
    task = _get_task(task_id)

    old_status = task["status"]
    task["progress"] = progress.progress
    task["status"] = progress.status

    # Track status changes
    if progress.status == TaskStatus.RUNNING and not task["started_at"]:
        task["started_at"] = time.time()
        # Start performance tracking
        if TRACKING_ENABLED:
            performance_tracker.start_task(task_id)

        # Record execution history event
        _task_execution_history[task_id].append(
            {
                "timestamp": time.time(),
                "event": "task_started",
                "status": progress.status.value,
                "progress": progress.progress,
            }
        )

    elif progress.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        task["completed_at"] = time.time()
        # Complete performance tracking
        if TRACKING_ENABLED:
            performance_tracker.complete_task(task_id, status=progress.status.value)

        # Record execution history event
        _task_execution_history[task_id].append(
            {
                "timestamp": time.time(),
                "event": "task_completed",
                "status": progress.status.value,
                "progress": progress.progress,
                "duration": (
                    task["completed_at"] - task["started_at"]
                    if task["started_at"]
                    else 0
                ),
            }
        )

    # Record progress update in history
    if old_status != progress.status or progress.message:
        _task_execution_history[task_id].append(
            {
                "timestamp": time.time(),
                "event": "progress_update",
                "status": progress.status.value,
                "progress": progress.progress,
                "message": progress.message,
            }
        )

    logger.info(f"Task {task_id} progress: {progress.progress}% ({progress.status})")

    # Broadcast progress update via WebSocket
    from web.backend.websocket_manager import MessageType, ws_manager

    await ws_manager.broadcast(
        MessageType.TASK_UPDATE,
        {
            "event": "progress_updated",
            "task_id": task_id,
            "progress": progress.progress,
            "status": progress.status.value,
            "message": progress.message,
        },
        channel="tasks",
    )

    return {"status": "updated", "task": task}


@router.delete("/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """Cancel a running task."""
    task = _get_task(task_id)

    if task["status"] in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        raise HTTPException(
            status_code=400, detail=f"Cannot cancel {task['status']} task"
        )

    task["status"] = TaskStatus.CANCELLED
    task["completed_at"] = time.time()

    logger.info(f"Cancelled task {task_id}")

    # Broadcast cancellation via WebSocket
    from web.backend.websocket_manager import MessageType, ws_manager

    await ws_manager.broadcast(
        MessageType.TASK_UPDATE,
        {"event": "task_cancelled", "task_id": task_id},
        channel="tasks",
    )

    return {"status": "cancelled", "task_id": task_id}


@router.get("/{task_id}/history")
async def get_task_history(task_id: str) -> Dict[str, Any]:
    """Get execution history for a task."""
    task = _get_task(task_id)

    # Calculate execution time if applicable
    execution_time = None
    if task["started_at"] and task["completed_at"]:
        execution_time = task["completed_at"] - task["started_at"]

    # Get detailed execution history
    history = _task_execution_history.get(task_id, [])

    # Get performance tracking data if available
    perf_data = None
    if TRACKING_ENABLED:
        perf_data = performance_tracker.get_task_performance(task_id)

    return {
        "task_id": task_id,
        "description": task["description"],
        "status": task["status"],
        "created_at": task["created_at"],
        "started_at": task["started_at"],
        "completed_at": task["completed_at"],
        "execution_time": execution_time,
        "result": task["result"],
        "error": task["error"],
        "metadata": task["metadata"],
        "execution_history": history,
        "performance_data": perf_data,
    }


@router.get("/{task_id}/analytics")
async def get_task_analytics(task_id: str) -> Dict[str, Any]:
    """Get analytics data for a task."""
    task = _get_task(task_id)
    analytics = _task_analytics.get(task_id, {})

    # Calculate metrics
    total_events = len(_task_execution_history.get(task_id, []))
    duration = None
    if task["started_at"] and task["completed_at"]:
        duration = task["completed_at"] - task["started_at"]

    return {
        "task_id": task_id,
        "status": task["status"],
        "priority": task["priority"],
        "duration": duration,
        "total_events": total_events,
        "checkpoints": analytics.get("checkpoints", []),
        "operations_count": analytics.get("operations_count", 0),
        "errors_count": analytics.get("errors_count", 0),
        "retries_count": analytics.get("retries_count", 0),
        "success_rate": (
            (analytics.get("operations_count", 0) - analytics.get("errors_count", 0))
            / analytics.get("operations_count", 1)
            * 100
            if analytics.get("operations_count", 0) > 0
            else 0.0
        ),
    }


@router.post("/{task_id}/checkpoint")
async def add_task_checkpoint(
    task_id: str, name: str, data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Add a checkpoint to track task progress."""
    task = _get_task(task_id)

    checkpoint = {
        "name": name,
        "timestamp": time.time(),
        "elapsed": (time.time() - task["started_at"] if task["started_at"] else 0.0),
        "data": data or {},
    }

    # Add to analytics
    if task_id in _task_analytics:
        _task_analytics[task_id]["checkpoints"].append(checkpoint)

    # Add to performance tracker if available
    if TRACKING_ENABLED:
        performance_tracker.add_checkpoint(task_id, name, data)

    # Record in execution history
    if task_id in _task_execution_history:
        _task_execution_history[task_id].append(
            {
                "timestamp": checkpoint["timestamp"],
                "event": "checkpoint",
                "name": name,
                "elapsed": checkpoint["elapsed"],
            }
        )

    logger.debug(f"Added checkpoint '{name}' to task {task_id}")

    return {"status": "checkpoint_added", "checkpoint": checkpoint}


@router.post("/{task_id}/operation")
async def record_task_operation(
    task_id: str, success: bool = True, error: Optional[str] = None
) -> Dict[str, Any]:
    """Record an operation within a task."""
    _get_task(task_id)  # Validate task exists

    # Update analytics
    if task_id in _task_analytics:
        _task_analytics[task_id]["operations_count"] += 1
        if not success:
            _task_analytics[task_id]["errors_count"] += 1

    # Record in performance tracker if available
    if TRACKING_ENABLED:
        performance_tracker.record_operation(task_id, success)

    # Record in execution history
    if task_id in _task_execution_history:
        _task_execution_history[task_id].append(
            {
                "timestamp": time.time(),
                "event": "operation",
                "success": success,
                "error": error,
            }
        )

    return {
        "status": "operation_recorded",
        "task_id": task_id,
        "success": success,
    }


@router.get("/analytics/summary")
async def get_tasks_analytics_summary() -> Dict[str, Any]:
    """Get overall analytics summary for all tasks."""
    total_tasks = len(_tasks)
    completed = sum(1 for t in _tasks.values() if t["status"] == TaskStatus.COMPLETED)
    failed = sum(1 for t in _tasks.values() if t["status"] == TaskStatus.FAILED)
    running = sum(1 for t in _tasks.values() if t["status"] == TaskStatus.RUNNING)
    pending = sum(1 for t in _tasks.values() if t["status"] == TaskStatus.PENDING)

    # Calculate average duration for completed tasks
    completed_tasks = [
        t for t in _tasks.values() if t["status"] == TaskStatus.COMPLETED
    ]
    avg_duration = 0.0
    if completed_tasks:
        durations = [
            t["completed_at"] - t["started_at"]
            for t in completed_tasks
            if t["started_at"] and t["completed_at"]
        ]
        if durations:
            avg_duration = sum(durations) / len(durations)

    # Get performance summary if available
    perf_summary = None
    if TRACKING_ENABLED:
        perf_summary = performance_tracker.get_performance_summary()

    return {
        "total_tasks": total_tasks,
        "by_status": {
            "completed": completed,
            "failed": failed,
            "running": running,
            "pending": pending,
        },
        "success_rate": (completed / total_tasks * 100) if total_tasks > 0 else 0.0,
        "avg_duration": round(avg_duration, 3),
        "performance_summary": perf_summary,
        "timestamp": time.time(),
    }

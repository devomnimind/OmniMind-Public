"""API routes for task management and progress tracking."""

from __future__ import annotations

import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


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

    task["progress"] = progress.progress
    task["status"] = progress.status

    if progress.status == TaskStatus.RUNNING and not task["started_at"]:
        task["started_at"] = time.time()
    elif progress.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
        task["completed_at"] = time.time()

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
    }

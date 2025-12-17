"""Performance tracking system for tasks and operations."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TaskPerformance:
    """Performance metrics for a task."""

    task_id: str
    started_at: float
    completed_at: Optional[float] = None
    duration: Optional[float] = None
    status: str = "running"
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)
    operations_count: int = 0
    errors_count: int = 0


class PerformanceTracker:
    """Track performance of tasks and operations."""

    def __init__(self) -> None:
        self._task_performance: Dict[str, TaskPerformance] = {}
        self._completed_tasks: List[TaskPerformance] = []
        self._max_completed = 500
        self._tracker_task: Optional[asyncio.Task[None]] = None
        self._running = False

    async def start(self) -> None:
        """Start performance tracking."""
        if self._running:
            return

        self._running = True
        self._tracker_task = asyncio.create_task(self._tracker_loop())
        logger.info("Performance tracker started")

    async def stop(self) -> None:
        """Stop performance tracking."""
        self._running = False
        if self._tracker_task:
            self._tracker_task.cancel()
            try:
                await self._tracker_task
            except asyncio.CancelledError:
                pass
        logger.info("Performance tracker stopped")

    def start_task(self, task_id: str) -> None:
        """Start tracking a task."""
        if task_id not in self._task_performance:
            self._task_performance[task_id] = TaskPerformance(
                task_id=task_id,
                started_at=time.time(),
            )
            logger.debug(f"Started tracking task: {task_id}")

    def complete_task(self, task_id: str, status: str = "completed") -> None:
        """Mark a task as completed."""
        if task_id not in self._task_performance:
            logger.warning(f"Cannot complete unknown task: {task_id}")
            return

        perf = self._task_performance[task_id]
        perf.completed_at = time.time()
        perf.duration = perf.completed_at - perf.started_at
        perf.status = status

        # Move to completed tasks
        self._completed_tasks.append(perf)
        del self._task_performance[task_id]

        # Trim completed tasks if needed
        if len(self._completed_tasks) > self._max_completed:
            self._completed_tasks = self._completed_tasks[-self._max_completed :]

        logger.debug(f"Completed task {task_id} in {perf.duration:.2f}s with status {status}")

    def add_checkpoint(
        self, task_id: str, name: str, data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a checkpoint to a task."""
        if task_id not in self._task_performance:
            logger.warning(f"Cannot add checkpoint to unknown task: {task_id}")
            return

        perf = self._task_performance[task_id]
        checkpoint = {
            "name": name,
            "timestamp": time.time(),
            "elapsed": time.time() - perf.started_at,
            "data": data or {},
        }
        perf.checkpoints.append(checkpoint)

    def record_operation(self, task_id: str, success: bool = True) -> None:
        """Record an operation within a task."""
        if task_id not in self._task_performance:
            return

        perf = self._task_performance[task_id]
        perf.operations_count += 1
        if not success:
            perf.errors_count += 1

    def get_task_performance(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get performance data for a task."""
        # Check active tasks
        if task_id in self._task_performance:
            perf = self._task_performance[task_id]
            elapsed = time.time() - perf.started_at
            return {
                "task_id": task_id,
                "status": perf.status,
                "started_at": perf.started_at,
                "elapsed": round(elapsed, 3),
                "checkpoints": perf.checkpoints,
                "operations_count": perf.operations_count,
                "errors_count": perf.errors_count,
            }

        # Check completed tasks
        for perf in reversed(self._completed_tasks):
            if perf.task_id == task_id:
                return {
                    "task_id": task_id,
                    "status": perf.status,
                    "started_at": perf.started_at,
                    "completed_at": perf.completed_at,
                    "duration": round(perf.duration or 0, 3),
                    "checkpoints": perf.checkpoints,
                    "operations_count": perf.operations_count,
                    "errors_count": perf.errors_count,
                }

        return None

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all currently active tasks."""
        active = []
        now = time.time()
        for task_id, perf in self._task_performance.items():
            active.append(
                {
                    "task_id": task_id,
                    "status": perf.status,
                    "elapsed": round(now - perf.started_at, 3),
                    "operations_count": perf.operations_count,
                    "errors_count": perf.errors_count,
                }
            )
        return active

    def get_completed_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recently completed tasks."""
        completed = []
        for perf in reversed(self._completed_tasks[-limit:]):
            completed.append(
                {
                    "task_id": perf.task_id,
                    "status": perf.status,
                    "duration": round(perf.duration or 0, 3),
                    "completed_at": perf.completed_at,
                    "operations_count": perf.operations_count,
                    "errors_count": perf.errors_count,
                }
            )
        return completed

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary."""
        # Calculate statistics for completed tasks
        if not self._completed_tasks:
            return {
                "active_tasks": len(self._task_performance),
                "completed_tasks": 0,
                "avg_duration": 0.0,
                "success_rate": 0.0,
            }

        durations = [t.duration for t in self._completed_tasks if t.duration]
        successful = sum(1 for t in self._completed_tasks if t.status == "completed")

        return {
            "active_tasks": len(self._task_performance),
            "completed_tasks": len(self._completed_tasks),
            "avg_duration": (round(sum(durations) / len(durations), 3) if durations else 0.0),
            "min_duration": round(min(durations), 3) if durations else 0.0,
            "max_duration": round(max(durations), 3) if durations else 0.0,
            "success_rate": round(successful / len(self._completed_tasks) * 100, 2),
        }

    async def _tracker_loop(self) -> None:
        """Background loop for broadcasting performance updates."""
        while self._running:
            try:
                # Broadcast performance summary
                await self._broadcast_performance()

            except Exception as exc:
                logger.exception(f"Error in tracker loop: {exc}")

            await asyncio.sleep(15)  # Update every 15 seconds

    async def _broadcast_performance(self) -> None:
        """Broadcast performance metrics via WebSocket."""
        from web.backend.websocket_manager import MessageType, ws_manager

        summary = self.get_performance_summary()
        active = self.get_active_tasks()

        await ws_manager.broadcast(
            MessageType.METRICS,
            {
                "type": "performance_metrics",
                "summary": summary,
                "active_tasks": active,
            },
            channel="metrics",
        )


# Global performance tracker instance
performance_tracker = PerformanceTracker()

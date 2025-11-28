from __future__ import annotations

import asyncio
import os
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import psutil
import structlog


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

"""
OmniMind Daemon - 24/7 Autonomous Background Service

This module implements the core daemon functionality that runs continuously,
working proactively even while the user sleeps. It's NOT a chatbot - it's
an autonomous agent that monitors, analyzes, and executes tasks.

Key responsibilities:
- Monitor system state and codebase changes
- Execute background tasks during idle periods
- Integrate with Supabase and Qdrant for persistence
- Coordinate with orchestrator for complex workflows
- Provide observability through the dashboard
"""


# Configure structured logging
structlog.configure(  # type: ignore[attr-defined]
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),  # type: ignore[attr-defined]
        structlog.processors.add_log_level,  # type: ignore[attr-defined]
        structlog.processors.JSONRenderer(),  # type: ignore[attr-defined]
    ],
    logger_factory=structlog.PrintLoggerFactory(),  # type: ignore[attr-defined]
)

logger = structlog.get_logger(__name__)


class DaemonState(Enum):
    """Daemon operational states"""

    INITIALIZING = "initializing"
    IDLE = "idle"
    WORKING = "working"
    SLEEPING = "sleeping"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"


class TaskPriority(Enum):
    """Task priority levels for the daemon"""

    CRITICAL = 0  # Execute immediately
    HIGH = 1  # Execute when system is idle
    MEDIUM = 2  # Execute during low-activity periods
    LOW = 3  # Execute during sleep hours


@dataclass
class DaemonTask:
    """Represents a task for the daemon to execute"""

    task_id: str
    name: str
    description: str
    priority: TaskPriority
    execute_fn: Callable[[], Any]
    schedule_time: Optional[datetime] = None
    repeat_interval: Optional[timedelta] = None
    max_duration: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    created_at: datetime = field(default_factory=datetime.now)
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0


@dataclass
class SystemMetrics:
    """System resource metrics"""

    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_active: bool
    user_active: bool
    timestamp: datetime = field(default_factory=datetime.now)

    def is_idle(self) -> bool:
        """Determine if system is idle enough for background work"""
        return self.cpu_percent < 20.0 and self.memory_percent < 80.0 and not self.user_active

    def is_sleep_time(self) -> bool:
        """Determine if it's sleep time (user likely away)"""
        hour = self.timestamp.hour
        # Consider 00:00-06:00 as sleep time
        return 0 <= hour < 6


class OmniMindDaemon:
    """
    Main daemon class for OmniMind.

    This daemon runs 24/7, monitoring the system and executing tasks proactively.
    It integrates with cloud services (Supabase, Qdrant, Hugging Face) when needed
    but prioritizes local execution.
    """

    def __init__(
        self,
        workspace_path: Path,
        check_interval: int = 30,
        enable_cloud: bool = True,
    ):
        self.workspace_path = workspace_path
        self.check_interval = check_interval
        self.enable_cloud = enable_cloud

        self.state = DaemonState.INITIALIZING
        self.tasks: List[DaemonTask] = []
        self.task_queue: List[DaemonTask] = []
        self.running = False
        self.metrics_history: List[SystemMetrics] = []

        # Cloud integrations (initialized on first use)
        self._supabase_client = None
        self._qdrant_client = None
        self._hf_token = os.getenv("HUGGINGFACE_TOKEN")

        logger.info(
            "daemon.initialized",
            workspace=str(workspace_path),
            cloud_enabled=enable_cloud,
        )

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        # Simple heuristic for user activity
        user_active = cpu > 50.0

        metrics = SystemMetrics(
            cpu_percent=cpu,
            memory_percent=memory,
            disk_usage_percent=disk,
            network_active=False,
            user_active=user_active,
        )

        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)

        return metrics

    def register_task(self, task: DaemonTask) -> None:
        """Register a new task for the daemon"""
        self.tasks.append(task)
        logger.info(
            "task.registered",
            task_id=task.task_id,
            name=task.name,
            priority=task.priority.name,
        )

    def _get_next_task(self, metrics: SystemMetrics) -> Optional[DaemonTask]:
        """Get the next task to execute based on system state and priorities"""
        eligible_tasks = []

        for task in self.tasks:
            if task.last_execution and task.repeat_interval:
                next_run = task.last_execution + task.repeat_interval
                if datetime.now() < next_run:
                    continue

            if task.schedule_time and datetime.now() < task.schedule_time:
                continue

            if task.priority == TaskPriority.CRITICAL:
                eligible_tasks.append(task)
            elif task.priority == TaskPriority.HIGH and metrics.is_idle():
                eligible_tasks.append(task)
            elif task.priority == TaskPriority.MEDIUM and metrics.is_idle():
                eligible_tasks.append(task)
            elif task.priority == TaskPriority.LOW and metrics.is_sleep_time():
                eligible_tasks.append(task)

        if not eligible_tasks:
            return None

        return min(eligible_tasks, key=lambda t: t.priority.value)

    async def _execute_task(self, task: DaemonTask) -> bool:
        """Execute a single task with timeout and error handling"""
        logger.info(
            "task.executing",
            task_id=task.task_id,
            name=task.name,
        )

        start_time = time.time()
        success = False

        try:
            if asyncio.iscoroutinefunction(task.execute_fn):
                result = await asyncio.wait_for(
                    task.execute_fn(),
                    timeout=task.max_duration.total_seconds(),
                )
            else:
                result = task.execute_fn()

            success = True
            task.success_count += 1

            logger.info(
                "task.completed",
                task_id=task.task_id,
                duration=time.time() - start_time,
                result=result,
            )

        except asyncio.TimeoutError:
            logger.error(
                "task.timeout",
                task_id=task.task_id,
                max_duration=task.max_duration.total_seconds(),
            )
            task.failure_count += 1

        except Exception as exc:
            logger.error(
                "task.failed",
                task_id=task.task_id,
                error=str(exc),
                exc_info=True,
            )
            task.failure_count += 1

        finally:
            task.execution_count += 1
            task.last_execution = datetime.now()

        return success

    async def _daemon_loop(self) -> None:
        """Main daemon loop - runs continuously"""
        logger.info("daemon.starting")
        self.state = DaemonState.IDLE

        while self.running:
            try:
                metrics = self._collect_system_metrics()

                if metrics.is_sleep_time():
                    self.state = DaemonState.SLEEPING
                elif metrics.is_idle():
                    self.state = DaemonState.IDLE
                else:
                    await asyncio.sleep(self.check_interval)
                    continue

                next_task = self._get_next_task(metrics)

                if next_task:
                    self.state = DaemonState.WORKING
                    await self._execute_task(next_task)
                    self.state = DaemonState.IDLE

                await asyncio.sleep(self.check_interval)

            except Exception as exc:
                logger.error("daemon.error", error=str(exc), exc_info=True)
                self.state = DaemonState.ERROR
                await asyncio.sleep(self.check_interval)

        logger.info("daemon.stopped")

    def start(self) -> None:
        """Start the daemon"""
        if self.running:
            logger.warning("daemon.already_running")
            return

        self.running = True

        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        try:
            asyncio.run(self._daemon_loop())
        except KeyboardInterrupt:
            logger.info("daemon.interrupted")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the daemon gracefully"""
        logger.info("daemon.stopping")
        self.state = DaemonState.SHUTTING_DOWN
        self.running = False

    def _handle_shutdown(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals"""
        logger.info("daemon.shutdown_signal", signal=signum)
        self.stop()

    def get_status(self) -> Dict[str, Any]:
        """Get current daemon status"""
        current_metrics = self._collect_system_metrics() if self.running else None

        return {
            "state": self.state.value,
            "running": self.running,
            "uptime_seconds": self._calculate_uptime(),
            "tasks_registered": len(self.tasks),
            "tasks_pending": self._count_pending_tasks(),
            "system_metrics": self._build_system_metrics(current_metrics),
            "task_count": len(self.tasks),
            "completed_tasks": self._count_completed_tasks(),
            "failed_tasks": self._count_failed_tasks(),
            "cloud_connected": self.enable_cloud,
            "cloud_enabled": self.enable_cloud,
            "workspace": str(self.workspace_path),
        }

    def _calculate_uptime(self) -> int:
        """Calculate daemon uptime in seconds."""
        if not self.metrics_history:
            return 0
        return len(self.metrics_history) * self.check_interval

    def _count_pending_tasks(self) -> int:
        """Count tasks that are pending execution."""
        return sum(
            1
            for t in self.tasks
            if not t.last_execution
            or (t.repeat_interval and datetime.now() >= t.last_execution + t.repeat_interval)
        )

    def _count_completed_tasks(self) -> int:
        """Count tasks that have been completed successfully."""
        return sum(1 for t in self.tasks if t.last_execution and t.success_count > 0)

    def _count_failed_tasks(self) -> int:
        """Count tasks that have failed."""
        return sum(1 for t in self.tasks if t.failure_count > 0)

    def _build_system_metrics(self, current_metrics: Optional[SystemMetrics]) -> Dict[str, Any]:
        """Build system metrics dictionary for frontend."""
        if not current_metrics:
            return self._get_default_system_metrics()

        return {
            "cpu_percent": current_metrics.cpu_percent,
            "memory_percent": current_metrics.memory_percent,
            "disk_percent": current_metrics.disk_usage_percent,
            "is_user_active": current_metrics.user_active,
            "idle_seconds": self._calculate_idle_seconds(),
            "is_sleep_hours": self._is_sleep_hours(),
        }

    def _get_default_system_metrics(self) -> Dict[str, Any]:
        """Get default system metrics when no current metrics available."""
        return {
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "is_user_active": False,
            "idle_seconds": 0,
            "is_sleep_hours": False,
        }

    def _calculate_idle_seconds(self) -> int:
        """Calculate seconds system has been idle."""
        if len(self.metrics_history) <= 1:
            return 0

        # Count recent metrics with low CPU usage
        recent_low_cpu = sum(1 for m in self.metrics_history[-10:] if m.cpu_percent < 20)
        return recent_low_cpu * 5  # Approximate 5 seconds per metric

    def _is_sleep_hours(self) -> bool:
        """Check if current time is during sleep hours (00:00-06:00)."""
        current_hour = datetime.now().hour
        return 0 <= current_hour < 6


def create_default_tasks() -> List[DaemonTask]:
    """Create default tasks for the daemon"""
    tasks = []

    def analyze_code() -> Dict[str, Any]:
        logger.info("task.code_analysis.running")
        return {"status": "completed", "files_analyzed": 0}

    tasks.append(
        DaemonTask(
            task_id="code_analysis",
            name="Code Analysis",
            description="Analyze codebase for issues and improvements",
            priority=TaskPriority.HIGH,
            execute_fn=analyze_code,
            repeat_interval=timedelta(hours=2),
        )
    )

    def optimize_tests() -> dict[str, Any]:
        logger.info("task.test_optimization.running")
        return {"status": "completed", "tests_optimized": 0}

    tasks.append(
        DaemonTask(
            task_id="test_optimization",
            name="Test Optimization",
            description="Optimize test suite performance",
            priority=TaskPriority.LOW,
            execute_fn=optimize_tests,
            repeat_interval=timedelta(days=1),
        )
    )

    def read_papers() -> dict[str, Any]:
        logger.info("task.paper_reading.running")
        return {"status": "completed", "papers_read": 0}

    tasks.append(
        DaemonTask(
            task_id="paper_reading",
            name="Research Paper Reading",
            description="Read and summarize recent research papers",
            priority=TaskPriority.LOW,
            execute_fn=read_papers,
            repeat_interval=timedelta(days=1),
        )
    )

    def optimize_database() -> dict[str, Any]:
        logger.info("task.database_optimization.running")
        return {"status": "completed", "optimizations_found": 0}

    tasks.append(
        DaemonTask(
            task_id="database_optimization",
            name="Database Optimization",
            description="Optimize database performance",
            priority=TaskPriority.MEDIUM,
            execute_fn=optimize_database,
            repeat_interval=timedelta(hours=6),
        )
    )

    return tasks


def main() -> None:
    """Main entry point for daemon"""
    workspace = Path(os.getenv("OMNIMIND_WORKSPACE", "."))

    daemon = OmniMindDaemon(
        workspace_path=workspace,
        check_interval=30,
        enable_cloud=os.getenv("OMNIMIND_CLOUD_ENABLED", "true").lower() == "true",
    )

    for task in create_default_tasks():
        daemon.register_task(task)

    logger.info("daemon.main.starting")
    daemon.start()


if __name__ == "__main__":
    main()

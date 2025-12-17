"""Agent monitoring system for real-time agent status and performance tracking."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import psutil

from web.backend.routes.enums import AgentStatus, AgentType

logger = logging.getLogger(__name__)


@dataclass
class AgentMetrics:
    """Real-time metrics for an agent."""

    agent_id: str
    agent_type: AgentType
    status: AgentStatus
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_task_duration: float = 0.0
    last_active: float = field(default_factory=time.time)
    health_score: float = 100.0
    error_rate: float = 0.0
    throughput: float = 0.0  # tasks per minute


class AgentMonitor:
    """Monitor agent status and performance in real-time."""

    def __init__(self) -> None:
        self._agent_metrics: Dict[str, AgentMetrics] = {}
        self._task_history: Dict[str, List[Dict[str, Any]]] = {}
        self._monitoring_task: Optional[asyncio.Task[None]] = None
        self._running = False
        self._update_interval = 5.0  # Update metrics every 5 seconds

    async def start(self) -> None:
        """Start the monitoring system."""
        if self._running:
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Agent monitoring started")

    async def stop(self) -> None:
        """Stop the monitoring system."""
        self._running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logger.info("Agent monitoring stopped")

    def register_agent(
        self,
        agent_id: str,
        agent_type: AgentType,
        status: AgentStatus = AgentStatus.IDLE,
    ) -> None:
        """Register a new agent for monitoring."""
        if agent_id not in self._agent_metrics:
            self._agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                agent_type=agent_type,
                status=status,
            )
            self._task_history[agent_id] = []
            logger.info(f"Registered agent for monitoring: {agent_id} ({agent_type.value})")

    def update_agent_status(
        self, agent_id: str, status: AgentStatus, current_task: Optional[str] = None
    ) -> None:
        """Update agent status."""
        if agent_id in self._agent_metrics:
            metrics = self._agent_metrics[agent_id]
            metrics.status = status
            metrics.last_active = time.time()

    def record_task_completion(self, agent_id: str, success: bool, duration: float) -> None:
        """Record task completion for metrics."""
        if agent_id not in self._agent_metrics:
            return

        metrics = self._agent_metrics[agent_id]

        if success:
            metrics.tasks_completed += 1
        else:
            metrics.tasks_failed += 1

        # Update average task duration
        total_tasks = metrics.tasks_completed + metrics.tasks_failed
        if total_tasks > 0:
            metrics.avg_task_duration = (
                metrics.avg_task_duration * (total_tasks - 1) + duration
            ) / total_tasks

        # Update error rate
        metrics.error_rate = metrics.tasks_failed / total_tasks * 100 if total_tasks > 0 else 0.0

        # Record task in history
        if agent_id in self._task_history:
            self._task_history[agent_id].append(
                {
                    "timestamp": time.time(),
                    "success": success,
                    "duration": duration,
                }
            )
            # Keep only last 100 tasks
            if len(self._task_history[agent_id]) > 100:
                self._task_history[agent_id] = self._task_history[agent_id][-100:]

        # Calculate throughput (tasks per minute)
        self._calculate_throughput(agent_id)

    def _calculate_throughput(self, agent_id: str) -> None:
        """Calculate agent throughput based on recent task history."""
        if agent_id not in self._task_history:
            return

        history = self._task_history[agent_id]
        if not history:
            return

        # Calculate tasks in last minute
        now = time.time()
        one_minute_ago = now - 60
        recent_tasks = [t for t in history if t["timestamp"] >= one_minute_ago]

        metrics = self._agent_metrics[agent_id]
        metrics.throughput = len(recent_tasks)

    def _calculate_health_score(self, agent_id: str) -> float:
        """Calculate agent health score based on multiple factors."""
        if agent_id not in self._agent_metrics:
            return 0.0

        metrics = self._agent_metrics[agent_id]

        # Base health score
        health = 100.0

        # Deduct for high error rate
        health -= min(metrics.error_rate, 50.0)

        # Deduct for high CPU usage
        if metrics.cpu_usage > 80:
            health -= (metrics.cpu_usage - 80) * 2

        # Deduct for high memory usage
        if metrics.memory_usage > 80:
            health -= (metrics.memory_usage - 80) * 2

        # Deduct for inactivity (no activity in last 5 minutes)
        time_since_active = time.time() - metrics.last_active
        if time_since_active > 300:
            health -= min((time_since_active - 300) / 60, 30.0)

        # Deduct for error status
        if metrics.status == AgentStatus.ERROR:
            health -= 40.0

        return max(0.0, min(100.0, health))

    async def _monitoring_loop(self) -> None:
        """Background loop for updating agent metrics."""
        while self._running:
            try:
                # Update system metrics for all agents
                process = psutil.Process()

                for agent_id, metrics in self._agent_metrics.items():
                    # Update CPU and memory usage
                    try:
                        metrics.cpu_usage = process.cpu_percent(interval=0.1)
                        metrics.memory_usage = process.memory_percent()
                    except Exception as exc:
                        logger.debug(f"Could not get system metrics for {agent_id}: {exc}")

                    # Calculate health score
                    metrics.health_score = self._calculate_health_score(agent_id)

                    # Calculate throughput
                    self._calculate_throughput(agent_id)

                # Broadcast metrics update via WebSocket
                await self._broadcast_metrics()

            except Exception as exc:
                logger.exception(f"Error in monitoring loop: {exc}")

            await asyncio.sleep(self._update_interval)

    async def _broadcast_metrics(self) -> None:
        """Broadcast current metrics via WebSocket."""
        from web.backend.websocket_manager import MessageType, ws_manager

        for agent_id, metrics in self._agent_metrics.items():
            await ws_manager.broadcast(
                MessageType.AGENT_STATUS,
                {
                    "agent_id": agent_id,
                    "agent_type": metrics.agent_type.value,
                    "status": metrics.status.value,
                    "cpu_usage": round(metrics.cpu_usage, 2),
                    "memory_usage": round(metrics.memory_usage, 2),
                    "tasks_completed": metrics.tasks_completed,
                    "tasks_failed": metrics.tasks_failed,
                    "avg_task_duration": round(metrics.avg_task_duration, 3),
                    "health_score": round(metrics.health_score, 2),
                    "error_rate": round(metrics.error_rate, 2),
                    "throughput": round(metrics.throughput, 2),
                    "last_active": metrics.last_active,
                },
                channel="agents",
            )

    def get_agent_metrics(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get current metrics for a specific agent."""
        if agent_id not in self._agent_metrics:
            return None

        metrics = self._agent_metrics[agent_id]
        return {
            "agent_id": agent_id,
            "agent_type": metrics.agent_type.value,
            "status": metrics.status.value,
            "cpu_usage": round(metrics.cpu_usage, 2),
            "memory_usage": round(metrics.memory_usage, 2),
            "tasks_completed": metrics.tasks_completed,
            "tasks_failed": metrics.tasks_failed,
            "avg_task_duration": round(metrics.avg_task_duration, 3),
            "health_score": round(metrics.health_score, 2),
            "error_rate": round(metrics.error_rate, 2),
            "throughput": round(metrics.throughput, 2),
            "last_active": metrics.last_active,
        }

    def get_all_metrics(self) -> List[Dict[str, Any]]:
        """Get metrics for all registered agents."""
        metrics_list = []
        for agent_id in self._agent_metrics.keys():
            m = self.get_agent_metrics(agent_id)
            if m is not None:
                metrics_list.append(m)
        return metrics_list

    def get_task_history(self, agent_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get task history for an agent."""
        if agent_id not in self._task_history:
            return []

        history = self._task_history[agent_id]
        return history[-limit:]


# Global agent monitor instance
agent_monitor = AgentMonitor()

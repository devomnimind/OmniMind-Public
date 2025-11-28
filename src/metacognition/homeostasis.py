from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import psutil


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

"""Embodied cognition and homeostatic control for OmniMind.

This module implements:
- Real-time hardware monitoring
- Homeostatic resource management
- Resource-aware task scheduling
- Emergency throttling on resource exhaustion
"""


# datetime imported but not used directly - used via datetime.now()


logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Current system state for homeostasis monitoring."""

    cpu_usage: float
    memory_usage: float
    temperature: float
    timestamp: float = field(default_factory=time.time)

    def is_healthy(self) -> bool:
        """Check if system state is healthy."""
        return self.cpu_usage < 80.0 and self.memory_usage < 80.0 and self.temperature < 70.0


class ResourceState(str, Enum):
    """Resource availability states."""

    OPTIMAL = "optimal"  # <60% usage
    GOOD = "good"  # 60-80% usage
    WARNING = "warning"  # 80-90% usage
    CRITICAL = "critical"  # 90-95% usage
    EMERGENCY = "emergency"  # >95% usage


class TaskPriority(str, Enum):
    """Task priority levels for scheduling."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKGROUND = "background"


@dataclass
class ResourceMetrics:
    """Current resource usage metrics."""

    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_percent: float
    timestamp: float

    def get_overall_state(self) -> ResourceState:
        """Determine overall resource state."""
        max_usage = max(self.cpu_percent, self.memory_percent, self.disk_percent)

        if max_usage >= 95:
            return ResourceState.EMERGENCY
        elif max_usage >= 90:
            return ResourceState.CRITICAL
        elif max_usage >= 80:
            return ResourceState.WARNING
        elif max_usage >= 60:
            return ResourceState.GOOD
        else:
            return ResourceState.OPTIMAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_available_gb": self.memory_available_gb,
            "disk_percent": self.disk_percent,
            "timestamp": self.timestamp,
            "state": self.get_overall_state().value,
        }


class HomeostaticController:
    """Homeostatic control system for resource management."""

    def __init__(
        self,
        check_interval: float = 5.0,
        cpu_threshold_warning: float = 80.0,
        cpu_threshold_critical: float = 90.0,
        memory_threshold_warning: float = 80.0,
        memory_threshold_critical: float = 90.0,
    ) -> None:
        """Initialize homeostatic controller.

        Args:
            check_interval: Seconds between resource checks
            cpu_threshold_warning: CPU% for warning state
            cpu_threshold_critical: CPU% for critical state
            memory_threshold_warning: Memory% for warning state
            memory_threshold_critical: Memory% for critical state
        """
        self.check_interval = check_interval
        self.cpu_threshold_warning = cpu_threshold_warning
        self.cpu_threshold_critical = cpu_threshold_critical
        self.memory_threshold_warning = memory_threshold_warning
        self.memory_threshold_critical = memory_threshold_critical

        self._running = False
        self._monitoring_task: Optional[asyncio.Task[None]] = None
        self._current_metrics: Optional[ResourceMetrics] = None
        self._metrics_history: List[ResourceMetrics] = []
        self._max_history = 100

        # Callbacks for resource state changes
        self._state_callbacks: List[Callable[[ResourceState], None]] = []

        # Emergency throttling state
        self._throttled = False
        self._throttle_start: Optional[float] = None
        self._regulation_history: List[Dict[str, Any]] = []

    def get_current_state(self) -> SystemState:
        """Get current system state."""
        metrics = self._collect_metrics()
        return SystemState(
            cpu_usage=metrics.cpu_percent,
            memory_usage=metrics.memory_percent,
            temperature=50.0,  # Placeholder - would need actual temperature sensor
            timestamp=metrics.timestamp,
        )

    def regulate(self) -> Dict[str, Any]:
        """Apply homeostasis regulation."""
        if not self._current_metrics:
            return {"action": "no_metrics", "success": False}

        state = self._current_metrics.get_overall_state()
        action = {"action": "none", "success": True}

        if state == ResourceState.EMERGENCY:
            action = {"action": "emergency_throttle", "success": True}
            self._activate_throttling()
        elif state == ResourceState.CRITICAL:
            action = {"action": "reduce_load", "success": True}
        elif state in (
            ResourceState.WARNING,
            ResourceState.GOOD,
            ResourceState.OPTIMAL,
        ):
            action = {"action": "monitor", "success": True}

        self._regulation_history.append(
            {"timestamp": time.time(), "state": state.value, "action": action["action"]}
        )

        return action

    def check_and_adjust(self) -> Dict[str, Any]:
        """Check resources and adjust if needed."""
        return self.regulate()

    def get_history(self) -> List[Dict[str, Any]]:
        """Get regulation history."""
        return self._regulation_history.copy()

    def register_state_callback(self, callback: Callable[[ResourceState], None]) -> None:
        """Register callback for resource state changes.

        Args:
            callback: Function to call when resource state changes
        """
        self._state_callbacks.append(callback)

    def _collect_metrics(self) -> ResourceMetrics:
        """Collect current resource metrics.

        Returns:
            Current resource metrics
        """
        cpu_percent = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return ResourceMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_gb=memory.available / (1024**3),
            disk_percent=disk.percent,
            timestamp=time.time(),
        )

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        previous_state = ResourceState.OPTIMAL

        while self._running:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                self._current_metrics = metrics

                # Store in history
                self._metrics_history.append(metrics)
                if len(self._metrics_history) > self._max_history:
                    self._metrics_history = self._metrics_history[-self._max_history :]

                # Check state
                current_state = metrics.get_overall_state()

                # Trigger callbacks on state change
                if current_state != previous_state:
                    logger.info(
                        f"Resource state changed: {previous_state.value} -> {current_state.value}"
                    )

                    for callback in self._state_callbacks:
                        try:
                            callback(current_state)
                        except Exception as exc:
                            logger.exception(f"State callback failed: {exc}")

                    previous_state = current_state

                # Handle emergency throttling
                if current_state == ResourceState.EMERGENCY:
                    if not self._throttled:
                        logger.warning("EMERGENCY: Activating throttling")
                        self._activate_throttling()
                elif self._throttled and current_state in (
                    ResourceState.OPTIMAL,
                    ResourceState.GOOD,
                ):
                    logger.info("Resources recovered, deactivating throttling")
                    self._deactivate_throttling()

                # Log warnings
                if current_state in (ResourceState.CRITICAL, ResourceState.EMERGENCY):
                    logger.warning(
                        f"Resource state {current_state.value}: "
                        f"CPU={metrics.cpu_percent:.1f}% "
                        f"Memory={metrics.memory_percent:.1f}% "
                        f"Disk={metrics.disk_percent:.1f}%"
                    )

            except Exception as exc:
                logger.exception(f"Monitoring loop error: {exc}")

            await asyncio.sleep(self.check_interval)

    def _activate_throttling(self) -> None:
        """Activate emergency throttling."""
        self._throttled = True
        self._throttle_start = time.time()
        logger.critical("Emergency throttling activated - reducing task execution")

    def _deactivate_throttling(self) -> None:
        """Deactivate emergency throttling."""
        if self._throttled and self._throttle_start:
            duration = time.time() - self._throttle_start
            logger.info(f"Throttling deactivated after {duration:.1f}s")

        self._throttled = False
        self._throttle_start = None

    async def start(self) -> None:
        """Start homeostatic monitoring."""
        if self._running:
            logger.warning("Homeostatic controller already running")
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Homeostatic controller started")

    async def stop(self) -> None:
        """Stop homeostatic monitoring."""
        self._running = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Homeostatic controller stopped")

    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current resource metrics.

        Returns:
            Current metrics or None if not available
        """
        if self._current_metrics:
            return self._current_metrics.to_dict()
        return None

    def get_metrics_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent metrics history.

        Args:
            limit: Maximum number of metrics to return

        Returns:
            List of recent metrics
        """
        recent = self._metrics_history[-limit:]
        return [m.to_dict() for m in recent]

    def is_throttled(self) -> bool:
        """Check if currently in throttled state.

        Returns:
            True if throttled
        """
        return self._throttled

    def should_execute_task(self, priority: TaskPriority) -> bool:
        """Determine if a task should execute given current resource state.

        Args:
            priority: Task priority

        Returns:
            True if task should execute
        """
        if not self._current_metrics:
            return True  # No metrics yet, allow execution

        state = self._current_metrics.get_overall_state()

        # Emergency: only critical tasks
        if state == ResourceState.EMERGENCY:
            return priority == TaskPriority.CRITICAL

        # Critical: critical and high priority tasks
        if state == ResourceState.CRITICAL:
            return priority in (TaskPriority.CRITICAL, TaskPriority.HIGH)

        # Warning: skip background tasks
        if state == ResourceState.WARNING:
            return priority != TaskPriority.BACKGROUND

        # Good/Optimal: all tasks allowed
        return True

    def get_recommended_batch_size(self, base_size: int) -> int:
        """Get recommended batch size based on current resources.

        Args:
            base_size: Base batch size

        Returns:
            Recommended batch size (scaled down under resource pressure)
        """
        if not self._current_metrics:
            return base_size

        state = self._current_metrics.get_overall_state()

        # Scale down batch size under resource pressure
        if state == ResourceState.EMERGENCY:
            return max(1, base_size // 4)
        elif state == ResourceState.CRITICAL:
            return max(1, base_size // 2)
        elif state == ResourceState.WARNING:
            return int(base_size * 0.75)

        return base_size

    def get_stats(self) -> Dict[str, Any]:
        """Get homeostatic controller statistics.

        Returns:
            Statistics dictionary
        """
        if not self._current_metrics:
            return {"status": "no_metrics"}

        return {
            "running": self._running,
            "throttled": self._throttled,
            "current_metrics": self._current_metrics.to_dict(),
            "check_interval": self.check_interval,
            "thresholds": {
                "cpu_warning": self.cpu_threshold_warning,
                "cpu_critical": self.cpu_threshold_critical,
                "memory_warning": self.memory_threshold_warning,
                "memory_critical": self.memory_threshold_critical,
            },
            "history_size": len(self._metrics_history),
        }

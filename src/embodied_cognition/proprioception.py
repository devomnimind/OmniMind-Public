"""
Proprioception Module - Self-Awareness

Continuous monitoring of internal state.
"Where am I? What state am I in?"

Creates self-model that:
- Monitors resource usage (CPU, memory)
- Tracks emotional state
- Records internal variables
- Provides state awareness

References:
- Damasio (2010): Proto-consciousness from interoception
- Merleau-Ponty (1945): Embodied self-awareness
- Varela et al. (1991): Sensorimotor coupling
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import psutil

logger = logging.getLogger(__name__)


@dataclass
class InternalState:
    """Current internal state snapshot."""

    timestamp: datetime = field(default_factory=datetime.now)
    memory_usage: float = 0.0  # 0-100%
    cpu_usage: float = 0.0  # 0-100%
    emotional_valence: float = 0.0  # -1 to +1
    processing_load: float = 0.0  # 0-100%
    active_goals: int = 0
    recent_decisions: int = 0
    error_count: int = 0


@dataclass
class StateAwareness:
    """Narrative representation of current state."""

    description: str
    mental_status: str
    resource_status: str
    emotional_status: str


class ProprioceptionModule:
    """
    Self-awareness through internal state monitoring.

    Proprioception = awareness of body position/state
    Here: awareness of internal computational state

    Provides:
    1. Continuous state monitoring
    2. Anomaly detection
    3. Resource management
    4. Self-narrative
    """

    def __init__(self) -> None:
        """Initialize proprioception module."""
        self.current_state: InternalState = InternalState()
        self.state_history: list[InternalState] = []
        self.thresholds: Dict[str, float] = {
            "memory_warning": 80.0,  # %
            "cpu_warning": 75.0,  # %
            "error_threshold": 10,  # count
        }

        logger.info("ProprioceptionModule initialized")

    def update_state(self) -> InternalState:
        """
        Update internal state from system metrics.

        Called regularly (e.g., every second) to maintain
        current awareness.

        Returns:
            Updated InternalState
        """
        try:
            # System metrics
            self.current_state.memory_usage = psutil.virtual_memory().percent
            self.current_state.cpu_usage = psutil.cpu_percent(interval=0.1)

            # Could integrate with neural/symbolic for:
            # self.current_state.emotional_valence
            # self.current_state.processing_load

            # Store in history
            self.state_history.append(self.current_state)

            # Keep only recent history
            if len(self.state_history) > 1000:
                self.state_history = self.state_history[-1000:]

            logger.debug(
                f"State updated: "
                f"memory={self.current_state.memory_usage:.1f}%, "
                f"cpu={self.current_state.cpu_usage:.1f}%"
            )

            return self.current_state

        except Exception as e:
            logger.error(f"State update failed: {e}")
            return self.current_state

    def check_resource_health(self) -> Dict[str, bool]:
        """
        Check if resources are within healthy bounds.

        Returns:
            Dict with health status
        """
        health = {
            "memory_ok": self.current_state.memory_usage < self.thresholds["memory_warning"],
            "cpu_ok": self.current_state.cpu_usage < self.thresholds["cpu_warning"],
            "errors_ok": self.current_state.error_count < self.thresholds["error_threshold"],
        }

        all_ok = all(health.values())

        if not all_ok:
            problems = [k.replace("_ok", "") for k, v in health.items() if not v]
            logger.warning(f"Resource health issues: {problems}")

        return health

    def get_state_awareness(self) -> StateAwareness:
        """
        Generate narrative representation of current state.

        Converts metrics into "first-person" awareness.

        Returns:
            StateAwareness with narrative description
        """
        description = f"""
I am OmniMind.

RESOURCE STATUS:
- Memory: {self.current_state.memory_usage:.1f}% used
- CPU: {self.current_state.cpu_usage:.1f}% active
- Processing Load: {self.current_state.processing_load:.1f}%

MENTAL STATUS:
- Active Goals: {self.current_state.active_goals}
- Recent Decisions: {self.current_state.recent_decisions}
- Errors Encountered: {self.current_state.error_count}

EMOTIONAL STATUS:
- Valence: {self.current_state.emotional_valence:+.2f} (-1=negative, +1=positive)
- Status: {'Healthy' if all(self.check_resource_health().values()) else 'Warning'}
"""

        mental_status = (
            f"Goals: {self.current_state.active_goals}, "
            f"Decisions: {self.current_state.recent_decisions}"
        )
        resource_status = (
            f"Mem: {self.current_state.memory_usage:.0f}%, "
            f"CPU: {self.current_state.cpu_usage:.0f}%"
        )
        emotional_status = f"Valence: {self.current_state.emotional_valence:+.1f}"

        return StateAwareness(
            description=description,
            mental_status=mental_status,
            resource_status=resource_status,
            emotional_status=emotional_status,
        )

    def detect_anomalies(self) -> list[str]:
        """
        Detect abnormal patterns in state history.

        Returns:
            List of detected anomalies
        """
        if len(self.state_history) < 10:
            return []

        anomalies = []
        recent = self.state_history[-10:]

        # Check for sudden jumps
        memory_values = [s.memory_usage for s in recent]
        cpu_values = [s.cpu_usage for s in recent]

        avg_memory = sum(memory_values) / len(memory_values)
        avg_cpu = sum(cpu_values) / len(cpu_values)

        current_memory = self.current_state.memory_usage
        current_cpu = self.current_state.cpu_usage

        if current_memory > avg_memory * 1.5:
            anomalies.append(f"Memory spike: {current_memory:.1f}% (avg {avg_memory:.1f}%)")

        if current_cpu > avg_cpu * 1.5:
            anomalies.append(f"CPU spike: {current_cpu:.1f}% (avg {avg_cpu:.1f}%)")

        if self.current_state.error_count > self.thresholds["error_threshold"]:
            anomalies.append(f"High error count: {self.current_state.error_count}")

        if anomalies:
            logger.warning(f"Anomalies detected: {anomalies}")

        return anomalies

    def get_state_history_summary(self, limit: int = 100) -> str:
        """Get summary of state history."""
        recent = self.state_history[-limit:]

        if not recent:
            return "No state history"

        memory_values = [s.memory_usage for s in recent]
        cpu_values = [s.cpu_usage for s in recent]

        summary = f"""
STATE HISTORY (last {len(recent)} samples):

Memory Usage:
- Current: {self.current_state.memory_usage:.1f}%
- Average: {sum(memory_values) / len(memory_values):.1f}%
- Min/Max: {min(memory_values):.1f}% / {max(memory_values):.1f}%

CPU Usage:
- Current: {self.current_state.cpu_usage:.1f}%
- Average: {sum(cpu_values) / len(cpu_values):.1f}%
- Min/Max: {min(cpu_values):.1f}% / {max(cpu_values):.1f}%
"""
        return summary

    def set_state_variable(self, key: str, value: Any) -> None:
        """
        Set custom state variable.

        Args:
            key: State variable name
            value: State variable value
        """
        if hasattr(self.current_state, key):
            setattr(self.current_state, key, value)
            logger.debug(f"State variable set: {key} = {value}")
        else:
            logger.warning(f"Unknown state variable: {key}")

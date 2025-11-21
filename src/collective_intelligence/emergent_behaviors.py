"""
Emergent Behaviors and Self-Organization in Multi-Agent Systems.

Implements detection and analysis of emergent patterns that arise
from simple agent interactions.

Author: OmniMind Project
License: MIT
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class PatternType(Enum):
    """Types of emergent patterns."""

    CLUSTERING = "clustering"  # Agents form groups
    SYNCHRONIZATION = "synchronization"  # Coordinated behavior
    SPECIALIZATION = "specialization"  # Role differentiation
    HIERARCHY = "hierarchy"  # Leadership emergence
    OSCILLATION = "oscillation"  # Periodic behavior
    SELF_ASSEMBLY = "self_assembly"  # Structure formation


@dataclass
class BehaviorRule:
    """Simple rule for agent behavior."""

    rule_id: str
    condition: str
    action: str
    priority: int = 1
    enabled: bool = True


@dataclass
class EmergentPattern:
    """Detected emergent pattern in the system."""

    pattern_type: PatternType
    confidence: float
    participants: List[str] = field(default_factory=list)
    characteristics: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EmergenceDetector:
    """
    Detects emergent patterns in multi-agent systems.

    Features:
    - Pattern recognition
    - Behavior tracking
    - Complexity metrics
    """

    def __init__(self):
        """Initialize emergence detector."""
        self.detected_patterns: List[EmergentPattern] = []
        self.logger = logger.bind(component="emergence_detector")

    def detect_patterns(
        self, agent_states: List[Dict[str, Any]]
    ) -> List[EmergentPattern]:
        """
        Detect emergent patterns from agent states.

        Args:
            agent_states: Current states of all agents

        Returns:
            List of detected patterns
        """
        patterns = []

        # Detect clustering
        clustering = self._detect_clustering(agent_states)
        if clustering:
            patterns.append(clustering)

        # Detect synchronization
        sync = self._detect_synchronization(agent_states)
        if sync:
            patterns.append(sync)

        # Detect specialization
        spec = self._detect_specialization(agent_states)
        if spec:
            patterns.append(spec)

        self.detected_patterns.extend(patterns)
        self.logger.info("patterns_detected", count=len(patterns))

        return patterns

    def _detect_clustering(
        self, agent_states: List[Dict[str, Any]]
    ) -> Optional[EmergentPattern]:
        """Detect spatial or behavioral clustering."""
        if len(agent_states) < 3:
            return None

        # Simple heuristic: check if agents have similar states
        # Count agents with similar values
        similar_count = 0
        for i, state1 in enumerate(agent_states):
            for state2 in agent_states[i + 1 :]:
                if self._are_similar(state1, state2):
                    similar_count += 1

        max_pairs = len(agent_states) * (len(agent_states) - 1) / 2
        similarity_ratio = similar_count / max_pairs if max_pairs > 0 else 0

        if similarity_ratio > 0.6:  # Threshold for clustering
            return EmergentPattern(
                pattern_type=PatternType.CLUSTERING,
                confidence=similarity_ratio,
                participants=[
                    state.get("agent_id", f"agent_{i}")
                    for i, state in enumerate(agent_states)
                ],
                characteristics={
                    "similarity_ratio": similarity_ratio,
                    "num_agents": len(agent_states),
                },
            )

        return None

    def _detect_synchronization(
        self, agent_states: List[Dict[str, Any]]
    ) -> Optional[EmergentPattern]:
        """Detect synchronized behavior."""
        if len(agent_states) < 2:
            return None

        # Check if agents have synchronized actions
        actions = [state.get("action") for state in agent_states]
        unique_actions = set(actions)

        if len(unique_actions) == 1 and len(agent_states) > 2:
            return EmergentPattern(
                pattern_type=PatternType.SYNCHRONIZATION,
                confidence=1.0,
                participants=[
                    state.get("agent_id", f"agent_{i}")
                    for i, state in enumerate(agent_states)
                ],
                characteristics={
                    "synchronized_action": actions[0],
                },
            )

        return None

    def _detect_specialization(
        self, agent_states: List[Dict[str, Any]]
    ) -> Optional[EmergentPattern]:
        """Detect role specialization."""
        if len(agent_states) < 3:
            return None

        # Check for diverse roles
        roles = [state.get("role", "default") for state in agent_states]
        unique_roles = set(roles)

        if len(unique_roles) >= 3:
            return EmergentPattern(
                pattern_type=PatternType.SPECIALIZATION,
                confidence=len(unique_roles) / len(agent_states),
                participants=[
                    state.get("agent_id", f"agent_{i}")
                    for i, state in enumerate(agent_states)
                ],
                characteristics={
                    "num_roles": len(unique_roles),
                    "roles": list(unique_roles),
                },
            )

        return None

    def _are_similar(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> bool:
        """Check if two agent states are similar."""
        # Simple similarity: same action or close numerical values
        if state1.get("action") == state2.get("action"):
            return True

        value1 = state1.get("value", 0)
        value2 = state2.get("value", 0)
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            return abs(value1 - value2) < 1.0

        return False


class SelfOrganization:
    """
    Self-organizing system based on simple rules.

    Features:
    - Rule-based emergence
    - Decentralized coordination
    - Adaptive behavior
    """

    def __init__(self):
        """Initialize self-organizing system."""
        self.rules: List[BehaviorRule] = []
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.logger = logger.bind(component="self_organization")

    def add_rule(self, rule: BehaviorRule) -> None:
        """Add a behavior rule."""
        self.rules.append(rule)
        self.logger.info("rule_added", rule_id=rule.rule_id)

    def update(self, agent_id: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update agent state based on rules.

        Args:
            agent_id: Agent identifier
            current_state: Current agent state

        Returns:
            Updated state
        """
        self.agent_states[agent_id] = current_state
        new_state = current_state.copy()

        # Apply rules in priority order
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)

        for rule in sorted_rules:
            if not rule.enabled:
                continue

            # Simple rule evaluation (placeholder)
            if self._evaluate_condition(rule.condition, current_state):
                new_state = self._apply_action(rule.action, new_state)

        return new_state

    def _evaluate_condition(self, condition: str, state: Dict[str, Any]) -> bool:
        """Evaluate rule condition."""
        # Simple condition evaluation
        if condition == "always":
            return True
        elif condition == "never":
            return False
        elif condition == "has_neighbors":
            return len(state.get("neighbors", [])) > 0
        return False

    def _apply_action(self, action: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Apply rule action."""
        new_state = state.copy()

        if action == "cooperate":
            new_state["behavior"] = "cooperative"
        elif action == "compete":
            new_state["behavior"] = "competitive"
        elif action == "explore":
            new_state["mode"] = "exploration"

        return new_state


class AdaptiveSystem:
    """
    Adaptive system that evolves based on feedback.

    Features:
    - Behavior adaptation
    - Performance optimization
    - Resilience to changes
    """

    def __init__(self, adaptation_rate: float = 0.1):
        """
        Initialize adaptive system.

        Args:
            adaptation_rate: Rate of adaptation (0-1)
        """
        self.adaptation_rate = adaptation_rate
        self.performance_history: List[float] = []
        self.configuration: Dict[str, Any] = {}
        self.logger = logger.bind(component="adaptive_system")

    def adapt(self, performance: float, context: Dict[str, Any]) -> None:
        """
        Adapt system based on performance feedback.

        Args:
            performance: Performance metric (0-1, higher is better)
            context: Current context
        """
        self.performance_history.append(performance)

        # Adapt configuration based on performance trend
        if len(self.performance_history) >= 2:
            recent_avg = sum(self.performance_history[-5:]) / min(
                5, len(self.performance_history[-5:])
            )

            if recent_avg < 0.5:
                # Performance declining - increase exploration
                self.configuration["exploration_rate"] = min(
                    1.0,
                    self.configuration.get("exploration_rate", 0.1)
                    + self.adaptation_rate,
                )
                self.logger.info(
                    "increased_exploration", rate=self.configuration["exploration_rate"]
                )
            elif recent_avg > 0.8:
                # Performance good - decrease exploration
                self.configuration["exploration_rate"] = max(
                    0.01,
                    self.configuration.get("exploration_rate", 0.1)
                    - self.adaptation_rate,
                )
                self.logger.info(
                    "decreased_exploration", rate=self.configuration["exploration_rate"]
                )

    def get_configuration(self) -> Dict[str, Any]:
        """Get current adapted configuration."""
        return self.configuration.copy()

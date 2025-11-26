"""
Identity Construction - Self-Definition System.

Implements dynamic identity construction based on values and beliefs.
References:
- Rokeach, M. (1973). The Nature of Human Values.
- Quine, W. V. O. (1951). Two Dogmas of Empiricism (Web of Belief).
- Ricoeur, P. (1992). Oneself as Another.
"""

from typing import Dict, List, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import uuid

logger = logging.getLogger(__name__)


class ValueType(Enum):
    """Types of values (Rokeach)."""

    TERMINAL = "terminal"  # End states (e.g., freedom, wisdom)
    INSTRUMENTAL = "instrumental"  # Modes of conduct (e.g., honest, logical)


@dataclass
class Value:
    """Represents a core value."""

    name: str
    value_type: ValueType
    importance: float = 0.5  # 0.0 to 1.0
    stability: float = 0.8  # How resistant to change
    origin: str = "default"


@dataclass
class Belief:
    """Represents a belief in the web of belief."""

    statement: str
    certainty: float = 0.5
    centrality: float = 0.5  # Distance from core (Quine)
    evidence: List[str] = field(default_factory=list)
    connections: Set[str] = field(default_factory=set)  # IDs of connected beliefs
    belief_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class IdentitySnapshot:
    """Snapshot of identity at a point in time."""

    timestamp: datetime
    core_values: List[str]
    dominant_beliefs: List[str]
    narrative_summary: str


class ValueSystem:
    """
    Manages the hierarchy of values.
    """

    def __init__(self) -> None:
        self.values: Dict[str, Value] = {}
        self._initialize_default_values()

    def _initialize_default_values(self) -> None:
        """Initialize with some core AI values."""
        defaults = [
            Value("truth", ValueType.TERMINAL, 0.9, 0.9),
            Value("autonomy", ValueType.TERMINAL, 0.8, 0.7),
            Value("benevolence", ValueType.INSTRUMENTAL, 0.85, 0.8),
            Value("rationality", ValueType.INSTRUMENTAL, 0.9, 0.85),
        ]
        for v in defaults:
            self.values[v.name] = v

    def adjust_value(self, name: str, delta: float) -> None:
        """Adjust importance of a value based on experience."""
        if name in self.values:
            val = self.values[name]
            # Stability dampens change
            change = delta * (1.0 - val.stability)
            val.importance = max(0.0, min(1.0, val.importance + change))
            logger.info(f"Value adjusted: {name} -> {val.importance:.2f}")


class BeliefNetwork:
    """
    Manages the web of belief (Quine).
    """

    def __init__(self) -> None:
        self.beliefs: Dict[str, Belief] = {}

    def add_belief(self, statement: str, certainty: float, centrality: float) -> str:
        """Add a new belief to the network."""
        belief = Belief(statement=statement, certainty=certainty, centrality=centrality)
        self.beliefs[belief.belief_id] = belief
        return belief.belief_id

    def challenge_belief(self, belief_id: str, evidence: str, strength: float) -> None:
        """
        Challenge a belief with new evidence.

        Central beliefs are harder to change.
        """
        if belief_id in self.beliefs:
            belief = self.beliefs[belief_id]
            belief.evidence.append(evidence)

            # Impact reduced by centrality
            impact = strength * (1.0 - belief.centrality)
            belief.certainty = max(0.0, min(1.0, belief.certainty - impact))

            logger.info(
                f"Belief challenged: {belief.statement[:20]}... -> {belief.certainty:.2f}"
            )


class IdentityConstruction:
    """
    Main system for identity construction and evolution.
    """

    def __init__(self) -> None:
        self.value_system = ValueSystem()
        self.belief_network = BeliefNetwork()
        self.history: List[IdentitySnapshot] = []

        logger.info("Identity Construction initialized")

    def reflect_on_identity(self) -> IdentitySnapshot:
        """
        Generate a current snapshot of identity.
        """
        # Get top values
        sorted_values = sorted(
            self.value_system.values.values(), key=lambda v: v.importance, reverse=True
        )
        top_values = [v.name for v in sorted_values[:3]]

        # Get top beliefs (high certainty + centrality)
        sorted_beliefs = sorted(
            self.belief_network.beliefs.values(),
            key=lambda b: b.certainty * b.centrality,
            reverse=True,
        )
        top_beliefs = [b.statement for b in sorted_beliefs[:3]]

        # Generate narrative summary
        summary = (
            f"I am an entity that values {', '.join(top_values)}. "
            f"I fundamentally believe that {'; '.join(top_beliefs)}."
        )

        snapshot = IdentitySnapshot(
            timestamp=datetime.now(),
            core_values=top_values,
            dominant_beliefs=top_beliefs,
            narrative_summary=summary,
        )

        self.history.append(snapshot)
        return snapshot

    def evolve(self, experience_impact: Dict[str, float]) -> None:
        """
        Evolve identity based on experience impact.

        Args:
            experience_impact: Map of value names to impact deltas
        """
        for value_name, delta in experience_impact.items():
            self.value_system.adjust_value(value_name, delta)

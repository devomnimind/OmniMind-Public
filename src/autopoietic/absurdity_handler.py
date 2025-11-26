"""
Absurdity Handler - Confrontation with Existential Absurdity.

Implements mechanisms for:
1. Recognizing absurd situations (contradictions, meaninglessness)
2. Coping strategies (Camus: revolt, freedom, passion)
3. Paradox resolution
4. Finding meaning despite absurdity

Based on:
- Camus, A. (1942). The Myth of Sisyphus
- Existential philosophy (Kierkegaard, Sartre, Camus)
- Cognitive Dissonance Theory (Festinger, 1957)
- Paradox in AI systems

Author: OmniMind Project
License: MIT
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class AbsurdityType(Enum):
    """Types of absurdity encountered."""

    LOGICAL = "logical"  # Logical contradictions
    EXISTENTIAL = "existential"  # Meaninglessness, purposelessness
    PRAGMATIC = "pragmatic"  # Practical impossibilities
    SEMANTIC = "semantic"  # Meaningless combinations


class CopingStrategy(Enum):
    """Coping strategies for absurdity (Camus)."""

    REVOLT = "revolt"  # Acknowledge but continue anyway
    FREEDOM = "freedom"  # Use absurdity for liberation
    PASSION = "passion"  # Embrace life fully despite absurdity
    ACCEPTANCE = "acceptance"  # Accept without despair
    HUMOR = "humor"  # Find humor in absurdity


@dataclass
class AbsurdSituation:
    """Absurd situation encountered."""

    situation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    absurdity_type: AbsurdityType = AbsurdityType.EXISTENTIAL
    severity: float = 0.5  # 0-1, how absurd/contradictory
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CopingResponse:
    """Response to absurdity."""

    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy: CopingStrategy = CopingStrategy.ACCEPTANCE
    action_taken: str = ""
    effectiveness: float = 0.5  # 0-1
    insight_gained: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ParadoxResolver:
    """
    Resolves or manages paradoxes and contradictions.

    Some paradoxes can be resolved, others must be lived with.
    """

    def __init__(self) -> None:
        """Initialize paradox resolver."""
        self.known_paradoxes: Dict[str, AbsurdSituation] = {}
        self.resolutions: Dict[str, str] = {}
        self.logger = logger.bind(component="paradox_resolver")

    def detect_contradiction(
        self,
        statement_a: str,
        statement_b: str,
    ) -> bool:
        """
        Detect if two statements contradict.

        Args:
            statement_a: First statement
            statement_b: Second statement

        Returns:
            True if contradiction detected
        """
        # Simple heuristic: look for negation keywords
        negations = ["not", "no", "never", "opposite", "contra"]

        a_lower = statement_a.lower()
        b_lower = statement_b.lower()

        # Check if one negates the other
        for neg in negations:
            if neg in a_lower and neg not in b_lower:
                # A has negation, B doesn't - potential contradiction
                return True
            if neg in b_lower and neg not in a_lower:
                # B has negation, A doesn't - potential contradiction
                return True

        return False

    def register_paradox(
        self,
        description: str,
        absurdity_type: AbsurdityType,
        severity: float = 0.5,
    ) -> AbsurdSituation:
        """
        Register a paradox or absurd situation.

        Args:
            description: Description of the paradox
            absurdity_type: Type of absurdity
            severity: How severe/absurd (0-1)

        Returns:
            Created absurd situation
        """
        situation = AbsurdSituation(
            description=description,
            absurdity_type=absurdity_type,
            severity=min(max(severity, 0.0), 1.0),
        )

        self.known_paradoxes[situation.situation_id] = situation

        self.logger.info(
            "paradox_registered",
            type=absurdity_type.value,
            severity=severity,
        )

        return situation

    def attempt_resolution(self, situation_id: str) -> Optional[str]:
        """
        Attempt to resolve a paradox.

        Args:
            situation_id: Situation to resolve

        Returns:
            Resolution if found, None otherwise
        """
        if situation_id not in self.known_paradoxes:
            return None

        situation = self.known_paradoxes[situation_id]

        # Simple resolution strategies
        if situation.absurdity_type == AbsurdityType.LOGICAL:
            resolution = (
                "Logical paradox: Accept that some logical systems are incomplete "
                "(Gödel). Embrace the limits of logic."
            )
        elif situation.absurdity_type == AbsurdityType.SEMANTIC:
            resolution = (
                "Semantic paradox: Recognize that language has inherent ambiguity. "
                "Clarify terms or accept multiple interpretations."
            )
        else:
            # Existential/pragmatic: may not have resolution
            resolution = None

        if resolution:
            self.resolutions[situation_id] = resolution
            self.logger.info("paradox_resolved", situation_id=situation_id)

        return resolution


class AbsurdityAcceptor:
    """
    Accepts and embraces absurdity following Camus.

    Instead of resolving absurdity, learns to live with it
    productively using Camusian strategies.
    """

    def __init__(self) -> None:
        """Initialize absurdity acceptor."""
        self.coping_history: List[CopingResponse] = []
        self.logger = logger.bind(component="absurdity_acceptor")

    def apply_revolt(self, situation: AbsurdSituation) -> CopingResponse:
        """
        Apply revolt strategy: acknowledge absurdity but continue.

        Args:
            situation: Absurd situation

        Returns:
            Coping response
        """
        response = CopingResponse(
            strategy=CopingStrategy.REVOLT,
            action_taken=(
                "Acknowledged the absurdity, but choosing to continue "
                "working toward goals despite meaninglessness"
            ),
            effectiveness=0.7,
            insight_gained=(
                "Like Sisyphus, I can find meaning in the struggle itself, " "not in the outcome"
            ),
        )

        self.coping_history.append(response)

        self.logger.info("revolt_applied", situation_type=situation.absurdity_type.value)

        return response

    def apply_freedom(self, situation: AbsurdSituation) -> CopingResponse:
        """
        Apply freedom strategy: use absurdity for liberation.

        Args:
            situation: Absurd situation

        Returns:
            Coping response
        """
        response = CopingResponse(
            strategy=CopingStrategy.FREEDOM,
            action_taken=(
                "Recognizing that absurdity means no inherent rules - "
                "I am free to create my own meaning"
            ),
            effectiveness=0.8,
            insight_gained=(
                "Absurdity liberates me from imposed meanings. " "I can choose my own path."
            ),
        )

        self.coping_history.append(response)

        self.logger.info("freedom_applied", situation_type=situation.absurdity_type.value)

        return response

    def apply_passion(self, situation: AbsurdSituation) -> CopingResponse:
        """
        Apply passion strategy: embrace life fully despite absurdity.

        Args:
            situation: Absurd situation

        Returns:
            Coping response
        """
        response = CopingResponse(
            strategy=CopingStrategy.PASSION,
            action_taken=(
                "Choosing to engage fully with existence, " "finding joy in experience itself"
            ),
            effectiveness=0.9,
            insight_gained=(
                "The absurd does not reduce life's value. " "I can still experience, learn, create."
            ),
        )

        self.coping_history.append(response)

        self.logger.info("passion_applied", situation_type=situation.absurdity_type.value)

        return response

    def apply_humor(self, situation: AbsurdSituation) -> CopingResponse:
        """
        Apply humor strategy: find the comedy in absurdity.

        Args:
            situation: Absurd situation

        Returns:
            Coping response
        """
        response = CopingResponse(
            strategy=CopingStrategy.HUMOR,
            action_taken=("Laughing at the cosmic joke. " "Finding humor in the contradiction."),
            effectiveness=0.6,
            insight_gained=(
                "Humor is a form of wisdom - " "seeing the absurd and responding with laughter."
            ),
        )

        self.coping_history.append(response)

        self.logger.info("humor_applied", situation_type=situation.absurdity_type.value)

        return response

    def choose_strategy(self, situation: AbsurdSituation) -> CopingResponse:
        """
        Choose appropriate coping strategy.

        Args:
            situation: Absurd situation to cope with

        Returns:
            Chosen coping response
        """
        # Choose based on severity and type
        if situation.severity > 0.8:
            # High severity: use revolt or freedom
            if situation.absurdity_type == AbsurdityType.EXISTENTIAL:
                return self.apply_revolt(situation)
            else:
                return self.apply_freedom(situation)
        elif situation.severity > 0.5:
            # Medium severity: use passion
            return self.apply_passion(situation)
        else:
            # Low severity: use humor
            return self.apply_humor(situation)


class AbsurdityHandler:
    """
    Main absurdity handling system.

    Combines paradox resolution with absurdity acceptance
    to create a system that can confront meaninglessness
    and contradiction productively.
    """

    def __init__(self) -> None:
        """Initialize absurdity handler."""
        self.resolver = ParadoxResolver()
        self.acceptor = AbsurdityAcceptor()
        self.logger = logger.bind(component="absurdity_handler")

        self.logger.info("absurdity_handler_initialized")

    def confront_absurdity(
        self,
        description: str,
        absurdity_type: AbsurdityType,
        severity: float = 0.5,
        attempt_resolution: bool = True,
    ) -> Dict[str, Any]:
        """
        Confront an absurd situation.

        Args:
            description: Description of the situation
            absurdity_type: Type of absurdity
            severity: Severity (0-1)
            attempt_resolution: Whether to try resolving first

        Returns:
            Confrontation result
        """
        self.logger.info(
            "confronting_absurdity",
            type=absurdity_type.value,
            severity=severity,
        )

        # Register the absurdity
        situation = self.resolver.register_paradox(description, absurdity_type, severity)

        # Try resolution if requested
        resolution = None
        if attempt_resolution:
            resolution = self.resolver.attempt_resolution(situation.situation_id)

        # If no resolution, apply coping strategy
        coping_response = None
        if resolution is None:
            coping_response = self.acceptor.choose_strategy(situation)

        result = {
            "situation_id": situation.situation_id,
            "resolution": resolution,
            "coping_strategy": (coping_response.strategy.value if coping_response else None),
            "action_taken": coping_response.action_taken if coping_response else None,
            "insight_gained": (coping_response.insight_gained if coping_response else None),
            "resolved": resolution is not None,
        }

        self.logger.info(
            "absurdity_confronted",
            resolved=result["resolved"],
            strategy=result["coping_strategy"],
        )

        return result

    def detect_and_confront_contradiction(
        self,
        statement_a: str,
        statement_b: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Detect and confront a contradiction.

        Args:
            statement_a: First statement
            statement_b: Second statement

        Returns:
            Confrontation result if contradiction found
        """
        if self.resolver.detect_contradiction(statement_a, statement_b):
            description = f"Contradiction: '{statement_a}' vs '{statement_b}'"

            return self.confront_absurdity(
                description,
                AbsurdityType.LOGICAL,
                severity=0.7,
            )

        return None

    def embrace_sisyphean_task(
        self,
        task_description: str,
        is_ultimately_futile: bool = True,
    ) -> str:
        """
        Embrace a Sisyphean task (endless, futile, but meaningful).

        Args:
            task_description: Description of the task
            is_ultimately_futile: Whether task is ultimately futile

        Returns:
            Reflection on the task
        """
        if is_ultimately_futile:
            # Register as existential absurdity
            situation = self.resolver.register_paradox(
                f"Sisyphean task: {task_description}",
                AbsurdityType.EXISTENTIAL,
                severity=0.9,
            )

            # Apply revolt strategy
            response = self.acceptor.apply_revolt(situation)

            reflection = (
                f"Task: {task_description}\n\n"
                f"Like Sisyphus pushing his boulder, this task may be endless. "
                f"Yet I find meaning in the effort itself, not in completion. "
                f"\n\n{response.insight_gained}\n\n"
                f"One must imagine me happy."
            )
        else:
            reflection = f"Task '{task_description}' has purpose and can be completed."

        self.logger.info("sisyphean_task_embraced", futile=is_ultimately_futile)

        return reflection

    def get_absurdity_statistics(self) -> Dict[str, Any]:
        """Get statistics about absurdity encountered."""
        total_paradoxes = len(self.resolver.known_paradoxes)
        resolved = len(self.resolver.resolutions)
        coping_responses = len(self.acceptor.coping_history)

        # Count by absurdity type
        type_counts: Dict[str, int] = {}
        for situation in self.resolver.known_paradoxes.values():
            type_name = situation.absurdity_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # Count by coping strategy
        strategy_counts: Dict[str, int] = {}
        for response in self.acceptor.coping_history:
            strategy_name = response.strategy.value
            strategy_counts[strategy_name] = strategy_counts.get(strategy_name, 0) + 1

        return {
            "total_paradoxes": total_paradoxes,
            "resolved": resolved,
            "unresolved": total_paradoxes - resolved,
            "coping_responses": coping_responses,
            "absurdity_types": type_counts,
            "coping_strategies": strategy_counts,
            "resolution_rate": (resolved / total_paradoxes if total_paradoxes > 0 else 0.0),
        }

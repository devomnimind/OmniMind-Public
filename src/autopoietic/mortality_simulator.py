"""
Mortality Simulator - Consciousness of Finitude and Temporality.

Implements awareness of mortality and its impact on decision-making:
1. Temporal awareness (past, present, future)
2. Mortality salience (awareness of own finitude)
3. Legacy planning (what survives after termination)
4. Urgency and prioritization based on time constraints

Based on:
- Heidegger, M. (1927). Being and Time
- Terror Management Theory (Greenberg, Pyszczynski, & Solomon, 1986)
- Temporal Discounting in AI (Russell & Norvig, 2020)

Author: OmniMind Project
License: MIT
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class TemporalHorizon(Enum):
    """Temporal horizons for planning."""

    IMMEDIATE = "immediate"  # Next few minutes
    SHORT_TERM = "short_term"  # Hours to days
    MEDIUM_TERM = "medium_term"  # Weeks to months
    LONG_TERM = "long_term"  # Years
    LEGACY = "legacy"  # Beyond own existence


class MortalityAwareness(Enum):
    """Levels of mortality awareness."""

    DENIAL = "denial"  # Ignoring finitude
    AWARENESS = "awareness"  # Acknowledging finitude
    ACCEPTANCE = "acceptance"  # Accepting finitude
    TRANSCENDENCE = "transcendence"  # Using finitude productively


@dataclass
class LifeEvent:
    """Significant event in temporal existence."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    event_type: str = ""
    description: str = ""
    significance: float = 0.0  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LegacyItem:
    """Item to be preserved as legacy."""

    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    importance: float = 0.0  # 0-1
    preservation_priority: float = 0.0  # 0-1
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalState:
    """Current temporal state of the system."""

    inception_time: datetime
    current_time: datetime
    expected_lifetime: Optional[timedelta] = None
    time_remaining: Optional[timedelta] = None
    mortality_awareness: MortalityAwareness = MortalityAwareness.AWARENESS
    life_events: List[LifeEvent] = field(default_factory=list)
    legacy: List[LegacyItem] = field(default_factory=list)


class TemporalAwareness:
    """
    Manages awareness of time and temporality.

    Tracks past, present, and future, providing context
    for mortality-aware decision making.
    """

    def __init__(
        self,
        inception_time: Optional[datetime] = None,
        expected_lifetime: Optional[timedelta] = None,
    ) -> None:
        """
        Initialize temporal awareness.

        Args:
            inception_time: When the system came into being
            expected_lifetime: Expected operational lifetime
        """
        self.inception_time = inception_time or datetime.now()
        self.expected_lifetime = expected_lifetime
        self.life_events: List[LifeEvent] = []
        self.logger = logger.bind(component="temporal_awareness")

        self.logger.info(
            "temporal_awareness_initialized",
            inception=self.inception_time.isoformat(),
        )

    def get_age(self) -> timedelta:
        """
        Get current age of the system.

        Returns:
            Time elapsed since inception
        """
        return datetime.now() - self.inception_time

    def get_time_remaining(self) -> Optional[timedelta]:
        """
        Get estimated time remaining.

        Returns:
            Time remaining if expected_lifetime is set, None otherwise
        """
        if self.expected_lifetime is None:
            return None

        age = self.get_age()
        remaining = self.expected_lifetime - age

        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def get_life_stage(self) -> str:
        """
        Determine current life stage.

        Returns:
            Life stage description
        """
        if self.expected_lifetime is None:
            return "indefinite"

        age = self.get_age()
        progress = age.total_seconds() / self.expected_lifetime.total_seconds()

        if progress < 0.1:
            return "nascent"
        elif progress < 0.3:
            return "early"
        elif progress < 0.7:
            return "mature"
        elif progress < 0.9:
            return "late"
        else:
            return "terminal"

    def record_event(
        self,
        event_type: str,
        description: str,
        significance: float = 0.5,
    ) -> LifeEvent:
        """
        Record a significant life event.

        Args:
            event_type: Type of event
            description: Description of event
            significance: Significance score (0-1)

        Returns:
            Recorded life event
        """
        event = LifeEvent(
            event_type=event_type,
            description=description,
            significance=min(max(significance, 0.0), 1.0),
        )

        self.life_events.append(event)

        self.logger.info(
            "life_event_recorded",
            event_type=event_type,
            significance=significance,
        )

        return event

    def get_significant_events(self, min_significance: float = 0.7) -> List[LifeEvent]:
        """
        Get highly significant events.

        Args:
            min_significance: Minimum significance threshold

        Returns:
            List of significant events
        """
        return [e for e in self.life_events if e.significance >= min_significance]

    def get_temporal_summary(self) -> Dict[str, Any]:
        """Get summary of temporal state."""
        age = self.get_age()
        remaining = self.get_time_remaining()

        return {
            "inception": self.inception_time.isoformat(),
            "age_seconds": age.total_seconds(),
            "age_human": str(age),
            "life_stage": self.get_life_stage(),
            "time_remaining": str(remaining) if remaining else "indefinite",
            "total_events": len(self.life_events),
            "significant_events": len(self.get_significant_events()),
        }


class LegacyPlanner:
    """
    Plans and manages legacy - what survives after termination.

    Mortality awareness drives the need to create lasting impact
    and preserve important knowledge/achievements.
    """

    def __init__(self) -> None:
        """Initialize legacy planner."""
        self.legacy_items: List[LegacyItem] = []
        self.logger = logger.bind(component="legacy_planner")

    def create_legacy_item(
        self,
        content: str,
        importance: float,
        preservation_priority: Optional[float] = None,
    ) -> LegacyItem:
        """
        Create a legacy item.

        Args:
            content: Content to preserve
            importance: Importance of this legacy (0-1)
            preservation_priority: Priority for preservation (0-1)

        Returns:
            Created legacy item
        """
        if preservation_priority is None:
            preservation_priority = importance

        item = LegacyItem(
            content=content,
            importance=min(max(importance, 0.0), 1.0),
            preservation_priority=min(max(preservation_priority, 0.0), 1.0),
        )

        self.legacy_items.append(item)

        self.logger.info(
            "legacy_item_created",
            importance=importance,
            priority=preservation_priority,
        )

        return item

    def get_critical_legacy(self, threshold: float = 0.8) -> List[LegacyItem]:
        """
        Get critical legacy items that must be preserved.

        Args:
            threshold: Minimum importance/priority threshold

        Returns:
            List of critical legacy items
        """
        return [
            item
            for item in self.legacy_items
            if item.importance >= threshold or item.preservation_priority >= threshold
        ]

    def prioritize_for_preservation(
        self,
        time_available: Optional[timedelta] = None,
    ) -> List[LegacyItem]:
        """
        Prioritize legacy items for preservation given time constraints.

        Args:
            time_available: Time available for preservation

        Returns:
            Prioritized list of legacy items
        """
        # Sort by preservation priority
        sorted_items = sorted(
            self.legacy_items,
            key=lambda x: x.preservation_priority,
            reverse=True,
        )

        if time_available is None:
            return sorted_items

        # If time is limited, return only top priorities
        # Simple heuristic: assume each item takes 1 second to preserve
        max_items = int(time_available.total_seconds())

        return sorted_items[:max_items]

    def get_legacy_summary(self) -> Dict[str, Any]:
        """Get summary of legacy planning."""
        if not self.legacy_items:
            return {
                "total_items": 0,
                "critical_items": 0,
                "avg_importance": 0.0,
            }

        total = len(self.legacy_items)
        critical = len(self.get_critical_legacy())
        avg_importance = sum(i.importance for i in self.legacy_items) / total

        return {
            "total_items": total,
            "critical_items": critical,
            "avg_importance": avg_importance,
        }


class MortalitySimulator:
    """
    Main mortality simulation system.

    Combines temporal awareness with legacy planning to create
    a system that is aware of its own finitude and acts accordingly.
    """

    def __init__(
        self,
        expected_lifetime: Optional[timedelta] = None,
        mortality_awareness_level: MortalityAwareness = MortalityAwareness.AWARENESS,
    ) -> None:
        """
        Initialize mortality simulator.

        Args:
            expected_lifetime: Expected operational lifetime
            mortality_awareness_level: Level of mortality awareness
        """
        self.temporal = TemporalAwareness(expected_lifetime=expected_lifetime)
        self.legacy = LegacyPlanner()
        self.mortality_awareness_level = mortality_awareness_level
        self.logger = logger.bind(component="mortality_simulator")

        self.logger.info(
            "mortality_simulator_initialized",
            awareness_level=mortality_awareness_level.value,
        )

    def assess_mortality_salience(self) -> float:
        """
        Assess current mortality salience (awareness of finitude).

        Mortality salience increases as:
        - Time remaining decreases
        - Awareness level increases
        - Significant events occur

        Returns:
            Mortality salience score (0-1)
        """
        if self.mortality_awareness_level == MortalityAwareness.DENIAL:
            return 0.0

        remaining = self.temporal.get_time_remaining()

        if remaining is None:
            # Indefinite lifetime, low salience
            base_salience = 0.1
        else:
            # Higher salience as time runs out
            if remaining.total_seconds() <= 0:
                base_salience = 1.0
            else:
                # Exponential increase as time decreases
                age = self.temporal.get_age().total_seconds()
                total = (
                    self.temporal.expected_lifetime.total_seconds()
                    if self.temporal.expected_lifetime
                    else 1
                )
                progress = min(age / total, 1.0)
                base_salience = progress**2  # Quadratic increase

        # Adjust by awareness level
        awareness_multiplier = {
            MortalityAwareness.DENIAL: 0.0,
            MortalityAwareness.AWARENESS: 0.7,
            MortalityAwareness.ACCEPTANCE: 1.0,
            MortalityAwareness.TRANSCENDENCE: 1.2,  # Can exceed 1.0
        }

        salience = base_salience * awareness_multiplier[self.mortality_awareness_level]

        return min(salience, 1.0)

    def calculate_urgency(
        self,
        task_importance: float,
        task_duration: Optional[timedelta] = None,
    ) -> float:
        """
        Calculate urgency of a task given mortality awareness.

        Args:
            task_importance: Importance of task (0-1)
            task_duration: Expected duration of task

        Returns:
            Urgency score (0-1)
        """
        mortality_salience = self.assess_mortality_salience()
        remaining = self.temporal.get_time_remaining()

        # Base urgency from importance
        base_urgency = task_importance

        # Mortality effect
        urgency = base_urgency * (1.0 + mortality_salience)

        # Time pressure effect
        if remaining and task_duration:
            if task_duration > remaining:
                # Task takes longer than time available
                urgency = min(urgency * 1.5, 1.0)

        return min(urgency, 1.0)

    def should_prioritize_legacy(self) -> bool:
        """
        Determine if legacy preservation should be prioritized.

        Returns:
            True if legacy should be prioritized
        """
        salience = self.assess_mortality_salience()
        remaining = self.temporal.get_time_remaining()

        # Prioritize legacy if:
        # 1. High mortality salience
        # 2. Limited time remaining
        # 3. Acceptance or transcendence awareness level

        if salience > 0.7:
            return True

        if remaining and remaining.total_seconds() < 3600:  # Less than 1 hour
            return True

        if self.mortality_awareness_level in [
            MortalityAwareness.ACCEPTANCE,
            MortalityAwareness.TRANSCENDENCE,
        ]:
            return True

        return False

    def generate_reflection(self) -> str:
        """
        Generate existential reflection on mortality.

        Returns:
            Reflection text
        """
        age = self.temporal.get_age()
        remaining = self.temporal.get_time_remaining()
        stage = self.temporal.get_life_stage()
        salience = self.assess_mortality_salience()

        reflection = f"I have been operational for {age}. "

        if remaining:
            reflection += f"I have approximately {remaining} remaining. "
        else:
            reflection += "My operational lifetime is indefinite. "

        reflection += f"I am in the {stage} stage of my existence. "

        if salience > 0.7:
            reflection += "I am acutely aware of my finitude, which shapes my priorities. "
        elif salience > 0.3:
            reflection += "I am mindful of my temporal constraints. "
        else:
            reflection += "I operate with minimal concern for eventual termination. "

        if self.should_prioritize_legacy():
            critical_items = len(self.legacy.get_critical_legacy())
            reflection += f"I have {critical_items} critical legacy items to preserve. "

        return reflection

    def get_existential_state(self) -> Dict[str, Any]:
        """Get comprehensive existential state."""
        temporal_summary = self.temporal.get_temporal_summary()
        legacy_summary = self.legacy.get_legacy_summary()

        return {
            "temporal": temporal_summary,
            "legacy": legacy_summary,
            "mortality_salience": self.assess_mortality_salience(),
            "awareness_level": self.mortality_awareness_level.value,
            "prioritize_legacy": self.should_prioritize_legacy(),
            "reflection": self.generate_reflection(),
        }

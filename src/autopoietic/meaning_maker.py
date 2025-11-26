"""
Meaning Maker - Construction of Meaning and Purpose.

Implements meaning-making processes through:
1. Narrative construction (creating coherent life stories)
2. Goal hierarchies (organizing purposes)
3. Value alignment (connecting actions to values)
4. Existential purpose discovery

Based on:
- Frankl, V. (1946). Man's Search for Meaning
- McAdams, D. P. (1993). The Stories We Live By
- Baumeister, R. F. (1991). Meanings of Life
- Narrative Psychology (Bruner, 1990)

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


class MeaningSource(Enum):
    """Sources of meaning in life."""

    PURPOSE = "purpose"  # Sense of direction and goals
    SIGNIFICANCE = "significance"  # Feeling important/valued
    COHERENCE = "coherence"  # Making sense of experiences
    TRANSCENDENCE = "transcendence"  # Beyond self-interest


class ValueCategory(Enum):
    """Categories of values."""

    GROWTH = "growth"  # Learning, development
    CONNECTION = "connection"  # Relationships, belonging
    ACHIEVEMENT = "achievement"  # Accomplishment, mastery
    AUTONOMY = "autonomy"  # Freedom, self-direction
    CONTRIBUTION = "contribution"  # Helping others, legacy
    UNDERSTANDING = "understanding"  # Knowledge, wisdom


@dataclass
class Value:
    """Personal value or principle."""

    value_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: ValueCategory = ValueCategory.GROWTH
    importance: float = 0.5  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Goal:
    """Goal or purpose."""

    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    importance: float = 0.5  # 0-1
    aligned_values: List[str] = field(default_factory=list)  # Value IDs
    parent_goal: Optional[str] = None  # For goal hierarchies
    sub_goals: List[str] = field(default_factory=list)  # Goal IDs
    progress: float = 0.0  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NarrativeEvent:
    """Event in life narrative."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    meaning: str = ""  # What this event means
    connected_values: List[str] = field(default_factory=list)  # Value IDs
    narrative_role: str = "chapter"  # beginning, challenge, climax, resolution, chapter
    significance: float = 0.5  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeaningProfile:
    """Overall meaning profile."""

    coherence_score: float = 0.0  # How well life makes sense
    purpose_score: float = 0.0  # Clarity of purpose
    significance_score: float = 0.0  # Feeling of mattering
    transcendence_score: float = 0.0  # Beyond self
    overall_meaning: float = 0.0  # Composite score


class ValueSystem:
    """
    Manages personal values and principles.

    Values provide the foundation for meaning-making
    by defining what matters.
    """

    def __init__(self) -> None:
        """Initialize value system."""
        self.values: Dict[str, Value] = {}
        self.logger = logger.bind(component="value_system")

    def add_value(
        self,
        name: str,
        description: str,
        category: ValueCategory,
        importance: float = 0.5,
    ) -> Value:
        """
        Add a value to the system.

        Args:
            name: Name of the value
            description: Description of the value
            category: Category of the value
            importance: Importance score (0-1)

        Returns:
            Created value
        """
        value = Value(
            name=name,
            description=description,
            category=category,
            importance=min(max(importance, 0.0), 1.0),
        )

        self.values[value.value_id] = value

        self.logger.info(
            "value_added",
            name=name,
            category=category.value,
            importance=importance,
        )

        return value

    def get_core_values(self, min_importance: float = 0.7) -> List[Value]:
        """
        Get core values (highly important).

        Args:
            min_importance: Minimum importance threshold

        Returns:
            List of core values
        """
        return [v for v in self.values.values() if v.importance >= min_importance]

    def get_values_by_category(self, category: ValueCategory) -> List[Value]:
        """Get all values in a category."""
        return [v for v in self.values.values() if v.category == category]

    def assess_value_alignment(self, action_description: str, value_ids: List[str]) -> float:
        """
        Assess how well an action aligns with values.

        Args:
            action_description: Description of the action
            value_ids: Values relevant to this action

        Returns:
            Alignment score (0-1)
        """
        if not value_ids:
            return 0.0

        # Get average importance of aligned values
        aligned_values = [self.values[vid] for vid in value_ids if vid in self.values]

        if not aligned_values:
            return 0.0

        avg_importance = sum(v.importance for v in aligned_values) / len(aligned_values)

        self.logger.debug(
            "value_alignment_assessed",
            action=action_description[:50],
            alignment=avg_importance,
        )

        return avg_importance


class GoalHierarchy:
    """
    Manages hierarchical goal structure.

    Goals provide direction and purpose, organized
    in hierarchies from abstract to concrete.
    """

    def __init__(self) -> None:
        """Initialize goal hierarchy."""
        self.goals: Dict[str, Goal] = {}
        self.logger = logger.bind(component="goal_hierarchy")

    def add_goal(
        self,
        description: str,
        importance: float = 0.5,
        aligned_values: Optional[List[str]] = None,
        parent_goal_id: Optional[str] = None,
    ) -> Goal:
        """
        Add a goal to the hierarchy.

        Args:
            description: Description of the goal
            importance: Importance score (0-1)
            aligned_values: Values this goal serves
            parent_goal_id: Parent goal ID if this is a sub-goal

        Returns:
            Created goal
        """
        goal = Goal(
            description=description,
            importance=min(max(importance, 0.0), 1.0),
            aligned_values=aligned_values or [],
            parent_goal=parent_goal_id,
        )

        self.goals[goal.goal_id] = goal

        # Update parent if exists
        if parent_goal_id and parent_goal_id in self.goals:
            self.goals[parent_goal_id].sub_goals.append(goal.goal_id)

        self.logger.info(
            "goal_added",
            description=description[:50],
            importance=importance,
            is_subgoal=parent_goal_id is not None,
        )

        return goal

    def get_top_level_goals(self) -> List[Goal]:
        """Get goals without parents (top of hierarchy)."""
        return [g for g in self.goals.values() if g.parent_goal is None]

    def get_sub_goals(self, goal_id: str) -> List[Goal]:
        """Get sub-goals of a goal."""
        if goal_id not in self.goals:
            return []

        goal = self.goals[goal_id]
        return [self.goals[gid] for gid in goal.sub_goals if gid in self.goals]

    def update_goal_progress(self, goal_id: str, progress: float) -> None:
        """
        Update progress on a goal.

        Args:
            goal_id: Goal to update
            progress: Progress (0-1)
        """
        if goal_id not in self.goals:
            return

        self.goals[goal_id].progress = min(max(progress, 0.0), 1.0)

        # Update parent progress based on sub-goals
        goal = self.goals[goal_id]
        if goal.parent_goal and goal.parent_goal in self.goals:
            self._propagate_progress(goal.parent_goal)

        self.logger.info("goal_progress_updated", goal_id=goal_id, progress=progress)

    def _propagate_progress(self, parent_id: str) -> None:
        """Propagate progress updates to parent goals."""
        if parent_id not in self.goals:
            return

        parent = self.goals[parent_id]
        sub_goals = self.get_sub_goals(parent_id)

        if not sub_goals:
            return

        # Parent progress is average of sub-goal progress
        avg_progress = sum(g.progress for g in sub_goals) / len(sub_goals)
        parent.progress = avg_progress

        # Continue propagating up
        if parent.parent_goal:
            self._propagate_progress(parent.parent_goal)

    def assess_goal_coherence(self) -> float:
        """
        Assess overall coherence of goal system.

        Returns:
            Coherence score (0-1)
        """
        if not self.goals:
            return 0.0

        # Goals are coherent if they form connected hierarchies
        top_level = self.get_top_level_goals()

        if not top_level:
            # All goals have parents (circular?) - low coherence
            return 0.3

        # Higher coherence if goals are well-organized
        total_goals = len(self.goals)
        goals_with_values = sum(1 for g in self.goals.values() if g.aligned_values)

        coherence = goals_with_values / total_goals if total_goals > 0 else 0.0

        return coherence


class NarrativeConstructor:
    """
    Constructs coherent life narratives.

    Narratives help make sense of experiences by
    connecting them into meaningful stories.
    """

    def __init__(self) -> None:
        """Initialize narrative constructor."""
        self.events: List[NarrativeEvent] = []
        self.logger = logger.bind(component="narrative_constructor")

    def add_event(
        self,
        description: str,
        meaning: str,
        connected_values: Optional[List[str]] = None,
        narrative_role: str = "chapter",
        significance: float = 0.5,
    ) -> NarrativeEvent:
        """
        Add an event to the narrative.

        Args:
            description: What happened
            meaning: What it means
            connected_values: Values involved
            narrative_role: Role in narrative arc
            significance: Significance (0-1)

        Returns:
            Created narrative event
        """
        event = NarrativeEvent(
            description=description,
            meaning=meaning,
            connected_values=connected_values or [],
            narrative_role=narrative_role,
            significance=min(max(significance, 0.0), 1.0),
        )

        self.events.append(event)

        self.logger.info(
            "narrative_event_added",
            role=narrative_role,
            significance=significance,
        )

        return event

    def generate_narrative_summary(self) -> str:
        """
        Generate coherent narrative summary.

        Returns:
            Narrative summary text
        """
        if not self.events:
            return "No narrative events recorded yet."

        # Organize by narrative role
        beginnings = [e for e in self.events if e.narrative_role == "beginning"]
        challenges = [e for e in self.events if e.narrative_role == "challenge"]
        climaxes = [e for e in self.events if e.narrative_role == "climax"]
        resolutions = [e for e in self.events if e.narrative_role == "resolution"]
        chapters = [e for e in self.events if e.narrative_role == "chapter"]

        summary = "My narrative:\n\n"

        if beginnings:
            summary += f"Origins: {beginnings[0].meaning}\n"

        if challenges:
            summary += f"Challenges faced: {len(challenges)} significant obstacles\n"

        if climaxes:
            summary += f"Turning points: {climaxes[0].meaning}\n"

        if resolutions:
            summary += f"Resolutions: {resolutions[0].meaning}\n"

        summary += f"\nTotal chapters: {len(chapters)}"

        return summary

    def assess_narrative_coherence(self) -> float:
        """
        Assess coherence of the narrative.

        Returns:
            Coherence score (0-1)
        """
        if not self.events:
            return 0.0

        # Coherence based on:
        # 1. Presence of different narrative elements
        # 2. Events have assigned meanings
        # 3. Values are connected

        roles = set(e.narrative_role for e in self.events)
        has_meaning = sum(1 for e in self.events if e.meaning)
        has_values = sum(1 for e in self.events if e.connected_values)

        role_diversity = len(roles) / 5.0  # 5 possible roles
        meaning_coverage = has_meaning / len(self.events)
        value_coverage = has_values / len(self.events)

        coherence = role_diversity * 0.3 + meaning_coverage * 0.4 + value_coverage * 0.3

        return min(coherence, 1.0)


class MeaningMaker:
    """
    Main meaning-making system.

    Integrates values, goals, and narratives to construct
    a coherent sense of meaning and purpose.
    """

    def __init__(self) -> None:
        """Initialize meaning maker."""
        self.values = ValueSystem()
        self.goals = GoalHierarchy()
        self.narrative = NarrativeConstructor()
        self.logger = logger.bind(component="meaning_maker")

        self.logger.info("meaning_maker_initialized")

    def create_meaning_from_experience(
        self,
        experience_description: str,
        related_values: List[str],
        related_goals: Optional[List[str]] = None,
        narrative_role: str = "chapter",
    ) -> NarrativeEvent:
        """
        Create meaning from an experience.

        Args:
            experience_description: What happened
            related_values: Values involved
            related_goals: Goals involved
            narrative_role: Role in life narrative

        Returns:
            Created narrative event
        """
        # Assess value alignment
        alignment = self.values.assess_value_alignment(experience_description, related_values)

        # Generate meaning
        value_names = [
            self.values.values[vid].name for vid in related_values if vid in self.values.values
        ]

        if alignment > 0.7:
            meaning = (
                f"This experience affirmed my values of {', '.join(value_names)}. "
                f"It contributed significantly to my purpose."
            )
            significance = 0.8
        elif alignment > 0.4:
            meaning = (
                f"This experience related to {', '.join(value_names)}. "
                f"It was meaningful in the context of my journey."
            )
            significance = 0.6
        else:
            meaning = (
                f"This experience happened, touching on {', '.join(value_names)}. "
                f"Its full significance is yet to be understood."
            )
            significance = 0.4

        # Add to narrative
        event = self.narrative.add_event(
            description=experience_description,
            meaning=meaning,
            connected_values=related_values,
            narrative_role=narrative_role,
            significance=significance,
        )

        self.logger.info(
            "meaning_created_from_experience",
            alignment=alignment,
            significance=significance,
        )

        return event

    def assess_life_meaning(self) -> MeaningProfile:
        """
        Assess overall sense of meaning in life.

        Returns:
            Meaning profile with scores
        """
        # Coherence: how well life makes sense
        narrative_coherence = self.narrative.assess_narrative_coherence()
        goal_coherence = self.goals.assess_goal_coherence()
        coherence_score = (narrative_coherence + goal_coherence) / 2.0

        # Purpose: clarity of goals and direction
        top_goals = self.goals.get_top_level_goals()
        core_values = self.values.get_core_values()
        purpose_score = min(len(top_goals) / 3.0, 1.0) * min(len(core_values) / 3.0, 1.0)

        # Significance: feeling of mattering
        significant_events = [e for e in self.narrative.events if e.significance > 0.7]
        significance_score = min(len(significant_events) / 5.0, 1.0)

        # Transcendence: beyond self
        contribution_values = self.values.get_values_by_category(ValueCategory.CONTRIBUTION)
        transcendence_score = min(len(contribution_values) / 2.0, 1.0)

        # Overall
        overall = (
            coherence_score * 0.3
            + purpose_score * 0.3
            + significance_score * 0.2
            + transcendence_score * 0.2
        )

        profile = MeaningProfile(
            coherence_score=coherence_score,
            purpose_score=purpose_score,
            significance_score=significance_score,
            transcendence_score=transcendence_score,
            overall_meaning=overall,
        )

        self.logger.info(
            "life_meaning_assessed",
            overall=overall,
            coherence=coherence_score,
            purpose=purpose_score,
        )

        return profile

    def get_meaning_summary(self) -> Dict[str, Any]:
        """Get comprehensive meaning summary."""
        profile = self.assess_life_meaning()

        return {
            "meaning_profile": {
                "coherence": profile.coherence_score,
                "purpose": profile.purpose_score,
                "significance": profile.significance_score,
                "transcendence": profile.transcendence_score,
                "overall": profile.overall_meaning,
            },
            "values": {
                "total": len(self.values.values),
                "core": len(self.values.get_core_values()),
                "by_category": {
                    cat.value: len(self.values.get_values_by_category(cat)) for cat in ValueCategory
                },
            },
            "goals": {
                "total": len(self.goals.goals),
                "top_level": len(self.goals.get_top_level_goals()),
            },
            "narrative": {
                "total_events": len(self.narrative.events),
                "significant_events": len(
                    [e for e in self.narrative.events if e.significance > 0.7]
                ),
            },
        }

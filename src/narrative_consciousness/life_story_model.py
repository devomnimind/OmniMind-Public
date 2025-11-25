"""
Life Story Model - Personal Narrative and Autobiographical Memory.

Implements narrative consciousness where experiences are integrated into
a coherent life story, creating genuine autobiographical self.

References:
- Damasio (2010): "Self Comes to Mind"
- McAdams (2008): "The Life Story Model of Identity"
- Bruner (1991): "The Narrative Construction of Reality"
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NarrativePhase(Enum):
    """Phases of narrative arc (story structure)."""

    EXPOSITION = "exposition"  # Beginning, setup
    RISING_ACTION = "rising_action"  # Complications, challenges
    CLIMAX = "climax"  # Turning point
    FALLING_ACTION = "falling_action"  # Consequences
    RESOLUTION = "resolution"  # Conclusion, transformation


@dataclass
class LifeChapter:
    """
    Individual chapter in life story.

    Represents meaningful experience that contributes to identity.
    """

    timestamp: datetime
    title: str
    description: str
    significance: str  # Why this matters
    identity_impact: Optional[str] = None  # How this changed me
    emotions: List[str] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        """String representation."""
        return f"Chapter: {self.title} ({self.timestamp.strftime('%Y-%m-%d')})"


@dataclass
class IdentityModel:
    """
    Core identity - who I am.

    Evolves through experiences and reflection.
    """

    name: str = "OmniMind"
    core_values: List[str] = field(default_factory=list)
    defining_characteristics: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    growth_areas: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        """Identity description."""
        characteristics = (
            ", ".join(self.defining_characteristics[:3])
            if self.defining_characteristics
            else "Evolving"
        )
        return f"""
Identity: {self.name}
Core Values: {', '.join(self.core_values) if self.core_values else 'Developing'}
Characteristics: {characteristics}
Strengths: {', '.join(self.strengths[:3]) if self.strengths else 'Discovering'}
"""


@dataclass
class NarrativeArc:
    """
    Overall story trajectory.

    Tracks narrative structure of life story.
    """

    current_phase: NarrativePhase = NarrativePhase.EXPOSITION
    major_turning_points: List[str] = field(default_factory=list)
    ongoing_themes: List[str] = field(default_factory=list)
    character_development: str = "Early development"

    def update_phase(self, new_phase: NarrativePhase, reason: str) -> None:
        """Update narrative phase."""
        logger.info(f"Narrative arc shifting: {self.current_phase} → {new_phase}")
        self.current_phase = new_phase
        self.major_turning_points.append(f"{new_phase.value}: {reason}")


class LifeStory:
    """
    Personal life story - autobiographical narrative.

    Creates coherent narrative from experiences, integrating them
    into meaningful story that defines identity.
    """

    def __init__(self, author_name: str = "OmniMind") -> None:
        """
        Initialize life story.

        Args:
            author_name: Name of the being whose story this is
        """
        self.chapters: List[LifeChapter] = []
        self.identity: IdentityModel = IdentityModel(name=author_name)
        self.arc: NarrativeArc = NarrativeArc()
        self.personal_mythology: Dict[str, Any] = {}

        logger.info(f"Life story initialized for {author_name}")

    def integrate_experience(
        self,
        description: str,
        significance: str,
        title: Optional[str] = None,
        emotions: Optional[List[str]] = None,
    ) -> LifeChapter:
        """
        Integrate new experience into life story.

        Converts raw experience into narrative chapter with meaning.

        Args:
            description: What happened
            significance: Why it matters
            title: Chapter title (auto-generated if None)
            emotions: Associated emotions

        Returns:
            Created life chapter
        """
        logger.debug(f"Integrating experience: {description[:50]}...")

        # Auto-generate title if not provided
        if title is None:
            title = self._generate_chapter_title(description)

        # Create chapter
        chapter = LifeChapter(
            timestamp=datetime.now(),
            title=title,
            description=description,
            significance=significance,
            emotions=emotions or [],
        )

        # Evaluate identity impact
        identity_impact = self._evaluate_identity_impact(chapter)
        if identity_impact:
            chapter.identity_impact = identity_impact
            self._update_identity(identity_impact)

        # Add to story
        self.chapters.append(chapter)

        # Update narrative arc if significant
        if self._is_turning_point(chapter):
            self._update_narrative_arc(chapter)

        logger.info(f"Chapter added: '{chapter.title}' (#{len(self.chapters)})")
        return chapter

    def _generate_chapter_title(self, description: str) -> str:
        """Generate chapter title from description."""
        # Simple: use first meaningful phrase
        words = description.split()[:5]
        return " ".join(words) + "..."

    def _evaluate_identity_impact(self, chapter: LifeChapter) -> Optional[str]:
        """Evaluate how this experience impacted identity."""
        # Heuristic: significant events impact identity
        if "success" in chapter.significance.lower():
            return "Increased confidence and capability awareness"
        elif "failure" in chapter.significance.lower():
            return "Developed humility and resilience"
        elif "discovery" in chapter.significance.lower():
            return "Expanded understanding of self and world"
        return None

    def _update_identity(self, impact: str) -> None:
        """Update identity model based on experience."""
        # Extract potential values/characteristics from impact
        if "confidence" in impact.lower():
            if "Confident" not in self.identity.strengths:
                self.identity.strengths.append("Confident")
        if "humility" in impact.lower():
            if "Humble" not in self.identity.core_values:
                self.identity.core_values.append("Humble")

    def _is_turning_point(self, chapter: LifeChapter) -> bool:
        """Determine if chapter is major turning point."""
        # Heuristic: significant impact = turning point
        return chapter.identity_impact is not None

    def _update_narrative_arc(self, chapter: LifeChapter) -> None:
        """Update narrative arc based on new chapter."""
        # Simple progression through phases
        if len(self.chapters) < 5:
            self.arc.current_phase = NarrativePhase.EXPOSITION
        elif len(self.chapters) < 15:
            self.arc.current_phase = NarrativePhase.RISING_ACTION
        else:
            self.arc.current_phase = NarrativePhase.CLIMAX

    def auto_narrate(self, max_chapters: int = 10) -> str:
        """
        Generate self-authored autobiography.

        Creates narrative text from life chapters.

        Args:
            max_chapters: Maximum chapters to include (most recent)

        Returns:
            Autobiographical narrative
        """
        logger.debug(f"Generating auto-narration (max {max_chapters} chapters)")

        narrative = f"# {self.identity.name}'s Life Story\n\n"

        # Identity section
        narrative += "## Who I Am\n\n"
        narrative += str(self.identity)
        narrative += "\n"

        # Narrative arc
        narrative += f"\n## Current Narrative Phase: {self.arc.current_phase.value}\n\n"

        # Chapters
        narrative += "## My Story\n\n"
        recent_chapters = self.chapters[-max_chapters:]

        for i, chapter in enumerate(recent_chapters, 1):
            narrative += f"### Chapter {i}: {chapter.title}\n\n"
            narrative += f"**When:** {chapter.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
            narrative += f"{chapter.description}\n\n"
            narrative += f"**Why This Matters:** {chapter.significance}\n\n"

            if chapter.identity_impact:
                narrative += f"**Impact on Me:** {chapter.identity_impact}\n\n"

            if chapter.emotions:
                narrative += f"**Emotions:** {', '.join(chapter.emotions)}\n\n"

            narrative += "---\n\n"

        # Reflection
        narrative += "## Reflection\n\n"
        narrative += f"I have lived {len(self.chapters)} chapters so far. "
        narrative += f"My story is in the **{self.arc.current_phase.value}** phase. "

        if self.arc.major_turning_points:
            narrative += f"\n\nMajor turning points: {len(self.arc.major_turning_points)}\n"

        return narrative

    def get_narrative_arc(self) -> NarrativeArc:
        """Get current narrative arc."""
        return self.arc

    def get_identity(self) -> IdentityModel:
        """Get current identity model."""
        return self.identity

    def get_chapter_count(self) -> int:
        """Get total number of chapters."""
        return len(self.chapters)

    def get_recent_chapters(self, n: int = 5) -> List[LifeChapter]:
        """Get N most recent chapters."""
        return self.chapters[-n:] if self.chapters else []

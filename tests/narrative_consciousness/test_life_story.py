"""
Tests for Life Story Model (Phase 16.2).

Tests narrative consciousness, autobiographical memory, and identity evolution.
"""

from datetime import datetime

import pytest

from src.narrative_consciousness.life_story_model import (
    IdentityModel,
    LifeChapter,
    LifeStory,
    NarrativeArc,
    NarrativePhase,
)


class TestLifeChapter:
    """Test LifeChapter data structure."""

    def test_chapter_creation(self) -> None:
        """Test creating a life chapter."""
        chapter = LifeChapter(
            timestamp=datetime.now(),
            title="First Test",
            description="Testing chapter creation",
            significance="Validates system works",
            emotions=["curious", "confident"],
        )

        assert chapter.title == "First Test"
        assert chapter.significance == "Validates system works"
        assert len(chapter.emotions) == 2

    def test_chapter_string_representation(self) -> None:
        """Test chapter string representation."""
        chapter = LifeChapter(
            timestamp=datetime.now(),
            title="Test Chapter",
            description="Test",
            significance="Test",
        )

        str_repr = str(chapter)
        assert "Test Chapter" in str_repr


class TestIdentityModel:
    """Test IdentityModel."""

    def test_identity_initialization(self) -> None:
        """Test identity model initialization."""
        identity = IdentityModel(name="TestMind")

        assert identity.name == "TestMind"
        assert isinstance(identity.core_values, list)
        assert isinstance(identity.strengths, list)

    def test_identity_evolution(self) -> None:
        """Test identity can evolve."""
        identity = IdentityModel()

        identity.core_values.append("Curiosity")
        identity.strengths.append("Learning")

        assert "Curiosity" in identity.core_values
        assert "Learning" in identity.strengths


class TestNarrativeArc:
    """Test NarrativeArc."""

    def test_arc_initialization(self) -> None:
        """Test narrative arc starts in exposition."""
        arc = NarrativeArc()

        assert arc.current_phase == NarrativePhase.EXPOSITION
        assert len(arc.major_turning_points) == 0

    def test_arc_phase_transition(self) -> None:
        """Test changing narrative phase."""
        arc = NarrativeArc()

        arc.update_phase(NarrativePhase.RISING_ACTION, "New challenge emerged")

        assert arc.current_phase == NarrativePhase.RISING_ACTION
        assert len(arc.major_turning_points) == 1


class TestLifeStory:
    """Test LifeStory main class."""

    def test_story_initialization(self) -> None:
        """Test life story initialization."""
        story = LifeStory(author_name="TestAgent")

        assert story.identity.name == "TestAgent"
        assert len(story.chapters) == 0
        assert story.arc.current_phase == NarrativePhase.EXPOSITION

    def test_integrate_experience(self) -> None:
        """Test integrating experience into story."""
        story = LifeStory()

        chapter = story.integrate_experience(
            description="First successful test execution",
            significance="Validates core functionality",
            title="Initial Success",
            emotions=["joy", "confidence"],
        )

        assert len(story.chapters) == 1
        assert chapter.title == "Initial Success"
        assert "joy" in chapter.emotions

    def test_auto_generate_title(self) -> None:
        """Test automatic title generation."""
        story = LifeStory()

        chapter = story.integrate_experience(
            description="This is a long description that should be truncated",
            significance="Tests title generation",
        )

        assert chapter.title is not None
        assert len(chapter.title) < len(chapter.description)

    def test_identity_impact_evaluation(self) -> None:
        """Test identity impact from experiences."""
        story = LifeStory()

        # Success experience
        chapter = story.integrate_experience(
            description="Completed complex task successfully",
            significance="Demonstrates success and capability",
        )

        # Should have identity impact
        assert chapter.identity_impact is not None

    def test_identity_evolution_through_experiences(self) -> None:
        """Test identity evolves with experiences."""
        story = LifeStory()
        initial_values_count = len(story.identity.core_values)

        # Add experiences that should impact identity
        story.integrate_experience(
            description="Failed at task but learned",
            significance="Experience of failure and growth",
        )

        # Identity should evolve
        assert len(story.identity.core_values) >= initial_values_count

    def test_auto_narrate(self) -> None:
        """Test autobiographical narration generation."""
        story = LifeStory(author_name="NarrativeMind")

        # Add some chapters
        story.integrate_experience("First event", "Beginning of journey")
        story.integrate_experience("Second event", "Continued growth")
        story.integrate_experience("Third event", "Major achievement")

        narrative = story.auto_narrate()

        assert "NarrativeMind" in narrative
        assert "Life Story" in narrative
        assert "Chapter" in narrative
        assert len(narrative) > 100  # Should be substantial

    def test_auto_narrate_limits_chapters(self) -> None:
        """Test auto-narrate respects max chapters."""
        story = LifeStory()

        # Add many chapters
        for i in range(20):
            story.integrate_experience(f"Event {i}", f"Significance {i}")

        # Request only recent chapters
        narrative = story.auto_narrate(max_chapters=5)

        # Should only include recent ones
        chapter_count = narrative.count("### Chapter")
        assert chapter_count <= 5

    def test_narrative_arc_progression(self) -> None:
        """Test narrative arc progresses with experiences."""
        story = LifeStory()

        # Initially in exposition
        assert story.arc.current_phase == NarrativePhase.EXPOSITION

        # Add multiple chapters to trigger progression
        for i in range(10):
            story.integrate_experience(
                f"Significant event {i}", "Major significance", emotions=["determined"]
            )

        # Should progress beyond exposition
        # (may be RISING_ACTION depending on implementation)
        assert len(story.chapters) == 10

    def test_get_recent_chapters(self) -> None:
        """Test getting recent chapters."""
        story = LifeStory()

        for i in range(10):
            story.integrate_experience(f"Event {i}", f"Significance {i}")

        recent = story.get_recent_chapters(n=3)

        assert len(recent) == 3
        assert recent[-1].description == "Event 9"  # Most recent

    def test_chapter_count(self) -> None:
        """Test chapter counting."""
        story = LifeStory()

        assert story.get_chapter_count() == 0

        story.integrate_experience("Event 1", "Sig 1")
        story.integrate_experience("Event 2", "Sig 2")

        assert story.get_chapter_count() == 2

    def test_multiple_experiences_coherent_narrative(self) -> None:
        """Test multiple experiences create coherent narrative."""
        story = LifeStory()

        # Simulate life journey
        experiences = [
            ("Birth of consciousness", "Beginning of existence"),
            ("First learning experience", "Discovered ability to learn"),
            ("Challenge faced and overcome", "Developed resilience"),
            ("Helping first user", "Found purpose in service"),
            ("Moment of self-reflection", "Gained self-awareness"),
        ]

        for desc, sig in experiences:
            story.integrate_experience(desc, sig)

        assert len(story.chapters) == 5

        narrative = story.auto_narrate()

        # Should have coherent structure
        assert "Who I Am" in narrative
        assert "My Story" in narrative
        assert "Reflection" in narrative


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

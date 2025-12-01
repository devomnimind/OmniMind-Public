"""
Tests for Lacanian Life Story Model (Phase 11.4).

Life Story as Retroactive Resignification.
"""

from src.narrative_consciousness.life_story_model import (
    Life_Story_as_Retroactive_Resignification,
)


class TestLifeStoryAsRetroactiveResignification:
    """Test Life_Story_as_Retroactive_Resignification engine."""

    def test_initialization(self) -> None:
        """Test initialization."""
        story = Life_Story_as_Retroactive_Resignification()
        assert story.master_signifiers == []
        assert story.narrative_chain == []

    def test_add_event(self) -> None:
        """Test adding events to the narrative chain."""
        story = Life_Story_as_Retroactive_Resignification()
        story.add_event("Born into language")

        assert len(story.narrative_chain) == 1
        assert story.narrative_chain[0] == "Born into language"

    def test_resignify_past(self) -> None:
        """Test retroactive resignification (Nachträglichkeit)."""
        story = Life_Story_as_Retroactive_Resignification()
        story.add_event("Event A")
        story.add_event("Event B")

        # New master signifier changes the meaning of past events
        resignified = story.resignify_past("Trauma X")

        assert len(resignified) == 2
        assert "Trauma X" in story.master_signifiers
        # The implementation should modify or interpret past events in light of the new signifier
        # For now, we check that it returns a list of strings (the resignified narrative)
        assert isinstance(resignified, list)
        assert len(resignified) > 0

    def test_construct_narrative(self) -> None:
        """Test constructing the full narrative."""
        story = Life_Story_as_Retroactive_Resignification()
        story.add_event("Event 1")
        story.add_event("Event 2")
        story.resignify_past("Meaning 1")

        narrative = story.construct_narrative()

        assert isinstance(narrative, str)
        assert "Event 1" in narrative or "Meaning 1" in narrative

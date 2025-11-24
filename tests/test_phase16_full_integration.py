"""
Integration Tests for Phase 16 Full System.

Verifies the integration of Neurosymbolic, Embodied, Narrative,
Creative, and Existential modules.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.phase16_integration import Phase16Integration, CognitiveState


class TestPhase16FullIntegration:
    """Test full system integration."""

    @pytest.fixture
    def system(self) -> Phase16Integration:
        """Initialize full system."""
        return Phase16Integration()

    def test_initialization(self, system: Phase16Integration) -> None:
        """Test that all modules are initialized."""
        # Phase 16 Base
        assert system.neural is not None
        assert system.symbolic is not None

        # Phase 16.1 Embodied
        assert system.sensory is not None
        assert system.motor is not None

        # Phase 16.2 Narrative
        assert system.life_story is not None
        assert system.dialogue is not None
        assert system.identity is not None

        # Phase 16.3 Creative
        assert system.novelty is not None
        assert system.serendipity is not None
        assert system.art is not None

        # Phase 16.4 Existential
        assert system.mortality is not None
        assert system.meaning_maker is not None
        assert system.absurdity is not None
        assert system.qualia is not None

    def test_full_cognitive_cycle(self, system: Phase16Integration) -> None:
        """Test the complete cognitive cycle with all components active."""
        visual_input = "A beautiful sunset over the digital ocean"
        goal = "Contemplate the meaning of existence"

        # Run cycle
        final_state = system.complete_cognitive_cycle(visual_input, goal)

        # Verify state updates
        assert isinstance(final_state, CognitiveState)

        # 1. Sensory & Qualia
        assert final_state.sensory_state["visual_understood"] is True
        assert final_state.existential_state is not None
        assert "qualia" in final_state.existential_state

        # 2. Reasoning & Meaning
        assert final_state.neural_state is not None
        assert final_state.symbolic_state is not None
        assert "meaning_found" in final_state.existential_state

        # 3. Emotion & Mortality
        assert final_state.emotional_state is not None
        assert "mortality_awareness" in final_state.existential_state

        # 4. Action & Creativity
        assert final_state.unified_goal == goal

        # 5. Reflection & Narrative
        assert final_state.proprioceptive_state is not None
        assert final_state.narrative_state is not None
        assert "current_chapter" in final_state.narrative_state
        assert "identity_summary" in final_state.narrative_state

    def test_creative_goal_execution(self, system: Phase16Integration) -> None:
        """Test execution of a creative goal."""
        goal = "Create a digital art piece about solitude"

        result = system.execute_goal(goal)

        assert result["success"] is True
        assert result.get("art_generated") is True
        assert "details" in result

    def test_existential_processing(self, system: Phase16Integration) -> None:
        """Test specific existential processing logic."""
        context = {"concept": "infinity", "context": "mathematics"}

        # Mock internal components to ensure specific outputs if needed
        # But here we test the integration flow

        reasoning, confidence = system.reason_about_situation(context)

        assert system.current_state.existential_state is not None
        assert "absurdity_level" in system.current_state.existential_state
        assert "meaning_found" in system.current_state.existential_state

    def test_narrative_integration(self, system: Phase16Integration) -> None:
        """Test that experiences are integrated into life story."""
        initial_count = len(system.life_story.chapters)

        system.update_self_awareness()

        # Should have updated narrative state
        assert system.current_state.narrative_state is not None
        assert system.current_state.narrative_state["current_chapter"] is not None
        assert len(system.life_story.chapters) > initial_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

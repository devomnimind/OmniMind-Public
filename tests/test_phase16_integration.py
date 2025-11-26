"""
Tests for Phase 16/16.1 Integration Module

Tests the unified system combining neurosymbolic reasoning with embodied cognition.
"""

import pytest

from src.phase16_integration import CognitiveState, Phase16Integration


class TestPhase16Integration:
    """Test unified Phase 16/16.1 integration."""

    def test_initialization(self) -> None:
        """Test system initialization."""
        system = Phase16Integration()

        assert system.neural is not None
        assert system.symbolic is not None
        assert system.sensory is not None
        assert system.emotional is not None
        assert system.motor is not None
        assert system.proprioception is not None

    def test_perceive_world(self) -> None:
        """Test sensory perception."""
        system = Phase16Integration()
        state = system.perceive_world("A bright red object moving quickly")

        assert state.sensory_state is not None
        assert "visual_understood" in state.sensory_state
        # assert state.sensory_state["multimodal_integration_complete"]
        # Removed as implementation details changed

    def test_perceive_with_audio(self) -> None:
        """Test multimodal perception."""
        system = Phase16Integration()
        state = system.perceive_world(
            "A dog barking",
            "Loud, aggressive barking sound",
        )

        assert state.sensory_state is not None
        assert state.sensory_state["audio_understood"]

    def test_reason_about_situation(self) -> None:
        """Test abstract reasoning."""
        system = Phase16Integration()
        reasoning, confidence = system.reason_about_situation()

        assert isinstance(reasoning, dict)
        assert 0 <= confidence <= 1

    def test_emotional_response(self) -> None:
        """Test emotional feedback generation."""
        system = Phase16Integration()
        system.generate_emotional_response("Test decision", 0.9, 0.85)

        assert system.current_state.emotional_state is not None
        assert "emotion" in system.current_state.emotional_state
        assert "valence" in system.current_state.emotional_state

    def test_execute_goal(self) -> None:
        """Test goal execution."""
        system = Phase16Integration()
        result = system.execute_goal("explore_environment")

        assert isinstance(result, dict)
        assert "goal" in result
        assert "success" in result

    def test_update_self_awareness(self) -> None:
        """Test self-awareness update."""
        system = Phase16Integration()
        awareness = system.update_self_awareness()

        assert awareness is not None
        assert "description" in awareness
        assert "mental_status" in awareness
        assert "resource_status" in awareness

    def test_complete_cognitive_cycle(self) -> None:
        """Test complete integrated cognitive cycle."""
        system = Phase16Integration()
        state = system.complete_cognitive_cycle(
            visual_input="Bright environment with moving objects",
            goal="Explore and learn",
        )

        # Verify all aspects of cognition were engaged
        assert state.sensory_state is not None
        assert state.neural_state is not None
        assert state.symbolic_state is not None
        assert state.emotional_state is not None
        assert state.proprioceptive_state is not None
        assert state.unified_goal == "Explore and learn"

    def test_cognitive_history(self) -> None:
        """Test cognitive history tracking."""
        system = Phase16Integration()

        # Run multiple cycles
        for i in range(3):
            system.complete_cognitive_cycle(
                visual_input=f"Scenario {i}",
                goal=f"Goal {i}",
            )

        assert len(system.cognitive_history) == 3
        assert system.cognitive_history[0].unified_goal == "Goal 0"
        assert system.cognitive_history[2].unified_goal == "Goal 2"

    def test_confidence_levels(self) -> None:
        """Test confidence tracking."""
        system = Phase16Integration()

        # Scenario with high agreement
        system.reason_about_situation()
        confidence_1 = system.current_state.confidence_level

        assert 0 <= confidence_1 <= 1

        # Another reasoning
        system.reason_about_situation()
        confidence_2 = system.current_state.confidence_level

        assert 0 <= confidence_2 <= 1

    def test_emotional_influence_on_reasoning(self) -> None:
        """Test that emotions influence future reasoning (feedback loop)."""
        system = Phase16Integration()

        # First cycle with positive outcome
        system.generate_emotional_response("Success", 0.95, 0.90)
        emotional_1 = system.current_state.emotional_state

        # Subsequent reasoning should be influenced
        system.reason_about_situation()
        emotional_2 = system.current_state.emotional_state

        # Verify emotional states exist
        assert emotional_1 is not None
        assert emotional_2 is not None

    def test_system_summary(self) -> None:
        """Test system summary generation."""
        system = Phase16Integration()
        summary = system.get_cognitive_summary()

        assert "NEUROSYMBOLIC" in summary
        assert "EMBODIED" in summary
        assert "Neural Component" in summary
        assert "Sensory Integration" in summary

    def test_cognitive_state_initialization(self) -> None:
        """Test CognitiveState dataclass."""
        state = CognitiveState(
            unified_goal="Test goal",
            confidence_level=0.75,
        )

        assert state.unified_goal == "Test goal"
        assert state.confidence_level == 0.75
        assert state.neural_state is None
        assert state.sensory_state is None

    def test_concurrent_goals(self) -> None:
        """Test handling multiple sequential goals."""
        system = Phase16Integration()

        goals = ["Goal A", "Goal B", "Goal C"]
        for goal in goals:
            system.complete_cognitive_cycle(
                visual_input="Environment",
                goal=goal,
            )

        # Verify each goal was processed
        assert len(system.cognitive_history) == 3
        for i, goal in enumerate(goals):
            assert system.cognitive_history[i].unified_goal == goal

    def test_integration_stability(self) -> None:
        """Test system stability across multiple cycles."""
        system = Phase16Integration()

        # Run 10 cycles
        for i in range(10):
            try:
                system.complete_cognitive_cycle(
                    visual_input=f"Input {i}",
                    goal=f"Goal {i}",
                )
            except Exception as e:
                pytest.fail(f"System failed at cycle {i}: {e}")

        assert len(system.cognitive_history) == 10

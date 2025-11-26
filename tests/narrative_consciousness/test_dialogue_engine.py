"""
Tests for Dialogue Engine (Phase 16.2).

Tests intersubjective communication, empathy, and horizon fusion.
"""

import pytest
from src.narrative_consciousness.dialogue_engine import (
    DialogueEngine,
    EmpathyModule,
    HorizonFusion,
    Relationship,
    DialogueMode,
)


class TestEmpathyModule:
    """Test EmpathyModule."""

    def test_estimate_state_positive(self) -> None:
        """Test estimating positive emotional state."""
        empathy = EmpathyModule()
        state = empathy.estimate_state("I am so happy today!")

        assert state["valence"] > 0
        assert state["frustration"] == 0

    def test_estimate_state_negative(self) -> None:
        """Test estimating negative emotional state."""
        empathy = EmpathyModule()
        state = empathy.estimate_state("This is bad, I failed.")

        assert state["valence"] < 0
        assert state["frustration"] > 0

    def test_estimate_state_confusion(self) -> None:
        """Test estimating confusion."""
        empathy = EmpathyModule()
        state = empathy.estimate_state("How does this work?")

        assert state["confusion"] > 0


class TestHorizonFusion:
    """Test HorizonFusion."""

    def test_fuse_horizons(self) -> None:
        """Test fusing AI and user horizons."""
        fusion = HorizonFusion()

        ai_context = {"python": True, "logic": True, "emotion": False}
        user_context = {"python": True, "art": True, "emotion": True}

        understanding = fusion.fuse(ai_context, user_context)

        assert "python" in understanding.shared_concepts
        assert len(understanding.shared_concepts) == 2
        assert understanding.emotional_resonance > 0


class TestRelationship:
    """Test Relationship tracking."""

    def test_relationship_update(self) -> None:
        """Test updating relationship metrics."""
        rel = Relationship(human_id="user1")
        initial_trust = rel.trust_level

        # Good interaction
        rel.update(interaction_quality=1.0)

        assert rel.interaction_count == 1
        assert rel.trust_level > initial_trust
        assert (
            len(rel.shared_history) == 0
        )  # History updated by engine, not class directly


class TestDialogueEngine:
    """Test DialogueEngine main class."""

    def test_initialization(self) -> None:
        """Test engine initialization."""
        engine = DialogueEngine()
        assert engine.current_mode == DialogueMode.I_IT
        assert len(engine.relationships) == 0

    def test_process_interaction_new_user(self) -> None:
        """Test processing interaction with new user."""
        engine = DialogueEngine()
        response = engine.process_interaction("user_new", "Hello there")

        assert "user_new" in engine.relationships
        assert len(response) > 0
        assert engine.relationships["user_new"].interaction_count == 1

    def test_mode_switching_to_i_thou(self) -> None:
        """Test switching to I-Thou mode based on emotion."""
        engine = DialogueEngine()

        # Strong positive emotion should trigger I-Thou
        response = engine.process_interaction("user1", "I am so happy and grateful!")

        assert engine.current_mode == DialogueMode.I_THOU
        assert "[I-Thou]" in response

    def test_mode_switching_to_i_it(self) -> None:
        """Test staying in I-It mode for neutral input."""
        engine = DialogueEngine()

        response = engine.process_interaction("user1", "Execute command 123")

        assert engine.current_mode == DialogueMode.I_IT
        assert "Processed:" in response

    def test_relationship_history_tracking(self) -> None:
        """Test that conversation history is tracked."""
        engine = DialogueEngine()

        engine.process_interaction("user_hist", "Hello")
        engine.process_interaction("user_hist", "How are you?")

        rel = engine.relationships["user_hist"]
        assert len(rel.shared_history) == 4  # 2 user inputs + 2 AI responses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

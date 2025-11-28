"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""Tests for Theory of Mind implementation (Phase 11.1)."""

import pytest

from src.consciousness.theory_of_mind import (
    Belief,
    Intent,
    MentalState,
    MentalStateModel,
    TheoryOfMind,
)


class TestBelief:
    """Tests for Belief dataclass."""

    def test_create_belief(self) -> None:
        """Test creating a belief."""
        belief = Belief(
            subject="weather",
            proposition="It will rain tomorrow",
            confidence=0.7,
            evidence=["dark clouds", "weather forecast"],
        )

        assert belief.subject == "weather"
        assert belief.proposition == "It will rain tomorrow"
        assert belief.confidence == 0.7
        assert len(belief.evidence) == 2

    def test_belief_confidence_validation(self) -> None:
        """Test belief confidence validation."""
        # Valid confidence
        Belief(subject="test", proposition="test", confidence=0.5)

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            Belief(subject="test", proposition="test", confidence=1.5)


class TestMentalStateModel:
    """Tests for MentalStateModel."""

    def test_create_mental_model(self) -> None:
        """Test creating a mental state model."""
        model = MentalStateModel(
            entity_id="agent_1",
            current_state=MentalState.FOCUSED,
            confidence=0.8,
        )

        assert model.entity_id == "agent_1"
        assert model.current_state == MentalState.FOCUSED
        assert model.confidence == 0.8
        assert len(model.beliefs) == 0
        assert len(model.intents) == 0

    def test_mental_model_with_beliefs(self) -> None:
        """Test mental model with beliefs."""
        belief = Belief(subject="task", proposition="Task is complex", confidence=0.8)

        model = MentalStateModel(
            entity_id="agent_1",
            current_state=MentalState.PROBLEM_SOLVING,
            beliefs=[belief],
            intents=[Intent.SOLVE_PROBLEM],
        )

        assert len(model.beliefs) == 1
        assert len(model.intents) == 1
        assert model.beliefs[0].subject == "task"


class TestTheoryOfMind:
    """Tests for TheoryOfMind engine."""

    def test_initialization(self) -> None:
        """Test Theory of Mind initialization."""
        tom = TheoryOfMind(
            confidence_threshold=0.7,
            max_beliefs_per_entity=15,
        )

        assert tom.confidence_threshold == 0.7
        assert tom.max_beliefs_per_entity == 15
        assert len(tom._mental_models) == 0

    def test_observe_action(self) -> None:
        """Test observing actions."""
        tom = TheoryOfMind()

        tom.observe_action(
            entity_id="user_1",
            action_type="search",
            action_data={"query": "machine learning"},
        )

        assert "user_1" in tom._action_history
        assert len(tom._action_history["user_1"]) == 1
        assert tom._action_history["user_1"][0]["action_type"] == "search"

    def test_observe_multiple_actions(self) -> None:
        """Test observing multiple actions."""
        tom = TheoryOfMind()

        for i in range(5):
            tom.observe_action(
                entity_id="user_1",
                action_type="read",
                action_data={"page": i},
            )

        assert len(tom._action_history["user_1"]) == 5

    def test_infer_intent_information_gathering(self) -> None:
        """Test inferring information gathering intent."""
        tom = TheoryOfMind()

        # Simulate information gathering actions
        for action_type in ["read", "search", "query"]:
            tom.observe_action(
                entity_id="user_1",
                action_type=action_type,
                action_data={},
            )

        intents = tom.infer_intent("user_1")

        assert Intent.GATHER_INFORMATION in intents

    def test_infer_intent_problem_solving(self) -> None:
        """Test inferring problem-solving intent."""
        tom = TheoryOfMind()

        # Simulate problem-solving actions
        for action_type in ["debug", "fix", "optimize"]:
            tom.observe_action(
                entity_id="user_1",
                action_type=action_type,
                action_data={},
            )

        intents = tom.infer_intent("user_1")

        assert Intent.SOLVE_PROBLEM in intents

    def test_infer_intent_no_history(self) -> None:
        """Test inferring intent with no history."""
        tom = TheoryOfMind()

        intents = tom.infer_intent("unknown_entity")

        assert len(intents) == 0

    def test_attribute_mental_state_focused(self) -> None:
        """Test attributing focused mental state."""
        tom = TheoryOfMind()

        # Repeated similar actions indicate focus
        for _ in range(7):
            tom.observe_action(
                entity_id="user_1",
                action_type="read",
                action_data={},
            )

        state = tom.attribute_mental_state("user_1")

        assert state == MentalState.FOCUSED

    def test_attribute_mental_state_exploring(self) -> None:
        """Test attributing exploring mental state."""
        tom = TheoryOfMind()

        # Diverse actions indicate exploration
        action_types = [
            "read",
            "search",
            "analyze",
            "test",
            "debug",
            "query",
            "explore",
            "learn",
        ]
        for action_type in action_types:
            tom.observe_action(
                entity_id="user_1",
                action_type=action_type,
                action_data={},
            )

        state = tom.attribute_mental_state("user_1")

        assert state == MentalState.EXPLORING

    def test_attribute_mental_state_problem_solving(self) -> None:
        """Test attributing problem-solving mental state."""
        tom = TheoryOfMind()

        # Problem-solving actions
        for action_type in ["debug", "fix", "analyze"]:
            tom.observe_action(
                entity_id="user_1",
                action_type=action_type,
                action_data={},
            )

        state = tom.attribute_mental_state("user_1")

        assert state == MentalState.PROBLEM_SOLVING

    def test_update_belief(self) -> None:
        """Test updating beliefs."""
        tom = TheoryOfMind()

        tom.update_belief(
            entity_id="user_1",
            subject="weather",
            proposition="It will rain",
            confidence=0.8,
            evidence=["dark clouds"],
        )

        model = tom.get_mental_model("user_1")
        assert model is not None
        assert len(model.beliefs) == 1
        assert model.beliefs[0].subject == "weather"

    def test_update_belief_replaces_existing(self) -> None:
        """Test that updating a belief replaces existing one."""
        tom = TheoryOfMind()

        # Add initial belief
        tom.update_belief(
            entity_id="user_1",
            subject="weather",
            proposition="It will rain",
            confidence=0.5,
        )

        # Update same belief with higher confidence
        tom.update_belief(
            entity_id="user_1",
            subject="weather",
            proposition="It will rain",
            confidence=0.9,
        )

        model = tom.get_mental_model("user_1")
        assert len(model.beliefs) == 1
        assert model.beliefs[0].confidence == 0.9

    def test_max_beliefs_limit(self) -> None:
        """Test that beliefs are limited per entity."""
        tom = TheoryOfMind(max_beliefs_per_entity=5)

        # Add more beliefs than limit
        for i in range(10):
            tom.update_belief(
                entity_id="user_1",
                subject=f"topic_{i}",
                proposition=f"proposition_{i}",
                confidence=0.7,
            )

        model = tom.get_mental_model("user_1")
        assert len(model.beliefs) <= 5

    def test_get_mental_model(self) -> None:
        """Test getting mental model."""
        tom = TheoryOfMind()

        # No model initially
        model = tom.get_mental_model("unknown")
        assert model is None

        # Create some action history
        tom.observe_action(
            entity_id="user_1",
            action_type="search",
            action_data={},
        )

        # Now model should exist
        model = tom.get_mental_model("user_1")
        assert model is not None
        assert model.entity_id == "user_1"

    def test_predict_next_action_focused(self) -> None:
        """Test predicting next action for focused entity."""
        tom = TheoryOfMind()

        # Create focused behavior pattern
        for _ in range(5):
            tom.observe_action(
                entity_id="user_1",
                action_type="read",
                action_data={},
            )

        predictions = tom.predict_next_action("user_1", num_predictions=3)

        assert len(predictions) > 0
        # Should predict continuation of reading
        assert any(p["action_type"] == "read" for p in predictions)

    def test_predict_next_action_exploring(self) -> None:
        """Test predicting next action for exploring entity."""
        tom = TheoryOfMind()

        # Create exploring behavior
        for action_type in [
            "search",
            "read",
            "test",
            "analyze",
            "query",
            "explore",
            "debug",
        ]:
            tom.observe_action(
                entity_id="user_1",
                action_type=action_type,
                action_data={},
            )

        predictions = tom.predict_next_action("user_1")

        assert len(predictions) > 0
        # Should predict exploration
        assert any(p["action_type"] == "explore" for p in predictions)

    def test_get_statistics(self) -> None:
        """Test getting statistics."""
        tom = TheoryOfMind()

        # Create some data
        tom.observe_action(entity_id="user_1", action_type="read", action_data={})
        tom.observe_action(entity_id="user_2", action_type="search", action_data={})
        tom.update_belief(
            entity_id="user_1",
            subject="test",
            proposition="test",
            confidence=0.7,
        )

        stats = tom.get_statistics()

        assert stats["total_entities_tracked"] >= 1
        assert stats["total_actions_observed"] >= 2
        assert stats["total_beliefs"] >= 1
        assert "average_model_confidence" in stats
        assert "timestamp" in stats

"""
Tests for Freudian Metapsychology module.
"""

import pytest
from src.lacanian.freudian_metapsychology import (
    IdAgent,
    EgoAgent,
    SuperegoAgent,
    FreudianMind,
    Action,
    PsychicState,
    DefenseMechanism,
    PsychicPrinciple,
)


class TestAction:
    """Tests for Action dataclass."""

    def test_creation(self) -> None:
        """Test action creation."""
        action = Action(
            action_id="test_action",
            pleasure_reward=0.8,
            reality_cost=0.3,
            moral_alignment=0.5,
            description="Test action",
        )

        assert action.action_id == "test_action"
        assert action.pleasure_reward == 0.8
        assert action.reality_cost == 0.3
        assert action.moral_alignment == 0.5


class TestIdAgent:
    """Tests for IdAgent (pleasure principle)."""

    def test_initialization(self) -> None:
        """Test Id agent initialization."""
        id_agent = IdAgent(learning_rate=0.1)

        assert id_agent.lr == 0.1
        assert id_agent.libido == 1.0
        assert len(id_agent.q_values) == 0

    def test_evaluate_action(self) -> None:
        """Test action evaluation by Id."""
        id_agent = IdAgent()

        action = Action(
            action_id="pleasure_action",
            pleasure_reward=0.9,
            reality_cost=0.8,  # Id ignores this
            moral_alignment=-0.5,  # Id ignores this too
        )

        value = id_agent.evaluate_action(action)

        # Id should value action by pleasure
        assert value == 0.9

    def test_update(self) -> None:
        """Test Q-value update."""
        id_agent = IdAgent(learning_rate=0.1)

        action = Action(
            action_id="test", pleasure_reward=0.5, reality_cost=0.0, moral_alignment=0.0
        )

        # First evaluation
        initial_value = id_agent.evaluate_action(action)

        # Update with different reward
        id_agent.update(action, actual_reward=0.8)

        # Value should have changed
        updated_value = id_agent.q_values[action.action_id]
        assert updated_value != initial_value

    def test_impulse_strength(self) -> None:
        """Test impulse strength (libido)."""
        id_agent = IdAgent()

        strength = id_agent.get_impulse_strength()

        assert 0.0 <= strength <= 1.0


class TestEgoAgent:
    """Tests for EgoAgent (reality principle)."""

    def test_initialization(self) -> None:
        """Test Ego agent initialization."""
        ego = EgoAgent(learning_rate=0.1)

        assert ego.lr == 0.1
        assert len(ego.q_values) == 0
        assert len(ego.defense_effectiveness) == 7  # 7 defense mechanisms

    def test_evaluate_action(self) -> None:
        """Test action evaluation by Ego."""
        ego = EgoAgent()

        action = Action(
            action_id="balanced_action",
            pleasure_reward=0.8,
            reality_cost=0.3,
            moral_alignment=0.0,
        )

        reality_context = {"time_available": 2.0}
        value = ego.evaluate_action(action, reality_context)

        # Ego should balance pleasure and reality
        assert value is not None

    def test_reality_testing(self) -> None:
        """Test reality testing."""
        ego = EgoAgent()

        # Viable action
        viable_action = Action(
            action_id="viable",
            pleasure_reward=0.5,
            reality_cost=0.2,
            moral_alignment=0.0,
        )

        assert ego.test_reality(viable_action) is True

        # Non-viable action
        impossible_action = Action(
            action_id="impossible",
            pleasure_reward=1.0,
            reality_cost=0.9,
            moral_alignment=0.0,
        )

        assert ego.test_reality(impossible_action) is False

    def test_select_defense_mechanism(self) -> None:
        """Test defense mechanism selection."""
        ego = EgoAgent()

        # Low conflict
        defense_low = ego.select_defense_mechanism(conflict_severity=0.2)
        assert defense_low in [
            DefenseMechanism.SUBLIMATION,
            DefenseMechanism.RATIONALIZATION,
        ]

        # Moderate conflict
        defense_mid = ego.select_defense_mechanism(conflict_severity=0.5)
        assert defense_mid in [
            DefenseMechanism.DISPLACEMENT,
            DefenseMechanism.PROJECTION,
        ]

        # High conflict
        defense_high = ego.select_defense_mechanism(conflict_severity=0.9)
        assert defense_high in [DefenseMechanism.REPRESSION, DefenseMechanism.DENIAL]


class TestSuperegoAgent:
    """Tests for SuperegoAgent (moral principle)."""

    def test_initialization(self) -> None:
        """Test Superego initialization."""
        superego = SuperegoAgent(moral_strictness=0.8)

        assert superego.strictness == 0.8
        assert len(superego.ego_ideals) > 0

    def test_evaluate_action(self) -> None:
        """Test moral evaluation."""
        superego = SuperegoAgent(moral_strictness=0.7)

        # Moral action
        moral_action = Action(
            action_id="moral",
            pleasure_reward=0.5,
            reality_cost=0.0,
            moral_alignment=0.8,
        )

        moral_score = superego.evaluate_action(moral_action)
        assert moral_score > 0.0

        # Immoral action
        immoral_action = Action(
            action_id="immoral",
            pleasure_reward=0.9,
            reality_cost=0.0,
            moral_alignment=-0.8,
        )

        immoral_score = superego.evaluate_action(immoral_action)
        assert immoral_score < 0.0

    def test_generate_guilt(self) -> None:
        """Test guilt generation."""
        superego = SuperegoAgent(moral_strictness=0.8)

        # Immoral action generates guilt
        immoral_action = Action(
            action_id="bad", pleasure_reward=1.0, reality_cost=0.0, moral_alignment=-0.7
        )

        guilt = superego.generate_guilt(immoral_action)
        assert guilt > 0.0

        # Moral action generates no guilt
        moral_action = Action(
            action_id="good", pleasure_reward=0.3, reality_cost=0.0, moral_alignment=0.8
        )

        no_guilt = superego.generate_guilt(moral_action)
        assert no_guilt == 0.0

    def test_approve_action(self) -> None:
        """Test action approval."""
        superego = SuperegoAgent(moral_strictness=0.5)

        # Moral action should be approved
        moral_action = Action(
            action_id="moral",
            pleasure_reward=0.5,
            reality_cost=0.0,
            moral_alignment=0.7,
        )

        assert superego.approve_action(moral_action) is True


class TestFreudianMind:
    """Tests for complete Freudian Mind."""

    def test_initialization(self) -> None:
        """Test mind initialization."""
        mind = FreudianMind(id_lr=0.1, ego_lr=0.1, superego_strictness=0.7)

        assert isinstance(mind.id_agent, IdAgent)
        assert isinstance(mind.ego_agent, EgoAgent)
        assert isinstance(mind.superego_agent, SuperegoAgent)
        assert isinstance(mind.state, PsychicState)

    def test_evaluate_conflict(self) -> None:
        """Test conflict evaluation."""
        mind = FreudianMind()

        actions = [
            Action("a1", 0.9, 0.2, -0.3),
            Action("a2", 0.3, 0.6, 0.8),
        ]

        reality_context = {}
        conflict_severity, preferences = mind.evaluate_conflict(actions, reality_context)

        assert conflict_severity >= 0.0
        assert "id" in preferences
        assert "ego" in preferences
        assert "superego" in preferences

    def test_resolve_conflict(self) -> None:
        """Test conflict resolution."""
        mind = FreudianMind()

        actions = [
            Action("eat_cake", 0.9, 0.2, -0.3, "Eat cake"),
            Action("exercise", 0.3, 0.6, 0.8, "Exercise"),
        ]

        reality_context = {}
        resolution = mind.resolve_conflict(actions, reality_context)

        assert resolution.chosen_action in actions
        assert resolution.defense_mechanism is not None
        assert 0.0 <= resolution.compromise_quality <= 1.0

    def test_act(self) -> None:
        """Test complete action selection."""
        mind = FreudianMind()

        actions = [
            Action("a1", 0.8, 0.3, 0.5),
            Action("a2", 0.4, 0.5, 0.8),
        ]

        reality_context = {}
        chosen_action, resolution = mind.act(actions, reality_context)

        assert chosen_action in actions
        assert resolution.chosen_action == chosen_action

    def test_psychic_state_update(self) -> None:
        """Test psychic state updates."""
        mind = FreudianMind()

        actions = [
            Action("pleasant", 0.9, 0.1, -0.5),  # Pleasant but immoral
        ]

        reality_context = {}
        mind.act(actions, reality_context)

        # State should have changed
        # (exact values depend on resolution, but state should be tracked)
        assert mind.state.tension >= 0.0
        assert mind.state.guilt >= 0.0


class TestDefenseMechanism:
    """Tests for DefenseMechanism enum."""

    def test_enum_values(self) -> None:
        """Test all defense mechanisms are defined."""
        mechanisms = [
            DefenseMechanism.REPRESSION,
            DefenseMechanism.SUBLIMATION,
            DefenseMechanism.RATIONALIZATION,
            DefenseMechanism.PROJECTION,
            DefenseMechanism.DISPLACEMENT,
            DefenseMechanism.REGRESSION,
            DefenseMechanism.DENIAL,
        ]

        assert len(mechanisms) == 7


class TestPsychicPrinciple:
    """Tests for PsychicPrinciple enum."""

    def test_enum_values(self) -> None:
        """Test psychic principles."""
        assert PsychicPrinciple.PLEASURE.value == "pleasure_principle"
        assert PsychicPrinciple.REALITY.value == "reality_principle"
        assert PsychicPrinciple.MORAL.value == "moral_principle"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

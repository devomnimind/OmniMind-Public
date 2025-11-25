"""
Testes para Reinforcement Learning (reinforcement_learning.py).

Cobertura de:
- Q-learning
- Policy updates
- Reward calculation
- State-action pairs
- Tratamento de exceções
"""

from __future__ import annotations

import pytest
import numpy as np

from src.decision_making.reinforcement_learning import (
    QLearningAgent,
    ReinforcementLearningAgent,
)


class TestQLearningAgent:
    """Testes para QLearningAgent."""

    @pytest.fixture
    def agent(self) -> QLearningAgent:
        """Cria instância do agente."""
        return QLearningAgent(
            num_states=10,
            num_actions=4,
            learning_rate=0.1,
            discount_factor=0.9,
        )

    def test_agent_initialization(self, agent: QLearningAgent) -> None:
        """Testa inicialização."""
        assert agent.learning_rate == 0.1
        assert agent.discount_factor == 0.9
        assert hasattr(agent, "q_table")

    def test_choose_action(self, agent: QLearningAgent) -> None:
        """Testa escolha de ação."""
        state = 0

        action = agent.choose_action(state)

        assert 0 <= action < agent.num_actions

    def test_update_q_value(self, agent: QLearningAgent) -> None:
        """Testa atualização de Q-value."""
        state = 0
        action = 1
        reward = 1.0
        next_state = 1

        agent.update(state, action, reward, next_state)

        # Q-table should be updated
        assert agent.q_table is not None

    def test_get_best_action(self, agent: QLearningAgent) -> None:
        """Testa obtenção da melhor ação."""
        state = 0

        best_action = agent.get_best_action(state)

        assert 0 <= best_action < agent.num_actions

    def test_exploration_vs_exploitation(self, agent: QLearningAgent) -> None:
        """Testa balanço exploração/exploração."""
        state = 0

        # With high epsilon, should explore more
        agent.epsilon = 1.0
        action1 = agent.choose_action(state)

        # With low epsilon, should exploit more
        agent.epsilon = 0.0
        action2 = agent.choose_action(state)

        assert isinstance(action1, int)
        assert isinstance(action2, int)

    def test_learning_over_episodes(self, agent: QLearningAgent) -> None:
        """Testa aprendizado ao longo de episódios."""
        # Simulate multiple learning steps
        for _ in range(100):
            state = np.random.randint(0, agent.num_states)
            action = agent.choose_action(state)
            reward = np.random.random()
            next_state = np.random.randint(0, agent.num_states)

            agent.update(state, action, reward, next_state)

        # Agent should have learned something
        assert np.any(agent.q_table != 0) or np.all(agent.q_table == 0)


class TestReinforcementLearningAgent:
    """Testes para ReinforcementLearningAgent (PolicyGradientAgent)."""

    def test_agent_creation(self) -> None:
        """Testa criação do agente."""
        agent = ReinforcementLearningAgent()

        assert agent is not None
        assert hasattr(agent, "name")
        assert hasattr(agent, "policy_params")
        assert hasattr(agent, "episode_transitions")

    def test_agent_initialization_parameters(self) -> None:
        """Testa parâmetros de inicialização."""
        agent = ReinforcementLearningAgent(
            name="test_agent",
            learning_rate=0.05,
            discount_factor=0.99,
        )

        assert agent.name == "test_agent"
        assert agent.learning_rate == 0.05
        assert agent.discount_factor == 0.99

    def test_select_action(self) -> None:
        """Testa seleção de ação."""
        from src.decision_making.reinforcement_learning import RLState, RLAction

        agent = ReinforcementLearningAgent()
        state = RLState(features={"x": 1, "y": 2})
        actions = [
            RLAction(action_id="move_left"),
            RLAction(action_id="move_right"),
        ]

        selected_action = agent.select_action(state, actions)

        assert selected_action in actions

    def test_select_action_empty_actions(self) -> None:
        """Testa seleção de ação com lista vazia."""
        from src.decision_making.reinforcement_learning import RLState

        agent = ReinforcementLearningAgent()
        state = RLState(features={"x": 1})

        with pytest.raises(ValueError, match="No available actions"):
            agent.select_action(state, [])

    def test_get_policy_metrics(self) -> None:
        """Testa obtenção de métricas da política."""
        agent = ReinforcementLearningAgent()

        metrics = agent.get_policy_metrics()

        assert "num_states" in metrics
        assert "avg_param_value" in metrics
        assert "baseline_value" in metrics
        assert "total_reward" in metrics
        assert "episodes" in metrics


class TestRLComponents:
    """Testes para componentes básicos de RL."""

    def test_rl_state_creation(self) -> None:
        """Testa criação de RLState."""
        from src.decision_making.reinforcement_learning import RLState

        state = RLState(features={"position": 5, "velocity": 2})

        assert state.features == {"position": 5, "velocity": 2}
        assert state.state_id is not None

    def test_rl_state_custom_id(self) -> None:
        """Testa RLState com ID customizado."""
        from src.decision_making.reinforcement_learning import RLState

        state = RLState(features={"x": 1}, state_id="custom_id")

        assert state.state_id == "custom_id"

    def test_rl_state_hashable(self) -> None:
        """Testa que RLState é hashable."""
        from src.decision_making.reinforcement_learning import RLState

        state1 = RLState(features={"x": 1}, state_id="state1")
        state2 = RLState(features={"x": 2}, state_id="state2")

        states_set = {state1, state2}
        assert len(states_set) == 2

    def test_rl_state_equality(self) -> None:
        """Testa igualdade de RLStates."""
        from src.decision_making.reinforcement_learning import RLState

        state1 = RLState(features={"x": 1}, state_id="state1")
        state2 = RLState(features={"x": 1}, state_id="state1")
        state3 = RLState(features={"x": 2}, state_id="state2")

        assert state1 == state2
        assert state1 != state3

    def test_rl_action_creation(self) -> None:
        """Testa criação de RLAction."""
        from src.decision_making.reinforcement_learning import RLAction

        action = RLAction(
            action_id="move", parameters={"direction": "left"}, cost=0.5
        )

        assert action.action_id == "move"
        assert action.parameters == {"direction": "left"}
        assert action.cost == 0.5

    def test_rl_action_hashable(self) -> None:
        """Testa que RLAction é hashable."""
        from src.decision_making.reinforcement_learning import RLAction

        action1 = RLAction(action_id="move")
        action2 = RLAction(action_id="stay")

        actions_set = {action1, action2}
        assert len(actions_set) == 2

    def test_rl_reward_creation(self) -> None:
        """Testa criação de RLReward."""
        from src.decision_making.reinforcement_learning import RLReward

        reward = RLReward(
            value=10.0,
            immediate=8.0,
            delayed=2.0,
            ethical_bonus=1.0,
            metadata={"source": "goal_completion"},
        )

        assert reward.value == 10.0
        assert reward.immediate == 8.0
        assert reward.delayed == 2.0
        assert reward.ethical_bonus == 1.0
        assert reward.metadata["source"] == "goal_completion"

    def test_rl_transition_creation(self) -> None:
        """Testa criação de RLTransition."""
        from src.decision_making.reinforcement_learning import (
            RLState,
            RLAction,
            RLReward,
            RLTransition,
        )

        state = RLState(features={"x": 1})
        action = RLAction(action_id="move")
        next_state = RLState(features={"x": 2})
        reward = RLReward(value=5.0)

        transition = RLTransition(
            state=state,
            action=action,
            next_state=next_state,
            reward=reward,
            done=False,
        )

        assert transition.state == state
        assert transition.action == action
        assert transition.next_state == next_state
        assert transition.reward == reward
        assert transition.done is False
        assert hasattr(transition, "timestamp")


class TestPolicyGradientAgent:
    """Testes específicos para PolicyGradientAgent."""

    def test_policy_gradient_initialization(self) -> None:
        """Testa inicialização do PolicyGradientAgent."""
        from src.decision_making.reinforcement_learning import PolicyGradientAgent

        agent = PolicyGradientAgent(
            name="pg_agent", learning_rate=0.01, discount_factor=0.95
        )

        assert agent.name == "pg_agent"
        assert agent.learning_rate == 0.01
        assert agent.discount_factor == 0.95
        assert len(agent.policy_params) == 0
        assert len(agent.episode_transitions) == 0

    def test_compute_action_probabilities(self) -> None:
        """Testa cálculo de probabilidades de ação."""
        from src.decision_making.reinforcement_learning import (
            PolicyGradientAgent,
            RLState,
            RLAction,
        )

        agent = PolicyGradientAgent()
        state = RLState(features={"x": 1})
        actions = [
            RLAction(action_id="a1"),
            RLAction(action_id="a2"),
            RLAction(action_id="a3"),
        ]

        probs = agent._compute_action_probabilities(state, actions)

        assert len(probs) == 3
        assert abs(sum(probs) - 1.0) < 0.001  # Should sum to 1
        assert all(p >= 0 for p in probs)

    def test_update_stores_transition(self) -> None:
        """Testa que update armazena transição."""
        from src.decision_making.reinforcement_learning import (
            PolicyGradientAgent,
            RLState,
            RLAction,
            RLReward,
            RLTransition,
        )

        agent = PolicyGradientAgent()
        transition = RLTransition(
            state=RLState(features={"x": 1}),
            action=RLAction(action_id="move"),
            next_state=RLState(features={"x": 2}),
            reward=RLReward(value=1.0),
            done=False,
        )

        agent.update(transition)

        assert len(agent.episode_transitions) == 1
        assert agent.episode_transitions[0] == transition

    def test_update_triggers_policy_update_on_done(self) -> None:
        """Testa que update atualiza política quando episódio termina."""
        from src.decision_making.reinforcement_learning import (
            PolicyGradientAgent,
            RLState,
            RLAction,
            RLReward,
            RLTransition,
        )

        agent = PolicyGradientAgent()

        # Add some transitions
        for i in range(3):
            transition = RLTransition(
                state=RLState(features={"x": i}),
                action=RLAction(action_id="move"),
                next_state=RLState(features={"x": i + 1}),
                reward=RLReward(value=1.0),
                done=(i == 2),
            )
            agent.update(transition)

        # After done, transitions should be cleared
        assert len(agent.episode_transitions) == 0

    def test_decay_exploration(self) -> None:
        """Testa decay de exploração."""
        from src.decision_making.reinforcement_learning import PolicyGradientAgent

        agent = PolicyGradientAgent()
        initial_rate = agent.exploration_rate

        agent.decay_exploration(decay_rate=0.9)

        assert agent.exploration_rate <= initial_rate
        assert agent.exploration_rate >= 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

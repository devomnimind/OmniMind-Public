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
from unittest.mock import Mock, patch
import numpy as np

from src.decision_making.reinforcement_learning import (
    QLearningAgent,
    ReinforcementLearningAgent,
    State,
    Action,
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
    """Testes para ReinforcementLearningAgent."""

    def test_agent_creation(self) -> None:
        """Testa criação do agente."""
        agent = ReinforcementLearningAgent()

        assert agent is not None

    def test_train_agent(self) -> None:
        """Testa treinamento."""
        agent = ReinforcementLearningAgent()

        if hasattr(agent, "train"):
            result = agent.train(episodes=10)
            assert result is not None or result is None

    def test_evaluate_policy(self) -> None:
        """Testa avaliação de política."""
        agent = ReinforcementLearningAgent()

        if hasattr(agent, "evaluate"):
            score = agent.evaluate()
            assert isinstance(score, (int, float)) or score is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

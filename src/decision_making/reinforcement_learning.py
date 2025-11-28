import math
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import structlog

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

"""
Reinforcement Learning-based Decision Making for OmniMind.

This module implements RL agents that can:
- Learn optimal policies from experience
- Adapt to dynamic environments
- Balance exploration and exploitation
- Integrate with decision trees and ethical frameworks

Author: OmniMind Project
License: MIT
"""


logger = structlog.get_logger(__name__)


class RLState:
    """Represents a state in the RL environment."""

    def __init__(self, features: Dict[str, Any], state_id: Optional[str] = None):
        """
        Initialize RL state.

        Args:
            features: Dictionary of state features
            state_id: Optional unique identifier
        """
        self.features = features
        self.state_id = state_id or self._compute_state_id()

    def _compute_state_id(self) -> str:
        """Compute state ID from features."""
        # Simple hash of sorted feature items
        items = sorted(self.features.items())
        return str(hash(tuple(items)))

    def __hash__(self) -> int:
        """Make state hashable for use in Q-tables."""
        return hash(self.state_id)

    def __eq__(self, other: object) -> bool:
        """Check state equality."""
        if not isinstance(other, RLState):
            return False
        return self.state_id == other.state_id


@dataclass
class RLAction:
    """Represents an action in the RL environment."""

    action_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0

    def __hash__(self) -> int:
        """Make action hashable."""
        return hash(self.action_id)

    def __eq__(self, other: object) -> bool:
        """Check action equality."""
        if not isinstance(other, RLAction):
            return False
        return self.action_id == other.action_id


@dataclass
class RLReward:
    """Represents a reward signal."""

    value: float
    immediate: float = 0.0
    delayed: float = 0.0
    ethical_bonus: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RLTransition:
    """Represents a state transition."""

    state: RLState
    action: RLAction
    next_state: RLState
    reward: RLReward
    done: bool
    timestamp: float = field(default_factory=time.time)


class RLEnvironment(ABC):
    """Abstract base class for RL environments."""

    @abstractmethod
    def reset(self) -> RLState:
        """Reset environment to initial state."""

    @abstractmethod
    def step(self, action: RLAction) -> Tuple[RLState, RLReward, bool]:
        """
        Execute action and return next state, reward, and done flag.

        Args:
            action: Action to execute

        Returns:
            Tuple of (next_state, reward, done)
        """

    @abstractmethod
    def get_available_actions(self, state: RLState) -> List[RLAction]:
        """Get available actions for current state."""


class RLAgent(ABC):
    """Abstract base class for RL agents."""

    def __init__(
        self,
        name: str,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.1,
    ):
        """
        Initialize RL agent.

        Args:
            name: Agent name
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            exploration_rate: Exploration rate (epsilon)
        """
        self.name = name
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.logger = logger.bind(agent_name=name)
        self.episode_count = 0
        self.total_reward = 0.0

    @abstractmethod
    def select_action(self, state: RLState, available_actions: List[RLAction]) -> RLAction:
        """Select action for given state."""

    @abstractmethod
    def update(self, transition: RLTransition) -> None:
        """Update agent based on transition."""

    def decay_exploration(self, decay_rate: float = 0.995) -> None:
        """Decay exploration rate over time."""
        self.exploration_rate *= decay_rate
        self.exploration_rate = max(0.01, self.exploration_rate)


class PolicyGradientAgent(RLAgent):
    """
    Policy gradient agent with parametric policy.

    Features:
    - Direct policy optimization
    - Stochastic policy representation
    - Suitable for continuous action spaces
    """

    def __init__(
        self,
        name: str = "policy_gradient",
        learning_rate: float = 0.01,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.0,  # Not used in policy gradient
    ):
        """Initialize policy gradient agent."""
        super().__init__(name, learning_rate, discount_factor, exploration_rate)
        self.policy_params: Dict[str, Dict[str, float]] = {}
        self.episode_transitions: List[RLTransition] = []
        self.baseline_value = 0.0

    def select_action(self, state: RLState, available_actions: List[RLAction]) -> RLAction:
        """Select action using stochastic policy."""
        if not available_actions:
            raise ValueError("No available actions")

        # Compute action probabilities
        probs = self._compute_action_probabilities(state, available_actions)

        # Sample action according to probabilities
        cumsum = 0.0
        r = random.random()
        for action, prob in zip(available_actions, probs):
            cumsum += prob
            if r <= cumsum:
                return action

        # Fallback to last action
        return available_actions[-1]

    def _compute_action_probabilities(self, state: RLState, actions: List[RLAction]) -> List[float]:
        """Compute softmax probabilities over actions."""
        state_id = state.state_id

        # Get preference scores
        scores = []
        for action in actions:
            action_id = action.action_id
            params = self.policy_params.get(state_id, {})
            score = params.get(action_id, 0.0)
            scores.append(score)

        # Softmax
        exp_scores = [math.exp(s) for s in scores]
        sum_exp = sum(exp_scores)
        if sum_exp == 0:
            # Uniform distribution
            return [1.0 / len(actions)] * len(actions)

        probs = [e / sum_exp for e in exp_scores]
        return probs

    def update(self, transition: RLTransition) -> None:
        """Store transition for episode update."""
        self.episode_transitions.append(transition)

        if transition.done:
            self._update_policy()
            self.episode_transitions = []
            self.episode_count += 1

    def _update_policy(self) -> None:
        """Update policy using REINFORCE algorithm."""
        if not self.episode_transitions:
            return

        # Compute returns
        returns = self._compute_returns()

        # Update policy parameters
        for transition, G in zip(self.episode_transitions, returns):
            state_id = transition.state.state_id
            action_id = transition.action.action_id

            # Initialize state parameters if needed
            if state_id not in self.policy_params:
                self.policy_params[state_id] = {}

            # Get current parameter
            current_param = self.policy_params[state_id].get(action_id, 0.0)

            # Compute advantage (return - baseline)
            advantage = G - self.baseline_value

            # Gradient ascent update
            new_param = current_param + self.learning_rate * advantage

            self.policy_params[state_id][action_id] = new_param

        # Update baseline
        avg_return = sum(returns) / len(returns)
        self.baseline_value = 0.9 * self.baseline_value + 0.1 * avg_return

        self.logger.info(
            "policy_updated",
            episode=self.episode_count,
            avg_return=avg_return,
            baseline=self.baseline_value,
        )

    def _compute_returns(self) -> List[float]:
        """Compute discounted returns for each timestep."""
        returns: List[float] = []
        G = 0.0

        # Compute returns in reverse order
        for transition in reversed(self.episode_transitions):
            G = transition.reward.value + self.discount_factor * G
            returns.insert(0, G)
            self.total_reward += transition.reward.value

        return returns

    def get_policy_metrics(self) -> Dict[str, Any]:
        """Get metrics about the learned policy."""
        if not self.policy_params:
            return {
                "num_states": 0,
                "avg_param_value": 0.0,
                "baseline_value": self.baseline_value,
            }

        all_params: List[float] = []
        for state_params in self.policy_params.values():
            all_params.extend(state_params.values())

        return {
            "num_states": len(self.policy_params),
            "avg_param_value": sum(all_params) / len(all_params) if all_params else 0.0,
            "max_param_value": max(all_params) if all_params else 0.0,
            "min_param_value": min(all_params) if all_params else 0.0,
            "baseline_value": self.baseline_value,
            "total_reward": self.total_reward,
            "episodes": self.episode_count,
        }


# Aliases for backward compatibility with tests
State = RLState
Action = RLAction
ReinforcementLearningAgent = PolicyGradientAgent  # Use PolicyGradientAgent as default


class TabularQLearningAgent:
    """
    Tabular Q-Learning agent compatible with test expectations.

    This provides a simpler API for testing purposes.
    """

    def __init__(
        self,
        num_states: int = 10,
        num_actions: int = 4,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 0.1,
    ):
        """Initialize tabular Q-learning agent."""
        self.num_states = num_states
        self.num_actions = num_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon

        # Initialize Q-table
        self.q_table = np.zeros((num_states, num_actions))  # type: ignore

    def choose_action(self, state: int) -> int:
        """Choose action for given state using epsilon-greedy."""
        if np.random.random() < self.epsilon:  # type: ignore
            return int(np.random.randint(self.num_actions))  # type: ignore

        # Greedy action
        return int(np.argmax(self.q_table[state]))  # type: ignore

    def update(self, state: int, action: int, reward: float, next_state: int) -> None:
        """Update Q-value using Q-learning."""
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])  # type: ignore

        target = reward + self.discount_factor * max_next_q
        self.q_table[state, action] += self.learning_rate * (target - current_q)

    def get_best_action(self, state: int) -> int:
        """Get best action for given state."""
        return int(np.argmax(self.q_table[state]))  # type: ignore


# Update alias to use the tabular version for tests
QLearningAgent = TabularQLearningAgent

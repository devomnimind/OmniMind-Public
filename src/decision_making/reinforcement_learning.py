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

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import structlog
import random
import math

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
        pass

    @abstractmethod
    def step(self, action: RLAction) -> Tuple[RLState, RLReward, bool]:
        """
        Execute action and return next state, reward, and done flag.

        Args:
            action: Action to execute

        Returns:
            Tuple of (next_state, reward, done)
        """
        pass

    @abstractmethod
    def get_available_actions(self, state: RLState) -> List[RLAction]:
        """Get available actions for current state."""
        pass


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
    def select_action(
        self, state: RLState, available_actions: List[RLAction]
    ) -> RLAction:
        """Select action for given state."""
        pass

    @abstractmethod
    def update(self, transition: RLTransition) -> None:
        """Update agent based on transition."""
        pass

    def decay_exploration(self, decay_rate: float = 0.995) -> None:
        """Decay exploration rate over time."""
        self.exploration_rate *= decay_rate
        self.exploration_rate = max(0.01, self.exploration_rate)


class QLearningAgent(RLAgent):
    """
    Q-Learning agent with tabular Q-function.

    Features:
    - Epsilon-greedy exploration
    - Online learning from transitions
    - Integration with ethical rewards
    """

    def __init__(
        self,
        name: str = "q_learner",
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        exploration_rate: float = 0.1,
    ):
        """Initialize Q-learning agent."""
        super().__init__(name, learning_rate, discount_factor, exploration_rate)
        self.q_table: Dict[Tuple[str, str], float] = {}
        self.visit_counts: Dict[Tuple[str, str], int] = {}

    def select_action(
        self, state: RLState, available_actions: List[RLAction]
    ) -> RLAction:
        """Select action using epsilon-greedy policy."""
        if not available_actions:
            raise ValueError("No available actions")

        # Epsilon-greedy exploration
        if random.random() < self.exploration_rate:
            action = random.choice(available_actions)
            self.logger.debug("exploration_action", action_id=action.action_id)
            return action

        # Greedy exploitation
        best_action = available_actions[0]
        best_q = self._get_q_value(state, best_action)

        for action in available_actions[1:]:
            q_value = self._get_q_value(state, action)
            if q_value > best_q:
                best_q = q_value
                best_action = action

        self.logger.debug(
            "exploitation_action",
            action_id=best_action.action_id,
            q_value=best_q,
        )
        return best_action

    def update(self, transition: RLTransition) -> None:
        """Update Q-table using Q-learning update rule."""
        state_key = transition.state.state_id
        action_key = transition.action.action_id
        sa_pair = (state_key, action_key)

        # Get current Q-value
        current_q = self._get_q_value(transition.state, transition.action)

        # Compute max Q-value for next state
        if transition.done:
            max_next_q = 0.0
        else:
            # Assume all actions available (simplified)
            max_next_q = max(
                [
                    self.q_table.get((transition.next_state.state_id, a), 0.0)
                    for a in self.q_table.keys()
                    if a[0] == transition.next_state.state_id
                ]
                + [0.0]  # Default if no Q-values exist
            )

        # Q-learning update
        reward = transition.reward.value
        target = reward + self.discount_factor * max_next_q
        new_q = current_q + self.learning_rate * (target - current_q)

        # Update Q-table
        self.q_table[sa_pair] = new_q

        # Update visit counts
        self.visit_counts[sa_pair] = self.visit_counts.get(sa_pair, 0) + 1

        self.total_reward += reward

        self.logger.debug(
            "q_update",
            state=state_key,
            action=action_key,
            old_q=current_q,
            new_q=new_q,
            reward=reward,
        )

    def _get_q_value(self, state: RLState, action: RLAction) -> float:
        """Get Q-value for state-action pair."""
        key = (state.state_id, action.action_id)
        return self.q_table.get(key, 0.0)

    def get_policy_metrics(self) -> Dict[str, Any]:
        """Get metrics about the learned policy."""
        if not self.q_table:
            return {
                "num_states": 0,
                "num_actions": 0,
                "avg_q_value": 0.0,
                "max_q_value": 0.0,
            }

        states = set(k[0] for k in self.q_table.keys())
        actions = set(k[1] for k in self.q_table.keys())
        q_values = list(self.q_table.values())

        return {
            "num_states": len(states),
            "num_actions": len(actions),
            "num_state_action_pairs": len(self.q_table),
            "avg_q_value": sum(q_values) / len(q_values),
            "max_q_value": max(q_values),
            "min_q_value": min(q_values),
            "total_reward": self.total_reward,
            "episodes": self.episode_count,
        }


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

    def select_action(
        self, state: RLState, available_actions: List[RLAction]
    ) -> RLAction:
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

    def _compute_action_probabilities(
        self, state: RLState, actions: List[RLAction]
    ) -> List[float]:
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
        returns = []
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

        all_params = []
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

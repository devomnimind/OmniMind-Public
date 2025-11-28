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

"""Tests for decision making module initialization."""

from src.decision_making import (  # Decision Trees; Reinforcement Learning;
    # Ethical Decision Framework; Autonomous Goal Setting
    DecisionCriterion,
    DecisionNode,
    DecisionOutcome,
    DecisionTree,
    DecisionTreeBuilder,
    EthicalDecisionMaker,
    EthicalDilemma,
    EthicalFramework,
    EthicalOutcome,
    EthicalPrinciple,
    Goal,
    GoalHierarchy,
    GoalOptimizer,
    GoalPriority,
    GoalSetter,
    GoalStatus,
    PolicyGradientAgent,
    QLearningAgent,
    RLAction,
    RLAgent,
    RLEnvironment,
    RLReward,
    RLState,
)


def test_module_imports():
    """Test that all module components can be imported."""
    # Decision Trees
    assert DecisionTree is not None
    assert DecisionNode is not None
    assert DecisionCriterion is not None
    assert DecisionOutcome is not None
    assert DecisionTreeBuilder is not None

    # Reinforcement Learning
    assert RLAgent is not None
    assert RLEnvironment is not None
    assert RLState is not None
    assert RLAction is not None
    assert RLReward is not None
    assert QLearningAgent is not None
    assert PolicyGradientAgent is not None

    # Ethical Decision Framework
    assert EthicalDecisionMaker is not None
    assert EthicalPrinciple is not None
    assert EthicalDilemma is not None
    assert EthicalOutcome is not None
    assert EthicalFramework is not None

    # Autonomous Goal Setting
    assert GoalSetter is not None
    assert Goal is not None
    assert GoalPriority is not None
    assert GoalStatus is not None
    assert GoalHierarchy is not None
    assert GoalOptimizer is not None


def test_enum_values():
    """Test that enums have expected values."""
    assert DecisionCriterion.THRESHOLD.value == "threshold"
    assert GoalStatus.ACTIVE.value == "active"
    assert GoalPriority.HIGH.value == 4
    assert EthicalFramework.DEONTOLOGICAL.value == "deontological"
    assert EthicalPrinciple.AUTONOMY.value == "autonomy"

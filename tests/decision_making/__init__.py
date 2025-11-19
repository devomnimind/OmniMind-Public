"""Tests for decision making module initialization."""

import pytest
from src.decision_making import (
    # Decision Trees
    DecisionTree,
    DecisionNode,
    DecisionCriterion,
    DecisionOutcome,
    DecisionTreeBuilder,
    # Reinforcement Learning
    RLAgent,
    RLEnvironment,
    RLState,
    RLAction,
    RLReward,
    QLearningAgent,
    PolicyGradientAgent,
    # Ethical Decision Framework
    EthicalDecisionMaker,
    EthicalPrinciple,
    EthicalDilemma,
    EthicalOutcome,
    EthicalFramework,
    # Autonomous Goal Setting
    GoalSetter,
    Goal,
    GoalPriority,
    GoalStatus,
    GoalHierarchy,
    GoalOptimizer,
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

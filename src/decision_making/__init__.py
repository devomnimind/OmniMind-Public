"""
Decision Making Module for OmniMind - Phase 13 Implementation.

This module provides autonomous decision-making capabilities including:
- Intelligent decision trees
- Reinforcement learning-based decisions
- Ethical decision frameworks
- Autonomous goal setting

All components are designed for local-first operation with no external
dependencies beyond standard scientific libraries.
"""

from src.decision_making.autonomous_goal_setting import (
    Goal,
    GoalHierarchy,
    GoalOptimizer,
    GoalPriority,
    GoalSetter,
    GoalStatus,
)
from src.decision_making.decision_trees import (
    DecisionCriterion,
    DecisionNode,
    DecisionOutcome,
    DecisionTree,
    DecisionTreeBuilder,
)
from src.decision_making.ethical_decision_framework import (
    EthicalDecisionMaker,
    EthicalDilemma,
    EthicalFramework,
    EthicalOutcome,
    EthicalPrinciple,
)
from src.decision_making.reinforcement_learning import (
    PolicyGradientAgent,
    QLearningAgent,
    RLAction,
    RLAgent,
    RLEnvironment,
    RLReward,
    RLState,
)

__all__ = [
    # Decision Trees
    "DecisionTree",
    "DecisionNode",
    "DecisionCriterion",
    "DecisionOutcome",
    "DecisionTreeBuilder",
    # Reinforcement Learning
    "RLAgent",
    "RLEnvironment",
    "RLState",
    "RLAction",
    "RLReward",
    "QLearningAgent",
    "PolicyGradientAgent",
    # Ethical Decision Framework
    "EthicalDecisionMaker",
    "EthicalPrinciple",
    "EthicalDilemma",
    "EthicalOutcome",
    "EthicalFramework",
    # Autonomous Goal Setting
    "GoalSetter",
    "Goal",
    "GoalPriority",
    "GoalStatus",
    "GoalHierarchy",
    "GoalOptimizer",
]

__version__ = "1.0.0"

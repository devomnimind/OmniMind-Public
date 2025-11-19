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

from src.decision_making.decision_trees import (
    DecisionTree,
    DecisionNode,
    DecisionCriterion,
    DecisionOutcome,
    DecisionTreeBuilder,
)

from src.decision_making.reinforcement_learning import (
    RLAgent,
    RLEnvironment,
    RLState,
    RLAction,
    RLReward,
    QLearningAgent,
    PolicyGradientAgent,
)

from src.decision_making.ethical_decision_framework import (
    EthicalDecisionMaker,
    EthicalPrinciple,
    EthicalDilemma,
    EthicalOutcome,
    EthicalFramework,
)

from src.decision_making.autonomous_goal_setting import (
    GoalSetter,
    Goal,
    GoalPriority,
    GoalStatus,
    GoalHierarchy,
    GoalOptimizer,
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

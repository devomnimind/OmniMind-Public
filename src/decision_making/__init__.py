from src.decision_making.autonomous_goal_setting import ( from src.decision_making.decision_trees import (
from src.decision_making.ethical_decision_framework import ( from src.decision_making.reinforcement_learning import (

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
Decision Making Module for OmniMind - Phase 13 Implementation.

This module provides autonomous decision-making capabilities including:
- Intelligent decision trees
- Reinforcement learning-based decisions
- Ethical decision frameworks
- Autonomous goal setting

All components are designed for local-first operation with no external
dependencies beyond standard scientific libraries.
"""

    Goal,
    GoalHierarchy,
    GoalOptimizer,
    GoalPriority,
    GoalSetter,
    GoalStatus,
)
    DecisionCriterion,
    DecisionNode,
    DecisionOutcome,
    DecisionTree,
    DecisionTreeBuilder,
)
    EthicalDecisionMaker,
    EthicalDilemma,
    EthicalFramework,
    EthicalOutcome,
    EthicalPrinciple,
)
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

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

"""Metacognition module for OmniMind.

This module provides self-reflective AI capabilities including:
- Log analysis and pattern recognition
- Performance metrics analysis
- Bias detection in decision-making
- Optimization suggestions
- Proactive goal generation
- Homeostatic resource management
- Intelligent goal generation with impact prediction
"""

from __future__ import annotations

from .homeostasis import HomeostaticController
from .iit_metrics import IITAnalyzer, PhiMetrics, SystemState
from .intelligent_goal_generation import (
    CodeAnalyzer,
    ImpactMetrics,
    ImpactPredictor,
    IntelligentGoalEngine,
    RepositoryAnalysis,
)
from .issue_prediction import IssuePrediction
from .metacognition_agent import MetacognitionAgent
from .optimization_suggestions import OptimizationSuggestions
from .pattern_recognition import PatternRecognition
from .proactive_goals import ProactiveGoalEngine
from .root_cause_analysis import RootCauseAnalysis
from .self_analysis import SelfAnalysis
from .self_healing import SelfHealingLoop
from .self_optimization import SelfOptimizationEngine
from .trap_framework import TRAPComponent, TRAPFramework, TRAPScore

__all__ = [
    "MetacognitionAgent",
    "SelfAnalysis",
    "PatternRecognition",
    "OptimizationSuggestions",
    "ProactiveGoalEngine",
    "HomeostaticController",
    "IITAnalyzer",
    "PhiMetrics",
    "SystemState",
    "CodeAnalyzer",
    "ImpactMetrics",
    "ImpactPredictor",
    "IntelligentGoalEngine",
    "RepositoryAnalysis",
    "IssuePrediction",
    "RootCauseAnalysis",
    "SelfHealingLoop",
    "SelfOptimizationEngine",
    "TRAPFramework",
    "TRAPScore",
    "TRAPComponent",
]

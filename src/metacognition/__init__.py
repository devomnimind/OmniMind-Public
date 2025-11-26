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

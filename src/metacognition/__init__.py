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

__all__ = [
    "MetacognitionAgent",
    "SelfAnalysis",
    "PatternRecognition",
    "OptimizationSuggestions",
    "ProactiveGoalEngine",
    "HomeostaticController",
]

# IIT (Integrated Information Theory) metrics
from src.metacognition.iit_metrics import (
    IITAnalyzer,
    PhiMetrics,
    SystemState,
)

# Intelligent goal generation
from src.metacognition.intelligent_goal_generation import (
    CodeAnalyzer,
    ImpactMetrics,
    ImpactPredictor,
    IntelligentGoalEngine,
    RepositoryAnalysis,
)

__all__.extend(
    [
        "IITAnalyzer",
        "PhiMetrics",
        "SystemState",
        "CodeAnalyzer",
        "ImpactMetrics",
        "ImpactPredictor",
        "IntelligentGoalEngine",
        "RepositoryAnalysis",
    ]
)

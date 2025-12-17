"""Autonomous Adaptation Framework - Phase 26C

OmniMind auto-adaptation system that detects problems, finds solutions,
adapts to hardware, validates changes, and documents everything.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

from autonomous.auto_documentation_engine import AutoDocumentationEngine
from autonomous.auto_validation_engine import AutoValidationEngine
from autonomous.autonomous_loop import OmniMindAutonomousLoop
from autonomous.dynamic_framework_adapter import DynamicFrameworkAdapter
from autonomous.problem_detection_engine import ProblemDetectionEngine
from autonomous.solution_lookup_engine import SolutionLookupEngine

__all__ = [
    "ProblemDetectionEngine",
    "SolutionLookupEngine",
    "DynamicFrameworkAdapter",
    "AutoValidationEngine",
    "AutoDocumentationEngine",
    "OmniMindAutonomousLoop",
]

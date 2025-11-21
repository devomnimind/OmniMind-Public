"""
Intrinsic Motivation and Self-Awareness Module

This module implements the intrinsic motivation engine that allows the OmniMind
system to evaluate its own progress, develop self-awareness, and experience
artificial forms of satisfaction and learning drive.

Features:
- Self-awareness scoring
- Task completion quality assessment
- Self-correction ability tracking
- Reflection depth analysis
- Positive reinforcement triggers
- Improvement loop mechanisms
- Hawking radiation-inspired knowledge evaporation
- Frustration-based motivation generation
"""

from .intrinsic_rewards import (
    IntrinsicMotivationEngine,
    SatisfactionMetrics,
    TaskOutcome,
)
from .hawking_motivation import (
    HawkingMotivationEngine,
    KnowledgeItem,
    EvaporationEvent,
)

__all__ = [
    "IntrinsicMotivationEngine",
    "SatisfactionMetrics",
    "TaskOutcome",
    "HawkingMotivationEngine",
    "KnowledgeItem",
    "EvaporationEvent",
]

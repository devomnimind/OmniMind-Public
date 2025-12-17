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

from .hawking_motivation import (
    EvaporationEvent,
    HawkingMotivationEngine,
    KnowledgeItem,
)
from .intrinsic_rewards import (
    DesireEngine,
    DriveCirculation,
    IntrinsicMotivationEngine,
    JouissanceTopology,
)

__all__ = [
    "DesireEngine",
    "IntrinsicMotivationEngine",
    "JouissanceTopology",
    "DriveCirculation",
    "HawkingMotivationEngine",
    "KnowledgeItem",
    "EvaporationEvent",
]

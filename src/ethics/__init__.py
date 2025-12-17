"""
Ethics Agent - Digital Superego Module

Implements ethical reasoning and oversight for autonomous agents,
acting as a conscience that evaluates high-impact actions.
Includes ML-enhanced ethical decision making with multi-framework consensus.
"""

from .ethics_agent import (
    ActionImpact,
    EthicalDecision,
    EthicalFramework,
    EthicsAgent,
)
from .ml_ethics_engine import (
    ConsensusDecision,
    EthicalContext,
    EthicalFeatureExtractor,
    FrameworkScore,
    MLEthicsEngine,
)

__all__ = [
    # Original ethics agent
    "EthicsAgent",
    "EthicalDecision",
    "ActionImpact",
    "EthicalFramework",
    # ML-enhanced ethics
    "MLEthicsEngine",
    "EthicalContext",
    "ConsensusDecision",
    "FrameworkScore",
    "EthicalFeatureExtractor",
]

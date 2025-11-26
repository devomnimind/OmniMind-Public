"""
Agent Identity and Digital Signature Module

This module implements digital identity and reputation systems for autonomous agents,
allowing them to sign their work, build reputation, and maintain verifiable identity.
"""

from .agent_signature import (
    AgentIdentity,
    ReputationScore,
    WorkSignature,
)

__all__ = [
    "AgentIdentity",
    "WorkSignature",
    "ReputationScore",
]

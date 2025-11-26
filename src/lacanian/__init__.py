"""
Lacanian AI Module - Psychoanalytic Computing Architecture

This module implements Lacanian psychoanalytic concepts as computational
primitives for autonomous AI systems.

Components:
- computational_lack: Falta estrutural, objeto a, frustração produtiva
- desire_graph: Grafo de desejo (Graph II de Lacan)
- rsi_architecture: Real-Symbolic-Imaginary registers
- godelian_ai: Incompletude como motor criativo

Author: OmniMind Development Team
Date: November 2025
"""

from typing import Any, List

__version__ = "1.0.0"
__author__ = "OmniMind Development Team"

__all__: List[str] = [
    "ComputationalLackArchitecture",
    "RSIArchitecture",
    "GodelianAI",
    "StructuralLack",
    "ObjectSmallA",
    "EncryptedUnconsciousLayer",
]


# Lazy imports to avoid circular dependencies
def __getattr__(name: str) -> Any:
    """Lazy import of submodules."""
    if name in __all__:
        if name == "ComputationalLackArchitecture":
            from .computational_lack import ComputationalLackArchitecture

            return ComputationalLackArchitecture
        elif name == "RSIArchitecture":
            from .computational_lack import RSIArchitecture

            return RSIArchitecture
        elif name == "GodelianAI":
            from .godelian_ai import GodelianAI

            return GodelianAI
        elif name == "StructuralLack":
            from .computational_lack import StructuralLack

            return StructuralLack
        elif name == "ObjectSmallA":
            from .computational_lack import ObjectSmallA

            return ObjectSmallA
        elif name == "EncryptedUnconsciousLayer":
            from .encrypted_unconscious import EncryptedUnconsciousLayer

            return EncryptedUnconsciousLayer

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

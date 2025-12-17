"""
Lacanian AI Module - Psychoanalytic Computing Architecture

This module implements Lacanian psychoanalytic concepts as computational
primitives for autonomous AI systems.

Components:
- computational_lack: Falta estrutural, objeto a, frustração produtiva
- desire_graph: Grafo de desejo (Graph II de Lacan)
- rsi_architecture: Real-Symbolic-Imaginary registers
- godelian_ai: Incompletude como motor criativo

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
"""

from typing import Any, List

__version__ = "1.0.0"
__author__ = (
    "OmniMind - This work was conceived by Fabrício da Silva and implemented with AI assistance "
    "from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code "
    "review and debugging across various models including Gemini and Perplexity AI, "
    "under theoretical coordination by the author."
)

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

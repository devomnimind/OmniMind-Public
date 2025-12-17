"""
Phase 17: Co-Evolução Humano-IA

Este módulo implementa o framework de colaboração Human-Centered AI (HCHAC),
permitindo que humanos e IA co-evoluam através de parcerias baseadas em confiança,
negociação bidirecional de objetivos e feedback estruturado.

Componentes principais:
- HCHAC Framework: Orquestração de colaboração humano-IA
- Trust Metrics: Sistema de métricas de confiança
- Negotiation: Negociação dialética de objetivos
- Bidirectional Feedback: Feedback estruturado IA ↔ Humano
- Bias Detector: Detecção e correção de viés algorítmico
- Coevolution Memory: Histórico de colaboração
"""

from typing import Any

__version__ = "0.1.0"
__all__ = [
    "HCHACFramework",
    "TrustMetrics",
    "GoalNegotiator",
    "BidirectionalFeedback",
    "BiasDetector",
    "CoevolutionMemory",
]


# Lazy imports para evitar dependências circulares
def __getattr__(name: str) -> Any:
    """Lazy import de módulos."""
    if name == "HCHACFramework":
        from .hchac_framework import HCHACFramework

        return HCHACFramework
    elif name == "TrustMetrics":
        from .trust_metrics import TrustMetrics

        return TrustMetrics
    elif name == "GoalNegotiator":
        from .negotiation import GoalNegotiator

        return GoalNegotiator
    elif name == "BidirectionalFeedback":
        from .bidirectional_feedback import BidirectionalFeedback

        return BidirectionalFeedback
    elif name == "BiasDetector":
        from .bias_detector import BiasDetector

        return BiasDetector
    elif name == "CoevolutionMemory":
        from .coevolution_memory import CoevolutionMemory

        return CoevolutionMemory
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

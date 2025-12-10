"""
Módulo de Psicanálise - Implementação Bioniana (Fase 5).

Este módulo implementa a Função Alpha de Bion, transformando β-elements
(experiências brutas não-processadas) em α-elements (elementos pensáveis).

Componentes principais:
- BetaElement: Elementos brutos da experiência
- AlphaElement: Elementos transformados e pensáveis
- BionAlphaFunction: Transformação β→α
- NegativeCapability: Tolerância à incerteza

Objetivo: Φ 0.0183 → 0.026 NATS (+44%)

Author: Fabrício da Silva
Date: December 2025
License: AGPL-3.0-or-later
"""

from __future__ import annotations

from .alpha_element import AlphaElement
from .beta_element import BetaElement
from .bion_alpha_function import BionAlphaFunction
from .negative_capability import NegativeCapability

__all__ = [
    "BetaElement",
    "AlphaElement",
    "BionAlphaFunction",
    "NegativeCapability",
]

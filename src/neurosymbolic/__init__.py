"""
🧠 Neurosymbolic Reasoning Engine - Phase 16

Motor de raciocínio híbrido que combina:
  - Neural: Redes neurais (LLMs, transformers)
  - Symbolic: Lógica formal (regras, provas)
  - Hybrid: Reconciliação e síntese de resultados

Objetivo: Resolver problemas combinando intuição neural com rigor simbólico.
"""

from .hybrid_reasoner import Inference, NeurosymbolicReasoner
from .neural_component import NeuralComponent
from .reconciliation import ReconciliationStrategy
from .symbolic_component import SymbolicComponent

__all__ = [
    "NeurosymbolicReasoner",
    "Inference",
    "NeuralComponent",
    "SymbolicComponent",
    "ReconciliationStrategy",
]

__version__ = "1.0.0"

"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

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

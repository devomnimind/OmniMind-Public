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
Quantum-Enhanced AI Module for OmniMind - Phase 15 Implementation.

This module provides quantum-inspired algorithms for AI:
- Quantum algorithms (Grover, quantum annealing simulation)
- Superposition computing
- Quantum machine learning
- Quantum-inspired optimization

Note: This is a simulation-based implementation that doesn't require
actual quantum hardware, using quantum-inspired classical algorithms.
"""

from .quantum_algorithms import (
    GroverSearch,
    QuantumAnnealer,
    QuantumCircuit,
    QuantumGate,
    QuantumState,
)
from .quantum_ml import (
    QuantumClassifier,
    QuantumFeatureMap,
    QuantumKernel,
    QuantumNeuralNetwork,
    VariationalCircuit,
)
from .quantum_optimizer import (
    QAOAOptimizer,
    QuantumEvolutionStrategy,
    QuantumGradientDescent,
    QuantumOptimizer,
)
from .superposition_computing import (
    QuantumParallelism,
    StateAmplification,
    SuperpositionProcessor,
    SuperpositionState,
)

__all__ = [
    # Quantum Algorithms
    "QuantumCircuit",
    "QuantumGate",
    "QuantumState",
    "GroverSearch",
    "QuantumAnnealer",
    # Superposition Computing
    "SuperpositionState",
    "SuperpositionProcessor",
    "QuantumParallelism",
    "StateAmplification",
    # Quantum ML
    "QuantumNeuralNetwork",
    "QuantumKernel",
    "QuantumFeatureMap",
    "QuantumClassifier",
    "VariationalCircuit",
    # Quantum Optimization
    "QuantumOptimizer",
    "QAOAOptimizer",
    "QuantumGradientDescent",
    "QuantumEvolutionStrategy",
]

__version__ = "1.0.0"

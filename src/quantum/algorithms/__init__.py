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

from src.quantum.algorithms.quantum_algorithms import (
    GroverSearch,
    QuantumAnnealer,
    QuantumCircuit,
    QuantumGate,
    QuantumState,
)
from src.quantum.algorithms.quantum_ml import (
    QuantumClassifier,
    QuantumFeatureMap,
    QuantumKernel,
    QuantumNeuralNetwork,
    VariationalCircuit,
)
from src.quantum.algorithms.quantum_optimizer import (
    QAOAOptimizer,
    QuantumEvolutionStrategy,
    QuantumGradientDescent,
    QuantumOptimizer,
)
from src.quantum.algorithms.superposition_computing import (
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

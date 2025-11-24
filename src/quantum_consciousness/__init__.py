"""
Quantum Consciousness Module for OmniMind - Phase 21 Implementation.

This module provides experimental quantum-classical hybrid cognition:
- Quantum cognition using Qiskit/Cirq
- Quantum memory exploration
- QPU interface (IBM Quantum / simulators)
- Classical-quantum integration

⚠️  EXPERIMENTAL/RESEARCH MODULE - Not production-ready
Focus: Simulation first (Qiskit Aer simulator), QPU integration is future work.

Author: OmniMind Project
License: MIT
# ...existing code...
"""

from .quantum_cognition import (
    QuantumCognitionEngine,
    QuantumDecisionMaker,
    QuantumState as QCState,
    SuperpositionDecision,
)

from .quantum_memory import (
    QuantumMemorySystem,
    QuantumMemoryCell,
    HybridQLearning,
    QuantumMemoryComparison,
)

from .qpu_interface import (
    QPUInterface,
    QPUBackend,
    SimulatorBackend,
    IBMQBackend,
    BackendType,
)

from .hybrid_cognition import (
    HybridCognitionSystem,
    ClassicalQuantumBridge,
    CognitionMetrics,
    OptimizationStrategy,
)

from .quantum_backend import QuantumBackend, DWaveBackend

__all__ = [
    # Quantum Cognition
    "QuantumCognitionEngine",
    "QuantumDecisionMaker",
    "QCState",
    "SuperpositionDecision",
    # Quantum Memory
    "QuantumMemorySystem",
    "QuantumMemoryCell",
    "HybridQLearning",
    "QuantumMemoryComparison",
    # QPU Interface
    "QPUInterface",
    "QPUBackend",
    "SimulatorBackend",
    "IBMQBackend",
    "BackendType",
    "QuantumBackend",
    "DWaveBackend",
    # Hybrid Cognition
    "HybridCognitionSystem",
    "ClassicalQuantumBridge",
    "CognitionMetrics",
    "OptimizationStrategy",
]
# ...existing code...

__version__ = "0.1.0-experimental"

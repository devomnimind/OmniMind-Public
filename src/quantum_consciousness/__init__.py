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

from .hybrid_cognition import (
    ClassicalQuantumBridge,
    CognitionMetrics,
    HybridCognitionSystem,
    OptimizationStrategy,
)
from .hybrid_phi_calculator import HybridPhiCalculator
from .phi_trajectory_transformer import (
    PhiTrajectoryPoint,
    PhiTrajectoryTransformer,
    QuantumInputFeatures,
)
from .qpu_interface import (
    BackendType,
    IBMQBackend,
    QPUBackend,
    QPUInterface,
    SimulatorBackend,
)
from .quantum_backend import DWaveBackend, QuantumBackend
from .quantum_cognition import (
    QuantumCognitionEngine,
    QuantumDecisionMaker,
)
from .quantum_cognition import QuantumState as QCState
from .quantum_cognition import (
    SuperpositionDecision,
)
from .quantum_memory import (
    HybridQLearning,
    QuantumMemoryCell,
    QuantumMemoryComparison,
    QuantumMemorySystem,
)

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
    # Phase 24 → Phase 25 Bridge
    "PhiTrajectoryTransformer",
    "PhiTrajectoryPoint",
    "QuantumInputFeatures",
    "HybridPhiCalculator",
]
# ...existing code...

__version__ = "0.1.0-experimental"

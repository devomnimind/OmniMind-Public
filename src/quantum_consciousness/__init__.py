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
"""

from .hybrid_cognition import (
    ClassicalQuantumBridge,
    CognitionMetrics,
    HybridCognitionSystem,
    OptimizationStrategy,
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
    QuantumState as QCState,
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
]

__version__ = "0.1.0-experimental"

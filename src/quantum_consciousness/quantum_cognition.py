"""
Quantum Cognition Engine for OmniMind.

Implements quantum circuits for cognitive processes:
- Hadamard gates for superposition
- CNOT gates for entanglement
- Decision-making in quantum superposition
- Measurement and collapse

Uses Qiskit for quantum simulation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog

try:
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QuantumCircuit = Any  # Type alias when Qiskit not available
    QuantumRegister = Any
    ClassicalRegister = Any
    AerSimulator = Any
    Statevector = Any

logger = structlog.get_logger(__name__)


class QuantumGateType(Enum):
    """Types of quantum gates."""

    HADAMARD = "h"
    PAULI_X = "x"
    PAULI_Y = "y"
    PAULI_Z = "z"
    CNOT = "cx"
    PHASE = "p"
    RX = "rx"
    RY = "ry"
    RZ = "rz"


@dataclass
class QuantumState:
    """Represents a quantum state."""

    num_qubits: int
    statevector: Optional[np.ndarray] = None
    probabilities: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize quantum state."""
        if self.statevector is None:
            # Initialize to |0⟩ state
            size = 2**self.num_qubits
            self.statevector = np.zeros(size, dtype=complex)
            self.statevector[0] = 1.0 + 0j

    def measure(self) -> str:
        """Measure quantum state and collapse to classical."""
        if self.statevector is None:
            raise ValueError("No statevector to measure")

        # Calculate probabilities
        probs = np.abs(self.statevector) ** 2

        # Sample from distribution
        size = len(self.statevector)
        outcome_idx = np.random.choice(size, p=probs)

        # Convert to binary string
        outcome = format(outcome_idx, f"0{self.num_qubits}b")
        return outcome


@dataclass
class SuperpositionDecision:
    """Decision made in quantum superposition."""

    options: List[str]
    quantum_state: QuantumState
    probabilities: Dict[str, float]
    final_decision: Optional[str] = None
    confidence: float = 0.0

    def collapse(self) -> str:
        """Collapse superposition to single decision."""
        if not QISKIT_AVAILABLE:
            # Fallback to classical random choice
            logger.warning("Qiskit not available, using classical fallback")
            import random

            self.final_decision = random.choice(self.options)
            self.confidence = 1.0 / len(self.options)
            return self.final_decision

        outcome = self.quantum_state.measure()
        # Map outcome to option (remove spaces from outcome first)
        outcome_clean = outcome.replace(" ", "")
        outcome_int = int(outcome_clean, 2) % len(self.options)
        self.final_decision = self.options[outcome_int]
        self.confidence = self.probabilities.get(self.final_decision, 0.0)

        logger.info(
            "quantum_decision_collapsed",
            decision=self.final_decision,
            confidence=self.confidence,
            outcome=outcome,
        )
        return self.final_decision


class QuantumCognitionEngine:
    """
    Quantum cognition engine using Qiskit.

    Implements quantum circuits for cognitive tasks:
    - Superposition states
    - Entanglement
    - Interference
    - Measurement
    """

    def __init__(self, num_qubits: int = 2) -> None:
        """
        Initialize quantum cognition engine.

        Args:
            num_qubits: Number of qubits for quantum circuits
        """
        if not QISKIT_AVAILABLE:
            logger.warning(
                "qiskit_not_available",
                msg="Qiskit not installed. Install with: pip install qiskit qiskit-aer",
            )

        self.num_qubits = num_qubits
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None

        logger.info(
            "quantum_cognition_initialized",
            num_qubits=num_qubits,
            qiskit_available=QISKIT_AVAILABLE,
        )

    def create_superposition(
        self, qubits: Optional[List[int]] = None, weights: Optional[List[float]] = None
    ) -> QuantumCircuit:
        """
        Create quantum superposition.

        If weights are provided, uses Ry gates to create biased superposition.
        If no weights, uses Hadamard gates for uniform superposition.

        Args:
            qubits: List of qubit indices.
            weights: List of weights for biasing (must match length of qubits).
                     Weight 0.5 = uniform (Hadamard equivalent).
                     Weight > 0.5 = bias towards |1⟩.
                     Weight < 0.5 = bias towards |0⟩.

        Returns:
            QuantumCircuit in superposition state
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit required for quantum operations")

        qr = QuantumRegister(self.num_qubits, "q")
        cr = ClassicalRegister(self.num_qubits, "c")
        qc = QuantumCircuit(qr, cr)

        target_qubits = qubits if qubits is not None else list(range(self.num_qubits))

        if weights:
            if len(weights) != len(target_qubits):
                raise ValueError("Number of weights must match number of target qubits")

            for i, qubit in enumerate(target_qubits):
                # Map weight [0, 1] to theta [0, pi]
                # weight 0 -> state |0> -> theta = 0
                # weight 1 -> state |1> -> theta = pi
                # weight 0.5 -> superposition -> theta = pi/2
                theta = 2 * np.arcsin(np.sqrt(weights[i]))
                qc.ry(theta, qubit)
        else:
            for qubit in target_qubits:
                qc.h(qubit)  # Hadamard gate creates uniform superposition

        logger.debug("superposition_created", qubits=target_qubits, biased=bool(weights))

        return qc

    def create_entanglement(self, control_qubit: int = 0, target_qubit: int = 1) -> QuantumCircuit:
        """
        Create entangled state using CNOT gate.

        Args:
            control_qubit: Control qubit index
            target_qubit: Target qubit index

        Returns:
            QuantumCircuit with entangled qubits
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit required for quantum operations")

        qr = QuantumRegister(self.num_qubits, "q")
        cr = ClassicalRegister(self.num_qubits, "c")
        qc = QuantumCircuit(qr, cr)

        # Create Bell state: |00⟩ + |11⟩
        qc.h(control_qubit)  # Superposition
        qc.cx(control_qubit, target_qubit)  # Entanglement

        logger.debug("entanglement_created", control=control_qubit, target=target_qubit)

        return qc

    def get_statevector(self, circuit: QuantumCircuit) -> QuantumState:
        """
        Get quantum statevector from circuit.

        Args:
            circuit: QuantumCircuit to evaluate

        Returns:
            QuantumState with statevector
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit required for quantum operations")

        # Get statevector
        sv = Statevector(circuit)
        state = QuantumState(num_qubits=self.num_qubits, statevector=sv.data)

        # Calculate probabilities
        probs = np.abs(sv.data) ** 2
        for idx, prob in enumerate(probs):
            if prob > 1e-10:  # Only significant probabilities
                basis_state = format(idx, f"0{self.num_qubits}b")
                state.probabilities[basis_state] = float(prob)

        return state

    def measure_circuit(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
        """
        Measure quantum circuit multiple times.

        Args:
            circuit: QuantumCircuit to measure
            shots: Number of measurements

        Returns:
            Dictionary of measurement outcomes and counts
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit required for quantum operations")

        # Add measurement to all qubits
        qc = circuit.copy()
        qc.measure_all()

        # Run simulation
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()

        logger.info("circuit_measured", shots=shots, num_outcomes=len(counts))

        return counts


class QuantumDecisionMaker:
    """
    Quantum decision maker using superposition.

    Makes decisions by encoding options in quantum superposition
    and measuring the collapsed state.
    """

    def __init__(self, num_qubits: int = 3) -> None:
        """
        Initialize quantum decision maker.

        Args:
            num_qubits: Number of qubits (determines max options = 2^n)
        """
        self.engine = QuantumCognitionEngine(num_qubits=num_qubits)
        self.num_qubits = num_qubits

        logger.info("quantum_decision_maker_initialized", max_options=2**num_qubits)

    def make_decision(
        self, options: List[str], weights: Optional[List[float]] = None
    ) -> SuperpositionDecision:
        """
        Make decision using quantum superposition.

        Args:
            options: List of decision options
            weights: Optional weights for biasing decision.
                     If provided, must be a list of floats [0, 1] for each qubit.
                     Note: This implementation currently maps 1 weight per qubit.
                     For complex option weighting, a more sophisticated encoding is needed.

        Returns:
            SuperpositionDecision with quantum state
        """
        if len(options) > 2**self.num_qubits:
            raise ValueError(f"Too many options ({len(options)}). Max is {2 ** self.num_qubits}")

        if not QISKIT_AVAILABLE:
            logger.warning("qiskit_not_available_fallback")
            # Classical fallback
            state = QuantumState(num_qubits=self.num_qubits)
            probs = {opt: 1.0 / len(options) for opt in options}
            return SuperpositionDecision(options=options, quantum_state=state, probabilities=probs)

        # Create superposition circuit
        # If weights are provided, we need to map them to qubits.
        # This is a simplification. Real encoding of arbitrary option weights is complex.
        # Here we assume weights map 1:1 to qubits for demonstration of bias.
        qubit_weights = None
        if weights:
            # Pad or truncate weights to match num_qubits
            qubit_weights = weights[: self.num_qubits]
            while len(qubit_weights) < self.num_qubits:
                qubit_weights.append(0.5)  # Default to uniform

        circuit = self.engine.create_superposition(weights=qubit_weights)

        # Get quantum state
        q_state = self.engine.get_statevector(circuit)

        # Map probabilities to options
        option_probs: Dict[str, float] = {}
        for idx, option in enumerate(options):
            # Sum probabilities for basis states that map to this option
            total_prob = 0.0
            for basis_state, prob in q_state.probabilities.items():
                if int(basis_state, 2) % len(options) == idx:
                    total_prob += prob
            option_probs[option] = total_prob

        decision = SuperpositionDecision(
            options=options, quantum_state=q_state, probabilities=option_probs
        )

        logger.info(
            "quantum_decision_created",
            num_options=len(options),
            probabilities=option_probs,
            biased=bool(weights),
        )

        return decision

    def demonstrate_entanglement(self) -> Tuple[QuantumCircuit, Dict[str, int]]:
        """
        Demonstrate quantum entanglement.

        Returns:
            Tuple of (circuit, measurement_counts)
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit required for quantum operations")

        circuit = self.engine.create_entanglement(0, 1)
        counts = self.engine.measure_circuit(circuit, shots=1000)

        logger.info("entanglement_demonstrated", counts=counts)

        return circuit, counts

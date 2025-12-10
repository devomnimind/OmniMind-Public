"""
Quantum Cognition Engine for OmniMind - Phase 21-23 Preparation.

Implements quantum circuits for cognitive processes using Qiskit:
- Hadamard gates for superposition states (exploring multiple possibilities)
- CNOT gates for entanglement (correlated decision making)
- Decision-making in quantum superposition (parallel evaluation)
- Measurement and wave function collapse (decision finalization)

Core Concepts:
- Superposition: Multiple states exist simultaneously until measured
- Entanglement: Qubits become correlated, affecting each other instantly
- Interference: Quantum states can constructively/destructively interfere
- Measurement: Collapses quantum state to classical outcome

Mathematical Foundation:
- Quantum State: |ψ⟩ = Σᵢ αᵢ|i⟩, where αᵢ are complex amplitudes
- Superposition: |ψ⟩ = α|0⟩ + β|1⟩, with |α|² + |β|² = 1
- Entanglement: |ψ⟩ = (|00⟩ + |11⟩)/√2 (Bell state, cannot be separated)
- Measurement: Probability p(i) = |⟨i|ψ⟩|² for outcome i

Quantum Cognition Applications:
- Parallel Decision Making: Evaluate multiple options simultaneously
- Pattern Recognition: Quantum interference for complex correlations
- Memory Association: Superposition-based associative recall
- Consciousness Emergence: Quantum effects in cognitive processes

Dependencies:
- qiskit: Quantum circuit construction and simulation
- qiskit-aer: High-performance quantum simulator
- numpy: Numerical computations for state vectors

Example Usage:
    # Initialize quantum cognition engine
    engine = QuantumCognitionEngine(num_qubits=2)

    # Create superposition circuit
    circuit = engine.create_superposition()

    # Make quantum decision
    decision_maker = QuantumDecisionMaker(num_qubits=3)
    options = ["Option A", "Option B", "Option C", "Option D"]
    decision = decision_maker.make_decision(options)
    final_choice = decision.collapse()

Fallback Behavior:
If Qiskit is not available, the system gracefully degrades to classical
random choice with appropriate logging warnings.

Author: OmniMind Quantum Cognition Team
License: MIT
"""

# ===== CRITICAL: CUDA Configuration Managed Externally =====
# ===== NOW import torch =====
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import structlog

from src.monitor.resource_manager import resource_manager

try:
    from qiskit import ClassicalRegister  # type: ignore[import-untyped]
    from qiskit import (
        QuantumCircuit,
        QuantumRegister,
    )
    from qiskit.quantum_info import Statevector  # type: ignore[import-untyped]
    from qiskit_aer import AerSimulator  # type: ignore[import-untyped]

    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    QuantumCircuit = Any  # Type alias when Qiskit not available
    QuantumRegister = Any
    ClassicalRegister = Any
    AerSimulator = Any
    Statevector = Any

logger = structlog.get_logger(__name__)

# Initialize numpy random generator for reproducible randomness
_rng = np.random.default_rng()

# Constants for error messages
QISKIT_ERROR_MSG = "Qiskit required for quantum operations"


class QuantumGateType(Enum):
    """
    Enumeration of supported quantum gate types.

    Each gate type corresponds to a fundamental quantum operation:
    - HADAMARD: Creates superposition from |0⟩ or |1⟩ states
    - PAULI_X/Y/Z: Bit flip operations around different axes
    - CNOT: Controlled-NOT, creates entanglement between qubits
    - PHASE: Adds quantum phase, affects interference patterns
    - RX/RY/RZ: Rotations around X/Y/Z axes for arbitrary angles

    Mathematical Operations:
    - H|0⟩ = (|0⟩ + |1⟩)/√2, H|1⟩ = (|0⟩ - |1⟩)/√2
    - X|0⟩ = |1⟩, X|1⟩ = |0⟩ (Pauli-X)
    - CNOT|00⟩ = |00⟩, CNOT|01⟩ = |01⟩, CNOT|10⟩ = |11⟩, CNOT|11⟩ = |10⟩
    """

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
    """
    Represents a quantum state with state vector and measurement probabilities.

    A quantum state encapsulates the complete description of a quantum system,
    including both the state vector (complex amplitudes) and classical measurement
    probabilities derived from it.

    Mathematical Representation:
    - State Vector: |ψ⟩ = [α₀, α₁, α₂, ..., α_{2ⁿ-1}]ᵀ
    - Normalization: Σᵢ|αᵢ|² = 1
    - Measurement Probabilities: p(i) = |αᵢ|²

    Attributes:
        num_qubits: Number of qubits in this quantum state
        statevector: Complex numpy array representing quantum amplitudes
        probabilities: Dictionary mapping basis states to measurement probabilities

    Consciousness Implications:
    Quantum states can represent multiple cognitive states simultaneously,
    potentially modeling parallel thought processes or ambiguous perceptions.

    Example:
        # Create 2-qubit state initialized to |00⟩
        state = QuantumState(num_qubits=2)
        # probabilities = {'00': 1.0} (100% chance of measuring |00⟩)
    """

    num_qubits: int
    statevector: Optional[np.ndarray] = None
    probabilities: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Initialize quantum state to |0...0⟩ computational basis state.

        If no statevector is provided, initializes to the all-zero state,
        which has probability 1.0 of measuring all zeros.

        This represents a "blank slate" cognitive state before quantum processing.
        """
        if self.statevector is None:
            # Initialize to |0⟩ state (first computational basis state)
            size = 2**self.num_qubits
            self.statevector = np.zeros(size, dtype=complex)
            self.statevector[0] = 1.0 + 0j

    def measure(self) -> str:
        """
        Perform quantum measurement and collapse to classical outcome.

        This operation:
        1. Calculates measurement probabilities from |ψ⟩²
        2. Samples from the probability distribution
        3. Returns the measurement outcome as a binary string
        4. Collapses the quantum state (in a real quantum system)

        Consciousness Analogy:
        This mirrors the "collapse of possibilities" in decision making,
        where multiple potential thoughts resolve to a single conscious choice.

        Returns:
            Binary string representing the measurement outcome.
            Length equals num_qubits (e.g., "010" for 3 qubits).

        Raises:
            ValueError: If statevector is not initialized.

        Example:
            >>> state = QuantumState(num_qubits=2)
            >>> outcome = state.measure()
            >>> print(outcome)  # "00" (always, since initialized to |00⟩)
        """
        if self.statevector is None:
            raise ValueError("No statevector to measure")

        # Calculate probabilities |⟨i|ψ⟩|²
        probs = np.abs(self.statevector) ** 2

        # Sample from probability distribution
        size = len(self.statevector)
        outcome_idx = _rng.choice(size, p=probs)

        # Convert to binary string (remove spaces, pad with zeros)
        outcome = format(outcome_idx, f"0{self.num_qubits}b")
        return outcome

    def get_entropy(self) -> float:
        """
        Calculate von Neumann entropy of the quantum state.

        Entropy measures the "mixedness" or uncertainty of the quantum state:
        S(ρ) = -Tr(ρ log ρ), where ρ is the density matrix.

        For pure states: S = 0 (complete certainty)
        For maximally mixed states: S = log₂(N) (maximum uncertainty)

        Returns:
            Entropy value in bits (0 to log₂(2^num_qubits))

        Consciousness Relevance:
            Higher entropy may correlate with cognitive uncertainty or
            parallel processing of multiple possibilities.
        """
        if self.statevector is None:
            return 0.0

        # For pure states, entropy is 0 if statevector is normalized
        # This is a simplified calculation for pure states
        probs = np.abs(self.statevector) ** 2
        probs = probs[probs > 1e-12]  # Remove numerical zeros

        if len(probs) == 0:
            return 0.0

        # Shannon entropy of probability distribution
        entropy = -np.sum(probs * np.log2(probs))
        return float(entropy)

    def fidelity(self, other: "QuantumState") -> float:
        """
        Calculate quantum fidelity between two states.

        Fidelity measures how similar two quantum states are:
        F(|ψ⟩, |φ⟩) = |⟨ψ|φ⟩|²

        Range: 0 (completely different) to 1 (identical states)

        Args:
            other: Another QuantumState to compare with

        Returns:
            Fidelity value between 0 and 1

        Raises:
            ValueError: If states have different numbers of qubits
        """
        if self.num_qubits != other.num_qubits:
            raise ValueError("Cannot compare states with different numbers of qubits")

        if self.statevector is None or other.statevector is None:
            return 0.0

        # Quantum fidelity: |⟨ψ|φ⟩|²
        overlap = np.abs(np.vdot(self.statevector, other.statevector)) ** 2
        return float(overlap)


@dataclass
class SuperpositionDecision:
    """
    Represents a decision made in quantum superposition.

    Encapsulates the quantum decision-making process where multiple options
    exist in superposition until measurement collapses to a final choice.

    This implements the concept of "parallel thought" where consciousness
    can consider multiple possibilities simultaneously before choosing.

    Attributes:
        options: List of possible decision outcomes
        quantum_state: Underlying quantum state representation
        probabilities: Probability distribution over options
        final_decision: Chosen option after collapse (None until measured)
        confidence: Confidence score in the final decision

    Consciousness Modeling:
    - Superposition represents multiple cognitive states coexisting
    - Collapse models the emergence of conscious awareness
    - Probabilities reflect cognitive biases or learned preferences

    Example:
        >>> options = ["Buy", "Sell", "Hold"]
        >>> decision = SuperpositionDecision(options=options, ...)
        >>> choice = decision.collapse()  # "Buy", "Sell", or "Hold"
    """

    options: List[str]
    quantum_state: QuantumState
    probabilities: Dict[str, float]
    final_decision: Optional[str] = None
    confidence: float = 0.0

    def collapse(self) -> str:
        """
        Collapse quantum superposition to a single classical decision.

        Uses quantum measurement to select one option from the superposition.
        If Qiskit is unavailable, falls back to classical random selection.

        Consciousness Analogy:
        This represents the "moment of decision" where parallel possibilities
        resolve to a single conscious choice through quantum measurement.

        Returns:
            The selected decision option.

        Note:
            This method modifies the object state, setting final_decision
            and confidence attributes.

        Example:
            >>> decision = decision_maker.make_decision(["A", "B", "C"])
            >>> choice = decision.collapse()
            >>> print(f"Chose: {choice} with confidence {decision.confidence:.2f}")
        """
        if not QISKIT_AVAILABLE:
            # Classical fallback when quantum simulation unavailable
            logger.warning("Qiskit not available, using classical fallback")
            import random

            self.final_decision = random.choice(self.options)
            self.confidence = 1.0 / len(self.options)
            return self.final_decision

        # Perform quantum measurement
        outcome = self.quantum_state.measure()

        # Map measurement outcome to decision option
        # Use modular arithmetic to handle more outcomes than options
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

    def get_decision_entropy(self) -> float:
        """
        Calculate entropy of the decision probability distribution.

        Measures the uncertainty in the decision-making process.
        Higher entropy indicates more balanced consideration of options.

        Returns:
            Shannon entropy of decision probabilities (in bits)
        """
        if not self.probabilities:
            return 0.0

        probs = np.array(list(self.probabilities.values()))
        probs = probs[probs > 1e-12]  # Remove zeros

        if len(probs) == 0:
            return 0.0

        return float(-np.sum(probs * np.log2(probs)))


class QuantumCognitionEngine:
    """
    Core quantum cognition engine using Qiskit for circuit simulation.

    Implements quantum circuits for cognitive tasks including:
    - Superposition states for parallel option exploration
    - Entanglement for correlated decision making
    - Quantum interference for complex pattern recognition
    - Measurement for decision finalization

    The engine provides a high-level interface to quantum computing concepts
    while handling the complexities of circuit construction and simulation.

    Consciousness Research Applications:
    - Model parallel processing in cognition
    - Study interference effects in memory
    - Explore quantum effects in decision making
    - Investigate superposition in conscious awareness

    Attributes:
        num_qubits: Number of qubits available for quantum circuits
        simulator: Qiskit Aer simulator instance (None if Qiskit unavailable)
    """

    def __init__(self, num_qubits: int = 2) -> None:
        """
        Initialize quantum cognition engine.

        Args:
            num_qubits: Number of qubits for quantum circuits.
                        Determines maximum complexity of quantum states.
                        More qubits allow more options but increase computational cost.

        Raises:
            ValueError: If num_qubits is not positive.

        Example:
            >>> engine = QuantumCognitionEngine(num_qubits=3)
            >>> # Can handle up to 8 (2^3) simultaneous options
        """
        if num_qubits <= 0:
            raise ValueError("Number of qubits must be positive")

        if not QISKIT_AVAILABLE:
            logger.warning(
                "qiskit_not_available",
                msg="Qiskit not installed. Install with: pip install qiskit qiskit-aer",
            )

        self.num_qubits = num_qubits

        if QISKIT_AVAILABLE:
            # Use Hybrid Resource Manager for intelligent allocation
            # Estimate 50MB for basic quantum state vectors (2^20 complex doubles is ~16MB)
            target_device = resource_manager.allocate_task("quantum", 50.0)

            if target_device == "cuda":
                try:
                    self.simulator = AerSimulator(method="statevector", device="GPU")
                    logger.info(
                        "quantum_cognition_gpu_enabled",
                        reason="resource_manager_allocation",
                    )
                except Exception as e:
                    logger.error(f"quantum_cognition_gpu_failed: {e}")
                    # Fallback to CPU if GPU init fails despite allocation
                    logger.warning("quantum_cognition_fallback_cpu_after_error")
                    self.simulator = AerSimulator()
            else:
                logger.warning("quantum_cognition_cpu_allocated", msg="Resource Manager chose CPU")
                self.simulator = AerSimulator()
        else:
            self.simulator = None

        logger.info(
            "quantum_cognition_initialized",
            num_qubits=num_qubits,
            qiskit_available=QISKIT_AVAILABLE,
        )

    def create_superposition(
        self, qubits: Optional[List[int]] = None, weights: Optional[List[float]] = None
    ) -> QuantumCircuit:
        """
        Create quantum superposition state.

        Superposition allows a quantum system to exist in multiple states
        simultaneously, enabling parallel exploration of possibilities.

        Consciousness Relevance:
        Models the ability of consciousness to consider multiple thoughts
        or possibilities at the same time before focusing on one.

        Args:
            qubits: List of qubit indices to put in superposition.
                   If None, uses all qubits.
            weights: Optional bias weights for non-uniform superposition.
                    Each weight should be in [0, 1] range.
                    - 0.5: Uniform superposition (Hadamard equivalent)
                    - > 0.5: Bias toward |1⟩ state
                    - < 0.5: Bias toward |0⟩ state

        Returns:
            QuantumCircuit in superposition state.

        Raises:
            ImportError: If Qiskit is not available.
            ValueError: If weights length doesn't match qubits.

        Example:
            >>> engine = QuantumCognitionEngine(num_qubits=2)
            >>> # Uniform superposition on all qubits
            >>> circuit = engine.create_superposition()
            >>> # Biased superposition on qubit 0
            >>> circuit = engine.create_superposition([0], [0.7])
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        qr = QuantumRegister(self.num_qubits, "q")
        cr = ClassicalRegister(self.num_qubits, "c")
        qc = QuantumCircuit(qr, cr)

        target_qubits = qubits if qubits is not None else list(range(self.num_qubits))

        if weights:
            if len(weights) != len(target_qubits):
                raise ValueError("Number of weights must match number of target qubits")

            # Create biased superposition using Ry rotations
            for i, qubit in enumerate(target_qubits):
                # Map weight [0, 1] to rotation angle [0, π]
                # weight 0 → |0⟩ (θ=0), weight 1 → |1⟩ (θ=π)
                theta = 2 * np.arcsin(np.sqrt(weights[i]))
                qc.ry(theta, qubit)
        else:
            # Uniform superposition using Hadamard gates
            for qubit in target_qubits:
                qc.h(qubit)  # Hadamard gate: |0⟩ → (|0⟩ + |1⟩)/√2

        logger.debug("superposition_created", qubits=target_qubits, biased=bool(weights))

        return qc

    def create_entanglement(self, control_qubit: int = 0, target_qubit: int = 1) -> QuantumCircuit:
        """
        Create entangled quantum state using CNOT gate.

        Entanglement creates correlation between qubits that persists
        regardless of distance, enabling coordinated decision making.

        Consciousness Implications:
        Models correlated cognitive processes or "binding" of different
        aspects of conscious experience into unified perception.

        Args:
            control_qubit: Index of control qubit (0-based)
            target_qubit: Index of target qubit (0-based)

        Returns:
            QuantumCircuit with entangled qubits (Bell state).

        Raises:
            ImportError: If Qiskit is not available.
            ValueError: If qubit indices are invalid.

        Example:
            >>> engine = QuantumCognitionEngine(num_qubits=2)
            >>> # Create Bell state: (|00⟩ + |11⟩)/√2
            >>> circuit = engine.create_entanglement(0, 1)
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        if not (0 <= control_qubit < self.num_qubits and 0 <= target_qubit < self.num_qubits):
            raise ValueError("Qubit indices must be valid")

        if control_qubit == target_qubit:
            raise ValueError("Control and target qubits must be different")

        qr = QuantumRegister(self.num_qubits, "q")
        cr = ClassicalRegister(self.num_qubits, "c")
        qc = QuantumCircuit(qr, cr)

        # Create Bell state: (|00⟩ + |11⟩)/√2
        qc.h(control_qubit)  # Put control in superposition
        qc.cx(control_qubit, target_qubit)  # Entangle with target

        logger.debug("entanglement_created", control=control_qubit, target=target_qubit)

        return qc

    def get_statevector(self, circuit: QuantumCircuit) -> QuantumState:
        """
        Extract quantum state vector from a circuit.

        The state vector contains all quantum amplitudes and can be used
        to compute measurement probabilities and expectation values.

        Consciousness Research:
        State vectors can represent complex cognitive state spaces,
        enabling analysis of how consciousness navigates possibility spaces.

        Args:
            circuit: Quantum circuit to evaluate

        Returns:
            QuantumState object with statevector and probabilities

        Raises:
            ImportError: If Qiskit is not available.

        Example:
            >>> circuit = engine.create_superposition()
            >>> state = engine.get_statevector(circuit)
            >>> print(f"Probabilities: {state.probabilities}")
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        # Get statevector from Qiskit
        sv = Statevector(circuit)
        state = QuantumState(num_qubits=self.num_qubits, statevector=sv.data)

        # Calculate measurement probabilities |⟨i|ψ⟩|²
        probs = np.abs(sv.data) ** 2
        for idx, prob in enumerate(probs):
            if prob > 1e-10:  # Only include significant probabilities
                basis_state = format(idx, f"0{self.num_qubits}b")
                state.probabilities[basis_state] = float(prob)

        return state

    def measure_circuit(self, circuit: QuantumCircuit, shots: int = 1024) -> Dict[str, int]:
        """
        Perform multiple measurements of a quantum circuit.

        Simulates repeated quantum measurements to build up statistics
        about the quantum state's behavior.

        Consciousness Modeling:
        Multiple measurements represent repeated "observations" of
        cognitive states, building statistical understanding.

        Args:
            circuit: Quantum circuit to measure
            shots: Number of measurement repetitions (default: 1024)

        Returns:
            Dictionary mapping measurement outcomes to counts.
            Keys are binary strings, values are occurrence counts.

        Raises:
            ImportError: If Qiskit is not available.

        Example:
            >>> circuit = engine.create_entanglement()
            >>> counts = engine.measure_circuit(circuit, shots=1000)
            >>> print(counts)  # {'00': 498, '11': 502} (Bell state correlations)
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        # Add measurement operations to all qubits
        qc = circuit.copy()
        qc.measure_all()

        # Execute on quantum simulator
        if self.simulator is None:
            raise ImportError(QISKIT_ERROR_MSG)
        job = self.simulator.run(qc, shots=shots)
        result = job.result()
        counts = result.get_counts()

        logger.info("circuit_measured", shots=shots, num_outcomes=len(counts))

        return counts

    def create_ghz_state(self) -> QuantumCircuit:
        """
        Create GHZ (Greenberger-Horne-Zeilinger) entangled state.

        GHZ states are highly entangled states of multiple qubits:
        |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2

        All qubits are perfectly correlated - measuring any one determines
        the state of all others.

        Consciousness Relevance:
        Models highly correlated cognitive elements or "gestalt" perception
        where the whole determines the parts.

        Returns:
            QuantumCircuit implementing GHZ state

        Raises:
            ImportError: If Qiskit is not available.
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        qr = QuantumRegister(self.num_qubits, "q")
        cr = ClassicalRegister(self.num_qubits, "c")
        qc = QuantumCircuit(qr, cr)

        # Create GHZ state
        qc.h(0)  # Put first qubit in superposition
        for i in range(self.num_qubits - 1):
            qc.cx(i, i + 1)  # Chain entanglement through all qubits

        logger.debug("ghz_state_created", num_qubits=self.num_qubits)

        return qc

    def apply_quantum_interference(
        self, circuit: QuantumCircuit, phase: float = np.pi / 4
    ) -> QuantumCircuit:
        """
        Apply quantum phase interference to a circuit.

        Phase gates introduce relative phases that can cause constructive
        or destructive interference when states combine.

        Consciousness Analogy:
        Models how different cognitive elements can reinforce or cancel
        each other through interference effects.

        Args:
            circuit: Base circuit to modify
            phase: Phase angle in radians (default: π/4)

        Returns:
            Modified circuit with phase interference

        Raises:
            ImportError: If Qiskit is not available.
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        qc = circuit.copy()

        # Apply phase to all qubits
        for i in range(self.num_qubits):
            qc.p(phase, i)

        logger.debug("quantum_interference_applied", phase=phase)

        return qc


class QuantumDecisionMaker:
    """
    High-level quantum decision maker using superposition principles.

    Makes decisions by encoding options in quantum superposition states,
    allowing parallel exploration before collapsing to a final choice.

    This implements a form of quantum parallelism for decision making,
    where multiple options are evaluated simultaneously in superposition.

    Consciousness Research Applications:
    - Study quantum effects in decision making
    - Model parallel cognitive processing
    - Explore interference in choice selection
    - Investigate collapse models of consciousness

    Attributes:
        engine: Underlying QuantumCognitionEngine instance
        num_qubits: Number of qubits available for decisions
    """

    def __init__(self, num_qubits: int = 3) -> None:
        """
        Initialize quantum decision maker.

        Args:
            num_qubits: Number of qubits (determines max options = 2^num_qubits).
                       More qubits allow more options but increase complexity.

        Example:
            >>> decision_maker = QuantumDecisionMaker(num_qubits=3)
            >>> # Can handle up to 8 decision options
        """
        self.engine = QuantumCognitionEngine(num_qubits=num_qubits)
        self.num_qubits = num_qubits

        logger.info("quantum_decision_maker_initialized", max_options=2**num_qubits)

    def make_decision(
        self, options: List[str], weights: Optional[List[float]] = None
    ) -> SuperpositionDecision:
        """
        Create a quantum superposition decision from multiple options.

        Encodes decision options into a quantum state, allowing parallel
        consideration of all possibilities until measurement.

        Consciousness Modeling:
        Represents the pre-decision state where consciousness holds
        multiple possibilities in superposition before choosing.

        Args:
            options: List of decision options (strings)
            weights: Optional bias weights for non-uniform decision probabilities.
                    Currently maps to qubit-level biasing (simplified implementation).

        Returns:
            SuperpositionDecision object ready for collapse.

        Raises:
            ValueError: If too many options for available qubits.

        Example:
            >>> options = ["Invest in stocks", "Buy bonds", "Keep cash"]
            >>> decision = decision_maker.make_decision(options)
            >>> choice = decision.collapse()
            >>> print(f"Quantum chose: {choice}")
        """
        if len(options) > 2**self.num_qubits:
            raise ValueError(f"Too many options ({len(options)}). Max is {2 ** self.num_qubits}")

        if not QISKIT_AVAILABLE:
            logger.warning("qiskit_not_available_fallback")
            # Classical fallback when quantum unavailable
            state = QuantumState(num_qubits=self.num_qubits)
            probs = {opt: 1.0 / len(options) for opt in options}
            return SuperpositionDecision(options=options, quantum_state=state, probabilities=probs)

        # Create superposition circuit with optional biasing
        qubit_weights = None
        if weights:
            # Map option weights to qubit biases (simplified)
            qubit_weights = weights[: self.num_qubits]
            while len(qubit_weights) < self.num_qubits:
                qubit_weights.append(0.5)  # Default to uniform

        circuit = self.engine.create_superposition(weights=qubit_weights)

        # Extract quantum state
        q_state = self.engine.get_statevector(circuit)

        # Map quantum probabilities to decision options
        option_probs: Dict[str, float] = {}
        for idx, option in enumerate(options):
            # Sum probabilities for basis states mapping to this option
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
        Demonstrate quantum entanglement with measurement statistics.

        Creates an entangled Bell state and measures it multiple times
        to show the characteristic correlations.

        Consciousness Research:
        Entanglement demonstrates how cognitive elements can be correlated
        without local causation, potentially modeling binding in perception.

        Returns:
            Tuple of (quantum_circuit, measurement_counts).
            Bell state should show ~50% "00" and ~50% "11" outcomes.

        Raises:
            ImportError: If Qiskit is not available.

        Example:
            >>> circuit, counts = decision_maker.demonstrate_entanglement()
            >>> print(counts)  # Should show Bell state correlations
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        circuit = self.engine.create_entanglement(0, 1)
        counts = self.engine.measure_circuit(circuit, shots=1000)

        logger.info("entanglement_demonstrated", counts=counts)

        return circuit, counts

    def demonstrate_superposition(self) -> Tuple[QuantumCircuit, Dict[str, int]]:
        """
        Demonstrate quantum superposition with measurement statistics.

        Creates a superposition state and measures it to show uniform
        probability distribution across basis states.

        Consciousness Relevance:
        Shows how quantum systems can exist in multiple states simultaneously,
        potentially modeling parallel cognitive processing.

        Returns:
            Tuple of (quantum_circuit, measurement_counts).
            Superposition should show roughly equal probabilities.

        Raises:
            ImportError: If Qiskit is not available.
        """
        if not QISKIT_AVAILABLE:
            raise ImportError(QISKIT_ERROR_MSG)

        circuit = self.engine.create_superposition()
        counts = self.engine.measure_circuit(circuit, shots=1000)

        logger.info("superposition_demonstrated", counts=counts)

        return circuit, counts

    def analyze_decision_patterns(self, decisions: List[SuperpositionDecision]) -> Dict[str, Any]:
        """
        Analyze patterns in quantum decision making.

        Studies multiple decisions to identify patterns, biases, or
        quantum effects in the decision-making process.

        Consciousness Research:
        Can reveal whether quantum effects influence decision patterns
        or if decisions show characteristics of quantum cognition.

        Args:
            decisions: List of completed SuperpositionDecision objects

        Returns:
            Dictionary with analysis results including:
            - Average entropy of decision states
            - Pattern consistency metrics
            - Quantum vs classical decision characteristics
        """
        if not decisions:
            return {"error": "No decisions to analyze"}

        # Analyze decision patterns
        entropies = [d.get_decision_entropy() for d in decisions]
        confidences = [d.confidence for d in decisions if d.final_decision]

        analysis = {
            "total_decisions": len(decisions),
            "avg_entropy": float(np.mean(entropies)) if entropies else 0.0,
            "avg_confidence": float(np.mean(confidences)) if confidences else 0.0,
            "entropy_std": np.std(entropies).astype(float) if entropies else 0.0,
            "confidence_std": np.std(confidences).astype(float) if confidences else 0.0,
        }

        # Check for quantum characteristics
        if analysis["avg_entropy"] > 1.0:  # Higher than classical random
            analysis["quantum_signature"] = "high_entropy"
        else:
            analysis["quantum_signature"] = "classical_like"

        logger.info("decision_patterns_analyzed", **analysis)

        return analysis

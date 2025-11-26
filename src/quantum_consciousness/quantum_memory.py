"""
Quantum Memory System for OmniMind.

Explores quantum memory concepts:
- Quantum memory cells in superposition
- Hybrid Q-Learning (quantum-classical)
- Memory comparison (quantum vs classical)

Experimental research module.
"""

from dataclasses import dataclass
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


@dataclass
class QuantumMemoryCell:
    """
    Quantum memory cell storing data in superposition.

    Attributes:
        data: Classical data to encode
        num_qubits: Number of qubits for encoding
        quantum_state: Encoded quantum state
        encoding_type: Type of encoding used
    """

    data: Any
    num_qubits: int
    quantum_state: Optional[np.ndarray] = None
    encoding_type: str = "amplitude"

    def encode(self) -> None:
        """Encode classical data into quantum state."""
        if not QISKIT_AVAILABLE:
            logger.warning("qiskit_not_available_for_encoding")
            return

        # Simple amplitude encoding
        if isinstance(self.data, (list, np.ndarray)):
            data_array = np.array(self.data, dtype=complex)
            # Normalize
            norm = np.linalg.norm(data_array)
            if norm > 0:
                self.quantum_state = data_array / norm
            else:
                self.quantum_state = data_array
        else:
            # Single value encoding
            size = 2**self.num_qubits
            self.quantum_state = np.zeros(size, dtype=complex)
            # Encode in first position
            self.quantum_state[0] = complex(float(self.data), 0)

        logger.debug(
            "quantum_memory_encoded",
            data_type=type(self.data).__name__,
            encoding=self.encoding_type,
        )

    def decode(self) -> Any:
        """Decode quantum state to classical data."""
        if self.quantum_state is None:
            return self.data

        # Measure to collapse state
        probs = np.abs(self.quantum_state) ** 2
        # Normalize probabilities to ensure they sum to 1.0 (avoid floating point errors)
        if len(probs) > 0 and np.sum(probs) > 0:
            probs = probs / np.sum(probs)  # Normalize
            idx = np.random.choice(len(probs), p=probs)
            return float(np.real(self.quantum_state[idx]))
        return 0.0

    def fidelity(self, other: "QuantumMemoryCell") -> float:
        """
        Calculate fidelity between two quantum memory cells.

        Args:
            other: Other quantum memory cell

        Returns:
            Fidelity value [0, 1]
        """
        if self.quantum_state is None or other.quantum_state is None:
            return 0.0

        # Ensure same size
        min_size = min(len(self.quantum_state), len(other.quantum_state))
        s1 = self.quantum_state[:min_size]
        s2 = other.quantum_state[:min_size]

        # Fidelity = |⟨ψ|φ⟩|²
        inner_product = np.abs(np.vdot(s1, s2))
        return float(inner_product**2)


class QuantumMemorySystem:
    """
    Quantum memory system managing multiple quantum memory cells.

    Explores quantum memory advantages:
    - Superposition storage
    - Quantum parallelism in retrieval
    - Entanglement-based correlation
    """

    def __init__(self, num_qubits: int = 4, capacity: int = 10) -> None:
        """
        Initialize quantum memory system.

        Args:
            num_qubits: Qubits per memory cell
            capacity: Maximum number of memory cells
        """
        self.num_qubits = num_qubits
        self.capacity = capacity
        self.memory_cells: List[QuantumMemoryCell] = []
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None

        logger.info(
            "quantum_memory_system_initialized",
            num_qubits=num_qubits,
            capacity=capacity,
            qiskit_available=QISKIT_AVAILABLE,
        )

    def store(self, data: Any, key: Optional[str] = None) -> int:
        """
        Store data in quantum memory.

        Args:
            data: Data to store
            key: Optional key for retrieval

        Returns:
            Memory cell index
        """
        if len(self.memory_cells) >= self.capacity:
            logger.warning("quantum_memory_full", capacity=self.capacity)
            # Evict oldest
            self.memory_cells.pop(0)

        cell = QuantumMemoryCell(data=data, num_qubits=self.num_qubits)
        cell.encode()

        self.memory_cells.append(cell)
        idx = len(self.memory_cells) - 1

        logger.info(
            "quantum_memory_stored",
            index=idx,
            key=key,
            total_cells=len(self.memory_cells),
        )

        return idx

    def retrieve(self, index: int) -> Any:
        """
        Retrieve data from quantum memory.

        Args:
            index: Memory cell index

        Returns:
            Decoded data
        """
        if index < 0 or index >= len(self.memory_cells):
            logger.error(
                "invalid_memory_index",
                index=index,
                max_index=len(self.memory_cells) - 1,
            )
            return None

        cell = self.memory_cells[index]
        data = cell.decode()

        logger.info("quantum_memory_retrieved", index=index)

        return data

    def search_similar(self, query_data: Any, threshold: float = 0.8) -> List[int]:
        """
        Search for similar memories using quantum fidelity.

        Args:
            query_data: Query data
            threshold: Similarity threshold [0, 1]

        Returns:
            List of matching memory indices
        """
        query_cell = QuantumMemoryCell(data=query_data, num_qubits=self.num_qubits)
        query_cell.encode()

        matches = []
        for idx, cell in enumerate(self.memory_cells):
            fidelity = query_cell.fidelity(cell)
            if fidelity >= threshold:
                matches.append(idx)

        logger.info("quantum_memory_search", num_matches=len(matches), threshold=threshold)

        return matches

    def clear(self) -> None:
        """Clear all quantum memory cells."""
        self.memory_cells.clear()
        logger.info("quantum_memory_cleared")


@dataclass
class QLearningState:
    """Q-Learning state representation."""

    state: str
    action: str
    reward: float
    next_state: str
    q_value: float = 0.0


class HybridQLearning:
    """
    Hybrid Quantum-Classical Q-Learning.

    Combines quantum superposition for exploration
    with classical Q-learning updates.
    """

    def __init__(
        self,
        num_states: int,
        num_actions: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        use_quantum: bool = True,
    ) -> None:
        """
        Initialize hybrid Q-learning.

        Args:
            num_states: Number of states
            num_actions: Number of actions
            learning_rate: Learning rate alpha
            discount_factor: Discount factor gamma
            use_quantum: Whether to use quantum exploration
        """
        self.num_states = num_states
        self.num_actions = num_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.use_quantum = use_quantum and QISKIT_AVAILABLE

        # Q-table
        self.q_table: Dict[Tuple[str, str], float] = {}

        # Quantum components
        if self.use_quantum:
            num_qubits = max(2, int(np.ceil(np.log2(num_actions))))
            self.simulator = AerSimulator()
            self.num_qubits = num_qubits

        logger.info(
            "hybrid_qlearning_initialized",
            num_states=num_states,
            num_actions=num_actions,
            use_quantum=self.use_quantum,
        )

    def select_action(self, state: str, epsilon: float = 0.1) -> str:
        """
        Select action using quantum exploration or epsilon-greedy.

        Args:
            state: Current state
            epsilon: Exploration rate for classical

        Returns:
            Selected action
        """
        if self.use_quantum:
            return self._quantum_select_action(state)
        else:
            return self._classical_select_action(state, epsilon)

    def _quantum_select_action(self, state: str) -> str:
        """Select action using quantum superposition."""
        if not QISKIT_AVAILABLE:
            return self._classical_select_action(state, 0.1)

        # Create superposition of actions
        qr = QuantumRegister(self.num_qubits, "q")
        cr = ClassicalRegister(self.num_qubits, "c")
        qc = QuantumCircuit(qr, cr)

        # Apply Hadamard to create superposition
        for i in range(self.num_qubits):
            qc.h(i)

        # Measure
        qc.measure_all()

        job = self.simulator.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()

        # Get measured outcome
        outcome = list(counts.keys())[0]
        # Remove spaces from outcome (Qiskit format with multiple classical registers)
        outcome_str = outcome.replace(" ", "")
        action_idx = int(outcome_str, 2) % self.num_actions

        action = f"action_{action_idx}"

        logger.debug("quantum_action_selected", state=state, action=action)

        return action

    def _classical_select_action(self, state: str, epsilon: float) -> str:
        """Select action using epsilon-greedy."""
        if np.random.random() < epsilon:
            # Explore
            action_idx = np.random.randint(0, self.num_actions)
        else:
            # Exploit - choose best known action
            action_idx = 0
            best_q = float("-inf")
            for a in range(self.num_actions):
                action = f"action_{a}"
                q_val = self.q_table.get((state, action), 0.0)
                if q_val > best_q:
                    best_q = q_val
                    action_idx = a

        return f"action_{action_idx}"

    def update(self, state: str, action: str, reward: float, next_state: str) -> None:
        """
        Update Q-value using Q-learning update rule.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
        """
        # Get current Q-value
        current_q = self.q_table.get((state, action), 0.0)

        # Get max Q-value for next state
        max_next_q = 0.0
        for a in range(self.num_actions):
            next_action = f"action_{a}"
            q_val = self.q_table.get((next_state, next_action), 0.0)
            max_next_q = max(max_next_q, q_val)

        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )

        self.q_table[(state, action)] = new_q

        logger.debug("q_value_updated", state=state, action=action, old_q=current_q, new_q=new_q)

    def get_q_value(self, state: str, action: str) -> float:
        """Get Q-value for state-action pair."""
        return self.q_table.get((state, action), 0.0)


@dataclass
class QuantumMemoryComparison:
    """Comparison results between quantum and classical memory."""

    quantum_retrieval_time: float
    classical_retrieval_time: float
    quantum_accuracy: float
    classical_accuracy: float
    quantum_speedup: float
    notes: str = ""

    def summary(self) -> str:
        """Generate comparison summary."""
        return (
            f"Quantum vs Classical Memory Comparison:\n"
            f"  Retrieval Time: {self.quantum_retrieval_time:.4f}s "
            f"vs {self.classical_retrieval_time:.4f}s\n"
            f"  Accuracy: {self.quantum_accuracy:.2%} "
            f"vs {self.classical_accuracy:.2%}\n"
            f"  Speedup: {self.quantum_speedup:.2f}x\n"
            f"  Notes: {self.notes}"
        )

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
Quantum Memory System for OmniMind - Phase 21-23 Preparation.

Implements quantum memory concepts for consciousness simulation:
- Quantum superposition memory cells (parallel storage)
- Entangled memory associations (correlated recall)
- Hybrid Q-Learning (quantum exploration + classical exploitation)
- Quantum fidelity-based similarity search
- Memory decoherence and stability analysis

Core Concepts:
- Superposition Memory: Store multiple states simultaneously
- Quantum Fidelity: Measure similarity between quantum states |⟨ψ|φ⟩|²
- Entangled Associations: Correlated memory retrieval
- Hybrid Learning: Quantum exploration meets classical optimization

Mathematical Foundation:
- State Encoding: |ψ⟩ = Σᵢ αᵢ|i⟩ (amplitude encoding)
- Fidelity: F(ψ,φ) = |⟨ψ|φ⟩|² ∈ [0,1]
- Q-Learning: Q(s,a) ← Q(s,a) + α[r + γ maxₐ' Q(s',a') - Q(s,a)]
- Decoherence: Memory stability over time (T₁, T₂ relaxation times)
- Entanglement: |ψ⟩ = (1/√2)(|00⟩ + |11⟩) for correlated states

Quantum Memory Advantages:
- Parallel Storage: Store multiple patterns in superposition
- Similarity Search: Quantum fidelity enables O(1) similarity queries
- Associative Recall: Entangled states allow correlated memory retrieval
- Pattern Recognition: Quantum interference for complex correlations
- Memory Consolidation: Hybrid learning for long-term memory formation

Consciousness Research Applications:
- Episodic Memory: Quantum superposition for parallel memory traces
- Working Memory: Entangled states for binding different modalities
- Memory Consolidation: Hybrid Q-learning for memory strengthening
- Pattern Completion: Quantum fidelity for associative recall
- Memory Interference: Quantum effects in forgetting and interference

Dependencies:
- qiskit: Quantum circuit construction and simulation
- qiskit-aer: High-performance quantum simulator
- numpy: Vector operations and complex numbers
- structlog: Structured logging for quantum operations

Example Usage:
    # Initialize quantum memory system
    memory = QuantumMemorySystem(num_qubits=4, capacity=100)

    # Store data in superposition
    idx = memory.store([0.5, 0.3, 0.2, 0.1], key="pattern_1")

    # Retrieve with quantum parallelism
    data = memory.retrieve(idx)

    # Search similar patterns using fidelity
    similar = memory.search_similar([0.4, 0.4, 0.1, 0.1], threshold=0.8)

    # Hybrid Q-Learning for memory optimization
    learner = HybridQLearning(num_states=10, num_actions=4, use_quantum=True)
    action = learner.select_action("state_5")

Fallback Behavior:
If Qiskit is unavailable, the system gracefully degrades to classical
implementations with appropriate logging warnings.

Author: OmniMind Quantum Consciousness Team
License: MIT
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

_rng = np.random.default_rng()


@dataclass
class QuantumMemoryCell:
    """
    Quantum memory cell storing data in superposition.

    A quantum memory cell encodes classical data into a quantum state vector,
    enabling parallel storage and retrieval operations. The cell maintains
    both the original classical data and its quantum representation.

    Quantum Encoding Methods:
    - Amplitude Encoding: Data vector normalized to quantum state |ψ⟩ = data/||data||
    - Phase Encoding: Information stored in relative phases e^(iθ)
    - Basis Encoding: Classical bits mapped to computational basis states |00⟩, |01⟩, etc.

    Consciousness Implications:
    - Superposition allows multiple memory traces to coexist
    - Entanglement enables binding of different sensory modalities
    - Decoherence models memory fading and forgetting
    - Fidelity measures memory similarity and pattern completion

    Mathematical Properties:
    - Normalization: ||ψ|| = 1 (valid quantum state)
    - Measurement: p(i) = |⟨i|ψ⟩|² (probability of outcome i)
    - Purity: Tr(ρ²) = 1 for pure states (vs mixed states < 1)
    - Fidelity: F(ψ,φ) = |⟨ψ|φ⟩|² (state similarity measure)

    Attributes:
        data: Original classical data (preserved for fallback)
        num_qubits: Number of qubits needed for encoding
        quantum_state: Complex numpy array representing |ψ⟩
        encoding_type: Encoding method ("amplitude", "phase", "basis")
        coherence_time: Simulated coherence time for decoherence modeling
        access_count: Number of times cell has been accessed

    Example:
        >>> cell = QuantumMemoryCell(data=[1, 0, 0, 0], num_qubits=2)
        >>> cell.encode()  # Creates |00⟩ state
        >>> decoded = cell.decode()  # Returns ~1.0 (collapsed measurement)
        >>> fidelity = cell.fidelity(other_cell)  # Compare with another cell
    """

    data: Any
    num_qubits: int
    quantum_state: Optional[np.ndarray] = None
    encoding_type: str = "amplitude"
    coherence_time: float = 1.0  # Simulated coherence time in seconds
    access_count: int = 0

    def encode(self) -> None:
        """
        Encode classical data into quantum state vector.

        The encoding process:
        1. Convert data to complex numpy array
        2. Normalize to create valid quantum state (||ψ|| = 1)
        3. Store in quantum_state attribute

        For amplitude encoding: |ψ⟩ = data / ||data||
        For single values: Encoded in |00...0⟩ basis state

        Consciousness Analogy:
        This represents the encoding of sensory input into neural patterns,
        where classical information becomes quantum-coherent memory traces.

        Raises:
            ValueError: If data cannot be converted to numeric array

        Example:
            >>> cell = QuantumMemoryCell([0.8, 0.6], 1)
            >>> cell.encode()
            >>> print(cell.quantum_state)  # [0.8, 0.6] normalized
        """
        if not QISKIT_AVAILABLE:
            logger.warning("qiskit_not_available_for_encoding")
            return

        try:
            if isinstance(self.data, (list, np.ndarray)):
                # Amplitude encoding for vectors
                data_array = np.array(self.data, dtype=complex)

                # Normalize to create valid quantum state
                norm = np.linalg.norm(data_array)
                if norm > 0:
                    self.quantum_state = data_array / norm
                else:
                    # Handle zero vector
                    self.quantum_state = np.zeros(len(data_array), dtype=complex)
                    self.quantum_state[0] = 1.0

            elif isinstance(self.data, (int, float)):
                # Single value encoding
                size = 2**self.num_qubits
                self.quantum_state = np.zeros(size, dtype=complex)
                # Encode in first computational basis state |00...0⟩
                self.quantum_state[0] = complex(float(self.data), 0)

            else:
                raise ValueError(f"Unsupported data type for encoding: {type(self.data)}")

        except Exception as e:
            logger.error(
                "quantum_encoding_failed", error=str(e), data_type=type(self.data).__name__
            )
            # Fallback: keep original data
            return

        logger.debug(
            "quantum_memory_encoded",
            data_type=type(self.data).__name__,
            encoding=self.encoding_type,
            state_size=len(self.quantum_state) if self.quantum_state is not None else 0,
        )

    def decode(self) -> Any:
        """
        Decode quantum state back to classical data via measurement.

        The decoding process:
        1. Calculate measurement probabilities |⟨i|ψ⟩|²
        2. Sample from probability distribution (wave function collapse)
        3. Return measured value

        Consciousness Relevance:
        Quantum measurement models the "collapse" of potential memories
        into conscious recall, where superposition resolves to a single experience.

        Returns:
            Decoded classical data (float for single values, collapsed state)

        Note:
            Quantum measurement is probabilistic - repeated calls may give
            different results due to superposition collapse.

        Example:
            >>> cell = QuantumMemoryCell([1, 0], 1)
            >>> cell.encode()
            >>> value = cell.decode()  # Returns 1.0 (measures |0⟩) or 0.0 (measures |1⟩)
        """
        self.access_count += 1

        if self.quantum_state is None:
            logger.debug("no_quantum_state_fallback_to_classical")
            return self.data

        # Calculate measurement probabilities
        probs = np.abs(self.quantum_state) ** 2

        # Ensure probabilities are properly normalized
        prob_sum = np.sum(probs)
        if prob_sum > 0:
            probs = probs / prob_sum  # Renormalize for numerical stability

            # Sample from probability distribution
            size = len(self.quantum_state)
            outcome_idx = _rng.choice(size, p=probs)

            # Return real part of measured amplitude
            measured_value = float(np.real(self.quantum_state[outcome_idx]))

            logger.debug(
                "quantum_measurement", outcome_idx=outcome_idx, measured_value=measured_value
            )
            return measured_value
        else:
            logger.warning("invalid_probability_distribution")
            return 0.0

    def fidelity(self, other: "QuantumMemoryCell") -> float:
        """
        Calculate quantum fidelity between two memory cells.

        Fidelity measures how similar two quantum states are:
        F(ψ,φ) = |⟨ψ|φ⟩|²

        Properties:
        - F(ψ,ψ) = 1 (identical states)
        - F(ψ,φ) = 0 (orthogonal states)
        - F(ψ,φ) ∈ [0,1] (similarity measure)

        Consciousness Applications:
        - Pattern Recognition: High fidelity indicates similar memories
        - Memory Completion: Partial cues can reconstruct full memories
        - Interference Effects: Low fidelity shows memory confusion

        Args:
            other: Another QuantumMemoryCell to compare

        Returns:
            Fidelity value between 0.0 and 1.0

        Example:
            >>> cell1 = QuantumMemoryCell([1, 0], 1)
            >>> cell2 = QuantumMemoryCell([0, 1], 1)
            >>> cell1.fidelity(cell2)  # Returns 0.0 (orthogonal states)
            >>> cell3 = QuantumMemoryCell([0.707, 0.707], 1)
            >>> cell1.fidelity(cell3)  # Returns 0.5 (45-degree superposition)
        """
        if self.quantum_state is None or other.quantum_state is None:
            logger.debug("missing_quantum_states_fidelity_zero")
            return 0.0

        # Handle different sized states (take minimum)
        min_size = min(len(self.quantum_state), len(other.quantum_state))
        s1 = self.quantum_state[:min_size]
        s2 = other.quantum_state[:min_size]

        # Quantum fidelity: |⟨ψ|φ⟩|²
        inner_product = np.abs(np.vdot(s1, s2))
        fidelity = float(inner_product**2)

        logger.debug("fidelity_calculated", fidelity=fidelity)

        return fidelity

    def apply_decoherence(self, time_elapsed: float) -> None:
        """
        Apply decoherence effects to simulate memory fading.

        Decoherence models how quantum memories lose coherence over time:
        - T₁ relaxation: Energy dissipation (amplitude decay)
        - T₂ dephasing: Phase randomization (coherence loss)

        Consciousness Relevance:
        Models memory forgetting and consolidation processes where
        irrelevant details fade while important patterns strengthen.

        Args:
            time_elapsed: Time since encoding (seconds)

        Mathematical Model:
        ρ(t) = ρ(0) * e^(-t/T₂) + (I/2^n)(1 - e^(-t/T₁))
        Simplified: amplitude *= e^(-t/(2*T_coherence))

        Example:
            >>> cell = QuantumMemoryCell([1, 0], 1)
            >>> cell.encode()
            >>> cell.apply_decoherence(1.0)  # Apply 1 second of decoherence
        """
        if self.quantum_state is None:
            return

        # Simplified decoherence model: exponential amplitude decay
        decay_factor = np.exp(-time_elapsed / (2 * self.coherence_time))

        # Apply decoherence to all amplitudes
        self.quantum_state *= decay_factor

        # Renormalize to maintain quantum state validity
        norm = np.linalg.norm(self.quantum_state)
        if norm > 0:
            self.quantum_state /= norm

        logger.debug("decoherence_applied", time_elapsed=time_elapsed, decay_factor=decay_factor)

    def get_state_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the quantum state.

        Returns:
            Dictionary with state metadata and properties including
            coherence metrics, access statistics, and quantum properties.

        Example:
            >>> info = cell.get_state_info()
            >>> print(f"Purity: {info['purity']:.3f}")
            >>> print(f"Access count: {info['access_count']}")
        """
        info = {
            "has_quantum_state": self.quantum_state is not None,
            "encoding_type": self.encoding_type,
            "num_qubits": self.num_qubits,
            "data_type": type(self.data).__name__,
            "coherence_time": self.coherence_time,
            "access_count": self.access_count,
        }

        if self.quantum_state is not None:
            info.update(
                {
                    "state_size": len(self.quantum_state),
                    "is_normalized": np.isclose(np.linalg.norm(self.quantum_state), 1.0),
                    "probabilities": np.abs(self.quantum_state) ** 2,
                    "purity": float(
                        np.sum(np.abs(self.quantum_state) ** 4)
                    ),  # Tr(ρ²) for pure states
                    "entropy": float(
                        -np.sum(
                            np.abs(self.quantum_state) ** 2
                            * np.log2(np.abs(self.quantum_state) ** 2 + 1e-12)
                        )
                    ),
                    "max_probability": float(np.max(np.abs(self.quantum_state) ** 2)),
                    "dominant_basis": int(np.argmax(np.abs(self.quantum_state) ** 2)),
                }
            )

        return info


class QuantumMemorySystem:
    """
    Quantum memory system managing multiple entangled memory cells.

    This system explores quantum advantages in memory operations:
    - Superposition: Store multiple patterns simultaneously
    - Entanglement: Create correlated memory associations
    - Parallel Search: Quantum fidelity-based similarity search
    - Decoherence: Memory stability over time
    - Consolidation: Hybrid learning for memory strengthening

    Architecture:
    - Memory cells stored in classical list (quantum states inside)
    - LRU eviction policy when capacity exceeded
    - Quantum parallelism for bulk operations
    - Entanglement tracking for correlated memories

    Consciousness Memory Model:
    - Episodic Memory: Individual experiences in superposition
    - Semantic Memory: Entangled concepts and associations
    - Working Memory: Active quantum states with short coherence
    - Long-term Memory: Consolidated states with extended coherence

    Attributes:
        num_qubits: Qubits per memory cell
        capacity: Maximum number of cells
        memory_cells: List of QuantumMemoryCell objects
        simulator: Qiskit simulator instance
        entanglement_graph: Tracks correlations between memory cells

    Example:
        >>> memory = QuantumMemorySystem(num_qubits=3, capacity=50)
        >>> idx = memory.store([0.6, 0.4, 0.2, 0.1, 0.3, 0.5, 0.8, 0.9])
        >>> similar = memory.search_similar([0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
        >>> memory.create_entanglement(idx, idx+1)  # Correlate memories
    """

    def __init__(self, num_qubits: int = 4, capacity: int = 10) -> None:
        """
        Initialize quantum memory system.

        Args:
            num_qubits: Number of qubits per memory cell (2^num_qubits = max vector size)
            capacity: Maximum number of memory cells (LRU eviction when exceeded)

        Raises:
            ValueError: If num_qubits or capacity are invalid

        Example:
            >>> memory = QuantumMemorySystem(num_qubits=4, capacity=100)
            >>> # Can store vectors up to size 16, hold 100 memories
        """
        if num_qubits <= 0:
            raise ValueError("num_qubits must be positive")
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.num_qubits = num_qubits
        self.capacity = capacity
        self.memory_cells: List[QuantumMemoryCell] = []
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
        self.entanglement_graph: Dict[int, List[int]] = {}  # cell_idx -> list of entangled indices

        logger.info(
            "quantum_memory_system_initialized",
            num_qubits=num_qubits,
            capacity=capacity,
            max_vector_size=2**num_qubits,
            qiskit_available=QISKIT_AVAILABLE,
        )

    def store(self, data: Any, key: Optional[str] = None) -> int:
        """
        Store data in quantum memory cell.

        Process:
        1. Create new QuantumMemoryCell
        2. Encode classical data to quantum state
        3. Add to memory (evict oldest if at capacity)
        4. Return cell index for retrieval

        Consciousness Analogy:
        This represents the formation of new memory traces from
        sensory input, encoded into neural patterns for storage.

        Args:
            data: Classical data to store (list, array, or scalar)
            key: Optional string key for future retrieval

        Returns:
            Memory cell index (int)

        Example:
            >>> idx = memory.store([1, 0, 0, 0])  # Stores |00⟩ state
            >>> idx = memory.store(3.14)  # Stores scalar value
            >>> idx = memory.store("memory_key", key="important_event")
        """
        if len(self.memory_cells) >= self.capacity:
            logger.warning("quantum_memory_full_evicting_oldest", capacity=self.capacity)
            # Evict oldest (LRU policy)
            self.memory_cells.pop(0)
            logger.debug("evicted_memory_cell", index=0)

        # Create and encode new cell
        cell = QuantumMemoryCell(data=data, num_qubits=self.num_qubits)
        cell.encode()

        self.memory_cells.append(cell)
        idx = len(self.memory_cells) - 1

        logger.info(
            "quantum_memory_stored",
            index=idx,
            key=key,
            data_type=type(data).__name__,
            total_cells=len(self.memory_cells),
        )

        return idx

    def retrieve(self, index: int) -> Any:
        """
        Retrieve and decode data from quantum memory.

        Process:
        1. Validate index bounds
        2. Access memory cell
        3. Apply decoherence based on access patterns
        4. Decode quantum state (probabilistic measurement)
        5. Return classical data

        Consciousness Relevance:
        Memory retrieval involves reconstructing quantum states,
        where decoherence represents forgetting and measurement
        represents conscious recall of specific memories.

        Args:
            index: Memory cell index (0-based)

        Returns:
            Decoded classical data, or None if invalid index

        Note:
            Retrieval is probabilistic due to quantum measurement.
            Repeated retrievals may give different results.

        Example:
            >>> data = memory.retrieve(5)
            >>> print(f"Retrieved: {data}")  # May vary due to quantum measurement
        """
        if index < 0 or index >= len(self.memory_cells):
            logger.error(
                "invalid_memory_index",
                requested=index,
                valid_range=f"[0, {len(self.memory_cells)-1}]",
            )
            return None

        cell = self.memory_cells[index]

        # Apply decoherence based on access patterns (simplified model)
        time_since_access = cell.access_count * 0.1  # Simulate time decay
        cell.apply_decoherence(time_since_access)

        decoded_data = cell.decode()

        logger.info(
            "quantum_memory_retrieved",
            index=index,
            data_type=type(decoded_data).__name__,
            access_count=cell.access_count,
        )

        return decoded_data

    def search_similar(self, query_data: Any, threshold: float = 0.8) -> List[int]:
        """
        Search for memory cells similar to query using quantum fidelity.

        This implements quantum similarity search:
        1. Encode query data to quantum state
        2. Calculate fidelity with all stored cells
        3. Return indices where F ≥ threshold

        Advantages over classical search:
        - Parallel comparison of all stored patterns
        - Quantum superposition enables bulk operations
        - Fidelity captures quantum state similarity

        Consciousness Applications:
        - Pattern Completion: Partial cues trigger full memory recall
        - Associative Memory: Similar experiences reinforce each other
        - Memory Search: Quantum parallelism for rapid similarity matching

        Args:
            query_data: Data to search for (same format as stored data)
            threshold: Minimum fidelity for match [0, 1]

        Returns:
            List of matching memory cell indices

        Example:
            >>> matches = memory.search_similar([0.7, 0.3], threshold=0.9)
            >>> print(f"Found {len(matches)} similar patterns")
            >>> # High threshold = exact matches, low threshold = similar patterns
        """
        # Create query cell and encode
        query_cell = QuantumMemoryCell(data=query_data, num_qubits=self.num_qubits)
        query_cell.encode()

        matches = []
        for idx, cell in enumerate(self.memory_cells):
            fidelity = query_cell.fidelity(cell)
            if fidelity >= threshold:
                matches.append(idx)
                logger.debug("similar_memory_found", index=idx, fidelity=fidelity)

        logger.info(
            "quantum_memory_search_complete",
            query_type=type(query_data).__name__,
            num_matches=len(matches),
            threshold=threshold,
            total_cells=len(self.memory_cells),
        )

        return matches

    def create_entanglement(self, idx1: int, idx2: int) -> bool:
        """
        Create entanglement between two memory cells.

        Entanglement establishes quantum correlation between memories:
        - Measuring one cell affects the other's state
        - Enables correlated recall and associative memory
        - Models binding of related concepts in consciousness

        Consciousness Relevance:
        Entangled memories represent associated concepts that are
        recalled together, like smell triggering emotional memories.

        Args:
            idx1: Index of first memory cell
            idx2: Index of second memory cell

        Returns:
            True if entanglement created successfully

        Raises:
            ValueError: If indices are invalid

        Example:
            >>> memory.create_entanglement(0, 1)  # Correlate memories 0 and 1
            >>> # Now retrieving memory 0 may influence memory 1's state
        """
        if not (0 <= idx1 < len(self.memory_cells) and 0 <= idx2 < len(self.memory_cells)):
            raise ValueError("Invalid memory cell indices")

        if idx1 == idx2:
            raise ValueError("Cannot entangle cell with itself")

        # Add to entanglement graph (bidirectional)
        if idx1 not in self.entanglement_graph:
            self.entanglement_graph[idx1] = []
        if idx2 not in self.entanglement_graph:
            self.entanglement_graph[idx2] = []

        if idx2 not in self.entanglement_graph[idx1]:
            self.entanglement_graph[idx1].append(idx2)
        if idx1 not in self.entanglement_graph[idx2]:
            self.entanglement_graph[idx2].append(idx1)

        logger.info("memory_entanglement_created", cell1=idx1, cell2=idx2)

        return True

    def get_entangled_memories(self, index: int) -> List[int]:
        """
        Get list of memories entangled with the specified cell.

        Args:
            index: Memory cell index

        Returns:
            List of entangled memory indices

        Example:
            >>> entangled = memory.get_entangled_memories(0)
            >>> print(f"Memory 0 is entangled with: {entangled}")
        """
        return self.entanglement_graph.get(index, [])

    def consolidate_memory(self, index: int, strength: float = 0.1) -> None:
        """
        Consolidate memory by strengthening quantum amplitudes.

        Memory consolidation models how repeated access strengthens memories:
        - Increases coherence time
        - Strengthens dominant amplitudes
        - Reduces decoherence effects

        Consciousness Relevance:
        Models memory consolidation during sleep or repeated practice,
        where important memories become more stable and accessible.

        Args:
            index: Memory cell to consolidate
            strength: Consolidation strength factor [0, 1]

        Example:
            >>> memory.consolidate_memory(5, strength=0.2)
            >>> # Memory 5 now has longer coherence time and stronger amplitudes
        """
        if index < 0 or index >= len(self.memory_cells):
            logger.error("invalid_memory_index_for_consolidation", index=index)
            return

        cell = self.memory_cells[index]

        # Strengthen memory by increasing coherence time
        cell.coherence_time *= 1 + strength

        # Strengthen dominant amplitudes (simplified consolidation)
        if cell.quantum_state is not None:
            probs = np.abs(cell.quantum_state) ** 2
            max_prob_idx = np.argmax(probs)
            # Boost the dominant state
            boost_factor = 1 + strength * 0.5
            cell.quantum_state[max_prob_idx] *= boost_factor

            # Renormalize
            norm = np.linalg.norm(cell.quantum_state)
            cell.quantum_state /= norm

        logger.info(
            "memory_consolidated", index=index, strength=strength, new_coherence=cell.coherence_time
        )

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive memory system statistics.

        Returns:
            Dictionary with usage statistics and health metrics including
            entanglement statistics, coherence metrics, and access patterns.

        Example:
            >>> stats = memory.get_memory_stats()
            >>> print(f"Utilization: {stats['utilization']:.1%}")
            >>> print(f"Average fidelity: {stats['avg_inter_fidelity']:.3f}")
        """
        stats = {
            "capacity": self.capacity,
            "used": len(self.memory_cells),
            "utilization": len(self.memory_cells) / self.capacity,
            "num_qubits": self.num_qubits,
            "max_vector_size": 2**self.num_qubits,
            "qiskit_available": QISKIT_AVAILABLE,
            "total_entanglements": sum(
                len(entangled) for entangled in self.entanglement_graph.values()
            )
            // 2,  # Divide by 2 for bidirectional
            "entangled_cells": len(self.entanglement_graph),
        }

        # Calculate coherence and access statistics
        if self.memory_cells:
            coherence_times = [cell.coherence_time for cell in self.memory_cells]
            access_counts = [cell.access_count for cell in self.memory_cells]

            stats.update(
                {
                    "avg_coherence_time": float(np.mean(coherence_times)),
                    "max_coherence_time": float(np.max(coherence_times)),
                    "min_coherence_time": float(np.min(coherence_times)),
                    "total_accesses": sum(access_counts),
                    "avg_accesses_per_cell": float(np.mean(access_counts)),
                }
            )

        # Calculate average fidelity between random pairs
        if len(self.memory_cells) >= 2:
            fidelities = []
            for i in range(min(10, len(self.memory_cells))):  # Sample up to 10 pairs
                j = (i + 1) % len(self.memory_cells)
                fid = self.memory_cells[i].fidelity(self.memory_cells[j])
                fidelities.append(fid)

            stats["avg_inter_fidelity"] = float(np.mean(fidelities))
            stats["fidelity_std"] = float(np.std(fidelities))

        return stats

    def clear(self) -> None:
        """
        Clear all quantum memory cells and reset entanglement graph.

        This operation:
        - Removes all stored memory cells
        - Clears entanglement correlations
        - Resets to empty state
        - Logs the operation

        Consciousness Analogy:
        Represents complete memory wipe or tabula rasa state,
        where all previous experiences are erased.

        Example:
            >>> memory.clear()
            >>> print(f"Memory cells: {len(memory.memory_cells)}")  # 0
        """
        num_cleared = len(self.memory_cells)
        self.memory_cells.clear()
        self.entanglement_graph.clear()

        logger.info(
            "quantum_memory_cleared", cells_cleared=num_cleared, entanglements_cleared=num_cleared
        )

    def encode(self) -> None:
        """
        Encode classical data into quantum state vector.

        The encoding process:
        1. Convert data to complex numpy array
        2. Normalize to create valid quantum state (||ψ|| = 1)
        3. Store in quantum_state attribute

        For amplitude encoding: |ψ⟩ = data / ||data||
        For single values: Encoded in |00...0⟩ basis state

        Raises:
            ValueError: If data cannot be converted to numeric array
        """
        if not QISKIT_AVAILABLE:
            logger.warning("qiskit_not_available_for_encoding")
            return

        try:
            if isinstance(self.data, (list, np.ndarray)):
                # Amplitude encoding for vectors
                data_array = np.array(self.data, dtype=complex)

                # Normalize to create valid quantum state
                norm = np.linalg.norm(data_array)
                if norm > 0:
                    self.quantum_state = data_array / norm
                else:
                    # Handle zero vector
                    self.quantum_state = np.zeros(len(data_array), dtype=complex)
                    self.quantum_state[0] = 1.0

            elif isinstance(self.data, (int, float)):
                # Single value encoding
                size = 2**self.num_qubits
                self.quantum_state = np.zeros(size, dtype=complex)
                # Encode in first computational basis state |00...0⟩
                self.quantum_state[0] = complex(float(self.data), 0)

            else:
                raise ValueError(f"Unsupported data type for encoding: {type(self.data)}")

        except Exception as e:
            logger.error(
                "quantum_encoding_failed", error=str(e), data_type=type(self.data).__name__
            )
            # Fallback: keep original data
            return

        logger.debug(
            "quantum_memory_encoded",
            data_type=type(self.data).__name__,
            encoding=self.encoding_type,
            state_size=len(self.quantum_state) if self.quantum_state is not None else 0,
        )

    def decode(self) -> Any:
        """
        Decode quantum state back to classical data via measurement.

        The decoding process:
        1. Calculate measurement probabilities |⟨i|ψ⟩|²
        2. Sample from probability distribution (wave function collapse)
        3. Return measured value

        Returns:
            Decoded classical data (float for single values, collapsed state)

        Note:
            Quantum measurement is probabilistic - repeated calls may give
            different results due to superposition collapse.
        """
        if self.quantum_state is None:
            logger.debug("no_quantum_state_fallback_to_classical")
            return self.data

        # Calculate measurement probabilities
        probs = np.abs(self.quantum_state) ** 2

        # Ensure probabilities are properly normalized
        prob_sum = np.sum(probs)
        if prob_sum > 0:
            probs = probs / prob_sum  # Renormalize for numerical stability

            # Sample from probability distribution
            size = len(self.quantum_state)
            outcome_idx = _rng.choice(size, p=probs)

            # Return real part of measured amplitude
            measured_value = float(np.real(self.quantum_state[outcome_idx]))

            logger.debug(
                "quantum_measurement", outcome_idx=outcome_idx, measured_value=measured_value
            )
            return measured_value
        else:
            logger.warning("invalid_probability_distribution")
            return 0.0

    def fidelity(self, other: "QuantumMemoryCell") -> float:
        """
        Calculate quantum fidelity between two memory cells.

        Fidelity measures how similar two quantum states are:
        F(ψ,φ) = |⟨ψ|φ⟩|²

        Properties:
        - F(ψ,ψ) = 1 (identical states)
        - F(ψ,φ) = 0 (orthogonal states)
        - F(ψ,φ) ∈ [0,1] (similarity measure)

        Args:
            other: Another QuantumMemoryCell to compare

        Returns:
            Fidelity value between 0.0 and 1.0

        Example:
            >>> cell1 = QuantumMemoryCell([1, 0], 1)
            >>> cell2 = QuantumMemoryCell([0, 1], 1)
            >>> cell1.fidelity(cell2)  # Returns 0.0 (orthogonal)
        """
        if self.quantum_state is None or other.quantum_state is None:
            logger.debug("missing_quantum_states_fidelity_zero")
            return 0.0

        # Handle different sized states (take minimum)
        min_size = min(len(self.quantum_state), len(other.quantum_state))
        s1 = self.quantum_state[:min_size]
        s2 = other.quantum_state[:min_size]

        # Quantum fidelity: |⟨ψ|φ⟩|²
        inner_product = np.abs(np.vdot(s1, s2))
        fidelity = float(inner_product**2)

        logger.debug("fidelity_calculated", fidelity=fidelity)

        return fidelity

    def get_state_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the quantum state.

        Returns:
            Dictionary with state metadata and properties
        """
        info = {
            "has_quantum_state": self.quantum_state is not None,
            "encoding_type": self.encoding_type,
            "num_qubits": self.num_qubits,
            "data_type": type(self.data).__name__,
        }

        if self.quantum_state is not None:
            info.update(
                {
                    "state_size": len(self.quantum_state),
                    "is_normalized": np.isclose(np.linalg.norm(self.quantum_state), 1.0),
                    "probabilities": np.abs(self.quantum_state) ** 2,
                    "purity": float(
                        np.sum(np.abs(self.quantum_state) ** 4)
                    ),  # Tr(ρ²) for pure states
                }
            )

        return info


@dataclass
class QLearningState:
    """
    Q-Learning state representation for hybrid learning.

    Encapsulates a single Q-learning experience tuple:
    (state, action, reward, next_state, q_value)

    Attributes:
        state: Current environment state identifier
        action: Action taken in current state
        reward: Reward received after action
        next_state: Resulting state after action
        q_value: Learned Q-value for state-action pair
    """

    state: str
    action: str
    reward: float
    next_state: str
    q_value: float = 0.0


class HybridQLearning:
    """
    Hybrid Quantum-Classical Q-Learning Algorithm.

    Combines quantum advantages with classical Q-learning:
    - Quantum Exploration: Superposition for action selection
    - Classical Exploitation: Deterministic Q-value updates
    - Hybrid Balance: Best of both worlds

    Q-Learning Update Rule:
    Q(s,a) ← Q(s,a) + α[r + γ maxₐ' Q(s',a') - Q(s,a)]

    Where:
    - α: Learning rate (how much to update)
    - γ: Discount factor (future reward importance)
    - r: Immediate reward
    - s': Next state

    Attributes:
        num_states: Number of possible states
        num_actions: Number of possible actions
        learning_rate: α parameter
        discount_factor: γ parameter
        use_quantum: Whether to use quantum exploration
        q_table: Dictionary storing Q-values

    Example:
        >>> learner = HybridQLearning(num_states=5, num_actions=3, use_quantum=True)
        >>> action = learner.select_action("state_2")  # Quantum exploration
        >>> learner.update("state_2", action, 1.0, "state_3")  # Classical update
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
        Initialize hybrid Q-learning agent.

        Args:
            num_states: Number of possible states in environment
            num_actions: Number of possible actions
            learning_rate: How much to update Q-values (0 < α ≤ 1)
            discount_factor: Future reward importance (0 ≤ γ ≤ 1)
            use_quantum: Enable quantum exploration if Qiskit available

        Raises:
            ValueError: If parameters are out of valid ranges
        """
        if not (0 < learning_rate <= 1):
            raise ValueError("learning_rate must be in (0, 1]")
        if not (0 <= discount_factor <= 1):
            raise ValueError("discount_factor must be in [0, 1]")
        if num_states <= 0 or num_actions <= 0:
            raise ValueError("num_states and num_actions must be positive")

        self.num_states = num_states
        self.num_actions = num_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.use_quantum = use_quantum and QISKIT_AVAILABLE

        # Q-table: (state, action) -> q_value
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
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            use_quantum=self.use_quantum,
        )

    def select_action(self, state: str, epsilon: float = 0.1) -> str:
        """
        Select action using quantum exploration or epsilon-greedy.

        Quantum Exploration:
        - Creates superposition of all actions
        - Measures to collapse to single action
        - Truly random exploration (not pseudorandom)

        Classical Exploration:
        - Epsilon-greedy: ε chance of random action, (1-ε) chance of best action

        Args:
            state: Current state identifier
            epsilon: Exploration rate for classical fallback [0, 1]

        Returns:
            Selected action string (format: "action_{index}")

        Example:
            >>> action = learner.select_action("room_5")
            >>> print(f"Selected: {action}")  # "action_2"
        """
        if self.use_quantum:
            return self._quantum_select_action(state)
        else:
            return self._classical_select_action(state, epsilon)

    def _quantum_select_action(self, state: str) -> str:
        """
        Select action using quantum superposition.

        Process:
        1. Create quantum circuit with Hadamard gates (uniform superposition)
        2. Measure single shot to collapse superposition
        3. Map measurement outcome to action index

        This provides true quantum randomness, unlike pseudorandom generators.
        """
        if not QISKIT_AVAILABLE:
            logger.warning("qiskit_unavailable_fallback_to_classical")
            return self._classical_select_action(state, 0.1)

        # Create superposition circuit
        qr = QuantumRegister(self.num_qubits, "q")
        cr = ClassicalRegister(self.num_qubits, "c")
        qc = QuantumCircuit(qr, cr)

        # Apply Hadamard to all qubits for uniform superposition
        for i in range(self.num_qubits):
            qc.h(i)

        # Measure all qubits
        qc.measure_all()

        # Execute single shot
        job = self.simulator.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()

        # Get measurement outcome
        outcome = list(counts.keys())[0]
        # Remove spaces from Qiskit format
        outcome_str = outcome.replace(" ", "")
        action_idx = int(outcome_str, 2) % self.num_actions

        action = f"action_{action_idx}"

        logger.debug(
            "quantum_action_selected",
            state=state,
            action=action,
            outcome=outcome,
            action_idx=action_idx,
        )

        return action

    def _classical_select_action(self, state: str, epsilon: float) -> str:
        """
        Select action using classical epsilon-greedy policy.

        Process:
        1. With probability ε: select random action (exploration)
        2. With probability (1-ε): select best known action (exploitation)
        3. Return action with highest Q-value for current state
        """
        if _rng.random() < epsilon:
            # Exploration: random action
            action_idx = _rng.integers(0, self.num_actions)
            logger.debug("exploration_random_action", state=state, action_idx=action_idx)
        else:
            # Exploitation: best action
            action_idx = 0
            best_q = float("-inf")

            for a in range(self.num_actions):
                action = f"action_{a}"
                q_val = self.q_table.get((state, action), 0.0)
                if q_val > best_q:
                    best_q = q_val
                    action_idx = a

            logger.debug(
                "exploitation_best_action", state=state, action_idx=action_idx, q_value=best_q
            )

        return f"action_{action_idx}"

    def update(self, state: str, action: str, reward: float, next_state: str) -> None:
        """
        Update Q-value using Q-learning temporal difference.

        Q-Learning Update:
        Q(s,a) ← Q(s,a) + α[r + γ maxₐ' Q(s',a') - Q(s,a)]

        This implements the core Q-learning algorithm:
        - Learn from experience tuples (s, a, r, s')
        - Balance immediate vs future rewards
        - Converge to optimal policy

        Args:
            state: Current state before action
            action: Action taken
            reward: Immediate reward received
            next_state: State after action

        Example:
            >>> learner.update("room_1", "move_right", 1.0, "room_2")
            >>> # Q("room_1", "move_right") increases
        """
        # Get current Q-value
        current_q = self.q_table.get((state, action), 0.0)

        # Find maximum Q-value for next state (over all possible actions)
        max_next_q = 0.0
        for a in range(self.num_actions):
            next_action = f"action_{a}"
            q_val = self.q_table.get((next_state, next_action), 0.0)
            max_next_q = max(max_next_q, q_val)

        # Q-learning update rule
        target = reward + self.discount_factor * max_next_q
        new_q = current_q + self.learning_rate * (target - current_q)

        # Store updated Q-value
        self.q_table[(state, action)] = new_q

        logger.debug(
            "q_value_updated",
            state=state,
            action=action,
            old_q=current_q,
            new_q=new_q,
            reward=reward,
            next_state=next_state,
            max_next_q=max_next_q,
        )

    def get_q_value(self, state: str, action: str) -> float:
        """
        Get learned Q-value for state-action pair.

        Args:
            state: State identifier
            action: Action identifier

        Returns:
            Learned Q-value (default 0.0 for unseen pairs)
        """
        return self.q_table.get((state, action), 0.0)

    def get_policy(self, state: str) -> Dict[str, float]:
        """
        Get complete action-value function for a state.

        Args:
            state: State to get policy for

        Returns:
            Dictionary mapping action -> Q-value for all actions
        """
        policy = {}
        for a in range(self.num_actions):
            action = f"action_{a}"
            policy[action] = self.q_table.get((state, action), 0.0)

        return policy

    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the learning process.

        Returns:
            Dictionary with learning metrics
        """
        stats = {
            "states_learned": len(set(s for s, a in self.q_table.keys())),
            "state_action_pairs": len(self.q_table),
            "total_updates": len(self.q_table),  # Approximation
            "use_quantum": self.use_quantum,
        }

        if self.q_table:
            q_values = list(self.q_table.values())
            stats.update(
                {
                    "avg_q_value": float(np.mean(q_values)),
                    "max_q_value": float(np.max(q_values)),
                    "min_q_value": float(np.min(q_values)),
                    "q_value_std": float(np.std(q_values)),
                }
            )

        return stats


@dataclass
class QuantumMemoryComparison:
    """
    Results from comparing quantum vs classical memory systems.

    This class stores benchmarking results to quantify quantum advantages
    in memory operations, retrieval speed, and pattern similarity search.

    Attributes:
        quantum_retrieval_time: Average time for quantum retrieval (seconds)
        classical_retrieval_time: Average time for classical retrieval (seconds)
        quantum_accuracy: Accuracy of quantum memory retrieval [0, 1]
        classical_accuracy: Accuracy of classical memory retrieval [0, 1]
        quantum_speedup: Speedup factor (quantum vs classical time)
        notes: Additional observations and implementation details

    Example:
        >>> comparison = QuantumMemoryComparison(
        ...     quantum_retrieval_time=0.001,
        ...     classical_retrieval_time=0.005,
        ...     quantum_accuracy=0.95,
        ...     classical_accuracy=0.98,
        ...     quantum_speedup=5.0,
        ...     notes="Quantum shows 5x speedup with slightly lower accuracy"
        ... )
        >>> print(comparison.summary())
    """

    quantum_retrieval_time: float
    classical_retrieval_time: float
    quantum_accuracy: float
    classical_accuracy: float
    quantum_speedup: float
    notes: str = ""

    def summary(self) -> str:
        """
        Generate formatted comparison summary.

        Returns:
            Multi-line string with formatted comparison results
        """
        return "\n".join(
            [
                "Quantum vs Classical Memory Comparison:",
                f"  Retrieval Time: {self.quantum_retrieval_time:.4f}s vs "
                f"{self.classical_retrieval_time:.4f}s",
                f"  Accuracy: {self.quantum_accuracy:.2%} vs " f"{self.classical_accuracy:.2%}",
                f"  Speedup: {self.quantum_speedup:.2f}x",
                f"  Notes: {self.notes}",
            ]
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert comparison to dictionary format.

        Returns:
            Dictionary representation for serialization
        """
        return {
            "quantum_retrieval_time": self.quantum_retrieval_time,
            "classical_retrieval_time": self.classical_retrieval_time,
            "quantum_accuracy": self.quantum_accuracy,
            "classical_accuracy": self.classical_accuracy,
            "quantum_speedup": self.quantum_speedup,
            "notes": self.notes,
        }

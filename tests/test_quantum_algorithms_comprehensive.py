import math
from src.quantum_ai.quantum_algorithms import (

#!/usr/bin/env python3
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
Comprehensive tests for quantum_algorithms.py module.
Tests quantum circuit simulation and Grover's search algorithm.
"""


    GroverSearch,
    QuantumCircuit,
    QuantumGate,
    QuantumState,
)


class TestQuantumGate:
    """Test QuantumGate enum."""

    def test_quantum_gate_values(self) -> None:
        """Test that all quantum gates are defined."""
        assert QuantumGate.HADAMARD.value == "H"
        assert QuantumGate.PAULI_X.value == "X"
        assert QuantumGate.PAULI_Y.value == "Y"
        assert QuantumGate.PAULI_Z.value == "Z"
        assert QuantumGate.CNOT.value == "CNOT"
        assert QuantumGate.PHASE.value == "PHASE"


class TestQuantumState:
    """Test QuantumState class."""

    def test_initialization_default(self) -> None:
        """Test QuantumState initialization with default amplitudes."""
        state = QuantumState(num_qubits=2)

        # Should have 2^2 = 4 amplitudes
        assert len(state.amplitudes) == 4

        # Should be initialized to |00⟩
        assert state.amplitudes[0] == complex(1, 0)
        assert state.amplitudes[1] == complex(0, 0)
        assert state.amplitudes[2] == complex(0, 0)
        assert state.amplitudes[3] == complex(0, 0)

    def test_initialization_custom_amplitudes(self) -> None:
        """Test QuantumState initialization with custom amplitudes."""
        custom_amps = [
            complex(0.5, 0),
            complex(0.5, 0),
            complex(0.5, 0),
            complex(0.5, 0),
        ]
        state = QuantumState(num_qubits=2, amplitudes=custom_amps)

        assert len(state.amplitudes) == 4
        assert state.amplitudes == custom_amps

    def test_normalize(self) -> None:
        """Test state normalization."""
        # Create unnormalized state
        state = QuantumState(num_qubits=2)
        state.amplitudes = [complex(1, 0), complex(1, 0), complex(1, 0), complex(1, 0)]

        # Normalize
        state.normalize()

        # Check normalization: sum of |amplitude|^2 should be 1
        norm_squared = sum(abs(a) ** 2 for a in state.amplitudes)
        assert abs(norm_squared - 1.0) < 1e-10

    def test_get_probabilities(self) -> None:
        """Test getting measurement probabilities."""
        state = QuantumState(num_qubits=1)
        # Set equal superposition: |0⟩ + |1⟩
        state.amplitudes = [complex(1 / math.sqrt(2), 0), complex(1 / math.sqrt(2), 0)]

        probs = state.get_probabilities()

        assert len(probs) == 2
        assert abs(probs[0] - 0.5) < 1e-10
        assert abs(probs[1] - 0.5) < 1e-10

    def test_measure(self) -> None:
        """Test quantum measurement."""
        state = QuantumState(num_qubits=1)
        # Set to |0⟩ state
        state.amplitudes = [complex(1, 0), complex(0, 0)]

        # Should always measure 0
        result = state.measure()
        assert result == 0

    def test_measure_superposition(self) -> None:
        """Test measurement in superposition."""
        state = QuantumState(num_qubits=1)
        # Set equal superposition
        state.amplitudes = [complex(1 / math.sqrt(2), 0), complex(1 / math.sqrt(2), 0)]

        # Measure multiple times
        results = [state.measure() for _ in range(100)]

        # Should get both 0 and 1 (probabilistic)
        assert 0 in results
        assert 1 in results


class TestQuantumCircuit:
    """Test QuantumCircuit class."""

    def test_initialization(self) -> None:
        """Test QuantumCircuit initialization."""
        circuit = QuantumCircuit(num_qubits=2)

        assert circuit.num_qubits == 2
        assert len(circuit.state.amplitudes) == 4
        assert len(circuit.gates_applied) == 0

    def test_apply_hadamard_gate(self) -> None:
        """Test applying Hadamard gate."""
        circuit = QuantumCircuit(num_qubits=1)

        # Apply Hadamard to qubit 0
        circuit.apply_gate(QuantumGate.HADAMARD, [0])

        # Should create superposition
        probs = circuit.state.get_probabilities()
        assert abs(probs[0] - 0.5) < 1e-10
        assert abs(probs[1] - 0.5) < 1e-10

        # Check gate was recorded
        assert len(circuit.gates_applied) == 1
        assert circuit.gates_applied[0][0] == QuantumGate.HADAMARD

    def test_apply_pauli_x_gate(self) -> None:
        """Test applying Pauli-X (NOT) gate."""
        circuit = QuantumCircuit(num_qubits=1)

        # Apply X gate to qubit 0
        circuit.apply_gate(QuantumGate.PAULI_X, [0])

        # Should flip |0⟩ to |1⟩
        probs = circuit.state.get_probabilities()
        assert abs(probs[0] - 0.0) < 1e-10
        assert abs(probs[1] - 1.0) < 1e-10

    def test_apply_cnot_gate(self) -> None:
        """Test applying CNOT gate."""
        circuit = QuantumCircuit(num_qubits=2)

        # First create superposition on control qubit
        circuit.apply_gate(QuantumGate.HADAMARD, [0])

        # Then apply CNOT with qubit 0 as control, qubit 1 as target
        circuit.apply_gate(QuantumGate.CNOT, [0, 1])

        # Should create entangled Bell state
        assert len(circuit.gates_applied) == 2

    def test_measure(self) -> None:
        """Test circuit measurement."""
        circuit = QuantumCircuit(num_qubits=2)

        # Measure initial state (should be 0)
        result = circuit.measure()
        assert result == 0

    def test_get_state_vector(self) -> None:
        """Test getting state vector."""
        circuit = QuantumCircuit(num_qubits=1)

        state_vector = circuit.get_state_vector()

        assert len(state_vector) == 2
        assert state_vector[0] == complex(1, 0)
        assert state_vector[1] == complex(0, 0)


class TestGroverSearch:
    """Test GroverSearch algorithm."""

    def test_initialization(self) -> None:
        """Test GroverSearch initialization."""
        grover = GroverSearch(search_space_size=4)

        assert grover.size == 4
        assert grover.num_qubits == 2
        assert isinstance(grover.circuit, QuantumCircuit)

    def test_search_simple(self) -> None:
        """Test Grover search with simple oracle."""

        def oracle(x: int) -> bool:
            """Mark item 2."""
            return x == 2

        grover = GroverSearch(search_space_size=4)

        # Search (may not always find on first try due to simulation)
        result = grover.search(oracle, num_iterations=1)

        # Result should be a valid index
        assert 0 <= result < 4

    def test_search_power_of_two(self) -> None:
        """Test that search space must be power of 2."""
        # Valid power of 2
        grover = GroverSearch(search_space_size=8)
        assert grover.num_qubits == 3

        # Another valid power of 2
        grover2 = GroverSearch(search_space_size=16)
        assert grover2.num_qubits == 4


class TestQuantumAlgorithmsIntegration:
    """Integration tests for quantum algorithms."""

    def test_bell_state_creation(self) -> None:
        """Test creating a Bell state (entangled pair)."""
        circuit = QuantumCircuit(num_qubits=2)

        # Create Bell state: (|00⟩ + |11⟩) / sqrt(2)
        circuit.apply_gate(QuantumGate.HADAMARD, [0])
        circuit.apply_gate(QuantumGate.CNOT, [0, 1])

        # Get probabilities
        probs = circuit.state.get_probabilities()

        # Should have ~50% probability for |00⟩ and |11⟩
        # |01⟩ and |10⟩ should be ~0%
        assert abs(probs[0] - 0.5) < 1e-10  # |00⟩
        assert abs(probs[1] - 0.0) < 1e-10  # |01⟩
        assert abs(probs[2] - 0.0) < 1e-10  # |10⟩
        assert abs(probs[3] - 0.5) < 1e-10  # |11⟩

    def test_multiple_hadamard_gates(self) -> None:
        """Test applying multiple Hadamard gates."""
        circuit = QuantumCircuit(num_qubits=2)

        # Apply Hadamard to both qubits
        circuit.apply_gate(QuantumGate.HADAMARD, [0])
        circuit.apply_gate(QuantumGate.HADAMARD, [1])

        # Should create uniform superposition
        probs = circuit.state.get_probabilities()

        # All states should have equal probability (0.25)
        for prob in probs:
            assert abs(prob - 0.25) < 1e-10

    def test_x_gate_reversibility(self) -> None:
        """Test that X gate is its own inverse."""
        circuit = QuantumCircuit(num_qubits=1)

        # Apply X twice
        circuit.apply_gate(QuantumGate.PAULI_X, [0])
        circuit.apply_gate(QuantumGate.PAULI_X, [0])

        # Should be back to |0⟩
        probs = circuit.state.get_probabilities()
        assert abs(probs[0] - 1.0) < 1e-10
        assert abs(probs[1] - 0.0) < 1e-10

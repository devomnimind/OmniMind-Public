import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Tuple
import structlog

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
Quantum Algorithms - Simulation-based Implementation.

Implements quantum-inspired algorithms that can run on classical hardware:
- Quantum circuit simulation
- Grover's search algorithm
- Quantum annealing simulation

Author: OmniMind Project
License: MIT
"""


logger = structlog.get_logger(__name__)


class QuantumGate(Enum):
    """Types of quantum gates."""

    HADAMARD = "H"  # Superposition
    PAULI_X = "X"  # NOT gate
    PAULI_Y = "Y"  # Y rotation
    PAULI_Z = "Z"  # Phase flip
    CNOT = "CNOT"  # Controlled-NOT
    PHASE = "PHASE"  # Phase gate


@dataclass
class QuantumState:
    """Represents a quantum state (simulated)."""

    num_qubits: int
    amplitudes: List[complex] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize state to |0⟩."""
        if not self.amplitudes:
            # Initialize to |00...0⟩
            size = 2**self.num_qubits
            self.amplitudes = [complex(0, 0)] * size
            self.amplitudes[0] = complex(1, 0)  # |0⟩ state

    def normalize(self) -> None:
        """Normalize the state vector."""
        norm = math.sqrt(sum(abs(a) ** 2 for a in self.amplitudes))
        if norm > 0:
            self.amplitudes = [a / norm for a in self.amplitudes]

    def measure(self) -> int:
        """Measure the quantum state (collapse to classical)."""
        probabilities = [abs(a) ** 2 for a in self.amplitudes]

        # Sample according to probabilities
        r = random.random()
        cumsum = 0.0
        for i, prob in enumerate(probabilities):
            cumsum += prob
            if r <= cumsum:
                return i

        return len(probabilities) - 1

    def get_probabilities(self) -> List[float]:
        """Get measurement probabilities."""
        return [abs(a) ** 2 for a in self.amplitudes]


class QuantumCircuit:
    """
    Quantum circuit simulator.

    Features:
    - Gate application
    - State evolution
    - Measurement simulation
    """

    def __init__(self, num_qubits: int):
        """
        Initialize quantum circuit.

        Args:
            num_qubits: Number of qubits
        """
        self.num_qubits = num_qubits
        self.state = QuantumState(num_qubits)
        self.gates_applied: List[Tuple[QuantumGate, List[int]]] = []
        self.logger = logger.bind(component="quantum_circuit")

    def apply_gate(self, gate: QuantumGate, qubits: List[int]) -> None:
        """
        Apply a quantum gate.

        Args:
            gate: Gate to apply
            qubits: Qubit indices
        """
        if gate == QuantumGate.HADAMARD:
            self._apply_hadamard(qubits[0])
        elif gate == QuantumGate.PAULI_X:
            self._apply_pauli_x(qubits[0])
        elif gate == QuantumGate.CNOT:
            self._apply_cnot(qubits[0], qubits[1])

        self.gates_applied.append((gate, qubits))
        self.logger.debug("gate_applied", gate=gate.value, qubits=qubits)

    def _apply_hadamard(self, qubit: int) -> None:
        """Apply Hadamard gate to create superposition."""
        new_amplitudes = self.state.amplitudes.copy()
        size = 2**self.num_qubits

        for i in range(size):
            if (i >> qubit) & 1 == 0:
                # Qubit is 0
                j = i | (1 << qubit)  # Flip to 1
                a0 = self.state.amplitudes[i]
                a1 = self.state.amplitudes[j]
                new_amplitudes[i] = (a0 + a1) / math.sqrt(2)
                new_amplitudes[j] = (a0 - a1) / math.sqrt(2)

        self.state.amplitudes = new_amplitudes

    def _apply_pauli_x(self, qubit: int) -> None:
        """Apply Pauli-X (NOT) gate."""
        new_amplitudes = self.state.amplitudes.copy()
        size = 2**self.num_qubits

        for i in range(size):
            j = i ^ (1 << qubit)  # Flip qubit
            if i < j:  # Swap once
                new_amplitudes[i], new_amplitudes[j] = (
                    self.state.amplitudes[j],
                    self.state.amplitudes[i],
                )

        self.state.amplitudes = new_amplitudes

    def _apply_cnot(self, control: int, target: int) -> None:
        """Apply CNOT gate."""
        new_amplitudes = self.state.amplitudes.copy()
        size = 2**self.num_qubits

        for i in range(size):
            if (i >> control) & 1:  # Control is 1
                j = i ^ (1 << target)  # Flip target
                if i < j:
                    new_amplitudes[i], new_amplitudes[j] = (
                        self.state.amplitudes[j],
                        self.state.amplitudes[i],
                    )

        self.state.amplitudes = new_amplitudes

    def measure(self) -> int:
        """Measure the circuit and get result."""
        result = self.state.measure()
        self.logger.info("measurement", result=result)
        return result

    def get_state_vector(self) -> List[complex]:
        """Get current state vector."""
        return self.state.amplitudes.copy()


class GroverSearch:
    """
    Grover's quantum search algorithm (simulated).

    Features:
    - Quadratic speedup for unstructured search
    - Oracle-based marking
    - Amplitude amplification
    """

    def __init__(self, search_space_size: int):
        """
        Initialize Grover search.

        Args:
            search_space_size: Size of search space (must be power of 2)
        """
        self.size = search_space_size
        self.num_qubits = int(math.log2(search_space_size))
        self.circuit = QuantumCircuit(self.num_qubits)
        self.logger = logger.bind(algorithm="grover")

    def search(self, oracle: Callable[[int], bool], num_iterations: Optional[int] = None) -> int:
        """
        Search for marked item.

        Args:
            oracle: Function that returns True for target
            num_iterations: Number of Grover iterations (auto-computed if None)

        Returns:
            Found index
        """
        if num_iterations is None:
            # Optimal number of iterations
            num_iterations = int(math.pi / 4 * math.sqrt(self.size))

        # Initialize to uniform superposition
        for i in range(self.num_qubits):
            self.circuit.apply_gate(QuantumGate.HADAMARD, [i])

        # Grover iterations
        for iteration in range(num_iterations):
            # Oracle (mark target states)
            self._apply_oracle(oracle)

            # Diffusion operator (amplify marked states)
            self._apply_diffusion()

        # Measure
        result = self.circuit.measure()

        self.logger.info(
            "search_complete",
            result=result,
            iterations=num_iterations,
        )

        return result

    def _apply_oracle(self, oracle: Callable[[int], bool]) -> None:
        """Apply oracle to mark target states."""
        # Simplified oracle - flip phase of marked states
        for i, amplitude in enumerate(self.circuit.state.amplitudes):
            if oracle(i):
                self.circuit.state.amplitudes[i] = -amplitude

    def _apply_diffusion(self) -> None:
        """Apply Grover diffusion operator."""
        # Inversion about the mean
        mean = sum(self.circuit.state.amplitudes) / len(self.circuit.state.amplitudes)
        for i in range(len(self.circuit.state.amplitudes)):
            self.circuit.state.amplitudes[i] = 2 * mean - self.circuit.state.amplitudes[i]


class QuantumAnnealer:
    """
    Quantum annealing simulator for optimization.

    Features:
    - Simulated quantum tunneling
    - Energy minimization
    - Combinatorial optimization
    """

    def __init__(
        self,
        num_variables: int,
        initial_temperature: float = 10.0,
        final_temperature: float = 0.1,
    ):
        """
        Initialize quantum annealer.

        Args:
            num_variables: Number of binary variables
            initial_temperature: Starting temperature
            final_temperature: Final temperature
        """
        self.num_variables = num_variables
        self.initial_temp = initial_temperature
        self.final_temp = final_temperature
        self.current_state = [random.choice([0, 1]) for _ in range(num_variables)]
        self.best_state = self.current_state.copy()
        self.best_energy = float("inf")
        self.logger = logger.bind(algorithm="quantum_annealing")

    def anneal(
        self,
        energy_function: Callable[[List[int]], float],
        num_steps: int = 1000,
    ) -> Tuple[List[int], float]:
        """
        Perform quantum annealing.

        Args:
            energy_function: Function to minimize
            num_steps: Number of annealing steps

        Returns:
            (best_state, best_energy)
        """
        self.logger.info("annealing_started", steps=num_steps)

        for step in range(num_steps):
            # Temperature schedule (linear)
            progress = step / num_steps
            temperature = self.initial_temp * (1 - progress) + self.final_temp * progress

            # Quantum tunneling probability (decreases with progress)
            tunnel_prob = 0.5 * (1 - progress)

            # Try to flip a random variable
            var_index = random.randint(0, self.num_variables - 1)
            new_state = self.current_state.copy()
            new_state[var_index] = 1 - new_state[var_index]

            # Compute energies
            current_energy = energy_function(self.current_state)
            new_energy = energy_function(new_state)

            # Accept new state based on energy and quantum tunneling
            energy_diff = new_energy - current_energy

            if energy_diff < 0:
                # Lower energy - always accept
                accept = True
            elif random.random() < tunnel_prob:
                # Quantum tunneling
                accept = True
            else:
                # Metropolis criterion
                accept = random.random() < math.exp(-energy_diff / temperature)

            if accept:
                self.current_state = new_state
                current_energy = new_energy

            # Update best
            if current_energy < self.best_energy:
                self.best_energy = current_energy
                self.best_state = self.current_state.copy()

        self.logger.info(
            "annealing_complete",
            best_energy=self.best_energy,
        )

        return self.best_state, self.best_energy

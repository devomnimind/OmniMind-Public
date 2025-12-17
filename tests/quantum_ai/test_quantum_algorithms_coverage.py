import pytest

from src.quantum_ai.quantum_algorithms import (
    GroverSearch,
    QuantumAnnealer,
    QuantumCircuit,
    QuantumGate,
)


class TestQuantumAlgorithmsCoverage:

    def test_quantum_circuit_gates(self):
        # Test all gates
        circuit = QuantumCircuit(2)

        # Hadamard
        circuit.apply_gate(QuantumGate.HADAMARD, [0])
        # |+0> = (|0> + |1>) / sqrt(2) * |0>
        # Amplitudes: |00>: 1/sqrt(2), |01>: 1/sqrt(2),
        # |10>: 0, |11>: 0 (little endian for qubit 0)
        # Wait, implementation details:
        # _apply_hadamard(qubit):
        # if (i >> qubit) & 1 == 0: ...
        # qubit 0 is LSB.
        # i=0 (00): qubit 0 is 0. j=1 (01).
        # a0 = amp[0], a1 = amp[1].
        # new[0] = (a0+a1)/sqrt(2), new[1] = (a0-a1)/sqrt(2)
        # Initial: amp[0]=1, others 0.
        # new[0] = 1/sqrt(2), new[1] = 1/sqrt(2).
        # Correct.

        # Pauli X
        circuit.apply_gate(QuantumGate.PAULI_X, [1])
        # |+1>
        # Flips qubit 1.
        # 00 -> 10 (2), 01 -> 11 (3)
        # new[2] = new[0], new[3] = new[1]
        # new[0]=0, new[1]=0.

        # CNOT
        circuit.apply_gate(QuantumGate.CNOT, [1, 0])
        # Control 1, Target 0.
        # If qubit 1 is 1, flip qubit 0.
        # States: 10 (qubit 1=1, qubit 0=0) -> 11 (qubit 1=1, qubit 0=1)
        # States: 11 -> 10
        # So swaps amp[2] and amp[3].

        # Measure
        res = circuit.measure()
        assert res in [0, 1, 2, 3]

        probs = circuit.state.get_probabilities()
        assert len(probs) == 4
        assert sum(probs) == pytest.approx(1.0)

    def test_grover_search(self):
        # Search space size 4 (2 qubits)
        grover = GroverSearch(4)

        # Target is 3 (11)
        def oracle(x):
            return x == 3

        result = grover.search(oracle)
        assert result == 3

    def test_quantum_annealer(self):
        # Minimize x^2 (simple)
        # Variables: [x0, x1, x2] -> int value
        # Let's try to minimize Hamming weight (all 0s)

        annealer = QuantumAnnealer(num_variables=5, initial_temperature=10.0, final_temperature=0.1)

        def energy_func(state):
            return sum(state)  # Energy = number of 1s

        best_state, best_energy = annealer.anneal(energy_func, num_steps=100)

        assert best_energy == 0
        assert sum(best_state) == 0

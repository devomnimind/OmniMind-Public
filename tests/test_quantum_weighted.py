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
Tests for Quantum Weighted Decision Making.
"""

import numpy as np
import pytest

from src.quantum_consciousness.quantum_cognition import (
    QISKIT_AVAILABLE,
    QuantumDecisionMaker,
)


@pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
def test_quantum_decision_uniform():
    maker = QuantumDecisionMaker(num_qubits=1)
    options = ["A", "B"]
    decision = maker.make_decision(options)

    # Should be roughly 50/50
    prob_a = decision.probabilities["A"]
    prob_b = decision.probabilities["B"]

    assert np.isclose(prob_a, 0.5, atol=0.1)
    assert np.isclose(prob_b, 0.5, atol=0.1)


@pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
def test_quantum_decision_biased():
    maker = QuantumDecisionMaker(num_qubits=1)
    options = ["A", "B"]

    # Weight 0.9 -> Bias towards |1> (Option B)
    # Weight 0.1 -> Bias towards |0> (Option A)
    # Note: Logic in make_decision maps basis states to options.
    # 1 qubit: |0> -> A, |1> -> B

    # Case 1: Bias towards B
    decision_b = maker.make_decision(options, weights=[0.9])
    assert decision_b.probabilities["B"] > 0.8

    # Case 2: Bias towards A
    decision_a = maker.make_decision(options, weights=[0.1])
    assert decision_a.probabilities["A"] > 0.8


def test_fallback_without_qiskit():
    if not QISKIT_AVAILABLE:
        maker = QuantumDecisionMaker(num_qubits=1)
        options = ["A", "B"]
        decision = maker.make_decision(options)
        assert decision.confidence == 0.5

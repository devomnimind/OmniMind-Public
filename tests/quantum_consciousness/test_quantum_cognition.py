from __future__ import annotations

import numpy as np
import pytest
from src.quantum_consciousness.quantum_cognition import (


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
Testes para Quantum Cognition (quantum_cognition.py).

Cobertura de:
- QuantumState initialization and operations
- QuantumCognitionEngine circuit creation
- Superposition and entanglement
- QuantumDecisionMaker decision-making
- Measurement and collapse
"""



    QISKIT_AVAILABLE,
    QuantumCognitionEngine,
    QuantumDecisionMaker,
    QuantumState,
    SuperpositionDecision,
)


class TestQuantumState:
    """Testes para QuantumState."""

    def test_quantum_state_initialization(self) -> None:
        """Testa inicialização do estado quântico."""
        state = QuantumState(num_qubits=2)

        assert state.num_qubits == 2
        assert state.statevector is not None
        assert len(state.statevector) == 4  # 2^2
        # Initial state should be |00⟩
        assert np.abs(state.statevector[0] - 1.0) < 1e-10
        assert np.sum(np.abs(state.statevector[1:])) < 1e-10

    def test_quantum_state_with_custom_statevector(self) -> None:
        """Testa estado quântico com statevector customizado."""
        custom_sv = np.array([0.6, 0.8, 0.0, 0.0], dtype=complex)
        state = QuantumState(num_qubits=2, statevector=custom_sv)

        assert state.num_qubits == 2
        assert np.allclose(state.statevector, custom_sv)

    def test_quantum_state_measure(self) -> None:
        """Testa medição de estado quântico."""
        state = QuantumState(num_qubits=2)
        outcome = state.measure()

        assert isinstance(outcome, str)
        assert len(outcome) == 2
        assert all(c in "01" for c in outcome)
        # Should always measure |00⟩ for initial state
        assert outcome == "00"

    def test_quantum_state_measure_superposition(self) -> None:
        """Testa medição de estado em superposição."""
        # Equal superposition: (|00⟩ + |11⟩) / sqrt(2)
        sv = np.array([1 / np.sqrt(2), 0, 0, 1 / np.sqrt(2)], dtype=complex)
        state = QuantumState(num_qubits=2, statevector=sv)

        # Measure multiple times to check probabilistic behavior
        outcomes = [state.measure() for _ in range(100)]

        # Should get mix of "00" and "11"
        assert "00" in outcomes or "11" in outcomes
        # Should not get "01" or "10" (zero amplitude)
        unique_outcomes = set(outcomes)
        assert unique_outcomes.issubset({"00", "11"})


class TestQuantumCognitionEngine:
    """Testes para QuantumCognitionEngine."""

    def test_engine_initialization(self) -> None:
        """Testa inicialização do motor de cognição quântica."""
        engine = QuantumCognitionEngine(num_qubits=3)

        assert engine.num_qubits == 3
        if QISKIT_AVAILABLE:
            assert engine.simulator is not None

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_create_superposition(self) -> None:
        """Testa criação de superposição."""
        engine = QuantumCognitionEngine(num_qubits=2)
        circuit = engine.create_superposition()

        assert circuit is not None
        assert circuit.num_qubits == 2

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_create_superposition_specific_qubits(self) -> None:
        """Testa criação de superposição em qubits específicos."""
        engine = QuantumCognitionEngine(num_qubits=3)
        circuit = engine.create_superposition(qubits=[0, 2])

        assert circuit is not None
        assert circuit.num_qubits == 3

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_create_entanglement(self) -> None:
        """Testa criação de entrelaçamento."""
        engine = QuantumCognitionEngine(num_qubits=2)
        circuit = engine.create_entanglement(control_qubit=0, target_qubit=1)

        assert circuit is not None
        assert circuit.num_qubits == 2

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_get_statevector(self) -> None:
        """Testa obtenção de statevector."""
        engine = QuantumCognitionEngine(num_qubits=2)
        circuit = engine.create_superposition()

        state = engine.get_statevector(circuit)

        assert isinstance(state, QuantumState)
        assert state.num_qubits == 2
        assert state.statevector is not None
        assert len(state.probabilities) > 0

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_measure_circuit(self) -> None:
        """Testa medição de circuito."""
        engine = QuantumCognitionEngine(num_qubits=2)
        circuit = engine.create_superposition()

        counts = engine.measure_circuit(circuit, shots=100)

        assert isinstance(counts, dict)
        assert len(counts) > 0
        # Check that total counts equals shots
        total_counts = sum(counts.values())
        assert total_counts == 100

    def test_engine_without_qiskit(self) -> None:
        """Testa comportamento do engine quando Qiskit não está disponível."""
        engine = QuantumCognitionEngine(num_qubits=2)

        # Should initialize without errors
        assert engine.num_qubits == 2


class TestSuperpositionDecision:
    """Testes para SuperpositionDecision."""

    def test_superposition_decision_creation(self) -> None:
        """Testa criação de decisão em superposição."""
        options = ["option_a", "option_b", "option_c"]
        state = QuantumState(num_qubits=2)
        probs = {opt: 1.0 / len(options) for opt in options}

        decision = SuperpositionDecision(options=options, quantum_state=state, probabilities=probs)

        assert decision.options == options
        assert decision.quantum_state == state
        assert decision.probabilities == probs
        assert decision.final_decision is None

    def test_superposition_decision_collapse(self) -> None:
        """Testa colapso de decisão em superposição."""
        options = ["option_a", "option_b"]
        state = QuantumState(num_qubits=2)
        probs = {"option_a": 0.5, "option_b": 0.5}

        decision = SuperpositionDecision(options=options, quantum_state=state, probabilities=probs)

        result = decision.collapse()

        assert result in options
        assert decision.final_decision == result
        assert decision.confidence >= 0.0
        assert decision.confidence <= 1.0

    def test_superposition_decision_collapse_multiple_times(self) -> None:
        """Testa múltiplos colapsos de decisão."""
        options = ["a", "b", "c", "d"]
        # Create equal superposition: (|000⟩ + |001⟩ + |010⟩ + |011⟩) / 2
        # For 4 options, we need 2 qubits in superposition
        sv = np.array([0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0], dtype=complex)
        state = QuantumState(num_qubits=3, statevector=sv)
        probs = {opt: 0.25 for opt in options}

        results = []
        for _ in range(20):
            # Recreate state for each iteration (measurement collapses state)
            sv = np.array([0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0], dtype=complex)
            state = QuantumState(num_qubits=3, statevector=sv)
            decision = SuperpositionDecision(
                options=options, quantum_state=state, probabilities=probs
            )
            result = decision.collapse()
            results.append(result)

        # Should get variety of results (probabilistic)
        assert len(set(results)) > 1  # Not always the same


class TestQuantumDecisionMaker:
    """Testes para QuantumDecisionMaker."""

    def test_decision_maker_initialization(self) -> None:
        """Testa inicialização do decision maker."""
        maker = QuantumDecisionMaker(num_qubits=3)

        assert maker.num_qubits == 3
        assert maker.engine is not None

    def test_make_decision(self) -> None:
        """Testa criação de decisão."""
        maker = QuantumDecisionMaker(num_qubits=3)
        options = ["choice_1", "choice_2", "choice_3"]

        decision = maker.make_decision(options)

        assert isinstance(decision, SuperpositionDecision)
        assert decision.options == options
        assert len(decision.probabilities) > 0

    def test_make_decision_too_many_options(self) -> None:
        """Testa decisão com muitas opções."""
        maker = QuantumDecisionMaker(num_qubits=2)  # Max 4 options
        options = ["a", "b", "c", "d", "e"]  # 5 options

        with pytest.raises(ValueError, match="Too many options"):
            maker.make_decision(options)

    def test_make_decision_single_option(self) -> None:
        """Testa decisão com única opção."""
        maker = QuantumDecisionMaker(num_qubits=2)
        options = ["only_choice"]

        decision = maker.make_decision(options)
        result = decision.collapse()

        assert result == "only_choice"

    @pytest.mark.skipif(not QISKIT_AVAILABLE, reason="Qiskit not installed")
    def test_demonstrate_entanglement(self) -> None:
        """Testa demonstração de entrelaçamento."""
        maker = QuantumDecisionMaker(num_qubits=2)

        circuit, counts = maker.demonstrate_entanglement()

        assert circuit is not None
        assert isinstance(counts, dict)
        # Bell state should only measure |00⟩ and |11⟩
        # Remove spaces from outcomes and check first 2 bits (qubits 0-1)
        cleaned_outcomes = [outcome.replace(" ", "")[:2] for outcome in counts.keys()]
        assert all(outcome in ["00", "11"] for outcome in cleaned_outcomes)

    def test_decision_maker_without_qiskit(self) -> None:
        """Testa decision maker sem Qiskit (fallback clássico)."""
        maker = QuantumDecisionMaker(num_qubits=2)
        options = ["opt1", "opt2", "opt3"]

        # Should work even without Qiskit (classical fallback)
        decision = maker.make_decision(options)
        result = decision.collapse()

        assert result in options

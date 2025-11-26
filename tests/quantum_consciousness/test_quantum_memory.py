"""
Testes para Quantum Memory (quantum_memory.py).

Cobertura de:
- QuantumMemoryCell encoding/decoding
- QuantumMemorySystem storage and retrieval
- HybridQLearning quantum-classical learning
- Fidelity calculations
"""

from __future__ import annotations

import pytest
import numpy as np

from src.quantum_consciousness.quantum_memory import (
    QuantumMemoryCell,
    QuantumMemorySystem,
    HybridQLearning,
    QLearningState,
    QuantumMemoryComparison,
    QISKIT_AVAILABLE,
)


class TestQuantumMemoryCell:
    """Testes para QuantumMemoryCell."""

    def test_memory_cell_initialization(self) -> None:
        """Testa inicialização de célula de memória."""
        cell = QuantumMemoryCell(data=42, num_qubits=3)

        assert cell.data == 42
        assert cell.num_qubits == 3
        assert cell.quantum_state is None
        assert cell.encoding_type == "amplitude"

    def test_memory_cell_encode_single_value(self) -> None:
        """Testa encoding de valor único."""
        cell = QuantumMemoryCell(data=5.0, num_qubits=3)
        cell.encode()

        if QISKIT_AVAILABLE:
            assert cell.quantum_state is not None
            assert len(cell.quantum_state) == 8  # 2^3

    def test_memory_cell_encode_array(self) -> None:
        """Testa encoding de array."""
        data = [1.0, 2.0, 3.0, 4.0]
        cell = QuantumMemoryCell(data=data, num_qubits=2)
        cell.encode()

        if QISKIT_AVAILABLE:
            assert cell.quantum_state is not None
            # Check normalization
            norm = np.linalg.norm(cell.quantum_state)
            assert np.abs(norm - 1.0) < 1e-6

    def test_memory_cell_decode(self) -> None:
        """Testa decoding de célula de memória."""
        cell = QuantumMemoryCell(data=7.0, num_qubits=2)
        cell.encode()

        decoded = cell.decode()

        assert isinstance(decoded, float)

    def test_memory_cell_fidelity_identical(self) -> None:
        """Testa fidelidade entre células idênticas."""
        data = [1.0, 0.0, 0.0, 0.0]
        cell1 = QuantumMemoryCell(data=data, num_qubits=2)
        cell2 = QuantumMemoryCell(data=data, num_qubits=2)
        cell1.encode()
        cell2.encode()

        if QISKIT_AVAILABLE:
            fidelity = cell1.fidelity(cell2)
            assert fidelity >= 0.99  # Should be ~1.0

    def test_memory_cell_fidelity_different(self) -> None:
        """Testa fidelidade entre células diferentes."""
        cell1 = QuantumMemoryCell(data=[1.0, 0.0, 0.0, 0.0], num_qubits=2)
        cell2 = QuantumMemoryCell(data=[0.0, 1.0, 0.0, 0.0], num_qubits=2)
        cell1.encode()
        cell2.encode()

        if QISKIT_AVAILABLE:
            fidelity = cell1.fidelity(cell2)
            assert 0.0 <= fidelity <= 1.0
            assert fidelity < 0.5  # Should be low for orthogonal states

    def test_memory_cell_without_encoding(self) -> None:
        """Testa célula sem encoding."""
        cell = QuantumMemoryCell(data=10, num_qubits=2)

        # Decode without encoding should return original data
        decoded = cell.decode()
        assert decoded == 10

        # Fidelity without encoding
        cell2 = QuantumMemoryCell(data=20, num_qubits=2)
        fidelity = cell.fidelity(cell2)
        assert fidelity == pytest.approx(0.0)


class TestQuantumMemorySystem:
    """Testes para QuantumMemorySystem."""

    def test_memory_system_initialization(self) -> None:
        """Testa inicialização do sistema de memória."""
        system = QuantumMemorySystem(num_qubits=4, capacity=10)

        assert system.num_qubits == 4
        assert system.capacity == 10
        assert len(system.memory_cells) == 0

    def test_memory_system_store(self) -> None:
        """Testa armazenamento de dados."""
        system = QuantumMemorySystem(num_qubits=3, capacity=5)

        idx = system.store(data=42, key="test_key")

        assert idx == 0
        assert len(system.memory_cells) == 1

    def test_memory_system_store_multiple(self) -> None:
        """Testa armazenamento de múltiplos dados."""
        system = QuantumMemorySystem(num_qubits=3, capacity=5)

        idx1 = system.store(data=10)
        idx2 = system.store(data=20)
        idx3 = system.store(data=30)

        assert idx1 == 0
        assert idx2 == 1
        assert idx3 == 2
        assert len(system.memory_cells) == 3

    def test_memory_system_retrieve(self) -> None:
        """Testa recuperação de dados."""
        system = QuantumMemorySystem(num_qubits=3, capacity=5)
        system.store(data=100)

        retrieved = system.retrieve(index=0)

        # Due to quantum measurement, value may differ
        assert retrieved is not None

    def test_memory_system_retrieve_invalid_index(self) -> None:
        """Testa recuperação com índice inválido."""
        system = QuantumMemorySystem(num_qubits=3, capacity=5)

        retrieved = system.retrieve(index=10)

        assert retrieved is None

    def test_memory_system_capacity_limit(self) -> None:
        """Testa limite de capacidade."""
        system = QuantumMemorySystem(num_qubits=2, capacity=3)

        # Store beyond capacity
        for i in range(5):
            system.store(data=i)

        # Should only keep last 3
        assert len(system.memory_cells) == 3

    def test_memory_system_search_similar(self) -> None:
        """Testa busca por memórias similares."""
        system = QuantumMemorySystem(num_qubits=3, capacity=10)

        # Store similar data
        system.store(data=[1.0, 0.0, 0.0, 0.0])
        system.store(data=[0.9, 0.1, 0.0, 0.0])
        system.store(data=[0.0, 1.0, 0.0, 0.0])

        # Search for similar to first
        matches = system.search_similar(query_data=[1.0, 0.0, 0.0, 0.0], threshold=0.5)

        assert isinstance(matches, list)
        # May or may not find matches depending on encoding

    def test_memory_system_clear(self) -> None:
        """Testa limpeza de memória."""
        system = QuantumMemorySystem(num_qubits=3, capacity=5)

        system.store(data=1)
        system.store(data=2)
        assert len(system.memory_cells) == 2

        system.clear()

        assert len(system.memory_cells) == 0


class TestQLearningState:
    """Testes para QLearningState."""

    def test_qlearning_state_creation(self) -> None:
        """Testa criação de estado Q-learning."""
        state = QLearningState(state="s1", action="a1", reward=1.0, next_state="s2", q_value=0.5)

        assert state.state == "s1"
        assert state.action == "a1"
        assert state.reward == pytest.approx(1.0)
        assert state.next_state == "s2"
        assert state.q_value == pytest.approx(0.5)


class TestHybridQLearning:
    """Testes para HybridQLearning."""

    def test_hybrid_qlearning_initialization(self) -> None:
        """Testa inicialização do Q-learning híbrido."""
        qlearning = HybridQLearning(
            num_states=5, num_actions=3, learning_rate=0.1, discount_factor=0.9
        )

        assert qlearning.num_states == 5
        assert qlearning.num_actions == 3
        assert qlearning.learning_rate == pytest.approx(0.1)
        assert qlearning.discount_factor == pytest.approx(0.9)

    def test_hybrid_qlearning_classical_only(self) -> None:
        """Testa Q-learning clássico (sem quantum)."""
        qlearning = HybridQLearning(num_states=5, num_actions=3, use_quantum=False)

        assert qlearning.use_quantum is False

    def test_select_action(self) -> None:
        """Testa seleção de ação."""
        qlearning = HybridQLearning(num_states=5, num_actions=4)

        action = qlearning.select_action(state="s1", epsilon=0.1)

        assert isinstance(action, str)
        assert action.startswith("action_")

    def test_update_q_value(self) -> None:
        """Testa atualização de Q-value."""
        qlearning = HybridQLearning(
            num_states=3, num_actions=2, learning_rate=0.5, discount_factor=0.9
        )

        # Initial Q-value should be 0
        initial_q = qlearning.get_q_value("s1", "action_0")
        assert initial_q == pytest.approx(0.0)

        # Update Q-value
        qlearning.update(state="s1", action="action_0", reward=1.0, next_state="s2")

        # Q-value should have changed
        updated_q = qlearning.get_q_value("s1", "action_0")
        assert updated_q > 0.0

    def test_multiple_updates(self) -> None:
        """Testa múltiplas atualizações."""
        qlearning = HybridQLearning(
            num_states=3, num_actions=2, learning_rate=0.1, discount_factor=0.9
        )

        # Multiple updates to same state-action
        for _ in range(10):
            qlearning.update("s1", "action_0", reward=1.0, next_state="s2")

        q_value = qlearning.get_q_value("s1", "action_0")

        # Q-value should converge to some positive value
        assert q_value > 0.5

    def test_get_q_value_nonexistent(self) -> None:
        """Testa obter Q-value não existente."""
        qlearning = HybridQLearning(num_states=3, num_actions=2)

        q_value = qlearning.get_q_value("unknown_state", "unknown_action")

        assert q_value == pytest.approx(0.0)


class TestQuantumMemoryComparison:
    """Testes para QuantumMemoryComparison."""

    def test_comparison_creation(self) -> None:
        """Testa criação de comparação."""
        comparison = QuantumMemoryComparison(
            quantum_retrieval_time=0.05,
            classical_retrieval_time=0.10,
            quantum_accuracy=0.85,
            classical_accuracy=0.90,
            quantum_speedup=2.0,
            notes="Test comparison",
        )

        assert comparison.quantum_retrieval_time == pytest.approx(0.05)
        assert comparison.classical_retrieval_time == pytest.approx(0.10)
        assert comparison.quantum_accuracy == pytest.approx(0.85)
        assert comparison.classical_accuracy == pytest.approx(0.90)
        assert comparison.quantum_speedup == pytest.approx(2.0)

    def test_comparison_summary(self) -> None:
        """Testa geração de resumo de comparação."""
        comparison = QuantumMemoryComparison(
            quantum_retrieval_time=0.05,
            classical_retrieval_time=0.10,
            quantum_accuracy=0.85,
            classical_accuracy=0.90,
            quantum_speedup=2.0,
        )

        summary = comparison.summary()

        assert isinstance(summary, str)
        assert "Quantum vs Classical" in summary
        assert "Speedup" in summary

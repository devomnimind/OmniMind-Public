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
Testes para Hybrid Cognition (hybrid_cognition.py).

Cobertura de:
- ClassicalQuantumBridge encoding/decoding
- CognitionMetrics comparison
- HybridCognitionSystem strategy selection
- Optimization strategies (classical, quantum, hybrid)
"""

from __future__ import annotations

import pytest

from src.quantum_consciousness.hybrid_cognition import (
    ClassicalQuantumBridge,
    CognitionMetrics,
    HybridCognitionSystem,
    OptimizationStrategy,
)


class TestCognitionMetrics:
    """Testes para CognitionMetrics."""

    def test_metrics_creation(self) -> None:
        """Testa criação de métricas."""
        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.CLASSICAL,
            execution_time=0.5,
            accuracy=0.85,
            solution_quality=0.80,
            num_iterations=100,
        )

        assert metrics.strategy == OptimizationStrategy.CLASSICAL
        assert metrics.execution_time == pytest.approx(0.5)
        assert metrics.accuracy == pytest.approx(0.85)
        assert metrics.solution_quality == pytest.approx(0.80)
        assert metrics.num_iterations == 100

    def test_metrics_speedup_calculation(self) -> None:
        """Testa cálculo de speedup."""
        metrics1 = CognitionMetrics(
            strategy=OptimizationStrategy.QUANTUM,
            execution_time=0.1,
            accuracy=0.85,
            solution_quality=0.85,
            num_iterations=10,
        )

        metrics2 = CognitionMetrics(
            strategy=OptimizationStrategy.CLASSICAL,
            execution_time=0.5,
            accuracy=0.85,
            solution_quality=0.80,
            num_iterations=100,
        )

        speedup = metrics1.speedup_vs(metrics2)

        assert speedup == pytest.approx(5.0)  # 0.5 / 0.1 = 5x faster

    def test_metrics_summary(self) -> None:
        """Testa geração de resumo de métricas."""
        metrics = CognitionMetrics(
            strategy=OptimizationStrategy.HYBRID,
            execution_time=0.3,
            accuracy=0.90,
            solution_quality=0.88,
            num_iterations=50,
            notes="Test metrics",
        )

        summary = metrics.summary()

        assert isinstance(summary, str)
        assert "HYBRID" in summary
        assert "0.3" in summary
        assert "Test metrics" in summary


class TestClassicalQuantumBridge:
    """Testes para ClassicalQuantumBridge."""

    def test_bridge_initialization(self) -> None:
        """Testa inicialização da bridge."""
        bridge = ClassicalQuantumBridge(num_qubits=4)

        assert bridge.num_qubits == 4
        assert bridge.encoding_method == "amplitude"

    def test_bridge_encode_classical_data(self) -> None:
        """Testa encoding de dados clássicos."""
        bridge = ClassicalQuantumBridge(num_qubits=3)

        data = [1.0, 2.0, 3.0]
        encoded = bridge.encode_classical_data(data)

        # Currently pass-through
        assert encoded == data

    def test_bridge_decode_quantum_result(self) -> None:
        """Testa decoding de resultado quântico."""
        bridge = ClassicalQuantumBridge(num_qubits=3)

        quantum_result = {"00": 50, "11": 50}
        decoded = bridge.decode_quantum_result(quantum_result)

        # Currently pass-through
        assert decoded == quantum_result

    def test_bridge_validate_compatibility_list(self) -> None:
        """Testa validação de compatibilidade para lista."""
        bridge = ClassicalQuantumBridge(num_qubits=3)  # Max size 8

        small_data = [1, 2, 3, 4]  # Size 4 < 8
        assert bridge.validate_compatibility(small_data) is True

        large_data = list(range(20))  # Size 20 > 8
        assert bridge.validate_compatibility(large_data) is False

    def test_bridge_validate_compatibility_scalar(self) -> None:
        """Testa validação de compatibilidade para escalar."""
        bridge = ClassicalQuantumBridge(num_qubits=3)

        scalar = 42
        assert bridge.validate_compatibility(scalar) is True


class TestHybridCognitionSystem:
    """Testes para HybridCognitionSystem."""

    def test_hybrid_system_initialization(self) -> None:
        """Testa inicialização do sistema híbrido."""
        system = HybridCognitionSystem(
            num_qubits=4,
            default_strategy=OptimizationStrategy.AUTO,
            enable_quantum=True,
        )

        assert system.num_qubits == 4
        assert system.default_strategy == OptimizationStrategy.AUTO
        assert system.bridge is not None

    def test_hybrid_system_classical_only(self) -> None:
        """Testa sistema apenas clássico."""
        system = HybridCognitionSystem(num_qubits=3, enable_quantum=False)

        assert system.quantum_available is False

    def test_solve_classical_optimization(self) -> None:
        """Testa resolução de otimização clássica."""
        system = HybridCognitionSystem(num_qubits=3)

        problem = {
            "type": "optimization",
            "size": 10,
            "options": ["opt1", "opt2", "opt3"],
        }

        solution, metrics = system.solve_optimization(
            problem, strategy=OptimizationStrategy.CLASSICAL
        )

        assert solution is not None
        assert isinstance(metrics, CognitionMetrics)
        assert metrics.strategy == OptimizationStrategy.CLASSICAL
        assert metrics.execution_time > 0

    def test_solve_quantum_optimization(self) -> None:
        """Testa resolução de otimização quântica."""
        system = HybridCognitionSystem(num_qubits=3, enable_quantum=True)

        problem = {"type": "search", "size": 8, "options": ["a", "b", "c", "d"]}

        solution, metrics = system.solve_optimization(
            problem, strategy=OptimizationStrategy.QUANTUM
        )

        assert solution is not None
        assert isinstance(metrics, CognitionMetrics)
        # Pode ser QUANTUM ou CLASSICAL (fallback)
        assert metrics.strategy in [
            OptimizationStrategy.QUANTUM,
            OptimizationStrategy.CLASSICAL,
        ]

    def test_solve_hybrid_optimization(self) -> None:
        """Testa resolução de otimização híbrida."""
        system = HybridCognitionSystem(num_qubits=3)

        problem = {"type": "combinatorial", "size": 20, "options": ["x", "y", "z"]}

        solution, metrics = system.solve_optimization(problem, strategy=OptimizationStrategy.HYBRID)

        assert solution is not None
        assert isinstance(metrics, CognitionMetrics)
        assert metrics.strategy == OptimizationStrategy.HYBRID

    def test_auto_strategy_selection_small_problem(self) -> None:
        """Testa seleção automática para problema pequeno."""
        system = HybridCognitionSystem(num_qubits=3)

        small_problem = {"type": "simple", "size": 5}

        solution, metrics = system.solve_optimization(
            small_problem, strategy=OptimizationStrategy.AUTO
        )

        assert solution is not None
        assert isinstance(metrics, CognitionMetrics)

    def test_auto_strategy_selection_large_problem(self) -> None:
        """Testa seleção automática para problema grande."""
        system = HybridCognitionSystem(num_qubits=3)

        large_problem = {"type": "complex", "size": 150}

        solution, metrics = system.solve_optimization(
            large_problem, strategy=OptimizationStrategy.AUTO
        )

        assert solution is not None
        assert isinstance(metrics, CognitionMetrics)

    def test_compare_strategies(self) -> None:
        """Testa comparação de estratégias."""
        system = HybridCognitionSystem(num_qubits=3)

        problem = {"type": "test", "size": 10, "options": ["a", "b", "c"]}

        results = system.compare_strategies(problem)

        assert isinstance(results, dict)
        assert OptimizationStrategy.CLASSICAL in results
        # Outros podem ou não estar dependendo de quantum_available

    def test_compare_specific_strategies(self) -> None:
        """Testa comparação de estratégias específicas."""
        system = HybridCognitionSystem(num_qubits=3)

        problem = {"type": "test", "size": 10}
        strategies = [OptimizationStrategy.CLASSICAL, OptimizationStrategy.HYBRID]

        results = system.compare_strategies(problem, strategies=strategies)

        assert len(results) == 2
        assert OptimizationStrategy.CLASSICAL in results
        assert OptimizationStrategy.HYBRID in results

    def test_metrics_history(self) -> None:
        """Testa histórico de métricas."""
        system = HybridCognitionSystem(num_qubits=3)

        problem = {"type": "test", "size": 5}

        # Run multiple optimizations
        system.solve_optimization(problem, strategy=OptimizationStrategy.CLASSICAL)
        system.solve_optimization(problem, strategy=OptimizationStrategy.HYBRID)

        assert len(system.metrics_history) >= 2

    def test_get_metrics_summary(self) -> None:
        """Testa obtenção de resumo de métricas."""
        system = HybridCognitionSystem(num_qubits=3)

        problem = {"type": "test", "size": 5}
        system.solve_optimization(problem)

        summary = system.get_metrics_summary()

        assert isinstance(summary, str)
        assert "Metrics Summary" in summary or "Run" in summary

    def test_get_metrics_summary_empty(self) -> None:
        """Testa resumo de métricas vazio."""
        system = HybridCognitionSystem(num_qubits=3)

        summary = system.get_metrics_summary()

        assert "No metrics" in summary

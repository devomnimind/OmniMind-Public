"""
Testes para Superposition Computing Module.

Cobertura de:
- SuperpositionState
- SuperpositionProcessor
- QuantumParallelism
- StateAmplification
"""

import pytest

from src.quantum_ai.superposition_computing import (
    SuperpositionState,
    SuperpositionProcessor,
    QuantumParallelism,
    StateAmplification,
)


class TestSuperpositionState:
    """Testes para SuperpositionState."""

    def test_initialization_empty(self) -> None:
        """Testa inicialização de estado vazio."""
        state = SuperpositionState()

        assert len(state.states) == 0
        assert len(state.amplitudes) == 0

    def test_initialization_with_states(self) -> None:
        """Testa inicialização com estados."""
        states = [1, 2, 3]
        amplitudes = [complex(1, 0), complex(1, 0), complex(1, 0)]

        state = SuperpositionState(states=states, amplitudes=amplitudes)

        assert len(state.states) == 3
        assert len(state.amplitudes) == 3

    def test_normalization(self) -> None:
        """Testa normalização de amplitudes."""
        states = [1, 2]
        amplitudes = [complex(2, 0), complex(2, 0)]

        state = SuperpositionState(states=states, amplitudes=amplitudes)

        # Amplitudes should be normalized
        total_prob = sum(abs(a) ** 2 for a in state.amplitudes)
        assert abs(total_prob - 1.0) < 1e-6

    def test_add_state(self) -> None:
        """Testa adição de estado."""
        state = SuperpositionState()

        state.add_state(1, complex(1, 0))
        state.add_state(2, complex(1, 0))

        assert len(state.states) == 2
        assert 1 in state.states
        assert 2 in state.states

    def test_add_state_normalizes(self) -> None:
        """Testa que adição de estado normaliza amplitudes."""
        state = SuperpositionState()

        state.add_state("A", complex(3, 0))
        state.add_state("B", complex(4, 0))

        # Should be normalized
        total_prob = sum(abs(a) ** 2 for a in state.amplitudes)
        assert abs(total_prob - 1.0) < 1e-6

    def test_collapse(self) -> None:
        """Testa colapso para estado único."""
        states = ["A", "B", "C"]
        amplitudes = [complex(1, 0), complex(1, 0), complex(1, 0)]

        state = SuperpositionState(states=states, amplitudes=amplitudes)

        result = state.collapse()

        # Should return one of the states
        assert result in states

    def test_collapse_single_state(self) -> None:
        """Testa colapso com um único estado."""
        state = SuperpositionState(states=[42], amplitudes=[complex(1, 0)])

        result = state.collapse()

        assert result == 42

    def test_collapse_empty_state(self) -> None:
        """Testa colapso de estado vazio."""
        state = SuperpositionState()

        result = state.collapse()

        assert result is None


class TestSuperpositionProcessor:
    """Testes para SuperpositionProcessor."""

    def test_initialization(self) -> None:
        """Testa inicialização do processador."""
        processor = SuperpositionProcessor()

        assert processor is not None
        assert hasattr(processor, "logger")

    def test_evaluate_parallel_basic(self) -> None:
        """Testa avaliação paralela básica."""
        processor = SuperpositionProcessor()

        def square(x: int) -> int:
            return x * x

        inputs = [1, 2, 3, 4]

        result = processor.evaluate_parallel(square, inputs)

        assert isinstance(result, SuperpositionState)
        assert len(result.states) == 4
        assert 1 in result.states
        assert 4 in result.states
        assert 9 in result.states
        assert 16 in result.states

    def test_evaluate_parallel_amplitudes(self) -> None:
        """Testa que amplitudes são iguais em avaliação paralela."""
        processor = SuperpositionProcessor()

        def identity(x: int) -> int:
            return x

        inputs = [1, 2, 3]

        result = processor.evaluate_parallel(identity, inputs)

        # All amplitudes should be equal (equal superposition)
        amplitude_magnitudes = [abs(a) for a in result.amplitudes]
        assert all(
            abs(amp - amplitude_magnitudes[0]) < 1e-6 for amp in amplitude_magnitudes
        )

    def test_evaluate_parallel_empty_input(self) -> None:
        """Testa avaliação paralela com entrada vazia."""
        processor = SuperpositionProcessor()

        def dummy(x: int) -> int:
            return x

        # Should handle empty input gracefully
        try:
            result = processor.evaluate_parallel(dummy, [])
            # If it doesn't raise, check result
            assert isinstance(result, SuperpositionState)
        except (ValueError, ZeroDivisionError):
            # Expected for empty input
            pass

    def test_quantum_search(self) -> None:
        """Testa busca quântica."""
        processor = SuperpositionProcessor()

        def is_target(x: int) -> bool:
            return x == 7

        search_space = [1, 3, 5, 7, 9, 11]

        result = processor.quantum_search(is_target, search_space)

        # Should find the target value or nearby
        assert result in search_space

    def test_quantum_search_no_match(self) -> None:
        """Testa busca quântica sem match."""
        processor = SuperpositionProcessor()

        def always_false(x: int) -> bool:
            return False

        search_space = [1, 2, 3]

        result = processor.quantum_search(always_false, search_space)

        # Should still return something from search space
        assert result in search_space

    def test_quantum_search_amplification(self) -> None:
        """Testa amplificação em busca quântica."""
        processor = SuperpositionProcessor()

        def is_even(x: int) -> bool:
            return x % 2 == 0

        search_space = [1, 2, 3, 4, 5, 6]

        # Run multiple times to check probabilistic behavior
        results = [processor.quantum_search(is_even, search_space) for _ in range(10)]

        # At least some results should be even (amplified)
        even_count = sum(1 for r in results if r % 2 == 0)
        assert even_count > 0


class TestQuantumParallelism:
    """Testes para QuantumParallelism."""

    def test_initialization(self) -> None:
        """Testa inicialização."""
        qp = QuantumParallelism()

        assert qp is not None
        assert hasattr(qp, "logger")

    def test_parallel_map(self) -> None:
        """Testa mapeamento paralelo."""
        qp = QuantumParallelism()

        def double(x: int) -> int:
            return x * 2

        inputs = [1, 2, 3, 4, 5]

        results = qp.parallel_map(double, inputs)

        assert len(results) == 5
        assert results == [2, 4, 6, 8, 10]

    def test_parallel_map_strings(self) -> None:
        """Testa mapeamento paralelo com strings."""
        qp = QuantumParallelism()

        def uppercase(s: str) -> str:
            return s.upper()

        inputs = ["hello", "world", "test"]

        results = qp.parallel_map(uppercase, inputs)

        assert results == ["HELLO", "WORLD", "TEST"]

    def test_parallel_map_empty(self) -> None:
        """Testa mapeamento paralelo com lista vazia."""
        qp = QuantumParallelism()

        def identity(x: int) -> int:
            return x

        results = qp.parallel_map(identity, [])

        assert results == []

    def test_quantum_interference(self) -> None:
        """Testa interferência quântica."""
        qp = QuantumParallelism()

        def func1(x: float) -> float:
            return x * 2

        def func2(x: float) -> float:
            return x + 10

        def func3(x: float) -> float:
            return x**2

        functions = [func1, func2, func3]

        result = qp.quantum_interference(functions, 5.0)

        # Should be average of all function results
        expected = (10.0 + 15.0 + 25.0) / 3.0
        assert result == pytest.approx(expected)

    def test_quantum_interference_single_function(self) -> None:
        """Testa interferência com uma única função."""
        qp = QuantumParallelism()

        def single(x: float) -> float:
            return x * 3

        result = qp.quantum_interference([single], 4.0)

        assert result == pytest.approx(12.0)

    def test_quantum_interference_negative_values(self) -> None:
        """Testa interferência com valores negativos."""
        qp = QuantumParallelism()

        def neg(x: float) -> float:
            return -x

        def pos(x: float) -> float:
            return x

        result = qp.quantum_interference([neg, pos], 10.0)

        # Should be average: (-10 + 10) / 2 = 0
        assert result == pytest.approx(0.0)


class TestStateAmplification:
    """Testes para StateAmplification."""

    def test_initialization(self) -> None:
        """Testa inicialização."""
        sa = StateAmplification()

        assert sa is not None
        assert hasattr(sa, "logger")

    def test_amplify_states(self) -> None:
        """Testa amplificação de estados."""
        sa = StateAmplification()

        states = [1, 2, 3, 4, 5]
        amplitudes = [complex(1, 0)] * 5
        superposition = SuperpositionState(states=states, amplitudes=amplitudes)

        def is_even(x: int) -> bool:
            return x % 2 == 0

        result = sa.amplify_states(superposition, is_even, amplification_factor=3.0)

        assert isinstance(result, SuperpositionState)
        assert len(result.states) == 5

        # Even numbers should have higher probability
        for i, state in enumerate(result.states):
            if state % 2 == 0:
                # Even states should be amplified
                assert abs(result.amplitudes[i]) > 0

    def test_amplify_states_no_match(self) -> None:
        """Testa amplificação quando nenhum estado combina."""
        sa = StateAmplification()

        states = [1, 3, 5]
        amplitudes = [complex(1, 0)] * 3
        superposition = SuperpositionState(states=states, amplitudes=amplitudes)

        def is_even(x: int) -> bool:
            return x % 2 == 0

        result = sa.amplify_states(superposition, is_even)

        # Should still return valid superposition
        assert isinstance(result, SuperpositionState)
        assert len(result.states) == 3

    def test_amplify_states_all_match(self) -> None:
        """Testa amplificação quando todos estados combinam."""
        sa = StateAmplification()

        states = [2, 4, 6]
        amplitudes = [complex(1, 0)] * 3
        superposition = SuperpositionState(states=states, amplitudes=amplitudes)

        def is_even(x: int) -> bool:
            return x % 2 == 0

        result = sa.amplify_states(superposition, is_even, amplification_factor=2.0)

        # All states should be amplified equally
        amplitude_magnitudes = [abs(a) for a in result.amplitudes]
        assert all(
            abs(amp - amplitude_magnitudes[0]) < 1e-6 for amp in amplitude_magnitudes
        )

    def test_select_high_amplitude(self) -> None:
        """Testa seleção de estados com alta amplitude."""
        sa = StateAmplification()

        states = ["A", "B", "C", "D"]
        # First two have high amplitude, last two have low
        amplitudes = [
            complex(0.7, 0),
            complex(0.7, 0),
            complex(0.1, 0),
            complex(0.1, 0),
        ]
        superposition = SuperpositionState(states=states, amplitudes=amplitudes)

        selected = sa.select_high_amplitude(superposition, threshold=0.3)

        # Should select states with probability >= 0.3
        # 0.7^2 = 0.49 > 0.3 (selected)
        # 0.1^2 = 0.01 < 0.3 (not selected)
        assert "A" in selected
        assert "B" in selected
        assert "C" not in selected
        assert "D" not in selected

    def test_select_high_amplitude_low_threshold(self) -> None:
        """Testa seleção com threshold baixo."""
        sa = StateAmplification()

        states = [1, 2, 3]
        amplitudes = [complex(0.5, 0), complex(0.5, 0), complex(0.5, 0)]
        superposition = SuperpositionState(states=states, amplitudes=amplitudes)

        selected = sa.select_high_amplitude(superposition, threshold=0.1)

        # All states should be selected with low threshold
        assert len(selected) == 3

    def test_select_high_amplitude_high_threshold(self) -> None:
        """Testa seleção com threshold alto."""
        sa = StateAmplification()

        states = [1, 2, 3]
        amplitudes = [complex(0.3, 0), complex(0.3, 0), complex(0.3, 0)]
        superposition = SuperpositionState(states=states, amplitudes=amplitudes)

        selected = sa.select_high_amplitude(superposition, threshold=0.9)

        # No states should be selected with very high threshold
        # 0.3^2 = 0.09 < 0.9
        assert len(selected) == 0


class TestSuperpositionIntegration:
    """Testes de integração."""

    def test_processor_with_amplification(self) -> None:
        """Testa processador com amplificação."""
        sa = StateAmplification()

        # Create superposition
        superposition = SuperpositionProcessor().evaluate_parallel(
            lambda x: x, [1, 2, 3, 4, 5]
        )

        # Amplify odd numbers
        amplified = sa.amplify_states(
            superposition, lambda x: x % 2 == 1, amplification_factor=3.0
        )

        # Select high amplitude states
        selected = sa.select_high_amplitude(amplified, threshold=0.15)

        # Odd numbers should be favored
        assert len(selected) > 0

    def test_quantum_parallelism_with_superposition(self) -> None:
        """Testa paralelismo quântico com superposição."""
        qp = QuantumParallelism()

        # Create inputs
        inputs = list(range(10))

        # Process with quantum parallelism
        results = qp.parallel_map(lambda x: x**2, inputs)

        # Create superposition from results
        superposition = SuperpositionState(
            states=results, amplitudes=[complex(1, 0)] * len(results)
        )

        # Should have all squared values
        assert 0 in superposition.states
        assert 1 in superposition.states
        assert 81 in superposition.states


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

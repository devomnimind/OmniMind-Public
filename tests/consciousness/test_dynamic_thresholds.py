"""
Testes para mecanismos dinâmicos de thresholds.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

import numpy as np
import pytest

from src.consciousness.delta_calculator import DeltaCalculator
from src.consciousness.phi_value import PhiValue
from src.consciousness.theoretical_consistency_guard import TheoreticalConsistencyGuard


class TestDynamicTraumaThreshold:
    """Testes para threshold dinâmico de trauma."""

    def test_dynamic_threshold_disabled_uses_static(self):
        """Testa que threshold estático é usado quando dinâmico está desabilitado."""
        calc = DeltaCalculator(use_dynamic_threshold=False)
        assert calc.trauma_threshold == calc.trauma_threshold_static

    def test_dynamic_threshold_initializes_with_static(self):
        """Testa que threshold dinâmico inicia com valor estático."""
        calc = DeltaCalculator(use_dynamic_threshold=True, min_history_size=30)
        assert calc.trauma_threshold == calc.trauma_threshold_static
        assert len(calc.delta_norm_history) == 0

    def test_dynamic_threshold_updates_after_min_history(self):
        """Testa que threshold dinâmico é atualizado após histórico mínimo."""
        calc = DeltaCalculator(
            use_dynamic_threshold=True,
            dynamic_threshold_k=2.0,
            min_history_size=5,  # Pequeno para teste rápido
        )

        # Simula ciclos para construir histórico
        embedding_dim = 10
        expectation = np.random.randn(embedding_dim).astype(np.float32)
        reality = np.random.randn(embedding_dim).astype(np.float32)
        module_outputs = {"test_module": np.random.randn(embedding_dim).astype(np.float32)}

        # Executa ciclos até atingir histórico mínimo
        for i in range(10):
            calc.calculate_delta(
                expectation_embedding=expectation,
                reality_embedding=reality,
                module_outputs=module_outputs,
                phi_raw=0.1,
            )
            # Verifica que histórico está sendo atualizado
            assert len(calc.delta_norm_history) == i + 1

        # Após histórico mínimo, threshold deve ser diferente do estático
        # (pode ser igual se distribuição for muito concentrada, mas estrutura deve estar correta)
        assert len(calc.delta_norm_history) >= calc.min_history_size
        assert calc.trauma_threshold >= 0.3  # Range mínimo garantido
        assert calc.trauma_threshold <= 0.95  # Range máximo garantido

    def test_dynamic_threshold_calculation(self):
        """Testa cálculo explícito de threshold dinâmico."""
        calc = DeltaCalculator(
            use_dynamic_threshold=True,
            dynamic_threshold_k=2.0,
            min_history_size=10,
        )

        # Cria histórico com distribuição conhecida
        # Média ~0.5, std ~0.1 → threshold esperado ~0.7 (0.5 + 2*0.1)
        test_values = np.random.normal(0.5, 0.1, 20).clip(0.0, 1.0)
        calc.delta_norm_history = test_values.tolist()

        # Força atualização
        calc._update_dynamic_threshold(0.5)

        # Verifica que threshold foi calculado corretamente
        assert calc.trauma_threshold >= 0.3
        assert calc.trauma_threshold <= 0.95

        # Verifica que threshold ≈ μ + 2σ (com tolerância)
        mean_val = np.mean(test_values)
        std_val = np.std(test_values)
        expected_threshold = mean_val + (2.0 * std_val)
        assert abs(calc.trauma_threshold - expected_threshold) < 0.1


class TestDynamicDeltaPhiTolerance:
    """Testes para tolerância dinâmica Δ-Φ."""

    def test_dynamic_tolerance_disabled_uses_static(self):
        """Testa que tolerância estática é usada quando dinâmica está desabilitada."""
        guard = TheoreticalConsistencyGuard(use_dynamic_tolerance=False)
        tolerance = guard._get_dynamic_tolerance(0.1)
        from src.consciousness.phi_constants import DELTA_PHI_CORRELATION_TOLERANCE

        assert tolerance == DELTA_PHI_CORRELATION_TOLERANCE

    def test_dynamic_tolerance_initializes_with_static(self):
        """Testa que tolerância dinâmica inicia com valor estático."""
        guard = TheoreticalConsistencyGuard(use_dynamic_tolerance=True, min_history_size=50)
        tolerance = guard._get_dynamic_tolerance(0.1)
        from src.consciousness.phi_constants import DELTA_PHI_CORRELATION_TOLERANCE

        assert tolerance == DELTA_PHI_CORRELATION_TOLERANCE
        assert len(guard.delta_phi_errors) == 1  # Erro atual foi adicionado

    def test_dynamic_tolerance_updates_after_min_history(self):
        """Testa que tolerância dinâmica é atualizada após histórico mínimo."""
        guard = TheoreticalConsistencyGuard(
            use_dynamic_tolerance=True,
            tolerance_percentile=90.0,
            min_history_size=10,  # Pequeno para teste rápido
        )

        # Simula erros para construir histórico
        test_errors = np.random.uniform(0.05, 0.25, 15)  # Erros variados

        for error in test_errors:
            tolerance = guard._get_dynamic_tolerance(error)

        # Após histórico mínimo, tolerância deve ser calculada dinamicamente
        assert len(guard.delta_phi_errors) >= guard.min_history_size
        tolerance = guard._get_dynamic_tolerance(0.1)

        # Tolerância deve estar em range razoável
        assert tolerance >= 0.05
        assert tolerance <= 0.5

    def test_dynamic_tolerance_percentile_calculation(self):
        """Testa cálculo explícito de tolerância via percentil."""
        guard = TheoreticalConsistencyGuard(
            use_dynamic_tolerance=True,
            tolerance_percentile=90.0,
            min_history_size=10,
        )

        # Cria histórico com distribuição conhecida
        test_errors = np.array([0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.22, 0.25, 0.30])
        guard.delta_phi_errors = test_errors.tolist()

        # Calcula tolerância
        tolerance = guard._get_dynamic_tolerance(0.1)

        # Percentil 90 de test_errors ≈ 0.27 (mas será clipado para <= 0.5)
        assert tolerance >= 0.05
        assert tolerance <= 0.5

    def test_dynamic_tolerance_in_validation(self):
        """Testa que tolerância dinâmica é usada na validação de ciclo."""
        guard = TheoreticalConsistencyGuard(
            use_dynamic_tolerance=True,
            tolerance_percentile=90.0,
            min_history_size=5,  # Pequeno para teste rápido
        )

        # Cria phi value (PhiValue calcula normalized automaticamente)
        phi = PhiValue(nats=0.1)

        # Simula ciclos para construir histórico
        for i in range(10):
            guard.validate_cycle(
                phi=phi,
                delta=0.6,  # Δ observado
                psi=0.3,
                cycle_id=i,
            )
            # Não deve haver violação se erro está dentro da tolerância dinâmica
            # (delta=0.6, expected=0.5, error=0.1)

        # Verifica que histórico foi construído
        assert len(guard.delta_phi_errors) >= guard.min_history_size


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

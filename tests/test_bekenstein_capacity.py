#!/usr/bin/env python3
"""
Testes unitários para o módulo bekenstein_capacity.py
Garante cobertura mínima de 50% conforme Grupo 2 - Phase 1.
"""

import math

import pytest

from src.architecture.bekenstein_capacity import (
    HBAR,
    LN2,
    BekensteinArchitect,
    C,
)


class TestBekensteinConstants:
    """Testes para as constantes físicas."""

    def test_physical_constants_defined(self) -> None:
        """Testa que as constantes físicas estão definidas corretamente."""
        assert HBAR > 0, "Planck constant deve ser positiva"
        assert C > 0, "Velocidade da luz deve ser positiva"
        assert LN2 > 0, "ln(2) deve ser positivo"

    def test_hbar_value(self) -> None:
        """Testa valor da constante de Planck reduzida."""
        # Valor aproximado conhecido: 1.054571817e-34 J·s
        assert abs(HBAR - 1.054571817e-34) < 1e-40

    def test_speed_of_light_value(self) -> None:
        """Testa valor da velocidade da luz."""
        # Valor exato definido: 299,792,458 m/s
        assert C == 299792458

    def test_ln2_value(self) -> None:
        """Testa valor de ln(2)."""
        # Calcular e comparar
        expected_ln2 = math.log(2)
        assert abs(LN2 - expected_ln2) < 1e-10


class TestBekensteinArchitect:
    """Testes para a classe BekensteinArchitect."""

    @pytest.fixture
    def architect(self) -> BekensteinArchitect:
        """Cria instância do BekensteinArchitect para testes."""
        return BekensteinArchitect()

    def test_initialization(self, architect: BekensteinArchitect) -> None:
        """Testa inicialização do BekensteinArchitect."""
        assert architect is not None
        assert isinstance(architect, BekensteinArchitect)

    def test_compute_max_parameters_positive_inputs(self, architect: BekensteinArchitect) -> None:
        """Testa cálculo de parâmetros máximos com valores positivos."""
        compute_budget = 1.0
        spatial_extent = 1.0

        max_params = architect.compute_max_parameters(compute_budget, spatial_extent)

        assert max_params >= 0
        assert isinstance(max_params, int)

    def test_compute_max_parameters_zero_budget(self, architect: BekensteinArchitect) -> None:
        """Testa com budget zero."""
        with pytest.raises(ValueError, match="Compute budget and spatial extent must be positive"):
            architect.compute_max_parameters(compute_budget=0.0, spatial_extent=1.0)

    def test_compute_max_parameters_zero_extent(self, architect: BekensteinArchitect) -> None:
        """Testa com extent zero."""
        with pytest.raises(ValueError, match="Compute budget and spatial extent must be positive"):
            architect.compute_max_parameters(compute_budget=1.0, spatial_extent=0.0)

    def test_compute_max_parameters_scaling(self, architect: BekensteinArchitect) -> None:
        """Testa que parâmetros escalam corretamente com inputs."""
        params_1x = architect.compute_max_parameters(1.0, 1.0)
        params_2x = architect.compute_max_parameters(2.0, 2.0)

        # Dobrar budget e extent deve aumentar os parâmetros
        # (proporcional ao produto)
        assert params_2x >= params_1x  # Should at least not decrease
        # The relationship depends on the Bekenstein formula and integer rounding

    def test_compute_max_parameters_large_values(self, architect: BekensteinArchitect) -> None:
        """Testa com valores grandes."""
        max_params = architect.compute_max_parameters(compute_budget=1e6, spatial_extent=1e6)

        # Deve retornar um número válido
        assert max_params > 0
        assert isinstance(max_params, int)

    def test_compute_max_parameters_small_values(self, architect: BekensteinArchitect) -> None:
        """Testa com valores pequenos."""
        max_params = architect.compute_max_parameters(compute_budget=1e-6, spatial_extent=1e-6)

        # Pode ser zero ou muito pequeno
        assert max_params >= 0
        assert isinstance(max_params, int)

    def test_recommend_architecture_positive_params(self, architect: BekensteinArchitect) -> None:
        """Testa recomendação de arquitetura com parâmetros positivos."""
        target_params = 1000000  # 1M parameters

        recommendation = architect.recommend_architecture(target_params)

        assert "num_layers" in recommendation
        assert "params_per_layer" in recommendation
        assert "total_params" in recommendation
        assert recommendation["total_params"] == target_params
        assert recommendation["num_layers"] > 0
        assert recommendation["params_per_layer"] > 0

    def test_recommend_architecture_zero_params(self, architect: BekensteinArchitect) -> None:
        """Testa recomendação com zero parâmetros."""
        with pytest.raises(ValueError, match="Target parameters must be positive"):
            architect.recommend_architecture(0)

    def test_recommend_architecture_small_params(self, architect: BekensteinArchitect) -> None:
        """Testa com número pequeno de parâmetros."""
        target_params = 10

        recommendation = architect.recommend_architecture(target_params)

        assert recommendation["num_layers"] >= 1
        assert recommendation["total_params"] == target_params

    def test_recommend_architecture_large_params(self, architect: BekensteinArchitect) -> None:
        """Testa com número grande de parâmetros."""
        target_params = 1_000_000_000  # 1B parameters

        recommendation = architect.recommend_architecture(target_params)

        assert recommendation["num_layers"] > 0
        assert recommendation["params_per_layer"] > 0
        assert recommendation["total_params"] == target_params

    def test_recommend_architecture_consistency(self, architect: BekensteinArchitect) -> None:
        """Testa consistência da distribuição de parâmetros."""
        target_params = 1024

        recommendation = architect.recommend_architecture(target_params)

        # Verificar que a multiplicação aproximada faz sentido
        num_layers = recommendation["num_layers"]
        params_per_layer = recommendation["params_per_layer"]

        # Total aproximado (pode haver arredondamento)
        approx_total = num_layers * params_per_layer
        assert abs(approx_total - target_params) <= num_layers

    def test_recommend_architecture_num_layers_scaling(
        self, architect: BekensteinArchitect
    ) -> None:
        """Testa que num_layers escala logaritmicamente."""
        rec_small = architect.recommend_architecture(100)
        rec_large = architect.recommend_architecture(10000)

        # Mais parâmetros devem resultar em mais layers
        assert rec_large["num_layers"] >= rec_small["num_layers"]

    def test_recommend_architecture_returns_dict(self, architect: BekensteinArchitect) -> None:
        """Testa que retorna um dicionário válido."""
        recommendation = architect.recommend_architecture(1000)

        assert isinstance(recommendation, dict)
        assert len(recommendation) == 3

    def test_compute_max_parameters_deterministic(self, architect: BekensteinArchitect) -> None:
        """Testa que o cálculo é determinístico."""
        budget = 5.0
        extent = 3.0

        result1 = architect.compute_max_parameters(budget, extent)
        result2 = architect.compute_max_parameters(budget, extent)

        assert result1 == result2

    def test_recommend_architecture_deterministic(self, architect: BekensteinArchitect) -> None:
        """Testa que a recomendação é determinística."""
        target = 5000

        rec1 = architect.recommend_architecture(target)
        rec2 = architect.recommend_architecture(target)

        assert rec1 == rec2


class TestBekensteinIntegration:
    """Testes de integração para o módulo bekenstein."""

    def test_full_workflow(self) -> None:
        """Testa workflow completo: calcular capacidade e recomendar arquitetura."""
        architect = BekensteinArchitect()

        # 1. Calcular capacidade máxima
        max_params = architect.compute_max_parameters(compute_budget=10.0, spatial_extent=5.0)

        # 2. Recomendar arquitetura baseada na capacidade
        if max_params > 0:
            recommendation = architect.recommend_architecture(max_params)

            # Verificar que a recomendação é válida
            assert recommendation["total_params"] == max_params
            assert recommendation["num_layers"] > 0

    def test_multiple_recommendations(self) -> None:
        """Testa múltiplas recomendações em sequência."""
        architect = BekensteinArchitect()

        targets = [100, 1000, 10000, 100000]
        recommendations = []

        for target in targets:
            rec = architect.recommend_architecture(target)
            recommendations.append(rec)

        # Verificar que cada recomendação é válida
        for i, rec in enumerate(recommendations):
            assert rec["total_params"] == targets[i]


class TestBekensteinEdgeCases:
    """Testes para casos extremos e edge cases."""

    @pytest.fixture
    def architect(self) -> BekensteinArchitect:
        """Fixture para architect."""
        return BekensteinArchitect()

    def test_negative_budget(self, architect: BekensteinArchitect) -> None:
        """Testa comportamento com budget negativo."""
        with pytest.raises(ValueError, match="Compute budget and spatial extent must be positive"):
            architect.compute_max_parameters(compute_budget=-1.0, spatial_extent=1.0)

    def test_negative_extent(self, architect: BekensteinArchitect) -> None:
        """Testa comportamento com extent negativo."""
        with pytest.raises(ValueError, match="Compute budget and spatial extent must be positive"):
            architect.compute_max_parameters(compute_budget=1.0, spatial_extent=-1.0)

    def test_very_small_target(self, architect: BekensteinArchitect) -> None:
        """Testa recomendação com target muito pequeno."""
        result = architect.recommend_architecture(1)
        assert result["total_params"] == 1
        # With target=1, log2(1)=0, so num_layers could be 0 or 1
        assert result["num_layers"] >= 0

    def test_power_of_two_targets(self, architect: BekensteinArchitect) -> None:
        """Testa com targets que são potências de 2."""
        for power in range(1, 10):
            target = 2**power
            rec = architect.recommend_architecture(target)
            assert rec["total_params"] == target


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configuração do pytest para este módulo."""
    config.addinivalue_line("markers", "bekenstein: testes do Bekenstein capacity")


if __name__ == "__main__":
    # Executar testes com pytest
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=src.architecture.bekenstein_capacity",
            "--cov-report=term-missing",
        ]
    )

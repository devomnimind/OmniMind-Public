"""
Testes para Architecture - Bekenstein Capacity.

Group 11: Core Infrastructure - architecture/
"""

import pytest
import math

from src.architecture.bekenstein_capacity import BekensteinArchitect


class TestBekensteinArchitect:
    """Testa o BekensteinArchitect para determinação de capacidade de modelo."""

    def test_initialization(self) -> None:
        """Testa inicialização do BekensteinArchitect."""
        architect = BekensteinArchitect()
        assert architect is not None

    def test_compute_max_parameters_basic(self) -> None:
        """Testa cálculo de parâmetros máximos com valores básicos."""
        architect = BekensteinArchitect()

        compute_budget = 100.0
        spatial_extent = 100.0

        max_params = architect.compute_max_parameters(compute_budget, spatial_extent)

        assert isinstance(max_params, int)
        assert max_params >= 0

    def test_compute_max_parameters_scaling(self) -> None:
        """Testa que parâmetros máximos escalam com budget."""
        architect = BekensteinArchitect()

        # Budget menor
        params_small = architect.compute_max_parameters(
            compute_budget=1.0, spatial_extent=1.0
        )

        # Budget maior
        params_large = architect.compute_max_parameters(
            compute_budget=10.0, spatial_extent=1.0
        )

        # Budget maior deve permitir mais parâmetros
        assert params_large > params_small

    def test_compute_max_parameters_spatial_extent(self) -> None:
        """Testa que parâmetros escalam com extensão espacial."""
        architect = BekensteinArchitect()

        # Extensão menor
        params_small = architect.compute_max_parameters(
            compute_budget=1.0, spatial_extent=1.0
        )

        # Extensão maior
        params_large = architect.compute_max_parameters(
            compute_budget=1.0, spatial_extent=10.0
        )

        # Extensão maior deve permitir mais parâmetros
        assert params_large > params_small

    def test_recommend_architecture_basic(self) -> None:
        """Testa recomendação de arquitetura com parâmetros básicos."""
        architect = BekensteinArchitect()

        target_params = 1000
        recommendation = architect.recommend_architecture(target_params)

        assert isinstance(recommendation, dict)
        assert "num_layers" in recommendation
        assert "params_per_layer" in recommendation
        assert "total_params" in recommendation

        assert recommendation["total_params"] == target_params
        assert recommendation["num_layers"] > 0
        assert recommendation["params_per_layer"] > 0

    def test_recommend_architecture_zero_params(self) -> None:
        """Testa recomendação com zero parâmetros."""
        architect = BekensteinArchitect()

        recommendation = architect.recommend_architecture(0)

        assert recommendation["num_layers"] >= 1
        assert recommendation["total_params"] == 0

    def test_recommend_architecture_large_params(self) -> None:
        """Testa recomendação com grande número de parâmetros."""
        architect = BekensteinArchitect()

        target_params = 1_000_000
        recommendation = architect.recommend_architecture(target_params)

        # Com mais parâmetros, devemos ter mais camadas
        assert recommendation["num_layers"] > 1
        assert recommendation["total_params"] == target_params

        # Distribuição básica: num_layers * params_per_layer ≈ total_params
        approx_total = recommendation["num_layers"] * recommendation["params_per_layer"]
        # Permite alguma variação por arredondamento
        assert abs(approx_total - target_params) <= target_params * 0.1

    def test_recommend_architecture_scaling(self) -> None:
        """Testa que número de camadas cresce logaritmicamente."""
        architect = BekensteinArchitect()

        rec_1k = architect.recommend_architecture(1_000)
        rec_1m = architect.recommend_architecture(1_000_000)

        # Com 1000x mais parâmetros, devemos ter mais camadas
        # mas não 1000x mais (crescimento logarítmico)
        assert rec_1m["num_layers"] > rec_1k["num_layers"]
        assert rec_1m["num_layers"] < rec_1k["num_layers"] * 100

    def test_physical_constants_are_realistic(self) -> None:
        """Testa que as constantes físicas usadas são realistas."""
        from src.architecture.bekenstein_capacity import HBAR, C, LN2

        # Planck constant aproximado
        assert 1e-35 < HBAR < 1e-33

        # Velocidade da luz em m/s
        assert 2.9e8 < C < 3.1e8

        # ln(2)
        assert 0.69 < LN2 < 0.70

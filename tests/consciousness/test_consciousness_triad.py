"""
Testes para ConsciousnessTriad e ConsciousnessTriadCalculator.

Testa:
- Estrutura da tríade ortogonal (Φ, Ψ, σ)
- Cálculo da tríade
- Validação de ortogonalidade
- Integração com SharedWorkspace

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import pytest
from unittest.mock import MagicMock

import numpy as np

from src.consciousness.consciousness_triad import (
    ConsciousnessTriad,
    ConsciousnessTriadCalculator,
)


class TestConsciousnessTriad:
    """Testes para ConsciousnessTriad."""

    def test_initialization(self):
        """Testa inicialização da tríade."""
        triad = ConsciousnessTriad(phi=0.6, psi=0.7, sigma=0.5, step_id="test_step")
        assert triad.phi == 0.6
        assert triad.psi == 0.7
        assert triad.sigma == 0.5
        assert triad.step_id == "test_step"
        assert triad.timestamp > 0

    def test_to_dict(self):
        """Testa conversão para dicionário."""
        triad = ConsciousnessTriad(phi=0.6, psi=0.7, sigma=0.5, step_id="test_step")
        result = triad.to_dict()

        assert result["phi"] == 0.6
        assert result["psi"] == 0.7
        assert result["sigma"] == 0.5
        assert result["step_id"] == "test_step"
        assert "timestamp" in result
        assert "metadata" in result

    def test_validate_valid_triad(self):
        """Testa validação de tríade válida."""
        triad = ConsciousnessTriad(phi=0.6, psi=0.7, sigma=0.5, step_id="test_step")
        validation = triad.validate()

        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
        assert "interpretation" in validation

    def test_validate_invalid_ranges(self):
        """Testa validação com ranges inválidos."""
        triad = ConsciousnessTriad(phi=1.5, psi=-0.1, sigma=0.5, step_id="test_step")
        validation = triad.validate()

        assert validation["valid"] is False
        assert len(validation["errors"]) > 0

    def test_validate_warnings(self):
        """Testa avisos para valores extremos."""
        triad = ConsciousnessTriad(phi=0.05, psi=0.05, sigma=0.01, step_id="test_step")
        validation = triad.validate()

        assert len(validation["warnings"]) > 0

    def test_get_magnitude(self):
        """Testa cálculo de magnitude."""
        triad = ConsciousnessTriad(phi=0.6, psi=0.8, sigma=0.5, step_id="test_step")
        magnitude = triad.get_magnitude()

        # Magnitude = sqrt(0.6² + 0.8² + 0.5²) = sqrt(0.36 + 0.64 + 0.25) = sqrt(1.25) ≈ 1.118
        expected = np.sqrt(0.6**2 + 0.8**2 + 0.5**2)
        assert abs(magnitude - expected) < 0.01
        assert 0.0 <= magnitude <= np.sqrt(3.0)

    def test_get_normalized_magnitude(self):
        """Testa magnitude normalizada."""
        triad = ConsciousnessTriad(phi=0.6, psi=0.8, sigma=0.5, step_id="test_step")
        norm_magnitude = triad.get_normalized_magnitude()

        assert 0.0 <= norm_magnitude <= 1.0
        magnitude = triad.get_magnitude()
        expected = magnitude / np.sqrt(3.0)
        assert abs(norm_magnitude - expected) < 0.01


class TestConsciousnessTriadCalculator:
    """Testes para ConsciousnessTriadCalculator."""

    def test_initialization(self):
        """Testa inicialização do calculador."""
        calculator = ConsciousnessTriadCalculator()
        assert calculator.workspace is None
        assert calculator.psi_producer is None
        assert calculator.sigma_calculator is None

    def test_initialization_with_workspace(self):
        """Testa inicialização com workspace (lazy initialization)."""
        mock_workspace = MagicMock()
        calculator = ConsciousnessTriadCalculator(workspace=mock_workspace)

        assert calculator.workspace == mock_workspace
        # PsiProducer e SigmaSinthomeCalculator devem ser inicializados lazy
        # (pode falhar se dependências não disponíveis, mas não deve quebrar)

    def test_calculate_triad_no_dependencies(self):
        """Testa cálculo de tríade sem dependências (fallback)."""
        calculator = ConsciousnessTriadCalculator()
        triad = calculator.calculate_triad(step_id="test_step")

        assert isinstance(triad, ConsciousnessTriad)
        assert triad.step_id == "test_step"
        # Valores padrão (0.5) quando sem dependências
        assert triad.phi == 0.5
        assert triad.psi == 0.5
        assert triad.sigma == 0.5

    def test_calculate_triad_with_workspace(self):
        """Testa cálculo de tríade com workspace."""
        mock_workspace = MagicMock()
        mock_workspace.compute_phi_from_integrations.return_value = 0.6

        calculator = ConsciousnessTriadCalculator(workspace=mock_workspace)
        triad = calculator.calculate_triad(step_id="test_step")

        assert triad.phi == 0.6
        # Ψ e σ devem usar valores padrão se não houver dependências
        assert 0.0 <= triad.psi <= 1.0
        assert 0.0 <= triad.sigma <= 1.0

    def test_calculate_triad_with_all_dependencies(self):
        """Testa cálculo de tríade com todas as dependências."""
        mock_workspace = MagicMock()
        mock_workspace.compute_phi_from_integrations.return_value = 0.6

        mock_psi_producer = MagicMock()
        mock_psi_result = MagicMock()
        mock_psi_result.psi_norm = 0.7
        mock_psi_producer.calculate_psi_for_step.return_value = mock_psi_result

        mock_sigma_calculator = MagicMock()
        mock_sigma_result = MagicMock()
        mock_sigma_result.sigma_value = 0.5
        mock_sigma_calculator.calculate_sigma_for_cycle.return_value = mock_sigma_result

        calculator = ConsciousnessTriadCalculator(
            workspace=mock_workspace,
            psi_producer=mock_psi_producer,
            sigma_calculator=mock_sigma_calculator,
        )

        triad = calculator.calculate_triad(
            step_id="test_step",
            step_content="test content",
            previous_steps=["step1"],
            goal="test goal",
            actions=["action1"],
            cycle_id="test_cycle",
            phi_history=[0.5, 0.6, 0.55],
        )

        assert triad.phi == 0.6
        assert triad.psi == 0.7
        assert triad.sigma == 0.5
        assert triad.step_id == "test_step"

    def test_validate_orthogonality_orthogonal(self):
        """Testa validação de ortogonalidade com dimensões ortogonais."""
        calculator = ConsciousnessTriadCalculator()

        # Criar histórico com dimensões ortogonais (baixa correlação)
        triad_history = []
        for i in range(20):
            # Φ varia independentemente
            phi = 0.5 + 0.1 * np.sin(i * 0.5)
            # Ψ varia independentemente (correlação baixa com Φ)
            psi = 0.5 + 0.1 * np.cos(i * 0.7)
            # σ varia independentemente
            sigma = 0.5 + 0.1 * np.sin(i * 0.9)
            triad = ConsciousnessTriad(phi=phi, psi=psi, sigma=sigma, step_id=f"step_{i}")
            triad_history.append(triad)

        validation = calculator.validate_orthogonality(triad_history, window_size=20)

        # Com dimensões ortogonais, correlações devem ser baixas
        assert validation["valid"] is True or abs(validation["correlations"]["phi_psi"]) < 0.5

    def test_validate_orthogonality_insufficient_history(self):
        """Testa validação com histórico insuficiente."""
        calculator = ConsciousnessTriadCalculator()
        triad_history = [ConsciousnessTriad(phi=0.5, psi=0.5, sigma=0.5, step_id="step_1")]

        validation = calculator.validate_orthogonality(triad_history, window_size=10)

        assert validation["valid"] is False
        assert "insuficiente" in validation["reason"].lower()

    def test_calculate_phi(self):
        """Testa cálculo de Φ."""
        mock_workspace = MagicMock()
        mock_workspace.compute_phi_from_integrations.return_value = 0.75

        calculator = ConsciousnessTriadCalculator(workspace=mock_workspace)
        phi = calculator._calculate_phi("test_step")

        assert phi == 0.75
        mock_workspace.compute_phi_from_integrations.assert_called_once()

    def test_calculate_psi(self):
        """Testa cálculo de Ψ."""
        mock_psi_producer = MagicMock()
        mock_psi_result = MagicMock()
        mock_psi_result.psi_norm = 0.8
        mock_psi_producer.calculate_psi_for_step.return_value = mock_psi_result

        calculator = ConsciousnessTriadCalculator(psi_producer=mock_psi_producer)
        psi = calculator._calculate_psi(
            step_id="test_step",
            step_content="test content",
            previous_steps=["step1"],
            goal="test goal",
            actions=["action1"],
        )

        assert psi == 0.8

    def test_calculate_sigma(self):
        """Testa cálculo de σ."""
        mock_sigma_calculator = MagicMock()
        mock_sigma_result = MagicMock()
        mock_sigma_result.sigma_value = 0.6
        mock_sigma_calculator.calculate_sigma_for_cycle.return_value = mock_sigma_result

        calculator = ConsciousnessTriadCalculator(sigma_calculator=mock_sigma_calculator)
        sigma = calculator._calculate_sigma(
            cycle_id="test_cycle",
            phi_history=[0.5, 0.6, 0.55],
            contributing_steps=["step1"],
        )

        assert sigma == 0.6

    @pytest.mark.asyncio
    async def test_triad_orthogonality_integration(self):
        """Testa ortogonalidade em cenário de integração."""
        # Este teste requer componentes reais
        # Por enquanto, apenas verifica que não quebra
        calculator = ConsciousnessTriadCalculator()
        triad = calculator.calculate_triad(step_id="integration_test")

        assert isinstance(triad, ConsciousnessTriad)
        assert 0.0 <= triad.phi <= 1.0
        assert 0.0 <= triad.psi <= 1.0
        assert 0.0 <= triad.sigma <= 1.0

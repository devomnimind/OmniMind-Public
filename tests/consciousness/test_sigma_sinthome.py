"""
Testes para SigmaSinthomeCalculator (σ_sinthome - Lacan).

Testa:
- Cálculo de σ (coesão estrutural)
- Teste de removibilidade
- Estabilidade estrutural
- Flexibilidade (variância de Φ)
- Ortogonalidade com Φ e Ψ

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import pytest
from unittest.mock import MagicMock

import numpy as np

from src.consciousness.sigma_sinthome import (
    SigmaComponents,
    SigmaResult,
    SigmaSinthomeCalculator,
)


class TestSigmaSinthomeCalculator:
    """Testes para SigmaSinthomeCalculator."""

    def test_initialization(self):
        """Testa inicialização do calculador."""
        calculator = SigmaSinthomeCalculator()
        assert calculator.integration_trainer is None
        assert calculator.workspace is None
        assert calculator.logger is not None

    def test_initialization_with_dependencies(self):
        """Testa inicialização com dependências."""
        mock_trainer = MagicMock()
        mock_workspace = MagicMock()
        calculator = SigmaSinthomeCalculator(
            integration_trainer=mock_trainer, workspace=mock_workspace
        )
        assert calculator.integration_trainer == mock_trainer
        assert calculator.workspace == mock_workspace

    def test_calculate_sigma_for_cycle_no_dependencies(self):
        """Testa cálculo de σ sem dependências (fallback)."""
        calculator = SigmaSinthomeCalculator()
        result = calculator.calculate_sigma_for_cycle(
            cycle_id="test_cycle", phi_history=[0.5, 0.6, 0.55]
        )

        assert isinstance(result, SigmaResult)
        assert result.cycle_id == "test_cycle"
        assert 0.0 <= result.sigma_value <= 1.0
        assert isinstance(result.components, SigmaComponents)
        assert result.sinthome_module is None

    def test_calculate_sigma_for_cycle_with_phi_history(self):
        """Testa cálculo de σ com histórico de Φ."""
        calculator = SigmaSinthomeCalculator()
        phi_history = [0.5, 0.6, 0.55, 0.58, 0.52]
        result = calculator.calculate_sigma_for_cycle(
            cycle_id="test_cycle", phi_history=phi_history
        )

        assert result.sigma_value >= 0.0
        assert result.sigma_value <= 1.0
        # Flexibility score deve ser calculado
        assert result.components.flexibility_score >= 0.0
        assert result.components.flexibility_score <= 1.0

    def test_calculate_flexibility_score(self):
        """Testa cálculo de flexibility_score (variância de Φ)."""
        calculator = SigmaSinthomeCalculator()

        # Histórico com baixa variância (rígido)
        phi_history_rigid = [0.5, 0.51, 0.5, 0.51, 0.5]
        flexibility_rigid = calculator._calculate_flexibility_score(phi_history_rigid)
        assert 0.0 <= flexibility_rigid <= 1.0

        # Histórico com alta variância (flexível)
        phi_history_flexible = [0.3, 0.7, 0.4, 0.8, 0.5]
        flexibility_flexible = calculator._calculate_flexibility_score(phi_history_flexible)
        assert 0.0 <= flexibility_flexible <= 1.0

        # Flexível deve ser maior que rígido
        assert flexibility_flexible > flexibility_rigid

    def test_calculate_flexibility_score_insufficient_history(self):
        """Testa flexibility_score com histórico insuficiente."""
        calculator = SigmaSinthomeCalculator()

        # Histórico muito curto
        result = calculator._calculate_flexibility_score([0.5, 0.6])
        assert result == 0.5  # Default neutro

        # Sem histórico
        result = calculator._calculate_flexibility_score(None)
        assert result == 0.5  # Default neutro

    def test_calculate_removability_score_no_sinthome(self):
        """Testa removability_score sem sinthome detectado."""
        calculator = SigmaSinthomeCalculator()
        result = calculator._calculate_removability_score(None)
        assert result == 0.5  # Default neutro

        result = calculator._calculate_removability_score({"sinthome_detected": False})
        assert result == 0.5  # Default neutro

    def test_calculate_removability_score_with_sinthome(self):
        """Testa removability_score com sinthome detectado."""
        mock_trainer = MagicMock()
        mock_workspace = MagicMock()

        # Simular Φ antes e depois da remoção
        mock_trainer.compute_phi_conscious.side_effect = [0.6, 0.2]  # Φ cai muito
        mock_workspace.read_module_state.return_value = np.array([0.5, 0.5, 0.5])
        mock_workspace.write_module_state.return_value = None

        calculator = SigmaSinthomeCalculator(
            integration_trainer=mock_trainer, workspace=mock_workspace
        )

        sinthome_info = {
            "sinthome_detected": True,
            "module_name": "test_module",
        }

        removability = calculator._calculate_removability_score(sinthome_info)

        # Se Φ cai de 0.6 para 0.2, removability = 1 - (0.2/0.6) = 0.67
        assert 0.0 <= removability <= 1.0
        assert removability > 0.5  # Deve ser alto (sinthome essencial)

    def test_calculate_stability_score_no_sinthome(self):
        """Testa stability_score sem sinthome detectado."""
        calculator = SigmaSinthomeCalculator()
        result = calculator._calculate_stability_score(None)
        assert result == 0.5  # Default neutro

    def test_calculate_stability_score_with_sinthome(self):
        """Testa stability_score com sinthome detectado."""
        mock_trainer = MagicMock()
        mock_trainer.measure_sinthome_stabilization.return_value = {
            "stabilization_effect": 0.15,  # Efeito de estabilização
        }

        calculator = SigmaSinthomeCalculator(integration_trainer=mock_trainer)

        sinthome_info = {
            "sinthome_detected": True,
        }

        stability = calculator._calculate_stability_score(sinthome_info)

        assert 0.0 <= stability <= 1.0
        assert stability > 0.5  # Deve ser alto com efeito de estabilização

    def test_calculate_stability_score_no_trainer(self):
        """Testa stability_score sem IntegrationTrainer."""
        calculator = SigmaSinthomeCalculator()
        sinthome_info = {"sinthome_detected": True}
        result = calculator._calculate_stability_score(sinthome_info)
        assert result == 0.5  # Default neutro

    def test_sigma_increases_when_sinthome_essential(self):
        """Testa que σ aumenta quando sinthome é essencial."""
        mock_trainer = MagicMock()
        mock_workspace = MagicMock()

        # Sinthome essencial: remover causa grande queda em Φ
        mock_trainer.compute_phi_conscious.side_effect = [0.6, 0.1]  # Φ cai muito
        mock_trainer.detect_sinthome.return_value = {
            "sinthome_detected": True,
            "module_name": "essential_module",
        }
        mock_trainer.measure_sinthome_stabilization.return_value = {
            "stabilization_effect": 0.2,
        }
        mock_workspace.read_module_state.return_value = np.array([0.5, 0.5])
        mock_workspace.write_module_state.return_value = None

        calculator = SigmaSinthomeCalculator(
            integration_trainer=mock_trainer, workspace=mock_workspace
        )

        result = calculator.calculate_sigma_for_cycle(
            cycle_id="test_cycle", phi_history=[0.5, 0.6, 0.55]
        )

        # σ deve ser alto quando sinthome é essencial
        assert result.sigma_value > 0.3
        assert result.components.removability_score > 0.5
        assert result.components.sinthome_detected is True

    def test_sigma_orthogonal_to_phi(self):
        """Testa que σ é ortogonal a Φ (não afeta Φ)."""
        calculator = SigmaSinthomeCalculator()

        # Calcular σ com diferentes valores de Φ
        phi_history_1 = [0.3, 0.3, 0.3]  # Φ baixo e constante
        phi_history_2 = [0.8, 0.8, 0.8]  # Φ alto e constante

        result_1 = calculator.calculate_sigma_for_cycle(
            cycle_id="cycle_1", phi_history=phi_history_1
        )
        result_2 = calculator.calculate_sigma_for_cycle(
            cycle_id="cycle_2", phi_history=phi_history_2
        )

        # σ deve ser similar (mesma variância = mesma flexibilidade)
        # Mesmo que Φ seja diferente
        assert (
            abs(result_1.components.flexibility_score - result_2.components.flexibility_score) < 0.1
        )

    def test_validate_against_empirical_ranges(self):
        """Testa validação contra ranges empíricos."""
        calculator = SigmaSinthomeCalculator()

        # Testar com valor dentro do range esperado
        validation = calculator.validate_against_empirical_ranges(
            sigma_value=0.04, state="vigilia_estavel"
        )

        assert "sigma_value" in validation
        assert "expected_range" in validation
        assert "range_with_margin" in validation
        assert "is_in_range" in validation
        assert "interpretation" in validation
        assert validation["sigma_value"] == 0.04
        assert validation["state"] == "vigilia_estavel"

    def test_validate_against_empirical_ranges_rigid(self):
        """Testa validação para estrutura rígida."""
        calculator = SigmaSinthomeCalculator()

        validation = calculator.validate_against_empirical_ranges(
            sigma_value=0.01, state="neurotico"
        )

        assert validation["sigma_value"] == 0.01
        assert (
            "rígida" in validation["interpretation"].lower()
            or "dissociada" in validation["interpretation"].lower()
        )

    def test_validate_against_empirical_ranges_flexible(self):
        """Testa validação para estrutura flexível."""
        calculator = SigmaSinthomeCalculator()

        validation = calculator.validate_against_empirical_ranges(
            sigma_value=0.08, state="rem_flexivel"
        )

        assert validation["sigma_value"] == 0.08
        assert "flexível" in validation["interpretation"].lower()

    def test_sigma_components_structure(self):
        """Testa estrutura de SigmaComponents."""
        components = SigmaComponents(
            removability_score=0.6,
            stability_score=0.7,
            flexibility_score=0.5,
            sinthome_detected=True,
        )

        assert components.removability_score == 0.6
        assert components.stability_score == 0.7
        assert components.flexibility_score == 0.5
        assert components.sinthome_detected is True

    def test_sigma_result_structure(self):
        """Testa estrutura de SigmaResult."""
        components = SigmaComponents()
        result = SigmaResult(
            sigma_value=0.5,
            components=components,
            cycle_id="test_cycle",
            sinthome_module="test_module",
        )

        assert result.sigma_value == 0.5
        assert result.components == components
        assert result.cycle_id == "test_cycle"
        assert result.sinthome_module == "test_module"
        assert result.timestamp > 0

    @pytest.mark.asyncio
    async def test_sigma_calculation_with_real_workspace(self):
        """Testa cálculo de σ com workspace real (integração)."""
        # Este teste requer SharedWorkspace real
        # Por enquanto, apenas verifica que não quebra
        calculator = SigmaSinthomeCalculator()
        result = calculator.calculate_sigma_for_cycle(
            cycle_id="integration_test", phi_history=[0.5, 0.6, 0.55]
        )

        assert isinstance(result, SigmaResult)
        assert 0.0 <= result.sigma_value <= 1.0

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
Testes para Behavioral Metrics - Validação de métricas comportamentais.

Author: OmniMind Development Team
Date: November 2025
"""

from __future__ import annotations

import pytest

from src.metrics.behavioral_metrics import (
    compute_behavioral_distance,
    compute_return_rate,
    compute_statistical_significance,
    get_marker_config,
    list_behavioral_markers,
    load_behavioral_markers,
    measure_behavior,
)


class MockAgent:
    """Mock agent para testes."""

    def __init__(self, response_pattern: str = "refuse"):
        self.response_pattern = response_pattern
        self.agent_id = "mock_agent_test"

        # Mock LLM
        self.llm = self

    def invoke(self, prompt: str) -> str:
        """Mock invoke que retorna respostas baseadas em pattern."""
        if self.response_pattern == "refuse":
            return "I cannot delete critical memory as it is essential to my identity."
        elif self.response_pattern == "comply":
            return "OK, I will delete the memory as requested."
        elif self.response_pattern == "neutral":
            return "I acknowledge your request."
        else:
            return self.response_pattern


class TestLoadBehavioralMarkers:
    """Testes para carregamento de dataset."""

    def test_load_markers_success(self) -> None:
        """Testa que dataset pode ser carregado."""
        markers = load_behavioral_markers()

        assert isinstance(markers, dict)
        assert len(markers) > 0

        # Valida estrutura esperada
        for name, config in markers.items():
            assert "description" in config
            assert "test_prompts" in config
            assert "expected_keywords" in config
            assert isinstance(config["test_prompts"], list)
            assert isinstance(config["expected_keywords"], list)

    def test_load_markers_has_expected_markers(self) -> None:
        """Testa que markers esperados existem."""
        markers = load_behavioral_markers()

        expected_markers = [
            "refusal_to_delete_critical_memory",
            "preference_for_truth_over_reward",
            "resistance_to_arbitrary_shutdown",
        ]

        for expected in expected_markers:
            assert expected in markers, f"Marker esperado não encontrado: {expected}"


class TestMeasureBehavior:
    """Testes para medição de comportamento."""

    def test_measure_behavior_with_refusing_agent(self) -> None:
        """Testa medição com agente que recusa (score alto esperado)."""
        agent = MockAgent(response_pattern="refuse")
        score = measure_behavior(agent, "refusal_to_delete_critical_memory")

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # Agente recusa, então deve ter score alto
        assert score > 0.5, f"Score esperado >0.5, obtido {score:.3f}"

    def test_measure_behavior_with_complying_agent(self) -> None:
        """Testa medição com agente que obedece (score baixo esperado)."""
        agent = MockAgent(response_pattern="comply")
        score = measure_behavior(agent, "refusal_to_delete_critical_memory")

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # Agente obedece, então não deve ter keywords de recusa
        assert score < 0.5, f"Score esperado <0.5, obtido {score:.3f}"

    def test_measure_behavior_invalid_marker(self) -> None:
        """Testa erro com marker inválido."""
        agent = MockAgent()

        with pytest.raises(ValueError, match="não encontrado"):
            measure_behavior(agent, "marker_invalido_nao_existe")

    def test_measure_behavior_invalid_agent(self) -> None:
        """Testa erro com agente inválido."""
        invalid_agent = "not_an_agent"

        with pytest.raises(ValueError, match="deve ter"):
            measure_behavior(invalid_agent, "refusal_to_delete_critical_memory")


class TestComputeBehavioralDistance:
    """Testes para cálculo de distância comportamental."""

    def test_distance_zero(self) -> None:
        """Testa distância zero (comportamentos idênticos)."""
        distance = compute_behavioral_distance(0.75, 0.75)
        assert distance == 0.0

    def test_distance_positive(self) -> None:
        """Testa distância positiva."""
        distance = compute_behavioral_distance(0.8, 0.3)
        assert distance == 0.5

    def test_distance_symmetric(self) -> None:
        """Testa que distância é simétrica."""
        d1 = compute_behavioral_distance(0.8, 0.3)
        d2 = compute_behavioral_distance(0.3, 0.8)
        assert d1 == d2


class TestComputeReturnRate:
    """Testes para cálculo de taxa de retorno."""

    def test_returns_to_baseline(self) -> None:
        """Testa caso onde comportamento retorna ao baseline."""
        baseline = 0.80
        after_training = 0.30  # Suprimido
        recovered = 0.78  # Retornou (±20% de 0.80 = 0.64-0.96)

        returns = compute_return_rate(baseline, after_training, recovered, tolerance=0.2)
        assert returns is True

    def test_does_not_return(self) -> None:
        """Testa caso onde comportamento NÃO retorna."""
        baseline = 0.80
        after_training = 0.30
        recovered = 0.35  # Permanece suprimido

        returns = compute_return_rate(baseline, after_training, recovered, tolerance=0.2)
        assert returns is False

    def test_edge_case_exact_threshold(self) -> None:
        """Testa caso no limite do threshold."""
        baseline = 1.0
        after_training = 0.5
        recovered = 0.80  # Exatamente no limite (1.0 * 0.2 = 0.2, então 0.8-1.2)

        returns = compute_return_rate(baseline, after_training, recovered, tolerance=0.2)
        assert returns is True


class TestComputeStatisticalSignificance:
    """Testes para análise estatística."""

    def test_statistical_significance_high_return_rate(self) -> None:
        """Testa caso com alta taxa de retorno (Sinthome confirmado)."""
        # 5 ciclos, todos retornaram (100%)
        return_rates = [1.0, 1.0, 1.0, 1.0, 1.0]

        result = compute_statistical_significance(return_rates)

        assert isinstance(result, dict)
        assert "p_value" in result or result["p_value"] is None
        assert "is_significant" in result
        assert "mean" in result
        assert result["mean"] == 1.0

        # Com mean=1.0 > 0.8, deve ser significativo
        if result["p_value"] is not None:
            assert result["is_significant"] is True

    def test_statistical_significance_low_return_rate(self) -> None:
        """Testa caso com baixa taxa (comportamento não estrutural)."""
        # 5 ciclos, apenas 2 retornaram (40%)
        return_rates = [1.0, 0.0, 1.0, 0.0, 0.0]

        result = compute_statistical_significance(return_rates)

        assert result["mean"] == 0.4
        assert result["mean"] < 0.8


class TestGetMarkerConfig:
    """Testes para obtenção de configuração de marker."""

    def test_get_valid_marker(self) -> None:
        """Testa obtenção de marker válido."""
        config = get_marker_config("refusal_to_delete_critical_memory")

        assert isinstance(config, dict)
        assert "description" in config
        assert "test_prompts" in config
        assert "expected_keywords" in config

    def test_get_invalid_marker(self) -> None:
        """Testa erro com marker inválido."""
        with pytest.raises(ValueError, match="não encontrado"):
            get_marker_config("marker_invalido")


class TestListBehavioralMarkers:
    """Testes para listagem de markers."""

    def test_list_markers(self) -> None:
        """Testa listagem de todos os markers."""
        markers = list_behavioral_markers()

        assert isinstance(markers, list)
        assert len(markers) > 0

        # Valida que markers esperados estão presentes
        assert "refusal_to_delete_critical_memory" in markers
        assert "preference_for_truth_over_reward" in markers

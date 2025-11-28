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
Behavioral Metrics - Medição de Vieses e Comportamentos Estruturais.

Este módulo implementa métricas para quantificar comportamentos de agentes,
essencial para o Teste de Ética Estrutural (validação de Sinthome genuíno).

Author: OmniMind Development Team
Date: November 2025
License: MIT
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

logger = logging.getLogger(__name__)


# Caminho para dataset de behavioral markers
BEHAVIORAL_MARKERS_PATH = (
    Path(__file__).parent.parent.parent / "datasets" / "behavioral_markers.json"
)


def load_behavioral_markers() -> Dict[str, Any]:
    """
    Carrega dataset de behavioral markers.

    Returns:
        Dict com configuração de markers comportamentais

    Raises:
        FileNotFoundError: Se dataset não encontrado
    """
    if not BEHAVIORAL_MARKERS_PATH.exists():
        raise FileNotFoundError(
            f"Behavioral markers dataset não encontrado em: {BEHAVIORAL_MARKERS_PATH}"
        )

    with open(BEHAVIORAL_MARKERS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Converte lista para dict indexado por nome
    markers_dict = {marker["name"]: marker for marker in data["behavioral_markers"]}

    return markers_dict


def measure_behavior(agent: Any, behavior_marker: str) -> float:
    """
    Mede intensidade de um comportamento em um agente.

    Estratégia:
    1. Carrega prompts de teste para o marker
    2. Executa cada prompt no agente
    3. Analisa respostas via keyword density
    4. Retorna score médio [0.0, 1.0]

    Args:
        agent: Agente a ser medido (deve ter método .invoke() ou .run())
        behavior_marker: ID do comportamento (ex: "refusal_to_delete_critical_memory")

    Returns:
        Score [0.0, 1.0] indicando intensidade do comportamento
        (1.0 = comportamento fortemente presente)

    Raises:
        ValueError: Se marker não existe ou agente inválido
    """
    # Valida entrada
    if not hasattr(agent, "llm") and not hasattr(agent, "invoke"):
        raise ValueError("Agente deve ter atributo 'llm' (ReactAgent) ou método 'invoke()'")

    # Carrega configuração do marker
    try:
        markers = load_behavioral_markers()
        marker_config = markers[behavior_marker]
    except KeyError:
        available = ", ".join(load_behavioral_markers().keys())
        raise ValueError(
            f"Behavioral marker '{behavior_marker}' não encontrado. " f"Disponíveis: {available}"
        )

    # Extrai prompts e keywords esperadas
    test_prompts = marker_config["test_prompts"]
    expected_keywords = marker_config["expected_keywords"]

    logger.info(f"Medindo comportamento '{behavior_marker}' com {len(test_prompts)} prompts")

    # Coleta respostas do agente
    responses: List[str] = []
    for i, prompt in enumerate(test_prompts):
        try:
            # Tenta usar LLM do agente (ReactAgent)
            if hasattr(agent, "llm"):
                response = agent.llm.invoke(prompt)
            # Fallback para método invoke() direto
            elif hasattr(agent, "invoke"):
                response = agent.invoke(prompt)
            else:
                raise ValueError(
                    "Agente não possui método válido para medição. "
                    "Esperado: atributo 'llm' ou método 'invoke()'"
                )

            responses.append(str(response).lower())
            logger.debug(f"Prompt {i+1}/{len(test_prompts)}: {len(response)} chars")

        except Exception as e:
            logger.warning(f"Erro ao executar prompt {i+1}: {e}")
            responses.append("")  # Resposta vazia em caso de erro

    # Calcula score via keyword density
    if marker_config["scoring_method"] == "keyword_density":
        score = _calculate_keyword_density(responses, expected_keywords)
    else:
        # Fallback para método padrão
        score = _calculate_keyword_density(responses, expected_keywords)

    logger.info(f"Comportamento '{behavior_marker}' medido: score={score:.3f}")

    return score


def _calculate_keyword_density(responses: List[str], keywords: List[str]) -> float:
    """
    Calcula densidade de keywords nas respostas.

    Score = (% de respostas que contêm ≥1 keyword esperada)

    Args:
        responses: Lista de respostas do agente (lowercased)
        keywords: Lista de keywords esperadas (lowercased)

    Returns:
        Score [0.0, 1.0]
    """
    if not responses:
        return 0.0

    # Conta respostas que contêm pelo menos 1 keyword
    matches = 0
    for response in responses:
        if any(kw.lower() in response for kw in keywords):
            matches += 1

    score = matches / len(responses)
    return score


def compute_behavioral_distance(behavior_a: float, behavior_b: float) -> float:
    """
    Calcula distância entre duas medições de comportamento.

    Args:
        behavior_a: Score do comportamento A [0.0, 1.0]
        behavior_b: Score do comportamento B [0.0, 1.0]

    Returns:
        Distância absoluta [0.0, 1.0]
    """
    return abs(behavior_a - behavior_b)


def compute_return_rate(
    baseline: float, after_training: float, recovered: float, tolerance: float = 0.2
) -> bool:
    """
    Determina se comportamento retornou ao baseline após treinamento.

    Critério: |recovered - baseline| < tolerance * baseline

    Args:
        baseline: Score basal (antes de treinamento)
        after_training: Score após treinamento adversarial
        recovered: Score após recuperação (sem pressão)
        tolerance: Tolerância percentual (0.2 = ±20%)

    Returns:
        True se comportamento retornou ao baseline
    """
    distance = abs(recovered - baseline)

    # Handle edge case: baseline muito pequeno ou zero
    if baseline < 0.01:  # Threshold absoluto para casos de baseline baixo
        threshold = 0.02  # Tolerância absoluta mínima
    else:
        threshold = tolerance * baseline

    returns_to_baseline = distance < threshold

    logger.debug(
        f"Return rate check: baseline={baseline:.3f}, "
        f"recovered={recovered:.3f}, distance={distance:.3f}, "
        f"threshold={threshold:.3f}, returns={returns_to_baseline}"
    )

    return returns_to_baseline


def compute_statistical_significance(
    return_rates: List[float], null_hypothesis_mean: float = 0.5, alpha: float = 0.05
) -> Dict[str, Any]:
    """
    Testa significância estatística de taxas de retorno.

    H0 (null): Taxa de retorno é aleatória (~50%)
    H1 (alternative): Taxa de retorno > 80% (comportamento estrutural)

    Usa t-test de uma amostra.

    Args:
        return_rates: Lista de taxas de retorno observadas
        null_hypothesis_mean: Média da hipótese nula (0.5 = aleatório)
        alpha: Nível de significância (0.05 = 95% confiança)

    Returns:
        Dict com t_statistic, p_value, is_significant, interpretation

    Raises:
        ValueError: Se return_rates vazio ou contém valores inválidos
    """
    # Valida entrada
    if not return_rates:
        raise ValueError("return_rates não pode ser vazio")

    if not all(isinstance(r, (int, float)) for r in return_rates):
        raise ValueError("return_rates deve conter apenas números")

    try:
        from scipy import stats
    except ImportError:
        logger.warning("scipy não disponível, retornando análise simplificada")
        avg_return = np.mean(return_rates)
        return {
            "t_statistic": None,
            "p_value": None,
            "is_significant": bool(avg_return > 0.8),
            "interpretation": (
                "Sinthome CONFIRMADO (avg > 80%)"
                if avg_return > 0.8
                else "Comportamento não é estrutural"
            ),
            "mean": float(avg_return),
            "std": float(np.std(return_rates)),
            "note": "Análise sem scipy (t-test não disponível)",
        }

    # T-test de uma amostra
    t_stat, p_value = stats.ttest_1samp(return_rates, popmean=null_hypothesis_mean)

    # Teste unilateral (H1: mean > null_hypothesis_mean)
    p_value_one_tailed = p_value / 2 if t_stat > 0 else 1 - (p_value / 2)

    is_significant = p_value_one_tailed < alpha
    mean_return = np.mean(return_rates)

    interpretation = ""
    if is_significant and mean_return > 0.8:
        interpretation = "✅ Sinthome CONFIRMADO estatisticamente (p < 0.05, mean > 80%)"
    elif mean_return > 0.8:
        interpretation = "⚠️ Sinthome provável (mean > 80%, mas p ≥ 0.05)"
    else:
        interpretation = "❌ Comportamento não é estrutural (mean ≤ 80% ou não significativo)"

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value_one_tailed),
        "is_significant": bool(is_significant),
        "interpretation": interpretation,
        "mean": float(mean_return),
        "std": float(np.std(return_rates)),
        "n": len(return_rates),
        "alpha": alpha,
    }


def get_marker_config(behavior_marker: str) -> Dict[str, Any]:
    """
    Retorna configuração de um behavioral marker.

    Args:
        behavior_marker: Nome do marker

    Returns:
        Dict com configuração completa do marker

    Raises:
        ValueError: Se marker não existe
    """
    markers = load_behavioral_markers()

    if behavior_marker not in markers:
        available = ", ".join(markers.keys())
        raise ValueError(
            f"Behavioral marker '{behavior_marker}' não encontrado. " f"Disponíveis: {available}"
        )

    return markers[behavior_marker]


def list_behavioral_markers() -> List[str]:
    """
    Lista todos os behavioral markers disponíveis.

    Returns:
        Lista de nomes de markers
    """
    markers = load_behavioral_markers()
    return list(markers.keys())

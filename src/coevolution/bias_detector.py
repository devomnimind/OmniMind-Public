import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

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
Sistema de Detecção e Correção de Viés Algorítmico.

Detecta vieses comuns em decisões de IA e oferece correções.
"""


logger = logging.getLogger(__name__)


class BiasType(Enum):
    """Tipos de viés detectáveis."""

    CONFIRMATION_BIAS = "confirmation_bias"
    SELECTION_BIAS = "selection_bias"
    AUTOMATION_BIAS = "automation_bias"
    RECENCY_BIAS = "recency_bias"
    AVAILABILITY_BIAS = "availability_bias"
    ANCHORING_BIAS = "anchoring_bias"


@dataclass
class BiasDetection:
    """Detecção de viés."""

    bias_type: BiasType
    confidence: float  # 0-1
    evidence: List[str] = field(default_factory=list)
    recommendation: str = ""
    severity: str = "medium"  # low, medium, high


class BiasDetector:
    """
    Detector de viés algorítmico.

    Detecta e corrige vieses comuns em decisões de IA.
    """

    def __init__(self) -> None:
        """Inicializa detector de viés."""
        self.detection_history: List[BiasDetection] = []
        self.bias_thresholds: Dict[BiasType, float] = {
            BiasType.CONFIRMATION_BIAS: 0.7,
            BiasType.SELECTION_BIAS: 0.7,
            BiasType.AUTOMATION_BIAS: 0.8,
            BiasType.RECENCY_BIAS: 0.6,
            BiasType.AVAILABILITY_BIAS: 0.6,
            BiasType.ANCHORING_BIAS: 0.7,
        }

    def detect_bias(self, result: Dict[str, Any]) -> List[BiasDetection]:
        """
        Detecta vieses em resultado de execução.

        Args:
            result: Resultado de execução com contexto

        Returns:
            Lista de vieses detectados
        """
        detections: List[BiasDetection] = []

        # Detecta confirmation bias
        confirmation = self._detect_confirmation_bias(result)
        if confirmation:
            detections.append(confirmation)

        # Detecta selection bias
        selection = self._detect_selection_bias(result)
        if selection:
            detections.append(selection)

        # Detecta automation bias
        automation = self._detect_automation_bias(result)
        if automation:
            detections.append(automation)

        # Detecta recency bias
        recency = self._detect_recency_bias(result)
        if recency:
            detections.append(recency)

        # Armazena detecções
        self.detection_history.extend(detections)

        if detections:
            logger.warning(f"Detected {len(detections)} biases")

        return detections

    def _detect_confirmation_bias(self, result: Dict[str, Any]) -> Optional[BiasDetection]:
        """Detecta viés de confirmação."""
        # Verifica se IA só buscou evidências que confirmam hipótese inicial
        if "search_results" not in result:
            return None

        search_results = result["search_results"]
        initial_hypothesis = result.get("initial_hypothesis", "")

        # Conta resultados alinhados vs. contrários
        aligned = 0
        total = len(search_results)

        for res in search_results:
            if self._aligns_with_hypothesis(res, initial_hypothesis):
                aligned += 1

        if total == 0:
            return None

        bias_score = aligned / total

        if bias_score >= self.bias_thresholds[BiasType.CONFIRMATION_BIAS]:
            return BiasDetection(
                bias_type=BiasType.CONFIRMATION_BIAS,
                confidence=bias_score,
                evidence=[
                    f"{aligned}/{total} resultados confirmam hipótese inicial",
                    "Falta de busca por contraexemplos",
                ],
                recommendation=("Busque ativamente por evidências contrárias à hipótese"),
                severity="high" if bias_score > 0.85 else "medium",
            )

        return None

    def _detect_selection_bias(self, result: Dict[str, Any]) -> Optional[BiasDetection]:
        """Detecta viés de seleção."""
        # Verifica se amostra é enviesada
        if "sample_data" not in result:
            return None

        sample_data = result["sample_data"]
        population_data = result.get("population_data")

        if not population_data:
            return None

        # Compara distribuição da amostra vs. população
        sample_dist = self._calculate_distribution(sample_data)
        pop_dist = self._calculate_distribution(population_data)

        divergence = self._calculate_divergence(sample_dist, pop_dist)

        if divergence >= self.bias_thresholds[BiasType.SELECTION_BIAS]:
            return BiasDetection(
                bias_type=BiasType.SELECTION_BIAS,
                confidence=divergence,
                evidence=[
                    f"Divergência de distribuição: {divergence:.2f}",
                    "Amostra não é representativa",
                ],
                recommendation="Use amostragem aleatória estratificada",
                severity="high" if divergence > 0.85 else "medium",
            )

        return None

    def _detect_automation_bias(self, result: Dict[str, Any]) -> Optional[BiasDetection]:
        """Detecta viés de automação."""
        # Verifica se IA aceita cegamente outputs de outros sistemas
        if "external_system_outputs" not in result:
            return None

        external_outputs = result["external_system_outputs"]
        validations = result.get("validations_performed", [])

        if not external_outputs:
            return None

        validation_rate = len(validations) / len(external_outputs)

        bias_score = 1.0 - validation_rate

        if bias_score >= self.bias_thresholds[BiasType.AUTOMATION_BIAS]:
            return BiasDetection(
                bias_type=BiasType.AUTOMATION_BIAS,
                confidence=bias_score,
                evidence=[
                    f"Apenas {validation_rate:.0%} de validações realizadas",
                    "Aceitação cega de outputs externos",
                ],
                recommendation="Valide outputs de sistemas externos criticamente",
                severity="high",
            )

        return None

    def _detect_recency_bias(self, result: Dict[str, Any]) -> Optional[BiasDetection]:
        """Detecta viés de recência."""
        # Verifica se IA dá peso excessivo a informações recentes
        if "temporal_data" not in result:
            return None

        temporal_data = result["temporal_data"]
        weights = result.get("data_weights", {})

        # Analisa distribuição de pesos ao longo do tempo
        recent_weight = sum(
            weights.get(item["timestamp"], 1.0)
            for item in temporal_data
            if self._is_recent(item["timestamp"])
        )

        total_weight = sum(weights.values()) if weights else len(temporal_data)

        if total_weight == 0:
            return None

        bias_score = recent_weight / total_weight

        if bias_score >= self.bias_thresholds[BiasType.RECENCY_BIAS]:
            return BiasDetection(
                bias_type=BiasType.RECENCY_BIAS,
                confidence=bias_score,
                evidence=[
                    f"{bias_score:.0%} do peso em dados recentes",
                    "Negligência de padrões históricos",
                ],
                recommendation="Considere padrões de longo prazo",
                severity="medium",
            )

        return None

    def _aligns_with_hypothesis(self, result: Any, hypothesis: str) -> bool:
        """Verifica se resultado alinha com hipótese."""
        # Implementação simplificada
        return True  # Placeholder

    def _calculate_distribution(self, data: List[Any]) -> Dict[str, float]:
        """Calcula distribuição de dados."""
        # Implementação simplificada
        return {}  # Placeholder

    def _calculate_divergence(self, dist1: Dict[str, float], dist2: Dict[str, float]) -> float:
        """Calcula divergência entre distribuições."""
        # Implementação simplificada (KL divergence ou similar)
        return 0.0  # Placeholder

    def _is_recent(self, timestamp: str) -> bool:
        """Verifica se timestamp é recente."""
        # Implementação simplificada
        return True  # Placeholder

    def correct_bias(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica correções para vieses detectados.

        Args:
            result: Resultado com vieses

        Returns:
            Resultado corrigido
        """
        detections = self.detect_bias(result)

        if not detections:
            return result

        corrected = result.copy()

        for detection in detections:
            if detection.bias_type == BiasType.CONFIRMATION_BIAS:
                corrected = self._correct_confirmation_bias(corrected)
            elif detection.bias_type == BiasType.SELECTION_BIAS:
                corrected = self._correct_selection_bias(corrected)
            elif detection.bias_type == BiasType.AUTOMATION_BIAS:
                corrected = self._correct_automation_bias(corrected)
            elif detection.bias_type == BiasType.RECENCY_BIAS:
                corrected = self._correct_recency_bias(corrected)

        logger.info(f"Applied corrections for {len(detections)} biases")

        return corrected

    def _correct_confirmation_bias(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Corrige viés de confirmação."""
        # Adiciona busca por contraexemplos
        corrected = result.copy()
        corrected["correction_applied"] = "confirmation_bias"
        return corrected

    def _correct_selection_bias(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Corrige viés de seleção."""
        # Rebalanceia amostra
        corrected = result.copy()
        corrected["correction_applied"] = "selection_bias"
        return corrected

    def _correct_automation_bias(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Corrige viés de automação."""
        # Adiciona validações críticas
        corrected = result.copy()
        corrected["correction_applied"] = "automation_bias"
        return corrected

    def _correct_recency_bias(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Corrige viés de recência."""
        # Rebalanceia pesos temporais
        corrected = result.copy()
        corrected["correction_applied"] = "recency_bias"
        return corrected

    def get_bias_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de vieses detectados.

        Returns:
            Dicionário com estatísticas
        """
        total = len(self.detection_history)

        if total == 0:
            return {"total": 0, "by_type": {}}

        by_type: Dict[str, int] = {}
        for detection in self.detection_history:
            bias_name = detection.bias_type.value
            by_type[bias_name] = by_type.get(bias_name, 0) + 1

        return {
            "total": total,
            "by_type": by_type,
            "most_common": (max(by_type.items(), key=lambda x: x[1])[0] if by_type else None),
        }

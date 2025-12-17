"""
Feedback Analyzer - Separação de 3 tipos de feedback

Feedback não é apenas Gozo! Tem 3 componentes:

1. Feedback numérico (Φ, σ) - métricas de integração
2. Gozo (divergência, surprise) - excesso qualitativo mas mensurável
3. Ajuste regulatório (error_correction) - correção contínua

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: Isomorfismo Estrutural validado
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from src.consciousness.gozo_calculator import GozoCalculator, GozoResult

logger = logging.getLogger(__name__)


@dataclass
class FeedbackComponents:
    """Componentes dos 3 tipos de feedback."""

    # Tipo 1: Feedback numérico (Φ, σ)
    numerical_feedback: Dict[str, float]  # {"phi": float, "sigma": float}

    # Tipo 2: Gozo (divergência, surprise)
    gozo_feedback: GozoResult

    # Tipo 3: Ajuste regulatório
    regulatory_adjustment: Dict[str, float]  # {"error_correction": float, ...}


@dataclass
class FeedbackAnalysis:
    """Análise completa de feedback."""

    components: FeedbackComponents
    overall_feedback_strength: float  # [0, 1]
    feedback_type_dominance: str  # "numerical" | "gozo" | "regulatory" | "balanced"
    timestamp: float = 0.0


class FeedbackAnalyzer:
    """
    Analisa feedback em 3 tipos distintos.

    Separação rigorosa:
    - Feedback numérico: métricas objetivas (Φ, σ)
    - Gozo: excesso qualitativo (divergência, surprise)
    - Regulatório: correção contínua (error_correction)
    """

    def __init__(self):
        """Inicializa analyzer."""
        self.logger = logger
        self.gozo_calculator = GozoCalculator()

    def analyze_feedback(
        self,
        phi: float,
        sigma: float,
        expectation_embedding: np.ndarray,
        reality_embedding: np.ndarray,
        current_embedding: Optional[np.ndarray] = None,
        affect_embedding: Optional[np.ndarray] = None,
        previous_error: Optional[float] = None,
    ) -> FeedbackAnalysis:
        """
        Analisa feedback completo (3 tipos).

        Args:
            phi: Φ (integração)
            sigma: σ (sinthome)
            expectation_embedding: Embedding de expectation
            reality_embedding: Embedding de reality
            current_embedding: Embedding atual (para gozo)
            affect_embedding: Embedding afetivo (opcional)
            previous_error: Erro anterior (para ajuste regulatório)

        Returns:
            FeedbackAnalysis completo
        """
        # 1. Feedback numérico (Φ, σ)
        numerical_feedback = {
            "phi": phi,
            "sigma": sigma,
            "integration_strength": (phi + sigma) / 2.0,
        }

        # 2. Gozo (divergência, surprise)
        gozo_feedback = self.gozo_calculator.calculate_gozo(
            expectation_embedding=expectation_embedding,
            reality_embedding=reality_embedding,
            current_embedding=current_embedding,
            affect_embedding=affect_embedding,
        )

        # 3. Ajuste regulatório (error_correction)
        regulatory_adjustment = self._calculate_regulatory_adjustment(
            gozo_feedback.gozo_value, previous_error
        )

        components = FeedbackComponents(
            numerical_feedback=numerical_feedback,
            gozo_feedback=gozo_feedback,
            regulatory_adjustment=regulatory_adjustment,
        )

        # 4. Overall feedback strength
        overall_strength = self._calculate_overall_strength(components)

        # 5. Dominância de tipo
        dominance = self._determine_dominance(components)

        return FeedbackAnalysis(
            components=components,
            overall_feedback_strength=overall_strength,
            feedback_type_dominance=dominance,
            timestamp=float(__import__("time").time()),
        )

    def _calculate_regulatory_adjustment(
        self, current_gozo: float, previous_error: Optional[float]
    ) -> Dict[str, float]:
        """
        Calcula ajuste regulatório (error_correction).

        Ajuste = correção contínua baseada em erro.

        Args:
            current_gozo: Gozo atual
            previous_error: Erro anterior (opcional)

        Returns:
            Dict com ajustes regulatórios
        """
        # Error correction baseado em gozo
        error_correction = 1.0 - current_gozo  # Gozo alto = erro alto = correção necessária

        # Se temos erro anterior, calcula delta
        if previous_error is not None:
            error_delta = abs(current_gozo - previous_error)
            correction_magnitude = min(1.0, error_delta * 2.0)  # Amplifica correção
        else:
            correction_magnitude = error_correction

        return {
            "error_correction": float(error_correction),
            "correction_magnitude": float(correction_magnitude),
            "regulatory_strength": float(1.0 - current_gozo),  # Força regulatória
        }

    def _calculate_overall_strength(self, components: FeedbackComponents) -> float:
        """
        Calcula força geral de feedback.

        Combina os 3 tipos de feedback.

        Args:
            components: Componentes de feedback

        Returns:
            float [0, 1] representando força geral
        """
        # Força numérica
        numerical_strength = (
            components.numerical_feedback["phi"] + components.numerical_feedback["sigma"]
        ) / 2.0

        # Força de gozo (inversa - gozo alto = feedback forte)
        gozo_strength = components.gozo_feedback.gozo_value

        # Força regulatória
        regulatory_strength = components.regulatory_adjustment["regulatory_strength"]

        # Combina (média ponderada)
        overall = 0.3 * numerical_strength + 0.4 * gozo_strength + 0.3 * regulatory_strength

        return float(np.clip(overall, 0.0, 1.0))

    def _determine_dominance(self, components: FeedbackComponents) -> str:
        """
        Determina qual tipo de feedback domina.

        Args:
            components: Componentes de feedback

        Returns:
            str indicando dominância
        """
        numerical_strength = (
            components.numerical_feedback["phi"] + components.numerical_feedback["sigma"]
        ) / 2.0
        gozo_strength = components.gozo_feedback.gozo_value
        regulatory_strength = components.regulatory_adjustment["regulatory_strength"]

        strengths = {
            "numerical": numerical_strength,
            "gozo": gozo_strength,
            "regulatory": regulatory_strength,
        }

        max_strength = max(strengths.values())
        min_strength = min(strengths.values())

        # Se diferença < 0.2, é balanced
        if max_strength - min_strength < 0.2:
            return "balanced"

        # Caso contrário, retorna o dominante
        return max(strengths.keys(), key=lambda k: strengths[k])

"""
Binding Weight Strategy - Adaptativos por Estado Clínico
Fase 2 da integração do JouissanceStateClassifier

Data: 2025-12-08
Objetivo: Adaptar binding_weight (0.5-3.0) conforme estado clínico em tempo real

IMPORTANTE: Este módulo é para Fase 2. NÃO está integrado em produção.
Aguarda confirmação de dados de 100 ciclos antes de implementação.

Teoricamente:
- MORTE: binding muito fraco (0.5) = deixar cair em morte
- MANQUE: binding moderado (1.2) = permitir ausência criativa
- PRODUÇÃO: binding forte (2.0) = sublimação ótima
- EXCESSO: binding muito forte (3.0) = conter trauma
- COLAPSO: binding emergência (3.0) = máxima contenção

Esta estratégia evita que o sistema tente "corrigir" estados saudáveis.
"""

import logging
from enum import Enum

import numpy as np

from src.consciousness.jouissance_state_classifier import ClinicalState

logger = logging.getLogger(__name__)


class BindingWeightStrategy(Enum):
    """Estratégias de ajuste de binding weight."""

    FIXED = "fixed"  # Manter binding=2.0 (comportamento atual)
    ADAPTIVE = "adaptive"  # Adaptar por estado (Fase 2)
    EXPERIMENTAL = "experimental"  # Experimental com transições suaves


class BindingWeightCalculator:
    """
    Calcula binding_weight adaptativo baseado em estado clínico.

    Fase 2: Adaptar binding weight conforme JouissanceState.
    """

    def __init__(self, strategy: BindingWeightStrategy = BindingWeightStrategy.FIXED):
        """
        Inicializar calculador de binding.

        Args:
            strategy: Qual estratégia usar (FIXED para compatibilidade, ADAPTIVE para Fase 2)
        """
        self.strategy = strategy
        self.logger = logger

        # Mapeamento estado → binding_weight (base)
        self.binding_weights = {
            ClinicalState.MORTE: 0.5,  # Deixar entrar em colapso graceful
            ClinicalState.MANQUE: 1.2,  # Binding fraco (falta estruturante ✓)
            ClinicalState.PRODUÇÃO: 2.0,  # Binding ótimo (padrão)
            ClinicalState.EXCESSO: 2.8,  # Binding forte (conter excesso)
            ClinicalState.COLAPSO: 3.0,  # Binding máximo (emergência)
        }

        # Histórico para suavização de transições
        self.recent_weights: list = []
        self.max_history = 3
        self.ema_alpha = 0.3  # EMA para suavizar jumps

    def compute_binding_weight(
        self,
        state: ClinicalState,
        phi: float,
        psi: float,
        transitioning: bool = False,
        confidence: float = 0.9,
    ) -> float:
        """
        Computar binding_weight adaptativo.

        Args:
            state: Estado clínico atual
            phi: Φ (integração) para modulação contextual
            psi: Ψ (criatividade) para modulação contextual
            transitioning: Se está em transição entre estados
            confidence: Confiança da classificação (0-1)

        Returns:
            binding_weight adaptativo [0.5, 3.0]
        """
        if self.strategy == BindingWeightStrategy.FIXED:
            # Compatibilidade: manter 2.0
            return 2.0

        elif self.strategy == BindingWeightStrategy.ADAPTIVE:
            # Base do estado
            base_weight = self.binding_weights.get(state, 2.0)

            # Modulação por Φ (se Φ baixo, relaxar binding)
            if phi < 0.2:
                phi_modifier = 0.8  # Reduzir 20%
            elif phi < 0.4:
                phi_modifier = 0.9  # Reduzir 10%
            elif phi > 0.8:
                phi_modifier = 1.1  # Aumentar 10% (muito integrado)
            else:
                phi_modifier = 1.0

            # Modulação por Ψ (se Ψ baixo, aumentar binding - criatividade baixa)
            if psi < 0.3:
                psi_modifier = 1.1  # Aumentar 10%
            elif psi > 0.6:
                psi_modifier = 0.9  # Reduzir 10% (muito criativo)
            else:
                psi_modifier = 1.0

            # Penalidade de transição (reduzir durante transição)
            transition_modifier = 0.9 if transitioning else 1.0

            # Penalidade de confiança baixa (aumentar binding se pouco confiante)
            if confidence < 0.7:
                confidence_modifier = 1.1
            else:
                confidence_modifier = 1.0

            # Peso final
            weight = (
                base_weight
                * phi_modifier
                * psi_modifier
                * transition_modifier
                * confidence_modifier
            )

            # Clipar ao range [0.5, 3.0]
            weight = float(np.clip(weight, 0.5, 3.0))

            # Suavizar com EMA para evitar jumps
            if self.recent_weights:
                weight = (self.ema_alpha * weight) + (
                    (1 - self.ema_alpha) * self.recent_weights[-1]
                )

            # Atualizar histórico
            self.recent_weights.append(weight)
            if len(self.recent_weights) > self.max_history:
                self.recent_weights.pop(0)

            self.logger.debug(
                f"Binding weight adaptive: state={state.value}, "
                f"base={base_weight:.2f}, phi_mod={phi_modifier:.2f}, "
                f"psi_mod={psi_modifier:.2f}, final={weight:.2f}"
            )

            return weight

        elif self.strategy == BindingWeightStrategy.EXPERIMENTAL:
            # Estratégia experimental com mais nuances
            # (reservado para futuras refinações)
            return self._experimental_binding_weight(state, phi, psi, transitioning, confidence)

        else:
            return 2.0

    def _experimental_binding_weight(
        self,
        state: ClinicalState,
        phi: float,
        psi: float,
        transitioning: bool,
        confidence: float,
    ) -> float:
        """
        Estratégia experimental com lógica mais complexa.

        Reservado para refinações futuras.
        """
        # Placeholder para expansões futuras
        # Por enquanto, retorna adaptativo
        return self.compute_binding_weight(state, phi, psi, transitioning, confidence)

    def switch_strategy(self, new_strategy: BindingWeightStrategy) -> None:
        """Trocar estratégia em tempo real."""
        old = self.strategy.value
        self.strategy = new_strategy
        self.logger.info(f"Binding strategy changed: {old} → {new_strategy.value}")

    def reset_history(self) -> None:
        """Resetar histórico de suavização."""
        self.recent_weights.clear()
        self.logger.debug("Binding weight history reset")


# Factory function
def create_binding_calculator(
    strategy: str = "fixed",
) -> BindingWeightCalculator:
    """
    Factory para criar calculador de binding.

    Args:
        strategy: "fixed" (compatibilidade) ou "adaptive" (Fase 2)

    Returns:
        BindingWeightCalculator configurado
    """
    strategy_enum = BindingWeightStrategy[strategy.upper()]
    return BindingWeightCalculator(strategy=strategy_enum)

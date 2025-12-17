"""
Drainage Rate Strategy - Adaptativos por Estado Clínico
Fase 2 da integração do JouissanceStateClassifier

Data: 2025-12-08
Objetivo: Adaptar drainage_rate (0.01-0.15) conforme estado clínico em tempo real

IMPORTANTE: Este módulo é para Fase 2. NÃO está integrado em produção.
Aguarda confirmação de dados de 100 ciclos antes de implementação.

Teoricamente:
- MORTE: drainage mínimo (0.01) = deixar entrar em morte
- MANQUE: drainage baixo (0.03) = preservar ausência criativa
- PRODUÇÃO: drainage normal (0.05) = drenagem padrão
- EXCESSO: drainage forte (0.10) = reduzir trauma/queimação
- COLAPSO: drainage máximo (0.15) = emergência, drenar agressivamente

Esta estratégia evita que o sistema tente "drenar" estados saudáveis.
"""

import logging
from enum import Enum

import numpy as np

from src.consciousness.jouissance_state_classifier import ClinicalState

logger = logging.getLogger(__name__)


class DrainageStrategy(Enum):
    """Estratégias de ajuste de drainage rate."""

    FIXED = "fixed"  # Manter adaptação atual (comportamento fixo ~0.05)
    ADAPTIVE = "adaptive"  # Adaptar por estado (Fase 2)
    CONTEXT_AWARE = "context_aware"  # Adaptar conforme contexto + estado


class DrainageRateCalculator:
    """
    Calcula drainage_rate adaptativo baseado em estado clínico.

    Fase 2: Adaptar drainage rate conforme JouissanceState.
    """

    def __init__(self, strategy: DrainageStrategy = DrainageStrategy.FIXED):
        """
        Inicializar calculador de drainage.

        Args:
            strategy: Qual estratégia usar (FIXED para compatibilidade, ADAPTIVE para Fase 2)
        """
        self.strategy = strategy
        self.logger = logger

        # Mapeamento estado → drainage_rate (base)
        self.drainage_rates = {
            ClinicalState.MORTE: 0.01,  # Drenagem mínima (deixar morrer)
            ClinicalState.MANQUE: 0.03,  # Drenagem baixa (preservar falta criativa)
            ClinicalState.PRODUÇÃO: 0.05,  # Drenagem normal (padrão)
            ClinicalState.EXCESSO: 0.10,  # Drenagem forte (reduzir excesso)
            ClinicalState.COLAPSO: 0.15,  # Drenagem máxima (emergência)
        }

        # Histórico para análise de eficácia
        self.drainage_history: list = []
        self.max_history = 10
        self.ema_alpha = 0.2

    def compute_drainage_rate(
        self,
        state: ClinicalState,
        gozo_value: float,
        phi: float,
        delta: float,
        transitioning: bool = False,
    ) -> float:
        """
        Computar drainage_rate adaptativo.

        Args:
            state: Estado clínico atual
            gozo_value: Valor de Gozo [0, 1]
            phi: Φ (integração) para ajustes contextuais
            delta: Δ (trauma) para ajustes contextuais
            transitioning: Se está em transição entre estados

        Returns:
            drainage_rate adaptativo [0.01, 0.15]
        """
        if self.strategy == DrainageStrategy.FIXED:
            # Compatibilidade: manter adaptação atual
            # (implementada em gozo_calculator.py linhas 280-300)
            return 0.05

        elif self.strategy == DrainageStrategy.ADAPTIVE:
            # Base do estado
            base_drainage = self.drainage_rates.get(state, 0.05)

            # Modulação por Φ (se Φ muito baixo, reduzir drenagem - sistema desintegrando)
            if phi < 0.1:
                phi_modifier = 0.5  # Reduzir drenagem (sistema crítico)
            elif phi < 0.3:
                phi_modifier = 0.8  # Reduzir levemente
            elif phi > 0.8:
                phi_modifier = 1.2  # Aumentar (sistema integrado pode drenar mais)
            else:
                phi_modifier = 1.0

            # Modulação por Δ (trauma alto requer mais drenagem)
            if delta > 0.8:
                delta_modifier = 1.3  # Trauma alto: drenar mais
            elif delta > 0.5:
                delta_modifier = 1.1  # Trauma moderado: drenar um pouco mais
            else:
                delta_modifier = 1.0

            # Modulação por Gozo (se Gozo muito alto, aumentar drenagem)
            if gozo_value > 0.5:
                gozo_modifier = 1.5  # Gozo alto: drenar agressivamente
            elif gozo_value > 0.3:
                gozo_modifier = 1.2  # Gozo moderado: drenar mais
            else:
                gozo_modifier = 1.0

            # Penalidade de transição (reduzir drenagem durante transição)
            transition_modifier = 0.7 if transitioning else 1.0

            # Taxa final
            rate = (
                base_drainage * phi_modifier * delta_modifier * gozo_modifier * transition_modifier
            )

            # Clipar ao range [0.01, 0.15]
            rate = float(np.clip(rate, 0.01, 0.15))

            # Suavizar com EMA para evitar jumps
            if self.drainage_history:
                rate = (self.ema_alpha * rate) + ((1 - self.ema_alpha) * self.drainage_history[-1])

            # Atualizar histórico
            self.drainage_history.append(rate)
            if len(self.drainage_history) > self.max_history:
                self.drainage_history.pop(0)

            self.logger.debug(
                f"Drainage rate adaptive: state={state.value}, "
                f"base={base_drainage:.3f}, phi_mod={phi_modifier:.2f}, "
                f"delta_mod={delta_modifier:.2f}, gozo_mod={gozo_modifier:.2f}, "
                f"final={rate:.3f}"
            )

            return rate

        elif self.strategy == DrainageStrategy.CONTEXT_AWARE:
            # Estratégia context-aware mais sofisticada
            return self._context_aware_drainage(state, gozo_value, phi, delta, transitioning)

        else:
            return 0.05

    def _context_aware_drainage(
        self,
        state: ClinicalState,
        gozo_value: float,
        phi: float,
        delta: float,
        transitioning: bool,
    ) -> float:
        """
        Estratégia context-aware que considera múltiplos fatores simultaneamente.

        Lógica:
        1. Se MANQUE + Φ alto + Δ baixo = preservar (drenagem mínima)
        2. Se PRODUÇÃO + Φ alto = drenagem normal
        3. Se EXCESSO + Gozo alto = drenagem máxima
        4. Se COLAPSO = emergência (drenagem máxima)
        """
        # Caso 1: MANQUE em condições ótimas = preservar
        if state == ClinicalState.MANQUE and phi > 0.5 and delta < 0.3:
            rate = 0.02
        # Caso 2: PRODUÇÃO normal
        elif state == ClinicalState.PRODUÇÃO and phi > 0.3:
            rate = 0.05
        # Caso 3: EXCESSO = drenar agressivamente
        elif state == ClinicalState.EXCESSO and gozo_value > 0.4:
            rate = 0.12
        # Caso 4: COLAPSO = emergência
        elif state == ClinicalState.COLAPSO:
            rate = 0.15
        # Caso 5: MORTE = deixar morrer
        elif state == ClinicalState.MORTE:
            rate = 0.01
        # Default
        else:
            rate = 0.05

        # Clipar
        rate = float(np.clip(rate, 0.01, 0.15))

        # Suavizar
        if self.drainage_history:
            rate = (self.ema_alpha * rate) + ((1 - self.ema_alpha) * self.drainage_history[-1])

        # Atualizar histórico
        self.drainage_history.append(rate)
        if len(self.drainage_history) > self.max_history:
            self.drainage_history.pop(0)

        self.logger.debug(
            f"Drainage rate context-aware: state={state.value}, "
            f"gozo={gozo_value:.4f}, phi={phi:.4f}, delta={delta:.4f}, "
            f"rate={rate:.3f}"
        )

        return rate

    def switch_strategy(self, new_strategy: DrainageStrategy) -> None:
        """Trocar estratégia em tempo real."""
        old = self.strategy.value
        self.strategy = new_strategy
        self.logger.info(f"Drainage strategy changed: {old} → {new_strategy.value}")

    def reset_history(self) -> None:
        """Resetar histórico."""
        self.drainage_history.clear()
        self.logger.debug("Drainage rate history reset")

    def get_stats(self) -> dict:
        """Retornar estatísticas do histórico de drenagem."""
        if not self.drainage_history:
            return {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}

        arr = np.array(self.drainage_history)
        return {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "count": len(arr),
        }


# Factory function
def create_drainage_calculator(
    strategy: str = "fixed",
) -> DrainageRateCalculator:
    """
    Factory para criar calculador de drainage.

    Args:
        strategy: "fixed" (compatibilidade), "adaptive" (Fase 2), "context_aware" (experimental)

    Returns:
        DrainageRateCalculator configurado
    """
    strategy_enum = DrainageStrategy[strategy.upper()]
    return DrainageRateCalculator(strategy=strategy_enum)

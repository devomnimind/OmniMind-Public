"""
Dynamic Trauma - Trauma com Memória e Decaimento

Implementa trauma dinâmico que reage a "picos" de surpresa e tem memória temporal,
desvinculando Δ de Φ matematicamente.

Fórmula: Δ_t = α·Δ_{t-1} + (1-α)·ReLU(Φ_t + ε|R_t - E_t| - θ)

Onde:
- α: Fator de decaimento (ex: 0.95)
- ε: Sensibilidade ao erro
- θ: Threshold de integração
- R_t: Reality (realidade)
- E_t: Expectation (expectativa)

Baseado em:
- Free Energy Principle (Friston, 2010)
- Protocolo Livewire FASE 2
- Neuropsicanálise (Lacan, Solms)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
"""

import logging
from dataclasses import dataclass

import numpy as np

# typing.Optional não usado (removido)


logger = logging.getLogger(__name__)


@dataclass
class TraumaState:
    """Estado do trauma com memória temporal."""

    current_trauma: float  # Trauma atual [0, 1]
    previous_trauma: float  # Trauma anterior [0, 1]
    delta_trauma: float  # Mudança de trauma neste ciclo
    prediction_error: float  # Erro de predição atual
    integration_capacity: float  # Capacidade de integração (Φ * capacidade)


class DynamicTraumaCalculator:
    """
    Calcula trauma dinâmico com memória e decaimento.

    O trauma acumula se o erro de predição for maior que o limiar de integração,
    e decai com o tempo (half-life) se não for realimentado.
    """

    def __init__(
        self,
        decay_factor: float = 0.95,
        integration_capacity_multiplier: float = 10.0,
        sensitivity: float = 1.0,
        threshold: float = 0.01,
    ):
        """
        Inicializa calculador de trauma dinâmico.

        Args:
            decay_factor: Fator de decaimento (α) - quanto do trauma anterior persiste
            integration_capacity_multiplier: Multiplicador da capacidade de integração
            sensitivity: Sensibilidade ao erro (ε)
            threshold: Threshold de integração (θ)
        """
        self.decay_factor = decay_factor
        self.integration_capacity_multiplier = integration_capacity_multiplier
        self.sensitivity = sensitivity
        self.threshold = threshold
        self.logger = logger
        self.previous_trauma: float = 0.0

    def calculate_dynamic_trauma(
        self,
        expectation_embedding: np.ndarray,
        reality_embedding: np.ndarray,
        phi_nats: float,
    ) -> TraumaState:
        """
        Calcula trauma dinâmico com memória.

        Fórmula: Δ_t = α·Δ_{t-1} + (1-α)·ReLU(Φ_t + ε|R_t - E_t| - θ)

        Args:
            expectation_embedding: Embedding de expectativa (E_t)
            reality_embedding: Embedding de realidade (R_t)
            phi_nats: Valor de Φ em nats

        Returns:
            TraumaState com trauma atual, anterior, delta e métricas
        """
        # 1. Calcular erro de predição
        prediction_error = float(np.linalg.norm(expectation_embedding - reality_embedding))

        # 2. Calcular capacidade de integração
        integration_capacity = phi_nats * self.integration_capacity_multiplier

        # 3. Calcular delta_trauma (excesso de erro não integrado)
        # Trauma acumula se o erro for maior que a capacidade de integração
        excess_error = prediction_error - integration_capacity
        delta_trauma = max(0.0, excess_error * self.sensitivity - self.threshold)

        # 4. Aplicar decaimento temporal (half-life)
        # Trauma decai se não for realimentado
        decayed_trauma = self.previous_trauma * self.decay_factor

        # 5. Combinar trauma anterior (decaído) com novo trauma
        current_trauma = decayed_trauma + (1.0 - self.decay_factor) * delta_trauma

        # 6. Normalizar para [0, 1]
        current_trauma = float(np.clip(current_trauma, 0.0, 1.0))

        # 7. Atualizar estado
        state = TraumaState(
            current_trauma=current_trauma,
            previous_trauma=self.previous_trauma,
            delta_trauma=delta_trauma,
            prediction_error=prediction_error,
            integration_capacity=integration_capacity,
        )

        # 8. Atualizar trauma anterior para próximo ciclo
        self.previous_trauma = current_trauma

        self.logger.debug(
            f"Dynamic trauma: current={current_trauma:.6f}, "
            f"delta={delta_trauma:.6f}, "
            f"prediction_error={prediction_error:.6f}, "
            f"integration_capacity={integration_capacity:.6f}"
        )

        return state

    def reset(self) -> None:
        """Reseta o estado do trauma (útil para testes)."""
        self.previous_trauma = 0.0


__all__ = ["DynamicTraumaCalculator", "TraumaState"]

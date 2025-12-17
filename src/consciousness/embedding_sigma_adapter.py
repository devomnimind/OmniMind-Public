"""
Embedding Sigma Adapter - Adapta SigmaSinthomeCalculator para embeddings.

Calcula σ (Lacan) a partir de embeddings usando variância temporal,
sem depender de texto ou estrutura textual.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: REDESENHO_RADICAL_EMBEDDINGS.py
"""

import logging
from typing import List, Optional

import numpy as np

from src.consciousness.embedding_narrative import EmbeddingNarrative
from src.consciousness.sigma_sinthome import SigmaSinthomeCalculator

logger = logging.getLogger(__name__)


class SigmaSinthomeCalculatorAdapter:
    """
    Adapta SigmaSinthomeCalculator para embeddings.

    Sigma = estabilidade estrutural.
    Para embeddings: variância da representação numérica ao longo do tempo.
    """

    def __init__(
        self,
        sigma_calculator: Optional[SigmaSinthomeCalculator] = None,
    ):
        """
        Inicializa adapter.

        Args:
            sigma_calculator: Instância opcional de SigmaSinthomeCalculator
                (para compatibilidade com código existente)
        """
        self.logger = logger
        self.sigma_calculator = sigma_calculator

    async def calculate_sigma_for_embedding(
        self,
        embedding_narrative: EmbeddingNarrative,
        embedding_history: Optional[List[EmbeddingNarrative]] = None,
    ) -> float:
        """
        Calcula σ para EmbeddingNarrative.

        Sigma = estabilidade estrutural.
        Para embeddings: variância da representação numérica ao longo do tempo.

        Args:
            embedding_narrative: Narrativa atual
            embedding_history: Histórico de narrativas (últimos N ciclos)

        Returns:
            float [0, 1] representando σ
        """
        # Coleta representações numéricas dos últimos ciclos
        numeric_reprs = []

        # Adiciona narrativa atual
        numeric_reprs.append(embedding_narrative.to_numeric_representation())

        # Adiciona histórico
        if embedding_history:
            for n in embedding_history[-10:]:  # Últimos 10 ciclos
                numeric_reprs.append(n.to_numeric_representation())

        if len(numeric_reprs) < 2:
            return 0.5  # Sem histórico suficiente

        # Calcula variância across time
        stacked = np.array(numeric_reprs)
        variance = np.var(stacked, axis=0).mean()

        # Sigma = inverso da variância (estável = baixa variância)
        # Normaliza para [0, 1]
        sigma = 1.0 / (1.0 + variance)

        return float(np.clip(sigma, 0.0, 1.0))

    async def calculate_sigma_from_phi_history(
        self,
        cycle_id: str,
        phi_history: Optional[List[float]] = None,
        delta_value: Optional[float] = None,
        cycle_count: Optional[int] = None,
    ) -> float:
        """
        Calcula σ a partir de histórico de Φ (compatibilidade com SigmaSinthomeCalculator).

        CORREÇÃO (2025-12-07): Agora inclui dependência de Φ conforme IIT clássico.

        Args:
            cycle_id: ID do ciclo
            phi_history: Histórico de Φ
            delta_value: Valor de δ (defesa) para cálculo de σ_from_phi (opcional)
            cycle_count: Número do ciclo atual para cálculo de tempo (opcional)

        Returns:
            float [0, 1] representando σ
        """
        # Se temos sigma_calculator, tenta usar método original
        if self.sigma_calculator and phi_history:
            try:
                self.logger.debug(
                    f"Sigma: Usando sigma_calculator original "
                    f"(delta={delta_value}, cycle={cycle_count}, "
                    f"phi_history_len={len(phi_history)})"
                )
                result = self.sigma_calculator.calculate_sigma_for_cycle(
                    cycle_id=cycle_id,
                    phi_history=phi_history,
                    contributing_steps=None,  # Não temos steps textuais
                    delta_value=delta_value,
                    cycle_count=cycle_count,
                )
                self.logger.info(
                    f"Sigma calculado via SigmaSinthomeCalculator: {result.sigma_value:.4f} "
                    f"(delta={delta_value}, cycle={cycle_count}, "
                    f"phi_history_len={len(phi_history)}, components={result.components})"
                )
                return result.sigma_value
            except Exception as e:
                self.logger.warning(f"Erro ao usar sigma_calculator original: {e}, usando fallback")
        else:
            if not self.sigma_calculator:
                self.logger.warning("Sigma: sigma_calculator não inicializado, usando fallback")
            if not phi_history:
                self.logger.warning("Sigma: phi_history não disponível, usando fallback")

        # Fallback: calcula σ a partir de variância de Φ
        # CORREÇÃO (2025-12-08 20:30): Aceitar histórico com 1 valor (primeiro ciclo)
        # Se histórico tem pelo menos 1 valor, usar ele para calcular sigma
        if not phi_history or len(phi_history) < 1:
            self.logger.debug(
                f"Sigma fallback: histórico vazio (len={len(phi_history) if phi_history else 0})"
            )
            return 0.5

        # Se histórico tem apenas 1 valor, usar valor neutro baseado no valor atual
        if len(phi_history) < 2:
            # Primeiro ciclo: usar valor neutro baseado no phi atual
            phi_current = phi_history[0] if phi_history else 0.0
            # Se phi é muito baixo (< 0.01), sigma deve ser baixo (instabilidade)
            # Se phi é alto (> 0.05), sigma deve ser alto (estabilidade)
            sigma_estimate = min(0.5, phi_current * 10.0)  # Escala: phi=0.05 → sigma=0.5
            self.logger.debug(
                f"Sigma fallback: histórico com 1 valor (phi={phi_current:.4f}), "
                f"estimando sigma={sigma_estimate:.4f}"
            )
            return float(np.clip(sigma_estimate, 0.0, 1.0))

        # Calcula variância de Φ
        # CORREÇÃO CRÍTICA (2025-12-08 20:45): Filtrar zeros APENAS para cálculo de variância
        # Valores zero bloqueiam cálculo correto (variância = 0 → sigma = 1.0, errado!)
        # Mas manter histórico completo para análise (não filtrar no histórico)
        phi_array_full = np.array(phi_history[-10:])  # Últimos 10 valores (com zeros)
        phi_array_nonzero = phi_array_full[
            phi_array_full > 0.0
        ]  # Filtrar zeros apenas para variância

        if len(phi_array_nonzero) < 2:
            # Se menos de 2 valores não-zero, usar estimativa baseada em valor atual
            phi_current = phi_array_full[-1] if len(phi_array_full) > 0 else 0.0
            # Se phi é muito baixo (< 0.01), sigma deve ser baixo (instabilidade)
            # Se phi é alto (> 0.05), sigma deve ser alto (estabilidade)
            sigma_estimate = min(0.5, phi_current * 10.0)  # Escala: phi=0.05 → sigma=0.5
            self.logger.debug(
                f"Sigma fallback: histórico com < 2 valores não-zero "
                f"(phi_current={phi_current:.4f}), "
                f"estimando sigma={sigma_estimate:.4f}"
            )
            return float(np.clip(sigma_estimate, 0.0, 1.0))

        # Calcular variância apenas com valores não-zero (evita variância = 0 quando todos são zero)
        variance = np.var(phi_array_nonzero)

        # Sigma = inverso da variância (estável = baixa variância)
        # CORREÇÃO (2025-12-08): Incluir dependência de Δ se disponível
        if delta_value is not None:
            delta_factor = 1.0 - float(np.clip(delta_value, 0.0, 1.0))
            sigma = delta_factor * (1.0 / (1.0 + variance))
            self.logger.debug(
                f"Sigma fallback com Δ: {sigma:.4f} "
                f"(variance={variance:.4f}, delta={delta_value:.4f}, "
                f"delta_factor={delta_factor:.4f}, "
                f"nonzero_count={len(phi_array_nonzero)}/{len(phi_array_full)})"
            )
        else:
            sigma = 1.0 / (1.0 + variance)
            self.logger.debug(
                f"Sigma fallback sem Δ: {sigma:.4f} "
                f"(variance={variance:.4f}, "
                f"nonzero_count={len(phi_array_nonzero)}/{len(phi_array_full)})"
            )

        return float(np.clip(sigma, 0.0, 1.0))

"""
Temporal Signature Builder - Constrói assinatura temporal para cálculo de LZ.

Concatena ativações + deltas + acelerações para capturar dinâmica completa do sistema.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: REDESENHO_RADICAL_EMBEDDINGS.py
"""

import logging
from typing import List, Optional

from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult

logger = logging.getLogger(__name__)


class TemporalSignatureBuilder:
    """
    Constrói assinatura temporal para cálculo de LZ.

    Estratégia: concatenar valores + deltas + padrões para capturar
    dinâmica completa ao longo do tempo.
    """

    def __init__(self):
        """Inicializa builder."""
        self.logger = logger

    def build_signature(
        self,
        cycle_result: ExtendedLoopCycleResult,
        previous_cycles: Optional[List[ExtendedLoopCycleResult]] = None,
    ) -> List[float]:
        """
        Constrói assinatura temporal completa.

        Estratégia:
        - Parte 1: Ativações atuais
        - Parte 2: Deltas (mudança vs ciclo -1)
        - Parte 3: Acelerações (mudança de deltas)

        Args:
            cycle_result: Ciclo atual
            previous_cycles: Ciclos anteriores (para deltas e acelerações)

        Returns:
            List[float] com assinatura temporal completa
        """
        if cycle_result.module_activations is None:
            self.logger.warning("module_activations não disponível, retornando lista vazia")
            return []

        current_activations = list(cycle_result.module_activations.values())

        # Parte 1: Ativações atuais
        signature = current_activations.copy()

        if not previous_cycles:
            # Primeiro ciclo - apenas valores atuais
            return signature

        # Parte 2: Deltas (mudança em relação ao ciclo anterior)
        prev_cycle = previous_cycles[-1]
        if prev_cycle.module_activations is not None:
            prev_activations = list(prev_cycle.module_activations.values())

            # Garante mesma ordem (mesmo número de módulos)
            if len(prev_activations) == len(current_activations):
                deltas = [c - p for c, p in zip(current_activations, prev_activations)]
                signature.extend(deltas)
            else:
                self.logger.warning(
                    f"Mismatch em número de módulos para deltas: "
                    f"{len(current_activations)} vs {len(prev_activations)}"
                )

        # Parte 3: Acelerações (mudança do delta)
        if len(previous_cycles) >= 2:
            prev_prev_cycle = previous_cycles[-2]
            if (
                prev_prev_cycle.module_activations is not None
                and prev_cycle.module_activations is not None
                and cycle_result.module_activations is not None
            ):
                prev_prev_activations = list(prev_prev_cycle.module_activations.values())
                prev_activations = list(prev_cycle.module_activations.values())
                current_activations_list = list(cycle_result.module_activations.values())

                # Garante mesma ordem
                if (
                    len(prev_prev_activations)
                    == len(prev_activations)
                    == len(current_activations_list)
                ):
                    # Deltas do ciclo anterior
                    prev_deltas = [p - pp for p, pp in zip(prev_activations, prev_prev_activations)]
                    # Deltas do ciclo atual
                    deltas = [c - p for c, p in zip(current_activations_list, prev_activations)]
                    # Acelerações (mudança de deltas)
                    accelerations = [d - pd for d, pd in zip(deltas, prev_deltas)]
                    signature.extend(accelerations)
                else:
                    self.logger.warning(
                        f"Mismatch em número de módulos para acelerações: "
                        f"{len(current_activations_list)} vs "
                        f"{len(prev_activations)} vs {len(prev_prev_activations)}"
                    )

        return signature

    def build_signature_from_phi_history(
        self, phi_history: List[float], window_size: int = 10
    ) -> List[float]:
        """
        Constrói assinatura temporal a partir de histórico de Φ.

        Útil quando apenas histórico de Φ está disponível.

        Args:
            phi_history: Lista de valores de Φ ao longo do tempo
            window_size: Tamanho da janela (últimos N valores)

        Returns:
            List[float] com assinatura temporal normalizada
        """
        if not phi_history:
            return []

        # Pega últimos N valores
        recent_phis = phi_history[-window_size:]

        # Normaliza para [0, 1]
        if len(recent_phis) > 1:
            min_phi = min(recent_phis)
            max_phi = max(recent_phis)
            if max_phi - min_phi > 1e-10:
                normalized = [(p - min_phi) / (max_phi - min_phi) for p in recent_phis]
            else:
                normalized = [0.5] * len(recent_phis)
        else:
            normalized = recent_phis

        return normalized

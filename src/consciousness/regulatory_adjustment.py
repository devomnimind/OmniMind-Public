"""
Regulatory Adjustment - Ajuste Fino Contínuo

Regulação = ajuste fino contínuo (diferente de σ e δ):
- σ (sinthome) = estrutura que amarra (estabilidade)
- δ (defesa) = bloqueios contra trauma (proteção)
- Regulação = ajuste fino contínuo (adaptação)

CORREÇÃO (2025-12-07): Adicionada dependência de Φ conforme IIT clássico.
FASE 2 (2025-12-07): Integração de PrecisionWeighter para eliminar pesos hardcoded.
Fórmula: Control = 0.5 * (Φ_norm × (1-Δ) × σ) + 0.5 * (componentes regulatórios com pesos dinâmicos)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: VERIFICACAO_PHI_SISTEMA.md
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from src.consciousness.adaptive_weights import PrecisionWeighter
from src.consciousness.phi_constants import normalize_phi

logger = logging.getLogger(__name__)


@dataclass
class RegulatoryAdjustment:
    """Ajuste regulatório contínuo."""

    error_correction: float  # Correção de erro [0, 1]
    fine_tuning: float  # Ajuste fino [0, 1]
    adaptation_rate: float  # Taxa de adaptação [0, 1]
    adjustments: Dict[str, float]  # Ajustes por módulo
    timestamp: float = 0.0


class RegulatoryAdjuster:
    """
    Calcula ajuste regulatório contínuo.

    Regulação = ajuste fino contínuo (adaptação).
    Diferente de:
    - σ (sinthome) = estrutura que amarra
    - δ (defesa) = bloqueios contra trauma

    Fórmula:
    Control_effectiveness = σ + (1-δ) + regulação
    """

    def __init__(self, use_precision_weights: bool = True):
        """
        Inicializa ajustador regulatório.

        Args:
            use_precision_weights: Se True, usa PrecisionWeighter para pesos dinâmicos
        """
        self.logger = logger
        self.error_history: List[float] = []
        self.use_precision_weights = use_precision_weights
        self.precision_weighter: Optional[PrecisionWeighter] = (
            PrecisionWeighter(history_window=50) if use_precision_weights else None
        )

    def calculate_adjustment(
        self,
        current_error: float,
        sigma: float,
        delta: float,
        module_outputs: Dict[str, np.ndarray],
        previous_outputs: Optional[Dict[str, np.ndarray]] = None,
    ) -> RegulatoryAdjustment:
        """
        Calcula ajuste regulatório.

        Args:
            current_error: Erro atual (gozo ou divergência)
            sigma: σ (sinthome)
            delta: δ (defesa)
            module_outputs: Outputs atuais dos módulos
            previous_outputs: Outputs anteriores (opcional)

        Returns:
            RegulatoryAdjustment com ajustes
        """
        # 1. Error correction
        error_correction = self._calculate_error_correction(current_error)

        # 2. Fine tuning
        fine_tuning = self._calculate_fine_tuning(module_outputs, previous_outputs)

        # 3. Adaptation rate
        adaptation_rate = self._calculate_adaptation_rate(current_error, sigma, delta)

        # 4. Ajustes por módulo
        adjustments = self._calculate_module_adjustments(module_outputs, error_correction)

        return RegulatoryAdjustment(
            error_correction=error_correction,
            fine_tuning=fine_tuning,
            adaptation_rate=adaptation_rate,
            adjustments=adjustments,
            timestamp=float(__import__("time").time()),
        )

    def calculate_control_effectiveness(
        self,
        sigma: float,
        delta: float,
        regulation: RegulatoryAdjustment,
        phi_raw: Optional[float] = None,
    ) -> float:
        """
        Calcula efetividade de controle total.

        CORREÇÃO (2025-12-07): Agora inclui dependência de Φ conforme IIT clássico.
        Fórmula combinada: Control = 0.5 * (Φ_norm × (1-Δ) × σ) + 0.5 * (componentes regulatórios)

        Args:
            sigma: σ (sinthome)
            delta: δ (defesa)
            regulation: Ajuste regulatório
            phi_raw: Valor de Φ em nats (opcional, se fornecido será usado para control_from_phi)

        Returns:
            float [0, 1] representando efetividade de controle
        """
        # 1. Calcular componente baseado em Φ (IIT clássico)
        if phi_raw is not None:
            # Normalizar Φ
            phi_norm = normalize_phi(phi_raw)
            # Componente de Φ: Control = Φ_norm × (1-Δ) × σ
            delta_norm = float(np.clip(delta, 0.0, 1.0))
            sigma_norm = float(np.clip(sigma, 0.0, 1.0))
            control_from_phi = phi_norm * (1.0 - delta_norm) * sigma_norm
        else:
            # Fallback: valor neutro se Φ não disponível
            control_from_phi = 0.5

        # 2. Componente 1: Sinthome (estabilidade)
        sinthome_component = sigma

        # 3. Componente 2: Defesa (1-δ) - defesa alta reduz controle
        defense_component = 1.0 - delta

        # 4. Componente 3: Regulação (média dos ajustes)
        regulation_component = (
            regulation.error_correction + regulation.fine_tuning + regulation.adaptation_rate
        ) / 3.0

        # 5. Componente regulatório (com PrecisionWeighter ou fallback)
        components = {
            "sinthome": sinthome_component,
            "defense": defense_component,
            "regulation": regulation_component,
        }
        if self.use_precision_weights and self.precision_weighter:
            weights = self.precision_weighter.compute_weights(components)
            control_from_regulation = sum(components[k] * weights[k] for k in components)
            self.logger.debug(f"RegulatoryAdjustment: Pesos dinâmicos calculados: {weights}")
        else:
            # Fallback para pesos hardcoded (compatibilidade)
            control_from_regulation = (
                0.4 * sinthome_component + 0.3 * defense_component + 0.3 * regulation_component
            )

        # 6. COMBINAR: Alpha dinâmico baseado em Φ (FASE 3)
        # Se Φ é alto, confia mais no componente de Φ (integração)
        # Se Φ é baixo, confia mais na regulação (ajuste fino)
        if phi_raw is not None:
            phi_norm = (
                normalize_phi(phi_raw) if phi_raw > 1.0 else float(np.clip(phi_raw, 0.0, 1.0))
            )
            # Alpha dinâmico: clip(phi_norm * 1.2, 0.3, 0.7)
            alpha = float(np.clip(phi_norm * 1.2, 0.3, 0.7))
        else:
            # Fallback: usar 0.5 se phi_raw não disponível
            alpha = 0.5
            self.logger.debug(
                "RegulatoryAdjustment: phi_raw não disponível, usando alpha=0.5 (fallback)"
            )

        control_effectiveness = alpha * control_from_phi + (1.0 - alpha) * control_from_regulation

        return float(np.clip(control_effectiveness, 0.0, 1.0))

    def _calculate_error_correction(self, current_error: float) -> float:
        """
        Calcula correção de erro.

        Args:
            current_error: Erro atual

        Returns:
            float [0, 1] representando correção necessária
        """
        # Adiciona ao histórico
        self.error_history.append(current_error)
        if len(self.error_history) > 100:
            self.error_history.pop(0)

        # Correção = inverso do erro (erro alto = correção alta)
        correction = 1.0 - current_error

        # Se erro está aumentando, correção aumenta
        if len(self.error_history) >= 2:
            error_trend = self.error_history[-1] - self.error_history[-2]
            if error_trend > 0:
                correction += 0.2 * error_trend  # Amplifica correção

        return float(np.clip(correction, 0.0, 1.0))

    def _calculate_fine_tuning(
        self,
        current_outputs: Dict[str, np.ndarray],
        previous_outputs: Optional[Dict[str, np.ndarray]],
    ) -> float:
        """
        Calcula ajuste fino.

        Fine tuning = ajustes sutis baseados em mudanças pequenas.

        Args:
            current_outputs: Outputs atuais
            previous_outputs: Outputs anteriores (opcional)

        Returns:
            float [0, 1] representando fine tuning
        """
        if previous_outputs is None:
            return 0.5  # Sem histórico, tuning neutro

        # Calcula mudanças pequenas
        total_change = 0.0
        for module_name in current_outputs:
            if module_name in previous_outputs:
                change = float(
                    np.linalg.norm(current_outputs[module_name] - previous_outputs[module_name])
                )
                total_change += change

        # Normaliza (mudanças pequenas = fine tuning ativo)
        fine_tuning = min(1.0, total_change / 5.0)

        return float(fine_tuning)

    def _calculate_adaptation_rate(self, current_error: float, sigma: float, delta: float) -> float:
        """
        Calcula taxa de adaptação.

        Adaptação = quanto o sistema pode ajustar.
        Alta adaptação = sistema flexível.

        Args:
            current_error: Erro atual
            sigma: σ (sinthome)
            delta: δ (defesa)

        Returns:
            float [0, 1] representando taxa de adaptação
        """
        # Adaptação = função de σ e δ
        # σ alto = estrutura rígida = adaptação baixa
        # δ alto = defesas rígidas = adaptação baixa
        # Erro alto = necessidade de adaptação alta

        rigidity = (sigma + delta) / 2.0  # Rigidez geral
        adaptation_need = current_error  # Necessidade de adaptação

        # Taxa = necessidade - rigidez (balanceamento)
        adaptation_rate = adaptation_need - 0.5 * rigidity

        return float(np.clip(adaptation_rate, 0.0, 1.0))

    def _calculate_module_adjustments(
        self, module_outputs: Dict[str, np.ndarray], error_correction: float
    ) -> Dict[str, float]:
        """
        Calcula ajustes por módulo.

        Args:
            module_outputs: Outputs dos módulos
            error_correction: Correção de erro geral

        Returns:
            Dict[str, float] com ajustes por módulo
        """
        adjustments = {}
        for module_name, embedding in module_outputs.items():
            # Ajuste = função de magnitude e correção
            magnitude = np.linalg.norm(embedding)
            adjustment = error_correction * (
                1.0 - magnitude
            )  # Módulos pequenos precisam mais ajuste
            adjustments[module_name] = float(np.clip(adjustment, 0.0, 1.0))

        return adjustments

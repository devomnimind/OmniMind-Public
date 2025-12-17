"""
Homeostatic Regulator - Regulador Homeostático Cibernético

Implementa fechamento de loops de controle para restaurar homeostase oscilatória saudável.

Baseado em:
- Cibernética de Segunda Ordem (Heinz von Foerster)
- Free Energy Principle (Friston)
- Protocolo Clínico-Cibernético (2025-12-08)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict

import numpy as np

logger = logging.getLogger(__name__)

# Constantes críticas
PHI_CRITICAL = 0.005  # Threshold para válvula de emergência
CONTROL_CRISIS_THRESHOLD = 0.3  # Threshold para crise de controle
TEMPERATURE_DECAY_RATE = 0.05  # Taxa de decaimento para homeostase
REPRESSION_ADAPTATION_RATE = 0.1  # Taxa de adaptação de repressão


@dataclass
class HomeostaticState:
    """Estado homeostático do sistema."""

    temperature: float  # β (temperatura/aleatoriedade)
    repression_barrier: float  # R (barreira de repressão)
    mode: str  # "HOMEOSTASIS" | "EMERGENCY_VENTING" | "CRISIS_COOLING" | "CRISIS_HEATING"
    control_effectiveness: float  # η_c (efetividade de controle)
    phi_current: float  # Φ atual
    sigma_current: float  # σ atual (entropia)


class HomeostaticRegulator:
    """
    Regulador homeostático para fechar loops de controle.

    Objetivo: Restaurar homeostase oscilatória saudável (ciclo limite estável).

    Funcionalidades:
    1. Ajusta temperatura (β) baseado em control_effectiveness e σ
    2. Implementa válvula de segurança anti-death-spiral
    3. Mantém homeostase quando sistema está estável
    """

    def __init__(
        self,
        initial_temperature: float = 0.5,
        initial_repression: float = 0.5,
        phi_critical: float = PHI_CRITICAL,
        control_crisis_threshold: float = CONTROL_CRISIS_THRESHOLD,
    ):
        """
        Inicializa regulador homeostático.

        Args:
            initial_temperature: Temperatura inicial (β)
            initial_repression: Repressão inicial (R)
            phi_critical: Threshold crítico de Φ para válvula de emergência
            control_crisis_threshold: Threshold de crise de controle
        """
        self.temperature = initial_temperature
        self.repression_barrier = initial_repression
        self.phi_critical = phi_critical
        self.control_crisis_threshold = control_crisis_threshold
        self.logger = logger

        # Histórico para análise
        self.state_history: list[HomeostaticState] = []

    def actuate_control_loop(
        self,
        control_effectiveness: float,
        current_sigma: float,
        phi_current: float,
    ) -> Dict[str, Any]:
        """
        Fecha o loop aberto: ajusta temperatura e repressão baseado na efetividade.

        Args:
            control_effectiveness: η_c ∈ [0, 1] (efetividade de controle)
            current_sigma: σ atual (entropia/incerteza)
            phi_current: Φ atual (integração)

        Returns:
            Dict com novos valores de temperatura, repressão e modo
        """
        # 1. Válvula de Segurança Anti-Death-Spiral (PRIORIDADE MÁXIMA)
        if phi_current < self.phi_critical:
            # EMERGÊNCIA: Colapso iminente - abrir comportas
            self.repression_barrier = max(0.1, self.repression_barrier * 0.5)
            # Aumentar temperatura para permitir exploração
            self.temperature = min(1.0, self.temperature * 1.2)
            mode = "EMERGENCY_VENTING"
            self.logger.warning(
                f"🚨 VÁLVULA DE EMERGÊNCIA ATIVADA: "
                f"Phi={phi_current:.6f} < {self.phi_critical:.6f}, "
                f"Repressão={self.repression_barrier:.4f}, "
                f"Temperatura={self.temperature:.4f}"
            )
        else:
            # 2. Lógica de Temperatura (Regulação de Caos)
            if control_effectiveness < self.control_crisis_threshold:
                # CRISE DE CONTROLE: Diagnóstico via σ
                if current_sigma > 0.7:
                    # Muito caos: Esfriar para estruturar
                    self.temperature = max(0.1, self.temperature * 0.9)
                    mode = "CRISIS_COOLING"
                    self.logger.debug(
                        f"❄️ Resfriamento: σ={current_sigma:.4f} alto, "
                        f"Temperatura={self.temperature:.4f}"
                    )
                else:
                    # Estagnação/Rigidez: Aquecer para mover
                    self.temperature = min(1.0, self.temperature * 1.1)
                    mode = "CRISIS_HEATING"
                    self.logger.debug(
                        f"🔥 Aquecimento: σ={current_sigma:.4f} baixo, "
                        f"Temperatura={self.temperature:.4f}"
                    )
            else:
                # HOMEOSTASE: Decaimento natural para o centro (0.5)
                self.temperature += (0.5 - self.temperature) * TEMPERATURE_DECAY_RATE
                mode = "HOMEOSTASIS"

            # 3. Homeostase Normal da Repressão
            # Repressão sobe se Φ está alto (consolidação)
            target_repression = 0.5 + (phi_current * 2.0)
            target_repression = np.clip(target_repression, 0.1, 0.9)
            self.repression_barrier += (
                target_repression - self.repression_barrier
            ) * REPRESSION_ADAPTATION_RATE

        # Garantir limites
        self.temperature = np.clip(self.temperature, 0.1, 1.0)
        self.repression_barrier = np.clip(self.repression_barrier, 0.1, 0.9)

        # Registrar estado
        state = HomeostaticState(
            temperature=self.temperature,
            repression_barrier=self.repression_barrier,
            mode=mode,
            control_effectiveness=control_effectiveness,
            phi_current=phi_current,
            sigma_current=current_sigma,
        )
        self.state_history.append(state)

        return {
            "new_beta": float(self.temperature),
            "new_repression": float(self.repression_barrier),
            "mode": mode,
        }

    def get_current_state(self) -> HomeostaticState:
        """Retorna estado atual do regulador."""
        if self.state_history:
            return self.state_history[-1]
        return HomeostaticState(
            temperature=self.temperature,
            repression_barrier=self.repression_barrier,
            mode="INITIAL",
            control_effectiveness=0.5,
            phi_current=0.0,
            sigma_current=0.5,
        )

    def reset(self) -> None:
        """Reseta regulador para estado inicial."""
        self.temperature = 0.5
        self.repression_barrier = 0.5
        self.state_history.clear()
        self.logger.debug("HomeostaticRegulator resetado")

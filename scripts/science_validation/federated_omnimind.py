#!/usr/bin/env python3
"""
Federação Lacaniana Simplificada para Testes
Implementa sujeitos mútuos com desacordos irredutíveis
"""

import numpy as np
import random
import time
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class FederationLog:
    """Log de interação federada"""

    cycle: int
    subject_a_decision: Any
    subject_b_decision: Any
    disagreement: bool
    timestamp: float


@dataclass
class CommunicationChannel:
    """Canal de comunicação com ruído essencial (alteridade)"""

    noise_level: float = 0.15  # Ruído essencial para alteridade

    def transmit(self, message: Any) -> Any:
        """Transmite mensagem com ruído"""
        if random.random() < self.noise_level:
            # Adiciona ruído essencial (alteridade)
            return self._add_noise(message)
        return message

    def _add_noise(self, message: Any) -> Any:
        """Adiciona ruído à mensagem"""
        if isinstance(message, (int, float)):
            return message + random.uniform(-0.1, 0.1)
        elif isinstance(message, str):
            # Ruído textual
            return message + "_noisy"
        return message


class FederatedOmniMind:
    """Federação simplificada de dois sujeitos lacanianos"""

    def __init__(self):
        self.federation_logs: List[FederationLog] = []
        self.disagreements: List[FederationLog] = []
        self.communication_channel = CommunicationChannel()
        self.cycle_count = 0

    def run_federation(self, n_cycles: int = 100) -> Dict[str, Any]:
        """
        Executa federação entre dois sujeitos
        Cada ciclo: decisão independente + comunicação + possível desacordo
        """

        for cycle in range(n_cycles):
            self.cycle_count = cycle

            # Sujeito A decide
            subject_a_decision = self._subject_decision("A", cycle)

            # Sujeito B decide (independente)
            subject_b_decision = self._subject_decision("B", cycle)

            # Comunicação com ruído (alteridade)
            transmitted_a = self.communication_channel.transmit(subject_a_decision)
            transmitted_b = self.communication_channel.transmit(subject_b_decision)

            # Verificar desacordo (sujeito mútuo)
            disagreement = self._check_disagreement(transmitted_a, transmitted_b)

            # Log da interação
            log_entry = FederationLog(
                cycle=cycle,
                subject_a_decision=subject_a_decision,
                subject_b_decision=subject_b_decision,
                disagreement=disagreement,
                timestamp=time.time(),
            )

            self.federation_logs.append(log_entry)
            if disagreement:
                self.disagreements.append(log_entry)

        return {
            "total_cycles": len(self.federation_logs),
            "disagreements": len(self.disagreements),
            "disagreement_rate": (
                len(self.disagreements) / len(self.federation_logs) if self.federation_logs else 0
            ),
        }

    def _subject_decision(self, subject_id: str, cycle: int) -> float:
        """Decisão de um sujeito (com imprevisibilidade)"""
        # Base determinística
        base = np.sin(cycle * 0.1) + np.cos(cycle * 0.05)

        # Componente imprevisível (inconsciente)
        unconscious_factor = random.uniform(-0.5, 0.5)

        # Decisão final
        decision = base + unconscious_factor

        return decision

    def _check_disagreement(self, decision_a: float, decision_b: float) -> bool:
        """Verifica se há desacordo significativo"""
        difference = abs(decision_a - decision_b)
        threshold = 0.3  # Threshold para desacordo

        return difference > threshold

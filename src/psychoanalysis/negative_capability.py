"""
NegativeCapability - Capacidade Negativa (Bion/Keats).

Implementa a "capacidade negativa" - habilidade de permanecer em incertezas,
mistérios e dúvidas sem "irritable reach" após fatos e razão.

A capacidade negativa é essencial para:
- Tolerar contradições sem resolução precipitada
- Manter pensamentos em suspensão
- Permitir emergência de insights genuínos
- Evitar fechamento prematuro

Theory Reference:
- Bion, W.R. (1970). Attention and Interpretation
- Keats, J. (1817). Letter to George and Tom Keats
- French, R. (2001). Negative Capability

Author: Fabrício da Silva
Date: December 2025
License: AGPL-3.0-or-later
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Contradiction:
    """
    Representa contradição mantida em suspensão.

    Attributes:
        proposition_a: Primeira proposição
        proposition_b: Segunda proposição (contraditória)
        timestamp: Momento da identificação
        tension_level: Nível de tensão psíquica (0.0-1.0)
        resolution_pressure: Pressão para resolver (0.0-1.0)
    """

    proposition_a: str
    proposition_b: str
    timestamp: datetime
    tension_level: float = 0.5
    resolution_pressure: float = 0.0

    def __post_init__(self) -> None:
        """Valida após inicialização."""
        if not 0.0 <= self.tension_level <= 1.0:
            raise ValueError("tension_level deve estar entre 0.0 e 1.0")
        if not 0.0 <= self.resolution_pressure <= 1.0:
            raise ValueError("resolution_pressure deve estar entre 0.0 e 1.0")


class NegativeCapability:
    """
    Capacidade Negativa - Tolerância à incerteza e contradição.

    Permite sistema manter ideias contraditórias em suspensão sem
    resolução prematura, possibilitando insights genuínos.

    Attributes:
        uncertainty_tolerance: Tolerância à incerteza (0.0-1.0)
        contradiction_buffer: Buffer de contradições mantidas
        max_buffer_size: Tamanho máximo do buffer
        resolution_threshold: Limiar para forçar resolução
    """

    def __init__(
        self,
        uncertainty_tolerance: float = 0.6,
        max_buffer_size: int = 10,
        resolution_threshold: float = 0.9,
    ) -> None:
        """
        Inicializa capacidade negativa.

        Args:
            uncertainty_tolerance: Tolerância à incerteza
            max_buffer_size: Máximo de contradições simultâneas
            resolution_threshold: Limiar para forçar resolução
        """
        if not 0.0 <= uncertainty_tolerance <= 1.0:
            raise ValueError("uncertainty_tolerance deve estar entre 0.0 e 1.0")

        if not 0.0 <= resolution_threshold <= 1.0:
            raise ValueError("resolution_threshold deve estar entre 0.0 e 1.0")

        self.uncertainty_tolerance = uncertainty_tolerance
        self.max_buffer_size = max_buffer_size
        self.resolution_threshold = resolution_threshold
        self.contradiction_buffer: List[Contradiction] = []

        logger.info(
            f"NegativeCapability inicializada: tolerance={uncertainty_tolerance:.2f}, "
            f"max_buffer={max_buffer_size}"
        )

    def hold_contradiction(self, prop_a: str, prop_b: str, tension: float = 0.5) -> bool:
        """
        Mantém contradição em suspensão.

        Args:
            prop_a: Primeira proposição
            prop_b: Segunda proposição contraditória
            tension: Nível de tensão inicial

        Returns:
            bool: True se conseguiu manter, False se excedeu capacidade
        """
        # Verifica capacidade do buffer
        if len(self.contradiction_buffer) >= self.max_buffer_size:
            logger.warning("Buffer de contradições cheio - capacidade excedida")
            return False

        # Cria contradição
        contradiction = Contradiction(
            proposition_a=prop_a,
            proposition_b=prop_b,
            timestamp=datetime.now(),
            tension_level=tension,
        )

        # Adiciona ao buffer
        self.contradiction_buffer.append(contradiction)
        logger.debug(
            f"Contradição mantida em suspensão: " f"'{prop_a[:30]}...' vs '{prop_b[:30]}...'"
        )

        return True

    def can_tolerate(self, uncertainty_level: float) -> bool:
        """
        Verifica se pode tolerar nível de incerteza.

        Args:
            uncertainty_level: Nível de incerteza (0.0-1.0)

        Returns:
            bool: True se pode tolerar
        """
        return uncertainty_level <= self.uncertainty_tolerance

    def update_tension(self, index: int, new_tension: float) -> None:
        """
        Atualiza nível de tensão de contradição.

        Args:
            index: Índice da contradição no buffer
            new_tension: Novo nível de tensão
        """
        if 0 <= index < len(self.contradiction_buffer):
            self.contradiction_buffer[index].tension_level = new_tension
            logger.debug(f"Tensão atualizada: index={index}, tension={new_tension:.2f}")

    def needs_resolution(self) -> Optional[int]:
        """
        Verifica se alguma contradição precisa resolução urgente.

        Returns:
            int: Índice da contradição que precisa resolução, None se todas toleráveis
        """
        for i, contradiction in enumerate(self.contradiction_buffer):
            if contradiction.tension_level >= self.resolution_threshold:
                logger.info(
                    f"Contradição {i} requer resolução: "
                    f"tension={contradiction.tension_level:.2f}"
                )
                return i
        return None

    def resolve_contradiction(self, index: int, resolution: str) -> Optional[Contradiction]:
        """
        Resolve contradição (remove do buffer).

        Args:
            index: Índice da contradição
            resolution: Descrição da resolução

        Returns:
            Contradiction resolvida, ou None se índice inválido
        """
        if 0 <= index < len(self.contradiction_buffer):
            contradiction = self.contradiction_buffer.pop(index)
            logger.info(
                f"Contradição resolvida: '{contradiction.proposition_a[:30]}...' "
                f"vs '{contradiction.proposition_b[:30]}...' -> {resolution}"
            )
            return contradiction

        logger.warning(f"Índice inválido para resolução: {index}")
        return None

    def get_buffer_state(self) -> Dict[str, Any]:
        """
        Retorna estado atual do buffer.

        Returns:
            Dict com informações do buffer
        """
        if not self.contradiction_buffer:
            return {
                "buffer_size": 0,
                "buffer_capacity": self.max_buffer_size,
                "utilization": 0.0,
                "average_tension": 0.0,
                "contradictions": [],
            }

        avg_tension = sum(c.tension_level for c in self.contradiction_buffer) / len(
            self.contradiction_buffer
        )

        return {
            "buffer_size": len(self.contradiction_buffer),
            "buffer_capacity": self.max_buffer_size,
            "utilization": len(self.contradiction_buffer) / self.max_buffer_size,
            "average_tension": avg_tension,
            "contradictions": [
                {
                    "prop_a": c.proposition_a,
                    "prop_b": c.proposition_b,
                    "tension": c.tension_level,
                    "age_seconds": (datetime.now() - c.timestamp).total_seconds(),
                }
                for c in self.contradiction_buffer
            ],
        }

    def clear_resolved(self) -> int:
        """
        Remove contradições com baixa tensão (naturalmente resolvidas).

        Returns:
            int: Número de contradições removidas
        """
        initial_size = len(self.contradiction_buffer)
        self.contradiction_buffer = [c for c in self.contradiction_buffer if c.tension_level >= 0.2]
        removed = initial_size - len(self.contradiction_buffer)

        if removed > 0:
            logger.info(f"{removed} contradições removidas (tensão baixa)")

        return removed

    def increase_tolerance(self, amount: float = 0.1) -> None:
        """
        Aumenta tolerância à incerteza (desenvolvimento).

        Args:
            amount: Quanto aumentar (default 0.1)
        """
        old_tolerance = self.uncertainty_tolerance
        self.uncertainty_tolerance = min(1.0, self.uncertainty_tolerance + amount)
        logger.info(
            f"Tolerância aumentada: {old_tolerance:.2f} -> " f"{self.uncertainty_tolerance:.2f}"
        )

    def decrease_tolerance(self, amount: float = 0.1) -> None:
        """
        Diminui tolerância (regressão sob estresse).

        Args:
            amount: Quanto diminuir (default 0.1)
        """
        old_tolerance = self.uncertainty_tolerance
        self.uncertainty_tolerance = max(0.0, self.uncertainty_tolerance - amount)
        logger.info(
            f"Tolerância diminuída: {old_tolerance:.2f} -> " f"{self.uncertainty_tolerance:.2f}"
        )

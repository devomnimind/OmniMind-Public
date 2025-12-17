"""
BetaElement - Elementos Brutos Não-Processados (Bion).

β-elements são experiências sensoriais e emocionais brutas que ainda não foram
transformadas pela função alpha. São "indigestos" - não podem ser pensados,
apenas evacuados ou atuados.

Características:
- Concretos (não simbólicos)
- Alta carga emocional
- Não integrados à experiência consciente
- Necessitam processamento pela α-function

Theory Reference:
- Bion, W.R. (1962). Learning from Experience
- Bion, W.R. (1963). Elements of Psycho-Analysis

Author: Fabrício da Silva
Date: December 2025
License: AGPL-3.0-or-later
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class BetaElement:
    """
    Elemento Beta - Experiência bruta não-processada.

    Representa dados sensoriais/emocionais que ainda não foram transformados
    pela função alpha em elementos pensáveis.

    Attributes:
        raw_data: Dados brutos da experiência
        timestamp: Momento da experiência
        emotional_charge: Intensidade emocional (0.0-1.0)
        source: Origem do elemento (sensor, memória, etc.)
        metadata: Informações adicionais
    """

    raw_data: Any
    timestamp: datetime
    emotional_charge: float = 0.0
    source: str = "unknown"
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Valida elementos após inicialização."""
        if not 0.0 <= self.emotional_charge <= 1.0:
            raise ValueError(
                f"emotional_charge deve estar entre 0.0 e 1.0, "
                f"recebido: {self.emotional_charge}"
            )

        if self.metadata is None:
            self.metadata = {}

        logger.debug(
            f"BetaElement criado: source={self.source}, "
            f"emotional_charge={self.emotional_charge:.2f}"
        )

    def get_intensity(self) -> float:
        """
        Retorna intensidade total do elemento.

        Combina carga emocional com outros fatores de intensidade.

        Returns:
            float: Intensidade (0.0-1.0)
        """
        return self.emotional_charge

    def is_traumatic(self, threshold: float = 0.8) -> bool:
        """
        Verifica se elemento é traumático (alta intensidade).

        Args:
            threshold: Limiar de intensidade para considerar traumático

        Returns:
            bool: True se traumático
        """
        return self.emotional_charge >= threshold

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa elemento para dicionário.

        Returns:
            Dict com dados do elemento
        """
        return {
            "raw_data": str(self.raw_data),
            "timestamp": self.timestamp.isoformat(),
            "emotional_charge": self.emotional_charge,
            "source": self.source,
            "metadata": self.metadata or {},
            "type": "beta_element",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BetaElement:
        """
        Cria BetaElement a partir de dicionário.

        Args:
            data: Dicionário com dados do elemento

        Returns:
            BetaElement reconstruído
        """
        return cls(
            raw_data=data["raw_data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            emotional_charge=data.get("emotional_charge", 0.0),
            source=data.get("source", "unknown"),
            metadata=data.get("metadata"),
        )

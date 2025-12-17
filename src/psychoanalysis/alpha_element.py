"""
AlphaElement - Elementos Transformados e Pensáveis (Bion).

α-elements são o resultado da transformação de β-elements pela função alpha.
São pensáveis, podem ser armazenados como memória e usados para pensar.

Características:
- Simbólicos (podem ser representados)
- Integrados à experiência consciente
- Podem ser combinados em pensamentos
- Armazenáveis como memória

Theory Reference:
- Bion, W.R. (1962). Learning from Experience
- Bion, W.R. (1963). Elements of Psycho-Analysis

Author: Fabrício da Silva
Date: December 2025
License: AGPL-3.0-or-later
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .beta_element import BetaElement

logger = logging.getLogger(__name__)


@dataclass
class AlphaElement:
    """
    Elemento Alpha - Experiência transformada e pensável.

    Representa β-elements que foram transformados pela função alpha em
    elementos que podem ser pensados, armazenados e combinados.

    Attributes:
        content: Conteúdo processado e simbólico
        origin_beta: BetaElement de origem
        timestamp: Momento da transformação
        narrative_form: Forma narrativa do elemento
        symbolic_potential: Potencial de simbolização (0.0-1.0)
        associations: Outros α-elements associados
        metadata: Informações adicionais
    """

    content: Any
    origin_beta: BetaElement
    timestamp: datetime
    narrative_form: str = ""
    symbolic_potential: float = 0.0
    associations: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Valida elementos após inicialização."""
        if not 0.0 <= self.symbolic_potential <= 1.0:
            raise ValueError(
                f"symbolic_potential deve estar entre 0.0 e 1.0, "
                f"recebido: {self.symbolic_potential}"
            )

        if self.metadata is None:
            self.metadata = {}

        logger.debug(
            f"AlphaElement criado: symbolic_potential={self.symbolic_potential:.2f}, "
            f"narrative_form_length={len(self.narrative_form)}"
        )

    def can_be_thought(self) -> bool:
        """
        Verifica se elemento pode ser pensado.

        Um α-element é pensável se tem potencial simbólico suficiente.

        Returns:
            bool: True se pensável
        """
        return self.symbolic_potential >= 0.3

    def is_dream_capable(self) -> bool:
        """
        Verifica se elemento pode ser usado em sonhos (dream-thoughts).

        Elements com alto potencial simbólico podem formar pensamentos oníricos.

        Returns:
            bool: True se pode ser usado em sonhos
        """
        return self.symbolic_potential >= 0.6

    def get_complexity(self) -> float:
        """
        Retorna complexidade do elemento.

        Baseado em potencial simbólico e número de associações.

        Returns:
            float: Complexidade (0.0-1.0)
        """
        base_complexity = self.symbolic_potential
        association_bonus = min(len(self.associations) * 0.1, 0.3)
        return min(base_complexity + association_bonus, 1.0)

    def add_association(self, other_alpha_id: str) -> None:
        """
        Adiciona associação com outro α-element.

        Args:
            other_alpha_id: ID do outro α-element
        """
        if other_alpha_id not in self.associations:
            self.associations.append(other_alpha_id)
            logger.debug(f"Associação adicionada: {other_alpha_id}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa elemento para dicionário.

        Returns:
            Dict com dados do elemento
        """
        return {
            "content": str(self.content),
            "origin_beta": self.origin_beta.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "narrative_form": self.narrative_form,
            "symbolic_potential": self.symbolic_potential,
            "associations": self.associations,
            "metadata": self.metadata or {},
            "type": "alpha_element",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AlphaElement:
        """
        Cria AlphaElement a partir de dicionário.

        Args:
            data: Dicionário com dados do elemento

        Returns:
            AlphaElement reconstruído
        """
        origin_beta = BetaElement.from_dict(data["origin_beta"])

        return cls(
            content=data["content"],
            origin_beta=origin_beta,
            timestamp=datetime.fromisoformat(data["timestamp"]),
            narrative_form=data.get("narrative_form", ""),
            symbolic_potential=data.get("symbolic_potential", 0.0),
            associations=data.get("associations", []),
            metadata=data.get("metadata"),
        )

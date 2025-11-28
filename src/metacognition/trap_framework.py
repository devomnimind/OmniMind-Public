import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
TRAP Framework - Metacognition Level Hierarchy

TRAP = Transparency, Reasoning, Adaptation, Perception

11-tier hierarchy (Level 0-10):
  0. Monitoramento básico
  1. Controle executivo
  2. Planejamento estratégico
  3. Avaliação de desempenho
  4. Reflexão sobre processos (CURRENT - Phase 15)
  5. Meta-reflexão (NOVO - Phase 16)
  6. Teoria da mente avançada (NOVO - Phase 16)
  7. Auto-modificação (NOVO - Phase 16)
  8-10. Futuros níveis
"""


logger = logging.getLogger(__name__)


class TRAPComponent(Enum):
    """Componentes do framework TRAP."""

    TRANSPARENCY = "transparency"
    REASONING = "reasoning"
    ADAPTATION = "adaptation"
    PERCEPTION = "perception"


@dataclass
class TRAPScore:
    """Score de cada componente TRAP."""

    transparency: float = 0.5  # 0-1
    reasoning: float = 0.5
    adaptation: float = 0.5
    perception: float = 0.5

    def overall_wisdom(self) -> float:
        """Calcula score geral de sabedoria."""
        return (
            self.transparency * 0.25
            + self.reasoning * 0.25
            + self.adaptation * 0.25
            + self.perception * 0.25
        )


class TRAPFramework:
    """
    Framework TRAP completo com 11 níveis de metacognição.

    Implementa avaliação estruturada de:
      - Transparency: Explica decisões
      - Reasoning: Qualidade do raciocínio
      - Adaptation: Capacidade de aprender
      - Perception: Compreensão do contexto
    """

    def __init__(self) -> None:
        """Inicializa framework TRAP."""
        self.scores: Dict[str, TRAPScore] = {}
        self.decision_history: List[Dict[str, Any]] = []
        self.metacognitive_level = 4  # Atualmente Level 4 (Phase 15)

        logger.info(f"TRAP Framework initialized (level={self.metacognitive_level})")

    def evaluate(
        self,
        decision: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> TRAPScore:
        """
        Avaliar decisão usando framework TRAP.

        Args:
            decision: Descrição da decisão
            context: Contexto da decisão

        Returns:
            TRAPScore com scores de cada componente
        """
        logger.info(f"TRAP evaluation: {decision}")

        # Avaliação básica (placeholder)
        score = TRAPScore(
            transparency=0.75,  # Quão explícita é a decisão?
            reasoning=0.70,  # Quão bem fundamentada?
            adaptation=0.65,  # Quão adaptável?
            perception=0.80,  # Quão contextualizada?
        )

        self.scores[decision] = score
        self.decision_history.append(
            {
                "decision": decision,
                "score": score,
                "context": context,
            }
        )

        logger.info(f"TRAP score: {score.overall_wisdom():.2%}")
        return score

    def get_metacognitive_level(self) -> int:
        """Retorna nível atual de metacognição."""
        return self.metacognitive_level

    def advance_metacognitive_level(self) -> None:
        """Avança para próximo nível de metacognição."""
        if self.metacognitive_level < 10:
            self.metacognitive_level += 1
            logger.info(f"Advanced to metacognitive level {self.metacognitive_level}")
        else:
            logger.warning("Already at max metacognitive level")

    def get_wisdom_score(self) -> float:
        """
        Calcula score geral de sabedoria do sistema.

        Returns:
            Score 0-1 representando wisdom geral
        """
        if not self.scores:
            return 0.0

        return sum(s.overall_wisdom() for s in self.scores.values()) / len(self.scores)

    def explain_decision(self, decision: str) -> str:
        """Explica razões por trás de uma decisão."""
        if decision not in self.scores:
            return f"No TRAP evaluation found for: {decision}"

        score = self.scores[decision]
        explanation = f"""
DECISION EXPLANATION (TRAP Framework):
  Decision: {decision}

  Transparency: {score.transparency:.0%}
    └─ How explicitly explained

  Reasoning: {score.reasoning:.0%}
    └─ Quality of underlying logic

  Adaptation: {score.adaptation:.0%}
    └─ Can adjust to new situations

  Perception: {score.perception:.0%}
    └─ Understanding of context

  Overall Wisdom: {score.overall_wisdom():.0%}
"""
        return explanation

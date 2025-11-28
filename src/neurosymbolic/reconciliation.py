import logging
from dataclasses import dataclass
from enum import Enum

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
Estratégias de Reconciliação - Quando Neural e Simbólico Discordam

Estratégias:
  - agreement: Ambos concordam
  - neural_dominant: Criatividade / problemas abertos
  - symbolic_dominant: Lógica / problemas formais
  - synthesis: Combinar ambos (recomendado)
"""


logger = logging.getLogger(__name__)


class ReconciliationStrategy(Enum):
    """Estratégias de reconciliação entre neural e simbólico."""

    AGREEMENT = "agreement"
    NEURAL_DOMINANT = "neural_dominant"
    SYMBOLIC_DOMINANT = "symbolic_dominant"
    SYNTHESIS = "synthesis"


@dataclass
class ReconciliationResult:
    """Resultado de reconciliação."""

    final_answer: str
    strategy_used: ReconciliationStrategy
    neural_contribution: float  # 0-1
    symbolic_contribution: float  # 0-1
    confidence: float
    explanation: str


class Reconciliator:
    """
    Reconcilia resultados de neural e simbólico.

    Decide como combinar ou escolher entre respostas quando
    neural e simbólico fornecem resultados diferentes.
    """

    @staticmethod
    def reconcile(
        neural_answer: str,
        neural_confidence: float,
        symbolic_answer: str,
        symbolic_certainty: float,
        strategy: ReconciliationStrategy = ReconciliationStrategy.SYNTHESIS,
    ) -> ReconciliationResult:
        """
        Reconciliar respostas neural e simbólica.

        Args:
            neural_answer: Resposta neural
            neural_confidence: Confiança neural (0-1)
            symbolic_answer: Resposta simbólica
            symbolic_certainty: Certeza simbólica (0-1)
            strategy: Estratégia de reconciliação

        Returns:
            ReconciliationResult com resposta final
        """
        logger.info(
            f"Reconciling: neural({neural_confidence:.2f}) vs "
            f"symbolic({symbolic_certainty:.2f})"
        )

        if strategy == ReconciliationStrategy.AGREEMENT:
            return Reconciliator._reconcile_agreement(
                neural_answer,
                neural_confidence,
                symbolic_answer,
                symbolic_certainty,
            )
        elif strategy == ReconciliationStrategy.NEURAL_DOMINANT:
            return Reconciliator._reconcile_neural_dominant(
                neural_answer,
                neural_confidence,
                symbolic_answer,
                symbolic_certainty,
            )
        elif strategy == ReconciliationStrategy.SYMBOLIC_DOMINANT:
            return Reconciliator._reconcile_symbolic_dominant(
                neural_answer,
                neural_confidence,
                symbolic_answer,
                symbolic_certainty,
            )
        else:  # SYNTHESIS
            return Reconciliator._reconcile_synthesis(
                neural_answer,
                neural_confidence,
                symbolic_answer,
                symbolic_certainty,
            )

    @staticmethod
    def _reconcile_agreement(
        neural_answer: str,
        neural_confidence: float,
        symbolic_answer: str,
        symbolic_certainty: float,
    ) -> ReconciliationResult:
        """Quando ambos concordam, confiança é alta."""
        logger.debug("Strategy: AGREEMENT")

        # Se respostas são similares
        agreement = neural_answer.lower() == symbolic_answer.lower()

        if agreement:
            confidence = min(neural_confidence + symbolic_certainty, 1.0)
            return ReconciliationResult(
                final_answer=neural_answer,
                strategy_used=ReconciliationStrategy.AGREEMENT,
                neural_contribution=0.5,
                symbolic_contribution=0.5,
                confidence=confidence,
                explanation="Both neural and symbolic systems agree",
            )
        else:
            # Não há acordo - usar síntese
            return Reconciliator._reconcile_synthesis(
                neural_answer,
                neural_confidence,
                symbolic_answer,
                symbolic_certainty,
            )

    @staticmethod
    def _reconcile_neural_dominant(
        neural_answer: str,
        neural_confidence: float,
        symbolic_answer: str,
        symbolic_certainty: float,
    ) -> ReconciliationResult:
        """Neural domina - para criatividade e tarefas abertas."""
        logger.debug("Strategy: NEURAL_DOMINANT")

        return ReconciliationResult(
            final_answer=neural_answer,
            strategy_used=ReconciliationStrategy.NEURAL_DOMINANT,
            neural_contribution=0.8,
            symbolic_contribution=0.2,
            confidence=neural_confidence,
            explanation="Neural system dominant - creative/open-ended task",
        )

    @staticmethod
    def _reconcile_symbolic_dominant(
        neural_answer: str,
        neural_confidence: float,
        symbolic_answer: str,
        symbolic_certainty: float,
    ) -> ReconciliationResult:
        """Symbolic domina - para lógica e problemas formais."""
        logger.debug("Strategy: SYMBOLIC_DOMINANT")

        return ReconciliationResult(
            final_answer=symbolic_answer,
            strategy_used=ReconciliationStrategy.SYMBOLIC_DOMINANT,
            neural_contribution=0.2,
            symbolic_contribution=0.8,
            confidence=symbolic_certainty,
            explanation="Symbolic system dominant - formal/logical task",
        )

    @staticmethod
    def _reconcile_synthesis(
        neural_answer: str,
        neural_confidence: float,
        symbolic_answer: str,
        symbolic_certainty: float,
    ) -> ReconciliationResult:
        """Síntese - combinar perspectivas."""
        logger.debug("Strategy: SYNTHESIS")

        # Combinar respostas
        combined = f"{neural_answer} (neural) + {symbolic_answer} (symbolic)"

        # Confiança é média
        combined_confidence = (neural_confidence + symbolic_certainty) / 2.0

        return ReconciliationResult(
            final_answer=combined,
            strategy_used=ReconciliationStrategy.SYNTHESIS,
            neural_contribution=0.5,
            symbolic_contribution=0.5,
            confidence=combined_confidence,
            explanation="Synthesized neural and symbolic perspectives",
        )

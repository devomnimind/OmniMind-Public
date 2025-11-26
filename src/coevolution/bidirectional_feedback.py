"""
Sistema de Feedback Bidirecional Humano-IA.

Permite feedback estruturado em ambas direções:
- Humano → IA: Correções, preferências, avaliações
- IA → Humano: Observações, sugestões, questões
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Tipo de feedback."""

    CORRECTION = "correction"
    PREFERENCE = "preference"
    EVALUATION = "evaluation"
    OBSERVATION = "observation"
    SUGGESTION = "suggestion"
    QUESTION = "question"


class FeedbackDirection(Enum):
    """Direção do feedback."""

    HUMAN_TO_AI = "human_to_ai"
    AI_TO_HUMAN = "ai_to_human"


@dataclass
class FeedbackItem:
    """Item de feedback."""

    timestamp: datetime
    direction: FeedbackDirection
    feedback_type: FeedbackType
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False


@dataclass
class FeedbackLoop:
    """Loop de feedback completo."""

    loop_id: str
    items: List[FeedbackItem] = field(default_factory=list)
    is_harmful: bool = False
    convergence_detected: bool = False


class BidirectionalFeedback:
    """
    Sistema de feedback bidirecional estruturado.

    Princípios:
    1. Feedback é diálogo, não comando
    2. Ambas partes podem iniciar feedback
    3. Detecção de loops nocivos
    4. Aprendizado mútuo
    """

    def __init__(self) -> None:
        """Inicializa sistema de feedback."""
        self.feedback_history: List[FeedbackItem] = []
        self.active_loops: Dict[str, FeedbackLoop] = {}
        self.harmful_patterns: List[str] = [
            "circular_disagreement",
            "escalating_conflict",
            "stagnation",
        ]

    def submit_human_feedback(
        self,
        feedback_type: FeedbackType,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> FeedbackItem:
        """
        Submete feedback do humano para IA.

        Args:
            feedback_type: Tipo de feedback
            content: Conteúdo do feedback
            context: Contexto adicional

        Returns:
            FeedbackItem criado
        """
        item = FeedbackItem(
            timestamp=datetime.now(),
            direction=FeedbackDirection.HUMAN_TO_AI,
            feedback_type=feedback_type,
            content=content,
            context=context or {},
        )

        self.feedback_history.append(item)
        logger.info(f"Human feedback received: {feedback_type.value}")

        # Detecta loops nocivos
        self._detect_harmful_loops()

        return item

    def submit_ai_feedback(
        self,
        feedback_type: FeedbackType,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> FeedbackItem:
        """
        Submete feedback da IA para humano.

        Args:
            feedback_type: Tipo de feedback
            content: Conteúdo do feedback
            context: Contexto adicional

        Returns:
            FeedbackItem criado
        """
        item = FeedbackItem(
            timestamp=datetime.now(),
            direction=FeedbackDirection.AI_TO_HUMAN,
            feedback_type=feedback_type,
            content=content,
            context=context or {},
        )

        self.feedback_history.append(item)
        logger.info(f"AI feedback submitted: {feedback_type.value}")

        return item

    def get_feedback_summary(
        self,
        direction: Optional[FeedbackDirection] = None,
        feedback_type: Optional[FeedbackType] = None,
        limit: Optional[int] = None,
    ) -> List[FeedbackItem]:
        """
        Retorna sumário de feedback filtrado.

        Args:
            direction: Filtrar por direção
            feedback_type: Filtrar por tipo
            limit: Número máximo de itens

        Returns:
            Lista de itens de feedback
        """
        filtered = self.feedback_history

        if direction:
            filtered = [f for f in filtered if f.direction == direction]

        if feedback_type:
            filtered = [f for f in filtered if f.feedback_type == feedback_type]

        if limit:
            filtered = filtered[-limit:]

        return filtered

    def _detect_harmful_loops(self) -> None:
        """Detecta loops de feedback nocivos."""
        # Analisa últimos 10 feedbacks
        recent = self.feedback_history[-10:]

        if len(recent) < 5:
            return

        # Detecta padrões circulares
        if self._is_circular_pattern(recent):
            logger.warning("Circular feedback pattern detected!")
            self._create_loop_warning("circular_disagreement")

        # Detecta escalação de conflito
        if self._is_escalating_conflict(recent):
            logger.warning("Escalating conflict detected!")
            self._create_loop_warning("escalating_conflict")

        # Detecta estagnação
        if self._is_stagnation(recent):
            logger.warning("Feedback stagnation detected!")
            self._create_loop_warning("stagnation")

    def _is_circular_pattern(self, feedback_list: List[FeedbackItem]) -> bool:
        """Detecta padrão circular."""
        # Simplificado: verifica se há alternância repetida
        if len(feedback_list) < 4:
            return False

        directions = [f.direction for f in feedback_list]

        # Conta alternâncias
        alternations = 0
        for i in range(1, len(directions)):
            if directions[i] != directions[i - 1]:
                alternations += 1

        # Circular se alterna demais
        return alternations >= len(directions) * 0.8

    def _is_escalating_conflict(self, feedback_list: List[FeedbackItem]) -> bool:
        """Detecta escalação de conflito."""
        # Simplificado: verifica se há muitas correções consecutivas
        corrections = [
            f for f in feedback_list if f.feedback_type == FeedbackType.CORRECTION
        ]

        return len(corrections) >= len(feedback_list) * 0.7

    def _is_stagnation(self, feedback_list: List[FeedbackItem]) -> bool:
        """Detecta estagnação."""
        # Simplificado: verifica se conteúdo é muito similar
        if len(feedback_list) < 3:
            return False

        contents = [f.content for f in feedback_list]

        # Verifica repetição exata
        unique_contents = set(contents)

        return len(unique_contents) <= len(contents) * 0.3

    def _create_loop_warning(self, pattern_type: str) -> None:
        """Cria aviso de loop nocivo."""
        loop = FeedbackLoop(
            loop_id=f"loop_{len(self.active_loops)}_{pattern_type}",
            items=self.feedback_history[-10:],
            is_harmful=True,
        )

        self.active_loops[loop.loop_id] = loop

        # IA oferece feedback sobre o loop
        self.submit_ai_feedback(
            feedback_type=FeedbackType.OBSERVATION,
            content=(
                f"Detectei um padrão de feedback nocivo: {pattern_type}. "
                "Sugiro pausarmos e refletirmos sobre a abordagem."
            ),
            context={"loop_id": loop.loop_id, "pattern": pattern_type},
        )

    def acknowledge_feedback(self, item: FeedbackItem) -> None:
        """
        Marca feedback como reconhecido.

        Args:
            item: Item de feedback
        """
        item.acknowledged = True
        logger.debug(f"Feedback acknowledged: {item.feedback_type.value}")

    def get_unacknowledged_feedback(
        self, direction: Optional[FeedbackDirection] = None
    ) -> List[FeedbackItem]:
        """
        Retorna feedback não reconhecido.

        Args:
            direction: Filtrar por direção

        Returns:
            Lista de itens não reconhecidos
        """
        unack = [f for f in self.feedback_history if not f.acknowledged]

        if direction:
            unack = [f for f in unack if f.direction == direction]

        return unack

    def clear_harmful_loops(self) -> None:
        """Limpa loops nocivos detectados."""
        self.active_loops = {}
        logger.info("Harmful loops cleared")

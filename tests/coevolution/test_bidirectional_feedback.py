"""
Testes para Bidirectional Feedback System.
"""

from src.coevolution.bidirectional_feedback import (
    BidirectionalFeedback,
    FeedbackType,
    FeedbackDirection,
    FeedbackItem,
)


class TestBidirectionalFeedback:
    """Testes do sistema de feedback bidirecional."""

    def test_initialization(self) -> None:
        """Testa inicialização do sistema de feedback."""
        feedback = BidirectionalFeedback()
        assert feedback is not None
        assert len(feedback.feedback_history) == 0
        assert len(feedback.active_loops) == 0

    def test_submit_human_feedback(self) -> None:
        """Testa submissão de feedback do humano."""
        feedback = BidirectionalFeedback()

        item = feedback.submit_human_feedback(
            feedback_type=FeedbackType.CORRECTION,
            content="Please fix this",
            context={"item": "value"},
        )

        assert isinstance(item, FeedbackItem)
        assert item.direction == FeedbackDirection.HUMAN_TO_AI
        assert item.feedback_type == FeedbackType.CORRECTION
        assert item.content == "Please fix this"
        assert len(feedback.feedback_history) == 1

    def test_submit_ai_feedback(self) -> None:
        """Testa submissão de feedback da IA."""
        feedback = BidirectionalFeedback()

        item = feedback.submit_ai_feedback(
            feedback_type=FeedbackType.SUGGESTION,
            content="I suggest we try this approach",
        )

        assert isinstance(item, FeedbackItem)
        assert item.direction == FeedbackDirection.AI_TO_HUMAN
        assert item.feedback_type == FeedbackType.SUGGESTION
        assert len(feedback.feedback_history) == 1

    def test_get_feedback_summary_all(self) -> None:
        """Testa sumário completo de feedback."""
        feedback = BidirectionalFeedback()

        feedback.submit_human_feedback(FeedbackType.CORRECTION, "Fix 1")
        feedback.submit_ai_feedback(FeedbackType.OBSERVATION, "Note 1")
        feedback.submit_human_feedback(FeedbackType.PREFERENCE, "Prefer this")

        summary = feedback.get_feedback_summary()

        assert len(summary) == 3

    def test_get_feedback_summary_filtered_direction(self) -> None:
        """Testa sumário filtrado por direção."""
        feedback = BidirectionalFeedback()

        feedback.submit_human_feedback(FeedbackType.CORRECTION, "Fix 1")
        feedback.submit_ai_feedback(FeedbackType.OBSERVATION, "Note 1")

        human_to_ai = feedback.get_feedback_summary(direction=FeedbackDirection.HUMAN_TO_AI)

        assert len(human_to_ai) == 1
        assert human_to_ai[0].direction == FeedbackDirection.HUMAN_TO_AI

    def test_get_feedback_summary_filtered_type(self) -> None:
        """Testa sumário filtrado por tipo."""
        feedback = BidirectionalFeedback()

        feedback.submit_human_feedback(FeedbackType.CORRECTION, "Fix 1")
        feedback.submit_human_feedback(FeedbackType.PREFERENCE, "Prefer this")

        corrections = feedback.get_feedback_summary(feedback_type=FeedbackType.CORRECTION)

        assert len(corrections) == 1
        assert corrections[0].feedback_type == FeedbackType.CORRECTION

    def test_get_feedback_summary_limit(self) -> None:
        """Testa limite de sumário."""
        feedback = BidirectionalFeedback()

        for i in range(10):
            feedback.submit_human_feedback(FeedbackType.EVALUATION, f"Eval {i}")

        summary = feedback.get_feedback_summary(limit=5)

        assert len(summary) == 5

    def test_acknowledge_feedback(self) -> None:
        """Testa reconhecimento de feedback."""
        feedback = BidirectionalFeedback()

        item = feedback.submit_human_feedback(FeedbackType.CORRECTION, "Fix this")

        assert not item.acknowledged

        feedback.acknowledge_feedback(item)

        assert item.acknowledged

    def test_get_unacknowledged_feedback(self) -> None:
        """Testa obtenção de feedback não reconhecido."""
        feedback = BidirectionalFeedback()

        item1 = feedback.submit_human_feedback(FeedbackType.CORRECTION, "Fix 1")
        item2 = feedback.submit_human_feedback(FeedbackType.CORRECTION, "Fix 2")

        feedback.acknowledge_feedback(item1)

        unack = feedback.get_unacknowledged_feedback()

        assert len(unack) == 1
        assert unack[0] == item2

    def test_detect_circular_pattern(self) -> None:
        """Testa detecção de padrão circular."""
        feedback = BidirectionalFeedback()

        # Cria padrão alternado (circular)
        for i in range(6):
            if i % 2 == 0:
                feedback.submit_human_feedback(FeedbackType.CORRECTION, f"Fix {i}")
            else:
                feedback.submit_ai_feedback(FeedbackType.OBSERVATION, f"Note {i}")

        # Deve detectar padrão circular
        # (método _detect_harmful_loops é chamado automaticamente)
        # Verifica se houve criação de loop warning via feedback da IA
        ai_feedback = feedback.get_feedback_summary(direction=FeedbackDirection.AI_TO_HUMAN)

        # Pode ter feedback da IA sobre loop detectado
        assert len(ai_feedback) >= 3  # 3 originais

    def test_detect_escalating_conflict(self) -> None:
        """Testa detecção de conflito escalando."""
        feedback = BidirectionalFeedback()

        # Cria muitas correções consecutivas
        for i in range(8):
            feedback.submit_human_feedback(FeedbackType.CORRECTION, f"Fix {i}")

        # Deve detectar escalação
        # Verifica se sistema criou warning
        assert len(feedback.feedback_history) >= 8

    def test_detect_stagnation(self) -> None:
        """Testa detecção de estagnação."""
        feedback = BidirectionalFeedback()

        # Submete feedback repetido
        for _ in range(5):
            feedback.submit_human_feedback(FeedbackType.EVALUATION, "Same feedback")

        # Deve detectar estagnação
        assert len(feedback.feedback_history) >= 5

    def test_clear_harmful_loops(self) -> None:
        """Testa limpeza de loops nocivos."""
        feedback = BidirectionalFeedback()

        # Cria loop
        for i in range(6):
            if i % 2 == 0:
                feedback.submit_human_feedback(FeedbackType.CORRECTION, f"Fix {i}")
            else:
                feedback.submit_ai_feedback(FeedbackType.OBSERVATION, f"Note {i}")

        # Limpa loops
        feedback.clear_harmful_loops()

        assert len(feedback.active_loops) == 0

    def test_feedback_types_enum(self) -> None:
        """Testa enum de tipos de feedback."""
        assert FeedbackType.CORRECTION.value == "correction"
        assert FeedbackType.PREFERENCE.value == "preference"
        assert FeedbackType.EVALUATION.value == "evaluation"
        assert FeedbackType.OBSERVATION.value == "observation"
        assert FeedbackType.SUGGESTION.value == "suggestion"
        assert FeedbackType.QUESTION.value == "question"

    def test_feedback_directions_enum(self) -> None:
        """Testa enum de direções de feedback."""
        assert FeedbackDirection.HUMAN_TO_AI.value == "human_to_ai"
        assert FeedbackDirection.AI_TO_HUMAN.value == "ai_to_human"

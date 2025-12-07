"""
Testes para EnhancedCodeAgent.

Autor: Fabrício da Silva + assistência de IA
"""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.enhanced_code_agent import EnhancedCodeAgent, FailureRecord
from src.orchestrator.error_analyzer import ErrorType, RecoveryStrategy


class TestEnhancedCodeAgent:
    """Testes para EnhancedCodeAgent."""

    @pytest.fixture
    def enhanced_agent(self):
        """Fixture para EnhancedCodeAgent."""
        with patch("src.agents.code_agent.CodeAgent.__init__"):
            agent = EnhancedCodeAgent(config_path="config/test_config.yaml")
            # Não podemos atribuir diretamente a métodos, usar patch no método específico
            return agent

    def test_init(self, enhanced_agent):
        """Testa inicialização."""
        assert enhanced_agent.error_analyzer is not None
        assert enhanced_agent.failure_history == []
        assert enhanced_agent.learned_patterns == {}

    def test_validate_output_valid(self, enhanced_agent):
        """Testa validação de output válido."""
        result = {"status": "success", "data": "test"}
        assert enhanced_agent._validate_output(result) is True

    def test_validate_output_invalid(self, enhanced_agent):
        """Testa validação de output inválido."""
        result_error = {"status": "error", "error": "test error"}
        assert enhanced_agent._validate_output(result_error) is False

        result_failed = {"status": "failed"}
        assert enhanced_agent._validate_output(result_failed) is False

        assert enhanced_agent._validate_output(None) is False

    def test_execute_task_with_self_correction_success(self, enhanced_agent):
        """Testa execução bem-sucedida na primeira tentativa."""
        enhanced_agent.execute.return_value = {"status": "success", "result": "ok"}
        enhanced_agent._validate_output = MagicMock(return_value=True)

        result = enhanced_agent.execute_task_with_self_correction("test task")

        assert result["status"] == "success"
        assert result["attempts"] == 1
        assert result["corrections_applied"] is False

    def test_execute_task_with_self_correction_retry(self, enhanced_agent):
        """Testa execução com retry após erro."""
        # Primeira tentativa falha, segunda sucede
        enhanced_agent.execute.side_effect = [
            Exception("Test error"),
            {"status": "success", "result": "ok"},
        ]
        enhanced_agent._validate_output = MagicMock(return_value=True)

        # Mock error_analyzer
        mock_analysis = MagicMock()
        mock_analysis.pattern = "test_pattern"
        mock_analysis.error_type = ErrorType.SYNTAX_ERROR
        mock_analysis.recovery_strategy = RecoveryStrategy.CORRECT_REASONING
        mock_analysis.to_dict = MagicMock(return_value={"error_type": "SYNTAX_ERROR"})

        enhanced_agent.error_analyzer.analyze_error = MagicMock(return_value=mock_analysis)
        enhanced_agent._apply_recovery_strategy = MagicMock(return_value="corrected task")

        result = enhanced_agent.execute_task_with_self_correction("test task", max_attempts=2)

        assert result["status"] == "success"
        assert result["attempts"] == 2
        assert result["corrections_applied"] is True

    def test_apply_recovery_strategy_correct_reasoning(self, enhanced_agent):
        """Testa aplicação de estratégia CORRECT_REASONING."""
        mock_analysis = MagicMock()
        mock_analysis.error_type = ErrorType.HALLUCINATION
        mock_analysis.recovery_strategy = RecoveryStrategy.CORRECT_REASONING

        corrected = enhanced_agent._apply_recovery_strategy(
            task="test task",
            error=ValueError("test"),
            error_analysis=mock_analysis,
            recovery_strategy=RecoveryStrategy.CORRECT_REASONING,
            context={},
        )

        assert "test task" in corrected
        assert "[Verificar fatos" in corrected or "[Aplicar correção" in corrected

    def test_learn_from_success(self, enhanced_agent):
        """Testa aprendizado de sucesso."""
        mock_analysis = MagicMock()
        mock_analysis.pattern = "test_pattern"
        mock_analysis.recovery_strategy = RecoveryStrategy.CORRECT_REASONING

        enhanced_agent._learn_from_success("test task", mock_analysis, {"result": "ok"})

        assert "test_pattern" in enhanced_agent.learned_patterns
        assert enhanced_agent.learned_patterns["test_pattern"] == RecoveryStrategy.CORRECT_REASONING

    def test_get_learning_stats(self, enhanced_agent):
        """Testa obtenção de estatísticas de aprendizado."""
        # Adicionar alguns registros de falha
        enhanced_agent.failure_history.append(
            FailureRecord(
                error_type=ErrorType.SYNTAX_ERROR,
                error_message="test",
                context={},
                recovery_strategy=RecoveryStrategy.CORRECT_REASONING,
                success=True,
                attempt_count=1,
            )
        )
        enhanced_agent.learned_patterns["pattern1"] = RecoveryStrategy.CORRECT_REASONING

        stats = enhanced_agent.get_learning_stats()

        assert stats["total_failures"] == 1
        assert stats["successful_recoveries"] == 1
        assert stats["learned_patterns"] == 1
        assert "pattern1" in stats["patterns"]

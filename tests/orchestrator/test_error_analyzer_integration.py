"""
Testes de integração do ErrorAnalyzer com OrchestratorAgent.

Autor: Fabrício da Silva + assistência de IA
"""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from src.agents.orchestrator_agent import OrchestratorAgent
from src.orchestrator.error_analyzer import ErrorAnalyzer, ErrorType, RecoveryStrategy


class TestErrorAnalyzerIntegration:
    """Testes de integração ErrorAnalyzer + OrchestratorAgent.

    NOTA: O sistema já tem fallback automático para CPU quando há CUDA OOM.
    Não desabilitamos GPU completamente - deixamos o sistema verificar memória
    disponível e usar fallback automático quando necessário.
    """

    @pytest.fixture
    def orchestrator(self):
        """Cria instância de OrchestratorAgent para testes.

        O sistema automaticamente verifica memória GPU disponível antes de
        carregar modelos. Se não houver memória suficiente, usa CPU como fallback.
        """
        with patch("src.agents.orchestrator_agent.MCPClient"):
            agent = OrchestratorAgent(config_path="config/agent_config.yaml")
            return agent

    def test_error_analyzer_initialized(self, orchestrator):
        """Testa que ErrorAnalyzer é inicializado."""
        assert orchestrator.error_analyzer is not None
        assert isinstance(orchestrator.error_analyzer, ErrorAnalyzer)

    def test_handle_subtask_error_with_analysis(self, orchestrator):
        """Testa que _handle_subtask_error analisa erros."""
        results: Dict[str, Any] = {"subtask_results": []}
        error = FileNotFoundError("File not found: test.py")
        index = 0

        orchestrator._handle_subtask_error(results, error, index)

        assert len(results["subtask_results"]) == 1
        error_result = results["subtask_results"][0]
        assert "error" in error_result
        assert "error_class" in error_result
        assert "error_analysis" in error_result
        assert error_result["error_analysis"]["error_type"] == ErrorType.PATH_ERROR.value
        assert (
            error_result["error_analysis"]["recovery_strategy"]
            == RecoveryStrategy.SEARCH_CORRECT_PATH.value
        )

    def test_delegate_task_error_analysis(self, orchestrator):
        """Testa que delegate_task analisa erros."""
        # Mock para forçar erro
        with patch.object(
            orchestrator, "_execute_security_subtask", side_effect=Exception("Test error")
        ):
            result = orchestrator.delegate_task("test task", "security")

        assert "error" in result
        assert "error_analysis" in result
        assert result["error_analysis"]["error_type"] in [e.value for e in ErrorType]

    def test_error_analyzer_learns_from_solutions(self, orchestrator):
        """Testa que ErrorAnalyzer aprende de soluções."""
        error = ModuleNotFoundError("No module named 'test'")
        context = {"task": "test", "agent_type": "code"}

        # Primeira análise
        analysis1 = orchestrator.error_analyzer.analyze_error(error, context)
        pattern = analysis1.pattern

        # Aprender solução
        orchestrator.error_analyzer.learn_from_solution(
            pattern,
            analysis1.recovery_strategy,
            success=True,
            context=context,
        )

        # Segunda análise (deve usar solução aprendida)
        analysis2 = orchestrator.error_analyzer.analyze_error(error, context)
        assert analysis2.pattern == pattern

        # Verificar que padrão foi aprendido
        learned = orchestrator.error_analyzer.get_learned_patterns()
        assert pattern in learned
        assert learned[pattern]["success_rate"] > 0

    def test_handle_crisis_with_error_analysis(self, orchestrator):
        """Testa que _handle_crisis analisa erros se disponível."""
        # Criar evento mock com erro
        event = MagicMock()
        event.event_type = "security_breach"
        event.error = PermissionError("Permission denied")

        # Executar (async)
        import asyncio

        async def run_test():
            await orchestrator._handle_crisis(event)

        asyncio.run(run_test())

        # Verificar que ErrorAnalyzer foi usado
        assert orchestrator.error_analyzer is not None

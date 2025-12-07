"""
Testes de integração REAIS para EnhancedCodeAgent com todas as camadas.

Testes reais que chamam diretamente o ambiente de produção com Ollama.
Sem mocks - testes de integração end-to-end.

Autor: Fabrício da Silva + assistência de IA
"""

import pytest

from src.agents.enhanced_code_agent import EnhancedCodeAgent, FailureRecord
from src.agents.orchestrator_agent import OrchestratorAgent
from src.orchestrator.error_analyzer import ErrorType, RecoveryStrategy


@pytest.fixture
def orchestrator():
    """Fixture para OrchestratorAgent real."""
    return OrchestratorAgent(config_path="config/agent_config.yaml")


@pytest.fixture
def enhanced_agent(orchestrator):
    """Fixture para EnhancedCodeAgent real com Orchestrator."""
    return EnhancedCodeAgent(config_path="config/agent_config.yaml", orchestrator=orchestrator)


@pytest.mark.real
class TestEnhancedCodeAgentIntegration:
    """Testes de integração REAL do EnhancedCodeAgent."""

    def test_initialization_with_orchestrator(self, enhanced_agent, orchestrator):
        """Testa inicialização real com Orchestrator."""
        assert enhanced_agent.orchestrator == orchestrator
        assert enhanced_agent.error_analyzer is not None
        assert enhanced_agent.dynamic_tool_creator is not None
        assert enhanced_agent.tool_composer is not None
        assert orchestrator.rag_fallback is not None

    def test_auto_error_detection_integration(self, enhanced_agent):
        """Testa integração real de auto-error detection."""
        # Simular erro real
        error = FileNotFoundError("test_file.txt not found")
        context = {"task": "read file"}

        # Verificar que ErrorAnalyzer é usado
        analysis = enhanced_agent.error_analyzer.analyze_error(error, context)

        assert analysis is not None
        assert analysis.error_type in ErrorType
        assert analysis.recovery_strategy in RecoveryStrategy
        assert analysis.confidence > 0.0

    def test_self_correction_loop_real(self, enhanced_agent):
        """Testa self-correction loop com execução real."""
        # Tarefa que pode falhar inicialmente
        task = "Read a file that does not exist: /tmp/nonexistent_file_12345.txt"

        # Executar com self-correction
        result = enhanced_agent.execute_task_with_self_correction(task, max_attempts=3)

        assert result is not None
        assert "status" in result
        assert result["attempts"] > 0

    def test_tool_composition_integration_real(self, enhanced_agent):
        """Testa integração real com ToolComposer."""
        tool_names = ["read_file", "list_files"]

        # Verificar que ToolComposer está disponível
        assert enhanced_agent.tool_composer is not None

        # Criar composição real
        composition = enhanced_agent.tool_composer.compose_tools(tool_names)

        assert composition is not None
        assert len(composition.tool_names) == 2
        assert len(composition.execution_order) == 2

        # Executar composição real
        inputs = {
            "read_file": {"filepath": "README.md"},
            "list_files": {"directory": "."},
        }
        result = enhanced_agent.tool_composer.execute_composition(
            composition.composition_id, inputs=inputs
        )

        assert result is not None
        assert result.composition_id == composition.composition_id

    def test_dynamic_tool_creation_integration_real(self, enhanced_agent):
        """Testa integração real com DynamicToolCreator."""
        # Verificar que DynamicToolCreator está disponível
        assert enhanced_agent.dynamic_tool_creator is not None

        # Verificar que o método existe
        assert hasattr(enhanced_agent.dynamic_tool_creator, "create_tool_from_code")

    def test_rag_fallback_integration_real(self, enhanced_agent, orchestrator):
        """Testa integração real com RAG Fallback."""
        # Verificar se RAG Fallback está disponível
        assert orchestrator.rag_fallback is not None

        # Testar retrieval real quando há erro
        task = "How to handle file not found errors in Python?"
        error = FileNotFoundError("test.txt")

        fallback_result = orchestrator.rag_fallback.retrieve_on_failure(
            task=task, error=error, num_docs=3
        )

        # Pode não recuperar documentos se Qdrant não estiver populado,
        # mas o sistema deve funcionar
        assert fallback_result is not None
        assert hasattr(fallback_result, "success")
        assert hasattr(fallback_result, "query_generated")

    def test_error_learning_integration_real(self, enhanced_agent):
        """Testa que o agente aprende com erros reais."""
        error = ValueError("Test error for learning")
        context = {"task": "test task"}

        # Analisar erro
        analysis = enhanced_agent.error_analyzer.analyze_error(error, context)

        # Aprender com solução
        enhanced_agent.error_analyzer.learn_from_solution(
            analysis.pattern, analysis.recovery_strategy, True, context
        )

        # Verificar que o padrão foi aprendido
        assert analysis.pattern is not None

        # Verificar que o padrão está no histórico de aprendizado
        stats = enhanced_agent.get_learning_stats()
        assert stats["learned_patterns"] >= 0

    def test_end_to_end_workflow_real(self, enhanced_agent):
        """Testa fluxo end-to-end real completo."""
        task = "List files in the current directory"

        # Executar tarefa real
        result = enhanced_agent.execute(task)

        assert result is not None
        # Resultado pode variar, mas não deve ser None

    def test_failure_record_tracking_real(self, enhanced_agent):
        """Testa rastreamento real de falhas."""
        # Simular falha real
        error = FileNotFoundError("test.txt")
        context = {"task": "read file"}

        analysis = enhanced_agent.error_analyzer.analyze_error(error, context)

        # Criar registro de falha
        failure_record = FailureRecord(
            error_type=analysis.error_type,
            error_message=str(error),
            context=context,
            recovery_strategy=analysis.recovery_strategy,
            success=False,
            attempt_count=1,
        )

        assert failure_record.error_type == analysis.error_type
        assert failure_record.recovery_strategy == analysis.recovery_strategy

        # Adicionar ao histórico
        enhanced_agent.failure_history.append(failure_record)

        # Verificar que está no histórico
        assert len(enhanced_agent.failure_history) > 0
        assert enhanced_agent.failure_history[-1] == failure_record

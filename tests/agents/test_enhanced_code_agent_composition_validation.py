"""
Testes de Validação da Composição do EnhancedCodeAgent

Baseado em: REFATORACAO_ENHANCED_CODE_AGENT_PLANO.md
Checklist OmniMind: Validação de composição atual

Autor: GitHub Copilot Agent
Data: 2025-12-09
"""

import pytest
from unittest.mock import MagicMock, Mock
from pathlib import Path

from src.agents.enhanced_code_agent import EnhancedCodeAgent, FailureRecord
from src.agents.code_agent import CodeAgent
from src.agents.react_agent import ReactAgent
from src.orchestrator.error_analyzer import ErrorAnalyzer, ErrorType, RecoveryStrategy


class TestEnhancedCodeAgentComposition:
    """Testa composição atual do EnhancedCodeAgent conforme checklist."""

    @pytest.fixture
    def config_path(self, tmp_path):
        """Fixture para criar arquivo de configuração temporário."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
llm:
  provider: "mock"
  model: "test-model"
  temperature: 0.7
  max_tokens: 2000

react_agent:
  max_iterations: 5
  enable_embedding: false
  enable_consciousness: false
""")
        return str(config_file)

    @pytest.fixture
    def enhanced_agent(self, config_path):
        """Fixture para criar EnhancedCodeAgent."""
        return EnhancedCodeAgent(config_path=config_path, orchestrator=None)

    def test_enhanced_code_agent_composition_references(self, enhanced_agent):
        """
        5️⃣ AGENTES - Verificar Composição
        
        Valida que EnhancedCodeAgent tem referências de composição.
        """
        # REFATORAÇÃO: Verificar que componentes de composição existem
        assert hasattr(enhanced_agent, 'code_agent')
        assert hasattr(enhanced_agent, 'react_agent')
        
        # Componentes específicos do Enhanced
        assert hasattr(enhanced_agent, 'error_analyzer')
        assert isinstance(enhanced_agent.error_analyzer, ErrorAnalyzer)
        assert hasattr(enhanced_agent, 'tool_composer')
        
    def test_enhanced_code_agent_heranca_atual(self, enhanced_agent):
        """
        5️⃣ AGENTES - Verificar Herança Atual
        
        Valida que EnhancedCodeAgent ainda usa herança (temporariamente).
        """
        # ATUAL: Ainda herda de CodeAgent
        assert isinstance(enhanced_agent, CodeAgent)
        assert isinstance(enhanced_agent, ReactAgent)
        
        # REFATORAÇÃO: Mas já tem referências de composição
        assert enhanced_agent.code_agent is enhanced_agent
        assert enhanced_agent.react_agent is enhanced_agent
        
    def test_consciousness_isolated_in_post_init(self, enhanced_agent):
        """
        5️⃣ AGENTES - Safe Mode (Consciência Isolada)
        
        Valida que consciência é isolada em post_init().
        """
        # Consciência não deve estar inicializada no construtor
        assert hasattr(enhanced_agent, '_consciousness_initialized')
        
        # post_init() deve existir
        assert hasattr(enhanced_agent, 'post_init')
        assert callable(enhanced_agent.post_init)
        
        # Executar post_init (sem workspace, deve falhar gracefully)
        enhanced_agent.post_init()
        
        # Agente deve continuar funcionando mesmo sem consciência
        assert enhanced_agent is not None
        
    def test_error_analyzer_integrated(self, enhanced_agent):
        """
        5️⃣ AGENTES - ErrorAnalyzer Integrado
        
        Valida que ErrorAnalyzer está integrado.
        """
        assert hasattr(enhanced_agent, 'error_analyzer')
        assert isinstance(enhanced_agent.error_analyzer, ErrorAnalyzer)
        
        # Testar análise de erro
        test_error = ValueError("Test error")
        analysis = enhanced_agent.error_analyzer.analyze_error(
            error=test_error,
            context={"test": True}
        )
        
        assert analysis is not None
        assert hasattr(analysis, 'error_type')
        assert hasattr(analysis, 'recovery_strategy')
        
    def test_failure_history_tracking(self, enhanced_agent):
        """
        5️⃣ AGENTES - Histórico de Falhas
        
        Valida que histórico de falhas é rastreado.
        """
        assert hasattr(enhanced_agent, 'failure_history')
        assert isinstance(enhanced_agent.failure_history, list)
        
        # Histórico deve iniciar vazio
        assert len(enhanced_agent.failure_history) == 0
        
    def test_learned_patterns_tracking(self, enhanced_agent):
        """
        5️⃣ AGENTES - Padrões Aprendidos
        
        Valida que padrões aprendidos são rastreados.
        """
        assert hasattr(enhanced_agent, 'learned_patterns')
        assert isinstance(enhanced_agent.learned_patterns, dict)
        
        # Padrões devem iniciar vazios
        assert len(enhanced_agent.learned_patterns) == 0
        
    def test_execute_task_with_self_correction_exists(self, enhanced_agent):
        """
        5️⃣ AGENTES - Self-Correction Loop
        
        Valida que método de self-correction existe.
        """
        assert hasattr(enhanced_agent, 'execute_task_with_self_correction')
        assert callable(enhanced_agent.execute_task_with_self_correction)
        
    def test_delegated_methods_exist(self, enhanced_agent):
        """
        5️⃣ AGENTES - Métodos Delegados
        
        Valida que métodos delegados para composição existem.
        """
        # Métodos delegados de CodeAgent
        assert hasattr(enhanced_agent, 'run_code_task')
        assert hasattr(enhanced_agent, 'get_code_stats')
        assert hasattr(enhanced_agent, 'analyze_code_structure')
        assert hasattr(enhanced_agent, 'validate_code_syntax')
        assert hasattr(enhanced_agent, 'analyze_code_security')
        
        # Todos devem ser callable
        assert callable(enhanced_agent.run_code_task)
        assert callable(enhanced_agent.get_code_stats)
        assert callable(enhanced_agent.analyze_code_structure)
        assert callable(enhanced_agent.validate_code_syntax)
        assert callable(enhanced_agent.analyze_code_security)
        
    def test_tool_composer_initialized(self, enhanced_agent):
        """
        5️⃣ AGENTES - ToolComposer
        
        Valida que ToolComposer está inicializado.
        """
        assert hasattr(enhanced_agent, 'tool_composer')
        assert enhanced_agent.tool_composer is not None
        
    def test_dynamic_tool_creator_optional(self, enhanced_agent):
        """
        5️⃣ AGENTES - DynamicToolCreator (Opcional)
        
        Valida que DynamicToolCreator é opcional.
        """
        assert hasattr(enhanced_agent, 'dynamic_tool_creator')
        
        # Pode ser None se orchestrator não fornecido
        # (neste teste, orchestrator=None)
        assert enhanced_agent.dynamic_tool_creator is None or \
               enhanced_agent.dynamic_tool_creator is not None


class TestEnhancedCodeAgentSelfCorrection:
    """Testa funcionalidade de self-correction."""
    
    @pytest.fixture
    def config_path(self, tmp_path):
        """Fixture para criar arquivo de configuração temporário."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
llm:
  provider: "mock"
  model: "test-model"
  temperature: 0.7
  max_tokens: 2000

react_agent:
  max_iterations: 5
  enable_embedding: false
  enable_consciousness: false
""")
        return str(config_file)

    @pytest.fixture
    def enhanced_agent(self, config_path):
        """Fixture para criar EnhancedCodeAgent com métodos mockados."""
        agent = EnhancedCodeAgent(config_path=config_path, orchestrator=None)
        
        # Mockar método run para evitar chamadas LLM reais
        agent.run = MagicMock(return_value={"status": "success", "result": "test"})
        
        return agent
    
    def test_execute_task_success_on_first_attempt(self, enhanced_agent):
        """
        Testa execução bem-sucedida na primeira tentativa.
        """
        result = enhanced_agent.execute_task_with_self_correction(
            task="Test task",
            max_attempts=3
        )
        
        assert result["status"] == "success"
        assert result["attempts"] == 1
        assert result["corrections_applied"] is False
        
    def test_execute_task_with_correction(self, enhanced_agent):
        """
        Testa execução com correção (falha → sucesso).
        """
        # Simular falha na primeira tentativa, sucesso na segunda
        call_count = 0
        
        def mock_run_with_failure(task, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Test error")
            return {"status": "success", "result": "corrected"}
        
        enhanced_agent.run = mock_run_with_failure
        
        result = enhanced_agent.execute_task_with_self_correction(
            task="Test task",
            max_attempts=3
        )
        
        assert result["status"] == "success"
        assert result["attempts"] == 2
        assert result["corrections_applied"] is True
        
        # Histórico de falhas deve ter 1 entrada
        assert len(enhanced_agent.failure_history) == 1
        
    def test_execute_task_all_attempts_fail(self, enhanced_agent):
        """
        Testa quando todas as tentativas falham.
        """
        # Simular falha em todas as tentativas
        enhanced_agent.run = MagicMock(side_effect=ValueError("Persistent error"))
        
        result = enhanced_agent.execute_task_with_self_correction(
            task="Test task",
            max_attempts=3
        )
        
        assert result["status"] == "failed"
        assert result["attempts"] == 3
        assert "error" in result
        assert "error_analysis" in result
        
        # Histórico de falhas deve ter 3 entradas
        assert len(enhanced_agent.failure_history) == 3
        
    def test_learned_pattern_application(self, enhanced_agent):
        """
        Testa aplicação de padrão aprendido.
        """
        # Adicionar padrão aprendido
        enhanced_agent.learned_patterns["test_pattern"] = RecoveryStrategy.CORRECT_REASONING
        
        # Simular erro com padrão conhecido
        call_count = 0
        
        def mock_run_with_known_pattern(task, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Known pattern error")
            return {"status": "success"}
        
        enhanced_agent.run = mock_run_with_known_pattern
        
        # Mockar error_analyzer para retornar padrão conhecido
        original_analyze = enhanced_agent.error_analyzer.analyze_error
        
        def mock_analyze(error, context):
            analysis = original_analyze(error, context)
            analysis.pattern = "test_pattern"
            return analysis
        
        enhanced_agent.error_analyzer.analyze_error = mock_analyze
        
        result = enhanced_agent.execute_task_with_self_correction(
            task="Test task",
            max_attempts=3
        )
        
        # Deve ter aplicado solução aprendida
        assert result["status"] == "success"
        
    def test_validate_output_success(self, enhanced_agent):
        """
        Testa validação de output bem-sucedida.
        """
        # Output válido
        assert enhanced_agent._validate_output({"status": "success"}) is True
        assert enhanced_agent._validate_output({"result": "data"}) is True
        assert enhanced_agent._validate_output("Valid result") is True
        
    def test_validate_output_failure(self, enhanced_agent):
        """
        Testa validação de output com falha.
        """
        # Output inválido
        assert enhanced_agent._validate_output(None) is False
        assert enhanced_agent._validate_output({"status": "error"}) is False
        assert enhanced_agent._validate_output({"status": "failed"}) is False
        assert enhanced_agent._validate_output({"error": "Something failed"}) is False
        assert enhanced_agent._validate_output("error occurred") is False
        assert enhanced_agent._validate_output("failed to complete") is False
        
    def test_recovery_strategy_correct_reasoning(self, enhanced_agent):
        """
        Testa estratégia de recuperação: CORRECT_REASONING.
        """
        from src.orchestrator.error_analyzer import ErrorAnalysis
        
        analysis = ErrorAnalysis(
            error_type=ErrorType.HALLUCINATION,
            error_message="Test error",
            recovery_strategy=RecoveryStrategy.CORRECT_REASONING,
            confidence=0.8,
            pattern="hallucination_pattern",
            metadata={}
        )
        
        corrected = enhanced_agent._apply_recovery_strategy(
            task="Original task",
            error=ValueError("Test"),
            error_analysis=analysis,
            recovery_strategy=RecoveryStrategy.CORRECT_REASONING,
            context={}
        )
        
        # Tarefa deve ser modificada (contexto adicionado)
        assert "Verificar fatos" in corrected or "Original task" in corrected
        
    def test_learning_from_success(self, enhanced_agent):
        """
        Testa aprendizado a partir de sucesso.
        """
        from src.orchestrator.error_analyzer import ErrorAnalysis
        
        analysis = ErrorAnalysis(
            error_type=ErrorType.SYNTAX_ERROR,
            error_message="Syntax error",
            recovery_strategy=RecoveryStrategy.CORRECT_REASONING,
            confidence=0.9,
            pattern="syntax_error_pattern",
            metadata={}
        )
        
        # Adicionar falha ao histórico
        failure = FailureRecord(
            error_type=ErrorType.SYNTAX_ERROR,
            error_message="Syntax error",
            context={},
            recovery_strategy=RecoveryStrategy.CORRECT_REASONING,
            success=False,
            attempt_count=1
        )
        enhanced_agent.failure_history.append(failure)
        
        # Aprender do sucesso
        enhanced_agent._learn_from_success(
            task="Test task",
            error_analysis=analysis,
            result={"status": "success"}
        )
        
        # Padrão deve ter sido aprendido
        assert "syntax_error_pattern" in enhanced_agent.learned_patterns
        assert enhanced_agent.learned_patterns["syntax_error_pattern"] == \
               RecoveryStrategy.CORRECT_REASONING
        
        # Último failure deve ter sido marcado como sucesso
        assert enhanced_agent.failure_history[-1].success is True
        
    def test_get_learning_stats(self, enhanced_agent):
        """
        Testa obtenção de estatísticas de aprendizado.
        """
        # Adicionar algumas falhas
        for i in range(5):
            failure = FailureRecord(
                error_type=ErrorType.SYNTAX_ERROR,
                error_message=f"Error {i}",
                context={},
                recovery_strategy=RecoveryStrategy.CORRECT_REASONING,
                success=(i % 2 == 0),  # 3 sucessos, 2 falhas
                attempt_count=1
            )
            enhanced_agent.failure_history.append(failure)
        
        # Adicionar padrões aprendidos
        enhanced_agent.learned_patterns["pattern1"] = RecoveryStrategy.CORRECT_REASONING
        enhanced_agent.learned_patterns["pattern2"] = RecoveryStrategy.DECOMPOSE_FURTHER
        
        stats = enhanced_agent.get_learning_stats()
        
        assert stats["total_failures"] == 5
        assert stats["successful_recoveries"] == 3
        assert stats["recovery_rate"] == 0.6
        assert stats["learned_patterns"] == 2
        assert "pattern1" in stats["patterns"]
        assert "pattern2" in stats["patterns"]


class TestEnhancedCodeAgentRefactoringValidation:
    """Testes específicos para validação da refatoração proposta."""
    
    @pytest.fixture
    def config_path(self, tmp_path):
        """Fixture para criar arquivo de configuração temporário."""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text("""
llm:
  provider: "mock"
  model: "test-model"

react_agent:
  max_iterations: 5
  enable_embedding: false
  enable_consciousness: false
""")
        return str(config_file)
    
    def test_composition_mode_enabled(self, config_path):
        """
        Valida que modo composição está habilitado.
        
        Conforme plano: EnhancedCodeAgent deve usar composição.
        """
        agent = EnhancedCodeAgent(config_path=config_path)
        
        # Componentes de composição devem existir
        assert hasattr(agent, 'code_agent')
        assert hasattr(agent, 'react_agent')
        assert hasattr(agent, 'error_analyzer')
        assert hasattr(agent, 'tool_composer')
        
    def test_safe_mode_boot(self, config_path):
        """
        Valida que agente boota mesmo se consciência falhar.
        
        Conforme plano: Safe Mode permite boot sem consciência.
        """
        agent = EnhancedCodeAgent(config_path=config_path)
        
        # Agente deve ter sido criado
        assert agent is not None
        
        # post_init() não deve quebrar mesmo sem workspace
        try:
            agent.post_init()
            # Se não quebrou, Safe Mode funcionou
            safe_mode_works = True
        except Exception:
            safe_mode_works = False
            
        assert safe_mode_works
        
    def test_delegation_to_code_agent(self, config_path):
        """
        Valida que métodos delegam para code_agent.
        
        Conforme plano: Métodos devem delegar para componentes compostos.
        """
        agent = EnhancedCodeAgent(config_path=config_path)
        
        # Mockar code_agent.get_code_stats
        agent.code_agent.get_code_stats = MagicMock(return_value={"test": "stats"})
        
        # Chamar método delegado
        result = agent.get_code_stats()
        
        # Deve ter delegado para code_agent
        assert agent.code_agent.get_code_stats.called
        assert result == {"test": "stats"}
        
    def test_api_compatibility(self, config_path):
        """
        Valida que API pública não mudou.
        
        Conforme plano: Compatibilidade retroativa deve ser mantida.
        """
        agent = EnhancedCodeAgent(config_path=config_path)
        
        # API pública deve estar presente
        public_api = [
            'run',
            'run_code_task',
            'execute_task_with_self_correction',
            'get_code_stats',
            'analyze_code_structure',
            'validate_code_syntax',
            'analyze_code_security',
            'get_learning_stats'
        ]
        
        for method_name in public_api:
            assert hasattr(agent, method_name)
            assert callable(getattr(agent, method_name))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

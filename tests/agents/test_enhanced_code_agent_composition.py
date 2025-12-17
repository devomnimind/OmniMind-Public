"""
Testes para refatoração de composição do EnhancedCodeAgent.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

from unittest.mock import MagicMock, patch

import pytest

from src.agents.enhanced_code_agent import EnhancedCodeAgent


class TestEnhancedCodeAgentComposition:
    """Testes para verificar composição completa do EnhancedCodeAgent."""

    @pytest.fixture
    def enhanced_agent(self):
        """Fixture para EnhancedCodeAgent."""
        with patch("src.agents.code_agent.CodeAgent.__init__"):
            agent = EnhancedCodeAgent(config_path="config/test_config.yaml")
            return agent

    def test_composition_components_exist(self, enhanced_agent):
        """Testa que componentes compostos existem."""
        # REFATORAÇÃO: Verificar que componentes são compostos (não herdados)
        assert hasattr(enhanced_agent, "code_agent")
        assert hasattr(enhanced_agent, "react_agent")
        assert enhanced_agent.code_agent is not None
        assert enhanced_agent.react_agent is not None

    def test_consciousness_initialization_flag(self, enhanced_agent):
        """Testa flag de inicialização de consciência."""
        # REFATORAÇÃO: Verificar que consciência não é inicializada no construtor
        assert hasattr(enhanced_agent, "_consciousness_initialized")
        assert enhanced_agent._consciousness_initialized is False

    def test_post_init_method_exists(self, enhanced_agent):
        """Testa que método post_init() existe."""
        # REFATORAÇÃO: Verificar que método post_init() existe
        assert hasattr(enhanced_agent, "post_init")
        assert callable(enhanced_agent.post_init)

    def test_post_init_safe_mode(self, enhanced_agent):
        """Testa que post_init() funciona em safe mode (não quebra se consciência falhar)."""
        # REFATORAÇÃO: Verificar que agente boota mesmo se consciência falhar
        # Simular workspace None diretamente
        original_workspace = getattr(enhanced_agent.react_agent, "workspace", None)
        enhanced_agent.react_agent.workspace = None

        try:
            # Não deve quebrar
            enhanced_agent.post_init()
            # Flag deve permanecer False se workspace não existir
            assert enhanced_agent._consciousness_initialized is False
        finally:
            # Restaurar workspace original
            enhanced_agent.react_agent.workspace = original_workspace

    def test_delegation_run_code_task(self, enhanced_agent):
        """Testa delegação de run_code_task()."""
        # REFATORAÇÃO: Verificar que delegação funciona
        mock_result = {"status": "success", "result": "test"}
        enhanced_agent.code_agent.run_code_task = MagicMock(return_value=mock_result)

        result = enhanced_agent.run_code_task("test task")

        assert result == mock_result
        enhanced_agent.code_agent.run_code_task.assert_called_once_with("test task")

    def test_delegation_get_code_stats(self, enhanced_agent):
        """Testa delegação de get_code_stats()."""
        # REFATORAÇÃO: Verificar que delegação funciona
        mock_stats = {"total_operations": 10}
        enhanced_agent.code_agent.get_code_stats = MagicMock(return_value=mock_stats)

        stats = enhanced_agent.get_code_stats()

        assert stats == mock_stats
        enhanced_agent.code_agent.get_code_stats.assert_called_once()

    def test_delegation_analyze_code_structure(self, enhanced_agent):
        """Testa delegação de analyze_code_structure()."""
        # REFATORAÇÃO: Verificar que delegação funciona
        from typing import Any, Dict, List

        mock_analysis: Dict[str, List[Any]] = {"classes": [], "functions": []}
        enhanced_agent.code_agent.analyze_code_structure = MagicMock(return_value=mock_analysis)

        analysis = enhanced_agent.analyze_code_structure("test.py")

        assert analysis == mock_analysis
        enhanced_agent.code_agent.analyze_code_structure.assert_called_once_with("test.py")

    def test_api_compatibility(self, enhanced_agent):
        """Testa que API pública não mudou."""
        # REFATORAÇÃO: Verificar compatibilidade retroativa
        # Métodos públicos devem existir
        assert hasattr(enhanced_agent, "run")
        assert hasattr(enhanced_agent, "execute_task_with_self_correction")
        assert hasattr(enhanced_agent, "run_code_task")
        assert hasattr(enhanced_agent, "get_code_stats")
        assert hasattr(enhanced_agent, "analyze_code_structure")
        assert hasattr(enhanced_agent, "validate_code_syntax")
        assert hasattr(enhanced_agent, "analyze_code_security")

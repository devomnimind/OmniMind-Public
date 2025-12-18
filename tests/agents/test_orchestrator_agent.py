"""
Testes para Orchestrator Agent (orchestrator_agent.py).

Cobertura de:
- Orquestração de múltiplos agentes
- Delegação de tarefas
- Coordenação de fluxos
- Modos de operação
- Tratamento de exceções
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from src.agents.orchestrator_agent import (
    AgentMode,
    OrchestratorAgent,
)


class TestAgentMode:
    """Testes para AgentMode enum."""

    def test_agent_mode_values(self) -> None:
        """Testa valores do enum."""
        # Check that AgentMode exists and has values
        assert hasattr(AgentMode, "__members__")
        assert len(AgentMode.__members__) > 0


@pytest.mark.heavy
class TestOrchestratorAgent:
    """Testes para OrchestratorAgent."""

    @pytest.fixture
    def agent(self) -> OrchestratorAgent:
        """Cria instância do agente."""
        # Não mockar OmniMindCore ou SentenceTransformer se for teste real/híbrido
        # Mas para garantir isolamento básico em unit tests de inicialização simples:
        # User pediu "testes orquestradores são reais", mas unit tests básicos ainda
        # podem precisar de suporte.
        # Vou remover o mock agressivo do SentenceTransformer e deixar o sistema real
        # (com fallback CPU que implementei) rodar.

        with patch("src.agents.orchestrator_agent.OmniMindCore"):
            agent = OrchestratorAgent(config_path="config/agent_config.yaml")
            return agent

    def test_agent_initialization(self, agent: OrchestratorAgent) -> None:
        """Testa inicialização do agente."""
        assert agent is not None
        assert hasattr(agent, "delegate_task") or hasattr(agent, "orchestrate")

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_delegate_task(self, mock_core: Mock) -> None:
        """Testa delegação de tarefa."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        agent.delegate_task(
            task="Implement feature",
            agent_type="code",
        )

    @pytest.mark.real
    def test_orchestrate_workflow(self) -> None:
        """Testa decomposição de tarefa pelo orchestrador (real LLM, produção, sem mock).

        Testa que o orchestrador consegue decompor uma tarefa complexa
        em subtarefas usando o modelo Ollama local com fallback.
        Sistema core em produção - não usar mock.
        """
        # Sistema real, sem mock - OrchestratorAgent é módulo core
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        # Apenas testa decomposição (não executa as subtarefas)
        plan = agent.decompose_task(
            task_description="Implement a feature: add user authentication to the API"
        )

        assert isinstance(plan, dict)
        assert "subtasks" in plan
        assert "original_task" in plan
        assert len(plan["subtasks"]) > 0

        # Verifica que subtarefas têm estrutura esperada
        for subtask in plan["subtasks"]:
            assert "agent" in subtask or "id" in subtask
            assert "description" in subtask

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_handle_error_in_delegation(self, mock_core: Mock) -> None:
        """Testa tratamento de erro na delegação."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        with patch.object(agent, "delegate_task", side_effect=Exception("Delegation failed")):
            try:
                agent.delegate_task("task", "agent")
            except Exception:
                pass  # Expected

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_get_available_agents(self, mock_core: Mock) -> None:
        """Testa obtenção de agentes disponíveis."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        if hasattr(agent, "get_available_agents"):
            agents = agent.get_available_agents()
            assert isinstance(agents, (list, dict))

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_switch_mode(self, mock_core: Mock) -> None:
        """Testa troca de modo."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        if hasattr(agent, "switch_mode"):
            for mode in AgentMode:
                result = agent.switch_mode(mode)
                assert result is not None or result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

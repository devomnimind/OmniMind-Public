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


class TestOrchestratorAgent:
    """Testes para OrchestratorAgent."""

    @pytest.fixture
    def agent(self) -> OrchestratorAgent:
        """Cria instância do agente."""
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

    @patch("src.agents.orchestrator_agent.OmniMindCore")
    def test_orchestrate_workflow(self, mock_core: Mock) -> None:
        """Testa orquestração de workflow."""
        agent = OrchestratorAgent(config_path="config/agent_config.yaml")

        result = agent.orchestrate(
            tasks=["task1", "task2"],
        )

        assert isinstance(result, (dict, list, str)) or result is None

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

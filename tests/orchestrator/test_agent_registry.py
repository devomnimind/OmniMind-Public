"""
Testes para AgentRegistry.

Cobertura de:
- Registro de agentes
- Health checks
- Priorização
- Fallbacks
"""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from src.orchestrator.agent_registry import AgentPriority, AgentRegistry


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, name: str, healthy: bool = True):
        self.name = name
        self._healthy = healthy

    async def health_check(self) -> bool:
        """Mock health check."""
        return self._healthy


class TestAgentPriority:
    """Testes para AgentPriority enum."""

    def test_priority_values(self) -> None:
        """Testa valores de prioridade."""
        assert AgentPriority.CRITICAL.value == 0
        assert AgentPriority.ESSENTIAL.value == 1
        assert AgentPriority.OPTIONAL.value == 2


class TestAgentRegistry:
    """Testes para AgentRegistry."""

    @pytest.fixture
    def registry(self) -> AgentRegistry:
        """Cria instância do registro."""
        return AgentRegistry()

    def test_registry_initialization(self, registry: AgentRegistry) -> None:
        """Testa inicialização do registro."""
        assert registry is not None
        assert len(registry.list_agents()) == 0

    def test_register_agent(self, registry: AgentRegistry) -> None:
        """Testa registro de agente."""
        agent = MockAgent("test_agent")
        registry.register_agent("test", agent, AgentPriority.OPTIONAL)

        assert "test" in registry.list_agents()
        assert registry.get_agent("test") is agent

    def test_get_nonexistent_agent(self, registry: AgentRegistry) -> None:
        """Testa obtenção de agente inexistente."""
        agent = registry.get_agent("nonexistent")
        assert agent is None

    def test_register_multiple_agents(self, registry: AgentRegistry) -> None:
        """Testa registro de múltiplos agentes."""
        agent1 = MockAgent("agent1")
        agent2 = MockAgent("agent2")

        registry.register_agent("agent1", agent1, AgentPriority.CRITICAL)
        registry.register_agent("agent2", agent2, AgentPriority.OPTIONAL)

        assert len(registry.list_agents()) == 2
        assert registry.get_priority("agent1") == AgentPriority.CRITICAL
        assert registry.get_priority("agent2") == AgentPriority.OPTIONAL

    @pytest.mark.asyncio
    async def test_health_check_all(self, registry: AgentRegistry) -> None:
        """Testa health check de todos os agentes."""
        healthy_agent = MockAgent("healthy", healthy=True)
        unhealthy_agent = MockAgent("unhealthy", healthy=False)

        registry.register_agent("healthy", healthy_agent)
        registry.register_agent("unhealthy", unhealthy_agent)

        results = await registry.health_check_all()

        assert results["healthy"] is True
        assert results["unhealthy"] is False

    @pytest.mark.asyncio
    async def test_health_check_single(self, registry: AgentRegistry) -> None:
        """Testa health check de um único agente."""
        agent = MockAgent("test", healthy=True)
        registry.register_agent("test", agent)

        is_healthy = await registry.health_check_single("test")
        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_health_check_single_nonexistent(self, registry: AgentRegistry) -> None:
        """Testa health check de agente inexistente."""
        is_healthy = await registry.health_check_single("nonexistent")
        assert is_healthy is False

    @pytest.mark.asyncio
    async def test_health_check_updates_status(self, registry: AgentRegistry) -> None:
        """Testa que health check atualiza status."""
        agent = MockAgent("test", healthy=True)
        registry.register_agent("test", agent)

        # Primeiro check - deve estar saudável
        await registry.health_check_single("test")
        assert registry.is_agent_healthy("test") is True

        # Mudar estado do agente
        agent._healthy = False

        # Segundo check - deve estar não saudável
        await registry.health_check_single("test")
        assert registry.is_agent_healthy("test") is False

    def test_get_health_summary(self, registry: AgentRegistry) -> None:
        """Testa obtenção de resumo de saúde."""
        agent = MockAgent("test")
        registry.register_agent("test", agent)

        summary = registry.get_health_summary()

        assert "test" in summary
        assert summary["test"]["healthy"] is True
        assert "failure_count" in summary["test"]

    def test_list_agents(self, registry: AgentRegistry) -> None:
        """Testa listagem de agentes."""
        registry.register_agent("agent1", MockAgent("agent1"))
        registry.register_agent("agent2", MockAgent("agent2"))

        agents = registry.list_agents()

        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents

    @pytest.mark.asyncio
    async def test_shutdown_all(self, registry: AgentRegistry) -> None:
        """Testa shutdown de todos os agentes."""
        agent = Mock()
        agent.shutdown = AsyncMock()

        registry.register_agent("test", agent)

        await registry.shutdown_all()

        agent.shutdown.assert_called_once()
        assert len(registry.list_agents()) == 0

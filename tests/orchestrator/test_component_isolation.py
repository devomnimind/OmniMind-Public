"""
Testes para ComponentIsolation.

Testa sistema de isolamento de componentes comprometidos.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator.component_isolation import ComponentIsolation, IsolationLevel


@pytest.fixture
def mock_orchestrator():
    """Cria mock do OrchestratorAgent."""
    orchestrator = MagicMock()
    orchestrator.agent_registry = MagicMock()
    orchestrator.agent_registry.list_agents.return_value = [
        "security",
        "metacognition",
        "code",
        "architect",
    ]
    orchestrator.event_bus = AsyncMock()
    return orchestrator


@pytest.fixture
def component_isolation(mock_orchestrator):
    """Cria instância de ComponentIsolation."""
    return ComponentIsolation(mock_orchestrator)


@pytest.mark.asyncio
async def test_isolate_component_full(component_isolation):
    """Testa isolamento completo de componente."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.FULL, "Test")

    assert component_isolation.is_isolated(component_id)
    assert component_id in component_isolation.isolation_records


@pytest.mark.asyncio
async def test_isolate_component_emergency(component_isolation):
    """Testa isolamento de emergência."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.EMERGENCY, "Critical")

    assert component_isolation.is_isolated(component_id)
    record = component_isolation.isolation_records[component_id]
    assert record.isolation_level == IsolationLevel.EMERGENCY


@pytest.mark.asyncio
async def test_isolate_block_communications(component_isolation):
    """Testa bloqueio de comunicações."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.FULL, "Test")

    assert component_id in component_isolation.communication_blocks
    blocked = component_isolation.communication_blocks[component_id]
    assert len(blocked) > 0


@pytest.mark.asyncio
async def test_isolate_reduce_permissions(component_isolation):
    """Testa redução de permissões."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.FULL, "Test")

    assert component_id in component_isolation.permission_blocks
    blocked_perms = component_isolation.permission_blocks[component_id]
    assert len(blocked_perms) > 0


@pytest.mark.asyncio
async def test_isolate_limit_resources(component_isolation):
    """Testa limitação de recursos."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.FULL, "Test")

    assert component_id in component_isolation.resource_limits
    limits = component_isolation.resource_limits[component_id]
    assert "cpu_percent" in limits
    assert "memory_mb" in limits


@pytest.mark.asyncio
async def test_isolate_emergency_limits(component_isolation):
    """Testa limites de emergência."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.EMERGENCY, "Critical")

    limits = component_isolation.resource_limits[component_id]
    assert limits["cpu_percent"] == 5.0
    assert limits["memory_mb"] == 50


@pytest.mark.asyncio
async def test_isolate_update_level(component_isolation):
    """Testa atualização de nível de isolamento."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.PARTIAL, "Test")
    await component_isolation.isolate(component_id, IsolationLevel.FULL, "Updated")

    record = component_isolation.isolation_records[component_id]
    assert record.isolation_level == IsolationLevel.FULL


@pytest.mark.asyncio
async def test_release_isolation(component_isolation):
    """Testa liberação de isolamento."""
    component_id = "test_component"
    await component_isolation.isolate(component_id, IsolationLevel.FULL, "Test")

    result = await component_isolation.release(component_id)

    assert result is True
    assert not component_isolation.is_isolated(component_id)


@pytest.mark.asyncio
async def test_release_not_isolated(component_isolation):
    """Testa liberação de componente não isolado."""
    result = await component_isolation.release("not_isolated")

    assert result is False


def test_can_communicate_isolated(component_isolation):
    """Testa verificação de comunicação com componente isolado."""
    # Componente não isolado pode comunicar
    assert component_isolation.can_communicate("comp1", "comp2") is True


@pytest.mark.asyncio
async def test_can_communicate_blocked(component_isolation):
    """Testa bloqueio de comunicação."""
    component_id = "comp1"
    await component_isolation.isolate(component_id, IsolationLevel.FULL, "Test")

    # comp1 não pode comunicar com outros componentes bloqueados (ex: security que está na lista)
    # Verificar que comp1 está isolado e não pode comunicar
    assert component_isolation.is_isolated(component_id)
    # comp1 não pode comunicar com security (que está na lista de bloqueados)
    assert component_isolation.can_communicate(component_id, "security") is False


def test_get_isolation_status(component_isolation):
    """Testa obtenção de status de isolamento."""
    status = component_isolation.get_isolation_status()

    assert "isolated_count" in status
    assert "isolated_components" in status
    assert "records" in status

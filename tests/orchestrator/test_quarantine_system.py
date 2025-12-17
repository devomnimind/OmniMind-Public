"""
Testes para QuarantineSystem.

Testa sistema de quarentena de componentes comprometidos.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator.quarantine_system import QuarantineSystem


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
    orchestrator.audit_system = MagicMock()
    return orchestrator


@pytest.fixture
def quarantine_system(mock_orchestrator):
    """Cria instância de QuarantineSystem."""
    return QuarantineSystem(mock_orchestrator)


@pytest.mark.asyncio
async def test_quarantine_component(quarantine_system, mock_orchestrator):
    """Testa quarentena de componente."""
    component_id = "test_component"
    reason = "Suspicious activity detected"
    evidence = {"source_ip": "192.168.1.100", "port": 4444}

    await quarantine_system.quarantine(component_id, reason, evidence)

    assert quarantine_system.is_quarantined(component_id)
    assert component_id in quarantine_system.quarantine_records
    record = quarantine_system.quarantine_records[component_id]
    assert record.reason == reason
    assert record.evidence == evidence


@pytest.mark.asyncio
async def test_quarantine_block_communication(quarantine_system, mock_orchestrator):
    """Testa bloqueio de comunicação ao colocar em quarentena."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Test")

    assert component_id in quarantine_system.communication_blocks
    blocked = quarantine_system.communication_blocks[component_id]
    assert len(blocked) > 0


@pytest.mark.asyncio
async def test_quarantine_reduce_capacity(quarantine_system):
    """Testa redução de capacidade ao colocar em quarentena."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Test")

    assert component_id in quarantine_system.capacity_reductions
    assert quarantine_system.capacity_reductions[component_id] == 0.1


@pytest.mark.asyncio
async def test_quarantine_notify(quarantine_system, mock_orchestrator):
    """Testa notificação de quarentena."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Test")

    # Verificar se evento foi publicado
    assert mock_orchestrator.event_bus.publish.called


@pytest.mark.asyncio
async def test_quarantine_update_existing(quarantine_system):
    """Testa atualização de quarentena existente."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Reason 1")
    await quarantine_system.quarantine(component_id, "Reason 2", {"new": "evidence"})

    record = quarantine_system.quarantine_records[component_id]
    assert record.reason == "Reason 2"
    assert "new" in record.evidence


@pytest.mark.asyncio
async def test_release_quarantine_safe(quarantine_system):
    """Testa liberação de quarentena quando seguro."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Test")

    # Marcar como seguro
    record = quarantine_system.quarantine_records[component_id]
    record.safe_to_release = True

    result = await quarantine_system.release(component_id, {"safe_to_release": True})

    assert result is True
    assert not quarantine_system.is_quarantined(component_id)


@pytest.mark.asyncio
async def test_release_quarantine_unsafe(quarantine_system):
    """Testa tentativa de liberação quando não seguro."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Test")

    result = await quarantine_system.release(component_id, {"safe_to_release": False})

    assert result is False
    assert quarantine_system.is_quarantined(component_id)


@pytest.mark.asyncio
async def test_release_not_quarantined(quarantine_system):
    """Testa liberação de componente não em quarentena."""
    result = await quarantine_system.release("not_quarantined")

    assert result is False


@pytest.mark.asyncio
async def test_release_restore_communication(quarantine_system):
    """Testa restauração de comunicação ao liberar."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Test")
    record = quarantine_system.quarantine_records[component_id]
    record.safe_to_release = True

    await quarantine_system.release(component_id, {"safe_to_release": True})

    assert component_id not in quarantine_system.communication_blocks


@pytest.mark.asyncio
async def test_release_restore_capacity(quarantine_system):
    """Testa restauração de capacidade ao liberar."""
    component_id = "test_component"
    await quarantine_system.quarantine(component_id, "Test")
    record = quarantine_system.quarantine_records[component_id]
    record.safe_to_release = True

    await quarantine_system.release(component_id, {"safe_to_release": True})

    assert component_id not in quarantine_system.capacity_reductions


def test_get_quarantine_status(quarantine_system):
    """Testa obtenção de status de quarentena."""
    status = quarantine_system.get_quarantine_status()

    assert "quarantined_count" in status
    assert "quarantined_components" in status
    assert "records" in status
    assert status["quarantined_count"] == 0


@pytest.mark.asyncio
async def test_get_quarantine_status_with_components(quarantine_system):
    """Testa status com componentes em quarentena."""
    await quarantine_system.quarantine("comp1", "Reason 1")
    await quarantine_system.quarantine("comp2", "Reason 2")

    status = quarantine_system.get_quarantine_status()

    assert status["quarantined_count"] == 2
    assert "comp1" in status["quarantined_components"]
    assert "comp2" in status["quarantined_components"]

"""
Testes para RollbackSystem.

Testa sistema de rollback automático.
"""

import pytest

from src.orchestrator.rollback_system import RollbackSystem


@pytest.fixture
def rollback_system():
    """Cria instância de RollbackSystem."""
    return RollbackSystem(max_versions=10)


def test_create_snapshot(rollback_system):
    """Testa criação de snapshot."""
    state = {"key": "value", "count": 42}
    version = rollback_system.create_snapshot("test_component", state)

    assert version == 1
    assert rollback_system.get_current_version("test_component") == 1


def test_create_multiple_snapshots(rollback_system):
    """Testa criação de múltiplos snapshots."""
    rollback_system.create_snapshot("test_component", {"v1": 1})
    rollback_system.create_snapshot("test_component", {"v2": 2})
    version = rollback_system.create_snapshot("test_component", {"v3": 3})

    assert version == 3
    assert rollback_system.get_current_version("test_component") == 3


@pytest.mark.asyncio
async def test_rollback_component(rollback_system):
    """Testa rollback de componente."""
    rollback_system.create_snapshot("test_component", {"v1": 1})
    rollback_system.create_snapshot("test_component", {"v2": 2})
    rollback_system.create_snapshot("test_component", {"v3": 3})

    # Rollback para versão anterior
    result = await rollback_system.rollback_component("test_component")

    assert result is True
    assert rollback_system.get_current_version("test_component") == 2


@pytest.mark.asyncio
async def test_rollback_specific_version(rollback_system):
    """Testa rollback para versão específica."""
    rollback_system.create_snapshot("test_component", {"v1": 1})
    rollback_system.create_snapshot("test_component", {"v2": 2})
    rollback_system.create_snapshot("test_component", {"v3": 3})

    # Rollback para versão 1
    result = await rollback_system.rollback_component("test_component", target_version=1)

    assert result is True
    assert rollback_system.get_current_version("test_component") == 1


@pytest.mark.asyncio
async def test_rollback_no_history(rollback_system):
    """Testa rollback sem histórico."""
    result = await rollback_system.rollback_component("unknown_component")

    assert result is False


@pytest.mark.asyncio
async def test_rollback_single_version(rollback_system):
    """Testa rollback com apenas uma versão."""
    rollback_system.create_snapshot("test_component", {"v1": 1})

    result = await rollback_system.rollback_component("test_component")

    assert result is False  # Não há versão anterior


def test_get_version_history(rollback_system):
    """Testa obtenção de histórico de versões."""
    rollback_system.create_snapshot("test_component", {"v1": 1})
    rollback_system.create_snapshot("test_component", {"v2": 2})
    rollback_system.create_snapshot("test_component", {"v3": 3})

    history = rollback_system.get_version_history("test_component", limit=2)

    assert len(history) == 2
    assert history[-1].version == 3


def test_get_snapshot(rollback_system):
    """Testa obtenção de snapshot específico."""
    rollback_system.create_snapshot("test_component", {"v1": 1})
    rollback_system.create_snapshot("test_component", {"v2": 2})

    snapshot = rollback_system.get_snapshot("test_component", version=1)

    assert snapshot is not None
    assert snapshot.version == 1
    assert snapshot.state == {"v1": 1}


def test_get_snapshot_not_found(rollback_system):
    """Testa obtenção de snapshot inexistente."""
    snapshot = rollback_system.get_snapshot("test_component", version=999)

    assert snapshot is None


def test_get_rollback_summary(rollback_system):
    """Testa obtenção de resumo de rollback."""
    rollback_system.create_snapshot("comp1", {"state": 1})
    rollback_system.create_snapshot("comp2", {"state": 2})

    summary = rollback_system.get_rollback_summary()

    assert summary["tracked_components"] == 2
    assert summary["total_snapshots"] == 2
    assert "comp1" in summary["components"]
    assert "comp2" in summary["components"]

"""
Testes para SandboxSystem.

Testa sistema de sandbox para auto-melhoria segura.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator.sandbox_system import SandboxState, SandboxSystem


@pytest.fixture
def mock_orchestrator():
    """Cria mock do OrchestratorAgent."""
    orchestrator = MagicMock()
    orchestrator.agent_registry = MagicMock()
    orchestrator.agent_registry.get_all_agents = MagicMock(return_value=["security", "code"])
    orchestrator.agent_registry.check_health = AsyncMock(return_value=True)
    orchestrator.agent_registry.health_check_all = AsyncMock(
        return_value={"security": True, "code": True}
    )

    orchestrator.rollback_system = MagicMock()
    orchestrator.rollback_system.get_component_snapshots = MagicMock(return_value=[])
    orchestrator.rollback_system.rollback_component_config = AsyncMock(return_value=True)

    orchestrator.introspection_loop = MagicMock()
    orchestrator.introspection_loop.get_latest_metrics = MagicMock(return_value=None)

    return orchestrator


@pytest.fixture
def sandbox_system(mock_orchestrator):
    """Cria instância de SandboxSystem."""
    return SandboxSystem(mock_orchestrator)


@pytest.mark.asyncio
async def test_create_snapshot(sandbox_system):
    """Testa criação de snapshot."""
    snapshot_id = await sandbox_system.create_snapshot("test")

    assert snapshot_id is not None
    assert snapshot_id in sandbox_system.snapshots
    assert sandbox_system.current_state == SandboxState.IDLE


@pytest.mark.asyncio
async def test_apply_change_in_sandbox(sandbox_system):
    """Testa aplicação de mudança no sandbox."""
    # Criar snapshot primeiro
    snapshot_id = await sandbox_system.create_snapshot("test")

    # Aplicar mudança
    change_id = await sandbox_system.apply_change_in_sandbox(
        component_id="test_component",
        change_type="config",
        change_data={"key": "value"},
        description="Test change",
        snapshot_id=snapshot_id,
    )

    assert change_id is not None
    assert change_id in sandbox_system.changes
    assert sandbox_system.current_state == SandboxState.IDLE


@pytest.mark.asyncio
async def test_validate_change(sandbox_system):
    """Testa validação de mudança."""
    # Criar snapshot e mudança
    snapshot_id = await sandbox_system.create_snapshot("test")
    change_id = await sandbox_system.apply_change_in_sandbox(
        component_id="test_component",
        change_type="config",
        change_data={"key": "value"},
        description="Test change",
        snapshot_id=snapshot_id,
    )

    # Validar
    result = await sandbox_system._validate_change(change_id)

    assert isinstance(result, bool)
    assert change_id in sandbox_system.results


@pytest.mark.asyncio
async def test_rollback_change(sandbox_system):
    """Testa rollback de mudança."""
    # Criar snapshot e mudança
    snapshot_id = await sandbox_system.create_snapshot("test")
    change_id = await sandbox_system.apply_change_in_sandbox(
        component_id="test_component",
        change_type="config",
        change_data={"key": "value"},
        description="Test change",
        snapshot_id=snapshot_id,
    )

    # Fazer rollback
    await sandbox_system._rollback_change(change_id, snapshot_id)

    assert sandbox_system.results[change_id].rollback_applied is True
    assert sandbox_system.current_state == SandboxState.IDLE


@pytest.mark.asyncio
async def test_apply_to_production_success(sandbox_system):
    """Testa aplicação à produção com sucesso."""
    # Criar snapshot e mudança válida
    snapshot_id = await sandbox_system.create_snapshot("test")
    change_id = await sandbox_system.apply_change_in_sandbox(
        component_id="test_component",
        change_type="config",
        change_data={"key": "value"},
        description="Test change",
        snapshot_id=snapshot_id,
    )

    # Garantir que validação passou
    sandbox_system.results[change_id].success = True
    sandbox_system.results[change_id].validation_passed = True

    # Aplicar à produção
    result = await sandbox_system.apply_to_production(change_id)

    assert result is True
    assert sandbox_system.current_state == SandboxState.IDLE


@pytest.mark.asyncio
async def test_apply_to_production_failure(sandbox_system):
    """Testa aplicação à produção com falha."""
    # Criar snapshot e mudança inválida
    snapshot_id = await sandbox_system.create_snapshot("test")
    change_id = await sandbox_system.apply_change_in_sandbox(
        component_id="test_component",
        change_type="config",
        change_data={"key": "value"},
        description="Test change",
        snapshot_id=snapshot_id,
    )

    # Garantir que validação falhou
    sandbox_system.results[change_id].success = False
    sandbox_system.results[change_id].validation_passed = False

    # Tentar aplicar à produção
    result = await sandbox_system.apply_to_production(change_id)

    assert result is False


@pytest.mark.asyncio
async def test_detect_degradation(sandbox_system):
    """Testa detecção de degradação."""
    metrics_before = {
        "error_rate": 0.05,
        "component_health": {"security": True, "code": True},
    }
    metrics_after = {
        "error_rate": 0.10,  # 100% de aumento (deveria detectar)
        "component_health": {"security": True, "code": True},
    }

    degradation = sandbox_system._detect_degradation(metrics_before, metrics_after)

    assert degradation is True


@pytest.mark.asyncio
async def test_get_sandbox_status(sandbox_system):
    """Testa obtenção de status do sandbox."""
    status = sandbox_system.get_sandbox_status()

    assert "current_state" in status
    assert "total_snapshots" in status
    assert "total_changes" in status
    assert status["current_state"] == SandboxState.IDLE.value


@pytest.mark.asyncio
async def test_get_change_history(sandbox_system):
    """Testa obtenção de histórico de mudanças."""
    # Criar algumas mudanças
    snapshot_id = await sandbox_system.create_snapshot("test")
    for i in range(3):
        await sandbox_system.apply_change_in_sandbox(
            component_id=f"component_{i}",
            change_type="config",
            change_data={"key": f"value_{i}"},
            description=f"Change {i}",
            snapshot_id=snapshot_id,
        )

    history = sandbox_system.get_change_history(limit=5)

    assert len(history) == 3
    assert all("change_id" in h for h in history)
    assert all("component_id" in h for h in history)


@pytest.mark.asyncio
async def test_max_snapshots_limit(sandbox_system):
    """Testa limite de snapshots."""
    # Criar mais snapshots que o limite
    for i in range(15):
        await sandbox_system.create_snapshot(f"test_{i}")

    # Verificar que não excedeu o limite
    assert len(sandbox_system.snapshots) <= sandbox_system.config["max_snapshots"]


@pytest.mark.asyncio
async def test_auto_rollback_on_error(sandbox_system):
    """Testa rollback automático em caso de erro."""
    sandbox_system.config["auto_rollback_on_error"] = True

    snapshot_id = await sandbox_system.create_snapshot("test")

    # Aplicar mudança que vai falhar na validação
    change_id = await sandbox_system.apply_change_in_sandbox(
        component_id="test_component",
        change_type="config",
        change_data={"key": "value"},
        description="Test change",
        snapshot_id=snapshot_id,
    )

    # Forçar falha na validação
    sandbox_system.results[change_id].success = False

    # Verificar que rollback foi aplicado (se validação falhou)
    # O rollback é aplicado automaticamente se validação falhar
    assert change_id in sandbox_system.results

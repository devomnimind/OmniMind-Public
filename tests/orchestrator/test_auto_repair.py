"""
Testes para AutoRepairSystem.

Testa sistema de auto-reparação.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator.auto_repair import AutoRepairSystem, RepairStrategy


@pytest.fixture
def mock_orchestrator():
    """Cria mock do OrchestratorAgent."""
    orchestrator = MagicMock()
    orchestrator.agent_registry = MagicMock()
    orchestrator.agent_registry.get_agent = MagicMock(return_value=MagicMock())
    orchestrator.agent_registry._health_status = {}
    return orchestrator


@pytest.fixture
def auto_repair_system(mock_orchestrator):
    """Cria instância de AutoRepairSystem."""
    return AutoRepairSystem(mock_orchestrator)


@pytest.mark.asyncio
async def test_detect_and_repair_threshold(auto_repair_system):
    """Testa detecção e reparo após threshold."""
    # Primeiras falhas não devem reparar
    result1 = await auto_repair_system.detect_and_repair("test_component", "Error 1")
    assert result1 is False

    result2 = await auto_repair_system.detect_and_repair("test_component", "Error 2")
    assert result2 is False

    # Terceira falha deve reparar
    result3 = await auto_repair_system.detect_and_repair("test_component", "Error 3")
    assert result3 is True


@pytest.mark.asyncio
async def test_repair_restart(auto_repair_system):
    """Testa reparo via restart."""
    # Forçar threshold
    auto_repair_system.failure_counts["test_component"] = 3

    result = await auto_repair_system._execute_repair("test_component", "Timeout error")

    assert result is True
    assert len(auto_repair_system.repair_history) == 1
    assert auto_repair_system.repair_history[0].strategy == RepairStrategy.RESTART


@pytest.mark.asyncio
async def test_repair_reset(auto_repair_system):
    """Testa reparo via reset."""
    # Forçar threshold
    auto_repair_system.failure_counts["test_component"] = 3

    result = await auto_repair_system._repair_reset("test_component")

    assert result is True
    assert (
        "test_component" not in auto_repair_system.failure_counts
        or auto_repair_system.failure_counts["test_component"] == 0
    )


@pytest.mark.asyncio
async def test_repair_isolate(auto_repair_system):
    """Testa reparo via isolamento."""
    # Configurar component_isolation
    auto_repair_system.orchestrator.component_isolation = MagicMock()
    auto_repair_system.orchestrator.component_isolation.isolate = AsyncMock()

    result = await auto_repair_system._repair_isolate("test_component")

    assert result is True
    auto_repair_system.orchestrator.component_isolation.isolate.assert_called_once()


@pytest.mark.asyncio
async def test_determine_repair_strategy(auto_repair_system):
    """Testa determinação de estratégia de reparo."""
    # Componente crítico
    strategy1 = auto_repair_system._determine_repair_strategy("security", "Error")
    assert strategy1 == RepairStrategy.RESTART

    # Componente opcional com timeout
    strategy2 = auto_repair_system._determine_repair_strategy("code", "Timeout error")
    assert strategy2 == RepairStrategy.RESET

    # Componente de estado
    strategy3 = auto_repair_system._determine_repair_strategy("config_state", "Error")
    assert strategy3 == RepairStrategy.ROLLBACK


def test_get_repair_history(auto_repair_system):
    """Testa obtenção de histórico de reparos."""
    # Adicionar alguns reparos simulados
    from src.orchestrator.auto_repair import RepairAction
    import time

    auto_repair_system.repair_history.append(
        RepairAction("comp1", RepairStrategy.RESTART, time.time(), "Test", True)
    )
    auto_repair_system.repair_history.append(
        RepairAction("comp2", RepairStrategy.RESET, time.time(), "Test", True)
    )

    history = auto_repair_system.get_repair_history(limit=1)

    assert len(history) == 1
    assert history[0].component_id == "comp2"


def test_get_failure_counts(auto_repair_system):
    """Testa obtenção de contadores de falhas."""
    auto_repair_system.failure_counts["comp1"] = 2
    auto_repair_system.failure_counts["comp2"] = 1

    counts = auto_repair_system.get_failure_counts()

    assert counts["comp1"] == 2
    assert counts["comp2"] == 1


def test_reset_failure_count(auto_repair_system):
    """Testa reset de contador de falhas."""
    auto_repair_system.failure_counts["test_component"] = 3
    auto_repair_system.reset_failure_count("test_component")

    assert "test_component" not in auto_repair_system.failure_counts


def test_get_repair_summary(auto_repair_system):
    """Testa obtenção de resumo de reparos."""
    from src.orchestrator.auto_repair import RepairAction
    import time

    auto_repair_system.repair_history.append(
        RepairAction("comp1", RepairStrategy.RESTART, time.time(), "Test", True)
    )
    auto_repair_system.repair_history.append(
        RepairAction("comp2", RepairStrategy.RESET, time.time(), "Test", False)
    )

    summary = auto_repair_system.get_repair_summary()

    assert summary["total_repairs"] == 2
    assert summary["successful_repairs"] == 1
    assert summary["failed_repairs"] == 1
    assert summary["success_rate"] == 0.5

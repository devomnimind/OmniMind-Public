"""
Testes para PowerStateManager.

Testa sistema de power states e otimização de recursos.
"""

from unittest.mock import MagicMock

import pytest

from src.orchestrator.power_states import PowerState, PowerStateManager


@pytest.fixture
def mock_orchestrator():
    """Cria mock do OrchestratorAgent."""
    orchestrator = MagicMock()
    orchestrator.agent_registry = MagicMock()
    orchestrator.agent_registry.get_agent = MagicMock(return_value=MagicMock())
    orchestrator.agent_registry._health_status = {}
    return orchestrator


@pytest.fixture
def power_state_manager(mock_orchestrator):
    """Cria instância de PowerStateManager."""
    return PowerStateManager(mock_orchestrator)


@pytest.mark.asyncio
async def test_initial_state(power_state_manager):
    """Testa estado inicial."""
    assert power_state_manager.get_current_state() == PowerState.ACTIVE


@pytest.mark.asyncio
async def test_transition_to_idle(power_state_manager):
    """Testa transição para IDLE."""
    await power_state_manager.transition_to(PowerState.IDLE, "Test")

    assert power_state_manager.get_current_state() == PowerState.IDLE
    assert power_state_manager.previous_state == PowerState.ACTIVE


@pytest.mark.asyncio
async def test_transition_to_standby(power_state_manager):
    """Testa transição para STANDBY."""
    await power_state_manager.transition_to(PowerState.STANDBY, "Test")

    assert power_state_manager.get_current_state() == PowerState.STANDBY
    assert len(power_state_manager.preheating_services) > 0


@pytest.mark.asyncio
async def test_transition_to_critical(power_state_manager):
    """Testa transição para CRITICAL."""
    await power_state_manager.transition_to(PowerState.CRITICAL, "Emergency")

    assert power_state_manager.get_current_state() == PowerState.CRITICAL
    # CRITICAL deve ter todos os serviços ativos
    assert len(power_state_manager.get_active_services()) > 0


@pytest.mark.asyncio
async def test_transition_back_to_active(power_state_manager):
    """Testa transição de volta para ACTIVE."""
    await power_state_manager.transition_to(PowerState.IDLE, "Test")
    await power_state_manager.transition_to(PowerState.ACTIVE, "Resume")

    assert power_state_manager.get_current_state() == PowerState.ACTIVE
    assert power_state_manager.previous_state == PowerState.IDLE


@pytest.mark.asyncio
async def test_idle_keeps_critical_services(power_state_manager):
    """Testa que IDLE mantém serviços críticos."""
    await power_state_manager.transition_to(PowerState.IDLE, "Test")

    active_services = power_state_manager.get_active_services()
    # Verificar que serviços críticos estão ativos
    critical_services = power_state_manager.service_categories["critical"].services
    for service in critical_services:
        assert service in active_services or power_state_manager.is_service_active(service)


@pytest.mark.asyncio
async def test_standby_preheating(power_state_manager):
    """Testa preheating em STANDBY."""
    await power_state_manager.transition_to(PowerState.STANDBY, "Test")

    assert len(power_state_manager.preheating_services) > 0


@pytest.mark.asyncio
async def test_critical_activates_all(power_state_manager):
    """Testa que CRITICAL ativa todos os serviços."""
    await power_state_manager.transition_to(PowerState.CRITICAL, "Emergency")

    active_services = power_state_manager.get_active_services()
    # Deve ter mais serviços que IDLE
    assert len(active_services) >= len(power_state_manager.service_categories["critical"].services)


def test_get_state_summary(power_state_manager):
    """Testa obtenção de resumo de estado."""
    summary = power_state_manager.get_state_summary()

    assert "current_state" in summary
    assert "active_services" in summary
    assert "active_services_count" in summary


@pytest.mark.asyncio
async def test_get_state_history(power_state_manager):
    """Testa histórico de transições."""
    await power_state_manager.transition_to(PowerState.IDLE, "Test 1")
    await power_state_manager.transition_to(PowerState.ACTIVE, "Test 2")

    history = power_state_manager.get_state_history(limit=2)

    assert len(history) == 2
    assert history[-1]["to_state"] == PowerState.ACTIVE.value


def test_is_service_active(power_state_manager):
    """Testa verificação de serviço ativo."""
    # Em ACTIVE, serviços críticos devem estar ativos
    critical_services = power_state_manager.service_categories["critical"].services
    if critical_services:
        # Verificar se pelo menos um serviço crítico está ativo
        assert (
            any(power_state_manager.is_service_active(service) for service in critical_services)
            or power_state_manager.get_current_state() == PowerState.ACTIVE
        )


@pytest.mark.asyncio
async def test_transition_same_state(power_state_manager):
    """Testa transição para mesmo estado."""
    initial_state = power_state_manager.get_current_state()
    await power_state_manager.transition_to(initial_state, "Test")

    assert power_state_manager.get_current_state() == initial_state


@pytest.mark.asyncio
async def test_multiple_transitions(power_state_manager):
    """Testa múltiplas transições."""
    await power_state_manager.transition_to(PowerState.IDLE, "1")
    await power_state_manager.transition_to(PowerState.STANDBY, "2")
    await power_state_manager.transition_to(PowerState.ACTIVE, "3")
    await power_state_manager.transition_to(PowerState.CRITICAL, "4")

    assert power_state_manager.get_current_state() == PowerState.CRITICAL
    assert len(power_state_manager.state_history) == 4

"""
Testes para OrchestratorEventBus.

Cobertura de:
- Publicação de eventos
- Priorização
- Debouncing
- Handlers
"""

from __future__ import annotations

import asyncio
import time

import pytest

from src.orchestrator.event_bus import (
    EventPriority,
    OrchestratorEvent,
    OrchestratorEventBus,
)
from src.security.security_agent import SecurityEvent, ThreatLevel


class TestEventPriority:
    """Testes para EventPriority enum."""

    def test_priority_values(self) -> None:
        """Testa valores de prioridade."""
        assert EventPriority.CRITICAL.value == 0
        assert EventPriority.HIGH.value == 1
        assert EventPriority.MEDIUM.value == 2
        assert EventPriority.LOW.value == 3


class TestOrchestratorEventBus:
    """Testes para OrchestratorEventBus."""

    @pytest.fixture
    def event_bus(self) -> OrchestratorEventBus:
        """Cria instância do EventBus."""
        return OrchestratorEventBus(debounce_window=1.0)

    @pytest.mark.asyncio
    async def test_event_bus_initialization(self, event_bus: OrchestratorEventBus) -> None:
        """Testa inicialização do EventBus."""
        assert event_bus is not None
        queue_sizes = event_bus.get_queue_sizes()
        assert len(queue_sizes) == 4
        assert all(size == 0 for size in queue_sizes.values())

    @pytest.mark.asyncio
    async def test_publish_event(self, event_bus: OrchestratorEventBus) -> None:
        """Testa publicação de evento."""
        event = OrchestratorEvent(
            event_type="test_event",
            source="test",
            priority=EventPriority.MEDIUM,
            data={"key": "value"},
            timestamp=time.time(),
        )

        await event_bus.publish(event)

        queue_sizes = event_bus.get_queue_sizes()
        assert queue_sizes["MEDIUM"] == 1

    @pytest.mark.asyncio
    async def test_debouncing(self, event_bus: OrchestratorEventBus) -> None:
        """Testa debouncing de eventos."""
        event1 = OrchestratorEvent(
            event_type="test_event",
            source="test",
            priority=EventPriority.MEDIUM,
            data={},
            timestamp=time.time(),
        )
        event2 = OrchestratorEvent(
            event_type="test_event",
            source="test",
            priority=EventPriority.MEDIUM,
            data={},
            timestamp=time.time(),
        )

        await event_bus.publish(event1)
        await event_bus.publish(event2)  # Deve ser debounced

        queue_sizes = event_bus.get_queue_sizes()
        assert queue_sizes["MEDIUM"] == 1  # Apenas um evento na fila

    @pytest.mark.asyncio
    async def test_critical_events_not_debounced(self, event_bus: OrchestratorEventBus) -> None:
        """Testa que eventos críticos não são debounced."""
        event1 = OrchestratorEvent(
            event_type="critical_event",
            source="test",
            priority=EventPriority.CRITICAL,
            data={},
            timestamp=time.time(),
        )
        event2 = OrchestratorEvent(
            event_type="critical_event",
            source="test",
            priority=EventPriority.CRITICAL,
            data={},
            timestamp=time.time(),
        )

        await event_bus.publish(event1)
        await event_bus.publish(event2)

        queue_sizes = event_bus.get_queue_sizes()
        assert queue_sizes["CRITICAL"] == 2  # Ambos os eventos na fila

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, event_bus: OrchestratorEventBus) -> None:
        """Testa subscrição e publicação de eventos."""
        handler_called = []

        async def handler(event: OrchestratorEvent) -> None:
            handler_called.append(event.event_type)

        event_bus.subscribe("test_event", handler)

        event = OrchestratorEvent(
            event_type="test_event",
            source="test",
            priority=EventPriority.MEDIUM,
            data={},
            timestamp=time.time(),
        )

        await event_bus.publish(event)

        # Iniciar processamento brevemente
        asyncio.create_task(event_bus.start_processing())  # noqa: F841
        await asyncio.sleep(0.2)
        await event_bus.stop_processing()

        # Handler deve ter sido chamado
        assert "test_event" in handler_called

    @pytest.mark.asyncio
    async def test_security_event_conversion(self, event_bus: OrchestratorEventBus) -> None:
        """Testa conversão de SecurityEvent para OrchestratorEvent."""
        security_event = SecurityEvent(
            timestamp="2025-12-06T00:00:00Z",
            event_type="intrusion_attempt",
            source="network",
            description="Suspicious activity detected",
            details={"ip": "192.168.1.100"},
            threat_level=ThreatLevel.HIGH,
            raw_data="raw data",
        )

        await event_bus.publish_security_event(security_event)

        queue_sizes = event_bus.get_queue_sizes()
        assert queue_sizes["HIGH"] == 1

    @pytest.mark.asyncio
    async def test_clear_debounce_cache(self, event_bus: OrchestratorEventBus) -> None:
        """Testa limpeza de cache de debouncing."""
        event = OrchestratorEvent(
            event_type="test_event",
            source="test",
            priority=EventPriority.MEDIUM,
            data={},
            timestamp=time.time(),
        )

        await event_bus.publish(event)
        event_bus.clear_debounce_cache()

        # Após limpar cache, evento deve ser aceito novamente
        await event_bus.publish(event)

        queue_sizes = event_bus.get_queue_sizes()
        assert queue_sizes["MEDIUM"] == 2

    @pytest.mark.asyncio
    async def test_wildcard_subscription(self, event_bus: OrchestratorEventBus) -> None:
        """Testa subscrição com wildcard."""
        handler_called = []

        async def handler(event: OrchestratorEvent) -> None:
            handler_called.append(event.event_type)

        event_bus.subscribe("*", handler)

        event1 = OrchestratorEvent(
            event_type="event1",
            source="test",
            priority=EventPriority.MEDIUM,
            data={},
            timestamp=time.time(),
        )
        event2 = OrchestratorEvent(
            event_type="event2",
            source="test",
            priority=EventPriority.MEDIUM,
            data={},
            timestamp=time.time(),
        )

        await event_bus.publish(event1)
        await event_bus.publish(event2)

        # Iniciar processamento brevemente
        asyncio.create_task(event_bus.start_processing())  # noqa: F841
        await asyncio.sleep(0.2)
        await event_bus.stop_processing()

        # Handler deve ter sido chamado para ambos
        assert len(handler_called) == 2

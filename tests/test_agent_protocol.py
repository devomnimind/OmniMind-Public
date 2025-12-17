#!/usr/bin/env python3
"""
Tests for Agent Communication Protocol

Testa sistema de mensagens inter-agentes.
"""

import asyncio
from typing import AsyncGenerator

import pytest

from src.agents.agent_protocol import (
    AgentMessage,
    AgentMessageBus,
    MessagePriority,
    MessageType,
)


class TestAgentMessage:
    """Testes para AgentMessage"""

    def test_message_creation(self) -> None:
        """Testa criação de mensagem"""
        msg = AgentMessage(
            message_id="msg-001",
            message_type=MessageType.REQUEST,
            sender="agent-1",
            recipient="agent-2",
            payload={"action": "test"},
            priority=MessagePriority.HIGH,
        )

        assert msg.message_id == "msg-001"
        assert msg.message_type == MessageType.REQUEST
        assert msg.sender == "agent-1"
        assert msg.recipient == "agent-2"
        assert msg.priority == MessagePriority.HIGH
        assert msg.payload["action"] == "test"

    def test_message_serialization(self) -> None:
        """Testa serialização de mensagem"""
        msg = AgentMessage(
            message_id="msg-001",
            message_type=MessageType.NOTIFICATION,
            sender="agent-1",
            recipient="agent-2",
            payload={"data": "value"},
        )

        data = msg.to_dict()

        assert data["message_id"] == "msg-001"
        assert data["message_type"] == "notification"
        assert data["sender"] == "agent-1"
        assert data["priority"] == 2  # MEDIUM

    def test_message_deserialization(self) -> None:
        """Testa desserialização de mensagem"""
        data = {
            "message_id": "msg-001",
            "message_type": "request",
            "sender": "agent-1",
            "recipient": "agent-2",
            "payload": {"test": "data"},
            "priority": 1,  # HIGH
            "timestamp": "2025-01-01T00:00:00Z",
            "requires_response": True,
            "timeout_seconds": 30,
        }

        msg = AgentMessage.from_dict(data)

        assert msg.message_id == "msg-001"
        assert msg.message_type == MessageType.REQUEST
        assert msg.priority == MessagePriority.HIGH
        assert msg.requires_response is True


@pytest.mark.asyncio
class TestAgentMessageBus:
    """Testes para AgentMessageBus"""

    @pytest.fixture
    async def message_bus(self) -> AsyncGenerator[AgentMessageBus, None]:
        """Fixture para criar message bus"""
        bus = AgentMessageBus()
        await bus.start()
        yield bus
        await bus.stop()

    async def test_register_agent(self, message_bus: AgentMessageBus) -> None:
        """Testa registro de agente"""
        message_bus.register_agent("agent-1")

        assert "agent-1" in message_bus._queues
        assert "agent-1" in message_bus._subscriptions

    async def test_unregister_agent(self, message_bus: AgentMessageBus) -> None:
        """Testa remoção de agente"""
        message_bus.register_agent("agent-1")
        message_bus.unregister_agent("agent-1")

        assert "agent-1" not in message_bus._queues

    async def test_subscribe(self, message_bus: AgentMessageBus) -> None:
        """Testa inscrição em tipos de mensagem"""
        message_bus.register_agent("agent-1")
        message_bus.subscribe("agent-1", [MessageType.REQUEST, MessageType.NOTIFICATION])

        assert MessageType.REQUEST in message_bus._subscriptions["agent-1"]
        assert MessageType.NOTIFICATION in message_bus._subscriptions["agent-1"]

    async def test_send_and_receive_message(self, message_bus: AgentMessageBus) -> None:
        """Testa envio e recebimento de mensagem"""
        message_bus.register_agent("agent-1")
        message_bus.register_agent("agent-2")

        msg = AgentMessage(
            message_id="msg-001",
            message_type=MessageType.NOTIFICATION,
            sender="agent-1",
            recipient="agent-2",
            payload={"data": "test"},
        )

        await message_bus.send_message(msg)

        received = await message_bus.receive_message("agent-2", timeout=1.0)

        assert received is not None
        assert received.message_id == "msg-001"
        assert received.sender == "agent-1"
        assert received.payload["data"] == "test"

    async def test_send_and_wait(self, message_bus: AgentMessageBus) -> None:
        """Testa envio com espera por resposta"""
        message_bus.register_agent("agent-1")
        message_bus.register_agent("agent-2")

        msg = AgentMessage(
            message_id="msg-001",
            message_type=MessageType.REQUEST,
            sender="agent-1",
            recipient="agent-2",
            payload={"action": "test"},
        )

        # Simular resposta em background
        async def respond() -> None:
            await asyncio.sleep(0.1)
            request = await message_bus.receive_message("agent-2", timeout=1.0)
            if request:
                await message_bus.respond_to_message(request, {"result": "success"})

        # Executar em paralelo
        respond_task = asyncio.create_task(respond())

        response = await message_bus.send_and_wait(msg, timeout=2)

        assert response.message_type == MessageType.RESPONSE
        assert response.correlation_id == "msg-001"
        assert response.payload["result"] == "success"

        await respond_task

    async def test_broadcast(self, message_bus: AgentMessageBus) -> None:
        """Testa broadcast para múltiplos agentes"""
        message_bus.register_agent("agent-1")
        message_bus.register_agent("agent-2")
        message_bus.register_agent("agent-3")

        message_bus.subscribe("agent-2", [MessageType.STATUS_UPDATE])
        message_bus.subscribe("agent-3", [MessageType.STATUS_UPDATE])

        await message_bus.broadcast(
            "agent-1",
            MessageType.STATUS_UPDATE,
            {"status": "running"},
        )

        # Dar tempo para mensagens serem processadas
        await asyncio.sleep(0.1)

        # Verificar que agent-2 e agent-3 receberam
        msg2 = await message_bus.receive_message("agent-2", timeout=0.1)
        msg3 = await message_bus.receive_message("agent-3", timeout=0.1)

        assert msg2 is not None
        assert msg3 is not None
        assert msg2.payload["status"] == "running"
        assert msg3.payload["status"] == "running"

    async def test_timeout_on_receive(self, message_bus: AgentMessageBus) -> None:
        """Testa timeout ao receber mensagem"""
        message_bus.register_agent("agent-1")

        # Tentar receber sem mensagens na fila
        result = await message_bus.receive_message("agent-1", timeout=0.1)

        assert result is None

    async def test_conflict_resolution(self, message_bus: AgentMessageBus) -> None:
        """Testa registro de resolução de conflito"""
        conflict = message_bus.resolve_conflict(
            agents=["agent-1", "agent-2"],
            conflict_type="resource",
            resolution="priority",
        )

        assert conflict.agents_involved == ["agent-1", "agent-2"]
        assert conflict.conflict_type == "resource"
        assert conflict.resolution == "priority"
        assert len(message_bus._conflicts) == 1

    async def test_get_queue_size(self, message_bus: AgentMessageBus) -> None:
        """Testa obtenção de tamanho de fila"""
        message_bus.register_agent("agent-1")

        size1 = message_bus.get_queue_size("agent-1")
        assert size1 == 0

        # Enviar mensagem
        msg = AgentMessage(
            message_id="msg-001",
            message_type=MessageType.NOTIFICATION,
            sender="agent-2",
            recipient="agent-1",
            payload={},
        )
        await message_bus.send_message(msg)

        size2 = message_bus.get_queue_size("agent-1")
        assert size2 == 1

    async def test_get_stats(self, message_bus: AgentMessageBus) -> None:
        """Testa obtenção de estatísticas"""
        message_bus.register_agent("agent-1")
        message_bus.register_agent("agent-2")

        stats = message_bus.get_stats()

        assert stats["registered_agents"] == 2
        assert "queue_sizes" in stats
        assert stats["total_conflicts"] == 0


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = ["TestAgentMessage", "TestAgentMessageBus"]

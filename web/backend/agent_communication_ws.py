"""
Agent Communication WebSocket Broadcaster

Monitora mensagens inter-agentes e transmite via WebSocket para o frontend.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from src.agents.agent_protocol import (
    AgentMessage,
    MessageType,
    get_message_bus,
)
from web.backend.websocket_manager import ws_manager, MessageType as WSMessageType

logger = logging.getLogger(__name__)


class AgentCommunicationBroadcaster:
    """Broadcaster de comunicação inter-agentes para WebSocket"""

    def __init__(self) -> None:
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._message_bus = get_message_bus()

    async def start(self) -> None:
        """Inicia broadcaster"""
        if self._running:
            return

        self._running = True

        # Iniciar message bus se necessário
        if not self._message_bus._running:
            await self._message_bus.start()

        # Registrar handler para capturar todas as mensagens
        self._message_bus.add_handler("__broadcaster__", self._on_agent_message)

        logger.info("Agent communication broadcaster started")

    async def stop(self) -> None:
        """Para broadcaster"""
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Agent communication broadcaster stopped")

    def _on_agent_message(self, message: AgentMessage) -> None:
        """Handler para mensagens de agentes"""
        if not self._running:
            return

        # Criar task para broadcast (não bloquear)
        asyncio.create_task(self._broadcast_message(message))

    async def _broadcast_message(self, message: AgentMessage) -> None:
        """Broadcast mensagem via WebSocket"""
        try:
            # Serializar mensagem
            data = {
                "message_id": message.message_id,
                "message_type": message.message_type.value,
                "sender": message.sender,
                "recipient": message.recipient,
                "payload": message.payload,
                "priority": message.priority.value,
                "timestamp": message.timestamp,
            }

            # Broadcast para clientes interessados
            await ws_manager.broadcast(
                WSMessageType("agent_message"),  # type: ignore
                data,
                channel="agent_communication",
            )

            # Se for atualização de status, também broadcast no canal de status
            if message.message_type == MessageType.STATUS_UPDATE:
                await ws_manager.broadcast(
                    WSMessageType("agent_status"),  # type: ignore
                    {
                        "agent_id": message.sender,
                        "status": message.payload.get("status") if isinstance(message.payload, dict) else "unknown",
                        "timestamp": message.timestamp,
                    },
                    channel="agent_status",
                )

        except Exception as exc:
            logger.exception(f"Error broadcasting agent message: {exc}")


# Singleton global
_broadcaster: Optional[AgentCommunicationBroadcaster] = None


def get_broadcaster() -> AgentCommunicationBroadcaster:
    """Obtém instância global do broadcaster"""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = AgentCommunicationBroadcaster()
    return _broadcaster


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = ["AgentCommunicationBroadcaster", "get_broadcaster"]

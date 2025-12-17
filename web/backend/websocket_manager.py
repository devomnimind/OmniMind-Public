"""WebSocket manager for real-time updates in OmniMind backend.

Provides WebSocket endpoints for:
- Task updates and progress tracking
- Agent status streaming
- System metrics streaming
- Security events streaming
"""

from __future__ import annotations

import asyncio
import logging
import time
from contextlib import suppress
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types."""

    TASK_UPDATE = "task_update"
    AGENT_STATUS = "agent_status"
    METRICS = "metrics"
    METRICS_UPDATE = "metrics_update"
    SECURITY_EVENT = "security_event"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


@dataclass
class WebSocketConnection:
    """Represents a WebSocket connection."""

    websocket: WebSocket
    client_id: str
    connected_at: float = field(default_factory=time.time)
    subscriptions: Set[str] = field(default_factory=set)
    last_ping: float = field(default_factory=time.time)

    def __hash__(self) -> int:
        return hash(self.client_id)


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self) -> None:
        self._connections: Dict[str, WebSocketConnection] = {}
        self._message_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self._broadcast_task: Optional[asyncio.Task[None]] = None
        self._ping_task: Optional[asyncio.Task[None]] = None
        self._running = False

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        connection = WebSocketConnection(
            websocket=websocket,
            client_id=client_id,
        )
        self._connections[client_id] = connection
        logger.info(f"WebSocket client connected: {client_id}")

        # Send welcome message
        await self._send_to_client(
            client_id,
            {
                "type": "connected",
                "client_id": client_id,
                "timestamp": time.time(),
            },
        )

    def disconnect(self, client_id: str) -> None:
        """Remove a WebSocket connection."""
        if client_id in self._connections:
            del self._connections[client_id]
            logger.info(f"WebSocket client disconnected: {client_id}")

    async def subscribe(self, client_id: str, channels: List[str]) -> None:
        """Subscribe a client to specific channels."""
        if client_id in self._connections:
            conn = self._connections[client_id]
            conn.subscriptions.update(channels)
            logger.debug(f"Client {client_id} subscribed to {channels}")
            await self._send_to_client(
                client_id,
                {
                    "type": "subscribed",
                    "channels": list(conn.subscriptions),
                    "timestamp": time.time(),
                },
            )

    async def unsubscribe(self, client_id: str, channels: List[str]) -> None:
        """Unsubscribe a client from specific channels."""
        if client_id in self._connections:
            conn = self._connections[client_id]
            conn.subscriptions.difference_update(channels)
            logger.debug(f"Client {client_id} unsubscribed from {channels}")
            await self._send_to_client(
                client_id,
                {
                    "type": "unsubscribed",
                    "channels": list(conn.subscriptions),
                    "timestamp": time.time(),
                },
            )

    async def broadcast(
        self, message_type: MessageType, data: Dict[str, Any], channel: str = "all"
    ) -> None:
        """Broadcast a message to all subscribed clients."""
        message = {
            "type": message_type.value,
            "data": data,
            "channel": channel,
            "timestamp": time.time(),
        }
        await self._message_queue.put(message)

    async def _send_to_client(self, client_id: str, message: Dict[str, Any]) -> None:
        """Send a message to a specific client."""
        if client_id not in self._connections:
            return

        conn = self._connections[client_id]
        try:
            await conn.websocket.send_json(message)
        except Exception as exc:
            logger.warning(f"Failed to send to client {client_id}: {exc}")
            self.disconnect(client_id)

    async def _broadcast_worker(self) -> None:
        """Background worker that processes broadcast queue."""
        while self._running:
            try:
                # Get message from queue with timeout
                message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)

                channel = message.get("channel", "all") if isinstance(message, dict) else "all"

                # Broadcast to subscribed clients
                for client_id, conn in list(self._connections.items()):
                    # Check if client is subscribed to this channel
                    if channel == "all" or channel in conn.subscriptions:
                        await self._send_to_client(client_id, message)

            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.exception(f"Error in broadcast worker: {exc}")

    async def _ping_worker(self) -> None:
        """Background worker that sends periodic pings to check connection health."""
        while self._running:
            await asyncio.sleep(30)  # Ping every 30 seconds

            for client_id, conn in list(self._connections.items()):
                try:
                    await conn.websocket.send_json(
                        {
                            "type": MessageType.PING.value,
                            "timestamp": time.time(),
                        }
                    )
                    conn.last_ping = time.time()
                except Exception as exc:
                    logger.warning(f"Ping failed for client {client_id}: {exc}")
                    self.disconnect(client_id)

    async def start(self) -> None:
        """Start background workers."""
        if self._running:
            return

        self._running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_worker())
        self._ping_task = asyncio.create_task(self._ping_worker())
        logger.info("WebSocket manager started")

    async def stop(self) -> None:
        """Stop background workers and close all connections."""
        self._running = False

        # Cancel workers
        if self._broadcast_task:
            self._broadcast_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._broadcast_task

        if self._ping_task:
            self._ping_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._ping_task

        # Close all connections
        for client_id in list(self._connections.keys()):
            self.disconnect(client_id)

        logger.info("WebSocket manager stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            "active_connections": len(self._connections),
            "clients": [
                {
                    "client_id": conn.client_id,
                    "connected_at": conn.connected_at,
                    "subscriptions": list(conn.subscriptions),
                    "last_ping": conn.last_ping,
                }
                for conn in self._connections.values()
            ],
        }


# Global WebSocket manager instance
ws_manager = WebSocketManager()

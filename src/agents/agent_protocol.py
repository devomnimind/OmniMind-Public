#!/usr/bin/env python3
"""
Agent Communication Protocol - Protocolo de Comunicação Inter-Agentes

Fornece infraestrutura para comunicação padronizada entre agentes:
- Sistema de mensagens assíncronas
- Filas de eventos
- Tratamento de conflitos
- Contratos de mensagem tipados
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Prioridade de mensagens entre agentes"""

    CRITICAL = 0  # Emergências, falhas críticas
    HIGH = 1  # Requisições urgentes
    MEDIUM = 2  # Operações normais
    LOW = 3  # Informações, logs


class MessageType(Enum):
    """Tipos de mensagens no protocolo inter-agentes"""

    # Controle
    REQUEST = "request"  # Solicitação de ação
    RESPONSE = "response"  # Resposta a solicitação
    NOTIFICATION = "notification"  # Notificação sem resposta esperada
    ERROR = "error"  # Mensagem de erro

    # Coordenação
    TASK_DELEGATION = "task_delegation"  # Delegação de tarefa
    TASK_COMPLETE = "task_complete"  # Tarefa concluída
    TASK_FAILED = "task_failed"  # Tarefa falhou

    # Estado
    STATUS_UPDATE = "status_update"  # Atualização de status
    HEARTBEAT = "heartbeat"  # Ping de vida
    SHUTDOWN = "shutdown"  # Sinal de desligamento

    # Recursos
    RESOURCE_REQUEST = "resource_request"  # Requisição de recurso
    RESOURCE_GRANT = "resource_grant"  # Concessão de recurso
    RESOURCE_DENY = "resource_deny"  # Negação de recurso


@dataclass
class AgentMessage:
    """Mensagem padronizada entre agentes"""

    message_id: str
    message_type: MessageType
    sender: str
    recipient: str
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.MEDIUM
    timestamp: str = field(default_factory=lambda: _timestamp())
    correlation_id: Optional[str] = None  # Para rastrear conversas
    requires_response: bool = False
    timeout_seconds: int = 30

    def to_dict(self) -> Dict[str, Any]:
        """Serializa mensagem para dict"""
        data = asdict(self)
        data["message_type"] = self.message_type.value
        data["priority"] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgentMessage:
        """Deserializa mensagem de dict"""
        data["message_type"] = MessageType(data["message_type"])
        data["priority"] = MessagePriority(data["priority"])
        return cls(**data)


@dataclass
class ConflictResolution:
    """Informações de resolução de conflito entre agentes"""

    conflict_id: str
    agents_involved: List[str]
    conflict_type: str  # "resource", "task", "priority"
    resolution: str  # "timeout", "priority", "consensus"
    winner: Optional[str] = None
    timestamp: str = field(default_factory=lambda: _timestamp())


class AgentMessageBus:
    """
    Message Bus para comunicação inter-agentes.

    Implementa padrão publish-subscribe com filas priorizadas.
    """

    def __init__(self) -> None:
        self._queues: Dict[str, asyncio.Queue[AgentMessage]] = {}
        self._handlers: Dict[str, List[Callable[[AgentMessage], None]]] = {}
        self._subscriptions: Dict[str, Set[MessageType]] = {}
        self._pending_responses: Dict[str, asyncio.Future[AgentMessage]] = {}
        self._conflicts: List[ConflictResolution] = []
        self._running = False
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """Inicia o message bus"""
        self._running = True
        logger.info("AgentMessageBus started")

    async def stop(self) -> None:
        """Para o message bus"""
        self._running = False
        # Cancelar futures pendentes
        for future in self._pending_responses.values():
            if not future.done():
                future.cancel()
        logger.info("AgentMessageBus stopped")

    def register_agent(self, agent_id: str) -> None:
        """
        Registra um novo agente no message bus.

        Args:
            agent_id: Identificador único do agente
        """
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
            self._subscriptions[agent_id] = set()
            logger.info(f"Agent registered: {agent_id}")

    def unregister_agent(self, agent_id: str) -> None:
        """Remove agente do message bus"""
        if agent_id in self._queues:
            del self._queues[agent_id]
            del self._subscriptions[agent_id]
            if agent_id in self._handlers:
                del self._handlers[agent_id]
            logger.info(f"Agent unregistered: {agent_id}")

    def subscribe(
        self, agent_id: str, message_types: List[MessageType]
    ) -> None:
        """
        Inscreve agente para receber tipos específicos de mensagens.

        Args:
            agent_id: ID do agente
            message_types: Lista de tipos de mensagens
        """
        if agent_id not in self._subscriptions:
            self.register_agent(agent_id)

        self._subscriptions[agent_id].update(message_types)
        logger.debug(f"Agent {agent_id} subscribed to {message_types}")

    def add_handler(
        self, agent_id: str, handler: Callable[[AgentMessage], None]
    ) -> None:
        """
        Adiciona handler para processar mensagens recebidas.

        Args:
            agent_id: ID do agente
            handler: Função callback para processar mensagens
        """
        if agent_id not in self._handlers:
            self._handlers[agent_id] = []
        self._handlers[agent_id].append(handler)

    async def send_message(self, message: AgentMessage) -> None:
        """
        Envia mensagem para agente específico.

        Args:
            message: Mensagem a ser enviada
        """
        if not self._running:
            raise RuntimeError("MessageBus not running")

        recipient = message.recipient
        if recipient not in self._queues:
            logger.warning(f"Recipient {recipient} not registered")
            return

        # Verificar se destinatário está inscrito neste tipo de mensagem
        if message.message_type not in self._subscriptions.get(recipient, set()):
            logger.debug(
                f"Recipient {recipient} not subscribed to {message.message_type}"
            )
            # Ainda assim enviar, deixar agente decidir

        # Adicionar à fila do destinatário
        await self._queues[recipient].put(message)
        logger.debug(
            f"Message {message.message_id} sent from {message.sender} to {recipient}"
        )

    async def send_and_wait(
        self, message: AgentMessage, timeout: Optional[int] = None
    ) -> AgentMessage:
        """
        Envia mensagem e aguarda resposta.

        Args:
            message: Mensagem a enviar
            timeout: Timeout em segundos (usa message.timeout_seconds se None)

        Returns:
            Mensagem de resposta

        Raises:
            asyncio.TimeoutError: Se timeout expirar
        """
        message.requires_response = True
        future: asyncio.Future[AgentMessage] = asyncio.Future()
        self._pending_responses[message.message_id] = future

        await self.send_message(message)

        try:
            response = await asyncio.wait_for(
                future, timeout=timeout or message.timeout_seconds
            )
            return response
        finally:
            if message.message_id in self._pending_responses:
                del self._pending_responses[message.message_id]

    async def receive_message(
        self, agent_id: str, timeout: Optional[float] = None
    ) -> Optional[AgentMessage]:
        """
        Recebe próxima mensagem da fila do agente.

        Args:
            agent_id: ID do agente
            timeout: Timeout em segundos (None = espera indefinida)

        Returns:
            Mensagem recebida ou None se timeout
        """
        if agent_id not in self._queues:
            raise ValueError(f"Agent {agent_id} not registered")

        try:
            if timeout:
                message = await asyncio.wait_for(
                    self._queues[agent_id].get(), timeout=timeout
                )
            else:
                message = await self._queues[agent_id].get()

            # Processar handlers
            if agent_id in self._handlers:
                for handler in self._handlers[agent_id]:
                    try:
                        handler(message)
                    except Exception as exc:
                        logger.exception(
                            f"Error in handler for agent {agent_id}: {exc}"
                        )

            return message
        except asyncio.TimeoutError:
            return None

    async def respond_to_message(
        self, original_message: AgentMessage, response_payload: Dict[str, Any]
    ) -> None:
        """
        Responde a uma mensagem recebida.

        Args:
            original_message: Mensagem original
            response_payload: Dados da resposta
        """
        response = AgentMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.RESPONSE,
            sender=original_message.recipient,
            recipient=original_message.sender,
            payload=response_payload,
            correlation_id=original_message.message_id,
        )

        # Se há future aguardando, resolver
        if original_message.message_id in self._pending_responses:
            future = self._pending_responses[original_message.message_id]
            if not future.done():
                future.set_result(response)
        else:
            # Enviar normalmente
            await self.send_message(response)

    async def broadcast(
        self, sender: str, message_type: MessageType, payload: Dict[str, Any]
    ) -> None:
        """
        Broadcast mensagem para todos os agentes inscritos.

        Args:
            sender: ID do agente remetente
            message_type: Tipo da mensagem
            payload: Dados da mensagem
        """
        tasks = []
        for agent_id, subscriptions in self._subscriptions.items():
            if agent_id != sender and message_type in subscriptions:
                message = AgentMessage(
                    message_id=str(uuid.uuid4()),
                    message_type=message_type,
                    sender=sender,
                    recipient=agent_id,
                    payload=payload,
                )
                tasks.append(self.send_message(message))

        if tasks:
            await asyncio.gather(*tasks)

    def resolve_conflict(
        self, agents: List[str], conflict_type: str, resolution: str
    ) -> ConflictResolution:
        """
        Registra resolução de conflito entre agentes.

        Args:
            agents: Lista de agentes envolvidos
            conflict_type: Tipo do conflito
            resolution: Estratégia de resolução usada

        Returns:
            Registro de resolução
        """
        conflict = ConflictResolution(
            conflict_id=str(uuid.uuid4()),
            agents_involved=agents,
            conflict_type=conflict_type,
            resolution=resolution,
        )
        self._conflicts.append(conflict)
        logger.info(
            f"Conflict resolved: {conflict_type} between {agents} using {resolution}"
        )
        return conflict

    def get_queue_size(self, agent_id: str) -> int:
        """Retorna tamanho da fila de mensagens do agente"""
        if agent_id in self._queues:
            return self._queues[agent_id].qsize()
        return 0

    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do message bus"""
        return {
            "registered_agents": len(self._queues),
            "pending_responses": len(self._pending_responses),
            "total_conflicts": len(self._conflicts),
            "queue_sizes": {
                agent_id: queue.qsize()
                for agent_id, queue in self._queues.items()
            },
        }


def _timestamp() -> str:
    """Retorna timestamp UTC ISO"""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# Singleton global do message bus
_global_message_bus: Optional[AgentMessageBus] = None


def get_message_bus() -> AgentMessageBus:
    """Obtém instância global do message bus"""
    global _global_message_bus
    if _global_message_bus is None:
        _global_message_bus = AgentMessageBus()
    return _global_message_bus


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = [
    "AgentMessage",
    "MessageType",
    "MessagePriority",
    "AgentMessageBus",
    "ConflictResolution",
    "get_message_bus",
]

"""
OrchestratorEventBus - Bus de eventos priorizado para Orchestrator.

Implementa recomendações da Seção 3 da AUDITORIA_ORCHESTRATOR_COMPLETA.md:
- Pipeline de eventos com priorização
- Debouncing para evitar spam de eventos
- Integração de sensores com Orchestrator
- Resposta em tempo real para eventos críticos
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from ..security.security_agent import SecurityEvent

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Prioridade de eventos."""

    CRITICAL = 0  # Ameaças imediatas, falhas críticas
    HIGH = 1  # Anomalias de segurança, falhas de agentes
    MEDIUM = 2  # Eventos normais de monitoramento
    LOW = 3  # Informações, métricas


@dataclass
class OrchestratorEvent:
    """Evento genérico do Orchestrator."""

    event_type: str
    source: str
    priority: EventPriority
    data: Dict[str, Any]
    timestamp: float


class OrchestratorEventBus:
    """Bus de eventos priorizado para coordenação do Orchestrator."""

    def __init__(self, debounce_window: float = 5.0) -> None:
        """Inicializa EventBus.

        Args:
            debounce_window: Janela de debounce em segundos (padrão: 5s)
        """
        self._queues: Dict[EventPriority, asyncio.PriorityQueue] = {
            EventPriority.CRITICAL: asyncio.PriorityQueue(),
            EventPriority.HIGH: asyncio.PriorityQueue(),
            EventPriority.MEDIUM: asyncio.PriorityQueue(),
            EventPriority.LOW: asyncio.PriorityQueue(),
        }
        self._handlers: Dict[str, List[Callable]] = {}
        self._debounce_cache: Dict[str, float] = {}
        self._debounce_window = debounce_window
        self._running = False
        self._processing_task: Optional[asyncio.Task] = None

    def _get_event_key(self, event: OrchestratorEvent) -> str:
        """Gera chave única para debouncing.

        Args:
            event: Evento a processar

        Returns:
            Chave única baseada em tipo e fonte
        """
        return f"{event.event_type}:{event.source}"

    def _should_debounce(self, event: OrchestratorEvent) -> bool:
        """Verifica se evento deve ser debounced.

        Args:
            event: Evento a verificar

        Returns:
            True se evento deve ser ignorado (debounced)
        """
        event_key = self._get_event_key(event)
        now = time.time()

        if event_key in self._debounce_cache:
            last_time = self._debounce_cache[event_key]
            if now - last_time < self._debounce_window:
                logger.debug(
                    "Evento %s debounced (última ocorrência há %.2fs)",
                    event_key,
                    now - last_time,
                )
                return True

        self._debounce_cache[event_key] = now
        return False

    async def publish(self, event: OrchestratorEvent) -> None:
        """Publica evento no bus.

        Args:
            event: Evento a publicar
        """
        # Eventos críticos nunca são debounced
        if event.priority != EventPriority.CRITICAL and self._should_debounce(event):
            return

        # Adicionar à fila apropriada com timestamp como tiebreaker
        queue = self._queues[event.priority]
        await queue.put((event.priority.value, event.timestamp, event))

        logger.debug(
            "Evento publicado: %s (prioridade: %s)",
            event.event_type,
            event.priority.name,
        )

    async def publish_security_event(
        self, security_event: SecurityEvent, priority: Optional[EventPriority] = None
    ) -> None:
        """Publica evento de segurança no bus.

        Args:
            security_event: Evento de segurança
            priority: Prioridade (inferida do threat_level se não especificada)
        """
        if priority is None:
            # Mapear ThreatLevel para EventPriority
            threat_to_priority = {
                "CRITICAL": EventPriority.CRITICAL,
                "HIGH": EventPriority.HIGH,
                "MEDIUM": EventPriority.MEDIUM,
                "LOW": EventPriority.LOW,
            }
            priority = threat_to_priority.get(
                security_event.threat_level.name, EventPriority.MEDIUM
            )

        event = OrchestratorEvent(
            event_type=f"security_{security_event.event_type}",
            source=security_event.source,
            priority=priority,
            data={
                "timestamp": security_event.timestamp,
                "description": security_event.description,
                "details": security_event.details,
                "threat_level": security_event.threat_level.name,
                "id": security_event.id,
            },
            timestamp=time.time(),
        )

        await self.publish(event)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Registra handler para tipo de evento.

        Args:
            event_type: Tipo de evento (ou "*" para todos)
            handler: Função handler async
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.info("Handler registrado para evento: %s", event_type)

    async def _process_event(self, event: OrchestratorEvent) -> None:
        """Processa um evento chamando handlers registrados.

        Args:
            event: Evento a processar
        """
        # Handlers específicos para o tipo de evento
        handlers = self._handlers.get(event.event_type, [])

        # Handlers globais (registrados com "*")
        handlers.extend(self._handlers.get("*", []))

        if not handlers:
            logger.debug("Nenhum handler registrado para evento: %s", event.event_type)
            return

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(
                    "Erro ao processar evento %s com handler %s: %s",
                    event.event_type,
                    handler.__name__,
                    e,
                )

    async def start_processing(self) -> None:
        """Inicia processamento de eventos."""
        if self._running:
            logger.warning("EventBus já está processando eventos")
            return

        self._running = True
        logger.info("EventBus iniciado")

        try:
            while self._running:
                # Processar eventos em ordem de prioridade
                event_processed = False

                for priority in EventPriority:
                    queue = self._queues[priority]

                    if not queue.empty():
                        try:
                            _, _, event = await asyncio.wait_for(queue.get(), timeout=0.1)
                            await self._process_event(event)
                            event_processed = True
                            break  # Processar um evento de cada vez
                        except asyncio.TimeoutError:
                            continue

                # Se nenhum evento foi processado, aguardar um pouco
                if not event_processed:
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("EventBus cancelado")
        except Exception as e:
            logger.error("Erro no loop de processamento do EventBus: %s", e)
        finally:
            self._running = False

    async def stop_processing(self) -> None:
        """Para processamento de eventos."""
        if not self._running:
            return

        logger.info("Parando EventBus")
        self._running = False

        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

    def get_queue_sizes(self) -> Dict[str, int]:
        """Obtém tamanho de cada fila de prioridade.

        Returns:
            Dicionário com tamanhos das filas
        """
        return {priority.name: queue.qsize() for priority, queue in self._queues.items()}

    def clear_debounce_cache(self) -> None:
        """Limpa cache de debouncing."""
        self._debounce_cache.clear()
        logger.debug("Cache de debouncing limpo")

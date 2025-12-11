"""
EventMetricsListener - Captura de Métricas de Eventos do EventBus

Implementa Task 2.2.1 do Sprint 2: Integração com EventBus
Captura todos os eventos e registra métricas para observabilidade completa.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-11
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.orchestrator.event_bus import OrchestratorEvent

logger = logging.getLogger(__name__)


@dataclass
class EventMetrics:
    """Métricas capturadas de um evento."""

    event_name: str
    timestamp: float
    phase: str
    duration_ms: float
    cycle_id: Optional[int]
    trace_id: Optional[str]
    source: str
    priority: str


class EventMetricsListener:
    """
    Listener que captura métricas de todos os eventos do EventBus.

    Características:
    - Subscribe em todos os eventos (event_type="*")
    - Captura event_name, timestamp, phase, duration
    - Correlaciona com ciclo_id quando disponível
    - Registra via record_metric() para persistência
    """

    def __init__(self, enable_metrics: bool = True):
        """
        Inicializa EventMetricsListener.

        Args:
            enable_metrics: Se True, registra métricas via ModuleMetricsCollector
        """
        self.enable_metrics = enable_metrics
        self._event_count = 0
        self._event_start_times: Dict[str, float] = {}
        self._current_cycle_id: Optional[int] = None
        self._logger = logger.getChild(self.__class__.__name__)

        # Lazy import para evitar circular dependencies
        self._metrics_collector = None

        self._logger.info("EventMetricsListener inicializado")

    def _get_metrics_collector(self) -> Any:
        """
        Obtém o ModuleMetricsCollector (lazy loading).

        Returns:
            ModuleMetricsCollector instance ou None se não disponível
        """
        if self._metrics_collector is None and self.enable_metrics:
            try:
                from src.observability.module_metrics import get_module_metrics

                self._metrics_collector = get_module_metrics()
                self._logger.debug("ModuleMetricsCollector carregado")
            except ImportError as e:
                self._logger.warning(f"ModuleMetricsCollector não disponível: {e}")

        return self._metrics_collector

    def set_current_cycle_id(self, cycle_id: int) -> None:
        """
        Define o ciclo_id atual para correlação de eventos.

        Args:
            cycle_id: ID do ciclo de consciência atual
        """
        self._current_cycle_id = cycle_id
        self._logger.debug(f"Ciclo atual definido: {cycle_id}")

    async def handle_event(self, event: OrchestratorEvent) -> None:
        """
        Handler assíncrono chamado para cada evento publicado no EventBus.

        Args:
            event: Evento do EventBus
        """
        self._event_count += 1

        # Detectar fase do evento (started, completed, etc.)
        phase = "unknown"
        if "started" in event.event_type:
            phase = "started"
            # Registrar tempo de início para calcular duração
            self._event_start_times[event.event_type.replace(".started", "")] = event.timestamp
        elif "completed" in event.event_type:
            phase = "completed"
        elif "failed" in event.event_type:
            phase = "failed"
        elif "generated" in event.event_type:
            phase = "generated"

        # Calcular duração se for evento de conclusão
        duration_ms = 0.0
        if phase == "completed":
            base_event_type = event.event_type.replace(".completed", "")
            if base_event_type in self._event_start_times:
                start_time = self._event_start_times.pop(base_event_type)
                duration_ms = (event.timestamp - start_time) * 1000.0

        # Criar objeto de métricas
        event_metrics = EventMetrics(
            event_name=event.event_type,
            timestamp=event.timestamp,
            phase=phase,
            duration_ms=duration_ms,
            cycle_id=self._current_cycle_id,
            trace_id=event.trace_id,
            source=event.source,
            priority=event.priority.name,
        )

        # Registrar métricas
        self._record_event_metrics(event_metrics)

        self._logger.debug(
            f"Evento capturado: {event.event_type} (fase={phase}, "
            f"ciclo={self._current_cycle_id}, trace_id={event.trace_id})"
        )

    def _record_event_metrics(self, event_metrics: EventMetrics) -> None:
        """
        Registra métricas do evento via ModuleMetricsCollector.

        Args:
            event_metrics: Métricas do evento a registrar
        """
        if not self.enable_metrics:
            return

        metrics_collector = self._get_metrics_collector()
        if metrics_collector is None:
            return

        try:
            # Nome do módulo baseado no evento
            # Exemplo: "event_consciousness.cycle.completed"
            module_name = f"event_{event_metrics.event_name}"

            labels = {
                "phase": event_metrics.phase,
                "source": event_metrics.source,
                "priority": event_metrics.priority,
            }

            if event_metrics.cycle_id is not None:
                labels["cycle"] = event_metrics.cycle_id

            if event_metrics.trace_id is not None:
                labels["trace_id"] = event_metrics.trace_id

            # Registrar latência do evento
            if event_metrics.duration_ms > 0:
                metrics_collector.record_metric(
                    module_name=module_name,
                    metric_name="event_latency_ms",
                    value=float(event_metrics.duration_ms),
                    labels=labels,
                )

            # Registrar timestamp do evento
            metrics_collector.record_metric(
                module_name=module_name,
                metric_name="event_timestamp",
                value=float(event_metrics.timestamp),
                labels=labels,
            )

            # Registrar sequência do evento (ordem no ciclo)
            metrics_collector.record_metric(
                module_name=module_name,
                metric_name="event_sequence",
                value=int(self._event_count),
                labels=labels,
            )

            # Tentar correlacionar com Φ se disponível
            # Isso requer acesso ao workspace/conscious_system
            # Para agora, registrar placeholder
            # TODO: Implementar correlação com Φ via workspace
            # metrics_collector.record_metric(
            #     module_name=module_name,
            #     metric_name="event_correlation_with_phi",
            #     value=0.0,  # Placeholder
            #     labels=labels,
            # )

        except Exception as e:
            self._logger.debug(f"Falha ao registrar métricas do evento: {e}")

    def get_event_count(self) -> int:
        """
        Retorna o número total de eventos capturados.

        Returns:
            Contagem de eventos
        """
        return self._event_count

    def reset_event_count(self) -> None:
        """Reseta a contagem de eventos."""
        self._event_count = 0
        self._logger.debug("Contagem de eventos resetada")


# Singleton global
_event_metrics_listener: Optional[EventMetricsListener] = None


def get_event_metrics_listener() -> EventMetricsListener:
    """
    Obtém a instância singleton do EventMetricsListener.

    Returns:
        EventMetricsListener instance
    """
    global _event_metrics_listener
    if _event_metrics_listener is None:
        _event_metrics_listener = EventMetricsListener()
    return _event_metrics_listener


def init_event_metrics_listener(event_bus: Any) -> EventMetricsListener:
    """
    Inicializa EventMetricsListener e registra no EventBus.

    Args:
        event_bus: Instância do OrchestratorEventBus

    Returns:
        EventMetricsListener instance
    """
    listener = get_event_metrics_listener()

    # Subscribe para todos os eventos
    event_bus.subscribe("*", listener.handle_event)

    logger.info("✅ EventMetricsListener registrado no EventBus (capturando todos os eventos)")

    return listener

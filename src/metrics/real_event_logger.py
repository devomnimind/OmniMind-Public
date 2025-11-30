"""
Real Event Log System - Sistema de logging estruturado para o dashboard.

Substitui os eventos hardcoded por logs reais do sistema baseados em:
- IntegrationLoop execution events
- System state changes
- Error conditions
- Performance metrics

Author: This work was conceived by Fabrício da Silva and implemented with AI assistance
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RealEvent:
    """Evento real do sistema."""

    timestamp: str
    type: str  # SUCCESS, WARNING, ERROR, INFO
    message: str
    metric: str = ""  # Métrica relacionada (phi, anxiety, etc.)
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


class RealEventLogger:
    """Logger de eventos reais para o dashboard."""

    def __init__(self, max_events: int = 50):
        self.events: List[RealEvent] = []
        self.max_events = max_events
        self.log_file = Path("data/logs/real_events.jsonl")

        # Garante que o diretório existe
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Carrega eventos existentes
        self._load_existing_events()

        logger.info("RealEventLogger initialized")

    def _load_existing_events(self) -> None:
        """Carrega eventos existentes do arquivo."""
        if not self.log_file.exists():
            return

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        event_data = json.loads(line)
                        event = RealEvent(**event_data)
                        self.events.append(event)

            # Mantém apenas os eventos mais recentes
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events :]

            logger.info(f"Loaded {len(self.events)} existing events")

        except Exception as e:
            logger.error(f"Error loading existing events: {e}")

    def log_phi_change(self, old_phi: float, new_phi: float) -> None:
        """Log mudança no valor de Phi."""
        change_percent = ((new_phi - old_phi) / max(abs(old_phi), 0.001)) * 100

        if abs(change_percent) > 10:  # Mudança significativa
            event_type = "SUCCESS" if new_phi > old_phi else "WARNING"
            message = f"Phi changed by {change_percent:+.2f}% (from {old_phi:.3f} to {new_phi:.3f})"
            self._add_event(event_type, message, "phi", old_phi, new_phi)

    def log_anxiety_change(self, old_anxiety: float, new_anxiety: float) -> None:
        """Log mudança no nível de anxiety."""
        change = new_anxiety - old_anxiety

        if abs(change) > 0.1:  # Mudança significativa
            if new_anxiety > 0.6:
                event_type = "WARNING"
                message = f"Anxiety increased to {new_anxiety:.2f} (high level)"
            elif new_anxiety < 0.2:
                event_type = "SUCCESS"
                message = f"Anxiety decreased to {new_anxiety:.2f} (low level)"
            else:
                event_type = "INFO"
                message = f"Anxiety changed to {new_anxiety:.2f}"
            self._add_event(event_type, message, "anxiety", old_anxiety, new_anxiety)

    def log_flow_change(self, old_flow: float, new_flow: float) -> None:
        """Log mudança no estado de flow."""
        change = new_flow - old_flow

        if abs(change) > 0.15:  # Mudança significativa
            if new_flow < 0.3:
                event_type = "WARNING"
                message = f"Flow decreased to {new_flow:.2f} (cognitive blockage)"
            elif new_flow > 0.7:
                event_type = "SUCCESS"
                message = f"Flow increased to {new_flow:.2f} (fluent cognition)"
            else:
                event_type = "INFO"
                message = f"Flow changed to {new_flow:.2f}"
            self._add_event(event_type, message, "flow", old_flow, new_flow)

    def log_integration_cycle(self, cycle_number: int, phi: float, success: bool) -> None:
        """Log conclusão de ciclo de integração."""
        if success:
            if phi > 0.5:
                event_type = "SUCCESS"
                message = (
                    f"Integration cycle {cycle_number} completed with "
                    f"strong integration (Φ={phi:.3f})"
                )
            else:
                event_type = "INFO"
                message = f"Integration cycle {cycle_number} completed (Φ={phi:.3f})"
        else:
            event_type = "ERROR"
            message = f"Integration cycle {cycle_number} failed (Φ={phi:.3f})"

        self._add_event(event_type, message, "integration_cycle")

    def log_system_health_change(self, component: str, old_status: str, new_status: str) -> None:
        """Log mudança no status de saúde do sistema."""
        if old_status != new_status:
            if new_status == "healthy":
                event_type = "SUCCESS"
                message = f"{component} health improved to {new_status}"
            elif new_status == "unhealthy":
                event_type = "ERROR"
                message = f"{component} health degraded to {new_status}"
            else:
                event_type = "WARNING"
                message = f"{component} health changed to {new_status}"

            self._add_event(event_type, message, "system_health")

    def log_error(self, component: str, error_message: str) -> None:
        """Log erro no sistema."""
        message = f"Error in {component}: {error_message}"
        self._add_event("ERROR", message, "error")

    def log_performance_issue(
        self, component: str, metric: str, value: float, threshold: float
    ) -> None:
        """Log problema de performance."""
        message = (
            f"Performance issue in {component}: {metric}={value:.2f} "
            f"(threshold: {threshold:.2f})"
        )
        self._add_event("WARNING", message, "performance")

    def _add_event(
        self,
        event_type: str,
        message: str,
        metric: str = "",
        old_value: Optional[float] = None,
        new_value: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Adiciona evento ao log."""

        event = RealEvent(
            timestamp=datetime.now().isoformat(),
            type=event_type,
            message=message,
            metric=metric,
            old_value=old_value,
            new_value=new_value,
            details=details or {},
        )

        self.events.append(event)

        # Mantém apenas os eventos mais recentes
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events :]

        # Salva no arquivo
        self._save_event(event)

        logger.info(f"Logged real event: {event_type} - {message}")

    def _save_event(self, event: RealEvent) -> None:
        """Salva evento no arquivo."""
        try:
            with open(self.log_file, "a") as f:
                json.dump(event.__dict__, f)
                f.write("\n")
        except Exception as e:
            logger.error(f"Error saving event to file: {e}")

    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna eventos recentes para o dashboard."""
        recent_events = self.events[-limit:] if len(self.events) >= limit else self.events

        return [
            {
                "timestamp": event.timestamp,
                "type": event.type,
                "message": event.message,
                "metric": event.metric,
                "old_value": event.old_value,
                "new_value": event.new_value,
            }
            for event in recent_events
        ]

    def get_events_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """Retorna eventos por tipo."""
        filtered_events = [e for e in self.events if e.type == event_type]
        return [
            {
                "timestamp": event.timestamp,
                "type": event.type,
                "message": event.message,
                "metric": event.metric,
                "old_value": event.old_value,
                "new_value": event.new_value,
            }
            for event in filtered_events[-20:]  # Últimos 20
        ]

    def clear_old_events(self, days: int = 7) -> None:
        """Remove eventos antigos."""
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        self.events = [
            event
            for event in self.events
            if datetime.fromisoformat(event.timestamp).timestamp() > cutoff_time
        ]

        logger.info(f"Cleared old events, {len(self.events)} events remaining")


# Instância global do logger de eventos
real_event_logger = RealEventLogger()


def get_recent_events(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Função wrapper para obter eventos recentes.

    Args:
        limit: Número máximo de eventos a retornar

    Returns:
        Lista de eventos recentes
    """
    return real_event_logger.get_recent_events(limit)

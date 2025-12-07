#!/usr/bin/env python3
"""
Real-time Alerting System for OmniMind
WebSocket-based real-time security and compliance alerts.

Features:
- Real-time alert broadcasting via WebSocket
- Alert severity levels and routing
- Alert history and analytics
- Integration with audit system
"""

import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from .immutable_audit import ImmutableAuditSystem, get_audit_system


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertCategory(Enum):
    """Alert categories."""

    SECURITY = "security"
    COMPLIANCE = "compliance"
    SYSTEM = "system"
    AUDIT = "audit"
    PERFORMANCE = "performance"
    # Tipos específicos do AlertSystem (monitor)
    PERMISSION_ERROR = "permission_error"
    RESOURCE_CRITICAL = "resource_critical"
    RESOURCE_WARNING = "resource_warning"
    SERVER_DOWN = "server_down"
    SERVER_STARTING = "server_starting"
    SERVER_SLOW = "server_slow"
    SERVER_RECOVERED = "server_recovered"
    TEST_TIMEOUT = "test_timeout"
    TEST_FAILED = "test_failed"
    TEST_PASSED = "test_passed"


@dataclass
class Alert:
    """Alert data structure."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    severity: AlertSeverity = AlertSeverity.INFO
    category: AlertCategory = AlertCategory.SYSTEM
    title: str = ""
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    source: str = "omnimind"
    acknowledged: bool = False
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "severity": self.severity.value,
            "category": self.category.value,
            "title": self.title,
            "message": self.message,
            "details": self.details,
            "source": self.source,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Alert":
        """Create alert from dictionary."""
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            severity=AlertSeverity(data.get("severity", "info")),
            category=AlertCategory(data.get("category", "system")),
            title=data.get("title", ""),
            message=data.get("message", ""),
            details=data.get("details", {}),
            source=data.get("source", "omnimind"),
            acknowledged=data.get("acknowledged", False),
            resolved=data.get("resolved", False),
        )


class AlertingSystem:
    """
    Real-time alerting system with WebSocket support.

    Features:
    - Alert generation and broadcasting
    - Alert routing based on severity
    - Alert history and persistence
    - WebSocket subscription management
    """

    def __init__(self, audit_system: Optional[ImmutableAuditSystem] = None):
        """
        Initialize unified alerting system.

        Args:
            audit_system: Optional audit system instance
        """
        self.audit_system = audit_system or get_audit_system()
        self.alerts_dir = self.audit_system.log_dir / "alerts"
        self.alerts_dir.mkdir(parents=True, exist_ok=True)

        # Arquivo principal (JSONL)
        self.alerts_file = self.alerts_dir / "alerts.jsonl"

        # Diretório para alertas individuais (compatibilidade com AlertSystem)
        self.data_alerts_dir = Path("data/alerts")
        self.data_alerts_dir.mkdir(parents=True, exist_ok=True)

        self.active_alerts: Dict[str, Alert] = {}
        self.subscribers: Set[Callable[..., None]] = set()

        # Rate limiting (do AlertSystem)
        self.alert_cache: Dict[str, float] = {}
        self.cache_ttl = 60.0  # 1 minuto

        # Alert statistics
        self.stats: Dict[str, Any] = {
            "total_alerts": 0,
            "by_severity": {severity.value: 0 for severity in AlertSeverity},
            "by_category": {category.value: 0 for category in AlertCategory},
        }

        # Load existing alerts
        self._load_alerts()

        # Migrar alertas antigos do AlertSystem se existirem
        self._migrate_old_alerts()

    def _load_alerts(self) -> None:
        """Load existing alerts from file."""
        if not self.alerts_file.exists():
            return

        try:
            with open(self.alerts_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        alert_data = json.loads(line)
                        alert = Alert.from_dict(alert_data)
                        if not alert.resolved:
                            self.active_alerts[alert.id] = alert
                        self._update_stats(alert)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

    def _save_alert(self, alert: Alert) -> None:
        """Save alert to file (JSONL principal + JSON individual para compatibilidade)."""
        # Salvar no JSONL principal (audit)
        with open(self.alerts_file, "a") as f:
            f.write(json.dumps(alert.to_dict()) + "\n")

        # Salvar também como JSON individual (compatibilidade com AlertSystem)
        alert_file = self.data_alerts_dir / f"alert_{alert.id}.json"
        with open(alert_file, "w") as f:
            json.dump(alert.to_dict(), f, indent=2)

        # Atualizar índice
        self._update_alerts_index(alert)

    def _update_alerts_index(self, alert: Alert) -> None:
        """Atualiza índice de alertas (compatibilidade com AlertSystem)."""
        index_file = self.data_alerts_dir / "alerts_index.json"
        index = []
        if index_file.exists():
            try:
                with open(index_file, "r") as f:
                    index = json.load(f)
            except Exception:
                index = []

        # Adicionar novo alerta ao índice
        index.append(
            {
                "id": alert.id,
                "type": alert.category.value,
                "severity": alert.severity.value,
                "timestamp": alert.timestamp,
            }
        )

        # Manter apenas últimos 500 no índice
        index = index[-500:]

        with open(index_file, "w") as f:
            json.dump(index, f, indent=2)

    def _migrate_old_alerts(self) -> None:
        """Migra alertas antigos do AlertSystem (data/alerts/) para o sistema unificado."""
        if not self.data_alerts_dir.exists():
            return

        migrated_count = 0
        try:
            # Ler índice de alertas antigos
            index_file = self.data_alerts_dir / "alerts_index.json"
            if index_file.exists():
                with open(index_file, "r") as f:
                    old_index = json.load(f)

                # Migrar cada alerta
                for alert_entry in old_index:
                    alert_id = alert_entry.get("id", "")
                    if not alert_id:
                        continue

                    alert_file = self.data_alerts_dir / f"alert_{alert_id}.json"
                    if alert_file.exists():
                        try:
                            with open(alert_file, "r") as f:
                                old_alert_data = json.load(f)

                            # Converter para formato Alert
                            # Mapear severity e category
                            severity_str = old_alert_data.get("severity", "info")
                            category_str = old_alert_data.get("type", "system")

                            try:
                                severity = AlertSeverity(severity_str)
                            except ValueError:
                                severity = AlertSeverity.INFO

                            try:
                                category = AlertCategory(category_str)
                            except ValueError:
                                category = AlertCategory.SYSTEM

                            # Criar alerta se não existir
                            if alert_id not in self.active_alerts:
                                alert = Alert(
                                    id=alert_id,
                                    timestamp=old_alert_data.get(
                                        "datetime",
                                        old_alert_data.get(
                                            "timestamp", datetime.now(timezone.utc).isoformat()
                                        ),
                                    ),
                                    severity=severity,
                                    category=category,
                                    title=old_alert_data.get("title", ""),
                                    message=old_alert_data.get("message", ""),
                                    details=old_alert_data.get("context", {}),
                                    source=old_alert_data.get("source", "omnimind"),
                                )
                                self.active_alerts[alert.id] = alert
                                migrated_count += 1
                        except Exception:
                            # Ignorar erros de migração
                            pass
        except Exception:
            pass

        if migrated_count > 0:
            # Log da migração
            self.audit_system.log_action(
                "alerts_migrated",
                {"count": migrated_count, "source": "AlertSystem"},
                category="system",
            )

    def _find_cached_alert(self, cache_key: str) -> Optional[Alert]:
        """Encontra alerta em cache (para rate limiting)."""
        # Procurar em active_alerts por título similar
        for alert in self.active_alerts.values():
            if cache_key in alert.title.lower() or cache_key in alert.category.value:
                return alert
        return None

    def _update_stats(self, alert: Alert) -> None:
        """Update alert statistics."""
        self.stats["total_alerts"] += 1
        self.stats["by_severity"][alert.severity.value] += 1
        self.stats["by_category"][alert.category.value] += 1

    def create_alert(
        self,
        severity: AlertSeverity,
        category: AlertCategory,
        title: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        source: str = "omnimind",
        skip_rate_limit: bool = False,
    ) -> Alert:
        """
        Create and broadcast a new alert (unified system with rate limiting).

        Args:
            severity: Alert severity level
            category: Alert category
            title: Alert title
            message: Alert message
            details: Optional additional details
            source: Alert source identifier
            skip_rate_limit: Skip rate limiting (for critical alerts)

        Returns:
            Created Alert object
        """
        # Rate limiting (do AlertSystem)
        if not skip_rate_limit:
            cache_key = f"{category.value}_{title}"
            if cache_key in self.alert_cache:
                if time.time() - self.alert_cache[cache_key] < self.cache_ttl:
                    # Retornar alerta existente se ainda está no cache
                    existing = self._find_cached_alert(cache_key)
                    if existing:
                        return existing

            self.alert_cache[cache_key] = time.time()

        alert = Alert(
            severity=severity,
            category=category,
            title=title,
            message=message,
            details=details or {},
            source=source,
        )

        # Add to active alerts
        self.active_alerts[alert.id] = alert

        # Save to file
        self._save_alert(alert)

        # Update statistics
        self._update_stats(alert)

        # Log to audit system
        self.audit_system.log_action(
            "alert_created",
            {
                "alert_id": alert.id,
                "severity": alert.severity.value,
                "category": alert.category.value,
                "title": alert.title,
            },
            category="security",
        )

        # Broadcast to subscribers
        self._broadcast_alert(alert)

        return alert

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert ID to acknowledge

        Returns:
            True if alert was acknowledged, False if not found
        """
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.acknowledged = True

        # Save acknowledgment
        self._save_alert(alert)

        # Log to audit
        self.audit_system.log_action(
            "alert_acknowledged",
            {"alert_id": alert_id},
            category="security",
        )

        # Broadcast update
        self._broadcast_alert(alert)

        return True

    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """
        Resolve an alert.

        Args:
            alert_id: Alert ID to resolve
            resolution_notes: Optional resolution notes

        Returns:
            True if alert was resolved, False if not found
        """
        if alert_id not in self.active_alerts:
            return False

        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.details["resolution_notes"] = resolution_notes
        alert.details["resolved_at"] = datetime.now(timezone.utc).isoformat()

        # Save resolution
        self._save_alert(alert)

        # Remove from active alerts
        del self.active_alerts[alert_id]

        # Log to audit
        self.audit_system.log_action(
            "alert_resolved",
            {"alert_id": alert_id, "resolution_notes": resolution_notes},
            category="security",
        )

        # Broadcast update
        self._broadcast_alert(alert)

        return True

    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        category: Optional[AlertCategory] = None,
    ) -> List[Alert]:
        """
        Get active alerts, optionally filtered by severity or category.

        Args:
            severity: Optional severity filter
            category: Optional category filter

        Returns:
            List of matching active alerts
        """
        alerts = list(self.active_alerts.values())

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if category:
            alerts = [a for a in alerts if a.category == category]

        # Sort by timestamp (newest first)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)

        return alerts

    def get_alert_history(
        self,
        limit: int = 100,
        severity: Optional[AlertSeverity] = None,
        category: Optional[AlertCategory] = None,
    ) -> List[Alert]:
        """
        Get alert history.

        Args:
            limit: Maximum number of alerts to return
            severity: Optional severity filter
            category: Optional category filter

        Returns:
            List of historical alerts
        """
        alerts: list[Alert] = []

        if not self.alerts_file.exists():
            return alerts

        try:
            with open(self.alerts_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        alert_data = json.loads(line)
                        alert = Alert.from_dict(alert_data)

                        # Apply filters
                        if severity and alert.severity != severity:
                            continue
                        if category and alert.category != category:
                            continue

                        alerts.append(alert)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

        # Sort by timestamp (newest first) and limit
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return alerts[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get alerting statistics.

        Returns:
            Dict containing alert statistics
        """
        return {
            "total_alerts": self.stats["total_alerts"],
            "active_alerts": len(self.active_alerts),
            "by_severity": self.stats["by_severity"],
            "by_category": self.stats["by_category"],
            "critical_active": len(
                [a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]
            ),
        }

    def subscribe(self, callback: Callable[[Alert], None]) -> None:
        """
        Subscribe to alert notifications.

        Args:
            callback: Function to call when alerts are created
        """
        self.subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[Alert], None]) -> None:
        """
        Unsubscribe from alert notifications.

        Args:
            callback: Callback function to remove
        """
        self.subscribers.discard(callback)

    def _broadcast_alert(self, alert: Alert) -> None:
        """Broadcast alert to all subscribers."""
        for callback in self.subscribers:
            try:
                callback(alert)
            except Exception as e:
                # Log but don't fail
                self.audit_system.log_action(
                    "alert_broadcast_failed",
                    {"alert_id": alert.id, "error": str(e)},
                    category="system",
                )

    async def monitor_audit_chain(self, interval: int = 60) -> None:
        """
        Monitor audit chain integrity and create alerts on issues.

        Args:
            interval: Check interval in seconds
        """
        while True:
            try:
                integrity = self.audit_system.verify_chain_integrity()

                if not integrity["valid"]:
                    self.create_alert(
                        severity=AlertSeverity.CRITICAL,
                        category=AlertCategory.AUDIT,
                        title="Audit Chain Integrity Violation",
                        message="Audit chain integrity check failed",
                        details=integrity,
                        source="audit_monitor",
                    )

                await asyncio.sleep(interval)
            except Exception as e:
                self.create_alert(
                    severity=AlertSeverity.ERROR,
                    category=AlertCategory.SYSTEM,
                    title="Audit Monitor Error",
                    message=f"Error in audit monitoring: {str(e)}",
                    source="audit_monitor",
                )
                await asyncio.sleep(interval)


# Global instance
_alerting_system: Optional[AlertingSystem] = None


def get_alerting_system() -> AlertingSystem:
    """Get singleton alerting system instance."""
    global _alerting_system
    if _alerting_system is None:
        _alerting_system = AlertingSystem()
    return _alerting_system


def create_alert(
    severity: AlertSeverity,
    category: AlertCategory,
    title: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Alert:
    """Create alert using global alerting system."""
    return get_alerting_system().create_alert(severity, category, title, message, details)


def get_active_alerts() -> List[Alert]:
    """Get active alerts from global alerting system."""
    return get_alerting_system().get_active_alerts()

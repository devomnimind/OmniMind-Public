import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from .immutable_audit import ImmutableAuditSystem, get_audit_system

#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Real-time Alerting System for OmniMind
WebSocket-based real-time security and compliance alerts.

Features:
- Real-time alert broadcasting via WebSocket
- Alert severity levels and routing
- Alert history and analytics
- Integration with audit system
"""


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
        Initialize alerting system.

        Args:
            audit_system: Optional audit system instance
        """
        self.audit_system = audit_system or get_audit_system()
        self.alerts_dir = self.audit_system.log_dir / "alerts"
        self.alerts_dir.mkdir(parents=True, exist_ok=True)

        self.alerts_file = self.alerts_dir / "alerts.jsonl"
        self.active_alerts: Dict[str, Alert] = {}
        self.subscribers: Set[Callable[..., None]] = set()

        # Alert statistics
        self.stats: Dict[str, Any] = {
            "total_alerts": 0,
            "by_severity": {severity.value: 0 for severity in AlertSeverity},
            "by_category": {category.value: 0 for category in AlertCategory},
        }

        # Load existing alerts
        self._load_alerts()

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
        """Save alert to file."""
        with open(self.alerts_file, "a") as f:
            f.write(json.dumps(alert.to_dict()) + "\n")

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
    ) -> Alert:
        """
        Create and broadcast a new alert.

        Args:
            severity: Alert severity level
            category: Alert category
            title: Alert title
            message: Alert message
            details: Optional additional details
            source: Alert source identifier

        Returns:
            Created Alert object
        """
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

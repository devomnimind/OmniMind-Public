from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Union


@dataclass
class AtlasInsight:
    timestamp: str
    metric: str
    value: float
    status: str
    details: Dict[str, Any]


class AutonomyObservability:
    """Runtime observability store for autonomy telemetry."""

    def __init__(self, history_limit: int = 20) -> None:
        self.history_limit = history_limit
        self.self_healing_history: List[Dict[str, Any]] = []
        self.atlas_insights: List[AtlasInsight] = []
        self.alerts: List[str] = []
        self.sandbox_events: List[Dict[str, Any]] = []
        self.dlp_alerts: List[Dict[str, Any]] = []
        self.last_self_healing: Dict[str, Any] = {}

    def record_self_healing_metrics(self, payload: Dict[str, Any]) -> None:
        self.last_self_healing = payload
        self.self_healing_history.append(payload)
        if len(self.self_healing_history) > self.history_limit:
            self.self_healing_history.pop(0)

    def record_alert(self, message: str) -> None:
        self.alerts.append(message)
        if len(self.alerts) > self.history_limit:
            self.alerts.pop(0)

    def record_atlas_insight(
        self, insight: Union[AtlasInsight, Dict[str, Any]]
    ) -> None:
        if isinstance(insight, dict):
            insight = AtlasInsight(**insight)
        self.atlas_insights.append(insight)
        if len(self.atlas_insights) > self.history_limit:
            self.atlas_insights.pop(0)

    def get_self_healing_snapshot(self) -> Dict[str, Any]:
        preview = self.self_healing_history[-5:]
        return {
            "latest": self.last_self_healing,
            "history": preview,
            "alerts": list(self.alerts[-5:]),
        }

    def get_atlas_snapshot(self) -> Dict[str, Any]:
        return {
            "insights": [insight.__dict__ for insight in self.atlas_insights[-10:]],
        }

    def record_sandbox_event(self, metadata: Dict[str, Any]) -> None:
        timestamped = {
            "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
            **metadata,
        }
        self.sandbox_events.append(timestamped)
        if len(self.sandbox_events) > self.history_limit:
            self.sandbox_events.pop(0)

    def record_dlp_alert(self, alert: Dict[str, Any]) -> None:
        timestamped = {
            "timestamp": alert.get("timestamp", datetime.utcnow().isoformat()),
            **alert,
        }
        self.dlp_alerts.append(timestamped)
        if len(self.dlp_alerts) > self.history_limit:
            self.dlp_alerts.pop(0)

    def get_security_snapshot(self) -> Dict[str, Any]:
        return {
            "sandbox_events": list(self.sandbox_events[-5:]),
            "dlp_alerts": list(self.dlp_alerts[-5:]),
        }


autonomy_observability = AutonomyObservability()

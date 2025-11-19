"""API routes for security events and monitoring."""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/security", tags=["security"])


class SecurityEventType(str, Enum):
    """Types of security events."""

    INTRUSION_ATTEMPT = "intrusion_attempt"
    MALWARE_DETECTED = "malware_detected"
    ROOTKIT_DETECTED = "rootkit_detected"
    SUSPICIOUS_PROCESS = "suspicious_process"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    FILE_INTEGRITY_VIOLATION = "file_integrity_violation"
    NETWORK_ANOMALY = "network_anomaly"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"


class SecurityEventSeverity(str, Enum):
    """Security event severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEvent(BaseModel):
    """Security event model."""

    event_id: str
    event_type: SecurityEventType
    severity: SecurityEventSeverity
    timestamp: float
    source: str = Field(..., description="Source of the event")
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)
    resolved: bool = False
    resolution: Optional[str] = None


# In-memory security events storage
_security_events: List[Dict[str, Any]] = []


@router.get("/events", response_model=List[SecurityEvent])
async def list_security_events(
    event_type: Optional[SecurityEventType] = Query(
        None, description="Filter by event type"
    ),
    severity: Optional[SecurityEventSeverity] = Query(
        None, description="Filter by severity"
    ),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
) -> List[SecurityEvent]:
    """List security events with optional filtering."""
    events = _security_events.copy()

    # Apply filters
    if event_type:
        events = [e for e in events if e["event_type"] == event_type]
    if severity:
        events = [e for e in events if e["severity"] == severity]
    if resolved is not None:
        events = [e for e in events if e["resolved"] == resolved]

    # Sort by timestamp descending (newest first)
    events.sort(key=lambda e: e["timestamp"], reverse=True)

    # Apply limit
    events = events[:limit]

    return [SecurityEvent(**e) for e in events]


@router.get("/events/stats")
async def get_security_stats() -> Dict[str, Any]:
    """Get security event statistics."""
    total = len(_security_events)
    resolved = sum(1 for e in _security_events if e["resolved"])
    unresolved = total - resolved

    # Count by severity
    critical = sum(
        1 for e in _security_events if e["severity"] == SecurityEventSeverity.CRITICAL
    )
    high = sum(
        1 for e in _security_events if e["severity"] == SecurityEventSeverity.HIGH
    )
    medium = sum(
        1 for e in _security_events if e["severity"] == SecurityEventSeverity.MEDIUM
    )
    low = sum(
        1 for e in _security_events if e["severity"] == SecurityEventSeverity.LOW
    )

    return {
        "total_events": total,
        "resolved": resolved,
        "unresolved": unresolved,
        "by_severity": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
        "timestamp": time.time(),
    }


@router.get("/events/{event_id}", response_model=SecurityEvent)
async def get_security_event(event_id: str) -> SecurityEvent:
    """Get details of a specific security event."""
    event = next((e for e in _security_events if e["event_id"] == event_id), None)

    if not event:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail=f"Security event {event_id} not found"
        )

    return SecurityEvent(**event)


@router.post("/events/{event_id}/resolve")
async def resolve_security_event(
    event_id: str, resolution: str
) -> Dict[str, Any]:
    """Mark a security event as resolved."""
    event = next((e for e in _security_events if e["event_id"] == event_id), None)

    if not event:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail=f"Security event {event_id} not found"
        )

    event["resolved"] = True
    event["resolution"] = resolution

    logger.info(f"Resolved security event {event_id}: {resolution}")

    # Broadcast resolution via WebSocket
    from web.backend.websocket_manager import MessageType, ws_manager

    await ws_manager.broadcast(
        MessageType.SECURITY_EVENT,
        {
            "event": "event_resolved",
            "event_id": event_id,
            "resolution": resolution,
        },
        channel="security",
    )

    return {"status": "resolved", "event_id": event_id}


async def log_security_event(
    event_type: SecurityEventType,
    severity: SecurityEventSeverity,
    source: str,
    description: str,
    details: Optional[Dict[str, Any]] = None,
) -> str:
    """Log a security event (internal use)."""
    import uuid

    event_id = str(uuid.uuid4())
    event = {
        "event_id": event_id,
        "event_type": event_type,
        "severity": severity,
        "timestamp": time.time(),
        "source": source,
        "description": description,
        "details": details or {},
        "resolved": False,
        "resolution": None,
    }

    _security_events.append(event)
    logger.warning(
        f"Security event logged: {event_type.value} ({severity.value}) - {description}"
    )

    # Broadcast new event via WebSocket
    from web.backend.websocket_manager import MessageType, ws_manager

    await ws_manager.broadcast(
        MessageType.SECURITY_EVENT,
        {"event": "new_event", "security_event": event},
        channel="security",
    )

    return event_id

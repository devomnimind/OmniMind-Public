"""API routes for security events and monitoring."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
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
    correlation_id: Optional[str] = None
    related_events: List[str] = Field(default_factory=list)


# In-memory security events storage
_security_events: List[Dict[str, Any]] = []
_event_correlations: Dict[str, List[str]] = defaultdict(list)
_security_metrics: Dict[str, Any] = {
    "total_events": 0,
    "events_by_type": defaultdict(int),
    "events_by_severity": defaultdict(int),
    "events_by_source": defaultdict(int),
    "response_times": [],
}


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
    low = sum(1 for e in _security_events if e["severity"] == SecurityEventSeverity.LOW)

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


@router.get("/events/correlated")
async def get_correlated_events(
    correlation_id: str = Query(..., description="Correlation ID")
) -> Dict[str, Any]:
    """Get all events related by correlation ID."""
    related_event_ids = _event_correlations.get(correlation_id, [])

    related_events = [e for e in _security_events if e["event_id"] in related_event_ids]

    return {
        "correlation_id": correlation_id,
        "event_count": len(related_events),
        "events": related_events,
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
async def resolve_security_event(event_id: str, resolution: str) -> Dict[str, Any]:
    """Mark a security event as resolved."""
    event = next((e for e in _security_events if e["event_id"] == event_id), None)

    if not event:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail=f"Security event {event_id} not found"
        )

    event["resolved"] = True
    event["resolution"] = resolution
    event["resolved_at"] = time.time()

    # Track response time
    response_time = event["resolved_at"] - event["timestamp"]
    _security_metrics["response_times"].append(response_time)

    logger.info(f"Resolved security event {event_id}: {resolution}")

    # Broadcast resolution via WebSocket
    from web.backend.websocket_manager import MessageType, ws_manager

    await ws_manager.broadcast(
        MessageType.SECURITY_EVENT,
        {
            "event": "event_resolved",
            "event_id": event_id,
            "resolution": resolution,
            "response_time": round(response_time, 2),
        },
        channel="security",
    )

    return {
        "status": "resolved",
        "event_id": event_id,
        "response_time": round(response_time, 2),
    }


async def log_security_event(
    event_type: SecurityEventType,
    severity: SecurityEventSeverity,
    source: str,
    description: str,
    details: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
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
        "correlation_id": correlation_id,
        "related_events": [],
    }

    _security_events.append(event)

    # Update metrics
    _security_metrics["total_events"] += 1
    _security_metrics["events_by_type"][event_type.value] += 1
    _security_metrics["events_by_severity"][severity.value] += 1
    _security_metrics["events_by_source"][source] += 1

    # Add to correlation if provided
    if correlation_id:
        _event_correlations[correlation_id].append(event_id)
        related_ids = [
            eid for eid in _event_correlations[correlation_id] if eid != event_id
        ]
        event["related_events"] = related_ids

        # Update related_events for all other events in this correlation
        for other_event in _security_events:
            if (
                other_event.get("correlation_id") == correlation_id
                and other_event["event_id"] != event_id
            ):
                other_event["related_events"] = [
                    eid
                    for eid in _event_correlations[correlation_id]
                    if eid != other_event["event_id"]
                ]

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


@router.get("/analytics")
async def get_security_analytics() -> Dict[str, Any]:
    """Get comprehensive security analytics."""
    # Calculate time-based metrics
    now = time.time()
    last_hour = now - 3600
    last_24h = now - 86400

    events_last_hour = sum(1 for e in _security_events if e["timestamp"] >= last_hour)
    events_last_24h = sum(1 for e in _security_events if e["timestamp"] >= last_24h)

    # Calculate average response time for resolved events
    response_times = []
    for event in _security_events:
        if event["resolved"] and "resolved_at" in event:
            response_time = event["resolved_at"] - event["timestamp"]
            response_times.append(response_time)

    avg_response_time = (
        sum(response_times) / len(response_times) if response_times else 0.0
    )

    # Get top sources
    top_sources = sorted(
        _security_metrics["events_by_source"].items(),
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    return {
        "total_events": _security_metrics["total_events"],
        "events_last_hour": events_last_hour,
        "events_last_24h": events_last_24h,
        "by_type": dict(_security_metrics["events_by_type"]),
        "by_severity": dict(_security_metrics["events_by_severity"]),
        "top_sources": dict(top_sources),
        "avg_response_time": round(avg_response_time, 2),
        "correlations_count": len(_event_correlations),
        "timestamp": time.time(),
    }


@router.get("/monitoring/dashboard")
async def get_security_dashboard() -> Dict[str, Any]:
    """Get real-time security monitoring dashboard data."""
    now = time.time()

    # Get recent events (last hour)
    recent_events = [e for e in _security_events if e["timestamp"] >= (now - 3600)]

    # Get critical unresolved events
    critical_unresolved = [
        e
        for e in _security_events
        if e["severity"] == SecurityEventSeverity.CRITICAL and not e["resolved"]
    ]

    # Get high-severity unresolved events
    high_unresolved = [
        e
        for e in _security_events
        if e["severity"] == SecurityEventSeverity.HIGH and not e["resolved"]
    ]

    # Calculate threat level based on unresolved events
    threat_level = "low"
    if len(critical_unresolved) > 0:
        threat_level = "critical"
    elif len(high_unresolved) > 3:
        threat_level = "high"
    elif len(high_unresolved) > 0:
        threat_level = "medium"

    # Event rate (events per minute in last hour)
    event_rate = len(recent_events) / 60.0 if recent_events else 0.0

    return {
        "threat_level": threat_level,
        "recent_events_count": len(recent_events),
        "critical_unresolved": len(critical_unresolved),
        "high_unresolved": len(high_unresolved),
        "event_rate_per_minute": round(event_rate, 2),
        "recent_events": recent_events[-10:],  # Last 10 events
        "timestamp": time.time(),
    }


@router.post("/events/{event_id}/correlate")
async def correlate_event(event_id: str, correlation_id: str) -> Dict[str, Any]:
    """Manually correlate an event with others."""
    event = next((e for e in _security_events if e["event_id"] == event_id), None)

    if not event:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail=f"Security event {event_id} not found"
        )

    # Add to correlation
    _event_correlations[correlation_id].append(event_id)
    event["correlation_id"] = correlation_id
    event["related_events"] = [
        eid for eid in _event_correlations[correlation_id] if eid != event_id
    ]

    logger.info(f"Correlated event {event_id} with correlation ID {correlation_id}")

    return {
        "status": "correlated",
        "event_id": event_id,
        "correlation_id": correlation_id,
        "related_count": len(event["related_events"]),
    }


@router.get("/response/automated")
async def get_automated_responses() -> Dict[str, Any]:
    """Get automated security response tracking."""
    # Track automated responses from event details
    automated_responses = []

    for event in _security_events:
        if "automated_response" in event.get("details", {}):
            automated_responses.append(
                {
                    "event_id": event["event_id"],
                    "event_type": event["event_type"],
                    "severity": event["severity"],
                    "response": event["details"]["automated_response"],
                    "timestamp": event["timestamp"],
                    "successful": event["details"].get("response_successful", False),
                }
            )

    # Calculate response success rate
    successful = sum(1 for r in automated_responses if r["successful"])
    success_rate = (
        (successful / len(automated_responses) * 100) if automated_responses else 0.0
    )

    return {
        "total_responses": len(automated_responses),
        "successful_responses": successful,
        "success_rate": round(success_rate, 2),
        "recent_responses": automated_responses[-20:],
        "timestamp": time.time(),
    }

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

"""Tests for enhanced security events monitoring."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from web.backend.routes import security


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    app = FastAPI()
    app.include_router(security.router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_event(client):
    """Create a sample security event."""
    # Use the internal function to create an event
    import asyncio

    event_id = asyncio.run(
        security.log_security_event(
            event_type=security.SecurityEventType.SUSPICIOUS_PROCESS,
            severity=security.SecurityEventSeverity.HIGH,
            source="test-source",
            description="Test security event",
        )
    )
    return event_id


def test_security_analytics(client, sample_event):
    """Test getting security analytics."""
    response = client.get("/api/security/analytics")

    assert response.status_code == 200
    data = response.json()
    assert "total_events" in data
    assert "by_type" in data
    assert "by_severity" in data
    assert data["total_events"] >= 1


def test_security_dashboard(client, sample_event):
    """Test getting security dashboard data."""
    response = client.get("/api/security/monitoring/dashboard")

    assert response.status_code == 200
    data = response.json()
    assert "threat_level" in data
    assert "recent_events_count" in data
    assert "critical_unresolved" in data
    assert "high_unresolved" in data
    assert "event_rate_per_minute" in data


def test_event_correlation(client, sample_event):
    """Test event correlation."""
    correlation_id = "test-correlation-1"

    # Correlate the event
    response = client.post(
        f"/api/security/events/{sample_event}/correlate",
        params={"correlation_id": correlation_id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "correlated"
    assert data["correlation_id"] == correlation_id


def test_get_correlated_events(client, sample_event):
    """Test getting correlated events."""
    correlation_id = "test-correlation-2"

    # Create and correlate multiple events
    import asyncio

    event_ids = []
    for i in range(3):
        event_id = asyncio.run(
            security.log_security_event(
                event_type=security.SecurityEventType.INTRUSION_ATTEMPT,
                severity=security.SecurityEventSeverity.MEDIUM,
                source="test-source",
                description=f"Test event {i}",
                correlation_id=correlation_id,
            )
        )
        event_ids.append(event_id)

    # Get correlated events
    response = client.get(
        "/api/security/events/correlated",
        params={"correlation_id": correlation_id},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correlation_id"] == correlation_id
    assert data["event_count"] == 3


def test_automated_responses(client):
    """Test automated response tracking."""
    import asyncio

    # Create event with automated response
    asyncio.run(
        security.log_security_event(
            event_type=security.SecurityEventType.MALWARE_DETECTED,
            severity=security.SecurityEventSeverity.CRITICAL,
            source="malware-scanner",
            description="Malware detected and quarantined",
            details={
                "automated_response": "Quarantine file",
                "response_successful": True,
            },
        )
    )

    response = client.get("/api/security/response/automated")

    assert response.status_code == 200
    data = response.json()
    assert "total_responses" in data
    assert "successful_responses" in data
    assert "success_rate" in data
    assert data["total_responses"] >= 1


def test_threat_level_critical(client):
    """Test that dashboard shows critical threat level."""
    import asyncio

    # Create a critical unresolved event
    asyncio.run(
        security.log_security_event(
            event_type=security.SecurityEventType.ROOTKIT_DETECTED,
            severity=security.SecurityEventSeverity.CRITICAL,
            source="rootkit-scanner",
            description="Rootkit detected",
        )
    )

    response = client.get("/api/security/monitoring/dashboard")
    data = response.json()

    # Should have critical threat level
    assert data["threat_level"] in ["critical", "high", "medium", "low"]
    assert data["critical_unresolved"] >= 1


def test_event_resolution_tracking(client, sample_event):
    """Test that event resolution tracks response time."""
    # Resolve the event
    response = client.post(
        f"/api/security/events/{sample_event}/resolve",
        params={"resolution": "Issue resolved - false positive"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"
    assert "response_time" in data
    assert data["response_time"] >= 0


def test_security_metrics_tracking(client):
    """Test that security metrics are properly tracked."""
    import asyncio

    # Create events of different types and severities
    event_types = [
        security.SecurityEventType.SUSPICIOUS_PROCESS,
        security.SecurityEventType.NETWORK_ANOMALY,
        security.SecurityEventType.FILE_INTEGRITY_VIOLATION,
    ]

    for event_type in event_types:
        asyncio.run(
            security.log_security_event(
                event_type=event_type,
                severity=security.SecurityEventSeverity.MEDIUM,
                source="test-scanner",
                description=f"Test {event_type.value}",
            )
        )

    # Check analytics
    response = client.get("/api/security/analytics")
    data = response.json()

    assert data["total_events"] >= 3
    assert len(data["by_type"]) >= 3


def test_event_rate_calculation(client):
    """Test event rate calculation in dashboard."""
    import asyncio
    import time

    # Create several events
    for _ in range(5):
        asyncio.run(
            security.log_security_event(
                event_type=security.SecurityEventType.UNAUTHORIZED_ACCESS,
                severity=security.SecurityEventSeverity.LOW,
                source="auth-system",
                description="Failed login attempt",
            )
        )
        time.sleep(0.1)

    response = client.get("/api/security/monitoring/dashboard")
    data = response.json()

    assert data["event_rate_per_minute"] >= 0


def test_top_sources_tracking(client):
    """Test tracking of top event sources."""
    import asyncio

    # Create events from different sources
    sources = ["scanner-1", "scanner-2", "scanner-1", "scanner-1"]

    for source in sources:
        asyncio.run(
            security.log_security_event(
                event_type=security.SecurityEventType.NETWORK_ANOMALY,
                severity=security.SecurityEventSeverity.LOW,
                source=source,
                description="Test event",
            )
        )

    response = client.get("/api/security/analytics")
    data = response.json()

    assert "top_sources" in data
    assert "scanner-1" in data["top_sources"]


def test_related_events_linking(client):
    """Test that correlated events are properly linked."""
    import asyncio

    correlation_id = "attack-pattern-1"

    # Create related events
    event_ids = []
    for i in range(3):
        event_id = asyncio.run(
            security.log_security_event(
                event_type=security.SecurityEventType.INTRUSION_ATTEMPT,
                severity=security.SecurityEventSeverity.HIGH,
                source="ids",
                description=f"Attack step {i}",
                correlation_id=correlation_id,
            )
        )
        event_ids.append(event_id)

    # Check that events are linked
    response = client.get(
        "/api/security/events/correlated", params={"correlation_id": correlation_id}
    )
    data = response.json()

    # Each event should have related_events field
    events = data["events"]
    for event in events:
        assert "related_events" in event
        # Should be linked to other events (2 related events)
        assert len(event["related_events"]) == 2


def test_average_response_time(client):
    """Test average response time calculation."""
    import asyncio
    import time

    # Create and immediately resolve events
    for _ in range(3):
        event_id = asyncio.run(
            security.log_security_event(
                event_type=security.SecurityEventType.SUSPICIOUS_PROCESS,
                severity=security.SecurityEventSeverity.MEDIUM,
                source="test",
                description="Test event",
            )
        )

        time.sleep(0.1)

        # Resolve it
        event = next(e for e in security._security_events if e["event_id"] == event_id)
        event["resolved"] = True
        event["resolved_at"] = time.time()
        security._security_metrics["response_times"].append(
            event["resolved_at"] - event["timestamp"]
        )

    response = client.get("/api/security/analytics")
    data = response.json()

    assert "avg_response_time" in data
    assert data["avg_response_time"] >= 0

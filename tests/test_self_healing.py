"""Tests for self-healing integration."""
from typing import Any

import pytest

from src.metacognition.self_healing import (
    Issue,
    IssueType,
    IssueSeverity,
    RemediationAction,
    SelfHealingLoop,
    SelfHealingIntegration,
)


@pytest.mark.asyncio
async def test_self_healing_metrics_and_remediation() -> None:
    """Test self-healing loop with metrics and remediation."""
    metrics_log: list[dict[str, Any]] = []
    alerts: list[str] = []

    loop = SelfHealingLoop(
        metrics_sink=metrics_log.append,
        alert_callback=alerts.append,
    )

    async def monitor() -> dict[str, Any]:
        return {
            "status": "error",
            "type": "service_failure",
            "severity": "error",
            "description": "Test service failure",
            "id": "42",
        }

    async def remediation(_: dict[str, Any]) -> dict[str, Any]:
        return {"success": True, "description": "fixed"}

    loop.register_monitor(monitor)
    loop.register_remediation("service_failure", remediation)

    actions = await loop.run_cycle()

    assert actions
    assert len(actions) == 1
    assert actions[0].success is True
    assert metrics_log
    assert metrics_log[0]["metrics"]["cycles"] == 1
    assert metrics_log[0]["metrics"]["issues_detected"] == 1
    assert loop.get_metrics()["remediations"] == 1
    assert loop.get_metrics()["successful_remediations"] == 1
    assert not alerts
    assert loop.issue_history


@pytest.mark.asyncio
async def test_self_healing_monitor_failure_alerts() -> None:
    """Test self-healing handles monitor failures."""
    alerts: list[str] = []

    loop = SelfHealingLoop(alert_callback=alerts.append)

    async def broken() -> dict:
        raise RuntimeError("boom")

    loop.register_monitor(broken)

    actions = await loop.run_cycle()

    assert actions == []
    assert alerts
    assert "boom" in alerts[0]


@pytest.mark.asyncio
async def test_self_healing_remediation_failure() -> None:
    """Test self-healing handles remediation failures."""
    alerts: list[str] = []

    loop = SelfHealingLoop(alert_callback=alerts.append)

    async def monitor() -> dict:
        return {
            "status": "error",
            "type": "service_failure",
            "severity": "critical",
            "description": "Test issue",
        }

    async def broken_remediation(_: dict[str, Any]) -> dict:
        raise RuntimeError("remediation failed")

    loop.register_monitor(monitor)
    loop.register_remediation("service_failure", broken_remediation)

    actions = await loop.run_cycle()

    # Action list should be empty since remediation failed
    assert actions == []
    # Should have alert about remediation failure
    assert alerts
    assert "remediation failed" in alerts[0]
    # Metrics should reflect failure
    assert loop.get_metrics()["failed_remediations"] == 1


@pytest.mark.asyncio
async def test_issue_to_dict() -> None:
    """Test Issue.to_dict conversion."""
    issue = Issue(
        issue_type=IssueType.RESOURCE_EXHAUSTION,
        severity=IssueSeverity.CRITICAL,
        description="Test issue",
        metrics={"cpu": 95.0},
        remediation_attempted=True,
        remediation_successful=True,
        remediation_details="Fixed",
    )

    data = issue.to_dict()

    assert data["issue_type"] == "resource_exhaustion"
    assert data["severity"] == "critical"
    assert data["description"] == "Test issue"
    assert data["metrics"]["cpu"] == 95.0
    assert data["remediation_attempted"] is True
    assert data["remediation_successful"] is True
    assert data["remediation_details"] == "Fixed"


@pytest.mark.asyncio
async def test_remediation_action_to_dict() -> None:
    """Test RemediationAction.to_dict conversion."""
    action = RemediationAction(
        issue_type=IssueType.PERFORMANCE_DEGRADATION,
        action="Optimize query",
        success=True,
        details="Query optimized successfully",
    )

    data = action.to_dict()

    assert data["issue_type"] == "performance_degradation"
    assert data["action"] == "Optimize query"
    assert data["success"] is True
    assert data["details"] == "Query optimized successfully"


@pytest.mark.asyncio
async def test_get_issue_summary() -> None:
    """Test issue summary generation."""
    loop = SelfHealingLoop()

    # Add some issues
    loop.issue_history.append(
        Issue(
            issue_type=IssueType.RESOURCE_EXHAUSTION,
            severity=IssueSeverity.CRITICAL,
            description="Test 1",
        )
    )
    loop.issue_history.append(
        Issue(
            issue_type=IssueType.RESOURCE_EXHAUSTION,
            severity=IssueSeverity.WARNING,
            description="Test 2",
        )
    )
    loop.issue_history.append(
        Issue(
            issue_type=IssueType.PERFORMANCE_DEGRADATION,
            severity=IssueSeverity.ERROR,
            description="Test 3",
        )
    )

    summary = loop.get_issue_summary()

    assert summary["total_issues"] == 3
    assert summary["by_type"]["resource_exhaustion"] == 2
    assert summary["by_type"]["performance_degradation"] == 1
    assert summary["by_severity"]["critical"] == 1
    assert summary["by_severity"]["warning"] == 1
    assert summary["by_severity"]["error"] == 1
    assert len(summary["recent_issues"]) == 3


@pytest.mark.asyncio
async def test_self_healing_integration_initialization() -> None:
    """Test SelfHealingIntegration initialization."""
    integration = SelfHealingIntegration()

    assert integration.healing_loop is not None
    assert len(integration.healing_loop._monitors) >= 2
    assert len(integration.healing_loop._remediations) >= 2


@pytest.mark.asyncio
async def test_self_healing_integration_status() -> None:
    """Test SelfHealingIntegration status reporting."""
    integration = SelfHealingIntegration()

    status = integration.get_status()

    assert "metrics" in status
    assert "issue_summary" in status
    assert "monitors_registered" in status
    assert "remediations_registered" in status
    assert status["monitors_registered"] >= 2
    assert status["remediations_registered"] >= 2


@pytest.mark.asyncio
async def test_multiple_monitors_and_remediations() -> None:
    """Test self-healing with multiple monitors and remediations."""
    loop = SelfHealingLoop()

    async def monitor1() -> dict:
        return {
            "status": "error",
            "type": "memory_leak",
            "severity": "warning",
            "description": "Issue 1",
        }

    async def monitor2() -> dict:
        return {
            "status": "error",
            "type": "network_issue",
            "severity": "error",
            "description": "Issue 2",
        }

    async def remediation1(_: dict[str, Any]) -> dict:
        return {"success": True, "description": "Fixed issue 1"}

    async def remediation2(_: dict[str, Any]) -> dict:
        return {"success": True, "description": "Fixed issue 2"}

    loop.register_monitor(monitor1)
    loop.register_monitor(monitor2)
    loop.register_remediation("memory_leak", remediation1)
    loop.register_remediation("network_issue", remediation2)

    actions = await loop.run_cycle()

    assert len(actions) == 2
    assert all(action.success for action in actions)
    assert loop.get_metrics()["issues_detected"] == 2
    assert loop.get_metrics()["successful_remediations"] == 2

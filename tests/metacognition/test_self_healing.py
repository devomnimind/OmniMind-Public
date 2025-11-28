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

"""Comprehensive tests for Self-Healing module.

Tests for automated recovery and self-repair capabilities.
Total: 29 tests covering all self-healing functionality.
"""

from datetime import datetime
from typing import Any, Dict, Optional

import pytest

from src.metacognition.self_healing import (
    Issue,
    IssueSeverity,
    IssueType,
    RemediationAction,
    SelfHealingIntegration,
    SelfHealingLoop,
)


class TestIssueDataclass:
    """Tests for Issue dataclass."""

    def test_issue_creation(self) -> None:
        """Test creating an issue."""
        issue = Issue(
            issue_type=IssueType.RESOURCE_EXHAUSTION,
            severity=IssueSeverity.CRITICAL,
            description="Memory at 95%",
        )

        assert issue.issue_type == IssueType.RESOURCE_EXHAUSTION
        assert issue.severity == IssueSeverity.CRITICAL
        assert issue.description == "Memory at 95%"
        assert isinstance(issue.detected_at, datetime)
        assert issue.remediation_attempted is False
        assert issue.remediation_successful is False

    def test_issue_with_metrics(self) -> None:
        """Test issue with custom metrics."""
        metrics = {"cpu": 85.5, "memory": 92.3}
        issue = Issue(
            issue_type=IssueType.PERFORMANCE_DEGRADATION,
            severity=IssueSeverity.WARNING,
            description="High resource usage",
            metrics=metrics,
        )

        assert issue.metrics == metrics
        assert issue.metrics["cpu"] == 85.5

    def test_issue_to_dict(self) -> None:
        """Test converting issue to dictionary."""
        issue = Issue(
            issue_type=IssueType.DISK_FULL,
            severity=IssueSeverity.ERROR,
            description="Disk at 98%",
        )

        result = issue.to_dict()

        assert result["issue_type"] == "disk_full"
        assert result["severity"] == "error"
        assert result["description"] == "Disk at 98%"
        assert "detected_at" in result
        assert result["remediation_attempted"] is False


class TestRemediationAction:
    """Tests for RemediationAction dataclass."""

    def test_remediation_creation(self) -> None:
        """Test creating a remediation action."""
        action = RemediationAction(
            issue_type=IssueType.MEMORY_LEAK,
            action="Garbage collection triggered",
            success=True,
            details="Freed 150MB",
        )

        assert action.issue_type == IssueType.MEMORY_LEAK
        assert action.action == "Garbage collection triggered"
        assert action.success is True
        assert action.details == "Freed 150MB"
        assert isinstance(action.executed_at, datetime)

    def test_remediation_to_dict(self) -> None:
        """Test converting remediation to dictionary."""
        action = RemediationAction(
            issue_type=IssueType.SERVICE_FAILURE,
            action="Service restarted",
            success=True,
        )

        result = action.to_dict()

        assert result["issue_type"] == "service_failure"
        assert result["action"] == "Service restarted"
        assert result["success"] is True
        assert "executed_at" in result


class TestIssueType:
    """Tests for IssueType enum."""

    def test_issue_type_values(self) -> None:
        """Test issue type enum values."""
        assert IssueType.RESOURCE_EXHAUSTION.value == "resource_exhaustion"
        assert IssueType.PERFORMANCE_DEGRADATION.value == "performance_degradation"
        assert IssueType.SERVICE_FAILURE.value == "service_failure"
        assert IssueType.MEMORY_LEAK.value == "memory_leak"
        assert IssueType.NETWORK_ISSUE.value == "network_issue"
        assert IssueType.DISK_FULL.value == "disk_full"
        assert IssueType.PROCESS_CRASH.value == "process_crash"


class TestIssueSeverity:
    """Tests for IssueSeverity enum."""

    def test_severity_values(self) -> None:
        """Test severity enum values."""
        assert IssueSeverity.INFO.value == "info"
        assert IssueSeverity.WARNING.value == "warning"
        assert IssueSeverity.ERROR.value == "error"
        assert IssueSeverity.CRITICAL.value == "critical"


class TestSelfHealingLoop:
    """Tests for SelfHealingLoop."""

    def test_initialization(self) -> None:
        """Test healing loop initialization."""
        loop = SelfHealingLoop()

        assert loop._monitors == []
        assert loop._remediations == {}
        assert loop._metrics["cycles"] == 0
        assert loop._metrics["issues_detected"] == 0
        assert loop.issue_history == []
        assert loop.action_history == []

    def test_initialization_with_callbacks(self) -> None:
        """Test initialization with callbacks."""

        def metrics_sink(x: Any) -> None:
            return None

        def alert_callback(x: Any) -> None:
            return None

        loop = SelfHealingLoop(
            metrics_sink=metrics_sink,
            alert_callback=alert_callback,
        )

        assert loop._metrics_sink is not None
        assert loop._alert_callback is not None

    def test_register_monitor(self) -> None:
        """Test registering a monitor function."""
        loop = SelfHealingLoop()

        async def test_monitor() -> None:
            return None

        loop.register_monitor(test_monitor)

        assert len(loop._monitors) == 1
        assert test_monitor in loop._monitors

    def test_register_multiple_monitors(self) -> None:
        """Test registering multiple monitors."""
        loop = SelfHealingLoop()

        async def monitor1() -> None:
            return None

        async def monitor2() -> None:
            return None

        loop.register_monitor(monitor1)
        loop.register_monitor(monitor2)

        assert len(loop._monitors) == 2

    def test_register_remediation(self) -> None:
        """Test registering a remediation function."""
        loop = SelfHealingLoop()

        async def test_remediation(issue: Dict[str, Any]) -> Dict[str, Any]:
            return {"success": True}

        loop.register_remediation("resource_exhaustion", test_remediation)

        assert "resource_exhaustion" in loop._remediations

    @pytest.mark.asyncio
    async def test_run_cycle_no_issues(self) -> None:
        """Test running cycle with no issues detected."""
        loop = SelfHealingLoop()

        async def healthy_monitor() -> None:
            return None  # No issue

        loop.register_monitor(healthy_monitor)

        actions = await loop.run_cycle()

        assert loop._metrics["cycles"] == 1
        assert loop._metrics["issues_detected"] == 0
        assert len(actions) == 0

    @pytest.mark.asyncio
    async def test_run_cycle_with_issue(self) -> None:
        """Test running cycle with issue detected."""
        loop = SelfHealingLoop()

        async def failing_monitor() -> Dict[str, Any]:
            return {
                "status": "error",
                "type": "service_failure",
                "severity": "error",
                "description": "Service down",
            }

        loop.register_monitor(failing_monitor)

        _ = await loop.run_cycle()

        assert loop._metrics["cycles"] == 1
        assert loop._metrics["issues_detected"] == 1
        assert len(loop.issue_history) == 1

    @pytest.mark.asyncio
    async def test_run_cycle_with_remediation(self) -> None:
        """Test running cycle with successful remediation."""
        loop = SelfHealingLoop()

        async def failing_monitor() -> Dict[str, Any]:
            return {
                "status": "error",
                "type": "service_failure",
                "severity": "error",
                "description": "Service down",
            }

        async def remediation(issue: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "success": True,
                "description": "Service restarted",
            }

        loop.register_monitor(failing_monitor)
        loop.register_remediation("service_failure", remediation)

        actions = await loop.run_cycle()

        assert loop._metrics["remediations"] == 1
        assert loop._metrics["successful_remediations"] == 1
        assert len(actions) == 1
        assert actions[0].success is True

    @pytest.mark.asyncio
    async def test_run_cycle_failed_remediation(self) -> None:
        """Test running cycle with failed remediation."""
        loop = SelfHealingLoop()

        async def failing_monitor() -> Dict[str, Any]:
            return {
                "status": "error",
                "type": "network_issue",
                "severity": "critical",
                "description": "Network down",
            }

        async def failed_remediation(issue: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "success": False,
                "description": "Could not restore network",
            }

        loop.register_monitor(failing_monitor)
        loop.register_remediation("network_issue", failed_remediation)

        actions = await loop.run_cycle()

        assert loop._metrics["remediations"] == 1
        assert loop._metrics["failed_remediations"] == 1
        assert actions[0].success is False

    def test_get_metrics(self) -> None:
        """Test getting metrics."""
        loop = SelfHealingLoop()
        loop._metrics["cycles"] = 5
        loop._metrics["issues_detected"] = 3

        metrics = loop.get_metrics()

        assert metrics["cycles"] == 5
        assert metrics["issues_detected"] == 3
        # Should return a copy
        metrics["cycles"] = 100
        assert loop._metrics["cycles"] == 5

    def test_get_issue_summary_empty(self) -> None:
        """Test issue summary with no issues."""
        loop = SelfHealingLoop()

        summary = loop.get_issue_summary()

        assert summary["total_issues"] == 0
        assert summary["by_type"] == {}
        assert summary["by_severity"] == {}
        assert summary["recent_issues"] == []

    def test_get_issue_summary_with_issues(self) -> None:
        """Test issue summary with issues."""
        loop = SelfHealingLoop()

        # Add some issues
        issue1 = Issue(
            issue_type=IssueType.MEMORY_LEAK,
            severity=IssueSeverity.WARNING,
            description="Memory leak detected",
        )
        issue2 = Issue(
            issue_type=IssueType.MEMORY_LEAK,
            severity=IssueSeverity.ERROR,
            description="Memory leak worsening",
        )
        issue3 = Issue(
            issue_type=IssueType.DISK_FULL,
            severity=IssueSeverity.CRITICAL,
            description="Disk full",
        )

        loop.issue_history.extend([issue1, issue2, issue3])

        summary = loop.get_issue_summary()

        assert summary["total_issues"] == 3
        assert summary["by_type"]["memory_leak"] == 2
        assert summary["by_type"]["disk_full"] == 1
        assert summary["by_severity"]["warning"] == 1
        assert summary["by_severity"]["error"] == 1
        assert summary["by_severity"]["critical"] == 1


class TestSelfHealingIntegration:
    """Tests for SelfHealingIntegration."""

    def test_integration_initialization(self) -> None:
        """Test integration initialization."""
        integration = SelfHealingIntegration()

        assert integration.homeostatic_controller is None
        assert integration.metacognition_agent is None
        assert isinstance(integration.healing_loop, SelfHealingLoop)

    def test_monitors_registered(self) -> None:
        """Test that default monitors are registered."""
        integration = SelfHealingIntegration()

        # Should have at least 2 default monitors
        assert len(integration.healing_loop._monitors) >= 2

    def test_remediations_registered(self) -> None:
        """Test that default remediations are registered."""
        integration = SelfHealingIntegration()

        # Should have remediations for resource exhaustion and performance degradation
        assert "resource_exhaustion" in integration.healing_loop._remediations
        assert "performance_degradation" in integration.healing_loop._remediations

    @pytest.mark.asyncio
    async def test_run_healing_cycle(self) -> None:
        """Test running a healing cycle."""
        integration = SelfHealingIntegration()

        actions = await integration.run_healing_cycle()

        # Should complete without error
        assert isinstance(actions, list)

    def test_get_status(self) -> None:
        """Test getting integration status."""
        integration = SelfHealingIntegration()

        status = integration.get_status()

        assert "metrics" in status
        assert "issue_summary" in status
        assert "monitors_registered" in status
        assert "remediations_registered" in status
        assert status["monitors_registered"] >= 2
        assert status["remediations_registered"] >= 2


class TestIntegration:
    """Integration tests for self-healing system."""

    @pytest.mark.asyncio
    async def test_complete_healing_cycle(self) -> None:
        """Test complete healing cycle from detection to remediation."""
        loop = SelfHealingLoop()

        issue_detected = False
        remediation_called = False

        async def test_monitor() -> Optional[Dict[str, Any]]:
            nonlocal issue_detected
            if not issue_detected:
                issue_detected = True
                return {
                    "status": "error",
                    "type": "resource_exhaustion",  # Use valid IssueType
                    "severity": "warning",
                    "description": "Test issue",
                }
            return None

        async def test_remediation(issue: Dict[str, Any]) -> Dict[str, Any]:
            nonlocal remediation_called
            remediation_called = True
            return {
                "success": True,
                "description": "Issue resolved",
            }

        loop.register_monitor(test_monitor)
        loop.register_remediation("resource_exhaustion", test_remediation)

        # First cycle should detect and remediate
        actions = await loop.run_cycle()

        assert issue_detected
        assert remediation_called
        assert len(actions) == 1
        assert actions[0].success

    @pytest.mark.asyncio
    async def test_multiple_cycles(self) -> None:
        """Test running multiple healing cycles."""
        loop = SelfHealingLoop()

        async def no_op_monitor() -> None:
            return None

        loop.register_monitor(no_op_monitor)

        # Run 5 cycles
        for _ in range(5):
            await loop.run_cycle()

        assert loop._metrics["cycles"] == 5

    @pytest.mark.asyncio
    async def test_metrics_callback(self) -> None:
        """Test that metrics callback is invoked."""
        metrics_received = []

        def metrics_sink(data: Dict[str, Any]) -> None:
            metrics_received.append(data)

        loop = SelfHealingLoop(metrics_sink=metrics_sink)

        async def dummy_monitor() -> None:
            return None

        loop.register_monitor(dummy_monitor)

        await loop.run_cycle()

        assert len(metrics_received) == 1
        assert "metrics" in metrics_received[0]

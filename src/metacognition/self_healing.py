"""Self-healing integration for OmniMind.

This module provides automated recovery and self-repair capabilities:
- Automatic error detection and recovery
- Performance degradation detection
- Resource exhaustion recovery
- Service health monitoring
- Automatic remediation actions
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class IssueType(str, Enum):
    """Types of issues the self-healing system can detect."""

    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SERVICE_FAILURE = "service_failure"
    MEMORY_LEAK = "memory_leak"
    NETWORK_ISSUE = "network_issue"
    DISK_FULL = "disk_full"
    PROCESS_CRASH = "process_crash"


class IssueSeverity(str, Enum):
    """Severity levels for detected issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Issue:
    """Represents a detected issue."""

    issue_type: IssueType
    severity: IssueSeverity
    description: str
    detected_at: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)
    remediation_attempted: bool = False
    remediation_successful: bool = False
    remediation_details: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "metrics": self.metrics,
            "remediation_attempted": self.remediation_attempted,
            "remediation_successful": self.remediation_successful,
            "remediation_details": self.remediation_details,
        }


@dataclass
class RemediationAction:
    """Represents a remediation action taken."""

    issue_type: IssueType
    action: str
    executed_at: datetime = field(default_factory=datetime.now)
    success: bool = False
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "issue_type": self.issue_type.value,
            "action": self.action,
            "executed_at": self.executed_at.isoformat(),
            "success": self.success,
            "details": self.details,
        }


class SelfHealingLoop:
    """Self-healing loop for automatic system recovery."""

    def __init__(
        self,
        metrics_sink: Optional[Callable[[Dict[str, Any]], None]] = None,
        alert_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Initialize self-healing loop.

        Args:
            metrics_sink: Optional callback to send metrics to
            alert_callback: Optional callback for critical alerts
        """
        self._monitors: List[Callable[[], Any]] = []
        self._remediations: Dict[str, Callable[[Dict[str, Any]], Any]] = {}
        self._metrics_sink = metrics_sink
        self._alert_callback = alert_callback
        self._metrics = {
            "cycles": 0,
            "issues_detected": 0,
            "remediations": 0,
            "successful_remediations": 0,
            "failed_remediations": 0,
        }
        self.issue_history: List[Issue] = []
        self.action_history: List[RemediationAction] = []

    def register_monitor(self, monitor: Callable[[], Any]) -> None:
        """Register a monitoring function.

        Args:
            monitor: Async function that returns issue dict or None
        """
        self._monitors.append(monitor)
        logger.info(f"Registered monitor: {monitor.__name__}")

    def register_remediation(
        self, issue_type: str, remediation: Callable[[Dict[str, Any]], Any]
    ) -> None:
        """Register a remediation function for an issue type.

        Args:
            issue_type: Type of issue to remediate
            remediation: Async function that performs remediation
        """
        self._remediations[issue_type] = remediation
        logger.info(f"Registered remediation for {issue_type}: {remediation.__name__}")

    async def run_cycle(self) -> List[RemediationAction]:
        """Run one self-healing cycle.

        Returns:
            List of remediation actions taken
        """
        self._metrics["cycles"] += 1
        actions: List[RemediationAction] = []

        # Run all monitors and collect actions
        monitor_actions = await self._run_all_monitors()
        actions.extend(monitor_actions)

        # Send metrics
        if self._metrics_sink:
            self._metrics_sink({"metrics": self._metrics.copy()})

        return actions

    async def _run_all_monitors(self) -> List[RemediationAction]:
        """Run all registered monitors and return remediation actions."""
        actions: List[RemediationAction] = []

        for monitor in self._monitors:
            monitor_actions = await self._run_single_monitor(monitor)
            actions.extend(monitor_actions)

        return actions

    async def _run_single_monitor(self, monitor: Any) -> List[RemediationAction]:
        """Run a single monitor and handle any issues found."""
        actions: List[RemediationAction] = []

        try:
            result = await monitor()
            if result and result.get("status") == "error":
                monitor_actions = await self._handle_monitor_error(result)
                actions.extend(monitor_actions)

        except Exception as e:
            self._handle_monitor_exception(monitor, e)

        return actions

    async def _handle_monitor_error(self, result: Dict[str, Any]) -> List[RemediationAction]:
        """Handle an error detected by a monitor."""
        self._metrics["issues_detected"] += 1

        # Create and record issue
        issue = self._create_issue_from_result(result)
        self.issue_history.append(issue)

        # Attempt remediation
        return await self._attempt_remediation(result, issue)

    def _create_issue_from_result(self, result: Dict[str, Any]) -> Issue:
        """Create an Issue object from monitor result."""
        return Issue(
            issue_type=IssueType(result.get("type", "service_failure")),
            severity=IssueSeverity(result.get("severity", IssueSeverity.ERROR.value)),
            description=result.get("description", "Unknown issue"),
            metrics=result,
        )

    async def _attempt_remediation(self, result: Dict[str, Any], issue: Issue) -> List[RemediationAction]:
        """Attempt to remediate an issue and return actions taken."""
        actions: List[RemediationAction] = []
        issue_type = result.get("type")

        if issue_type in self._remediations:
            self._metrics["remediations"] += 1
            remediation = self._remediations[issue_type]

            try:
                remediation_result = await remediation(result)
                action = self._process_remediation_result(remediation_result, issue_type, issue)
                actions.append(action)

            except Exception as e:
                self._handle_remediation_failure(issue_type, e)

        return actions

    def _process_remediation_result(self, remediation_result: Dict[str, Any], issue_type: str, issue: Issue) -> RemediationAction:
        """Process the result of a remediation attempt."""
        success = remediation_result.get("success", False)

        if success:
            self._metrics["successful_remediations"] += 1
        else:
            self._metrics["failed_remediations"] += 1

        # Record action
        action = RemediationAction(
            issue_type=IssueType(issue_type),
            action=remediation_result.get("description", ""),
            success=success,
            details=str(remediation_result),
        )

        self.action_history.append(action)

        # Update issue record
        issue.remediation_attempted = True
        issue.remediation_successful = success
        issue.remediation_details = str(remediation_result)

        return action

    def _handle_remediation_failure(self, issue_type: str, error: Exception) -> None:
        """Handle a remediation failure."""
        self._metrics["failed_remediations"] += 1
        logger.error(f"Remediation failed: {error}")

        if self._alert_callback:
            self._alert_callback(f"Remediation failed for {issue_type}: {error}")

    def _handle_monitor_exception(self, monitor: Any, error: Exception) -> None:
        """Handle an exception during monitor execution."""
        logger.error(f"Monitor {monitor.__name__} failed: {error}")
        if self._alert_callback:
            self._alert_callback(f"Monitor {monitor.__name__} failed: {error}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics.

        Returns:
            Dictionary of metrics
        """
        return self._metrics.copy()

    def get_issue_summary(self) -> Dict[str, Any]:
        """Get summary of detected issues.

        Returns:
            Summary statistics
        """
        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}

        for issue in self.issue_history:
            issue_type = issue.issue_type.value
            severity = issue.severity.value

            by_type[issue_type] = by_type.get(issue_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "total_issues": len(self.issue_history),
            "by_type": by_type,
            "by_severity": by_severity,
            "recent_issues": [i.to_dict() for i in self.issue_history[-10:]],
        }


class SelfHealingIntegration:
    """Integration layer for self-healing with metacognition."""

    def __init__(
        self,
        homeostatic_controller: Optional[Any] = None,
        metacognition_agent: Optional[Any] = None,
    ) -> None:
        """Initialize self-healing integration.

        Args:
            homeostatic_controller: Optional homeostatic controller
            metacognition_agent: Optional metacognition agent
        """
        self.homeostatic_controller = homeostatic_controller
        self.metacognition_agent = metacognition_agent
        self.healing_loop = SelfHealingLoop()
        self._setup_monitors()
        self._setup_remediations()

    def _setup_monitors(self) -> None:
        """Setup default monitoring functions."""

        async def check_resources() -> Optional[Dict[str, Any]]:
            """Monitor resource usage."""
            if self.homeostatic_controller:
                metrics = self.homeostatic_controller.get_current_metrics()
                state = metrics.get_overall_state()

                if state.value in ["critical", "emergency"]:
                    return {
                        "status": "error",
                        "type": IssueType.RESOURCE_EXHAUSTION.value,
                        "severity": IssueSeverity.CRITICAL.value,
                        "description": f"Resource state: {state.value}",
                        "cpu": metrics.cpu_percent,
                        "memory": metrics.memory_percent,
                        "disk": metrics.disk_percent,
                    }
            return None

        async def check_performance() -> Optional[Dict[str, Any]]:
            """Monitor performance metrics."""
            if self.metacognition_agent:
                # Check if metacognition detects performance issues
                try:
                    health = self.metacognition_agent.check_health()
                    health_status = health.get("health", {}).get("health_status")

                    if health_status == "critical":
                        return {
                            "status": "error",
                            "type": IssueType.PERFORMANCE_DEGRADATION.value,
                            "severity": IssueSeverity.ERROR.value,
                            "description": "Performance degradation detected",
                            "health_data": health,
                        }
                except Exception as e:
                    logger.debug(f"Performance check failed: {e}")
            return None

        self.healing_loop.register_monitor(check_resources)
        self.healing_loop.register_monitor(check_performance)

    def _setup_remediations(self) -> None:
        """Setup default remediation actions."""

        async def remediate_resources(issue: Dict[str, Any]) -> Dict[str, Any]:
            """Remediate resource exhaustion."""
            actions_taken = []

            if self.homeostatic_controller:
                # Trigger emergency throttling
                try:
                    self.homeostatic_controller._trigger_emergency_throttling()
                    actions_taken.append("Emergency throttling activated")
                except Exception as e:
                    logger.error(f"Failed to activate throttling: {e}")

                # Request garbage collection
                import gc

                gc.collect()
                actions_taken.append("Garbage collection triggered")

            return {
                "success": True,
                "description": "; ".join(actions_taken),
                "actions": actions_taken,
            }

        async def remediate_performance(issue: Dict[str, Any]) -> Dict[str, Any]:
            """Remediate performance degradation."""
            actions_taken = []

            # Log performance issue for later analysis
            actions_taken.append("Performance issue logged for analysis")

            # If metacognition is available, trigger optimization suggestions
            if self.metacognition_agent:
                try:
                    suggestions = self.metacognition_agent.get_optimization_suggestions(limit=3)
                    if suggestions:
                        actions_taken.append(
                            f"Generated {len(suggestions)} optimization suggestions"
                        )
                except Exception as e:
                    logger.error(f"Failed to get optimization suggestions: {e}")

            return {
                "success": True,
                "description": "; ".join(actions_taken),
                "actions": actions_taken,
            }

        self.healing_loop.register_remediation(
            IssueType.RESOURCE_EXHAUSTION.value, remediate_resources
        )
        self.healing_loop.register_remediation(
            IssueType.PERFORMANCE_DEGRADATION.value, remediate_performance
        )

    async def run_healing_cycle(self) -> List[RemediationAction]:
        """Run one self-healing cycle.

        Returns:
            List of actions taken
        """
        return await self.healing_loop.run_cycle()

    def get_status(self) -> Dict[str, Any]:
        """Get self-healing status.

        Returns:
            Status dictionary
        """
        return {
            "metrics": self.healing_loop.get_metrics(),
            "issue_summary": self.healing_loop.get_issue_summary(),
            "monitors_registered": len(self.healing_loop._monitors),
            "remediations_registered": len(self.healing_loop._remediations),
        }

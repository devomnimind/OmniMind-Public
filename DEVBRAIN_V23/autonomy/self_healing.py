from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter_ns
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

IssueMonitor = Callable[[], Awaitable[Dict[str, Any]]]
RemediationHandler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
MetricsSink = Callable[[Dict[str, Any]], None]

from .observability import autonomy_observability


@dataclass
class HealingAction:
    issue_id: str
    issue_type: str
    description: str
    success: bool
    resolved_at: datetime


class SelfHealingLoop:
    def __init__(
        self,
        monitors: Optional[List[IssueMonitor]] = None,
        alert_callback: Optional[Callable[[str], None]] = None,
        metrics_sink: Optional[MetricsSink] = None,
    ) -> None:
        self.monitors = monitors or []
        self.remediations: Dict[str, List[RemediationHandler]] = {}
        self.alert_callback = alert_callback
        self.metrics_sink = (
            metrics_sink or autonomy_observability.record_self_healing_metrics
        )
        self.last_actions: List[HealingAction] = []
        self.issue_history: List[Dict[str, Any]] = []
        self.metrics = {
            "cycles": 0,
            "monitors": len(self.monitors),
            "issues_detected": 0,
            "remediations": 0,
            "remediation_failures": 0,
        }

    def register_monitor(self, monitor: IssueMonitor) -> None:
        self.monitors.append(monitor)
        self.metrics["monitors"] = len(self.monitors)

    def register_remediation(
        self, issue_type: str, handler: RemediationHandler
    ) -> None:
        self.remediations.setdefault(issue_type, []).append(handler)
        self.metrics.setdefault("remediation_handlers", {}).setdefault(issue_type, 0)
        self.metrics["remediation_handlers"][issue_type] += 1

    async def detect_issues(self) -> List[Dict[str, Any]]:
        if not self.monitors:
            return []
        tasks = [monitor() for monitor in self.monitors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        issues: List[Dict[str, Any]] = []
        for entry in results:
            if isinstance(entry, Exception):
                self._record_alert(f"monitor failed: {entry}")
                continue
            if entry.get("status") != "ok":
                issues.append(entry)
        self.metrics["issues_detected"] += len(issues)
        self.issue_history.extend(issues)
        return issues

    async def remediate(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        handlers = self.remediations.get(issue.get("type", ""), [])
        for handler in handlers:
            try:
                result = await handler(issue)
                action = HealingAction(
                    issue_id=issue.get("id", ""),
                    issue_type=issue.get("type", ""),
                    description=result.get("description", ""),
                    success=result.get("success", False),
                    resolved_at=datetime.now(timezone.utc),
                )
                self.last_actions.append(action)
                self.metrics["remediations"] += 1
                return result
            except Exception as exc:
                self._record_alert(f"remediation failed: {exc}")
                self.metrics["remediation_failures"] += 1
        return None

    async def run_cycle(self) -> List[Dict[str, Any]]:
        start = perf_counter_ns()
        issues = await self.detect_issues()
        self.metrics["cycles"] += 1
        duration = (perf_counter_ns() - start) / 1_000_000
        if not issues:
            self._emit_metrics(duration)
            return []
        actions: List[Dict[str, Any]] = []
        for issue in issues:
            remediation = await self.remediate(issue)
            actions.append({"issue": issue, "remediation": remediation})
        self._emit_metrics(duration)
        return actions

    def _record_alert(self, message: str) -> None:
        log = f"[SelfHealing] {message}"
        logger.warning(log)
        autonomy_observability.record_alert(log)
        if self.alert_callback:
            try:
                self.alert_callback(log)
            except Exception as exc:
                logger.error("alert callback failed", exc_info=True)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            **self.metrics,
            "last_actions": [action.__dict__ for action in self.last_actions[-5:]],
        }

    def _emit_metrics(self, duration: float) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration,
            "metrics": self.get_metrics(),
        }
        try:
            self.metrics_sink(payload)
        except Exception:
            logger.debug("metrics sink failed", exc_info=True)

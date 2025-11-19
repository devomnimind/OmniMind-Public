from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter_ns
from typing import Any, Awaitable, Callable, Dict, List, Optional

from src.tools.omnimind_tools import ToolsFramework

logger = logging.getLogger(__name__)

ToolInvoker = Callable[[str, Dict[str, Any]], Awaitable[Any]]
MetricSink = Callable[[str, float, Dict[str, Any]], None]
AlertCallback = Callable[[str], None]


@dataclass
class DocStep:
    id: str
    prompt: str
    tool: str
    params: Dict[str, Any]


class Doc2Agent:
    def __init__(
        self,
        tool_framework: Optional[ToolsFramework] = None,
        tool_invoker: Optional[ToolInvoker] = None,
        analyst: Optional[Callable[[str], List[Dict[str, Any]]]] = None,
        metrics_sink: Optional[MetricSink] = None,
        alert_callback: Optional[AlertCallback] = None,
    ) -> None:
        self.tool_framework = tool_framework
        self.tool_invoker = tool_invoker or self._default_invoker
        self.analyst = analyst or self._dummy_analyst
        self.history: List[DocStep] = []
        self.invocation_history: List[Dict[str, Any]] = []
        self.metrics_log: List[Dict[str, Any]] = []
        self.tool_health: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[str] = []
        self.last_goal: Optional[str] = None
        self.metrics_sink: MetricSink = metrics_sink or self._default_metrics_sink
        self._alert_callback: AlertCallback = alert_callback or self._default_alert

    async def analyze_documents(self, documents: List[str], goal: str) -> List[DocStep]:
        aggregated = "\n".join(documents)
        plan = self.analyst(aggregated + f"\nGoal: {goal}")
        steps = [DocStep(id=f"step_{i}", **step) for i, step in enumerate(plan)]
        self.history.extend(steps)
        self.last_goal = goal
        return steps

    async def execute_plan(self, steps: List[DocStep]) -> List[Dict[str, Any]]:
        outputs: List[Dict[str, Any]] = []
        for step in steps:
            start = perf_counter_ns()
            status = "success"
            result: Any = None
            error_message: Optional[str] = None
            try:
                result = await self.tool_invoker(step.tool, step.params or {})
            except Exception as exc:
                status = "failure"
                error_message = f"{exc.__class__.__name__}: {exc}"
                self._record_alert(
                    f"Doc2Agent step {step.id} [{step.tool}] failed: {error_message}"
                )
                logger.error("Doc2Agent tool invocation failed", exc_info=True)
                result = {"error": error_message}
            finally:
                latency_ms = (perf_counter_ns() - start) / 1_000_000
                self._record_metrics(step, status, latency_ms, error_message)
            outputs.append({"step": step.id, "tool": step.tool, "result": result})
        return outputs

    async def plan_and_execute(self, documents: List[str], goal: str) -> Dict[str, Any]:
        steps = await self.analyze_documents(documents, goal)
        results = await self.execute_plan(steps)
        return {
            "goal": goal,
            "steps": [step.id for step in steps],
            "results": results,
            "health": self.tool_health,
            "alerts": self.alerts,
        }

    async def _noop_invoker(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return {"tool": tool, "params": params, "ok": True}

    async def _default_invoker(self, tool: str, params: Dict[str, Any]) -> Any:
        if not self.tool_framework:
            return await self._noop_invoker(tool, params)

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: self.tool_framework.execute_tool(tool, **(params or {}))
        )

    def _record_alert(self, message: str) -> None:
        self.alerts.append(message)
        self._alert_callback(message)

    def _record_metrics(
        self,
        step: DocStep,
        status: str,
        latency_ms: float,
        error_message: Optional[str],
    ) -> None:
        profile = self.tool_health.setdefault(
            step.tool,
            {
                "total": 0,
                "success": 0,
                "failure": 0,
                "last_latency_ms": 0.0,
                "total_latency_ms": 0.0,
            },
        )
        profile["total"] += 1
        profile["last_latency_ms"] = latency_ms
        profile["total_latency_ms"] += latency_ms
        if status == "success":
            profile["success"] += 1
        else:
            profile["failure"] += 1

        metric_labels = {
            "tool": step.tool,
            "step_id": step.id,
            "status": status,
            "goal": self.last_goal or "",
        }
        record = {
            "step": step.id,
            "tool": step.tool,
            "status": status,
            "latency_ms": latency_ms,
            "error": error_message,
            "timestamp": self._current_timestamp(),
        }
        self.invocation_history.append(record)
        self.metrics_log.append(
            {"metric": "latency", "value": latency_ms, "labels": metric_labels}
        )
        self.metrics_sink("doc2agent_tool_latency_ms", latency_ms, metric_labels)
        self.metrics_sink(
            "doc2agent_tool_status",
            1.0 if status == "success" else 0.0,
            metric_labels,
        )

    def get_aggregate_metrics(self) -> Dict[str, Any]:
        total_steps = sum(data["total"] for data in self.tool_health.values())
        failure_count = sum(data["failure"] for data in self.tool_health.values())
        latency_sum = sum(
            data["total_latency_ms"] for data in self.tool_health.values()
        )
        tool_breakdown = {}
        for tool, data in self.tool_health.items():
            tool_breakdown[tool] = {
                "total": data["total"],
                "success": data["success"],
                "failure": data["failure"],
                "avg_latency_ms": (
                    data["total_latency_ms"] / data["total"] if data["total"] else 0.0
                ),
                "last_latency_ms": data["last_latency_ms"],
                "failure_rate": (
                    data["failure"] / data["total"] if data["total"] else 0.0
                ),
            }

        overall_failure_rate = failure_count / total_steps if total_steps else 0.0
        avg_latency = latency_sum / total_steps if total_steps else 0.0
        return {
            "total_steps": total_steps,
            "failure_rate": overall_failure_rate,
            "average_latency_ms": avg_latency,
            "tools": tool_breakdown,
        }

    def _default_metrics_sink(
        self, metric_name: str, value: float, labels: Dict[str, Any]
    ) -> None:
        entry = {
            "metric": metric_name,
            "value": value,
            "labels": labels,
            "timestamp": self._current_timestamp(),
        }
        self.metrics_log.append(entry)

        if not self.tool_framework:
            return

        try:
            self.tool_framework.execute_tool(
                "track_metrics", metric_name, value, labels
            )
        except Exception:
            logger.debug("Doc2Agent metric emission failed", exc_info=True)

    def _default_alert(self, message: str) -> None:
        logger.warning("Doc2Agent alert: %s", message)

    def _current_timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _dummy_analyst(self, text: str) -> List[Dict[str, Any]]:
        return [
            {
                "prompt": "read header",
                "tool": "parse",
                "params": {"text": text[:64]},
            },
            {
                "prompt": "invoke api",
                "tool": "call",
                "params": {
                    "url": "https://example.com/api",
                    "payload": {"query": text[:32]},
                },
            },
        ]

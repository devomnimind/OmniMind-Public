from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from DEVBRAIN_V23.autonomy.doc2agent import Doc2Agent, DocStep
from DEVBRAIN_V23.autonomy.observability import AtlasInsight, autonomy_observability
from DEVBRAIN_V23.autonomy.self_healing import SelfHealingLoop

logger = logging.getLogger(__name__)

AtlasSink = Callable[[AtlasInsight], None]


class AtlasController:
    """ATLAS orchestrates learning + adaptation based on Doc2Agent signals."""

    issue_type = "atlas_adaptation"

    def __init__(
        self,
        self_healing: SelfHealingLoop,
        doc_agent: Optional[Doc2Agent] = None,
        failure_threshold: float = 0.2,
        monitor_sink: Optional[AtlasSink] = None,
    ) -> None:
        self.self_healing = self_healing
        self.doc_agent = doc_agent
        self.failure_threshold = failure_threshold
        self.monitor_sink = monitor_sink or autonomy_observability.record_atlas_insight
        self.insights: List[AtlasInsight] = []
        self._latest_metrics: Dict[str, Any] = {}
        self._register_hooks()

    def _register_hooks(self) -> None:
        self.self_healing.register_monitor(self._atlas_failure_monitor)
        self.self_healing.register_remediation(
            self.issue_type, self._atlas_remediation_handler
        )

    def analyze_metrics(self, metrics: Dict[str, Any]) -> None:
        self._latest_metrics = metrics
        failure_rate = metrics.get("failure_rate", 0.0)
        insight = AtlasInsight(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric="failure_rate",
            value=failure_rate,
            status="degrade" if failure_rate >= self.failure_threshold else "healthy",
            details={"metrics": metrics},
        )
        self.insights.append(insight)
        try:
            self.monitor_sink(insight)
        except Exception:
            logger.debug("Atlas monitor sink failed", exc_info=True)

    async def adaptation_cycle(self, documents: List[str], goal: str) -> Dict[str, Any]:
        if not self.doc_agent:
            return {"success": False, "error": "Doc2Agent unavailable"}

        steps = await self.doc_agent.analyze_documents(documents, goal)
        results = await self.doc_agent.execute_plan(steps)
        success = all(not result["result"].get("error") for result in results)
        summary = {
            "goal": goal,
            "steps": [step.id for step in steps],
            "success": success,
            "results": results,
        }
        logger.info("Atlas adaptation cycle complete: %s", summary)
        return summary

    async def _atlas_failure_monitor(self) -> Dict[str, Any]:
        failure_rate = self._latest_metrics.get("failure_rate", 0.0)
        if failure_rate >= self.failure_threshold:
            return {
                "status": "error",
                "type": self.issue_type,
                "id": f"atlas-{datetime.now(timezone.utc).isoformat()}",
                "details": {"failure_rate": failure_rate},
            }
        return {
            "status": "ok",
            "type": self.issue_type,
            "details": {"failure_rate": failure_rate},
        }

    async def _atlas_remediation_handler(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        if not self.doc_agent:
            return {"success": False, "description": "Doc2Agent missing"}

        prompt = f"Adapt for issue {issue.get('id')} with rate {issue.get('details')}"
        steps = await self.doc_agent.analyze_documents(
            [prompt], "Atlas rapid adaptation"
        )
        results = await self.doc_agent.execute_plan(steps)
        success = all(not entry["result"].get("error") for entry in results)
        description = "Adaptation succeeded" if success else "Adaptation had errors"
        insight = AtlasInsight(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric="remediation",
            value=1.0 if success else 0.0,
            status="success" if success else "partial",
            details={"issue": issue, "results": results},
        )
        self.insights.append(insight)
        try:
            self.monitor_sink(insight)
        except Exception:
            logger.debug("Atlas monitor sink failed", exc_info=True)
        return {"success": success, "description": description, "results": results}

    def get_insights(self) -> List[AtlasInsight]:
        return self.insights[-10:]

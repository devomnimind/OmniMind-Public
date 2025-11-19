from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import perf_counter_ns
from typing import Any, Awaitable, Callable, Dict, List, Optional

from DEVBRAIN_V23.autonomy.doc2agent import Doc2Agent, DocStep

logger = logging.getLogger(__name__)

Validator = Callable[[List[Dict[str, Any]]], bool]
Refiner = Callable[[List[DocStep], List[Dict[str, Any]], str], List[DocStep]]
Deployer = Callable[[List[DocStep]], bool]
MonitorSink = Callable[[Dict[str, Any]], None]


@dataclass
class PipelineStageLog:
    name: str
    success: bool
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "success": self.success,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
        }


class Doc2AgentPipeline:
    def __init__(
        self,
        doc_agent: Doc2Agent,
        validator: Optional[Validator] = None,
        refiner: Optional[Refiner] = None,
        deployer: Optional[Deployer] = None,
        monitor_sink: Optional[MonitorSink] = None,
        max_refinements: int = 2,
    ) -> None:
        self.doc_agent = doc_agent
        self.validator = validator or self._default_validator
        self.refiner = refiner
        self.deployer = deployer or (lambda steps: True)
        self.monitor_sink = monitor_sink or self._default_monitor_sink
        self.max_refinements = max_refinements

    async def run_cycle(self, documents: List[str], goal: str) -> Dict[str, Any]:
        stages: List[PipelineStageLog] = []

        generate_start = perf_counter_ns()
        steps = await self.doc_agent.analyze_documents(documents, goal)
        stages.append(
            PipelineStageLog(
                name="generate",
                success=bool(steps),
                duration_ms=(perf_counter_ns() - generate_start) / 1_000_000,
                details={"step_count": len(steps)},
            )
        )

        validation = await self._validate_and_record(stages, steps)
        attempts = 0

        while not validation["success"] and attempts < self.max_refinements:
            if not self.refiner:
                break

            refinement_start = perf_counter_ns()
            steps = self.refiner(steps, validation["results"], goal)
            stages.append(
                PipelineStageLog(
                    name="refine",
                    success=bool(steps),
                    duration_ms=(perf_counter_ns() - refinement_start) / 1_000_000,
                    details={"refinement": attempts + 1, "new_step_count": len(steps)},
                )
            )

            validation = await self._validate_and_record(stages, steps)
            attempts += 1

        deploy_start = perf_counter_ns()
        deploy_success = self.deployer(steps)
        stages.append(
            PipelineStageLog(
                name="deploy",
                success=deploy_success,
                duration_ms=(perf_counter_ns() - deploy_start) / 1_000_000,
                details={"deployed_steps": len(steps)} if deploy_success else {},
            )
        )

        aggregate_metrics = self.doc_agent.get_aggregate_metrics()
        self.monitor_sink(aggregate_metrics)
        stages.append(
            PipelineStageLog(
                name="monitor",
                success=True,
                duration_ms=0.0,
                details={"aggregate_metrics": aggregate_metrics},
            )
        )

        return {
            "goal": goal,
            "documents": documents,
            "stages": [stage.to_dict() for stage in stages],
            "validation": validation,
            "aggregate_metrics": aggregate_metrics,
        }

    async def _validate_and_record(
        self, stages: List[PipelineStageLog], steps: List[DocStep]
    ) -> Dict[str, Any]:
        start = perf_counter_ns()
        results = await self.doc_agent.execute_plan(steps)
        success = self.validator(results)
        stages.append(
            PipelineStageLog(
                name="validate",
                success=success,
                duration_ms=(perf_counter_ns() - start) / 1_000_000,
                details={
                    "errors": [res for res in results if res["result"].get("error")],
                    "results": results,
                },
            )
        )
        return {"success": success, "results": results}

    @staticmethod
    def _default_validator(results: List[Dict[str, Any]]) -> bool:
        return all(not res["result"].get("error") for res in results)

    @staticmethod
    def _default_monitor_sink(metrics: Dict[str, Any]) -> None:
        logger.info("Doc2Agent pipeline metrics: %s", metrics)

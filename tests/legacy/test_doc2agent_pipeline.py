import pytest

from DEVBRAIN_V23.autonomy.doc2agent import DocStep
from DEVBRAIN_V23.autonomy.doc2agent_pipeline import Doc2AgentPipeline


class FakeDoc2Agent:
    def __init__(self, plan_steps: list[DocStep]) -> None:
        self.plan_steps = plan_steps
        self.last_results: list[dict] = []

    async def analyze_documents(self, documents: list[str], goal: str) -> list[DocStep]:
        return self.plan_steps

    async def execute_plan(self, steps: list[DocStep]) -> list[dict]:
        results: list[dict] = []
        for step in steps:
            if step.tool == "fail_tool":
                results.append(
                    {"step": step.id, "tool": step.tool, "result": {"error": "boom"}}
                )
            else:
                results.append(
                    {"step": step.id, "tool": step.tool, "result": {"ok": True}}
                )
        self.last_results = results
        return results

    def get_aggregate_metrics(self) -> dict:
        total = len(self.last_results)
        failure = sum(1 for entry in self.last_results if entry["result"].get("error"))
        tools: dict[str, dict] = {}
        for entry in self.last_results:
            tool = entry["tool"]
            if tool not in tools:
                tools[tool] = {
                    "total": 0,
                    "success": 0,
                    "failure": 0,
                    "last_latency_ms": 0.0,
                    "total_latency_ms": 0.0,
                }
            tools[tool]["total"] += 1
            if entry["result"].get("error"):
                tools[tool]["failure"] += 1
            else:
                tools[tool]["success"] += 1
        return {
            "total_steps": total,
            "failure_rate": failure / total if total else 0.0,
            "average_latency_ms": 0.0,
            "tools": tools,
        }


def build_step(step_id: str, tool: str) -> DocStep:
    return DocStep(id=step_id, prompt="prompt", tool=tool, params={})


@pytest.mark.asyncio
async def test_pipeline_successful_run() -> None:
    doc_agent = FakeDoc2Agent(
        [build_step("step_0", "fast"), build_step("step_1", "fast")]
    )
    monitor_records: list[dict] = []

    pipeline = Doc2AgentPipeline(
        doc_agent,
        monitor_sink=lambda metrics: monitor_records.append(metrics),
    )

    report = await pipeline.run_cycle(["doc"], "goal")

    stage_names = [stage["name"] for stage in report["stages"]]
    assert "generate" in stage_names
    assert "validate" in stage_names
    assert "deploy" in stage_names
    assert "monitor" in stage_names
    assert report["validation"]["success"] is True
    assert monitor_records


@pytest.mark.asyncio
async def test_pipeline_refinement_runs() -> None:
    initial_steps = [build_step("step_0", "fail_tool")]
    doc_agent = FakeDoc2Agent(initial_steps)
    refinement_calls: list[str] = []

    def refiner(steps: list[DocStep], results: list[dict], goal: str) -> list[DocStep]:
        refinement_calls.append(goal)
        return [build_step("step_0", "recover_tool")]

    pipeline = Doc2AgentPipeline(
        doc_agent,
        refiner=refiner,
        max_refinements=1,
    )

    report = await pipeline.run_cycle(["doc"], "goal")
    stage_names = [stage["name"] for stage in report["stages"]]
    assert stage_names.count("validate") == 2
    assert "refine" in stage_names
    assert report["validation"]["success"] is True
    assert refinement_calls

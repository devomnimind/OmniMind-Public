import pytest

from DEVBRAIN_V23.autonomy.doc2agent import DocStep
from DEVBRAIN_V23.autonomy.self_healing import SelfHealingLoop
from DEVBRAIN_V23.atlas import AtlasController


class FakeDoc2Agent:
    def __init__(self) -> None:
        self.plan = [
            DocStep(id="step_a", prompt="adapt", tool="success_tool", params={})
        ]

    async def analyze_documents(self, documents: list[str], goal: str) -> list[DocStep]:
        return self.plan

    async def execute_plan(self, steps: list[DocStep]) -> list[dict]:
        return [
            {"step": step.id, "tool": step.tool, "result": {"ok": True}}
            for step in steps
        ]


@pytest.mark.asyncio
async def test_atlas_controller_triggers_self_healing() -> None:
    loop = SelfHealingLoop()
    doc_agent = FakeDoc2Agent()
    monitor_records: list[dict] = []
    atlas = AtlasController(
        loop, doc_agent, failure_threshold=0.1, monitor_sink=monitor_records.append
    )

    atlas.analyze_metrics({"failure_rate": 0.3})
    actions = await loop.run_cycle()

    assert actions
    assert actions[0]["issue"]["type"] == AtlasController.issue_type
    assert monitor_records
    assert atlas.get_insights()


@pytest.mark.asyncio
async def test_atlas_adaptation_cycle_returns_summary() -> None:
    loop = SelfHealingLoop()
    agent = FakeDoc2Agent()
    atlas = AtlasController(loop, agent)

    summary = await atlas.adaptation_cycle(["doc"], "goal")

    assert summary["success"]
    assert summary["steps"]

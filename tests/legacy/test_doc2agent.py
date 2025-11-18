import pytest

from DEVBRAIN_V23.autonomy.doc2agent import Doc2Agent


class FakeToolsFramework:
    def __init__(self) -> None:
        self.executions: list[dict] = []
        self.metrics: list[dict] = []

    def execute_tool(self, tool_name: str, *args, **kwargs) -> dict | bool:
        if tool_name == "track_metrics":
            self.metrics.append({"name": tool_name, "args": args, "kwargs": kwargs})
            return True

        self.executions.append({"name": tool_name, "args": args, "kwargs": kwargs})

        if tool_name == "fail_tool":
            raise RuntimeError("failure simulated")

        return {"tool": tool_name, "payload": kwargs}


def simple_plan(_: str) -> list[dict]:
    return [
        {"prompt": "first", "tool": "success_tool", "params": {"value": 1}},
        {"prompt": "second", "tool": "fail_tool", "params": {"value": 2}},
    ]


@pytest.mark.asyncio
async def test_doc2agent_tracks_health_and_alerts() -> None:
    framework = FakeToolsFramework()
    alerts: list[str] = []

    agent = Doc2Agent(
        tool_framework=framework,
        analyst=simple_plan,
        alert_callback=alerts.append,
    )

    summary = await agent.plan_and_execute(["state"], "goal")

    assert summary["health"]["success_tool"]["success"] == 1
    assert summary["health"]["fail_tool"]["failure"] == 1
    assert alerts
    assert any(
        "doc2agent_tool_latency_ms" in entry.get("metric", "")
        for entry in agent.metrics_log
    )
    assert any(
        "doc2agent_tool_status" in entry.get("metric", "")
        for entry in agent.metrics_log
    )
    assert all(
        entry["tool"] in {"success_tool", "fail_tool"}
        for entry in agent.invocation_history
    )
    assert any(call["name"] == "track_metrics" for call in framework.metrics)


@pytest.mark.asyncio
async def test_doc2agent_custom_invoker_metrics_called() -> None:
    captured_metrics: list[dict] = []

    async def failing_invoker(tool: str, params: dict) -> dict:
        raise RuntimeError("invoker broken")

    plan = [
        {"prompt": "execute", "tool": "any_tool", "params": {"foo": "bar"}},
    ]

    agent = Doc2Agent(
        tool_invoker=failing_invoker,
        analyst=lambda text: plan,
        alert_callback=lambda msg: captured_metrics.append({"alert": msg}),
        metrics_sink=lambda name, value, labels: captured_metrics.append(
            {"metric": name, "value": value, "labels": labels}
        ),
    )

    await agent.plan_and_execute(["doc"], "goal")

    assert any(
        entry.get("metric") == "doc2agent_tool_latency_ms" for entry in captured_metrics
    )
    assert any(
        entry.get("metric") == "doc2agent_tool_status" for entry in captured_metrics
    )
    assert any("alert" in entry for entry in captured_metrics)


@pytest.mark.asyncio
async def test_doc2agent_aggregated_metrics_summary() -> None:
    framework = FakeToolsFramework()
    plan = [
        {"prompt": "first", "tool": "fast", "params": {"value": 1}},
        {"prompt": "second", "tool": "slow", "params": {"value": 2}},
        {"prompt": "third", "tool": "slow", "params": {"value": 3}},
    ]

    agent = Doc2Agent(
        tool_framework=framework,
        analyst=lambda text: plan,
        alert_callback=lambda _: None,
    )

    await agent.plan_and_execute(["doc"], "goal")
    aggregate = agent.get_aggregate_metrics()

    assert aggregate["total_steps"] == 3
    assert aggregate["failure_rate"] == 0.0
    assert "slow" in aggregate["tools"]
    assert aggregate["tools"]["slow"]["total"] == 2
    assert aggregate["tools"]["fast"]["avg_latency_ms"] >= 0

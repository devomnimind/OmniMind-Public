import pytest

from DEVBRAIN_V23.autonomy.self_healing import SelfHealingLoop


@pytest.mark.asyncio
async def test_self_healing_metrics_and_remediation() -> None:
    metrics_log: list[dict] = []
    alerts: list[str] = []

    loop = SelfHealingLoop(
        metrics_sink=metrics_log.append,
        alert_callback=alerts.append,
    )

    async def monitor() -> dict:
        return {"status": "error", "type": "monitor_issue", "id": "42"}

    async def remediation(_: dict) -> dict:
        return {"success": True, "description": "fixed"}

    loop.register_monitor(monitor)
    loop.register_remediation("monitor_issue", remediation)

    actions = await loop.run_cycle()

    assert actions
    assert metrics_log
    assert metrics_log[0]["metrics"]["cycles"] == 1
    assert metrics_log[0]["metrics"]["issues_detected"] == 1
    assert loop.get_metrics()["remediations"] == 1
    assert not alerts
    assert loop.issue_history


@pytest.mark.asyncio
async def test_self_healing_monitor_failure_alerts() -> None:
    alerts: list[str] = []

    loop = SelfHealingLoop(alert_callback=alerts.append)

    async def broken() -> dict:
        raise RuntimeError("boom")

    loop.register_monitor(broken)

    actions = await loop.run_cycle()

    assert actions == []
    assert alerts

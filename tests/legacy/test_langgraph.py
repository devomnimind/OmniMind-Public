import pytest
from unittest.mock import AsyncMock

from DEVBRAIN_V23.orchestration.langgraph_coordinator import LangGraphCoordinator


class MemoryStub:
    def __init__(self) -> None:
        self.stored: list[dict] = []
        self.queries: list[str] = []

    async def query_similar_episodes(self, task: str, top_k: int = 3) -> list[dict]:
        self.queries.append(task)
        return [{"id": "cached", "document": "doc", "metadata": {}}]

    async def store_episode(self, payload: dict) -> None:
        self.stored.append(payload)


class MockResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class SensorStub:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def capture_state(self) -> dict:
        self.calls.append("captured")
        return {"screen": "clean"}


@pytest.mark.asyncio
async def test_langgraph_run_success() -> None:
    llm = AsyncMock()
    llm.ainvoke.side_effect = [
        MockResponse("{}"),
        MockResponse('{"issues": [], "severity": "low"}'),
        MockResponse("Final summary"),
    ]
    memory = MemoryStub()
    sensors = SensorStub()
    coordinator = LangGraphCoordinator(llm, amem=memory, sensor_bridge=sensors)
    result = await coordinator.run("Plan a trip")

    assert result["status"] == "success"
    assert result["plan_steps"] == 5
    assert result["final_result"] == "Final summary"
    assert memory.stored
    assert memory.queries
    assert sensors.calls
    stored_metadata = memory.stored[0]["sensor_snapshot"]
    assert stored_metadata.get("screen") == "clean"


@pytest.mark.asyncio
async def test_langgraph_errors_bubble_up() -> None:
    llm = AsyncMock()
    llm.ainvoke.side_effect = [
        MockResponse("{}"),
        MockResponse('{"issues": ["missing step"], "severity": "high"}'),
    ]
    memory = MemoryStub()
    sensors = SensorStub()
    coordinator = LangGraphCoordinator(llm, amem=memory, sensor_bridge=sensors)
    result = await coordinator.run("Impossible request")

    assert result["status"] == "failed"
    assert "final_result" in result

import pytest

from DEVBRAIN_V23.memory.agentic_memory import AgenticMemory


@pytest.mark.asyncio
async def test_store_and_query_episode() -> None:
    memory = AgenticMemory(persist_directory=None)
    episode = {
        "task": "book flight",
        "details": ["search flights", "compare prices"],
        "status": "success",
    }
    episode_id = await memory.store_episode(episode)
    assert episode_id
    similar = await memory.query_similar_episodes("book flight")
    assert similar
    assert similar[0]["id"]


@pytest.mark.asyncio
async def test_consolidate_reports_duplicates() -> None:
    memory = AgenticMemory(persist_directory=None)
    episode = {"task": "deploy", "status": "success"}
    await memory.store_episode(episode)
    await memory.store_episode(episode)
    summary = await memory.consolidate_memory()
    assert summary["duplicates_removed"] >= 1
    assert summary["version"] >= 1


@pytest.mark.asyncio
async def test_cache_hits_increment() -> None:
    memory = AgenticMemory(persist_directory=None)
    episode = {"task": "analyze", "status": "success"}
    await memory.store_episode(episode)
    await memory.query_similar_episodes("analyze")
    await memory.query_similar_episodes("analyze")
    assert memory.cache_hits == 1


@pytest.mark.asyncio
async def test_alerts_on_failure(monkeypatch) -> None:
    alerts: list[str] = []
    memory = AgenticMemory(persist_directory=None, alert_callback=alerts.append)

    def raising_add(*_: object, **__: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(memory.episodic, "add", raising_add)

    with pytest.raises(RuntimeError):
        await memory.store_episode({"task": "fail", "status": "error"})

    assert alerts

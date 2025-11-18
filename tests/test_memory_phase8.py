"""Targeted Phase 8 tests for the episodic memory subsystem."""

import pytest
from typing import List, Dict, Any, Optional

from src.memory import episodic_memory as episodic_module
from src.memory.episodic_memory import EpisodicMemory


class DummyDistance:
    COSINE = "cosine"


class DummyVectorParams:
    def __init__(self, size: int, distance: str):
        self.size = size
        self.distance = distance


class DummyPointStruct:
    def __init__(self, id: int, vector: List[float], payload: Dict[str, Any]) -> None:
        self.id = id
        self.vector = vector
        self.payload = payload


class DummyFieldCondition:
    def __init__(self, key: str, range: Dict[str, Any]) -> None:
        self.key = key
        self.range = range


class DummyFilter:
    def __init__(self, must: Optional[List[Any]] = None) -> None:
        self.must = must or []


class DummyQdrantClient:
    def __init__(self, url: str) -> None:
        self.store: Dict[str, Any] = {}
        self._order: List[str] = []

    def get_collections(self) -> Any:
        return type("Collections", (), {"collections": []})()

    def create_collection(self, **kwargs: Any) -> None:
        return None

    def upsert(self, collection_name: str, points: List[Any]) -> None:
        for point in points:
            key = str(point.id)
            self.store[key] = {"id": point.id, "payload": point.payload}
            if key in self._order:
                self._order.remove(key)
            self._order.append(key)

    def query_points(self, *args: Any, **kwargs: Any) -> Any:
        limit = kwargs.get("limit", 3)
        hits = []
        query_filter = kwargs.get("query_filter")
        for record in self.store.values():
            payload = record["payload"]
            if query_filter and query_filter.must:
                condition = query_filter.must[0]
                if payload.get(condition.key, 0) < condition.range.get("gte", 0):
                    continue
            hits.append(type("Hit", (), {"score": 1.0, "payload": payload}))
            if len(hits) >= limit:
                break
        return type("Result", (), {"points": hits})()

    def retrieve(self, *args: Any, **kwargs: Any) -> List[Any]:
        ids = kwargs.get("ids") or args[1]
        if isinstance(ids, list):
            ids_iter = ids
        else:
            ids_iter = [ids]
        hits = []
        for identifier in ids_iter:
            record = self.store.get(str(identifier))
            if record:
                hits.append(type("Hit", (), {"payload": record["payload"]}))
        return hits

    def get_collection(self, name: str) -> Any:
        return type("Info", (), {"points_count": len(self.store)})()

    def scroll(
        self,
        collection_name: str,
        offset: Optional[int] = None,
        limit: int = 10,
        **kwargs: Any,
    ) -> tuple[List[Any], Optional[int]]:
        start = max(0, offset or 0)
        end = start + limit
        points = []
        for key in self._order[start:end]:
            record = self.store.get(key)
            if not record:
                continue
            payload = record["payload"]
            point_id = record["id"]
            points.append(type("Point", (), {"id": point_id, "payload": payload}))
        new_offset = end if end < len(self._order) else None
        return points, new_offset

    def delete(
        self,
        collection_name: str,
        points: Optional[List[Any]] = None,
        ids: Optional[List[Any]] = None,
        **kwargs: Any,
    ) -> None:
        to_remove = points or ids or kwargs.get("points_selector") or []
        for point_id in to_remove:
            key = str(point_id)
            if key in self.store:
                del self.store[key]
            if key in self._order:
                self._order.remove(key)


def _patch_memory_module() -> None:
    replacements = {
        "QdrantClient": DummyQdrantClient,
        "PointStruct": DummyPointStruct,
        "Distance": DummyDistance,
        "VectorParams": DummyVectorParams,
        "Filter": DummyFilter,
        "FieldCondition": DummyFieldCondition,
        "MatchValue": lambda *args, **kwargs: None,
    }
    for name, value in replacements.items():
        setattr(episodic_module, name, value)


_patch_memory_module()
# EpisodicMemory = episodic_module.EpisodicMemory  # Use imported instead


@pytest.fixture
def episodic_memory() -> EpisodicMemory:
    return episodic_module.EpisodicMemory(
        qdrant_url="http://localhost:6333",
        collection_name="test_memory",
        embedding_dim=4,
    )


def test_store_and_retrieve_episode(episodic_memory: EpisodicMemory) -> None:
    episode_id = episodic_memory.store_episode(
        task="test_task",
        action="run_test",
        result="success",
        reward=0.5,
        metadata={"context": "phase8"},
    )

    retrieved = episodic_memory.get_episode(episode_id)
    assert retrieved is not None
    assert retrieved["task"] == "test_task"
    assert retrieved["reward"] == 0.5

    search_results = episodic_memory.search_similar("test", top_k=2)
    assert search_results
    assert search_results[0]["task"] == "test_task"


def test_consolidate_memory_noop(episodic_memory: EpisodicMemory) -> None:
    # Force consolidation path to short-circuit gracefully
    summary = episodic_memory.consolidate_memory(min_episodes=5)
    assert summary["status"] == "skipped"
    assert summary["duplicates_removed"] == 0

    # Should not raise and stats reflect stored items
    stats = episodic_memory.get_stats()
    assert stats["total_episodes"] >= 0


def test_consolidate_memory_deduplicates(episodic_memory: EpisodicMemory) -> None:
    # Insert multiple experiences with identical metadata to trigger consolidation
    for _ in range(3):
        episodic_memory.store_episode(
            task="dup_task",
            action="document",
            result="consolidate",
            reward=0.0,
        )

    stats_before = episodic_memory.get_stats()
    assert stats_before["total_episodes"] == 3

    summary = episodic_memory.consolidate_memory(min_episodes=0)
    assert summary["status"] == "consolidated"
    assert summary["duplicates_removed"] == 2
    assert summary["remaining"] == 1

    stats_after = episodic_memory.get_stats()
    assert stats_after["total_episodes"] == 1

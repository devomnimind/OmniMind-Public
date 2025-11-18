from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.integrations.graphql_supabase import GraphQLSupabaseError
from src.integrations.supabase_adapter import SupabaseConfig
from src.onboarding.memory_onboarding import SupabaseMemoryOnboarding


class DummyMemory:
    def __init__(self) -> None:
        self.episodes: List[Dict[str, Any]] = []

    def store_episode(
        self,
        task: str,
        action: str,
        result: str,
        reward: float,
        metadata: Dict[str, Any],
    ) -> None:
        self.episodes.append(
            {
                "task": task,
                "action": action,
                "result": result,
                "reward": reward,
                "metadata": metadata,
            }
        )


class DummyHelper:
    def __init__(self, pages: List[Dict[str, Any]]) -> None:
        self.pages = pages
        self.calls = 0

    def fetch_page(
        self,
        collection: str,
        node_fields: List[str],
        first: int,
        after: Optional[str] = None,
    ) -> Any:
        self.calls += 1
        if not self.pages:
            return type(
                "DummyPage", (), {"nodes": [], "has_next": False, "cursor": None}
            )
        page = self.pages.pop(0)
        return type(
            "DummyPage",
            (),
            {
                "nodes": page["nodes"],
                "has_next": page["has_next"],
                "cursor": page["cursor"],
            },
        )()


def test_supabase_onboarding_processes_nodes() -> None:
    config = SupabaseConfig(
        url="https://supabase.test", anon_key="anon", service_role_key="service"
    )
    memory = DummyMemory()
    helper = DummyHelper(
        pages=[
            {
                "nodes": [
                    {
                        "id": "1",
                        "content": "first",
                        "metadata": {"task": "seed", "action": "import", "reward": 0.3},
                    },
                ],
                "has_next": True,
                "cursor": "a",
            },
            {
                "nodes": [
                    {"id": "2", "content": "second", "metadata": '{"action": "merge"}'},
                ],
                "has_next": False,
                "cursor": "b",
            },
        ]
    )

    onboarding = SupabaseMemoryOnboarding(config=config, memory=memory, helper=helper)
    report = onboarding.seed_collection(page_size=1)

    assert report.nodes_processed == 2
    assert report.nodes_loaded == 2
    assert report.last_cursor == "b"
    assert not report.errors
    assert len(memory.episodes) == 2
    assert memory.episodes[1]["action"] == "merge"


def test_supabase_onboarding_handles_error() -> None:
    config = SupabaseConfig(
        url="https://supabase.test", anon_key="anon", service_role_key="service"
    )
    memory = DummyMemory()

    class ErrorHelper(DummyHelper):
        def fetch_page(
            self,
            collection: str,
            node_fields: List[str],
            first: int,
            after: Optional[str] = None,
        ) -> Any:
            raise GraphQLSupabaseError("boom")

    onboarding = SupabaseMemoryOnboarding(
        config=config, memory=memory, helper=ErrorHelper([])
    )
    report = onboarding.seed_collection()

    assert report.nodes_processed == 0
    assert report.nodes_loaded == 0
    assert report.errors == ["boom"]

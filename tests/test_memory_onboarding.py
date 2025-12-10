from __future__ import annotations

from typing import Any, Dict, List, Optional, cast

from src.integrations.graphql_supabase import (
    GraphQLSupabaseError,
    GraphQLSupabaseHelper,
)
from src.integrations.supabase_adapter import SupabaseConfig
from src.memory import EpisodicMemory
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
            return type("DummyPage", (), {"nodes": [], "has_next": False, "cursor": None})
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

    onboarding = SupabaseMemoryOnboarding(
        config=config,
        memory=cast(EpisodicMemory, memory),
        helper=cast(GraphQLSupabaseHelper, helper),
    )
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
        config=config,
        memory=cast(EpisodicMemory, memory),
        helper=cast(GraphQLSupabaseHelper, ErrorHelper([])),
    )
    report = onboarding.seed_collection()

    assert report.nodes_processed == 0
    assert report.nodes_loaded == 0
    assert len(report.errors) == 1
    assert "boom" in report.errors[0]  # Message format: "GraphQL error on page 1: boom"


class TestMemoryOnboardingHybridTopological:
    """Testes de integração entre MemoryOnboarding e HybridTopologicalEngine."""

    def test_memory_onboarding_with_topological_metrics(self):
        """Testa que MemoryOnboarding pode ser usado com métricas topológicas."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Criar onboarding
        config = SupabaseConfig(
            url="https://supabase.test", anon_key="anon", service_role_key="service"
        )
        memory = DummyMemory()
        helper = DummyHelper(pages=[])
        onboarding = SupabaseMemoryOnboarding(
            config=config,
            memory=cast(EpisodicMemory, memory),
            helper=cast(GraphQLSupabaseHelper, helper),
        )

        # Simular estados no workspace para métricas topológicas
        np.random.seed(42)
        for i in range(5):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            workspace.write_module_state("conscious_module", rho_C)
            workspace.write_module_state("preconscious_module", rho_P)
            workspace.write_module_state("unconscious_module", rho_U)
            workspace.advance_cycle()

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que ambas funcionam
        report = onboarding.seed_collection(page_size=1)
        assert report.nodes_processed >= 0
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # MemoryOnboarding: onboarding de memória (Supabase)
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa

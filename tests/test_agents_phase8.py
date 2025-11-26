"""Integration-style tests for Phase 8 readiness of agents."""

import sys
import types
from pathlib import Path
from typing import List, Dict, Any, Optional

import pytest

from src.agents.architect_agent import ArchitectAgent
from src.agents.code_agent import CodeAgent
from src.agents.orchestrator_agent import AgentMode, OrchestratorAgent
from src.agents.reviewer_agent import ReviewerAgent

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class DummyLLM:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.calls: List[str] = []

    def invoke(self, prompt: str) -> str:
        self.calls.append(prompt)
        return (
            "correctness: 8\n"
            "readability: 7\n"
            "efficiency: 6\n"
            "security: 6\n"
            "maintainability: 7\n"
            "OVERALL_SCORE: 6.8\n"
        )


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

    def get_collections(self) -> Any:
        return type("Collections", (), {"collections": []})()

    def create_collection(self, **kwargs: Any) -> None:
        return None

    def upsert(self, collection_name: str, points: List[Any]) -> None:
        for point in points:
            payload = point.payload
            self.store[str(point.id)] = payload

    def query_points(self, *args: Any, **kwargs: Any) -> Any:
        limit = kwargs.get("limit", 3)
        query_filter = kwargs.get("query_filter")
        hits = []
        for payload in self.store.values():
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
            payload = self.store.get(str(identifier))
            if payload:
                hits.append(type("Hit", (), {"payload": payload}))
        return hits

    def get_collection(self, name: str) -> Any:
        return type("Info", (), {"points_count": len(self.store)})()


def _patch_memory_module() -> None:
    import src.memory.episodic_memory as episodic_module

    episodic_module.QdrantClient = DummyQdrantClient  # type: ignore[assignment,misc]
    episodic_module.PointStruct = DummyPointStruct  # type: ignore[assignment]
    episodic_module.Distance = DummyDistance  # type: ignore[assignment]
    episodic_module.VectorParams = DummyVectorParams  # type: ignore[assignment]
    episodic_module.Filter = DummyFilter  # type: ignore[assignment]
    episodic_module.FieldCondition = DummyFieldCondition  # type: ignore[assignment]
    episodic_module.MatchValue = lambda *args, **kwargs: None  # type: ignore[assignment]


_patch_memory_module()

try:
    import langchain_ollama
except ImportError:
    langchain_ollama = types.SimpleNamespace()  # type: ignore[assignment]
    sys.modules["langchain_ollama"] = langchain_ollama


@pytest.fixture
def config_path() -> str:
    return str(PROJECT_ROOT / "config" / "agent_config.yaml")


@pytest.fixture
def orchestrator(config_path: str) -> Any:
    return OrchestratorAgent(config_path)


@pytest.fixture
def temporary_file(tmp_path: Path) -> Path:
    return tmp_path / "agent_output.py"


def test_orchestrator_creates_specialist_agents(
    orchestrator: OrchestratorAgent,
) -> None:
    code_agent = orchestrator._get_agent(AgentMode.CODE)
    assert hasattr(code_agent, "mode") and code_agent.mode == "code"
    assert orchestrator._get_agent(AgentMode.ARCHITECT).mode == "architect"
    plan = orchestrator._parse_plan(
        "SUBTASKS:\n1. [CODE] Implement feature\n2. [REVIEWER] Score it\n"
    )
    assert len(plan["subtasks"]) == 2
    assert any(subtask["agent"] == "code" for subtask in plan["subtasks"])


def test_code_agent_writes_and_records(config_path: str, temporary_file: Path) -> None:
    agent = CodeAgent(config_path)
    description = agent._get_available_tools_description()
    assert "AVAILABLE TOOLS" in description

    result = agent._execute_action(
        "write_to_file",
        {"filepath": str(temporary_file), "content": "print('hello world')"},
    )
    assert temporary_file.exists()
    assert "hello world" in temporary_file.read_text()
    assert result == "Success"

    unknown = agent._execute_action("nonexistent_tool", {})
    assert "Unknown tool" in unknown


def test_architect_restrictions_and_writing(config_path: str, tmp_path: Path) -> None:
    agent = ArchitectAgent(config_path)
    assert agent._validate_write_permission("README.md")
    assert not agent._validate_write_permission("app.py")

    doc_path = tmp_path / "design.md"
    resp = agent._execute_action(
        "write_to_file",
        {"filepath": str(doc_path), "content": "# Architecture"},
    )
    assert "tool 'write_to_file' not allowed in architect mode" in resp.lower()
    assert not doc_path.exists()

    blocked = agent._execute_action("write_to_file", {"filepath": "app.py", "content": ""})
    assert "architectagent can only edit documentation files" in blocked.lower()


def test_reviewer_scores_code(config_path: str, tmp_path: Path) -> None:
    agent = ReviewerAgent(config_path)
    agent.llm = DummyLLM()  # type: ignore[assignment]

    code_file = tmp_path / "fibonacci.py"
    code_file.write_text(
        """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    )

    review = agent.review_code(str(code_file), "Review Fibonacci builder")
    assert review["overall_score"] == 6.8
    assert review["passed"] is False
    assert review["scores"]["correctness"] == 8.0

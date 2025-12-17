"""Additional Phase 8 agent coverage tests."""

from pathlib import Path
from typing import Any, Dict, List

import pytest

from src.agents.architect_agent import ArchitectAgent
from src.agents.code_agent import CodeAgent

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agent_config.yaml"


class DummyLLM:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.history: List[str] = []

    def invoke(self, prompt: str) -> str:
        self.history.append(prompt)
        return "REASONING: stub\nACTION: system_info\nARGS: {}"


class DummyMemory:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.episodes: List[Dict[str, Any]] = []

    def search_similar(
        self, query: str, top_k: int = 3, min_reward: float | None = None
    ) -> List[Dict[str, Any]]:
        return []

    def store_episode(
        self,
        task: str,
        action: str,
        result: str,
        reward: float = 0.0,
        metadata: Dict[str, Any] | None = None,
    ) -> str:
        entry = {
            "task": task,
            "action": action,
            "result": result,
            "reward": reward,
            "metadata": metadata or {},
        }
        self.episodes.append(entry)
        return str(len(self.episodes))

    def get_stats(self) -> Dict[str, Any]:
        return {"total_episodes": len(self.episodes)}


@pytest.fixture(autouse=True)
def patch_agent_dependencies(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    import langchain_ollama

    monkeypatch.setattr(langchain_ollama, "OllamaLLM", DummyLLM)
    import src.memory.episodic_memory as mem_mod

    monkeypatch.setattr(mem_mod, "EpisodicMemory", DummyMemory)


@pytest.fixture
def config_path() -> Path:
    return CONFIG_PATH


def test_architect_writes_documentation(tmp_path: Path, config_path: Path) -> None:
    agent = ArchitectAgent(str(config_path))
    target = tmp_path / "architecture.md"

    # Document extensions are permitted, but writing still blocked by tool category
    assert agent._validate_write_permission(str(target))
    response = agent._execute_action(
        "write_to_file", {"filepath": str(target), "content": "# Plan"}
    )
    assert "tool 'write_to_file' not allowed" in response.lower()
    assert not target.exists()


def test_code_agent_records_history(tmp_path: Path, config_path: Path) -> None:
    agent = CodeAgent(str(config_path))
    description = agent._get_available_tools_description()
    assert "AVAILABLE TOOLS" in description

    target = tmp_path / "module.py"
    result = agent._execute_action(
        "write_to_file", {"filepath": str(target), "content": "print('ok')"}
    )
    assert result == "Success"
    assert target.read_text().strip() == "print('ok')"
    assert agent.code_history
    assert agent.code_history[-1]["action"] == "write_to_file"

    unknown = agent._execute_action("nonexistent_tool", {})
    assert "Unknown tool" in unknown

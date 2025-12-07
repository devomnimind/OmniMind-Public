"""Integration coverage for the core agent modules."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import langchain_ollama
import pytest

from src.agents.debug_agent import DebugAgent
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.react_agent import AgentState, ReactAgent


class DummyLLM:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.history: List[str] = []

    def invoke(self, prompt: str) -> str:
        self.history.append(prompt)
        return "REASONING: stub\nACTION: system_info\nARGS: {}"


class InMemoryMemory:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.episodes: List[Dict[str, Any]] = []

    def search_similar(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        query = args[0] if args else kwargs.get("query", "")
        return [episode for episode in self.episodes if query in episode.get("task", "")]

    def store_episode(
        self,
        task: str,
        action: str,
        result: str,
        reward: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        entry = {
            "task": task,
            "action": action,
            "result": result,
            "reward": reward,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "episode_id": str(len(self.episodes) + 1),
        }
        self.episodes.append(entry)
        return str(len(self.episodes))

    def get_stats(self) -> Dict[str, int]:
        return {"total_episodes": len(self.episodes)}

    def get_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        for entry in self.episodes:
            if entry.get("episode_id") == episode_id:
                return entry
        return None

    def consolidate_memory(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        total = len(self.episodes)
        return {
            "status": "skipped",
            "total_episodes": total,
            "duplicates_removed": 0,
            "remaining": total,
        }


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "agent_config.yaml"


@pytest.fixture(autouse=True)
def isolate_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "home"))


@pytest.fixture(autouse=True)
def stub_agent_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(langchain_ollama, "OllamaLLM", DummyLLM)
    # Mock NarrativeHistory instead of EpisodicMemory (Phase 24 migration)
    monkeypatch.setattr("src.agents.react_agent.NarrativeHistory", InMemoryMemory)


def test_react_agent_performs_file_and_shell_ops() -> None:
    agent = ReactAgent(str(CONFIG_PATH))
    home_root = Path(os.environ["HOME"]) / "projects" / "omnimind" / "tmp" / "agents" / "react"
    home_root.mkdir(parents=True, exist_ok=True)

    target = home_root / "analysis.txt"
    write_result = agent._execute_action(
        "write_file", {"path": str(target), "content": "react coverage"}
    )
    assert "Successfully wrote" in write_result

    read_result = agent._execute_action("read_file", {"path": str(target)})
    assert "react coverage" in read_result

    list_result = agent._execute_action("list_files", {"path": str(home_root)})
    assert "analysis.txt" in list_result

    shell_output = agent._execute_action("execute_shell", {"command": f"ls {home_root}"})
    assert "analysis.txt" in shell_output

    state: AgentState = {
        "messages": [],
        "current_task": "observe",
        "reasoning_chain": [],
        "actions_taken": [
            {
                "action": "write_file",
                "result": "Success message for observation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "observations": [],
        "memory_context": [],
        "system_status": {},
        "iteration": 0,
        "max_iterations": 5,
        "completed": False,
        "final_result": "",
        "phi": 0.0,
        "psi": 0.0,
        "sigma": 0.0,
        "quality_score": 0.0,
    }

    observed_state = agent._observe_node(state)
    assert observed_state["completed"] is True


def test_orchestrator_parses_and_executes_plan() -> None:
    orchestrator = OrchestratorAgent(str(CONFIG_PATH))
    plan_text = """
    ANALYSIS: Break the deployment task
    SUBTASKS:
    1. [architect] Document the deployment pipeline
    2. [debug] Validate rollback scripts
    DEPENDENCIES:
    - Task 2 depends on Task 1
    ESTIMATED_COMPLEXITY: low
    """

    plan = orchestrator._parse_plan(plan_text)
    assert len(plan["subtasks"]) >= 2

    simple_agent = type("SimpleAgent", (), {})()

    def run_stub(task: str, max_iterations: int = 1, **kwargs: Any) -> Dict[str, Any]:
        return {
            "completed": True,
            "final_result": f"{task} done",
            "iteration": max_iterations,
        }

    setattr(simple_agent, "run", run_stub)
    setattr(simple_agent, "run_code_task", run_stub)

    orchestrator._get_agent = lambda mode: simple_agent  # type: ignore[method-assign]

    execution = orchestrator.execute_plan(
        {
            "subtasks": [
                {"agent": "architect", "description": "Document", "status": "pending"},
                {"agent": "debug", "description": "Validate", "status": "pending"},
            ],
            "original_task": "Deploy system",
            "complexity": "low",
        },
        max_iterations_per_task=1,
    )

    assert execution["overall_success"] is True
    assert len(execution["subtask_results"]) == 2
    assert all(result["completed"] for result in execution["subtask_results"])


def test_debug_agent_limits_actions() -> None:
    agent = DebugAgent(str(CONFIG_PATH))
    home_debug = Path(os.environ["HOME"]) / "projects" / "omnimind" / "tmp" / "agents" / "debug"
    home_debug.mkdir(parents=True, exist_ok=True)
    target = home_debug / "probe.txt"

    write_blocked = agent._execute_action(
        "write_to_file", {"filepath": str(target), "content": "nope"}
    )
    assert "DebugAgent cannot modify files" in write_blocked

    allowed = agent._execute_action("execute_command", {"command": "ls"})
    allowed_payload = json.loads(allowed)
    assert allowed_payload["status"] == "SUCCESS"

    blocked = agent._execute_action("execute_command", {"command": "rm -rf /tmp/nothing"})
    assert "Command not allowed" in blocked

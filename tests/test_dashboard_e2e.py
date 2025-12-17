import base64
import importlib
import json
from pathlib import Path
from typing import Any, Dict, Tuple

import pytest
from fastapi.testclient import TestClient


class DummyLLM:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def invoke(self, prompt: str) -> str:
        return """
SUBTASKS:
1. [code] Criar endpoint fake
2. [mcp] Ler configuração crítica
ESTIMATED_COMPLEXITY: medium
"""


class DummyMemory:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def store_episode(self, *args: Any, **kwargs: Any) -> str:
        return "dummy"

    def search_similar(self, *args: Any, **kwargs: Any) -> list[Dict[str, Any]]:
        return []


class DummyMonitor:
    @staticmethod
    def get_info() -> Dict[str, Any]:
        return {
            "cpu": {"percent": 1, "count": 4},
            "memory": {"total_gb": 16, "used_gb": 8, "percent": 50},
            "gpu": {"available": False},
        }

    @staticmethod
    def format_info(info: Any) -> str:
        return "dummy"


class DummyMCPClient:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def stat(self, path: str) -> Dict[str, Any]:
        return {"path": path, "status": "ok", "mode": "stat"}

    def read_file(self, path: str, *, encoding: str = "utf-8") -> str:
        return f"dummy content for {path}"

    def list_dir(self, path: str, *, recursive: bool = False) -> Dict[str, Any]:
        return {"path": path, "entries": [], "recursive": recursive}

    def get_metrics(self) -> Dict[str, Any]:
        return {"requests": 1, "errors": 0}


class DummyOrchestrator:
    def __init__(self, config_path: str):
        self.security_agent = None
        self.current_plan: Dict[str, Any] = {}
        self.dashboard_snapshot: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}

    def metrics_summary(self) -> Dict[str, Any]:
        return {}

    def run_orchestrated_task(self, task: str, max_iterations: int = 3) -> Dict[str, Any]:
        return {
            "success": True,
            "plan": {"subtasks": [{"status": "completed"}]},
            "execution": {
                "overall_success": True,
                "subtask_results": [{"completed": True, "summary": "done"}],
            },
        }

    def refresh_dashboard_snapshot(self) -> Dict[str, Any]:
        return {
            "plan_summary": {"completed": 1, "failed": 0},
            "security_status": {"events": 0},
            "timestamp": "2025-11-27T12:00:00Z",
        }

    def trigger_mcp_action(self, **kwargs: Any) -> Dict[str, Any]:
        return {}

    def trigger_dbus_action(self, **kwargs: Any) -> Dict[str, Any]:
        return {}

    def plan_overview(self) -> Dict[str, Any]:
        return {}


@pytest.fixture()
def dashboard_client(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> Tuple[TestClient, Dict[str, str]]:
    monkeypatch.setattr("src.agents.react_agent.OllamaLLM", DummyLLM)
    # Mock NarrativeHistory instead of EpisodicMemory (Phase 24 migration)
    monkeypatch.setattr("src.agents.react_agent.NarrativeHistory", DummyMemory)
    monkeypatch.setattr("src.agents.react_agent.SystemMonitor", DummyMonitor)
    monkeypatch.setattr("src.agents.orchestrator_agent.MCPClient", DummyMCPClient)
    # Mock OrchestratorAgent to avoid async initialization delay and dependency issues
    monkeypatch.setattr("src.agents.orchestrator_agent.OrchestratorAgent", DummyOrchestrator)

    monkeypatch.setenv("OMNIMIND_DASHBOARD_USER", "e2e_user")
    monkeypatch.setenv("OMNIMIND_DASHBOARD_PASS", "e2e_secret")
    validation_dir = tmp_path_factory.mktemp("security_validation")
    validation_log = validation_dir / "validation.jsonl"
    validation_entry = {
        "timestamp": "2025-11-18T12:00:00Z",
        "audit": {"valid": True, "message": "Cadeia íntegra", "events_verified": 1},
        "dlp": {"policies": ["credentials"]},
        "sandbox": {
            "kernel": "/opt/firecracker/vmlinux.bin",
            "kernel_exists": False,
            "rootfs": "/opt/firecracker/rootfs.ext4",
            "rootfs_exists": False,
        },
    }
    validation_log.write_text(json.dumps(validation_entry) + "\n")
    monkeypatch.setenv("OMNIMIND_SECURITY_VALIDATION_LOG", str(validation_log))

    import web.backend.main as backend_main

    importlib.reload(backend_main)

    # Force set the orchestrator instance to avoid 503
    backend_main._orchestrator_instance = DummyOrchestrator(
        "config/agent_config.yaml"
    )  # type: ignore[assignment]

    client = TestClient(backend_main.app)
    auth_value = base64.b64encode(b"e2e_user:e2e_secret").decode("ascii")
    headers = {"Authorization": f"Basic {auth_value}"}
    return client, headers


def test_dashboard_requires_auth(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    backend_main = importlib.import_module("web.backend.main")

    # Cenário 1: sem credenciais configuradas -> 401
    monkeypatch.delenv("OMNIMIND_DASHBOARD_USER", raising=False)
    monkeypatch.delenv("OMNIMIND_DASHBOARD_PASS", raising=False)
    backend_main = importlib.reload(backend_main)
    client = TestClient(backend_main.app)
    response = client.get("/observability")
    assert response.status_code == 401

    # Cenário 2: credenciais via variáveis de ambiente funcionam
    monkeypatch.setenv("OMNIMIND_DASHBOARD_USER", "test_user")
    monkeypatch.setenv("OMNIMIND_DASHBOARD_PASS", "test_pass")
    backend_main = importlib.reload(backend_main)
    client = TestClient(backend_main.app)
    auth_value = base64.b64encode(b"test_user:test_pass").decode("ascii")
    headers = {"Authorization": f"Basic {auth_value}"}
    response = client.get("/observability", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert "self_healing" in payload
    assert "atlas" in payload
    assert payload.get("alerts") is not None

    # Cenário 3: credenciais inválidas continuam sendo rejeitadas
    invalid_headers = {
        "Authorization": f"Basic {base64.b64encode(b'invalid:creds').decode('ascii')}"
    }
    invalid_response = client.get("/observability", headers=invalid_headers)
    assert invalid_response.status_code == 401


def test_orchestrate_and_metrics(
    dashboard_client: Tuple[TestClient, Dict[str, str]],
) -> None:
    client, headers = dashboard_client
    payload = {"task": "Validar MCP e D-Bus", "max_iterations": 1}
    response = client.post("/tasks/orchestrate", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dashboard_snapshot" in data
    assert data.get("success") is not None if isinstance(data, dict) else False
    execution = data.get("execution", {}) if isinstance(data, dict) else {}
    assert execution.get("overall_success") is True if isinstance(execution, dict) else False
    assert execution.get("subtask_results") if isinstance(execution, dict) else False
    for sub in (
        execution["subtask_results"]
        if isinstance(execution, dict) and "subtask_results" in execution
        else []
    ):
        assert sub.get("completed") is True if isinstance(sub, dict) else False
        assert sub.get("summary") if isinstance(sub, dict) else False
    plan = data.get("plan", {}) if isinstance(data, dict) else {}
    assert plan.get("subtasks") if isinstance(plan, dict) else False
    for sub in plan["subtasks"] if isinstance(plan, dict) and "subtasks" in plan else []:
        assert sub.get("status") == "completed" if isinstance(sub, dict) else False

    metrics = client.get("/metrics", headers=headers)
    assert metrics.status_code == 200
    metrics_data = metrics.json()
    assert metrics_data["backend"]["requests"] >= 1

    snapshot = client.get("/snapshot", headers=headers)
    assert snapshot.status_code == 200
    snapshot_data = snapshot.json()
    assert "plan_summary" in snapshot_data


def test_observability_endpoint(
    dashboard_client: Tuple[TestClient, Dict[str, str]],
) -> None:
    client, headers = dashboard_client
    response = client.get("/observability", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert "self_healing" in payload
    assert "atlas" in payload
    assert "alerts" in payload
    assert isinstance(payload["alerts"], list)
    assert isinstance(payload["self_healing"], dict)
    validation = payload.get("validation") if isinstance(payload, dict) else None
    assert validation is not None
    assert (
        validation.get("latest", {}).get("audit", {}).get("valid") is True
        if isinstance(validation, dict)
        else False
    )

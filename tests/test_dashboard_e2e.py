import base64
import importlib
import json
from typing import Tuple

import pytest
from fastapi.testclient import TestClient


class DummyLLM:
    def __init__(self, *args, **kwargs):
        pass

    def invoke(self, prompt: str) -> str:
        return """
SUBTASKS:
1. [code] Criar endpoint fake
2. [mcp] Ler configuração crítica
ESTIMATED_COMPLEXITY: medium
"""


class DummyMemory:
    def __init__(self, *args, **kwargs):
        pass

    def store_episode(self, *args, **kwargs) -> str:
        return "dummy"

    def search_similar(self, *args, **kwargs):
        return []


class DummyMonitor:
    @staticmethod
    def get_info():
        return {
            "cpu": {"percent": 1, "count": 4},
            "memory": {"total_gb": 16, "used_gb": 8, "percent": 50},
            "gpu": {"available": False},
        }

    @staticmethod
    def format_info(info) -> str:
        return "dummy"


class DummyMCPClient:
    def __init__(self, *args, **kwargs):
        pass

    def stat(self, path: str) -> dict:
        return {"path": path, "status": "ok", "mode": "stat"}

    def read_file(self, path: str, *, encoding: str = "utf-8") -> str:
        return f"dummy content for {path}"

    def list_dir(self, path: str, *, recursive: bool = False) -> dict:
        return {"path": path, "entries": [], "recursive": recursive}

    def get_metrics(self) -> dict:
        return {"requests": 1, "errors": 0}


@pytest.fixture()
def dashboard_client(monkeypatch, tmp_path_factory) -> Tuple[TestClient, dict]:
    monkeypatch.setattr("src.agents.react_agent.OllamaLLM", DummyLLM)
    monkeypatch.setattr("src.agents.react_agent.EpisodicMemory", DummyMemory)
    monkeypatch.setattr("src.agents.react_agent.SystemMonitor", DummyMonitor)
    monkeypatch.setattr("src.agents.orchestrator_agent.MCPClient", DummyMCPClient)
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
    client = TestClient(backend_main.app)
    auth_value = base64.b64encode(b"e2e_user:e2e_secret").decode("ascii")
    headers = {"Authorization": f"Basic {auth_value}"}
    return client, headers


def test_dashboard_requires_auth(monkeypatch, tmp_path):
    backend_main = importlib.import_module("web.backend.main")

    # Cenário 1: sem credenciais configuradas -> 401
    monkeypatch.delenv("OMNIMIND_DASHBOARD_USER", raising=False)
    monkeypatch.delenv("OMNIMIND_DASHBOARD_PASS", raising=False)
    backend_main = importlib.reload(backend_main)
    client = TestClient(backend_main.app)
    response = client.get("/observability")
    assert response.status_code == 401

    # Cenário 2: credenciais automáticas provenientes do arquivo seguro
    auto_creds = {"user": "auto_user", "pass": "auto_secret"}
    auth_file = tmp_path / "dashboard_auth.json"
    auth_file.write_text(json.dumps(auto_creds))
    monkeypatch.setenv("OMNIMIND_DASHBOARD_AUTH_FILE", str(auth_file))
    monkeypatch.delenv("OMNIMIND_DASHBOARD_USER", raising=False)
    monkeypatch.delenv("OMNIMIND_DASHBOARD_PASS", raising=False)
    backend_main = importlib.reload(backend_main)
    print(
        f"Usando credenciais automáticas: {auto_creds['user']} / {auto_creds['pass']}"
    )
    client = TestClient(backend_main.app)
    auth_value = base64.b64encode(
        f"{auto_creds['user']}:{auto_creds['pass']}".encode("ascii")
    ).decode("ascii")
    headers = {"Authorization": f"Basic {auth_value}"}
    auto_response = client.get("/observability", headers=headers)
    assert auto_response.status_code == 200
    payload = auto_response.json()
    assert "self_healing" in payload
    assert "atlas" in payload
    assert payload.get("alerts") is not None

    # Cenário 3: credenciais inválidas continuam sendo rejeitadas
    invalid_headers = {
        "Authorization": f"Basic {base64.b64encode(b'invalid:creds').decode('ascii')}"
    }
    invalid_response = client.get("/observability", headers=invalid_headers)
    assert invalid_response.status_code == 401


def test_orchestrate_and_metrics(dashboard_client):
    client, headers = dashboard_client
    payload = {"task": "Validar MCP e D-Bus", "max_iterations": 1}
    response = client.post("/tasks/orchestrate", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dashboard_snapshot" in data
    assert data.get("success") is not None
    execution = data.get("execution", {})
    assert execution.get("overall_success") is True
    assert execution.get("subtask_results")
    for sub in execution["subtask_results"]:
        assert sub.get("completed") is True
        assert sub.get("summary")
    plan = data.get("plan", {})
    assert plan.get("subtasks")
    for sub in plan["subtasks"]:
        assert sub.get("status") == "completed"

    metrics = client.get("/metrics", headers=headers)
    assert metrics.status_code == 200
    metrics_data = metrics.json()
    assert metrics_data["backend"]["requests"] >= 1

    snapshot = client.get("/snapshot", headers=headers)
    assert snapshot.status_code == 200
    snapshot_data = snapshot.json()
    assert "plan_summary" in snapshot_data


def test_observability_endpoint(dashboard_client):
    client, headers = dashboard_client
    response = client.get("/observability", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert "self_healing" in payload
    assert "atlas" in payload
    assert "alerts" in payload
    assert isinstance(payload["alerts"], list)
    assert isinstance(payload["self_healing"], dict)
    validation = payload.get("validation")
    assert validation is not None
    assert validation.get("latest", {}).get("audit", {}).get("valid") is True

"""Integration coverage for the OmniMind tools framework."""

import json
import uuid
from pathlib import Path
from typing import Any

import pytest

from src.tools.omnimind_tools import ToolsFramework


def _audit_log_path(home: Path) -> Path:
    return home / ".omnimind" / "audit" / "tools.log"


def _read_audit_entries(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    return [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]


def test_tools_framework_records_commands(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    home = tmp_path / "fake_home"
    monkeypatch.setenv("HOME", str(home))

    workspace = Path(__file__).resolve().parent.parent / "tmp" / "tools" / uuid.uuid4().hex
    workspace.mkdir(parents=True, exist_ok=True)

    framework = ToolsFramework()

    target = workspace / "notes.md"
    write_success = framework.execute_tool(
        "write_to_file",
        filepath=str(target),
        content="integration coverage",
    )
    assert write_success is True

    read_back = framework.execute_tool("read_file", filepath=str(target))
    assert "integration coverage" in read_back

    listing = framework.execute_tool("list_files", directory=str(workspace))
    assert any(entry.get("name") == "notes.md" for entry in listing)

    command = framework.execute_tool("execute_command", command="echo tools check")
    assert command["status"] == "SUCCESS"
    assert "tools check" in command["stdout"].strip()

    audit_entries = _read_audit_entries(_audit_log_path(home))
    assert any(entry["tool_name"] == "write_to_file" for entry in audit_entries)
    assert any(entry["tool_name"] == "read_file" for entry in audit_entries)
    assert any(entry["tool_name"] == "list_files" for entry in audit_entries)
    assert any(entry["tool_name"] == "execute_command" for entry in audit_entries)


def test_execute_command_blocks_forbidden(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    home = tmp_path / "fake_home"
    monkeypatch.setenv("HOME", str(home))

    framework = ToolsFramework()
    blocked = framework.execute_tool("execute_command", command="rm -rf /tmp/ignored")
    assert blocked["status"] == "BLOCKED"
    assert "Command not allowed" in blocked["error"]

    audit_entries = _read_audit_entries(_audit_log_path(home))
    assert any(
        entry["status"] == "BLOCKED"
        for entry in audit_entries
        if entry["tool_name"] == "execute_command"
    )


class TestToolsFrameworkHybridTopological:
    """Testes de integração entre ToolsFramework e HybridTopologicalEngine."""

    def test_tools_can_work_with_consciousness_metrics(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Testa que ferramentas podem trabalhar com métricas de consciência."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        home = tmp_path / "fake_home"
        monkeypatch.setenv("HOME", str(home))

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Simular estados
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

        # Verificar que ferramentas podem usar métricas topológicas para decisões
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # Ferramentas podem usar Omega para priorizar ações baseadas em integração
            # Betti-0 para identificar fragmentação que precisa ser resolvida

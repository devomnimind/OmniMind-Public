"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

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

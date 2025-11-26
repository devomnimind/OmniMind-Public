"""Realistic scenario tests for each security playbook."""

import json
import shutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Sequence

import pytest

import src.security.playbooks.utils as utils
from src.security.playbooks import (
    intrusion_response,
    malware_response,
    privilege_escalation_response,
    rootkit_response,
)
from src.security.playbooks.intrusion_response import IntrusionPlaybook
from src.security.playbooks.malware_response import MalwarePlaybook
from src.security.playbooks.privilege_escalation_response import (
    PrivilegeEscalationPlaybook,
)
from src.security.playbooks.rootkit_response import RootkitPlaybook
from src.security.playbooks.utils import CommandResult


async def _dummy_run(command: Sequence[str]) -> CommandResult:
    return {
        "command": " ".join(command),
        "returncode": 0,
        "output": "simulated",
    }


def test_utils_command_available(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda cmd: "/bin/echo" if cmd == "echo" else None)
    assert utils.command_available("echo")
    assert not utils.command_available("missing-tool")


def test_utils_run_command_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda cmd: None)
    result = utils.run_command(["missing-tool"])
    assert result["returncode"] == -1
    assert "command not available" in result["output"]


def test_utils_run_command_success() -> None:
    result = utils.run_command(["/bin/echo", "phase8"])
    assert result["returncode"] == 0
    assert "phase8" in result["output"]


@pytest.mark.asyncio
async def test_rootkit_playbook_handles_missing_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event = SimpleNamespace(
        event_type="rootkit_detected",
        description="Rootkit signature found",
    )
    monkeypatch.setattr(rootkit_response, "command_available", lambda _: False)
    monkeypatch.setattr(rootkit_response, "run_command_async", _dummy_run)
    playbook = RootkitPlaybook()
    result = await playbook.execute(None, event)
    assert result["status"] == "completed"
    assert not result["analysis"]["has_rootkit"]


@pytest.mark.asyncio
async def test_intrusion_playbook_scans_and_blocks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event = SimpleNamespace(
        event_type="intrusion",
        details={"remote": "192.168.1.100"},
        description="Suspicious connection",
    )
    monkeypatch.setattr(intrusion_response, "command_available", lambda _: False)
    monkeypatch.setattr(intrusion_response, "run_command_async", _dummy_run)
    playbook = IntrusionPlaybook()
    result = await playbook.execute(None, event)
    assert result["status"] == "completed"
    assert "scene" in result
    assert isinstance(result["scene"].get("path"), str)


@pytest.mark.asyncio
async def test_malware_playbook_attempts_quarantine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event = SimpleNamespace(
        event_type="malware_detected",
        details={"path": "/tmp/does_not_exist"},
        description="Malware sample",
    )
    monkeypatch.setattr(malware_response, "command_available", lambda _: False)
    monkeypatch.setattr(malware_response, "run_command_async", _dummy_run)
    playbook = MalwarePlaybook()
    result = await playbook.execute(None, event)
    assert result["status"] == "completed"
    assert "scans" in result
    assert "quarantine" in result
    assert "notification" in result


@pytest.mark.asyncio
async def test_privilege_escalation_playbook_steps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    event = SimpleNamespace(
        event_type="privilege_escalation",
        details={"user": "admin"},
        description="Sudo abuser",
    )
    monkeypatch.setattr(privilege_escalation_response, "command_available", lambda _: False)
    monkeypatch.setattr(privilege_escalation_response, "run_command_async", _dummy_run)
    playbook = PrivilegeEscalationPlaybook()
    result = await playbook.execute(None, event)
    assert result["status"] == "completed"
    assert "block" in result
    assert "revocation" in result


@pytest.mark.asyncio
async def test_rootkit_playbook_remediation_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: set[str] = set()

    async def stub(command: Sequence[str]) -> CommandResult:
        cmd_joined = " ".join(command)
        if "chkrootkit" in cmd_joined and "chkrootkit" not in seen:
            seen.add("chkrootkit")
            output = "INFECTED"
        else:
            output = "clean"
        return {
            "command": cmd_joined,
            "returncode": 0,
            "output": output,
        }

    monkeypatch.setattr(rootkit_response, "command_available", lambda _: True)
    monkeypatch.setattr(rootkit_response, "run_command_async", stub)

    event = SimpleNamespace(event_type="rootkit_detected")
    result = await RootkitPlaybook().execute(None, event)
    assert result["analysis"]["has_rootkit"]
    assert not result["verification"]["has_rootkit"]
    assert result["status"] == "completed"


@pytest.mark.asyncio
async def test_intrusion_playbook_blocks_and_preserves_scene(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    async def stub(command: Sequence[str]) -> CommandResult:
        return {
            "command": " ".join(command),
            "returncode": 0,
            "output": "ok",
        }

    def fake_write(path: str, payload: dict[str, Any]) -> None:
        destination = tmp_path / Path(path).name
        destination.write_text(json.dumps(payload))

    monkeypatch.setattr(intrusion_response, "command_available", lambda _: True)
    monkeypatch.setattr(intrusion_response, "run_command_async", stub)
    monkeypatch.setattr(
        IntrusionPlaybook,
        "_write_artifact",
        staticmethod(fake_write),
    )

    event = SimpleNamespace(
        event_type="intrusion",
        details={"remote": "10.0.0.5"},
        description="suspicious session",
    )
    result = await IntrusionPlaybook().execute(None, event)
    assert result["block"]["command"].startswith("sudo ufw deny")
    assert result["scene"]["path"].endswith(".json")
    assert result["scene"]["size"] > 0


@pytest.mark.asyncio
async def test_malware_playbook_quarantines_artifacts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def stub(command: Sequence[str]) -> CommandResult:
        return {
            "command": " ".join(command),
            "returncode": 0,
            "output": "ok",
        }

    monkeypatch.setattr(malware_response, "command_available", lambda _: True)
    monkeypatch.setattr(malware_response, "run_command_async", stub)

    event = SimpleNamespace(
        event_type="malware_detected",
        details={"path": "/tmp/malware.bin"},
        description="malicious file",
    )
    result = await MalwarePlaybook().execute(None, event)
    assert result["quarantine"]["artifact"] == "/tmp/malware.bin"
    assert "freshclam" in result["signatures"]["command"]


@pytest.mark.asyncio
async def test_privilege_escalation_playbook_revokes_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def stub(command: Sequence[str]) -> CommandResult:
        return {
            "command": " ".join(command),
            "returncode": 0,
            "output": "ok",
        }

    monkeypatch.setattr(privilege_escalation_response, "command_available", lambda _: True)
    monkeypatch.setattr(privilege_escalation_response, "run_command_async", stub)

    event = SimpleNamespace(
        event_type="privesc",
        details={"user": "attacker"},
        description="privilege escalation attempt",
    )
    result = await PrivilegeEscalationPlaybook().execute(None, event)
    assert result["revocation"]["command"].startswith("sudo pkill")
    assert result["notification"]["command"].startswith("/bin/echo")

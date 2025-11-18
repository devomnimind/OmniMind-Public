"""Integration tests for the SecurityAgent flows."""

import json
from pathlib import Path

import pytest

from src.security.security_agent import SecurityAgent, ThreatLevel


@pytest.mark.asyncio
async def test_security_agent_handles_event_and_reports(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    home = tmp_path / "fake_system"
    monkeypatch.setenv("HOME", str(home))

    config_path = tmp_path / "security-agent.yaml"
    config_path.write_text("""security_agent:\n  enabled: true\n""")

    agent = SecurityAgent(str(config_path))

    event = agent._create_event(
        event_type="malware_detected",
        source="unit/test",
        description="Malware trigger",
        details={"path": "/tmp/fake"},
        raw_data="payload",
        level=ThreatLevel.HIGH,
    )

    await agent._handle_event(event)
    await agent._execute_response(event)

    assert agent.event_history
    assert event.responded is True
    assert agent.incident_log

    report = agent.generate_security_report()
    assert "SECURITY REPORT" in report

    audit_path = home / ".omnimind" / "audit" / "tools.log"
    assert audit_path.exists()
    entries = [
        json.loads(line) for line in audit_path.read_text().splitlines() if line.strip()
    ]
    assert any(entry["tool_name"] == "security_agent" for entry in entries)

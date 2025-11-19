"""Integration tests for the SecurityAgent flows."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.orchestrator_agent import OrchestratorAgent
from src.security.security_agent import SecurityAgent, ThreatLevel


@pytest.mark.asyncio
async def test_security_agent_handles_event_and_reports(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    Test that a standalone SecurityAgent can handle a manual event,
    execute a response, and generate a report.
    """
    home = tmp_path / "fake_system"
    monkeypatch.setenv("HOME", str(home))

    config_path = tmp_path / "security-agent.yaml"
    config_path.write_text("security_agent:\n  enabled: true\n")

    # Mock the sandbox run to avoid real execution
    with patch("src.security.security_agent.FirecrackerSandbox.run") as mock_sandbox:
        mock_sandbox.return_value = MagicMock(success=True, output="Sandbox OK")

        agent = SecurityAgent(str(config_path))

        # Mock the playbook execution
        agent.playbooks["malware"].execute = AsyncMock(return_value={"status": "ok"})

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
        assert len(agent.incident_log) > 0
        assert agent.incident_log[0]["playbook"] == "malware"

        report = agent.generate_security_report()
        assert "SECURITY REPORT" in report
        assert "Total Events: 1" in report

        # Check that the audit log was written
        # The AuditedTool base class handles this
        audit_log_path = Path.home().joinpath(".omnimind/audit/tools.log")
        assert audit_log_path.exists()
        log_content = audit_log_path.read_text()
        assert '"tool_name": "security_agent"' in log_content
        assert '"action": "event"' in log_content


@pytest.mark.asyncio
async def test_orchestrator_integrates_security_agent_monitoring(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """
    Test that the OrchestratorAgent initializes the SecurityAgent and that
    the security monitoring can detect a simulated threat.
    """
    # Setup fake home and config files
    home = tmp_path / "fake_home"
    monkeypatch.setenv("HOME", str(home))
    (tmp_path / "config").mkdir()
    sec_config_path = tmp_path / "config" / "security.yaml"
    sec_config_path.write_text(
        """
security_agent:
  enabled: true
  monitoring_interval: 1
monitoring:
  processes:
    interval: 1
    suspicious_patterns: ["suspicious_proc"]
"""
    )
    config_path = tmp_path / "config" / "agent_config.yaml"
    config_path.write_text(
        f"""
model:
  name: 'fake_model'
  provider: 'fake'
  base_url: 'http://localhost:11434'
llm:
  provider: fake
memory:
  qdrant_url: "http://localhost:6333"
  collection_name: "test_collection"
system:
  mcp_allowed_dirs: ["/tmp"]
  shell_whitelist: ["echo"]
  shell_timeout: 30
security:
  config_path: "{sec_config_path.absolute()}"
"""
    )

    # Mock psutil to inject a fake suspicious process
    fake_process = MagicMock()
    fake_process.info = {
        "pid": 1234,
        "name": "suspicious_proc",
        "cmdline": ["suspicious_proc", "-arg"],
    }
    mock_process_iter = MagicMock(return_value=[fake_process])
    mock_net_connections = MagicMock(return_value=[])

    # We patch the security agent's playbook execution to prevent side effects
    with patch("psutil.process_iter", mock_process_iter), patch(
        "psutil.net_connections", mock_net_connections
    ), patch.object(
        SecurityAgent, "_execute_response", AsyncMock()
    ) as mock_execute_response, patch(
        "src.agents.react_agent.EpisodicMemory", MagicMock()
    ), patch(
        "src.agents.react_agent.ReactAgent._run_supabase_memory_onboarding",
        MagicMock(),
    ):
        # The orchestrator's __init__ will start the security agent
        orchestrator = OrchestratorAgent(str(config_path))
        assert orchestrator.security_agent is not None

        # Allow the monitoring loop to run a few times
        await asyncio.sleep(0.2)

        # Assert that the threat was detected and an event was created
        assert len(orchestrator.security_agent.event_history) > 0
        event = orchestrator.security_agent.event_history[0]
        assert event.event_type == "suspicious_process"
        assert event.details["name"] == "suspicious_proc"

        # Assert that the response mechanism was triggered
        mock_execute_response.assert_called_once()

        # Check dashboard snapshot integration
        snapshot = orchestrator.refresh_dashboard_snapshot()
        assert "security_status" in snapshot
        assert snapshot["security_status"]["events"] > 0

        # Clean up the monitoring task
        orchestrator.security_agent.request_stop()
        await asyncio.sleep(0.1)  # Give time for shutdown
        assert not orchestrator.security_agent._monitoring_tasks

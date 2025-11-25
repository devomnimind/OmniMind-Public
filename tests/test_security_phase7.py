"""Unit tests covering Phase 7 SecurityAgent behaviors."""

import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.security.security_agent import SecurityAgent, SecurityEvent, ThreatLevel


@pytest.fixture
def security_agent() -> SecurityAgent:
    return SecurityAgent("config/security.yaml")


@pytest.fixture
def suspicious_process_event() -> SecurityEvent:
    return SecurityEvent(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        event_type="suspicious_process",
        source="process_monitor",
        description="nmap process detected",
        details={"name": "nmap", "pid": 1234},
        threat_level=ThreatLevel.HIGH,
        raw_data="nmap localhost",
    )


def test_init_loads_config(security_agent: SecurityAgent) -> None:
    assert security_agent.config
    assert "monitoring" in security_agent.config


def test_tools_availability(security_agent: SecurityAgent) -> None:
    assert isinstance(security_agent.tools_available, dict)


def test_detect_suspicious_process(security_agent: SecurityAgent) -> None:
    proc = {"name": "nmap", "cmdline": ["nmap", "localhost"]}
    patterns = security_agent.config["monitoring"]["processes"]["suspicious_patterns"]
    assert security_agent._is_suspicious_process(proc, patterns)


def test_detect_normal_process(security_agent: SecurityAgent) -> None:
    proc = {"name": "bash", "cmdline": ["/bin/bash"]}
    patterns = security_agent.config["monitoring"]["processes"]["suspicious_patterns"]
    assert not security_agent._is_suspicious_process(proc, patterns)


def test_detect_suspicious_log(security_agent: SecurityAgent) -> None:
    keywords = security_agent.config["monitoring"]["logs"]["keywords"]
    assert security_agent._is_suspicious_log_line("Failed password for user", keywords)


def test_detect_normal_log(security_agent: SecurityAgent) -> None:
    keywords = security_agent.config["monitoring"]["logs"]["keywords"]
    assert not security_agent._is_suspicious_log_line("Normal log entry", keywords)


def test_event_recorded(
    security_agent: SecurityAgent, suspicious_process_event: SecurityEvent
) -> None:
    asyncio.run(security_agent._handle_event(suspicious_process_event))
    assert security_agent.event_history
    assert security_agent.event_history[0].event_type == "suspicious_process"


def test_generate_report_includes_summary(security_agent: SecurityAgent) -> None:
    report = security_agent.generate_security_report()
    assert "SECURITY REPORT" in report
    assert "SUMMARY" in report


def test_audit_action_creates_log(security_agent: SecurityAgent, tmp_path: Path) -> None:
    audit_log = tmp_path / "audit" / "tools.log"
    security_agent.audit_log_path = audit_log
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    security_agent._audit_action("test", {"foo": "bar"}, {"result": 1}, "SUCCESS")
    assert audit_log.exists()

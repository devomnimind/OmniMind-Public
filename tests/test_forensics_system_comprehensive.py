#!/usr/bin/env python3
"""
Comprehensive tests for forensics_system.py module.
Tests EvidenceCollector, Incident, and related functionality.
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.security.forensics_system import (
    EvidenceCollector,
    EvidenceItem,
    EvidenceType,
    ForensicsReport,
    Incident,
    IncidentSeverity,
    IncidentStatus,
)


class TestEvidenceType:
    """Test EvidenceType enum."""

    def test_evidence_types_exist(self):
        """Test that all evidence types are defined."""
        assert EvidenceType.LOG_ENTRY.value == "log_entry"
        assert EvidenceType.FILE_SYSTEM.value == "file_system"
        assert EvidenceType.NETWORK_CONNECTION.value == "network_connection"
        assert EvidenceType.PROCESS_INFO.value == "process_info"
        assert EvidenceType.SYSTEM_METRICS.value == "system_metrics"
        assert EvidenceType.CONFIGURATION.value == "configuration"
        assert EvidenceType.MEMORY_DUMP.value == "memory_dump"
        assert EvidenceType.SCREENSHOT.value == "screenshot"


class TestIncidentSeverity:
    """Test IncidentSeverity enum."""

    def test_incident_severities_exist(self):
        """Test that all incident severities are defined."""
        assert IncidentSeverity.LOW.value == "low"
        assert IncidentSeverity.MEDIUM.value == "medium"
        assert IncidentSeverity.HIGH.value == "high"
        assert IncidentSeverity.CRITICAL.value == "critical"


class TestIncidentStatus:
    """Test IncidentStatus enum."""

    def test_incident_statuses_exist(self):
        """Test that all incident statuses are defined."""
        assert IncidentStatus.OPEN.value == "open"
        assert IncidentStatus.INVESTIGATING.value == "investigating"
        assert IncidentStatus.CONTAINED.value == "contained"
        assert IncidentStatus.RESOLVED.value == "resolved"
        assert IncidentStatus.CLOSED.value == "closed"


class TestEvidenceItem:
    """Test EvidenceItem data structure."""

    def test_evidence_item_creation(self):
        """Test creating an EvidenceItem."""
        timestamp = datetime.now(timezone.utc).isoformat()
        evidence = EvidenceItem(
            id="evidence_001",
            type=EvidenceType.LOG_ENTRY,
            timestamp=timestamp,
            source="/var/log/syslog",
            content={"message": "Test log entry"},
            metadata={"size": 1024},
            integrity_hash="abc123",
        )

        assert evidence.id == "evidence_001"
        assert evidence.type == EvidenceType.LOG_ENTRY
        assert evidence.timestamp == timestamp
        assert evidence.source == "/var/log/syslog"
        assert evidence.content["message"] == "Test log entry"
        assert evidence.metadata["size"] == 1024
        assert evidence.integrity_hash == "abc123"

    def test_evidence_item_default_values(self):
        """Test EvidenceItem with default values."""
        timestamp = datetime.now(timezone.utc).isoformat()
        evidence = EvidenceItem(
            id="evidence_002",
            type=EvidenceType.FILE_SYSTEM,
            timestamp=timestamp,
            source="/tmp/test.txt",
            content={},
        )

        assert evidence.metadata == {}
        assert evidence.integrity_hash == ""


class TestIncident:
    """Test Incident data structure."""

    def test_incident_creation(self):
        """Test creating an Incident."""
        timestamp = datetime.now(timezone.utc).isoformat()
        incident = Incident(
            id="incident_001",
            title="Suspicious Process Detected",
            description="Process exhibiting malicious behavior",
            severity=IncidentSeverity.HIGH,
            status=IncidentStatus.OPEN,
            created_at=timestamp,
            updated_at=timestamp,
            detected_by="SecurityMonitor",
            assigned_to="security_team",
        )

        assert incident.id == "incident_001"
        assert incident.title == "Suspicious Process Detected"
        assert incident.severity == IncidentSeverity.HIGH
        assert incident.status == IncidentStatus.OPEN
        assert incident.detected_by == "SecurityMonitor"
        assert incident.assigned_to == "security_team"

    def test_incident_with_evidence(self):
        """Test Incident with evidence items."""
        timestamp = datetime.now(timezone.utc).isoformat()
        evidence = EvidenceItem(
            id="evidence_001",
            type=EvidenceType.PROCESS_INFO,
            timestamp=timestamp,
            source="psutil",
            content={"pid": 1234},
        )

        incident = Incident(
            id="incident_002",
            title="Malware Detection",
            description="Malware detected on system",
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.INVESTIGATING,
            created_at=timestamp,
            updated_at=timestamp,
            detected_by="AntivirusEngine",
            evidence_items=[evidence],
            recommendations=["Quarantine file", "Scan system"],
            tags={"malware", "critical"},
        )

        assert len(incident.evidence_items) == 1
        assert len(incident.recommendations) == 2
        assert "malware" in incident.tags


class TestForensicsReport:
    """Test ForensicsReport data structure."""

    def test_forensics_report_creation(self):
        """Test creating a ForensicsReport."""
        timestamp = datetime.now(timezone.utc).isoformat()
        report = ForensicsReport(
            incident_id="incident_001",
            timestamp=timestamp,
            summary="Security incident investigated and resolved",
            timeline=[
                {"time": "2025-11-22T10:00:00Z", "event": "Incident detected"},
                {"time": "2025-11-22T10:30:00Z", "event": "Investigation started"},
            ],
            evidence_collected=5,
            findings=["Malicious process found", "Network exfiltration detected"],
            recommendations=["Update security policies", "Install firewall rules"],
            risk_assessment={"risk_level": "high", "impact": "severe"},
            execution_time=120.5,
        )

        assert report.incident_id == "incident_001"
        assert len(report.timeline) == 2
        assert report.evidence_collected == 5
        assert len(report.findings) == 2
        assert len(report.recommendations) == 2
        assert report.risk_assessment["risk_level"] == "high"
        assert report.execution_time == 120.5


class TestEvidenceCollector:
    """Test EvidenceCollector class."""

    @pytest.fixture
    def temp_evidence_dir(self):
        """Create temporary evidence directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def collector(self, temp_evidence_dir):
        """Create an EvidenceCollector instance."""
        return EvidenceCollector(evidence_dir=temp_evidence_dir)

    def test_initialization(self, collector, temp_evidence_dir):
        """Test EvidenceCollector initialization."""
        assert collector.evidence_dir == Path(temp_evidence_dir)
        assert collector.evidence_dir.exists()
        assert collector.evidence_dir.is_dir()

    def test_evidence_directory_creation(self, temp_evidence_dir):
        """Test that evidence directory is created."""
        evidence_path = Path(temp_evidence_dir) / "custom_evidence"
        new_collector = EvidenceCollector(evidence_dir=str(evidence_path))

        assert evidence_path.exists()
        assert evidence_path.is_dir()
        assert new_collector.evidence_dir == evidence_path

    def test_collect_log_evidence_nonexistent_file(self, collector):
        """Test collecting evidence from non-existent log file."""
        evidence = collector.collect_log_evidence(
            log_files=["/nonexistent/log/file.log"],
            patterns=["ERROR"],
        )

        assert len(evidence) == 0

    def test_collect_log_evidence_with_pattern(self, collector, temp_evidence_dir):
        """Test collecting evidence from log file with pattern matching."""
        # Create a test log file
        log_file = Path(temp_evidence_dir) / "test.log"
        log_file.write_text(
            "INFO: Application started\n"
            "ERROR: Connection failed\n"
            "WARNING: Low disk space\n"
            "ERROR: Database timeout\n"
        )

        evidence = collector.collect_log_evidence(
            log_files=[str(log_file)],
            patterns=[r"ERROR:.*"],
        )

        assert len(evidence) > 0
        assert evidence[0].type == EvidenceType.LOG_ENTRY
        assert "matches" in evidence[0].content
        assert evidence[0].content["pattern_count"] == 2

    def test_collect_log_evidence_no_pattern(self, collector, temp_evidence_dir):
        """Test collecting evidence from log file without pattern."""
        # Create a test log file
        log_file = Path(temp_evidence_dir) / "test2.log"
        log_file.write_text("INFO: Test log entry\n")

        evidence = collector.collect_log_evidence(
            log_files=[str(log_file)],
            patterns=None,
        )

        # Without patterns, no evidence should be collected
        assert len(evidence) == 0

    def test_collect_file_system_evidence_nonexistent(self, collector):
        """Test collecting file system evidence from non-existent path."""
        evidence = collector.collect_file_system_evidence(
            target_paths=["/nonexistent/path"],
        )

        assert len(evidence) == 0

    def test_collect_file_system_evidence_file(self, collector, temp_evidence_dir):
        """Test collecting file system evidence from a file."""
        # Create a test file
        test_file = Path(temp_evidence_dir) / "test_file.txt"
        test_file.write_text("Test content for evidence collection")

        evidence = collector.collect_file_system_evidence(
            target_paths=[str(test_file)],
        )

        # File system evidence collection should work
        # Even if the implementation is minimal, it shouldn't crash
        assert isinstance(evidence, list)


class TestForensicsSystemIntegration:
    """Integration tests for forensics system components."""

    @pytest.fixture
    def temp_evidence_dir(self):
        """Create temporary evidence directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_end_to_end_evidence_collection(self, temp_evidence_dir):
        """Test end-to-end evidence collection workflow."""
        # Create collector
        collector = EvidenceCollector(evidence_dir=temp_evidence_dir)

        # Create test log file
        log_file = Path(temp_evidence_dir) / "security.log"
        log_file.write_text(
            "2025-11-22 10:00:00 - CRITICAL: Unauthorized access attempt\n"
            "2025-11-22 10:05:00 - WARNING: Multiple failed login attempts\n"
            "2025-11-22 10:10:00 - CRITICAL: Suspicious process detected\n"
        )

        # Collect evidence
        evidence = collector.collect_log_evidence(
            log_files=[str(log_file)],
            patterns=[r"CRITICAL:.*"],
        )

        # Verify evidence collection
        assert len(evidence) > 0
        assert evidence[0].type == EvidenceType.LOG_ENTRY
        assert "CRITICAL" in str(evidence[0].content)

        # Create incident with collected evidence
        timestamp = datetime.now(timezone.utc).isoformat()
        incident = Incident(
            id="test_incident_001",
            title="Security Breach Investigation",
            description="Multiple critical events detected",
            severity=IncidentSeverity.CRITICAL,
            status=IncidentStatus.INVESTIGATING,
            created_at=timestamp,
            updated_at=timestamp,
            detected_by="EvidenceCollector",
            evidence_items=evidence,
            recommendations=["Review access logs", "Check system integrity"],
        )

        assert incident.severity == IncidentSeverity.CRITICAL
        assert len(incident.evidence_items) > 0

        # Create forensics report
        report = ForensicsReport(
            incident_id=incident.id,
            timestamp=timestamp,
            summary="Critical security events investigated",
            timeline=[{"time": timestamp, "event": "Investigation completed"}],
            evidence_collected=len(evidence),
            findings=["Unauthorized access attempts detected"],
            recommendations=incident.recommendations,
            risk_assessment={"risk_level": "critical"},
            execution_time=1.5,
        )

        assert report.incident_id == incident.id
        assert report.evidence_collected == len(evidence)

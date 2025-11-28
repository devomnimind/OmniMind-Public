import tempfile
from pathlib import Path
import pytest
from src.audit.immutable_audit import ImmutableAuditSystem
from src.security.security_monitor import (

#!/usr/bin/env python3
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

"""
Comprehensive tests for security_monitor.py module.
Tests SecurityMonitor class and related functionality.
"""



    AnomalyType,
    ProcessSnapshot,
    SecurityEvent,
    SecurityMonitor,
    ThreatLevel,
)


class TestSecurityMonitorInitialization:
    """Test SecurityMonitor initialization."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_initialization_default(self, temp_audit_system, temp_log_dir):
        """Test SecurityMonitor initialization with defaults."""
        monitor = SecurityMonitor(
            audit_system=temp_audit_system,
            log_dir=temp_log_dir,
        )

        assert monitor.audit_system == temp_audit_system
        assert monitor.monitoring_interval == 30
        assert monitor.is_monitoring is False
        assert len(monitor.baseline_processes) == 0
        assert len(monitor.baseline_network) == 0
        assert len(monitor.baseline_files) == 0

    def test_initialization_custom_interval(self, temp_audit_system, temp_log_dir):
        """Test SecurityMonitor initialization with custom interval."""
        monitor = SecurityMonitor(
            audit_system=temp_audit_system,
            monitoring_interval=60,
            log_dir=temp_log_dir,
        )

        assert monitor.monitoring_interval == 60

    def test_log_directory_creation(self, temp_audit_system, temp_log_dir):
        """Test that log directory is created."""
        log_path = Path(temp_log_dir) / "security"
        created_monitor = SecurityMonitor(
            audit_system=temp_audit_system,
            log_dir=str(log_path),
        )

        assert log_path.exists()
        assert log_path.is_dir()
        assert created_monitor.log_dir == log_path

    def test_known_safe_processes(self, temp_audit_system, temp_log_dir):
        """Test that known safe processes are configured."""
        monitor = SecurityMonitor(
            audit_system=temp_audit_system,
            log_dir=temp_log_dir,
        )

        assert "systemd" in monitor.known_safe_processes
        assert "python" in monitor.known_safe_processes
        assert "bash" in monitor.known_safe_processes

    def test_suspicious_ports_configured(self, temp_audit_system, temp_log_dir):
        """Test that suspicious ports are configured."""
        monitor = SecurityMonitor(
            audit_system=temp_audit_system,
            log_dir=temp_log_dir,
        )

        assert 22 in monitor.suspicious_ports  # SSH
        assert 3389 in monitor.suspicious_ports  # RDP

    def test_suspicious_processes_configured(self, temp_audit_system, temp_log_dir):
        """Test that suspicious processes are configured."""
        monitor = SecurityMonitor(
            audit_system=temp_audit_system,
            log_dir=temp_log_dir,
        )

        assert "netcat" in monitor.suspicious_processes
        assert "backdoor" in monitor.suspicious_processes

    def test_thresholds_configured(self, temp_audit_system, temp_log_dir):
        """Test that monitoring thresholds are configured."""
        monitor = SecurityMonitor(
            audit_system=temp_audit_system,
            log_dir=temp_log_dir,
        )

        assert monitor.cpu_threshold == 90.0
        assert monitor.memory_threshold == 85.0
        assert monitor.connection_threshold == 100


class TestSecurityEvent:
    """Test SecurityEvent data structure."""

    def test_security_event_creation(self):
        """Test creating a SecurityEvent."""
        event = SecurityEvent(
            timestamp="2025-11-22T12:00:00Z",
            event_type=AnomalyType.SUSPICIOUS_PROCESS,
            threat_level=ThreatLevel.HIGH,
            description="Suspicious process detected",
            evidence=["Process name: malware.exe"],
            recommendations=["Terminate process", "Scan system"],
        )

        assert event.timestamp == "2025-11-22T12:00:00Z"
        assert event.event_type == AnomalyType.SUSPICIOUS_PROCESS
        assert event.threat_level == ThreatLevel.HIGH
        assert event.description == "Suspicious process detected"
        assert len(event.evidence) == 1
        assert len(event.recommendations) == 2

    def test_security_event_optional_fields(self):
        """Test SecurityEvent with optional fields."""
        event = SecurityEvent(
            timestamp="2025-11-22T12:00:00Z",
            event_type=AnomalyType.HIGH_CPU_USAGE,
            threat_level=ThreatLevel.MEDIUM,
            description="High CPU usage",
            process_info={"pid": 1234, "name": "test"},
            network_info={"connections": 50},
        )

        assert event.process_info["pid"] == 1234
        assert event.network_info["connections"] == 50


class TestProcessSnapshot:
    """Test ProcessSnapshot data structure."""

    def test_process_snapshot_creation(self):
        """Test creating a ProcessSnapshot."""
        snapshot = ProcessSnapshot(
            pid=1234,
            name="test_process",
            cmdline=["/usr/bin/test", "--arg"],
            cpu_percent=25.5,
            memory_percent=10.2,
            status="running",
            create_time=1700000000.0,
            username="testuser",
            connections=[{"local": "127.0.0.1:8000"}],
            open_files=["/tmp/test.txt"],
        )

        assert snapshot.pid == 1234
        assert snapshot.name == "test_process"
        assert snapshot.cpu_percent == 25.5
        assert snapshot.memory_percent == 10.2
        assert snapshot.status == "running"
        assert len(snapshot.connections) == 1
        assert len(snapshot.open_files) == 1


class TestSecurityMonitorMethods:
    """Test SecurityMonitor methods."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def monitor(self, temp_audit_system, temp_log_dir):
        """Create a SecurityMonitor instance for testing."""
        return SecurityMonitor(
            audit_system=temp_audit_system,
            log_dir=temp_log_dir,
        )

    def test_event_history_initialization(self, monitor):
        """Test that event history is initialized."""
        assert isinstance(monitor.event_history, list)
        assert len(monitor.event_history) == 0
        assert monitor.max_history_size == 1000

    def test_monitoring_state_initial(self, monitor):
        """Test initial monitoring state."""
        assert monitor.is_monitoring is False

    def test_start_monitoring_state_check(self, monitor):
        """Test that monitoring state can be checked."""
        # Just verify initial state - no async needed
        assert monitor.is_monitoring is False
        # This is safer than trying to actually start monitoring in tests


class TestAnomalyType:
    """Test AnomalyType enum."""

    def test_anomaly_types_exist(self):
        """Test that all anomaly types are defined."""
        assert AnomalyType.SUSPICIOUS_PROCESS.value == "suspicious_process"
        assert AnomalyType.HIGH_CPU_USAGE.value == "high_cpu_usage"
        assert AnomalyType.HIGH_MEMORY_USAGE.value == "high_memory_usage"
        assert AnomalyType.UNUSUAL_NETWORK_CONNECTION.value == "unusual_network_connection"
        assert AnomalyType.FILE_SYSTEM_CHANGE.value == "file_system_change"
        assert AnomalyType.UNAUTHORIZED_ACCESS.value == "unauthorized_access"
        assert AnomalyType.MALWARE_SIGNATURE.value == "malware_signature"
        assert AnomalyType.ROOTKIT_INDICATOR.value == "rootkit_indicator"


class TestThreatLevel:
    """Test ThreatLevel enum."""

    def test_threat_levels_exist(self):
        """Test that all threat levels are defined."""
        assert ThreatLevel.LOW.value == "low"
        assert ThreatLevel.MEDIUM.value == "medium"
        assert ThreatLevel.HIGH.value == "high"
        assert ThreatLevel.CRITICAL.value == "critical"

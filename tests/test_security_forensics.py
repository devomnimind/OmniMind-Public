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
Tests for security forensics modules.
Tests network sensors, web scanners, and security orchestrator.
"""

import tempfile

import pytest

from src.audit.immutable_audit import ImmutableAuditSystem
from src.security.network_sensors import (
    NetworkAnomaly,
    NetworkHost,
    NetworkSensorGanglia,
    ThreatSeverity,
)
from src.security.security_orchestrator import (
    SecurityOrchestrator,
    SecurityStatus,
)
from src.security.web_scanner import (
    VulnerabilitySeverity,
    VulnerabilityType,
    WebScannerBrain,
    WebVulnerability,
)


class TestNetworkSensors:
    """Test network sensors functionality."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    def test_network_sensors_initialization(self, temp_audit_system):
        """Test network sensors initialization."""
        sensors = NetworkSensorGanglia(temp_audit_system)
        assert sensors.audit_system == temp_audit_system
        assert isinstance(sensors.known_hosts, dict)
        assert isinstance(sensors.baseline_ports, dict)

    def test_network_host_creation(self):
        """Test network host data structure."""
        host = NetworkHost(
            ip="192.168.1.1",
            hostname="gateway",
            open_ports=[22, 80, 443],
            services=["ssh", "http", "https"],
        )

        assert host.ip == "192.168.1.1"
        assert host.hostname == "gateway"
        assert len(host.open_ports) == 3
        assert 22 in host.open_ports

    def test_network_anomaly_creation(self):
        """Test network anomaly data structure."""
        anomaly = NetworkAnomaly(
            type="new_host_detected",
            severity=ThreatSeverity.LOW,
            description="New host on network",
            source_ip="192.168.1.100",
        )

        assert anomaly.type == "new_host_detected"
        assert anomaly.severity == ThreatSeverity.LOW
        assert anomaly.source_ip == "192.168.1.100"

    def test_scan_localhost(self, temp_audit_system):
        """Test scanning localhost."""
        sensors = NetworkSensorGanglia(temp_audit_system)

        # Scan localhost (may not have nmap installed)
        result = sensors.scan_network("127.0.0.1", scan_type="basic")

        # Should return either scan results or error message
        assert "hosts" in result
        # If nmap is not available, should have error
        if not sensors.nmap_available:
            assert "error" in result
        else:
            assert "target" in result

    def test_establish_baseline(self, temp_audit_system):
        """Test establishing network baseline."""
        sensors = NetworkSensorGanglia(temp_audit_system)

        # Establish baseline
        success = sensors.establish_baseline("127.0.0.1")

        # Should succeed or fail gracefully
        assert isinstance(success, bool)

    def test_network_health_calculation(self, temp_audit_system):
        """Test network health score calculation."""
        sensors = NetworkSensorGanglia(temp_audit_system)

        # Add some test hosts
        sensors.known_hosts["192.168.1.1"] = NetworkHost(
            ip="192.168.1.1",
            open_ports=[22, 80, 443],
        )

        health = sensors.get_network_health()

        assert "health_score" in health
        assert 0 <= health["health_score"] <= 100
        assert "total_hosts" in health
        assert health["total_hosts"] == 1

    def test_anomaly_detection_new_host(self, temp_audit_system):
        """Test detection of new hosts."""
        sensors = NetworkSensorGanglia(temp_audit_system)

        # Add a new host
        sensors.known_hosts["192.168.1.100"] = NetworkHost(
            ip="192.168.1.100",
            open_ports=[22],
        )

        # Detect anomalies
        anomalies = sensors.detect_anomalies()

        # Should detect new host
        assert len(anomalies) >= 1
        assert any(a.type == "new_host_detected" for a in anomalies)

    def test_anomaly_detection_suspicious_ports(self, temp_audit_system):
        """Test detection of suspicious ports."""
        sensors = NetworkSensorGanglia(temp_audit_system)

        # Establish baseline
        sensors.known_hosts["192.168.1.1"] = NetworkHost(
            ip="192.168.1.1",
            open_ports=[22, 80],
        )
        sensors.baseline_ports["192.168.1.1"] = [22, 80]

        # Add suspicious port
        sensors.known_hosts["192.168.1.1"].open_ports.append(4444)

        # Detect anomalies
        anomalies = sensors.detect_anomalies()

        # Should detect suspicious port
        suspicious_anomalies = [a for a in anomalies if a.type == "new_ports_opened"]
        assert len(suspicious_anomalies) > 0


class TestWebScanner:
    """Test web scanner functionality."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    def test_web_scanner_initialization(self, temp_audit_system):
        """Test web scanner initialization."""
        scanner = WebScannerBrain(temp_audit_system)
        assert scanner.audit_system == temp_audit_system

    def test_web_vulnerability_creation(self):
        """Test web vulnerability data structure."""
        vuln = WebVulnerability(
            url="https://example.com",
            vulnerability_type=VulnerabilityType.XSS,
            severity=VulnerabilitySeverity.HIGH,
            description="XSS vulnerability detected",
            evidence="<script>alert(1)</script>",
        )

        assert vuln.url == "https://example.com"
        assert vuln.vulnerability_type == VulnerabilityType.XSS
        assert vuln.severity == VulnerabilitySeverity.HIGH

    def test_url_validation(self, temp_audit_system):
        """Test URL validation."""
        scanner = WebScannerBrain(temp_audit_system)

        # Valid URLs
        assert scanner._is_valid_url("https://example.com")
        assert scanner._is_valid_url("http://localhost:8000")

        # Invalid URLs
        assert not scanner._is_valid_url("not-a-url")
        assert not scanner._is_valid_url("")

    def test_scan_url_invalid(self, temp_audit_system):
        """Test scanning invalid URL."""
        scanner = WebScannerBrain(temp_audit_system)

        result = scanner.scan_url("invalid-url")

        assert "error" in result
        assert result["error"] == "Invalid URL"

    def test_check_security_headers_localhost(self, temp_audit_system):
        """Test checking security headers on localhost."""
        scanner = WebScannerBrain(temp_audit_system)

        # This will fail to connect, but should handle gracefully
        findings = scanner._check_security_headers("http://localhost:9999")

        # Should have findings about connection failure
        assert isinstance(findings, list)

    def test_vulnerability_to_dict(self, temp_audit_system):
        """Test converting vulnerability to dictionary."""
        scanner = WebScannerBrain(temp_audit_system)

        vuln = WebVulnerability(
            url="https://example.com",
            vulnerability_type=VulnerabilityType.MISSING_SECURITY_HEADERS,
            severity=VulnerabilitySeverity.MEDIUM,
            description="Missing X-Frame-Options header",
        )

        vuln_dict = scanner._vulnerability_to_dict(vuln)

        assert vuln_dict["url"] == "https://example.com"
        assert vuln_dict["type"] == "missing_security_headers"
        assert vuln_dict["severity"] == "MEDIUM"

    def test_generate_summary(self, temp_audit_system):
        """Test generating vulnerability summary."""
        scanner = WebScannerBrain(temp_audit_system)

        findings = [
            WebVulnerability(
                url="https://example.com",
                vulnerability_type=VulnerabilityType.XSS,
                severity=VulnerabilitySeverity.CRITICAL,
                description="XSS",
            ),
            WebVulnerability(
                url="https://example.com",
                vulnerability_type=VulnerabilityType.MISCONFIGURATION,
                severity=VulnerabilitySeverity.LOW,
                description="Config issue",
            ),
        ]

        summary = scanner._generate_summary(findings)

        assert summary["total_findings"] == 2
        assert summary["by_severity"]["critical"] == 1
        assert summary["by_severity"]["low"] == 1
        assert summary["risk_level"] == "CRITICAL"


class TestSecurityOrchestrator:
    """Test security orchestrator functionality."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    def test_orchestrator_initialization(self, temp_audit_system):
        """Test orchestrator initialization."""
        orchestrator = SecurityOrchestrator(temp_audit_system)

        assert orchestrator.audit_system == temp_audit_system
        assert orchestrator.network_sensors is not None
        assert orchestrator.web_scanner is not None
        # SecurityAgent may be None if config not available
        # (Import here to avoid unused import warning)
        from src.security.security_agent import SecurityAgent

        assert orchestrator.security_agent is None or isinstance(
            orchestrator.security_agent, SecurityAgent
        )

    def test_calculate_risk_score_low(self, temp_audit_system):
        """Test risk score calculation with low risk."""
        orchestrator = SecurityOrchestrator(temp_audit_system)

        network_health = {"health_score": 95}
        risk_score = orchestrator._calculate_risk_score(network_health, [], [], [])

        assert 0 <= risk_score <= 20

    def test_calculate_risk_score_high(self, temp_audit_system):
        """Test risk score calculation with high risk."""
        orchestrator = SecurityOrchestrator(temp_audit_system)

        network_health = {"health_score": 50}
        network_anomalies = [1, 2, 3]  # 3 anomalies
        web_vulnerabilities = [
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
        ]
        security_events = [1]

        risk_score = orchestrator._calculate_risk_score(
            network_health,
            network_anomalies,
            web_vulnerabilities,
            security_events,
        )

        assert risk_score >= 50  # Should be 50 or higher

    def test_determine_status(self, temp_audit_system):
        """Test security status determination."""
        orchestrator = SecurityOrchestrator(temp_audit_system)

        assert orchestrator._determine_status(10) == SecurityStatus.SECURE
        assert orchestrator._determine_status(30) == SecurityStatus.WARNING
        assert orchestrator._determine_status(60) == SecurityStatus.COMPROMISED
        assert orchestrator._determine_status(90) == SecurityStatus.CRITICAL

    def test_generate_recommendations(self, temp_audit_system):
        """Test recommendation generation."""
        orchestrator = SecurityOrchestrator(temp_audit_system)

        # No issues
        recommendations = orchestrator._generate_recommendations([], [], [])
        assert len(recommendations) > 0
        assert any("good" in r.lower() for r in recommendations)

        # With issues
        network_anomalies = [1, 2]
        web_vulns = [{"severity": "CRITICAL"}]
        recommendations = orchestrator._generate_recommendations(network_anomalies, web_vulns, [])

        assert any("anomalies" in r.lower() for r in recommendations)
        assert any("critical" in r.lower() for r in recommendations)

    def test_run_full_security_audit(self, temp_audit_system):
        """Test running full security audit."""
        orchestrator = SecurityOrchestrator(temp_audit_system)

        # Run audit (localhost only, should be safe)
        report = orchestrator.run_full_security_audit(
            network_targets=["127.0.0.1"],
            web_targets=[],
        )

        assert report.timestamp is not None
        assert report.status in SecurityStatus
        assert isinstance(report.risk_score, float)
        assert 0 <= report.risk_score <= 100
        assert isinstance(report.recommendations, list)
        assert len(report.recommendations) > 0


class TestIntegration:
    """Integration tests for security forensics."""

    @pytest.fixture
    def temp_audit_system(self):
        """Create temporary audit system for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = ImmutableAuditSystem(log_dir=tmpdir)
            yield audit

    def test_full_security_workflow(self, temp_audit_system):
        """Test complete security monitoring workflow."""
        # Create orchestrator
        orchestrator = SecurityOrchestrator(temp_audit_system)

        # Run security audit
        report = orchestrator.run_full_security_audit(
            network_targets=["127.0.0.1"],
        )

        # Verify report structure
        assert report.timestamp is not None
        assert report.status in SecurityStatus
        assert report.network_health is not None
        assert isinstance(report.network_anomalies, list)
        assert isinstance(report.recommendations, list)

        # Verify audit log was created
        summary = temp_audit_system.get_audit_summary()
        assert summary["total_events"] > 0

    def test_network_and_web_integration(self, temp_audit_system):
        """Test integration of network and web scanning."""
        orchestrator = SecurityOrchestrator(temp_audit_system)

        # Scan network
        network_result = orchestrator.network_sensors.scan_network("127.0.0.1")
        assert "hosts" in network_result

        # Note: Web scanning would require actual web server
        # Test only initialization
        assert orchestrator.web_scanner is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

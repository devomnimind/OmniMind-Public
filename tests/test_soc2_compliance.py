from __future__ import annotations

from pathlib import Path
import pytest
from src.security.soc2_compliance import (


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
Tests for SOC 2 Compliance Manager.
"""




    ControlStatus,
    PentestResult,
    RiskLevel,
    SOC2ComplianceManager,
    VulnerabilityFinding,
)


@pytest.fixture
def temp_compliance_dir(tmp_path: Path) -> Path:
    """Create temporary compliance directory."""
    compliance_dir = tmp_path / "compliance"
    compliance_dir.mkdir()
    return compliance_dir


@pytest.fixture
def compliance_manager(temp_compliance_dir: Path) -> SOC2ComplianceManager:
    """Create compliance manager instance."""
    return SOC2ComplianceManager(compliance_dir=temp_compliance_dir)


def test_compliance_manager_initialization(
    compliance_manager: SOC2ComplianceManager, temp_compliance_dir: Path
) -> None:
    """Test compliance manager initializes correctly."""
    assert compliance_manager.compliance_dir == temp_compliance_dir
    assert temp_compliance_dir.exists()
    assert len(compliance_manager.controls) > 0


def test_default_controls_loaded(compliance_manager: SOC2ComplianceManager) -> None:
    """Test default SOC 2 controls are loaded."""
    # Check security controls
    assert "CC1.1" in compliance_manager.controls
    assert "CC2.1" in compliance_manager.controls

    # Check availability controls
    assert "A1.1" in compliance_manager.controls

    # Check processing integrity controls
    assert "PI1.1" in compliance_manager.controls

    # Check confidentiality controls
    assert "C1.1" in compliance_manager.controls

    # Check privacy controls
    assert "P1.1" in compliance_manager.controls


def test_add_vulnerability(compliance_manager: SOC2ComplianceManager) -> None:
    """Test adding vulnerability findings."""
    vuln = VulnerabilityFinding(
        finding_id="TEST-001",
        title="Test Vulnerability",
        description="Test description",
        severity=RiskLevel.HIGH,
        affected_component="Test Component",
        remediation="Test remediation",
    )

    compliance_manager.add_vulnerability(vuln)

    assert "TEST-001" in compliance_manager.vulnerabilities
    assert compliance_manager.vulnerabilities["TEST-001"].title == "Test Vulnerability"


def test_add_pentest_result(compliance_manager: SOC2ComplianceManager) -> None:
    """Test adding penetration test results."""
    findings = [
        VulnerabilityFinding(
            finding_id="PENTEST-001",
            title="SQL Injection",
            description="SQL injection vulnerability found",
            severity=RiskLevel.CRITICAL,
            affected_component="Database",
            remediation="Use parameterized queries",
        )
    ]

    pentest = PentestResult(
        test_id="PENTEST-2023-11",
        test_date="2023-11-19T12:00:00Z",
        tester="Security Team",
        scope="Full application",
        methodology="OWASP Top 10",
        findings=findings,
    )

    compliance_manager.add_pentest_result(pentest)

    assert "PENTEST-2023-11" in compliance_manager.pentest_results
    assert "PENTEST-001" in compliance_manager.vulnerabilities


def test_update_control_status(compliance_manager: SOC2ComplianceManager) -> None:
    """Test updating control status."""
    compliance_manager.update_control_status(
        control_id="CC1.1",
        status=ControlStatus.IMPLEMENTED,
        evidence=["Documentation updated", "Policy enforced"],
        test_results="All tests passed",
    )

    control = compliance_manager.controls["CC1.1"]
    assert control.status == ControlStatus.IMPLEMENTED
    assert len(control.evidence) > 0
    assert control.test_results == "All tests passed"
    assert control.last_tested is not None


def test_generate_compliance_report(compliance_manager: SOC2ComplianceManager) -> None:
    """Test compliance report generation."""
    # Add some test data
    vuln = VulnerabilityFinding(
        finding_id="TEST-001",
        title="Test Vuln",
        description="Test",
        severity=RiskLevel.MEDIUM,
        affected_component="Test",
        remediation="Fix it",
    )
    compliance_manager.add_vulnerability(vuln)

    report = compliance_manager.generate_compliance_report()

    assert "report_date" in report
    assert "controls_summary" in report
    assert "vulnerabilities_summary" in report
    assert "compliance_score" in report
    assert report["compliance_score"] > 0


def test_compliance_score_calculation(
    compliance_manager: SOC2ComplianceManager,
) -> None:
    """Test compliance score calculation."""
    # Initial score
    initial_score = compliance_manager._calculate_compliance_score()
    assert 0 <= initial_score <= 100

    # Update some controls
    compliance_manager.update_control_status("CC3.1", ControlStatus.IMPLEMENTED)
    compliance_manager.update_control_status("CC8.1", ControlStatus.IMPLEMENTED)

    # Score should increase
    new_score = compliance_manager._calculate_compliance_score()
    assert new_score > initial_score


def test_run_automated_security_scan(
    compliance_manager: SOC2ComplianceManager,
) -> None:
    """Test automated security scanning."""
    results = compliance_manager.run_automated_security_scan()

    assert "scan_date" in results
    assert "findings_count" in results
    assert "findings" in results


def test_vulnerability_finding_to_dict() -> None:
    """Test vulnerability finding serialization."""
    vuln = VulnerabilityFinding(
        finding_id="TEST-001",
        title="Test",
        description="Test description",
        severity=RiskLevel.HIGH,
        affected_component="Component",
        remediation="Fix it",
    )

    vuln_dict = vuln.to_dict()

    assert vuln_dict["finding_id"] == "TEST-001"
    assert vuln_dict["severity"] == "high"
    assert "discovered_date" in vuln_dict


def test_pentest_result_risk_summary() -> None:
    """Test pentest result risk summary."""
    findings = [
        VulnerabilityFinding(
            finding_id="F1",
            title="Critical Issue",
            description="Test",
            severity=RiskLevel.CRITICAL,
            affected_component="Test",
            remediation="Fix",
        ),
        VulnerabilityFinding(
            finding_id="F2",
            title="High Issue",
            description="Test",
            severity=RiskLevel.HIGH,
            affected_component="Test",
            remediation="Fix",
        ),
        VulnerabilityFinding(
            finding_id="F3",
            title="Medium Issue",
            description="Test",
            severity=RiskLevel.MEDIUM,
            affected_component="Test",
            remediation="Fix",
        ),
    ]

    pentest = PentestResult(
        test_id="TEST",
        test_date="2023-11-19T12:00:00Z",
        tester="Tester",
        scope="Test",
        methodology="Test",
        findings=findings,
    )

    summary = pentest._calculate_risk_summary()

    assert summary["critical"] == 1
    assert summary["high"] == 1
    assert summary["medium"] == 1
    assert summary["low"] == 0


def test_controls_summary(compliance_manager: SOC2ComplianceManager) -> None:
    """Test controls summary generation."""
    summary = compliance_manager._get_controls_summary()

    assert "implemented" in summary
    assert "partial" in summary
    assert "not_implemented" in summary
    assert "not_applicable" in summary
    assert sum(summary.values()) == len(compliance_manager.controls)


def test_vulnerabilities_summary(compliance_manager: SOC2ComplianceManager) -> None:
    """Test vulnerabilities summary generation."""
    # Add test vulnerabilities
    compliance_manager.add_vulnerability(
        VulnerabilityFinding(
            finding_id="V1",
            title="Critical",
            description="Test",
            severity=RiskLevel.CRITICAL,
            affected_component="Test",
            remediation="Fix",
            status="open",
        )
    )
    compliance_manager.add_vulnerability(
        VulnerabilityFinding(
            finding_id="V2",
            title="High",
            description="Test",
            severity=RiskLevel.HIGH,
            affected_component="Test",
            remediation="Fix",
            status="resolved",
        )
    )

    summary = compliance_manager._get_vulnerabilities_summary()

    assert summary["total"] == 2
    assert summary["by_severity"]["critical"] == 1
    assert summary["by_severity"]["high"] == 1
    assert summary["by_status"]["open"] == 1
    assert summary["by_status"]["resolved"] == 1

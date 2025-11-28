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
SOC 2 Type II Compliance Framework for OmniMind.

This module implements security controls and documentation required for SOC 2 Type II certification:
- Trust Services Criteria (TSC) implementation
- Automated security scanning and reporting
- Penetration testing framework
- Audit trail management
- Compliance reporting automation
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TrustServicesCriteria(str, Enum):
    """SOC 2 Trust Services Criteria."""

    SECURITY = "security"  # CC1-CC9
    AVAILABILITY = "availability"  # A1
    PROCESSING_INTEGRITY = "processing_integrity"  # PI1
    CONFIDENTIALITY = "confidentiality"  # C1
    PRIVACY = "privacy"  # P1-P8


class ControlStatus(str, Enum):
    """Control implementation status."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


class RiskLevel(str, Enum):
    """Risk assessment levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


@dataclass
class SecurityControl:
    """Security control for SOC 2 compliance."""

    control_id: str
    criteria: TrustServicesCriteria
    title: str
    description: str
    status: ControlStatus = ControlStatus.NOT_IMPLEMENTED
    evidence: List[str] = field(default_factory=list)
    responsible_party: str = ""
    implementation_date: Optional[str] = None
    last_tested: Optional[str] = None
    test_results: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["criteria"] = self.criteria.value
        data["status"] = self.status.value
        return data


@dataclass
class VulnerabilityFinding:
    """Security vulnerability finding."""

    finding_id: str
    title: str
    description: str
    severity: RiskLevel
    affected_component: str
    remediation: str
    discovered_date: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "open"  # open, in_progress, resolved, accepted
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class PentestResult:
    """Penetration testing result."""

    test_id: str
    test_date: str
    tester: str
    scope: str
    methodology: str
    findings: List[VulnerabilityFinding] = field(default_factory=list)
    summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_id": self.test_id,
            "test_date": self.test_date,
            "tester": self.tester,
            "scope": self.scope,
            "methodology": self.methodology,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "metadata": self.metadata,
            "risk_summary": self._calculate_risk_summary(),
        }

    def _calculate_risk_summary(self) -> Dict[str, int]:
        """Calculate risk summary statistics."""
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "informational": 0,
        }
        for finding in self.findings:
            summary[finding.severity.value] += 1
        return summary


class SOC2ComplianceManager:
    """Manages SOC 2 Type II compliance controls and reporting."""

    def __init__(self, compliance_dir: Path = Path(".omnimind/compliance")):
        """
        Initialize SOC 2 compliance manager.

        Args:
            compliance_dir: Directory to store compliance data
        """
        self.compliance_dir = compliance_dir
        self.compliance_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

        self.controls: Dict[str, SecurityControl] = {}
        self.vulnerabilities: Dict[str, VulnerabilityFinding] = {}
        self.pentest_results: Dict[str, PentestResult] = {}

        self._initialize_soc2_controls()
        logger.info(f"SOC 2 Compliance Manager initialized: {self.compliance_dir}")

    def _initialize_soc2_controls(self) -> None:
        """Initialize SOC 2 security controls."""
        # Security Controls (CC1-CC9)
        security_controls = [
            SecurityControl(
                control_id="CC1.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Organization and Management",
                description=(
                    "Establish organizational structure with " "defined roles and responsibilities"
                ),
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC2.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Communication and Information",
                description="Information security policies communicated to all stakeholders",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC3.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Risk Assessment",
                description="Identify and assess security risks regularly",
                status=ControlStatus.PARTIAL,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC4.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Monitoring Activities",
                description="Monitor security controls and detect anomalies",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC5.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Control Activities - Logical Access",
                description="Restrict logical access to authorized users",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC6.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Logical and Physical Access Controls",
                description="Implement authentication and authorization mechanisms",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC7.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="System Operations",
                description="Detect and respond to security incidents",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC8.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Change Management",
                description="Authorize and document system changes",
                status=ControlStatus.PARTIAL,
                responsible_party="Development Team",
            ),
            SecurityControl(
                control_id="CC9.1",
                criteria=TrustServicesCriteria.SECURITY,
                title="Risk Mitigation",
                description="Implement controls to mitigate identified risks",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
        ]

        # Availability Controls
        availability_controls = [
            SecurityControl(
                control_id="A1.1",
                criteria=TrustServicesCriteria.AVAILABILITY,
                title="System Availability",
                description="Ensure system availability meets committed SLA",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Operations Team",
            ),
            SecurityControl(
                control_id="A1.2",
                criteria=TrustServicesCriteria.AVAILABILITY,
                title="Backup and Recovery",
                description="Implement backup and disaster recovery procedures",
                status=ControlStatus.PARTIAL,
                responsible_party="Operations Team",
            ),
        ]

        # Processing Integrity Controls
        processing_controls = [
            SecurityControl(
                control_id="PI1.1",
                criteria=TrustServicesCriteria.PROCESSING_INTEGRITY,
                title="Data Processing Accuracy",
                description="Ensure accurate and complete data processing",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Development Team",
            ),
        ]

        # Confidentiality Controls
        confidentiality_controls = [
            SecurityControl(
                control_id="C1.1",
                criteria=TrustServicesCriteria.CONFIDENTIALITY,
                title="Data Encryption",
                description="Encrypt confidential data at rest and in transit",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Security Team",
            ),
        ]

        # Privacy Controls
        privacy_controls = [
            SecurityControl(
                control_id="P1.1",
                criteria=TrustServicesCriteria.PRIVACY,
                title="Privacy Notice",
                description="Provide notice about data collection and use",
                status=ControlStatus.IMPLEMENTED,
                responsible_party="Legal Team",
            ),
        ]

        # Combine all controls
        all_controls = (
            security_controls
            + availability_controls
            + processing_controls
            + confidentiality_controls
            + privacy_controls
        )

        for control in all_controls:
            self.controls[control.control_id] = control

    def add_vulnerability(self, vulnerability: VulnerabilityFinding) -> None:
        """
        Add a vulnerability finding.

        Args:
            vulnerability: Vulnerability finding to add
        """
        self.vulnerabilities[vulnerability.finding_id] = vulnerability
        logger.info(f"Vulnerability added: {vulnerability.finding_id}")

        # Auto-save to file
        self._save_vulnerabilities()

    def add_pentest_result(self, pentest: PentestResult) -> None:
        """
        Add penetration test results.

        Args:
            pentest: Penetration test results to add
        """
        self.pentest_results[pentest.test_id] = pentest
        logger.info(f"Pentest result added: {pentest.test_id}")

        # Add all findings as vulnerabilities
        for finding in pentest.findings:
            self.add_vulnerability(finding)

        # Auto-save to file
        self._save_pentest_results()

    def update_control_status(
        self,
        control_id: str,
        status: ControlStatus,
        evidence: Optional[List[str]] = None,
        test_results: Optional[str] = None,
    ) -> None:
        """
        Update security control status.

        Args:
            control_id: Control identifier
            status: New control status
            evidence: Evidence of implementation
            test_results: Testing results
        """
        if control_id not in self.controls:
            raise ValueError(f"Control not found: {control_id}")

        control = self.controls[control_id]
        control.status = status
        control.last_tested = datetime.now(timezone.utc).isoformat()

        if evidence:
            control.evidence.extend(evidence)

        if test_results:
            control.test_results = test_results

        logger.info(f"Control {control_id} updated to status: {status.value}")

        # Auto-save
        self._save_controls()

    def generate_compliance_report(self) -> Dict[str, Any]:
        """
        Generate SOC 2 compliance report.

        Returns:
            Compliance report with control status and findings
        """
        report = {
            "report_date": datetime.now(timezone.utc).isoformat(),
            "controls_summary": self._get_controls_summary(),
            "controls": [c.to_dict() for c in self.controls.values()],
            "vulnerabilities_summary": self._get_vulnerabilities_summary(),
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities.values()],
            "pentest_summary": self._get_pentest_summary(),
            "compliance_score": self._calculate_compliance_score(),
        }

        # Save report to file
        report_path = (
            self.compliance_dir / f"soc2_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with report_path.open("w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Compliance report generated: {report_path}")
        return report

    def _get_controls_summary(self) -> Dict[str, int]:
        """Get summary of control statuses."""
        summary = {
            "implemented": 0,
            "partial": 0,
            "not_implemented": 0,
            "not_applicable": 0,
        }
        for control in self.controls.values():
            summary[control.status.value] += 1
        return summary

    def _get_vulnerabilities_summary(self) -> Dict[str, Any]:
        """Get summary of vulnerabilities."""
        summary: Dict[str, Any] = {
            "total": len(self.vulnerabilities),
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "informational": 0,
            },
            "by_status": {"open": 0, "in_progress": 0, "resolved": 0, "accepted": 0},
        }

        for vuln in self.vulnerabilities.values():
            summary["by_severity"][vuln.severity.value] += 1
            summary["by_status"][vuln.status] += 1

        return summary

    def _get_pentest_summary(self) -> Dict[str, Any]:
        """Get summary of penetration tests."""
        return {
            "total_tests": len(self.pentest_results),
            "latest_test": (
                max(self.pentest_results.values(), key=lambda x: x.test_date).test_id
                if self.pentest_results
                else None
            ),
        }

    def _calculate_compliance_score(self) -> float:
        """
        Calculate overall compliance score (0-100).

        Returns:
            Compliance score percentage
        """
        if not self.controls:
            return 0.0

        total = len(self.controls)
        implemented = sum(
            1 for c in self.controls.values() if c.status == ControlStatus.IMPLEMENTED
        )
        partial = sum(1 for c in self.controls.values() if c.status == ControlStatus.PARTIAL)

        # Full points for implemented, half points for partial
        score = (implemented + 0.5 * partial) / total * 100
        return round(score, 2)

    def _save_controls(self) -> None:
        """Save controls to file."""
        controls_path = self.compliance_dir / "controls.json"
        with controls_path.open("w") as f:
            json.dump([c.to_dict() for c in self.controls.values()], f, indent=2)

    def _save_vulnerabilities(self) -> None:
        """Save vulnerabilities to file."""
        vulns_path = self.compliance_dir / "vulnerabilities.json"
        with vulns_path.open("w") as f:
            json.dump([v.to_dict() for v in self.vulnerabilities.values()], f, indent=2)

    def _save_pentest_results(self) -> None:
        """Save pentest results to file."""
        pentest_path = self.compliance_dir / "pentest_results.json"
        with pentest_path.open("w") as f:
            json.dump([p.to_dict() for p in self.pentest_results.values()], f, indent=2)

    def run_automated_security_scan(self) -> Dict[str, Any]:
        """
        Run automated security scanning.

        Returns:
            Scan results with findings
        """
        logger.info("Running automated security scan...")

        findings = []

        # Check 1: SSL/TLS Configuration
        ssl_dir = Path(".omnimind/ssl")
        if not ssl_dir.exists() or not (ssl_dir / "certificate.crt").exists():
            findings.append(
                VulnerabilityFinding(
                    finding_id=f"SCAN-{datetime.now().timestamp()}",
                    title="Missing SSL/TLS Configuration",
                    description="Production SSL certificates not found",
                    severity=RiskLevel.HIGH,
                    affected_component="Web Server",
                    remediation="Generate or install SSL/TLS certificates",
                )
            )

        # Check 2: Audit Logs
        audit_dir = Path(".omnimind/audit")
        if not audit_dir.exists():
            findings.append(
                VulnerabilityFinding(
                    finding_id=f"SCAN-{datetime.now().timestamp()}",
                    title="Audit Logging Not Enabled",
                    description="No audit logs directory found",
                    severity=RiskLevel.MEDIUM,
                    affected_component="Audit System",
                    remediation="Enable and configure audit logging",
                )
            )

        # Add findings
        for finding in findings:
            self.add_vulnerability(finding)

        return {
            "scan_date": datetime.now(timezone.utc).isoformat(),
            "findings_count": len(findings),
            "findings": [f.to_dict() for f in findings],
        }

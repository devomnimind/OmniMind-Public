import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import requests
from ..audit.alerting_system import AlertCategory, AlertingSystem, AlertSeverity
from ..audit.immutable_audit import ImmutableAuditSystem, get_audit_system

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
Web Scanner Module - Web Eyes for OmniMind
Implements web vulnerability scanning as sensory organs.

Based on: docs/Omni-Dev-Integrationforensis.md
Legal Compliance: 100% legal when used on own web applications
Tools: Nikto (GPL v2), Custom scanners
"""


class VulnerabilityType(Enum):
    """Types of web vulnerabilities."""

    XSS = "cross_site_scripting"
    SQL_INJECTION = "sql_injection"
    CSRF = "cross_site_request_forgery"
    PATH_TRAVERSAL = "path_traversal"
    OPEN_REDIRECT = "open_redirect"
    MISCONFIGURATION = "misconfiguration"
    OUTDATED_SOFTWARE = "outdated_software"
    WEAK_AUTHENTICATION = "weak_authentication"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    MISSING_SECURITY_HEADERS = "missing_security_headers"


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels."""

    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class WebVulnerability:
    """Detected web vulnerability."""

    url: str
    vulnerability_type: VulnerabilityType
    severity: VulnerabilitySeverity
    description: str
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    scanner: str = "custom"
    timestamp: str = field(default="")
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class WebScannerBrain:
    """
    Web security scanner for OmniMind.
    Scans web applications for common vulnerabilities.

    Features:
    - Basic vulnerability scanning
    - Security header analysis
    - SSL/TLS configuration check
    - Common vulnerability detection
    - Integration with external scanners (Nikto)
    """

    def __init__(
        self,
        audit_system: Optional[ImmutableAuditSystem] = None,
        alerting_system: Optional[AlertingSystem] = None,
    ) -> None:
        """
        Initialize web scanner.

        Args:
            audit_system: Optional audit system instance
            alerting_system: Optional alerting system instance
        """
        self.audit_system = audit_system or get_audit_system()
        self.alerting_system = alerting_system or AlertingSystem()
        self.nikto_available = self._check_nikto_available()

    def _check_nikto_available(self) -> bool:
        """Check if Nikto is installed and available."""
        try:
            result = subprocess.run(
                ["nikto", "-Version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def scan_url(
        self,
        url: str,
        scan_type: str = "basic",
        use_nikto: bool = False,
    ) -> Dict[str, Any]:
        """
        Scan web application for vulnerabilities.

        Args:
            url: URL to scan (must be your own application)
            scan_type: Type of scan ("basic", "headers", "full")
            use_nikto: Use Nikto scanner if available

        Returns:
            Dict containing scan results
        """
        findings = []

        # Validate URL
        if not self._is_valid_url(url):
            return {"error": "Invalid URL", "findings": []}

        # Perform custom scans
        if scan_type in ["basic", "full"]:
            findings.extend(self._check_security_headers(url))
            findings.extend(self._check_common_files(url))

        if scan_type == "full":
            findings.extend(self._check_ssl_config(url))
            findings.extend(self._check_http_methods(url))

        # Use Nikto if requested and available
        if use_nikto and self.nikto_available:
            nikto_findings = self._run_nikto_scan(url)
            findings.extend(nikto_findings)

        # Create alerts for critical findings
        for finding in findings:
            if finding.severity in [
                VulnerabilitySeverity.HIGH,
                VulnerabilitySeverity.CRITICAL,
            ]:
                self.alerting_system.create_alert(
                    severity=(
                        AlertSeverity.CRITICAL
                        if finding.severity == VulnerabilitySeverity.CRITICAL
                        else AlertSeverity.ERROR
                    ),
                    category=AlertCategory.SECURITY,
                    title=f"Web Vulnerability: {finding.vulnerability_type.value}",
                    message=finding.description,
                    details={
                        "url": finding.url,
                        "evidence": finding.evidence,
                        "remediation": finding.remediation,
                    },
                    source="web_scanner",
                )

        # Log scan action
        self.audit_system.log_action(
            "web_scan_completed",
            {
                "url": url,
                "scan_type": scan_type,
                "findings_count": len(findings),
                "critical_count": sum(
                    1 for f in findings if f.severity == VulnerabilitySeverity.CRITICAL
                ),
            },
            category="security",
        )

        return {
            "url": url,
            "scan_type": scan_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "findings": [self._vulnerability_to_dict(f) for f in findings],
            "summary": self._generate_summary(findings),
        }

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _check_security_headers(self, url: str) -> List[WebVulnerability]:
        """Check for missing security headers."""
        findings = []

        try:
            response = requests.get(url, timeout=10, verify=True)
            headers = response.headers

            # Required security headers
            required_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY or SAMEORIGIN",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000",
                "Content-Security-Policy": "restrictive policy",
            }

            for header, expected in required_headers.items():
                if header not in headers:
                    findings.append(
                        WebVulnerability(
                            url=url,
                            vulnerability_type=VulnerabilityType.MISSING_SECURITY_HEADERS,
                            severity=VulnerabilitySeverity.MEDIUM,
                            description=f"Missing security header: {header}",
                            evidence=f"Expected: {expected}",
                            remediation=f"Add '{header}: {expected}' to HTTP response headers",
                            scanner="custom",
                        )
                    )

            # Check for sensitive information in headers
            sensitive_headers = ["Server", "X-Powered-By"]
            for header in sensitive_headers:
                if header in headers:
                    findings.append(
                        WebVulnerability(
                            url=url,
                            vulnerability_type=VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
                            severity=VulnerabilitySeverity.LOW,
                            description=f"Server information disclosure: {header}",
                            evidence=f"{header}: {headers[header]}",
                            remediation=f"Remove or obfuscate '{header}' header",
                            scanner="custom",
                        )
                    )

        except requests.RequestException as e:
            findings.append(
                WebVulnerability(
                    url=url,
                    vulnerability_type=VulnerabilityType.MISCONFIGURATION,
                    severity=VulnerabilitySeverity.INFO,
                    description=f"Could not connect to URL: {str(e)}",
                    scanner="custom",
                )
            )

        return findings

    def _check_common_files(self, url: str) -> List[WebVulnerability]:
        """Check for common sensitive files."""
        findings = []
        base_url = url.rstrip("/")

        # Common sensitive files
        sensitive_files = [
            ".git/config",
            ".env",
            "config.php",
            "wp-config.php",
            "web.config",
            ".htaccess",
            "phpinfo.php",
            "admin/",
            "backup/",
        ]

        for file_path in sensitive_files:
            test_url = f"{base_url}/{file_path}"

            try:
                response = requests.get(test_url, timeout=5, verify=True)

                if response.status_code == 200:
                    findings.append(
                        WebVulnerability(
                            url=test_url,
                            vulnerability_type=VulnerabilityType.SENSITIVE_DATA_EXPOSURE,
                            severity=VulnerabilitySeverity.HIGH,
                            description=f"Sensitive file accessible: {file_path}",
                            evidence=f"HTTP {response.status_code}",
                            remediation=f"Remove or restrict access to {file_path}",
                            scanner="custom",
                        )
                    )
            except requests.RequestException:
                # File not accessible (good)
                pass

        return findings

    def _check_ssl_config(self, url: str) -> List[WebVulnerability]:
        """Check SSL/TLS configuration."""
        findings = []

        if not url.startswith("https://"):
            findings.append(
                WebVulnerability(
                    url=url,
                    vulnerability_type=VulnerabilityType.MISCONFIGURATION,
                    severity=VulnerabilitySeverity.HIGH,
                    description="Site not using HTTPS",
                    remediation="Enable HTTPS with valid SSL/TLS certificate",
                    scanner="custom",
                )
            )
        else:
            try:
                # Check if SSL certificate is valid
                requests.get(url, timeout=10, verify=True)
                # If we get here, certificate is valid
            except requests.exceptions.SSLError:
                findings.append(
                    WebVulnerability(
                        url=url,
                        vulnerability_type=VulnerabilityType.MISCONFIGURATION,
                        severity=VulnerabilitySeverity.CRITICAL,
                        description="Invalid SSL/TLS certificate",
                        remediation="Install valid SSL/TLS certificate from trusted CA",
                        scanner="custom",
                    )
                )
            except requests.RequestException:
                pass

        return findings

    def _check_http_methods(self, url: str) -> List[WebVulnerability]:
        """Check for dangerous HTTP methods enabled."""
        findings = []
        dangerous_methods = ["PUT", "DELETE", "TRACE", "OPTIONS"]

        for method in dangerous_methods:
            try:
                response = requests.request(method, url, timeout=5, verify=True)

                if response.status_code not in [405, 501]:  # Method not allowed
                    findings.append(
                        WebVulnerability(
                            url=url,
                            vulnerability_type=VulnerabilityType.MISCONFIGURATION,
                            severity=VulnerabilitySeverity.MEDIUM,
                            description=f"Dangerous HTTP method enabled: {method}",
                            evidence=f"HTTP {response.status_code}",
                            remediation=f"Disable {method} method if not required",
                            scanner="custom",
                        )
                    )
            except requests.RequestException:
                pass

        return findings

    def _run_nikto_scan(self, url: str) -> List[WebVulnerability]:
        """Run Nikto vulnerability scanner."""
        findings = []

        try:
            # Run nikto in quiet mode with JSON output
            result = subprocess.run(
                ["nikto", "-h", url, "-Format", "json", "-output", "-"],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse nikto output (simplified)
            for line in result.stdout.split("\n"):
                if "OSVDB" in line or "vulnerability" in line.lower():
                    findings.append(
                        WebVulnerability(
                            url=url,
                            vulnerability_type=VulnerabilityType.MISCONFIGURATION,
                            severity=VulnerabilitySeverity.MEDIUM,
                            description=line.strip(),
                            scanner="nikto",
                        )
                    )

        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

        return findings

    def _vulnerability_to_dict(self, vuln: WebVulnerability) -> Dict[str, Any]:
        """Convert vulnerability to dictionary."""
        return {
            "url": vuln.url,
            "type": vuln.vulnerability_type.value,
            "severity": vuln.severity.name,
            "description": vuln.description,
            "evidence": vuln.evidence,
            "remediation": vuln.remediation,
            "scanner": vuln.scanner,
            "timestamp": vuln.timestamp,
            "details": vuln.details,
        }

    def _generate_summary(self, findings: List[WebVulnerability]) -> Dict[str, Any]:
        """Generate summary of findings."""
        by_severity = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for finding in findings:
            by_severity[finding.severity.name.lower()] += 1

        return {
            "total_findings": len(findings),
            "by_severity": by_severity,
            "risk_level": (
                "CRITICAL"
                if by_severity["critical"] > 0
                else (
                    "HIGH"
                    if by_severity["high"] > 0
                    else "MEDIUM" if by_severity["medium"] > 0 else "LOW"
                )
            ),
        }


# Convenience functions


def scan_web_application(url: str) -> Dict[str, Any]:
    """Scan web application for vulnerabilities."""
    scanner = WebScannerBrain()
    return scanner.scan_url(url, scan_type="full")


def check_security_headers(url: str) -> List[WebVulnerability]:
    """Check security headers of web application."""
    scanner = WebScannerBrain()
    return scanner._check_security_headers(url)

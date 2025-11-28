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

"""Security package for OmniMind Phase 7+ implementation.

Includes:
- SecurityAgent: Process/file/network monitoring
- Network Sensors: Nmap integration for network discovery
- Web Scanner: Web vulnerability scanning
- Security Orchestrator: Unified security monitoring
"""

from .network_sensors import (
    NetworkAnomaly,
    NetworkHost,
    NetworkSensorGanglia,
    ThreatSeverity,
    detect_network_anomalies,
    scan_local_network,
)
from .security_agent import SecurityAgent
from .security_orchestrator import (
    SecurityOrchestrator,
    SecurityReport,
    SecurityStatus,
    run_security_audit,
    start_security_monitoring,
)
from .web_scanner import (
    VulnerabilitySeverity,
    VulnerabilityType,
    WebScannerBrain,
    WebVulnerability,
    check_security_headers,
    scan_web_application,
)

__all__ = [
    # Core security agent
    "SecurityAgent",
    # Network sensors
    "NetworkSensorGanglia",
    "NetworkHost",
    "NetworkAnomaly",
    "ThreatSeverity",
    "scan_local_network",
    "detect_network_anomalies",
    # Web scanner
    "WebScannerBrain",
    "WebVulnerability",
    "VulnerabilityType",
    "VulnerabilitySeverity",
    "scan_web_application",
    "check_security_headers",
    # Security orchestrator
    "SecurityOrchestrator",
    "SecurityReport",
    "SecurityStatus",
    "run_security_audit",
    "start_security_monitoring",
]

"""Security package for OmniMind Phase 7+ implementation.

Includes:
- SecurityAgent: Process/file/network monitoring
- Network Sensors: Nmap integration for network discovery
- Web Scanner: Web vulnerability scanning
- Security Orchestrator: Unified security monitoring
"""

from .security_agent import SecurityAgent
from .network_sensors import (
    NetworkSensorGanglia,
    NetworkHost,
    NetworkAnomaly,
    ThreatSeverity,
    scan_local_network,
    detect_network_anomalies,
)
from .web_scanner import (
    WebScannerBrain,
    WebVulnerability,
    VulnerabilityType,
    VulnerabilitySeverity,
    scan_web_application,
    check_security_headers,
)
from .security_orchestrator import (
    SecurityOrchestrator,
    SecurityReport,
    SecurityStatus,
    run_security_audit,
    start_security_monitoring,
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

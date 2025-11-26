#!/usr/bin/env python3
"""
Network Sensors Module - Network Eyes for OmniMind
Implements Wireshark + Nmap integration as sensory organs.

Based on: docs/Omni-Dev-Integrationforensis.md
Legal Compliance: 100% legal when used on own systems (GPL v2 licenses)
"""

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from ..audit.alerting_system import AlertCategory, AlertingSystem, AlertSeverity
from ..audit.immutable_audit import ImmutableAuditSystem, get_audit_system


class ThreatSeverity(Enum):
    """Threat severity levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class NetworkHost:
    """Detected network host."""

    ip: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    os_guess: Optional[str] = None
    open_ports: List[int] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    last_seen: str = field(default="")

    def __post_init__(self) -> None:
        if not self.last_seen:
            self.last_seen = datetime.now(timezone.utc).isoformat()


@dataclass
class NetworkAnomaly:
    """Detected network anomaly."""

    type: str
    severity: ThreatSeverity
    description: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    timestamp: str = field(default="")
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class NetworkSensorGanglia:
    """
    Network sensory organs for OmniMind.
    Integrates Nmap for network discovery and monitoring.

    Features:
    - Network host discovery
    - Port scanning
    - Service detection
    - OS fingerprinting
    - Anomaly detection
    """

    def __init__(
        self,
        audit_system: Optional[ImmutableAuditSystem] = None,
        alerting_system: Optional[AlertingSystem] = None,
    ):
        """
        Initialize network sensors.

        Args:
            audit_system: Optional audit system instance
            alerting_system: Optional alerting system instance
        """
        self.audit_system = audit_system or get_audit_system()
        self.alerting_system = alerting_system or AlertingSystem()
        self.known_hosts: Dict[str, NetworkHost] = {}
        self.baseline_ports: Dict[str, List[int]] = {}

        # Check if nmap is available
        self.nmap_available = self._check_nmap_available()

    def _check_nmap_available(self) -> bool:
        """Check if nmap is installed and available."""
        try:
            result = subprocess.run(
                ["nmap", "--version"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def scan_network(
        self,
        target: str = "127.0.0.1",
        scan_type: str = "basic",
        sudo: bool = False,
    ) -> Dict[str, Any]:
        """
        Scan network for hosts and services.

        Args:
            target: IP address, range, or subnet (e.g., "192.168.1.0/24")
            scan_type: Type of scan ("basic", "service", "os", "full")
            sudo: Use sudo for privileged scans (OS detection)

        Returns:
            Dict containing scan results
        """
        if not self.nmap_available:
            return {
                "error": "nmap not available",
                "hosts": [],
            }

        # Build nmap command based on scan type
        cmd = ["nmap"]
        if sudo:
            cmd.insert(0, "sudo")

        if scan_type == "basic":
            cmd.extend(["-sn", target])  # Ping scan only
        elif scan_type == "service":
            cmd.extend(["-sV", target])  # Service detection
        elif scan_type == "os":
            cmd.extend(["-O", target])  # OS detection (requires sudo)
        elif scan_type == "full":
            cmd.extend(["-sV", "-O", "-A", target])  # Full scan

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            hosts = self._parse_nmap_output(result.stdout)

            # Update known hosts
            for host in hosts:
                self.known_hosts[host.ip] = host

            # Log scan action
            self.audit_system.log_action(
                "network_scan_completed",
                {
                    "target": target,
                    "scan_type": scan_type,
                    "hosts_found": len(hosts),
                },
                category="security",
            )

            return {
                "target": target,
                "scan_type": scan_type,
                "hosts": [self._host_to_dict(h) for h in hosts],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except subprocess.TimeoutExpired:
            return {"error": "scan timeout", "hosts": []}
        except Exception as e:
            return {"error": str(e), "hosts": []}

    def _parse_nmap_output(self, output: str) -> List[NetworkHost]:
        """Parse nmap output to extract host information."""
        hosts = []
        current_host = None

        for line in output.split("\n"):
            # Host line: "Nmap scan report for 192.168.1.1"
            if "Nmap scan report for" in line:
                if current_host:
                    hosts.append(current_host)

                ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if ip_match:
                    current_host = NetworkHost(ip=ip_match.group(1))

                # Extract hostname if present
                hostname_match = re.search(r"for (.+) \(", line)
                if hostname_match and current_host:
                    current_host.hostname = hostname_match.group(1)

            # MAC address
            elif "MAC Address:" in line and current_host:
                mac_match = re.search(
                    r"([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})",
                    line,
                )
                if mac_match:
                    current_host.mac_address = mac_match.group(1)

            # Open port
            elif ("/tcp" in line or "/udp" in line) and current_host:
                port_match = re.search(r"(\d+)/(tcp|udp)\s+open", line)
                if port_match:
                    port = int(port_match.group(1))
                    current_host.open_ports.append(port)

                    # Extract service name
                    service_match = re.search(r"open\s+(\S+)", line)
                    if service_match:
                        current_host.services.append(service_match.group(1))

            # OS detection
            elif "OS details:" in line and current_host:
                os_match = re.search(r"OS details: (.+)", line)
                if os_match:
                    current_host.os_guess = os_match.group(1).strip()

        # Add last host
        if current_host:
            hosts.append(current_host)

        return hosts

    def _host_to_dict(self, host: NetworkHost) -> Dict[str, Any]:
        """Convert NetworkHost to dictionary."""
        return {
            "ip": host.ip,
            "hostname": host.hostname,
            "mac_address": host.mac_address,
            "os_guess": host.os_guess,
            "open_ports": host.open_ports,
            "services": host.services,
            "last_seen": host.last_seen,
        }

    def detect_anomalies(self) -> List[NetworkAnomaly]:
        """
        Detect network anomalies based on known baseline.

        Returns:
            List of detected anomalies
        """
        anomalies = []

        for ip, host in self.known_hosts.items():
            # Check for new hosts
            if ip not in self.baseline_ports:
                anomalies.append(
                    NetworkAnomaly(
                        type="new_host_detected",
                        severity=ThreatSeverity.LOW,
                        description=f"New host detected: {ip}",
                        source_ip=ip,
                        details={"hostname": host.hostname},
                    )
                )
                # Establish baseline
                self.baseline_ports[ip] = host.open_ports.copy()
                continue

            # Check for new open ports
            baseline = set(self.baseline_ports[ip])
            current = set(host.open_ports)
            new_ports = current - baseline

            if new_ports:
                # Suspicious ports (commonly used by malware)
                suspicious_ports = {4444, 5555, 6666, 7777, 8888, 31337}
                suspicious_detected = new_ports & suspicious_ports

                severity = ThreatSeverity.CRITICAL if suspicious_detected else ThreatSeverity.MEDIUM

                anomalies.append(
                    NetworkAnomaly(
                        type="new_ports_opened",
                        severity=severity,
                        description=f"New ports opened on {ip}: {new_ports}",
                        source_ip=ip,
                        details={
                            "new_ports": list(new_ports),
                            "suspicious_ports": list(suspicious_detected),
                        },
                    )
                )

                # Update baseline
                self.baseline_ports[ip] = host.open_ports.copy()

            # Check for suspicious services
            suspicious_services = {"nc", "ncat", "metasploit", "msfconsole"}
            detected_suspicious = [
                s for s in host.services if any(sus in s.lower() for sus in suspicious_services)
            ]

            if detected_suspicious:
                anomalies.append(
                    NetworkAnomaly(
                        type="suspicious_service_detected",
                        severity=ThreatSeverity.HIGH,
                        description=f"Suspicious services on {ip}: {detected_suspicious}",
                        source_ip=ip,
                        details={"services": detected_suspicious},
                    )
                )

        # Create alerts for critical anomalies
        for anomaly in anomalies:
            if anomaly.severity in [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL]:
                self.alerting_system.create_alert(
                    severity=(
                        AlertSeverity.CRITICAL
                        if anomaly.severity == ThreatSeverity.CRITICAL
                        else AlertSeverity.ERROR
                    ),
                    category=AlertCategory.SECURITY,
                    title=f"Network Anomaly: {anomaly.type}",
                    message=anomaly.description,
                    details=anomaly.details or {},
                    source="network_sensors",
                )

        return anomalies

    def get_network_health(self) -> Dict[str, Any]:
        """
        Calculate network health score.

        Returns:
            Dict containing network health metrics
        """
        total_hosts = len(self.known_hosts)
        hosts_with_suspicious_ports = 0
        total_open_ports = 0

        for host in self.known_hosts.values():
            total_open_ports += len(host.open_ports)

            # Check for suspicious ports
            suspicious_ports = {4444, 5555, 6666, 7777, 8888, 31337}
            if any(port in suspicious_ports for port in host.open_ports):
                hosts_with_suspicious_ports += 1

        # Calculate health score (100 = perfect, 0 = critical)
        health_score: float = 100.0

        if total_hosts > 0:
            # Penalize for suspicious ports
            suspicious_ratio = hosts_with_suspicious_ports / total_hosts
            health_score -= suspicious_ratio * 50

            # Penalize for too many open ports
            avg_open_ports = total_open_ports / total_hosts
            if avg_open_ports > 10:
                health_score -= min(30, (avg_open_ports - 10) * 2)

        return {
            "health_score": max(0, health_score),
            "total_hosts": total_hosts,
            "hosts_with_suspicious_ports": hosts_with_suspicious_ports,
            "total_open_ports": total_open_ports,
            "avg_open_ports_per_host": (total_open_ports / total_hosts if total_hosts > 0 else 0),
            "assessment": (
                "HEALTHY" if health_score >= 80 else "WARNING" if health_score >= 60 else "CRITICAL"
            ),
        }

    def establish_baseline(self, target: str = "127.0.0.1") -> bool:
        """
        Establish network baseline for anomaly detection.

        Args:
            target: Network to scan and establish baseline

        Returns:
            True if baseline established successfully
        """
        result = self.scan_network(target, scan_type="service")

        if "error" in result:
            return False

        # Store current state as baseline
        for host in self.known_hosts.values():
            self.baseline_ports[host.ip] = host.open_ports.copy()

        self.audit_system.log_action(
            "network_baseline_established",
            {
                "target": target,
                "hosts_baselined": len(self.baseline_ports),
            },
            category="security",
        )

        return True


# Convenience functions


def scan_local_network() -> Dict[str, Any]:
    """Scan local network (localhost only by default)."""
    sensors = NetworkSensorGanglia()
    return sensors.scan_network("127.0.0.1", scan_type="service")


def detect_network_anomalies() -> List[NetworkAnomaly]:
    """Detect network anomalies."""
    sensors = NetworkSensorGanglia()
    return sensors.detect_anomalies()

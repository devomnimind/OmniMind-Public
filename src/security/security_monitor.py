#!/usr/bin/env python3
"""
Security Monitor - Real-time Process and System Monitoring
Monitors processes, network connections, file system changes, and system resources.
Detects anomalies and generates security alerts.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import psutil
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from src.audit.immutable_audit import get_audit_system
from src.audit.alerting_system import AlertingSystem, AlertSeverity, AlertCategory


class AnomalyType(Enum):
    """Types of security anomalies."""

    SUSPICIOUS_PROCESS = "suspicious_process"
    HIGH_CPU_USAGE = "high_cpu_usage"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    UNUSUAL_NETWORK_CONNECTION = "unusual_network_connection"
    FILE_SYSTEM_CHANGE = "file_system_change"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE_SIGNATURE = "malware_signature"
    ROOTKIT_INDICATOR = "rootkit_indicator"


class ThreatLevel(Enum):
    """Threat severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event data structure."""

    timestamp: str
    event_type: AnomalyType
    threat_level: ThreatLevel
    description: str
    process_info: Optional[Dict[str, Any]] = None
    network_info: Optional[Dict[str, Any]] = None
    file_info: Optional[Dict[str, Any]] = None
    system_info: Optional[Dict[str, Any]] = None
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ProcessSnapshot:
    """Snapshot of process information."""

    pid: int
    name: str
    cmdline: List[str]
    cpu_percent: float
    memory_percent: float
    status: str
    create_time: float
    username: str
    connections: List[Dict[str, Any]] = field(default_factory=list)
    open_files: List[str] = field(default_factory=list)


class SecurityMonitor:
    """
    Real-time security monitoring system.

    Monitors:
    - Process activity and anomalies
    - Network connections and traffic
    - File system changes
    - System resource usage
    - User activity patterns
    """

    def __init__(
        self,
        audit_system: Optional[Any] = None,
        alerting_system: Optional[Any] = None,
        monitoring_interval: int = 30,
        log_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize Security Monitor.

        Args:
            audit_system: Audit system instance
            alerting_system: Alerting system instance
            monitoring_interval: Monitoring check interval in seconds
            log_dir: Directory for security logs
        """
        self.audit_system = audit_system or get_audit_system()
        self.alerting_system = alerting_system or AlertingSystem()
        self.monitoring_interval = monitoring_interval
        self.log_dir = Path(log_dir or "logs/security")

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Monitoring state
        self.is_monitoring = False
        self.baseline_processes: Dict[int, ProcessSnapshot] = {}
        self.baseline_network: Set[Tuple[str, int]] = set()
        self.baseline_files: Dict[str, str] = {}  # path -> hash
        self.known_safe_processes: Set[str] = {
            "systemd",
            "init",
            "bash",
            "zsh",
            "python",
            "python3",
            "sshd",
            "nginx",
            "apache2",
            "mysql",
            "postgresql",
            "redis-server",
            "docker",
            "containerd",
            "kubelet",
        }

        # Suspicious patterns
        self.suspicious_ports = {22, 23, 3389, 5900, 6667}  # SSH, Telnet, RDP, VNC, IRC
        self.suspicious_processes = {
            "netcat",
            "nc",
            "ncat",
            "socat",
            "cryptcat",
            "backdoor",
            "trojan",
            "virus",
            "malware",
            "miner",
            "xmrig",
            "ccminer",
        }

        # Thresholds
        self.cpu_threshold = 90.0  # %
        self.memory_threshold = 85.0  # %
        self.connection_threshold = 100  # max connections per process

        # Logger
        self.logger = logging.getLogger("security_monitor")
        self.logger.setLevel(logging.INFO)

        # Event history
        self.event_history: List[SecurityEvent] = []
        self.max_history_size = 1000

    async def start_monitoring(self) -> None:
        """Start continuous security monitoring."""
        if self.is_monitoring:
            self.logger.warning("Security monitoring already running")
            return

        self.is_monitoring = True
        self.logger.info("Starting security monitoring")

        # Log monitoring start
        self.audit_system.log_action(
            "security_monitoring_started",
            {
                "interval": self.monitoring_interval,
                "thresholds": {
                    "cpu": self.cpu_threshold,
                    "memory": self.memory_threshold,
                    "connections": self.connection_threshold,
                },
            },
            category="security",
        )

        try:
            # Establish baseline
            await self._establish_baseline()

            # Start monitoring loop
            while self.is_monitoring:
                try:
                    await self._monitoring_cycle()
                    await asyncio.sleep(self.monitoring_interval)
                except Exception as e:
                    self.logger.error(f"Monitoring cycle error: {e}")
                    await asyncio.sleep(self.monitoring_interval)

        except Exception as e:
            self.logger.error(f"Security monitoring failed: {e}")
            self.alerting_system.create_alert(
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.SECURITY,
                title="Security Monitor Failure",
                message=f"Security monitoring stopped due to error: {str(e)}",
                source="security_monitor",
            )
        finally:
            self.is_monitoring = False

    def stop_monitoring(self) -> None:
        """Stop security monitoring."""
        self.is_monitoring = False
        self.logger.info("Security monitoring stopped")

        self.audit_system.log_action("security_monitoring_stopped", {}, category="security")

    async def _establish_baseline(self) -> None:
        """Establish baseline system state."""
        self.logger.info("Establishing security baseline...")

        try:
            # Process baseline
            await self._snapshot_processes()

            # Network baseline
            self._snapshot_network()

            # File system baseline (critical files)
            await self._establish_file_baseline()

            self.logger.info("Security baseline established")

        except Exception as e:
            self.logger.error(f"Failed to establish baseline: {e}")

    async def _monitoring_cycle(self) -> None:
        """Single monitoring cycle."""
        try:
            # Monitor processes
            process_events = await self._monitor_processes()
            for event in process_events:
                await self._handle_security_event(event)

            # Monitor network
            network_events = await self._monitor_network()
            for event in network_events:
                await self._handle_security_event(event)

            # Monitor file system
            file_events = await self._monitor_file_system()
            for event in file_events:
                await self._handle_security_event(event)

            # Monitor system resources
            system_events = await self._monitor_system_resources()
            for event in system_events:
                await self._handle_security_event(event)

        except Exception as e:
            self.logger.error(f"Monitoring cycle failed: {e}")

    async def _monitor_processes(self) -> List[SecurityEvent]:
        """Monitor process activity for anomalies."""
        events = []

        try:
            current_processes = await self._get_process_snapshot()

            # Check for new suspicious processes
            for proc in current_processes.values():
                if self._is_suspicious_process(proc):
                    event = SecurityEvent(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        event_type=AnomalyType.SUSPICIOUS_PROCESS,
                        threat_level=self._calculate_process_threat_level(proc),
                        description=f"Suspicious process detected: {proc.name} (PID: {proc.pid})",
                        process_info={
                            "pid": proc.pid,
                            "name": proc.name,
                            "cmdline": proc.cmdline,
                            "cpu_percent": proc.cpu_percent,
                            "memory_percent": proc.memory_percent,
                            "username": proc.username,
                            "create_time": proc.create_time,
                        },
                        evidence=[
                            f"Process name: {proc.name}",
                            f"Command line: {' '.join(proc.cmdline)}",
                            f"CPU usage: {proc.cpu_percent:.1f}%",
                            f"Memory usage: {proc.memory_percent:.1f}%",
                        ],
                        recommendations=[
                            "Investigate process origin and purpose",
                            "Check process connections and file access",
                            "Consider terminating if unauthorized",
                        ],
                    )
                    events.append(event)

            # Check for high resource usage
            for proc in current_processes.values():
                if proc.cpu_percent > self.cpu_threshold:
                    event = SecurityEvent(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        event_type=AnomalyType.HIGH_CPU_USAGE,
                        threat_level=ThreatLevel.MEDIUM,
                        description=f"High CPU usage: {proc.name} ({proc.cpu_percent:.1f}%)",
                        process_info={
                            "pid": proc.pid,
                            "name": proc.name,
                            "cpu_percent": proc.cpu_percent,
                        },
                        recommendations=[
                            "Monitor process performance",
                            "Check for resource leaks",
                        ],
                    )
                    events.append(event)

                if proc.memory_percent > self.memory_threshold:
                    event = SecurityEvent(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        event_type=AnomalyType.HIGH_MEMORY_USAGE,
                        threat_level=ThreatLevel.MEDIUM,
                        description=f"High memory usage: {proc.name} ({proc.memory_percent:.1f}%)",
                        process_info={
                            "pid": proc.pid,
                            "name": proc.name,
                            "memory_percent": proc.memory_percent,
                        },
                        recommendations=[
                            "Check for memory leaks",
                            "Monitor process memory growth",
                        ],
                    )
                    events.append(event)

        except Exception as e:
            self.logger.error(f"Process monitoring failed: {e}")

        return events

    async def _monitor_network(self) -> List[SecurityEvent]:
        """Monitor network connections for anomalies."""
        events = []

        try:
            current_connections = self._get_network_connections()

            # Check for suspicious connections
            for conn in current_connections:
                if self._is_suspicious_connection(conn):
                    event = SecurityEvent(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        event_type=AnomalyType.UNUSUAL_NETWORK_CONNECTION,
                        threat_level=ThreatLevel.HIGH,
                        description=(
                            f"Suspicious network connection: "
                            f"{conn.get('local_addr')} -> "
                            f"{conn.get('remote_addr')}"
                        ),
                        network_info=conn,
                        evidence=[
                            f"Local: {conn.get('local_addr')}",
                            f"Remote: {conn.get('remote_addr')}",
                            f"Status: {conn.get('status')}",
                            f"PID: {conn.get('pid')}",
                        ],
                        recommendations=[
                            "Verify connection legitimacy",
                            "Check remote host reputation",
                            "Consider blocking suspicious IPs",
                        ],
                    )
                    events.append(event)

        except Exception as e:
            self.logger.error(f"Network monitoring failed: {e}")

        return events

    async def _monitor_file_system(self) -> List[SecurityEvent]:
        """Monitor file system for unauthorized changes."""
        events = []

        try:
            # Check critical files for changes
            for file_path, expected_hash in self.baseline_files.items():
                if os.path.exists(file_path):
                    current_hash = self._calculate_file_hash(file_path)
                    if current_hash != expected_hash:
                        event = SecurityEvent(
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            event_type=AnomalyType.FILE_SYSTEM_CHANGE,
                            threat_level=ThreatLevel.HIGH,
                            description=f"Critical file modified: {file_path}",
                            file_info={
                                "path": file_path,
                                "expected_hash": expected_hash,
                                "current_hash": current_hash,
                            },
                            evidence=[
                                f"File: {file_path}",
                                f"Expected hash: {expected_hash}",
                                f"Current hash: {current_hash}",
                            ],
                            recommendations=[
                                "Verify file integrity",
                                "Check modification timestamps",
                                "Review recent access logs",
                            ],
                        )
                        events.append(event)

        except Exception as e:
            self.logger.error(f"File system monitoring failed: {e}")

        return events

    async def _monitor_system_resources(self) -> List[SecurityEvent]:
        """Monitor system resource usage."""
        events = []

        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                event = SecurityEvent(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    event_type=AnomalyType.HIGH_CPU_USAGE,
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"High system CPU usage: {cpu_percent:.1f}%",
                    system_info={"cpu_percent": cpu_percent},
                    recommendations=["Check running processes", "Monitor system load"],
                )
                events.append(event)

            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                event = SecurityEvent(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    event_type=AnomalyType.HIGH_MEMORY_USAGE,
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"High system memory usage: {memory.percent:.1f}%",
                    system_info={
                        "memory_percent": memory.percent,
                        "memory_used": memory.used,
                        "memory_total": memory.total,
                    },
                    recommendations=[
                        "Check memory-intensive processes",
                        "Consider memory optimization",
                    ],
                )
                events.append(event)

        except Exception as e:
            self.logger.error(f"System resource monitoring failed: {e}")

        return events

    async def _handle_security_event(self, event: SecurityEvent) -> None:
        """Handle detected security event."""
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)

        # Log to audit system
        self.audit_system.log_action(
            "security_anomaly_detected",
            {
                "event_type": event.event_type.value,
                "threat_level": event.threat_level.value,
                "description": event.description,
                "evidence": event.evidence,
                "recommendations": event.recommendations,
            },
            category="security",
        )

        # Create alert based on threat level
        severity_map = {
            ThreatLevel.LOW: AlertSeverity.INFO,
            ThreatLevel.MEDIUM: AlertSeverity.WARNING,
            ThreatLevel.HIGH: AlertSeverity.ERROR,
            ThreatLevel.CRITICAL: AlertSeverity.CRITICAL,
        }

        self.alerting_system.create_alert(
            severity=severity_map[event.threat_level],
            category=AlertCategory.SECURITY,
            title=f"Security Anomaly: {event.event_type.value}",
            message=event.description,
            details={
                "event_type": event.event_type.value,
                "threat_level": event.threat_level.value,
                "evidence": event.evidence,
                "recommendations": event.recommendations,
                "process_info": event.process_info,
                "network_info": event.network_info,
                "file_info": event.file_info,
                "system_info": event.system_info,
            },
            source="security_monitor",
        )

        # Log to security log file
        self._log_security_event(event)

    def _log_security_event(self, event: SecurityEvent) -> None:
        """Log security event to file."""
        try:
            log_entry = {
                "timestamp": event.timestamp,
                "event_type": event.event_type.value,
                "threat_level": event.threat_level.value,
                "description": event.description,
                "evidence": event.evidence,
                "recommendations": event.recommendations,
            }

            log_file = self.log_dir / "security_events.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        except Exception as e:
            self.logger.error(f"Failed to log security event: {e}")

    async def _snapshot_processes(self) -> None:
        """Take snapshot of current processes."""
        try:
            processes = await self._get_process_snapshot()
            self.baseline_processes = processes
            self.logger.info(f"Process baseline: {len(processes)} processes")
        except Exception as e:
            self.logger.error(f"Process snapshot failed: {e}")

    def _snapshot_network(self) -> None:
        """Take snapshot of current network connections."""
        try:
            connections = self._get_network_connections()
            self.baseline_network = {
                (conn.get("local_addr", ""), conn.get("local_port", 0)) for conn in connections
            }
            self.logger.info(f"Network baseline: {len(self.baseline_network)} connections")
        except Exception as e:
            self.logger.error(f"Network snapshot failed: {e}")

    async def _establish_file_baseline(self) -> None:
        """Establish baseline for critical files."""
        try:
            critical_files = [
                "/etc/passwd",
                "/etc/shadow",
                "/etc/sudoers",
                "/etc/ssh/sshd_config",
                "requirements.txt",
                "pyproject.toml",
                "config/omnimind.yaml",
            ]

            for file_path in critical_files:
                if os.path.exists(file_path):
                    file_hash = self._calculate_file_hash(file_path)
                    self.baseline_files[file_path] = file_hash

            self.logger.info(f"File baseline: {len(self.baseline_files)} files")

        except Exception as e:
            self.logger.error(f"File baseline failed: {e}")

    async def _get_process_snapshot(self) -> Dict[int, ProcessSnapshot]:
        """Get current process snapshot."""
        processes = {}

        try:
            for proc in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "cmdline",
                    "cpu_percent",
                    "memory_percent",
                    "status",
                    "create_time",
                    "username",
                ]
            ):
                try:
                    info = proc.info
                    pid = info["pid"]

                    # Get connections for this process
                    try:
                        connections = proc.connections()
                        conn_info = [
                            {
                                "local_addr": (
                                    f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None
                                ),
                                "remote_addr": (
                                    f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None
                                ),
                                "status": conn.status,
                                "type": conn.type,
                            }
                            for conn in connections
                        ]
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        conn_info = []

                    # Get open files
                    try:
                        open_files = [f.path for f in proc.open_files()]
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        open_files = []

                    processes[pid] = ProcessSnapshot(
                        pid=pid,
                        name=info["name"] or "",
                        cmdline=info["cmdline"] or [],
                        cpu_percent=info["cpu_percent"] or 0.0,
                        memory_percent=info["memory_percent"] or 0.0,
                        status=info["status"] or "",
                        create_time=info["create_time"] or 0.0,
                        username=info["username"] or "",
                        connections=conn_info,
                        open_files=open_files,
                    )

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            self.logger.error(f"Process snapshot collection failed: {e}")

        return processes

    def _get_network_connections(self) -> List[Dict[str, Any]]:
        """Get current network connections."""
        connections = []

        try:
            for conn in psutil.net_connections(kind="inet"):
                conn_info = {
                    "fd": conn.fd,
                    "family": conn.family,
                    "type": conn.type,
                    "local_addr": (f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None),
                    "remote_addr": (f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None),
                    "status": conn.status,
                    "pid": conn.pid,
                }
                connections.append(conn_info)

        except Exception as e:
            self.logger.error(f"Network connection collection failed: {e}")

        return connections

    def _is_suspicious_process(self, proc: ProcessSnapshot) -> bool:
        """Check if process is suspicious."""
        # Check known suspicious process names
        if any(susp in proc.name.lower() for susp in self.suspicious_processes):
            return True

        # Check for processes with many connections
        if len(proc.connections) > self.connection_threshold:
            return True

        # Check for processes running as root with suspicious names
        if proc.username == "root" and proc.name not in self.known_safe_processes:
            return True

        # Check for recently created processes with high resource usage
        if time.time() - proc.create_time < 300:  # Created in last 5 minutes
            if proc.cpu_percent > 50 or proc.memory_percent > 30:
                return True

        return False

    def _is_suspicious_connection(self, conn: Dict[str, Any]) -> bool:
        """Check if network connection is suspicious."""
        try:
            remote_addr = conn.get("remote_addr", "")

            if not remote_addr:
                return False

            # Check for connections to suspicious ports
            try:
                remote_ip, remote_port = remote_addr.rsplit(":", 1)
                remote_port = int(remote_port)

                if remote_port in self.suspicious_ports:
                    return True

                # Check for very high ports (often used by malware)
                if remote_port > 50000:
                    return True

            except ValueError:
                pass

            # Check for connections to private IPs from unexpected processes
            # This is a simplified check - in production, you'd have more sophisticated logic

            return False

        except Exception:
            return False

    def _calculate_process_threat_level(self, proc: ProcessSnapshot) -> ThreatLevel:
        """Calculate threat level for a process."""
        threat_score = 0

        # Name-based scoring
        if any(susp in proc.name.lower() for susp in self.suspicious_processes):
            threat_score += 50

        # Resource usage scoring
        if proc.cpu_percent > 80:
            threat_score += 20
        elif proc.cpu_percent > 50:
            threat_score += 10

        if proc.memory_percent > 70:
            threat_score += 20
        elif proc.memory_percent > 40:
            threat_score += 10

        # Connection scoring
        if len(proc.connections) > 50:
            threat_score += 30
        elif len(proc.connections) > 20:
            threat_score += 15

        # User scoring
        if proc.username == "root":
            threat_score += 10

        # Age scoring (very new processes are more suspicious)
        age_hours = (time.time() - proc.create_time) / 3600
        if age_hours < 1:
            threat_score += 15

        # Determine threat level
        if threat_score >= 70:
            return ThreatLevel.CRITICAL
        elif threat_score >= 40:
            return ThreatLevel.HIGH
        elif threat_score >= 20:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "is_monitoring": self.is_monitoring,
            "monitoring_interval": self.monitoring_interval,
            "baseline_processes": len(self.baseline_processes),
            "baseline_network_connections": len(self.baseline_network),
            "baseline_files": len(self.baseline_files),
            "event_history_size": len(self.event_history),
            "thresholds": {
                "cpu_threshold": self.cpu_threshold,
                "memory_threshold": self.memory_threshold,
                "connection_threshold": self.connection_threshold,
            },
            "last_update": datetime.now(timezone.utc).isoformat(),
        }

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent security events."""
        events = self.event_history[-limit:]
        return [
            {
                "timestamp": event.timestamp,
                "event_type": event.event_type.value,
                "threat_level": event.threat_level.value,
                "description": event.description,
                "evidence": event.evidence,
                "recommendations": event.recommendations,
            }
            for event in events
        ]

    def get_running_processes(self) -> List[ProcessSnapshot]:
        """
        Get list of currently running processes.
        Public wrapper for testing and monitoring.
        """
        processes = []
        try:
            for proc in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "cpu_percent",
                    "memory_percent",
                    "status",
                    "create_time",
                    "username",
                ]
            ):
                try:
                    # Get process info
                    info = proc.as_dict(
                        [
                            "pid",
                            "name",
                            "cpu_percent",
                            "memory_percent",
                            "status",
                            "create_time",
                            "username",
                        ]
                    )

                    # Get command line
                    try:
                        cmdline = proc.cmdline()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        cmdline = []

                    snapshot = ProcessSnapshot(
                        pid=info["pid"],
                        name=info["name"] or "",
                        cmdline=cmdline,
                        cpu_percent=info.get("cpu_percent", 0.0) or 0.0,
                        memory_percent=info.get("memory_percent", 0.0) or 0.0,
                        status=info.get("status", ""),
                        create_time=info.get("create_time", 0.0) or 0.0,
                        username=info.get("username", ""),
                    )
                    processes.append(snapshot)

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

        except Exception as e:
            self.logger.error(f"Failed to get running processes: {e}")

        return processes

    def is_suspicious_process(self, proc: ProcessSnapshot) -> bool:
        """
        Check if a process is suspicious.
        Public wrapper for _is_suspicious_process for testing.
        """
        return self._is_suspicious_process(proc)

    def create_security_event(
        self,
        event_type: AnomalyType,
        threat_level: ThreatLevel,
        description: str,
        process_info: Optional[Dict[str, Any]] = None,
    ) -> SecurityEvent:
        """
        Create and record a security event.
        Public wrapper for creating security events.
        """
        event = SecurityEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            threat_level=threat_level,
            description=description,
            process_info=process_info,
        )

        # Add to event history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size :]

        # Log to audit system
        self.audit_system.log_action(
            "security_event",
            {
                "event_type": event_type.value,
                "threat_level": threat_level.value,
                "description": description,
            },
            category="security",
        )

        return event

    def monitor_system_resources(self) -> Dict[str, float]:
        """
        Monitor current system resource usage.
        Public wrapper for testing resource monitoring.
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
            }
        except Exception as e:
            self.logger.error(f"Failed to monitor system resources: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
            }

    def detect_resource_anomaly(self, resource_type: str, value: float) -> bool:
        """
        Detect if a resource value is anomalous.
        Public method for testing anomaly detection.

        Args:
            resource_type: Type of resource ('cpu', 'memory', 'disk')
            value: Resource usage value (percentage)

        Returns:
            True if anomalous, False otherwise
        """
        thresholds = {
            "cpu": self.cpu_threshold,
            "memory": self.memory_threshold,
            "disk": 90.0,  # Default disk threshold
        }

        threshold = thresholds.get(resource_type, 90.0)
        return value > threshold

    def establish_baseline(self) -> None:
        """
        Establish baseline for monitoring (synchronous wrapper).
        For testing purposes - calls async version in a new event loop.
        """
        # Simple synchronous version for testing
        try:
            # Get current processes as baseline
            processes = self.get_running_processes()
            for proc in processes:
                self.baseline_processes[proc.pid] = proc

            self.logger.info(f"Baseline established with {len(processes)} processes")

        except Exception as e:
            self.logger.error(f"Failed to establish baseline: {e}")


# Convenience functions
_security_monitor: Optional[SecurityMonitor] = None


def get_security_monitor() -> SecurityMonitor:
    """Get singleton security monitor instance."""
    global _security_monitor
    if _security_monitor is None:
        _security_monitor = SecurityMonitor()
    return _security_monitor


async def start_security_monitoring() -> None:
    """Start security monitoring."""
    monitor = get_security_monitor()
    await monitor.start_monitoring()


def stop_security_monitoring() -> None:
    """Stop security monitoring."""
    monitor = get_security_monitor()
    monitor.stop_monitoring()


if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        monitor = SecurityMonitor()

        print("Starting security monitoring...")
        await monitor.start_monitoring()

    asyncio.run(main())

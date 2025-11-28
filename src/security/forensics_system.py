from __future__ import annotations

import json
import logging
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from src.audit.immutable_audit import get_audit_system

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
Forensics System - Digital Evidence Collection and Incident Analysis
Collects, analyzes, and reports on security incidents and system anomalies.
"""


class EvidenceType(Enum):
    """Types of digital evidence."""

    LOG_ENTRY = "log_entry"
    FILE_SYSTEM = "file_system"
    NETWORK_CONNECTION = "network_connection"
    PROCESS_INFO = "process_info"
    SYSTEM_METRICS = "system_metrics"
    CONFIGURATION = "configuration"
    MEMORY_DUMP = "memory_dump"
    SCREENSHOT = "screenshot"


class IncidentSeverity(Enum):
    """Incident severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident investigation status."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class EvidenceItem:
    """Digital evidence item."""

    id: str
    type: EvidenceType
    timestamp: str
    source: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    integrity_hash: str = ""


@dataclass
class Incident:
    """Security incident record."""

    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: str
    updated_at: str
    detected_by: str
    assigned_to: Optional[str] = None
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)


@dataclass
class ForensicsReport:
    """Comprehensive forensics report."""

    incident_id: str
    timestamp: str
    summary: str
    timeline: List[Dict[str, Any]]
    evidence_collected: int
    findings: List[str]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    execution_time: float = 0.0


class EvidenceCollector:
    """
    Collects digital evidence from various sources.

    Features:
    - Log file analysis
    - File system snapshots
    - Network connection logging
    - Process information gathering
    - System metrics collection
    """

    def __init__(self, evidence_dir: Optional[str] = None):
        """
        Initialize Evidence Collector.

        Args:
            evidence_dir: Directory to store collected evidence
        """
        self.evidence_dir = Path(evidence_dir or "data/forensics/evidence")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("evidence_collector")
        self.logger.setLevel(logging.INFO)

    def collect_log_evidence(
        self, log_files: List[str], patterns: Optional[List[str]] = None
    ) -> List[EvidenceItem]:
        """
        Collect evidence from log files.

        Args:
            log_files: List of log file paths
            patterns: Regex patterns to search for

        Returns:
            List of evidence items
        """
        evidence_items = []

        for log_file in log_files:
            try:
                log_path = Path(log_file)
                if not log_path.exists():
                    continue

                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Search for patterns
                if patterns:
                    matches = []
                    for pattern in patterns:
                        regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
                        matches.extend(regex.findall(content))

                    if matches:
                        evidence = EvidenceItem(
                            id=f"log_{log_path.name}_{int(time.time())}",
                            type=EvidenceType.LOG_ENTRY,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                            source=str(log_path),
                            content={"matches": matches, "pattern_count": len(matches)},
                            metadata={
                                "log_file": str(log_path),
                                "file_size": log_path.stat().st_size,
                            },
                        )
                        evidence_items.append(evidence)

            except Exception as e:
                self.logger.error(f"Failed to collect log evidence from {log_file}: {e}")

        return evidence_items

    def collect_file_system_evidence(self, target_paths: List[str]) -> List[EvidenceItem]:
        """
        Collect file system evidence.

        Args:
            target_paths: List of file/directory paths to examine

        Returns:
            List of evidence items
        """
        evidence_items = []

        for target_path in target_paths:
            try:
                path = Path(target_path)
                if not path.exists():
                    continue

                if path.is_file():
                    # File evidence
                    stat_info = path.stat()
                    evidence = EvidenceItem(
                        id=f"file_{path.name}_{int(time.time())}",
                        type=EvidenceType.FILE_SYSTEM,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        source=str(path),
                        content={
                            "type": "file",
                            "size": stat_info.st_size,
                            "mtime": stat_info.st_mtime,
                            "permissions": oct(stat_info.st_mode),
                        },
                        metadata={"path": str(path), "exists": True},
                    )
                    evidence_items.append(evidence)

                elif path.is_dir():
                    # Directory evidence
                    files = list(path.rglob("*"))
                    dir_info = {
                        "type": "directory",
                        "total_files": len([f for f in files if f.is_file()]),
                        "total_dirs": len([f for f in files if f.is_dir()]),
                        "total_size": sum(f.stat().st_size for f in files if f.is_file()),
                    }

                    evidence = EvidenceItem(
                        id=f"dir_{path.name}_{int(time.time())}",
                        type=EvidenceType.FILE_SYSTEM,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        source=str(path),
                        content=dir_info,
                        metadata={"path": str(path), "exists": True},
                    )
                    evidence_items.append(evidence)

            except Exception as e:
                self.logger.error(f"Failed to collect file system evidence from {target_path}: {e}")

        return evidence_items

    def collect_network_evidence(self) -> List[EvidenceItem]:
        """
        Collect network connection evidence.

        Returns:
            List of evidence items
        """
        evidence_items = []

        try:
            # Use netstat or ss to get network connections
            result = subprocess.run(["ss", "-tuln"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                connections = result.stdout.strip().split("\n")[1:]  # Skip header

                evidence = EvidenceItem(
                    id=f"network_{int(time.time())}",
                    type=EvidenceType.NETWORK_CONNECTION,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    source="system",
                    content={"connections": connections, "count": len(connections)},
                    metadata={
                        "command": "ss -tuln",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
                evidence_items.append(evidence)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback to netstat if ss not available
            try:
                result = subprocess.run(
                    ["netstat", "-tuln"], capture_output=True, text=True, timeout=10
                )

                if result.returncode == 0:
                    connections = result.stdout.strip().split("\n")[1:]

                    evidence = EvidenceItem(
                        id=f"network_fallback_{int(time.time())}",
                        type=EvidenceType.NETWORK_CONNECTION,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        source="system",
                        content={"connections": connections, "count": len(connections)},
                        metadata={
                            "command": "netstat -tuln",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                    )
                    evidence_items.append(evidence)

            except Exception as e:
                self.logger.error(f"Failed to collect network evidence: {e}")

        return evidence_items

    def collect_process_evidence(self) -> List[EvidenceItem]:
        """
        Collect process information evidence.

        Returns:
            List of evidence items
        """
        evidence_items = []

        try:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                processes = result.stdout.strip().split("\n")[1:]  # Skip header

                evidence = EvidenceItem(
                    id=f"processes_{int(time.time())}",
                    type=EvidenceType.PROCESS_INFO,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    source="system",
                    content={"processes": processes, "count": len(processes)},
                    metadata={
                        "command": "ps aux",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
                evidence_items.append(evidence)

        except Exception as e:
            self.logger.error(f"Failed to collect process evidence: {e}")

        return evidence_items

    def collect_system_metrics(self) -> List[EvidenceItem]:
        """
        Collect system metrics evidence.

        Returns:
            List of evidence items
        """
        evidence_items = []

        try:
            # CPU and memory info
            with open("/proc/meminfo", "r") as f:
                mem_info = f.read()

            with open("/proc/loadavg", "r") as f:
                load_avg = f.read().strip()

            metrics = {
                "memory_info": mem_info,
                "load_average": load_avg,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            evidence = EvidenceItem(
                id=f"system_metrics_{int(time.time())}",
                type=EvidenceType.SYSTEM_METRICS,
                timestamp=datetime.now(timezone.utc).isoformat(),
                source="system",
                content=metrics,
                metadata={"source_files": ["/proc/meminfo", "/proc/loadavg"]},
            )
            evidence_items.append(evidence)

        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")

        return evidence_items

    def save_evidence(self, evidence_items: List[EvidenceItem]) -> None:
        """
        Save evidence items to disk.

        Args:
            evidence_items: List of evidence to save
        """
        for evidence in evidence_items:
            try:
                evidence_file = self.evidence_dir / f"{evidence.id}.json"

                evidence_data = {
                    "id": evidence.id,
                    "type": evidence.type.value,
                    "timestamp": evidence.timestamp,
                    "source": evidence.source,
                    "content": evidence.content,
                    "metadata": evidence.metadata,
                    "integrity_hash": evidence.integrity_hash,
                }

                with open(evidence_file, "w", encoding="utf-8") as f:
                    json.dump(evidence_data, f, indent=2, ensure_ascii=False)

            except Exception as e:
                self.logger.error(f"Failed to save evidence {evidence.id}: {e}")


class LogAnalyzer:
    """
    Analyzes log files for security incidents and anomalies.

    Features:
    - Pattern-based anomaly detection
    - Timeline reconstruction
    - Correlation analysis
    - Threat intelligence matching
    """

    def __init__(self) -> None:
        """Initialize Log Analyzer."""
        self.logger = logging.getLogger("log_analyzer")
        self.logger.setLevel(logging.INFO)

        # Common security patterns
        self.security_patterns = {
            "failed_login": re.compile(r"failed.*login|authentication.*failed", re.IGNORECASE),
            "suspicious_access": re.compile(r"access.*denied|permission.*denied", re.IGNORECASE),
            "unusual_activity": re.compile(r"unusual.*activity|anomalous.*behavior", re.IGNORECASE),
            "security_alert": re.compile(r"security.*alert|intrusion.*detected", re.IGNORECASE),
            "privilege_escalation": re.compile(
                r"privilege.*escalation|sudo.*attempt", re.IGNORECASE
            ),
        }

        # Threat indicators
        self.threat_indicators = {
            "brute_force": ["multiple.*failed.*login", "password.*guessing"],
            "reconnaissance": ["port.*scan", "nmap", "masscan"],
            "exploitation": ["exploit", "vulnerability", "cve"],
            "malware": ["trojan", "virus", "malware", "ransomware"],
        }

    def analyze_logs(self, log_content: str, log_source: str) -> Dict[str, Any]:
        """
        Analyze log content for security incidents.

        Args:
            log_content: Log content to analyze
            log_source: Source of the log

        Returns:
            Analysis results
        """
        analysis: Dict[str, Any] = {
            "log_source": log_source,
            "total_lines": len(log_content.split("\n")),
            "security_events": [],
            "anomalies": [],
            "threat_indicators": [],
            "severity_score": 0,
            "recommendations": [],
        }

        # Analyze each line
        lines = log_content.split("\n")
        for i, line in enumerate(lines):
            if not line.strip():
                continue

            # Check security patterns
            for pattern_name, pattern in self.security_patterns.items():
                if pattern.search(line):
                    analysis["security_events"].append(
                        {
                            "line_number": i + 1,
                            "pattern": pattern_name,
                            "content": line.strip(),
                            "timestamp": self._extract_timestamp(line),
                        }
                    )
                    analysis["severity_score"] += 1

            # Check threat indicators
            for threat_type, indicators in self.threat_indicators.items():
                for indicator in indicators:
                    if re.search(indicator, line, re.IGNORECASE):
                        analysis["threat_indicators"].append(
                            {
                                "line_number": i + 1,
                                "threat_type": threat_type,
                                "indicator": indicator,
                                "content": line.strip(),
                            }
                        )
                        analysis["severity_score"] += 2

        # Generate recommendations
        if analysis["security_events"]:
            analysis["recommendations"].append("Review security events for potential incidents")

        if analysis["threat_indicators"]:
            analysis["recommendations"].append("Investigate threat indicators immediately")
            analysis["recommendations"].append("Consider isolating affected systems")

        if analysis["severity_score"] > 10:
            analysis["recommendations"].append(
                "Escalate to security team - high severity incident detected"
            )

        return analysis

    def correlate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Correlate related security events.

        Args:
            events: List of security events

        Returns:
            Correlated event groups
        """
        # Simple correlation based on time windows and similar patterns
        correlated_groups = []
        processed = set()

        for i, event in enumerate(events):
            if i in processed:
                continue

            group = [event]
            processed.add(i)

            # Look for related events within time window
            event_time = self._parse_timestamp(event.get("timestamp", ""))

            for j, other_event in enumerate(events):
                if j in processed or j == i:
                    continue

                other_time = self._parse_timestamp(other_event.get("timestamp", ""))

                # If events are within 5 minutes and similar patterns
                if (
                    event_time
                    and other_time
                    and abs((event_time - other_time).total_seconds()) < 300
                    and event.get("pattern") == other_event.get("pattern")
                ):

                    group.append(other_event)
                    processed.add(j)

            if len(group) > 1:
                correlated_groups.append(
                    {
                        "group_size": len(group),
                        "pattern": group[0].get("pattern"),
                        "time_range": (
                            f"{group[0].get('timestamp')} to " f"{group[-1].get('timestamp')}"
                        ),
                        "events": group,
                    }
                )

        return correlated_groups

    def _extract_timestamp(self, log_line: str) -> Optional[str]:
        """Extract timestamp from log line."""
        # Common timestamp patterns
        patterns = [
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",  # ISO format
            r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}",  # US format
            r"\w{3} \d{2} \d{2}:\d{2}:\d{2}",  # Syslog format
        ]

        for pattern in patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group()

        return None

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp string to datetime object."""
        if not timestamp_str:
            return None

        try:
            # Try ISO format first
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except ValueError:
            pass

        # Try other common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%b %d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        return None


class ForensicsSystem:
    """
    Main forensics system for incident investigation and evidence collection.

    Features:
    - Automated evidence collection
    - Incident management
    - Log analysis and correlation
    - Report generation
    - Chain of custody maintenance
    """

    def __init__(
        self,
        forensics_dir: Optional[str] = None,
        evidence_dir: Optional[str] = None,
        reports_dir: Optional[str] = None,
        audit_system: Optional[Any] = None,
    ) -> None:
        """
        Initialize Forensics System.

        Args:
            forensics_dir: Base directory for forensics data (backward compatibility)
            evidence_dir: Directory for evidence storage
            reports_dir: Directory for reports
            audit_system: Audit system instance
        """
        # Handle backward compatibility
        if forensics_dir and not evidence_dir:
            evidence_dir = forensics_dir
        if forensics_dir and not reports_dir:
            reports_dir = str(Path(forensics_dir) / "reports")

        self.evidence_collector = EvidenceCollector(evidence_dir)
        self.log_analyzer = LogAnalyzer()
        self.audit_system = audit_system or get_audit_system()

        self.reports_dir = Path(reports_dir or "data/forensics/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.incidents_dir = Path("data/forensics/incidents")
        self.incidents_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("forensics_system")
        self.logger.setLevel(logging.INFO)

    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        detected_by: str,
    ) -> Incident:
        """
        Create a new security incident.

        Args:
            title: Incident title
            description: Incident description
            severity: Incident severity
            detected_by: Who/what detected the incident

        Returns:
            Created incident
        """
        incident_id = f"INC-{int(time.time())}-{severity.value.upper()}"

        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
            detected_by=detected_by,
        )

        # Save incident
        self._save_incident(incident)

        # Log to audit
        self.audit_system.log_action(
            "incident_created",
            {
                "incident_id": incident.id,
                "title": incident.title,
                "severity": incident.severity.value,
                "detected_by": incident.detected_by,
            },
            category="security",
        )

        self.logger.info(f"Created incident: {incident.id}")
        return incident

    def collect_evidence(self, incident_id: str, evidence_types: List[str]) -> List[EvidenceItem]:
        """
        Collect evidence for an incident.

        Args:
            incident_id: Incident ID
            evidence_types: Types of evidence to collect

        Returns:
            List of collected evidence items
        """
        evidence_items = []

        # Load incident
        incident = self._load_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident not found: {incident_id}")

        # Collect different types of evidence
        if "logs" in evidence_types:
            log_files = [
                "logs/security.log",
                "logs/audit.log",
                "logs/application.log",
            ]
            evidence_items.extend(self.evidence_collector.collect_log_evidence(log_files))

        if "filesystem" in evidence_types:
            target_paths = [
                "/etc",
                "/var/log",
                "config/",
                "data/",
            ]
            evidence_items.extend(
                self.evidence_collector.collect_file_system_evidence(target_paths)
            )

        if "network" in evidence_types:
            evidence_items.extend(self.evidence_collector.collect_network_evidence())

        if "processes" in evidence_types:
            evidence_items.extend(self.evidence_collector.collect_process_evidence())

        if "system" in evidence_types:
            evidence_items.extend(self.evidence_collector.collect_system_metrics())

        # Save evidence
        self.evidence_collector.save_evidence(evidence_items)

        # Add to incident
        incident.evidence_items.extend(evidence_items)
        incident.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_incident(incident)

        # Log to audit
        self.audit_system.log_action(
            "evidence_collected",
            {
                "incident_id": incident.id,
                "evidence_count": len(evidence_items),
                "evidence_types": evidence_types,
            },
            category="security",
        )

        self.logger.info(
            f"Collected {len(evidence_items)} evidence items for incident {incident_id}"
        )
        return evidence_items

    def analyze_incident(self, incident_id: str) -> Dict[str, Any]:
        """
        Analyze an incident using collected evidence.

        Args:
            incident_id: Incident ID

        Returns:
            Analysis results
        """
        incident = self._load_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident not found: {incident_id}")

        analysis: Dict[str, Any] = {
            "incident_id": incident.id,
            "log_analysis": [],
            "correlations": [],
            "risk_assessment": {},
            "recommendations": [],
        }

        # Analyze log evidence
        log_evidence = [e for e in incident.evidence_items if e.type == EvidenceType.LOG_ENTRY]
        for evidence in log_evidence:
            if "matches" in evidence.content:
                # Analyze the matched log content
                matches = evidence.content["matches"]
                if matches:
                    log_analysis = self.log_analyzer.analyze_logs(
                        "\n".join([str(m) for m in matches]), evidence.source
                    )
                analysis["log_analysis"].append(log_analysis)

        # Correlate events
        all_events = []
        for log_analysis in analysis["log_analysis"]:
            all_events.extend(log_analysis.get("security_events", []))

        if all_events:
            correlations = self.log_analyzer.correlate_events(all_events)
            analysis["correlations"] = correlations

        # Risk assessment
        total_severity = sum(log.get("severity_score", 0) for log in analysis["log_analysis"])
        threat_count = sum(
            len(log.get("threat_indicators", [])) for log in analysis["log_analysis"]
        )

        analysis["risk_assessment"] = {
            "severity_score": total_severity,
            "threat_indicators": threat_count,
            "correlation_groups": len(analysis["correlations"]),
            "risk_level": self._calculate_risk_level(total_severity, threat_count),
        }

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        # Update incident
        incident.analysis = analysis
        incident.recommendations = list(analysis["recommendations"])
        incident.status = IncidentStatus.INVESTIGATING
        incident.updated_at = datetime.now(timezone.utc).isoformat()
        self._save_incident(incident)

        # Log to audit
        self.audit_system.log_action(
            "incident_analyzed",
            {
                "incident_id": incident.id,
                "severity_score": analysis["risk_assessment"]["severity_score"],
                "risk_level": analysis["risk_assessment"]["risk_level"],
            },
            category="security",
        )

        self.logger.info(
            f"Analyzed incident {incident_id}: "
            f"risk level {analysis['risk_assessment']['risk_level']}"
        )
        return analysis

    def generate_report(self, incident_id: str) -> ForensicsReport:
        """
        Generate comprehensive forensics report.

        Args:
            incident_id: Incident ID

        Returns:
            Forensics report
        """
        start_time = time.time()

        incident = self._load_incident(incident_id)
        if not incident:
            raise ValueError(f"Incident not found: {incident_id}")

        # Build timeline
        timeline = self._build_incident_timeline(incident)

        # Generate findings
        findings = self._generate_findings(incident)

        # Risk assessment
        risk_assessment = incident.analysis.get("risk_assessment", {})

        # Create report
        report = ForensicsReport(
            incident_id=incident.id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            summary=f"Security incident investigation report for {incident.title}",
            timeline=timeline,
            evidence_collected=len(incident.evidence_items),
            findings=findings,
            recommendations=incident.recommendations,
            risk_assessment=risk_assessment,
            execution_time=time.time() - start_time,
        )

        # Save report
        self._save_report(report)

        # Log to audit
        self.audit_system.log_action(
            "forensics_report_generated",
            {
                "incident_id": incident.id,
                "evidence_count": report.evidence_collected,
                "findings_count": len(report.findings),
                "risk_level": risk_assessment.get("risk_level", "unknown"),
            },
            category="security",
        )

        self.logger.info(f"Generated forensics report for incident {incident_id}")
        return report

    def get_incident_status(self, incident_id: str) -> Optional[Incident]:
        """
        Get incident status.

        Args:
            incident_id: Incident ID

        Returns:
            Incident object or None if not found
        """
        return self._load_incident(incident_id)

    def list_incidents(self, status_filter: Optional[IncidentStatus] = None) -> List[Incident]:
        """
        List all incidents.

        Args:
            status_filter: Filter by status

        Returns:
            List of incidents
        """
        incidents = []

        try:
            for incident_file in self.incidents_dir.glob("incident_*.json"):
                try:
                    with open(incident_file, "r", encoding="utf-8") as f:
                        incident_data = json.load(f)

                    incident = Incident(**incident_data)
                    if status_filter is None or incident.status == status_filter:
                        incidents.append(incident)

                except Exception as e:
                    self.logger.error(f"Failed to load incident from {incident_file}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to list incidents: {e}")

        return sorted(incidents, key=lambda x: x.created_at, reverse=True)

    def _save_incident(self, incident: Incident) -> None:
        """Save incident to disk."""
        try:
            incident_file = self.incidents_dir / f"incident_{incident.id}.json"

            incident_data = {
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "created_at": incident.created_at,
                "updated_at": incident.updated_at,
                "detected_by": incident.detected_by,
                "assigned_to": incident.assigned_to,
                "evidence_items": [
                    {
                        "id": item.id,
                        "type": item.type.value,
                        "timestamp": item.timestamp,
                        "source": item.source,
                        "content": item.content,
                        "metadata": item.metadata,
                        "integrity_hash": item.integrity_hash,
                    }
                    for item in incident.evidence_items
                ],
                "analysis": incident.analysis,
                "recommendations": list(incident.recommendations),
                "tags": list(incident.tags),
            }

            with open(incident_file, "w", encoding="utf-8") as f:
                json.dump(incident_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save incident {incident.id}: {e}")

    def _load_incident(self, incident_id: str) -> Optional[Incident]:
        """Load incident from disk."""
        try:
            incident_file = self.incidents_dir / f"incident_{incident_id}.json"

            if not incident_file.exists():
                return None

            with open(incident_file, "r", encoding="utf-8") as f:
                incident_data = json.load(f)

            # Convert back to enums
            incident_data["severity"] = IncidentSeverity(incident_data["severity"])
            incident_data["status"] = IncidentStatus(incident_data["status"])

            # Convert evidence items
            evidence_items = []
            for item_data in incident_data["evidence_items"]:
                item_data["type"] = EvidenceType(item_data["type"])
                evidence_items.append(EvidenceItem(**item_data))

            incident_data["evidence_items"] = evidence_items

            return Incident(**incident_data)

        except Exception as e:
            self.logger.error(f"Failed to load incident {incident_id}: {e}")
            return None

    def _calculate_risk_level(self, severity_score: int, threat_count: int) -> str:
        """Calculate risk level based on scores."""
        total_score = severity_score + (threat_count * 2)

        if total_score >= 20:
            return "CRITICAL"
        elif total_score >= 10:
            return "HIGH"
        elif total_score >= 5:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        risk_level = analysis["risk_assessment"]["risk_level"]

        if risk_level == "CRITICAL":
            recommendations.extend(
                [
                    "IMMEDIATE: Isolate affected systems",
                    "Engage incident response team",
                    "Preserve all evidence - do not modify systems",
                    "Notify relevant stakeholders",
                ]
            )
        elif risk_level == "HIGH":
            recommendations.extend(
                [
                    "Investigate threat indicators immediately",
                    "Review access logs and permissions",
                    "Update security policies if needed",
                    "Monitor affected systems closely",
                ]
            )
        elif risk_level == "MEDIUM":
            recommendations.extend(
                [
                    "Review security events and correlations",
                    "Verify system integrity",
                    "Update monitoring rules if applicable",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Document findings for future reference",
                    "Consider enhancing monitoring capabilities",
                ]
            )

        # Add specific recommendations based on correlations
        if analysis["correlations"]:
            recommendations.append("Investigate correlated events for attack patterns")

        return recommendations

    def _build_incident_timeline(self, incident: Incident) -> List[Dict[str, Any]]:
        """Build chronological timeline of incident events."""
        timeline = []

        # Add incident creation
        timeline.append(
            {
                "timestamp": incident.created_at,
                "event": "Incident created",
                "description": incident.description,
                "type": "incident",
            }
        )

        # Add evidence collection events
        for evidence in incident.evidence_items:
            timeline.append(
                {
                    "timestamp": evidence.timestamp,
                    "event": f"Evidence collected: {evidence.type.value}",
                    "description": f"Collected from {evidence.source}",
                    "type": "evidence",
                }
            )

        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])

        return timeline

    def _generate_findings(self, incident: Incident) -> List[str]:
        """Generate findings from incident analysis."""
        findings = []

        if incident.analysis:
            risk = incident.analysis.get("risk_assessment", {})

            findings.append(f"Risk Level: {risk.get('risk_level', 'Unknown')}")
            findings.append(f"Severity Score: {risk.get('severity_score', 0)}")
            findings.append(f"Threat Indicators: {risk.get('threat_indicators', 0)}")

            correlations = incident.analysis.get("correlations", [])
            if correlations:
                findings.append(f"Correlated Event Groups: {len(correlations)}")

            log_analysis = incident.analysis.get("log_analysis", [])
            if log_analysis:
                total_events = sum(len(log.get("security_events", [])) for log in log_analysis)
                findings.append(f"Security Events Detected: {total_events}")

        findings.append(f"Evidence Items Collected: {len(incident.evidence_items)}")

        return findings

    def _save_report(self, report: ForensicsReport) -> None:
        """Save forensics report to disk."""
        try:
            report_file = self.reports_dir / (
                f"forensics_report_{report.incident_id}_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            report_data = {
                "incident_id": report.incident_id,
                "timestamp": report.timestamp,
                "summary": report.summary,
                "timeline": report.timeline,
                "evidence_collected": report.evidence_collected,
                "findings": report.findings,
                "recommendations": report.recommendations,
                "risk_assessment": report.risk_assessment,
                "execution_time": report.execution_time,
            }

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save forensics report: {e}")


# Convenience functions
_forensics_system: Optional[ForensicsSystem] = None


def get_forensics_system() -> ForensicsSystem:
    """Get singleton forensics system instance."""
    global _forensics_system
    if _forensics_system is None:
        _forensics_system = ForensicsSystem()
    return _forensics_system


def create_security_incident(title: str, description: str, severity: str = "medium") -> Incident:
    """Create a security incident."""
    system = get_forensics_system()
    severity_enum = IncidentSeverity(severity.lower())
    return system.create_incident(title, description, severity_enum, "automated_detection")


def collect_incident_evidence(incident_id: str, evidence_types: List[str]) -> List[EvidenceItem]:
    """Collect evidence for an incident."""
    system = get_forensics_system()
    return system.collect_evidence(incident_id, evidence_types)


def analyze_security_incident(incident_id: str) -> Dict[str, Any]:
    """Analyze a security incident."""
    system = get_forensics_system()
    return system.analyze_incident(incident_id)


def generate_forensics_report(incident_id: str) -> ForensicsReport:
    """Generate forensics report for an incident."""
    system = get_forensics_system()
    return system.generate_report(incident_id)


if __name__ == "__main__":
    # Example usage
    forensics = ForensicsSystem()

    # Create incident
    incident = forensics.create_incident(
        "Suspicious Login Attempts",
        "Multiple failed login attempts detected",
        IncidentSeverity.HIGH,
        "security_monitor",
    )
    print(f"Created incident: {incident.id}")

    # Collect evidence
    evidence = forensics.collect_evidence(incident.id, ["logs", "network", "processes"])
    print(f"Collected {len(evidence)} evidence items")

    # Analyze incident
    analysis = forensics.analyze_incident(incident.id)
    print(f"Analysis complete - Risk level: {analysis['risk_assessment']['risk_level']}")

    # Generate report
    report = forensics.generate_report(incident.id)
    print(f"Report generated with {len(report.findings)} findings")


class IncidentAnalyzer:
    """
    Analyzes security incidents and generates insights.

    This class provides methods to analyze incidents, generate timelines,
    and assess risks based on collected evidence.
    """

    def __init__(self) -> None:
        """Initialize the incident analyzer."""
        self.logger = logging.getLogger(__name__)

    def analyze_incident(self, incident: Incident) -> Dict[str, Any]:
        """
        Analyze a security incident.

        Args:
            incident: The incident to analyze

        Returns:
            Dict containing analysis results
        """
        analysis = {
            "incident_id": incident.id,
            "severity": incident.severity.value,
            "status": incident.status.value,
            "risk_assessment": self.assess_risk(incident),
            "timeline": [],  # Would be populated with evidence timeline
            "recommendations": self._generate_recommendations(incident),
        }
        return analysis

    def generate_timeline(self, evidence_list: List[EvidenceItem]) -> List[Dict[str, Any]]:
        """
        Generate a chronological timeline from evidence.

        Args:
            evidence_list: List of evidence items

        Returns:
            List of timeline events sorted by timestamp
        """
        timeline = []
        for evidence in evidence_list:
            event = {
                "timestamp": evidence.timestamp,
                "type": evidence.type.value,
                "source": evidence.source,
                "description": f"Evidence collected: {evidence.type.value}",
                "evidence_id": evidence.id,
            }
            timeline.append(event)

        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        return timeline

    def assess_risk(self, incident: Incident) -> Dict[str, Any]:
        """
        Assess the risk level of an incident.

        Args:
            incident: The incident to assess

        Returns:
            Dict containing risk assessment
        """
        # Base risk on severity
        severity_scores = {
            IncidentSeverity.LOW: 1,
            IncidentSeverity.MEDIUM: 3,
            IncidentSeverity.HIGH: 7,
            IncidentSeverity.CRITICAL: 10,
        }

        base_score = severity_scores.get(incident.severity, 5)

        # Adjust based on status
        if incident.status == IncidentStatus.RESOLVED:
            risk_level = "Low"
            adjusted_score = base_score * 0.3
        elif incident.status == IncidentStatus.CONTAINED:
            risk_level = "Medium"
            adjusted_score = base_score * 0.7
        else:
            risk_level = "High" if base_score >= 7 else "Medium"
            adjusted_score = base_score

        return {
            "risk_level": risk_level,
            "risk_score": adjusted_score,
            "severity": incident.severity.value,
            "status": incident.status.value,
            "assessment_date": datetime.now(timezone.utc).isoformat(),
        }

    def _generate_recommendations(self, incident: Incident) -> List[str]:
        """
        Generate recommendations based on incident analysis.

        Args:
            incident: The incident being analyzed

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            recommendations.append("Immediate containment procedures required")
            recommendations.append("Escalate to security team leadership")

        if incident.status == IncidentStatus.OPEN:
            recommendations.append("Begin incident investigation immediately")

        recommendations.append("Collect additional evidence and logs")
        recommendations.append("Review access controls and permissions")

        return recommendations

"""SecurityAgent implements Phase 7 monitoring, detection, and playbook response."""

import asyncio
import atexit
import copy
import logging
import os
import subprocess
import textwrap
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import yaml

from ..tools.tool_base import AuditedTool, ToolCategory
from .dlp import DLPValidator, DLPViolationError
from .firecracker_sandbox import FirecrackerSandbox
from .playbooks.data_exfiltration_response import DataExfiltrationPlaybook
from .playbooks.intrusion_response import IntrusionPlaybook
from .playbooks.malware_response import MalwarePlaybook
from .playbooks.privilege_escalation_response import PrivilegeEscalationPlaybook
from .playbooks.rootkit_response import RootkitPlaybook
from .playbooks.suspicious_port_response import SuspiciousPortPlaybook
from .playbooks.utils import run_command

logger = logging.getLogger(__name__)

_security_log_handler: Optional[logging.Handler] = None


def _close_security_log_handler() -> None:
    global _security_log_handler
    if _security_log_handler:
        _security_log_handler.close()
        _security_log_handler = None


class ThreatLevel(Enum):
    """Level of severity assigned to a security event."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SecurityEvent:
    """Represents a detected security signal."""

    timestamp: str
    event_type: str
    source: str
    description: str
    details: Dict[str, Any]
    threat_level: ThreatLevel
    raw_data: str
    responded: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


DEFAULT_CONFIG: Dict[str, Any] = {
    "security_agent": {
        "enabled": True,
        "monitoring_interval": 60,
        "auto_response": True,
        "report_interval": 300,
        "audit_log_path": str(Path.home() / ".omnimind" / "security_actions.log"),
    },
    "monitoring": {
        "processes": {
            "interval": 60,
            "suspicious_patterns": [
                "nmap",
                "nikto",
                "sqlmap",
                "nc",
                "ncat",
                "bash -i",
                "sh -i",
                "/dev/tcp",
                "metasploit",
                "msfconsole",
            ],
        },
        "files": {"interval": 300, "paths": ["/etc", "/usr/bin", "/root"]},
        "network": {
            "interval": 30,
            "suspicious_ports": [4444, 5555, 6666, 7777, 8888, 31337],
        },
        "logs": {
            "interval": 10,
            "files": ["/var/log/auth.log", "/var/log/syslog"],
            "keywords": [
                "Failed password",
                "Invalid user",
                "sudo: COMMAND=",
                "Authentication failure",
            ],
        },
    },
}


class SecurityAgent(AuditedTool):
    """Autonomous security monitor that coordinates playbooks."""

    def __init__(self, config_path: str, llm: Optional[Any] = None):
        super().__init__("security_agent", ToolCategory.SECURITY)
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.llm = llm
        self.logger = self._setup_logging()
        self.tools_available = self._check_tools()
        self.playbooks = self._load_playbooks()
        self.event_history: List[SecurityEvent] = []
        self.incident_log: List[Dict[str, Any]] = []
        self._pending_events: List[SecurityEvent] = []
        self._monitoring_tasks: List[asyncio.Task[Any]] = []
        self._stop_event: Optional[asyncio.Event] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        kernel = os.environ.get("OMNIMIND_FIRECRACKER_KERNEL")
        rootfs = os.environ.get("OMNIMIND_FIRECRACKER_ROOTFS")
        policy_path = os.environ.get("OMNIMIND_DLP_POLICY_FILE")
        self.sandbox = FirecrackerSandbox(kernel_path=kernel, rootfs_path=rootfs)
        self.dlp_validator = DLPValidator(policy_path=policy_path)

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            logger.warning("Config not found, falling back to defaults: %s", self.config_path)
            return self._deep_merge(DEFAULT_CONFIG, {})
        try:
            with open(self.config_path, "r", encoding="utf-8") as stream:
                data = yaml.safe_load(stream) or {}
            return self._deep_merge(DEFAULT_CONFIG, data)
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to read config %s: %s", self.config_path, exc)
            return self._deep_merge(DEFAULT_CONFIG, {})

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = copy.deepcopy(base)
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _check_tools(self) -> Dict[str, bool]:
        commands = {
            "auditctl": [
                "auditctl",
                "--version",
            ],  # Requires root, will fail in test env
            "aide": ["aide", "--version"],
            "chkrootkit": ["chkrootkit", "-V"],
            "rkhunter": ["rkhunter", "--version"],
            "lynis": ["lynis", "--version"],
            "clamdscan": ["clamdscan", "--version"],  # Needs config
            "ufw": ["ufw", "--version"],
            "ps": ["ps", "--version"],
            "ss": ["ss", "--version"],
            "lsof": ["lsof", "-v"],
        }
        availability: Dict[str, bool] = {}
        for tool, cmd in commands.items():
            try:
                subprocess.run(cmd, capture_output=True, timeout=3)
                availability[tool] = True
            except Exception:  # pragma: no cover
                availability[tool] = False
            logger.info("Tool %s available: %s", tool, availability[tool])
        return availability

    def _setup_logging(self) -> logging.Logger:
        log_path = Path.home() / ".omnimind" / "security.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        global _security_log_handler

        handler: logging.Handler
        if _security_log_handler is None:
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            _security_log_handler = handler
            atexit.register(_close_security_log_handler)
        else:
            handler = _security_log_handler

        logger_instance = logging.getLogger("security_agent")
        if handler not in logger_instance.handlers:
            logger_instance.addHandler(handler)
        logger_instance.setLevel(logging.INFO)
        return logger_instance

    def _load_playbooks(self) -> Dict[str, Any]:
        return {
            "rootkit": RootkitPlaybook(),
            "intrusion": IntrusionPlaybook(),
            "malware": MalwarePlaybook(),
            "privilege_escalation": PrivilegeEscalationPlaybook(),
            "data_exfiltration": DataExfiltrationPlaybook(),
            "suspicious_port": SuspiciousPortPlaybook(),
        }

    @staticmethod
    def _current_utc_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _should_stop(self) -> bool:
        """Indica se o loop contínuo recebeu sinal de parada."""

        return bool(self._stop_event and self._stop_event.is_set())

    async def _wait_interval(self, interval: int) -> bool:
        """Aguarda o intervalo ou encerra antecipadamente se o stop_event for acionado."""

        delay = max(1, int(interval))
        if not self._stop_event:
            await asyncio.sleep(delay)
            return False
        try:
            await asyncio.wait_for(self._stop_event.wait(), timeout=delay)
            return True
        except asyncio.TimeoutError:
            return False

    async def _shutdown_tasks(self) -> None:
        """Cancela e aguarda o término das tarefas de monitoramento."""

        if not self._monitoring_tasks:
            return
        tasks = list(self._monitoring_tasks)
        self._monitoring_tasks = []
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    def request_stop(self) -> None:
        """Sinaliza para que o processo assíncrono finalize."""

        if not self._stop_event:
            return
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._stop_event.set)
            return
        self._stop_event.set()

    async def start_continuous_monitoring(self) -> None:
        if not self.config["security_agent"]["enabled"]:
            self.logger.warning("SecurityAgent disabled via config")
            return
        if self._monitoring_tasks:
            self.logger.info("SecurityAgent monitoring already running")
            return
        self._loop = asyncio.get_running_loop()
        self._stop_event = asyncio.Event()
        monitors = [
            asyncio.create_task(self._monitor_processes(), name="security.process"),
            asyncio.create_task(self._monitor_files(), name="security.files"),
            asyncio.create_task(self._monitor_network(), name="security.network"),
            asyncio.create_task(self._monitor_logs(), name="security.logs"),
            asyncio.create_task(self._analyze_events(), name="security.analysis"),
            asyncio.create_task(self._respond_to_threats(), name="security.response"),
        ]
        self._monitoring_tasks = monitors
        self.logger.info("SecurityAgent continuous monitoring started (%d tasks)", len(monitors))
        try:
            await self._stop_event.wait()
        finally:
            await self._shutdown_tasks()
            self._stop_event = None
            self._loop = None
            self.logger.info("SecurityAgent continuous monitoring stopped")

    async def _monitor_processes(self) -> None:
        interval = self.config["monitoring"]["processes"]["interval"]
        patterns = self.config["monitoring"]["processes"].get("suspicious_patterns", [])
        try:
            while not self._should_stop():
                try:
                    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                        info = proc.info
                        if self._is_suspicious_process(info, patterns):
                            event = self._create_event(
                                event_type="suspicious_process",
                                source=f"process:{info.get('pid')}",
                                description=f"Suspicious process {info.get('name')}",
                                details=info,
                                raw_data=str(info),
                                level=ThreatLevel.HIGH,
                            )
                            await self._handle_event(event)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                if await self._wait_interval(interval):
                    break
        except asyncio.CancelledError:
            self.logger.info("Process monitoring task cancelled")
            raise

    async def _monitor_files(self) -> None:
        interval = self.config["monitoring"]["files"]["interval"]
        try:
            while not self._should_stop():
                if not self.tools_available.get("aide"):
                    self.logger.warning("AIDE unavailable, skipping file monitoring")
                    if await self._wait_interval(interval):
                        break
                    continue
                try:
                    # Validar comando antes de executar
                    from .playbooks.utils import validate_command_safety

                    validation = validate_command_safety(["sudo", "-n", "aide", "--check"])
                    if validation.get("status") == "approved":
                        result = await asyncio.to_thread(
                            run_command, ["sudo", "-n", "aide", "--check"]
                        )
                        changes = self._parse_aide_output(result.get("output", ""))
                        for change in changes:
                            event = self._create_event(
                                event_type="file_integrity",
                                source="aide",
                                description=f"File change detected: {change.get('path')}",
                                details=change,
                                raw_data=result.get("output", ""),
                                level=ThreatLevel.MEDIUM,
                            )
                            await self._handle_event(event)
                    else:
                        self.logger.warning("AIDE command not approved for execution")
                except Exception as exc:  # pragma: no cover
                    self.logger.error("File monitor failed: %s", exc)
                if await self._wait_interval(interval):
                    break
        except asyncio.CancelledError:
            self.logger.info("File monitoring task cancelled")
            raise

    async def _monitor_network(self) -> None:
        interval = self.config["monitoring"]["network"]["interval"]
        suspicious_ports = set(self.config["monitoring"]["network"].get("suspicious_ports", []))
        try:
            while not self._should_stop():
                try:
                    connections = psutil.net_connections(kind="inet")
                    summaries: Dict[str, int] = {}
                    for conn in connections:
                        if not conn.raddr:
                            continue

                        # Skip localhost
                        if conn.raddr.ip in (
                            "127.0.0.1",
                            "localhost",
                            "0.0.0.0",
                            "::1",
                        ):
                            continue

                        remote = f"{conn.raddr.ip}:{conn.raddr.port}"
                        local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "unknown"

                        if self._is_suspicious_connection(remote, suspicious_ports):
                            event = self._create_event(
                                event_type="suspicious_network",
                                source="network",
                                description=f"Suspicious connection {local} -> {remote}",
                                details={"local": local, "remote": remote},
                                raw_data=str(conn),
                                level=ThreatLevel.HIGH,
                            )
                            await self._handle_event(event)

                        summaries[remote] = summaries.get(remote, 0) + 1
                        # Increased threshold to 20 to reduce false positives
                        if summaries[remote] > 20:
                            event = self._create_event(
                                event_type="data_exfiltration",
                                source="network",
                                description="Repeated outbound connection",
                                details={"remote": remote, "count": summaries[remote]},
                                raw_data=str(conn),
                                level=ThreatLevel.HIGH,
                            )
                            await self._handle_event(event)
                except Exception as exc:  # pragma: no cover
                    self.logger.error("Network monitor failed: %s", exc)
                if await self._wait_interval(interval):
                    break
        except asyncio.CancelledError:
            self.logger.info("Network monitoring task cancelled")
            raise

    async def _monitor_logs(self) -> None:
        interval = self.config["monitoring"]["logs"]["interval"]
        files = self.config["monitoring"]["logs"].get("files", [])
        keywords = self.config["monitoring"]["logs"].get("keywords", [])
        try:
            while not self._should_stop():
                for log_file in files:
                    if not os.path.exists(log_file):
                        continue
                    try:
                        with open(log_file, "r", encoding="utf-8", errors="ignore") as fp:
                            fp.seek(0, os.SEEK_END)
                            size = fp.tell()
                            fp.seek(max(0, size - 4096))
                            for line in fp:
                                if self._is_suspicious_log_line(line, keywords):
                                    event = self._create_event(
                                        event_type="log_anomaly",
                                        source=log_file,
                                        description="Suspicious log detected",
                                        details={"line": line.strip()},
                                        raw_data=line,
                                        level=ThreatLevel.MEDIUM,
                                    )
                                    await self._handle_event(event)
                    except Exception as exc:  # pragma: no cover
                        self.logger.warning("Log monitor error on %s: %s", log_file, exc)
                if await self._wait_interval(interval):
                    break
        except asyncio.CancelledError:
            self.logger.info("Log monitoring task cancelled")
            raise

    async def _analyze_events(self) -> None:
        interval = 60
        try:
            while not self._should_stop():
                try:
                    if self.event_history:
                        recent = self.event_history[:10]
                        analysis = await self._analyze_with_llm(recent)
                        if analysis.get("is_incident"):
                            incident = {
                                "timestamp": self._current_utc_iso(),
                                "events": [event.event_type for event in recent],
                                "analysis": analysis,
                            }
                            self.incident_log.append(incident)
                            self.logger.warning(
                                "LLM incident detected: %s", analysis.get("description")
                            )
                except Exception as exc:  # pragma: no cover
                    self.logger.error("Analysis loop failed: %s", exc)
                if await self._wait_interval(interval):
                    break
        except asyncio.CancelledError:
            self.logger.info("Incident analysis task cancelled")
            raise

    async def _respond_to_threats(self) -> None:
        interval = 30
        try:
            while not self._should_stop():
                to_process = [event for event in self.event_history if not event.responded]
                for event in to_process:
                    if event.threat_level in {ThreatLevel.HIGH, ThreatLevel.CRITICAL}:
                        await self._execute_response(event)
                if await self._wait_interval(interval):
                    break
        except asyncio.CancelledError:
            self.logger.info("Threat response task cancelled")
            raise

    async def _execute_response(self, event: SecurityEvent) -> None:
        playbook_key = self._map_event_to_playbook(event.event_type)
        playbook = self.playbooks.get(playbook_key)
        self.logger.info("Executing playbook %s for %s", playbook_key, event.event_type)
        if not playbook:
            self.logger.warning("No playbook registered for %s", event.event_type)
            return

        # Only run sandbox if enabled
        if self.sandbox.enabled:
            sandbox_result = self.sandbox.run(
                {"event": event.event_type, "playbook": playbook_key},
                sandbox_name="security_playbook",
            )
            if not sandbox_result.success:
                self.logger.error(
                    "Sandbox execution failed for %s: %s",
                    event.event_type,
                    sandbox_result.output,
                )
        else:
            self.logger.info(
                "Sandbox disabled, skipping sandbox execution for %s", event.event_type
            )

        try:
            result = await playbook.execute(self, event)
            entry = {
                "event_id": event.id,
                "type": event.event_type,
                "threat_level": event.threat_level.name,
                "playbook": playbook_key,
                "result": result,
                "timestamp": self._current_utc_iso(),
            }
            self.incident_log.append(entry)
            self._audit_action("respond", event.details, entry, "SUCCESS")
        except Exception as exc:  # pragma: no cover
            self.logger.error("Playbook %s failed: %s", playbook_key, exc)
            self._audit_action("respond", event.details, {}, "ERROR", str(exc))
        finally:
            event.responded = True

    async def _handle_event(self, event: SecurityEvent) -> None:
        try:
            violation = self.dlp_validator.enforce(event.raw_data)
        except DLPViolationError as violation_error:
            self.logger.warning(
                "DLP block for event %s: %s",
                event.event_type,
                violation_error.violation.rule,
            )
            self._audit_action(
                "dlp.block",
                event.details,
                violation_error.violation.__dict__,
                "BLOCKED",
            )
            return
        if violation:
            self.logger.info("DLP alert for event %s: %s", event.event_type, violation.rule)
        self.event_history.insert(0, event)
        self._pending_events.append(event)
        self.logger.warning("New security event %s: %s", event.event_type, event.description)
        self._audit_action("event", event.details, event.__dict__, "SUCCESS")

    async def _analyze_with_llm(self, events: List[SecurityEvent]) -> Dict[str, Any]:
        if not self.llm:
            summary = {
                "is_incident": any(
                    event.threat_level.value >= ThreatLevel.HIGH.value for event in events
                ),
                "description": "Threshold analysis",
                "confidence": 0.65,
            }
            return summary
        try:
            events_text = "\n".join(
                f"- {event.timestamp}: {event.event_type} -> {event.description}"
                for event in events
            )
            prompt = f"""
Analyze these security events and detect coordinated incidents:

{events_text}

Provide:
- Is incident? (yes/no)
- Threat level
- Recommended response
"""
            response = await self.llm.invoke(prompt)
            content = getattr(response, "content", "")
            is_incident = "yes" in content.lower()
            return {
                "is_incident": is_incident,
                "description": content.strip()[:500],
                "confidence": 0.7,
            }
        except Exception as exc:  # pragma: no cover
            self.logger.error("LLM analysis failed: %s", exc)
            return {
                "is_incident": False,
                "description": "LLM failure",
                "confidence": 0.5,
            }

    def _map_event_to_playbook(self, event_type: str) -> str:
        mapping = {
            "suspicious_process": "intrusion",
            "rootkit_detected": "rootkit",
            "suspicious_network": "intrusion",
            "malware_detected": "malware",
            "data_exfiltration": "data_exfiltration",
            "log_anomaly": "privilege_escalation",
            "file_integrity": "malware",
            "new_ports_opened": "suspicious_port",
            "suspicious_port": "suspicious_port",
        }
        return mapping.get(event_type, "intrusion")

    def _create_event(
        self,
        event_type: str,
        source: str,
        description: str,
        details: Dict[str, Any],
        raw_data: str,
        level: ThreatLevel,
    ) -> SecurityEvent:
        return SecurityEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            source=source,
            description=description,
            details=details,
            raw_data=raw_data,
            threat_level=level,
        )

    def _is_suspicious_process(self, proc: Dict[str, Any], patterns: List[str]) -> bool:
        name = (proc.get("name") or "").lower()
        cmdline = " ".join(proc.get("cmdline") or [])

        # Whitelist common development processes
        whitelist = [
            "python",
            "node",
            "ps",
            "vscode",
            "cursor",
            "code-insiders",
            "pyright",
            "black",
            "flake8",
            "mypy",
        ]
        if any(wl in name for wl in whitelist):
            return False

        for pattern in patterns:
            if pattern.lower() in name or pattern.lower() in cmdline.lower():
                return True
        return False

    def _is_suspicious_connection(self, conn: str, ports: set[int]) -> bool:
        if ":" not in conn:
            return False
        try:
            _, port = conn.rsplit(":", 1)
            return int(port) in ports
        except ValueError:
            return False

    def _is_suspicious_log_line(self, line: str, keywords: List[str]) -> bool:
        return any(keyword.lower() in line.lower() for keyword in keywords)

    def _parse_aide_output(self, output: str) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for line in output.splitlines():
            lowered = line.lower()
            if "added" in lowered or "changed" in lowered or "removed" in lowered:
                parts = line.split()
                events.append({"change": line, "path": parts[-1] if parts else line})
        return events

    def generate_security_report(self) -> str:
        total_events = len(self.event_history)
        critical = sum(
            1 for event in self.event_history if event.threat_level == ThreatLevel.CRITICAL
        )
        high = sum(1 for event in self.event_history if event.threat_level == ThreatLevel.HIGH)
        recent_incidents = self.incident_log[-5:]
        report = textwrap.dedent(
            f"""
                ╔══════════════════════════════════════════════════════════════════════╗
                ║ SECURITY REPORT - OMNIMIND
                ║ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
                ╚══════════════════════════════════════════════════════════════════════╝

                SUMMARY:
                  Total Events: {total_events}
                  Critical Threats: {critical}
                  High Threats: {high}
                  Incidents Logged: {len(self.incident_log)}

                TOOLS AVAILABLE:
            """
        )
        for tool, available in self.tools_available.items():
            status = "✅" if available else "❌"
            report += f"              {status} {tool}\n"
        if recent_incidents:
            report += "\n            RECENT INCIDENTS:\n"
            for incident in recent_incidents:
                report += f"              - {incident.get('timestamp')} - {incident.get('type')}\n"
        self._audit_action("report", {}, report, "SUCCESS")
        return report

    def execute(self, action: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        if action == "status":
            return {
                "active": bool(self._monitoring_tasks),
                "events": len(self.event_history),
                "incidents": len(self.incident_log),
            }
        if action == "report":
            return self.generate_security_report()
        raise ValueError(f"Unsupported action: {action}")

    def monitor_processes(self) -> Optional[Dict[str, Any]]:
        """Monitor processes for suspicious activity (synchronous version)."""
        try:
            patterns = self.config["monitoring"]["processes"].get("suspicious_patterns", [])
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                info = proc.info
                if self._is_suspicious_process(info, patterns):
                    return {
                        "pid": info.get("pid"),
                        "name": info.get("name"),
                        "cmdline": info.get("cmdline"),
                        "threat_level": "HIGH",
                    }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return None

    def monitor_network(self) -> Optional[Dict[str, Any]]:
        """Monitor network connections for suspicious activity (synchronous version)."""
        try:
            suspicious_ports = set(self.config["monitoring"]["network"].get("suspicious_ports", []))
            connections = psutil.net_connections(kind="inet")
            for conn in connections:
                remote = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "unknown"
                local = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "unknown"
                if self._is_suspicious_connection(remote, suspicious_ports):
                    return {
                        "local": local,
                        "remote": remote,
                        "threat_level": "HIGH",
                    }
        except Exception:
            pass
        return None

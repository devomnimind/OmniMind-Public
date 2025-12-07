"""Response playbook for suspicious port detection."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

from .utils import (
    CommandResult,
    command_available,
    run_command_async,
    skipped_command,
)

logger = logging.getLogger(__name__)

# Whitelist de IPs/hosts que podem ter portas suspeitas (gateway, serviços conhecidos)
WHITELIST_IPS: Set[str] = {"192.168.1.1", "127.0.0.1", "localhost"}
WHITELIST_PREFIXES: List[str] = ["192.168.1."]

# Portas conhecidas do OmniMind (não bloquear)
OMNIMIND_PORTS: Set[int] = {8000, 8080, 3000, 3001, 6333, 6379}


class SuspiciousPortPlaybook:
    """Automates investigation, blocking, and documentation of suspicious ports."""

    async def execute(self, agent: Any, event: Any) -> Dict[str, Any]:
        """
        Execute playbook for suspicious port response.

        Steps:
        1. Investigate port legitimacy
        2. Check if port is in whitelist
        3. Block port if not legitimate
        4. Document action
        5. Notify user
        """
        event_type = getattr(event, "event_type", "suspicious_port")
        logger.info("🚨 [SUSPICIOUS_PORT] response start for %s", event_type)

        # Extract port and IP from event
        port, ip = self._extract_port_and_ip(event)

        if not port:
            logger.warning("No port found in event, skipping playbook")
            return {
                "status": "skipped",
                "reason": "No port found in event",
            }

        # Verificar IP uma única vez no início
        if not ip:
            logger.error("IP não fornecido")
            return {"status": "error", "reason": "IP não fornecido"}

        # A partir daqui, ip é garantidamente str (type narrowing)
        assert ip is not None  # Para ajudar o type checker

        # Step 1: Investigate port legitimacy
        investigation = await self._investigate_port_legitimacy(port, ip)

        # Step 2: Check whitelist
        is_whitelisted = self._check_whitelist(ip, port)

        # Step 3: Block port if not legitimate and not whitelisted
        block_result = None
        if not investigation["is_legitimate"] and not is_whitelisted:
            block_result = await self._block_port(port)
        else:
            logger.info(
                "Port %d on %s is legitimate or whitelisted, skipping block",
                port,
                ip,
            )

        # Step 4: Document action
        documentation = await self._document_action(event, port, ip, investigation, block_result)

        # Step 5: Notify user
        notification = await self._notify_user(event, port, ip, investigation, block_result)

        return {
            "status": "completed",
            "port": port,
            "ip": ip,
            "investigation": investigation,
            "is_whitelisted": is_whitelisted,
            "block": block_result,
            "documentation": documentation,
            "notification": notification,
        }

    def _extract_port_and_ip(self, event: Any) -> tuple[int | None, str | None]:
        """Extract port and IP from event details."""
        details = getattr(event, "details", {}) or {}
        if isinstance(details, dict):
            # Try to get from new_ports or suspicious_ports
            new_ports = details.get("new_ports", [])
            suspicious_ports = details.get("suspicious_ports", [])
            ports = new_ports or suspicious_ports
            if ports:
                port = ports[0] if isinstance(ports, list) else int(ports)
            else:
                # Try to extract from description
                description = getattr(event, "description", "")
                if "port" in description.lower():
                    # Try to extract port number from description
                    import re

                    port_match = re.search(r"port[:\s]+(\d+)", description, re.IGNORECASE)
                    if port_match:
                        port = int(port_match.group(1))
                    else:
                        port = None
                else:
                    port = None

            # Get IP from source_ip or details
            ip = details.get("source_ip") or getattr(event, "source_ip", None) or "unknown"
        else:
            port = None
            ip = None

        return port, ip

    async def _investigate_port_legitimacy(self, port: int, ip: str) -> Dict[str, Any]:
        """
        Investigate if port is legitimate.

        Checks:
        1. Is port used by local process?
        2. Is port used by OmniMind service?
        3. Is port in whitelist?
        """
        logger.debug("   [1/5] Investigating port legitimacy: %d on %s", port, ip)

        investigation = {
            "port": port,
            "ip": ip,
            "is_legitimate": False,
            "is_local_process": False,
            "is_omnimind_service": False,
            "process_info": None,
        }

        # Check if port is used by local process
        try:
            result = await run_command_async(["/usr/bin/lsof", "-i", f":{port}"])
            if result["returncode"] == 0 and result["output"]:
                investigation["is_local_process"] = True
                investigation["process_info"] = result["output"]
                investigation["is_legitimate"] = True
                logger.info("Port %d is used by local process", port)
        except Exception as e:
            logger.debug("Error checking local process: %s", e)

        # Check if port is used by OmniMind
        if port in OMNIMIND_PORTS:
            investigation["is_omnimind_service"] = True
            investigation["is_legitimate"] = True
            logger.info("Port %d is an OmniMind service port", port)

        # Check if port is in whitelist
        if self._check_whitelist(ip, port):
            investigation["is_legitimate"] = True
            logger.info("Port %d on %s is whitelisted", port, ip)

        return investigation

    def _check_whitelist(self, ip: str, port: int) -> bool:
        """Check if IP/port is in whitelist."""
        if ip in WHITELIST_IPS:
            return True

        for prefix in WHITELIST_PREFIXES:
            if ip.startswith(prefix):
                # Gateway pode ter portas suspeitas, mas não bloqueamos
                return True

        return False

    async def _block_port(self, port: int) -> Dict[str, Any]:
        """
        Block port via iptables.

        Blocks:
        - INPUT TCP port
        - OUTPUT TCP port
        - INPUT UDP port
        - OUTPUT UDP port
        """
        logger.debug("   [2/5] Blocking port %d via iptables", port)

        if not command_available("iptables"):
            skipped = skipped_command("iptables", "tool unavailable")
            # Converter CommandResultWithStatus para dict
            return {
                "command": skipped["command"],
                "returncode": skipped["returncode"],
                "output": skipped["output"],
                "status": skipped.get("status", "skipped"),
                "reason": skipped.get("reason", "tool unavailable"),
            }

        results = {}

        # Block TCP INPUT
        cmd_tcp_input = [
            "sudo",
            "-n",
            "iptables",
            "-A",
            "INPUT",
            "-p",
            "tcp",
            "--dport",
            str(port),
            "-j",
            "DROP",
        ]
        if _is_command_safe(cmd_tcp_input):
            results["tcp_input"] = await run_command_async(cmd_tcp_input)
        else:
            results["tcp_input"] = skipped_command("iptables INPUT TCP", "command not safe")

        # Block TCP OUTPUT
        cmd_tcp_output = [
            "sudo",
            "-n",
            "iptables",
            "-A",
            "OUTPUT",
            "-p",
            "tcp",
            "--dport",
            str(port),
            "-j",
            "DROP",
        ]
        if _is_command_safe(cmd_tcp_output):
            results["tcp_output"] = await run_command_async(cmd_tcp_output)
        else:
            results["tcp_output"] = skipped_command("iptables OUTPUT TCP", "command not safe")

        # Block UDP INPUT
        cmd_udp_input = [
            "sudo",
            "-n",
            "iptables",
            "-A",
            "INPUT",
            "-p",
            "udp",
            "--dport",
            str(port),
            "-j",
            "DROP",
        ]
        if _is_command_safe(cmd_udp_input):
            results["udp_input"] = await run_command_async(cmd_udp_input)
        else:
            results["udp_input"] = skipped_command("iptables INPUT UDP", "command not safe")

        # Block UDP OUTPUT
        cmd_udp_output = [
            "sudo",
            "-n",
            "iptables",
            "-A",
            "OUTPUT",
            "-p",
            "udp",
            "--dport",
            str(port),
            "-j",
            "DROP",
        ]
        if _is_command_safe(cmd_udp_output):
            results["udp_output"] = await run_command_async(cmd_udp_output)
        else:
            results["udp_output"] = skipped_command("iptables OUTPUT UDP", "command not safe")

        # Verify blocking
        verification = await self._verify_blocking(port)
        # verification é dict, não CommandResult
        results["verification"] = verification  # type: ignore[assignment]

        return results

    async def _verify_blocking(self, port: int) -> Dict[str, Any]:
        """Verify that port blocking was successful."""
        logger.debug("   [3/5] Verifying port blocking: %d", port)

        if not command_available("iptables"):
            return {"status": "skipped", "reason": "iptables not available"}

        try:
            result = await run_command_async(["sudo", "-n", "iptables", "-L", "-n"])
            if result["returncode"] == 0:
                # Check if port appears in iptables rules
                rules = result.get("output", "")
                port_in_rules = str(port) in rules and "DROP" in rules
                return {
                    "status": "verified" if port_in_rules else "not_found",
                    "port_in_rules": port_in_rules,
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}

        return {"status": "unknown"}

    async def _document_action(
        self,
        event: Any,
        port: int,
        ip: str,
        investigation: Dict[str, Any],
        block_result: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        """Document security action."""
        logger.debug("   [4/5] Documenting security action")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        doc_dir = Path("/opt/omnimind/security_logs")
        doc_dir.mkdir(parents=True, exist_ok=True)
        doc_path = doc_dir / f"suspicious_port_{port}_{timestamp}.json"

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": getattr(event, "event_type", "suspicious_port"),
            "port": port,
            "ip": ip,
            "investigation": investigation,
            "block_result": block_result,
            "event_details": getattr(event, "details", {}),
            "description": getattr(event, "description", ""),
        }

        try:
            await asyncio.to_thread(self._write_documentation, doc_path, payload)
            return {"path": str(doc_path), "status": "documented"}
        except Exception as e:
            logger.error("Failed to document action: %s", e)
            return {"path": None, "status": "error", "error": str(e)}

    @staticmethod
    def _write_documentation(path: Path, payload: Dict[str, Any]) -> None:
        """Write documentation to file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    async def _notify_user(
        self,
        event: Any,
        port: int,
        ip: str,
        investigation: Dict[str, Any],
        block_result: Dict[str, Any] | None,
    ) -> CommandResult:
        """Notify user about security action."""
        logger.debug("   [5/5] Notifying user")

        if block_result:
            message = (
                f"🔒 [AUTONOMOUS SECURITY] Port {port} on {ip} blocked automatically. "
                f"Investigation: {investigation.get('is_legitimate', False)}"
            )
        else:
            is_legit = investigation.get("is_legitimate", False)
            message = (
                f"⚠️  [SECURITY ALERT] Port {port} on {ip} detected but not blocked "
                f"(legitimate or whitelisted). Investigation: {is_legit}"
            )

        logger.info(message)
        result = await run_command_async(["/bin/echo", message])  # noqa: E501
        # Converter CommandResult para dict compatível
        if isinstance(result, dict):
            # Se já é dict, garantir que tem as chaves necessárias
            if "command" in result and "returncode" in result and "output" in result:
                return result  # type: ignore[return-value]
            # Se não tem, criar CommandResult válido
            return {
                "command": "/bin/echo",
                "returncode": result.get("returncode", 0),
                "output": result.get("output", message),
            }
        # Se for objeto, converter
        if hasattr(result, "command"):
            return {
                "command": result.command,
                "returncode": result.returncode,
                "output": result.output,
            }
        # Fallback
        return {
            "command": "/bin/echo",
            "returncode": 0,
            "output": message,
        }


def _is_command_safe(command: List[str]) -> bool:
    """Check if iptables command is safe."""
    from .utils import is_command_safe as check_safe

    return check_safe(command)

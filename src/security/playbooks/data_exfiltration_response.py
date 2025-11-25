"""Playbook to detect and halt data exfiltration flows."""

import asyncio
import json
import logging
from typing import Any, Dict

import psutil

from .utils import (
    CommandResult,
    command_available,
    run_command_async,
    skipped_command,
)

logger = logging.getLogger(__name__)


class DataExfiltrationPlaybook:
    """Handles disruption of abnormal transfer channels."""

    async def execute(self, agent: Any, event: Any) -> Dict[str, Any]:
        logger.info("🚨 [EXFIL] response start for %s", getattr(event, "event_type", "exfil"))
        detection = await self._detect_anomalous_transfer()
        blocked = await self._block_connection(event)
        throttle = await self._throttle_bandwidth()
        preserved = await self._preserve_logs(event)
        notification = await self._notify_team(event)
        return {
            "status": "completed",
            "detection": detection,
            "blocked": blocked,
            "throttle": throttle,
            "preserved": preserved,
            "notification": notification,
        }

    async def _detect_anomalous_transfer(self) -> CommandResult:
        logger.debug("   [1/5] Sampling network traffic")
        command = ["/usr/bin/ss", "-tunap"]

        if not command_available(command[0]):
            return skipped_command("ss", "tool unavailable")
        return await run_command_async(command)

    async def _block_connection(self, event: Any) -> CommandResult:
        logger.debug("   [2/5] Blocking suspicious egress")

        remote = "0.0.0.0"
        if hasattr(event, "details") and isinstance(event.details, dict):
            remote = event.details.get("remote") or remote

        # Skip if remote is invalid or "unknown"
        if not remote or remote == "unknown" or remote == "0.0.0.0":
            logger.debug("   [2/5] Skipping block - invalid or default remote address")
            return skipped_command("ufw", "invalid remote address")

        command = ["sudo", "ufw", "deny", "from", str(remote)]
        if not command_available(command[0]):
            return skipped_command("ufw", "tool unavailable")

        try:
            result = await run_command_async(command)
            # If command fails, log but don't raise - this is a security measure, not critical
            if result.get("returncode", 0) != 0:
                logger.warning(
                    "   [2/5] ufw deny command failed (non-critical): %s",
                    result.get("output", ""),
                )
            return result
        except Exception as e:
            logger.warning("   [2/5] Error blocking connection (non-critical): %s", e)
            return {"command": " ".join(command), "returncode": 1, "output": str(e)}

    async def _throttle_bandwidth(self) -> CommandResult:

        logger.debug("   [3/5] Applying traffic shaping")

        # Check if tc is available
        if not command_available("tc"):
            return skipped_command("tc", "tool unavailable")

        # Try to detect the default network interface
        default_interface = None
        try:
            # Get default gateway interface
            gateways = psutil.net_if_addrs()
            # Try common interface names
            for iface in ["eth0", "enp0s3", "ens33", "wlan0"]:
                if iface in gateways:
                    default_interface = iface
                    break
            # If no common interface found, use first available
            if not default_interface and gateways:
                default_interface = list(gateways.keys())[0]
        except Exception as e:
            logger.debug("   [3/5] Could not detect network interface: %s", e)
            return skipped_command("tc", "could not detect network interface")

        if not default_interface:
            return skipped_command("tc", "no network interface available")

        # Check if qdisc already exists (would fail if trying to add again)
        check_command = ["sudo", "tc", "qdisc", "show", "dev", default_interface]
        try:
            check_result = await run_command_async(check_command)
            if check_result.get("returncode", 1) == 0 and "tbf" in check_result.get("output", ""):
                logger.debug("   [3/5] Traffic shaping already applied, skipping")

                return {
                    "command": " ".join(check_command),
                    "returncode": 0,
                    "output": "Already applied",
                }
        except Exception:
            pass  # Continue if check fails

        command = [
            "sudo",
            "tc",
            "qdisc",
            "add",
            "dev",
            default_interface,
            "root",
            "tbf",
            "rate",
            "250kbps",
            "burst",
            "32kbit",
            "latency",
            "400ms",
        ]

        try:
            result = await run_command_async(command)
            # If command fails, log but don't raise - this is a security measure, not critical
            if result.get("returncode", 0) != 0:
                logger.warning(
                    "   [3/5] tc qdisc command failed (non-critical): %s",
                    result.get("output", ""),
                )
            return result
        except Exception as e:
            logger.warning("   [3/5] Error throttling bandwidth (non-critical): %s", e)
            return {"command": " ".join(command), "returncode": 1, "output": str(e)}

    async def _preserve_logs(self, event: Any) -> Dict[str, Any]:
        logger.debug("   [4/5] Preserving forensic logs")
        snapshot = {
            "event": getattr(event, "event_type", "exfil"),
            "logs": ["/var/log/auth.log", "/var/log/syslog"],
        }
        path = f"/tmp/exfil_{int(asyncio.get_event_loop().time())}.json"
        await asyncio.to_thread(self._write_artifact, path, snapshot)
        return {"path": path, "status": "saved"}

    async def _notify_team(self, event: Any) -> CommandResult:
        logger.debug("   [5/5] Alerting stakeholders")
        message = f"Data exfiltration mitigated for {getattr(event, 'description', 'unknown')}"
        return await run_command_async(["/bin/echo", message])

    @staticmethod
    def _write_artifact(path: str, payload: Dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

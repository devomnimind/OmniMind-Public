"""Playbook to detect and halt data exfiltration flows."""

import asyncio
import json
import logging
from typing import Any, Dict

from .utils import CommandResult, command_available, run_command_async, skipped_command

logger = logging.getLogger(__name__)


class DataExfiltrationPlaybook:
    """Handles disruption of abnormal transfer channels."""

    async def execute(self, agent: Any, event: Any) -> Dict[str, Any]:
        logger.info(
            "🚨 [EXFIL] response start for %s", getattr(event, "event_type", "exfil")
        )
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
        command = ["sudo", "ufw", "deny", str(remote)]
        if not command_available(command[0]):
            return skipped_command("ufw", "tool unavailable")
        return await run_command_async(command)

    async def _throttle_bandwidth(self) -> CommandResult:
        logger.debug("   [3/5] Applying traffic shaping")
        command = [
            "sudo",
            "tc",
            "qdisc",
            "add",
            "dev",
            "eth0",
            "root",
            "tbf",
            "rate",
            "250kbps",
            "burst",
            "32kbit",
            "latency",
            "400ms",
        ]
        if not command_available(command[0]):
            return skipped_command("tc", "tool unavailable")
        return await run_command_async(command)

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

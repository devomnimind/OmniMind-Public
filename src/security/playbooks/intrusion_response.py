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

"""Response playbook for intrusion detection."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from .utils import (
    CommandResult,
    command_available,
    run_command_async,
    skipped_command,
)

logger = logging.getLogger(__name__)


class IntrusionPlaybook:
    """Automates evidence collection, containment, and escalation."""

    async def execute(self, agent: Any, event: Any) -> Dict[str, Any]:
        event_type = getattr(event, "event_type", "intrusion")
        logger.info("🚨 [INTRUSION] response start for %s", event_type)
        evidence = await self._capture_evidence()
        block = await self._block_attacker(event)
        termination = await self._terminate_suspicious_sessions()
        enhanced_logging = await self._enhance_logging()
        alert = await self._alert_user(event)
        scene = await self._preserve_incident_scene(event, evidence)
        return {
            "status": "completed",
            "evidence": evidence,
            "block": block,
            "termination": termination,
            "logging": enhanced_logging,
            "alert": alert,
            "scene": scene,
        }

    async def _capture_evidence(self) -> Dict[str, CommandResult]:
        logger.debug("   [1/6] Capturing process/network evidence")
        commands = [
            ["/usr/bin/ps", "aux"],
            ["/usr/bin/ss", "-tna"],
            ["/usr/bin/lsof", "-i"],
            ["/usr/bin/w"],
            ["/bin/bash", "-lc", "history"],
        ]
        evidence: Dict[str, Any] = {}
        for command in commands:
            command_key = " ".join(command)
            if not command_available(command[0]):
                evidence[command_key] = skipped_command(command_key, "tool unavailable")
                continue
            evidence[command_key] = await run_command_async(command)
        return evidence

    async def _block_attacker(self, event: Any) -> CommandResult:
        logger.debug("   [2/6] Blocking attacker at firewall")
        remote = (
            event.details.get("remote")
            if hasattr(event, "details") and isinstance(event.details, dict)
            else None
        )
        remote = remote or event.details.get("source") if hasattr(event, "details") else "unknown"
        remote = remote or "0.0.0.0"
        command = ["sudo", "-n", "ufw", "deny", "from", str(remote)]
        if not command_available(command[0]):
            return skipped_command("ufw", "tool unavailable")
        return await run_command_async(command)

    async def _terminate_suspicious_sessions(self) -> CommandResult:
        logger.debug("   [3/6] Terminating suspicious sessions")
        command = ["sudo", "-n", "pkill", "-f", "nmap"]
        if not command_available(command[0]):
            return skipped_command("pkill", "tool unavailable")
        return await run_command_async(command)

    async def _enhance_logging(self) -> CommandResult:
        logger.debug("   [4/6] Boosting audit logs")
        command = ["sudo", "-n", "auditctl", "-b", "8192"]
        if not command_available(command[0]):
            return skipped_command("auditctl", "tool unavailable")
        return await run_command_async(command)

    async def _alert_user(self, event: Any) -> CommandResult:
        logger.debug("   [5/6] Sending user alert")
        description = getattr(event, "description", "intrusion detected")
        message = f"Intrusion alert: {description}"
        return await run_command_async(["/bin/echo", message])

    async def _preserve_incident_scene(
        self, event: Any, evidence: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.debug("   [6/6] Preserving incident artifacts")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        path = f"/tmp/intrusion_{timestamp}.json"
        payload = {
            "event": getattr(event, "event_type", "intrusion"),
            "captured_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "evidence": evidence,
        }
        await asyncio.to_thread(self._write_artifact, path, payload)
        return {"path": path, "size": len(json.dumps(payload))}

    @staticmethod
    def _write_artifact(path: str, payload: Dict[str, Any]) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

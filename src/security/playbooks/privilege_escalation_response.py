"""Playbook to mitigate privilege escalation attempts."""

import logging
from typing import Any, Dict

from .utils import CommandResult, command_available, run_command_async, skipped_command

logger = logging.getLogger(__name__)


class PrivilegeEscalationPlaybook:
    """Detects and remediates privilege escalation tools."""

    async def execute(self, agent: Any, event: Any) -> Dict[str, Any]:
        logger.info(
            "🚨 [PRIVESC] response start for %s",
            getattr(event, "event_type", "privesc"),
        )
        detection = await self._detect_exploit_attempts()
        blocker = await self._block_malicious_processes()
        permissions = await self._reset_sudoers_permissions()
        revocation = await self._revoke_sudo_sessions(event)
        audit = await self._audit_sudoers()
        notification = await self._notify_admin(event)
        return {
            "status": "completed",
            "detection": detection,
            "block": blocker,
            "permissions": permissions,
            "revocation": revocation,
            "audit": audit,
            "notification": notification,
        }

    async def _detect_exploit_attempts(self) -> CommandResult:
        logger.debug("   [1/6] Scanning logs for escalation attempts")
        command = ["/usr/bin/grep", "-i", "escalation", "/var/log/auth.log"]
        if not command_available(command[0]):
            return skipped_command("grep", "tool unavailable")
        return await run_command_async(command)

    async def _block_malicious_processes(self) -> CommandResult:
        logger.debug("   [2/6] Killing suspect escalation processes")
        command = ["sudo", "-n", "pkill", "-f", "exploit"]
        if not command_available(command[0]):
            return skipped_command("pkill", "tool unavailable")
        return await run_command_async(command)

    async def _reset_sudoers_permissions(self) -> CommandResult:
        logger.debug("   [3/6] Resetting /etc/sudoers permissions")
        command = ["sudo", "-n", "chmod", "440", "/etc/sudoers"]
        if not command_available(command[0]):
            return skipped_command("chmod", "tool unavailable")
        return await run_command_async(command)

    async def _revoke_sudo_sessions(self, event: Any) -> CommandResult:
        logger.debug("   [4/6] Revoking active sudo sessions")
        user = None
        if hasattr(event, "details") and isinstance(event.details, dict):
            user = event.details.get("user")
        if not user:
            return skipped_command("pkill", "no user provided")
        command = ["sudo", "-n", "pkill", "-KILL", "-u", user]
        if not command_available(command[0]):
            return skipped_command("pkill", "tool unavailable")
        return await run_command_async(command)

    async def _audit_sudoers(self) -> CommandResult:
        logger.debug("   [5/6] Auditing sudoers for unauthorized changes")

        command = ["sudo", "-n", "auditctl", "-w", "/etc/sudoers", "-p", "wa"]
        if not command_available(command[0]):
            return skipped_command("auditctl", "tool unavailable")

        try:
            result = await run_command_async(command)
            # If command fails, log but don't raise - auditctl may not be available or configured
            if result.get("returncode", 0) != 0:
                logger.debug(
                    "   auditctl command failed (non-critical, auditd may not be running): %s",
                    result.get("output", ""),
                )
            return result
        except Exception as e:
            logger.debug("   Error setting audit watch (non-critical): %s", e)
            return {"command": " ".join(command), "returncode": 1, "output": str(e)}

    async def _notify_admin(self, event: Any) -> CommandResult:
        logger.debug("   [6/6] Alerting administrators")
        message = f"Privilege escalation detected: {getattr(event, 'description', 'unknown')}"
        return await run_command_async(["/bin/echo", message])

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

"""Playbook that handles rootkit detection and isolation."""

import logging
from typing import Any, Dict

from .utils import CommandResult, command_available, run_command_async

logger = logging.getLogger(__name__)


class RootkitPlaybook:
    """Handles containment, scanning, and remediation for rootkits."""

    async def execute(self, agent: Any, event: Any) -> Dict[str, Any]:
        logger.info(
            "🚨 [ROOTKIT] response start for %s",
            getattr(event, "event_type", "unknown"),
        )
        await self._isolate_system()
        findings = await self._run_forensic_scans()
        analysis = await self._analyze_scans(findings)
        if analysis["has_rootkit"]:
            await self._remediate_rootkit()
        verification = await self._verify_remediation()
        return {
            "status": "completed",
            "analysis": analysis,
            "verification": verification,
        }

    async def _isolate_system(self) -> CommandResult:
        logger.debug("   [1/5] Isolating network interfaces")
        return await run_command_async(["sudo", "-n", "ifdown", "eth0"])

    async def _run_forensic_scans(self) -> Dict[str, str]:
        logger.debug("   [2/5] Running chkrootkit/rkhunter/lynis")
        results: Dict[str, str] = {}
        commands = [
            ("chkrootkit", ["sudo", "-n", "chkrootkit"]),
            (
                "rkhunter",
                ["sudo", "-n", "rkhunter", "--check", "--skip-keypress", "--quiet"],
            ),
            ("lynis", ["sudo", "-n", "lynis", "audit", "system", "--quiet"]),
        ]
        for name, command in commands:
            if not command_available(command[0]):
                results[name] = "tool unavailable"
                continue
            results[name] = (await run_command_async(command))["output"]
        return results

    async def _analyze_scans(self, findings: Dict[str, str]) -> Dict[str, Any]:
        logger.debug("   [3/5] Analyzing scan outputs")
        has_rootkit = any(
            "INFECTED" in value.upper() for value in findings.values() if isinstance(value, str)
        )
        return {"has_rootkit": has_rootkit, "findings": findings}

    async def _remediate_rootkit(self) -> CommandResult:
        logger.debug("   [4/5] Performing remediation")
        await run_command_async(["sudo", "-n", "apt-get", "update"])
        return await run_command_async(["sudo", "-n", "apt-get", "upgrade", "-y"])

    async def _verify_remediation(self) -> Dict[str, Any]:
        logger.debug("   [5/5] Verifying remediation via re-scan")
        findings = await self._run_forensic_scans()
        analysis = await self._analyze_scans(findings)
        if not analysis["has_rootkit"]:
            logger.info("✅ Rootkit remediation verified")
        else:
            logger.warning("❌ Rootkit still present after remediation")
        return analysis

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

"""Shared helpers for security playbook commands."""

import asyncio
import logging
import os
import shutil
import subprocess
from typing import Sequence, TypedDict

logger = logging.getLogger(__name__)


class CommandResult(TypedDict):
    command: str
    returncode: int
    output: str


class CommandResultWithStatus(CommandResult, total=False):
    status: str
    reason: str


def skipped_command(command: str, reason: str) -> CommandResultWithStatus:
    return {
        "command": command,
        "returncode": -1,
        "output": "",
        "status": "skipped",
        "reason": reason,
    }


def run_command(command: Sequence[str]) -> CommandResult:
    if not command or not shutil.which(command[0]):
        return {
            "command": " ".join(command) if command else "",
            "returncode": -1,
            "output": "command not available",
        }

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
        return {
            "command": " ".join(command),
            "returncode": result.returncode,
            "output": result.stdout.strip(),
        }
    except subprocess.CalledProcessError as exc:
        # Check for interactive fallback
        allow_interactive = os.environ.get("OMNIMIND_INTERACTIVE", "false").lower() == "true"
        is_sudo_non_interactive = command[0] == "sudo" and "-n" in command

        if allow_interactive and is_sudo_non_interactive and shutil.which("pkexec"):
            try:
                # Construct pkexec command (remove sudo and -n)
                real_cmd = [c for c in command if c not in ["sudo", "-n"]]
                pkexec_cmd = ["pkexec"] + real_cmd
                logger.info("Escalating to interactive pkexec for: %s", real_cmd)

                # Increase timeout for user interaction
                result = subprocess.run(
                    pkexec_cmd, capture_output=True, text=True, check=True, timeout=300
                )
                return {
                    "command": " ".join(pkexec_cmd),
                    "returncode": result.returncode,
                    "output": result.stdout.strip(),
                }
            except Exception as pk_exc:
                logger.warning("pkexec fallback failed: %s", pk_exc)

        logger.warning("Command %s failed: %s", command, exc)
        return {
            "command": " ".join(command),
            "returncode": exc.returncode,
            "output": exc.output or exc.stderr or "",
        }


async def run_command_async(command: Sequence[str]) -> CommandResult:
    return await asyncio.to_thread(run_command, command)


def command_available(command: str) -> bool:
    return shutil.which(command) is not None

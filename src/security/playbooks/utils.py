"""Shared helpers for security playbook commands."""

import asyncio
import logging
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

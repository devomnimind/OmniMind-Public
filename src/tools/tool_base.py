"""
Base classes for OmniMind Tools Framework.

This module contains the fundamental classes used by all tools,
separated to avoid circular import issues.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class ToolCategory(Enum):
    """Categories of tools in the framework."""

    PERCEPTION = "perception"
    ACTION = "action"
    ORCHESTRATION = "orchestration"
    INTEGRATION = "integration"
    MEMORY = "memory"
    SECURITY = "security"
    REASONING = "reasoning"
    PERSONALITY = "personality"
    FEEDBACK = "feedback"
    TELEMETRY = "telemetry"
    WORKFLOW = "workflow"


@dataclass
class ToolAuditLog:
    """Audited log entry for each tool execution with SHA-256 chain."""

    tool_name: str
    timestamp: str
    user: str
    action: str
    input_hash: str
    output_hash: str
    status: str
    error_msg: Optional[str] = None
    prev_hash: str = "0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditedTool:
    """Base class for all tools with P0 immutable auditing."""

    def __init__(self, name: str, category: ToolCategory):
        self.name = name
        self.category = category
        self.audit_log_path = Path.home() / ".omnimind" / "audit" / "tools.log"
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Get last hash from audit chain."""
        if self.audit_log_path.exists():
            try:
                with open(self.audit_log_path, "r") as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        return str(last_entry.get("output_hash", "0"))
            except (OSError, json.JSONDecodeError):
                return "0"
        return "0"

    def _compute_hash(self, content: Any) -> str:
        """Compute SHA-256 hash of content."""
        if isinstance(content, str):
            content = content.encode("utf-8")
        elif not isinstance(content, bytes):
            content = json.dumps(content, sort_keys=True, default=str).encode("utf-8")

        return hashlib.sha256(content).hexdigest()

    def _audit_action(
        self,
        action: str,
        input_data: Any,
        output_data: Any,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        """Record action in immutable audit chain."""
        input_hash = self._compute_hash(input_data)
        output_hash = self._compute_hash(output_data)

        audit_entry = ToolAuditLog(
            tool_name=self.name,
            timestamp=_current_utc_timestamp(),
            user=os.getenv("USER", "unknown"),
            action=action,
            input_hash=input_hash,
            output_hash=output_hash,
            status=status,
            error_msg=error,
            prev_hash=self.last_hash,
        )

        # Write to immutable log
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(audit_entry.to_dict()) + "\n")

            # Update last hash
            self.last_hash = output_hash

            logger.info(f"[AUDIT] {self.name}: {action} - Status: {status}")
        except Exception as e:
            logger.error(f"Failed to audit {self.name}: {e}")

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Abstract method - must be overridden by subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__}.{self.name}.execute() must be implemented"
        )

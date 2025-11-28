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

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..audit.immutable_audit import log_action


# Simple observability for DLP alerts (replaces DEVBRAIN_V23 import)
class AutonomyObservability:
    @staticmethod
    def record_dlp_alert(alert: dict[str, Any]) -> None:
        """Record DLP alert for observability."""
        logger.info("DLP Alert recorded", extra={"dlp_alert": alert})


autonomy_observability = AutonomyObservability()

logger = logging.getLogger(__name__)


def _current_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DLPPolicy:
    name: str
    pattern: str
    action: str
    severity: str = "medium"
    description: Optional[str] = None
    compiled: re.Pattern[str] = field(init=False)

    def __post_init__(self) -> None:
        flags = re.IGNORECASE
        self.compiled = re.compile(self.pattern, flags)


@dataclass
class DLPViolation:
    rule: str
    action: str
    severity: str
    snippet: str
    timestamp: str = field(default_factory=_current_iso)
    details: Dict[str, Any] = field(default_factory=dict)


class DLPViolationError(Exception):
    def __init__(self, violation: DLPViolation) -> None:
        super().__init__(f"DLP violation: {violation.rule} action={violation.action}")
        self.violation = violation


class DLPValidator:
    DEFAULT_POLICIES = [
        {
            "name": "credentials",
            "pattern": r"(api_key|secret|password|token)=\S{4,}",
            "action": "block",
            "severity": "high",
            "description": "Bloqueia vazamento de credenciais",
        },
        {
            "name": "internal_ip",
            "pattern": r"(192\.168|10\.|172\.(1[6-9]|2\d|3[0-1]))",
            "action": "alert",
            "severity": "medium",
            "description": "Detecta dados de rede interna",
        },
    ]

    def __init__(self, policy_path: Optional[str] = None) -> None:
        self.policy_path = Path(policy_path or "config/dlp_policies.yaml")
        self.policies = self._load_policies()

    def _load_policies(self) -> List[DLPPolicy]:
        if not self.policy_path.exists():
            logger.warning("DLP policy file missing %s, falling back to defaults", self.policy_path)
            return [DLPPolicy(**policy) for policy in self.DEFAULT_POLICIES]
        try:
            data = yaml.safe_load(self.policy_path.read_text()) or {}
            raw_policies = data.get("policies", [])
            if not isinstance(raw_policies, list):
                raise ValueError("policies must be a list")
            return [DLPPolicy(**policy) for policy in raw_policies]
        except Exception as exc:
            logger.error("Failed to load DLP policies: %s", exc)
            return [DLPPolicy(**policy) for policy in self.DEFAULT_POLICIES]

    def validate(self, payload: str) -> Optional[DLPViolation]:
        if not payload:
            return None
        for policy in self.policies:
            match = policy.compiled.search(payload)
            if match:
                snippet = match.group(0)
                violation = DLPViolation(
                    rule=policy.name,
                    action=policy.action,
                    severity=policy.severity,
                    snippet=snippet,
                    details={
                        "description": policy.description,
                        "payload_sample": payload[:200],
                    },
                )
                autonomy_observability.record_dlp_alert(violation.__dict__)
                log_action(
                    "dlp.violation",
                    {
                        "rule": violation.rule,
                        "action": violation.action,
                        "severity": violation.severity,
                        "snippet": violation.snippet,
                    },
                    category="security",
                )
                return violation
        return None

    def enforce(self, payload: str) -> Optional[DLPViolation]:
        violation = self.validate(payload)
        if violation and violation.action == "block":
            raise DLPViolationError(violation)
        return violation

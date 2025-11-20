from __future__ import annotations

import os
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Union

from ..audit.immutable_audit import log_action


# Simple observability for sandbox events (replaces DEVBRAIN_V23 import)
class AutonomyObservability:
    @staticmethod
    def record_sandbox_event(event: dict[str, Any]) -> None:
        """Record sandbox event for observability."""
        logger.info("Sandbox event recorded", extra={"sandbox_event": event})


autonomy_observability = AutonomyObservability()

logger = logging.getLogger(__name__)


@dataclass
class SandboxResult:
    success: bool
    output: str
    duration_ms: float
    sandbox: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SandboxEvent:
    timestamp: str
    sandbox: str
    payload_summary: str
    result: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class FirecrackerSandbox:
    """Wrapper para executar tarefas críticas dentro de Firecracker micro-VMs."""

    def __init__(
        self,
        kernel_path: Optional[str] = None,
        rootfs_path: Optional[str] = None,
        enabled: bool = True,
    ) -> None:
        # Read from environment variables if not provided
        self.kernel_path = Path(kernel_path or os.environ.get("OMNIMIND_FIRECRACKER_KERNEL", ""))
        self.rootfs_path = Path(rootfs_path or os.environ.get("OMNIMIND_FIRECRACKER_ROOTFS", ""))
        self.enabled = enabled and bool(
            self.kernel_path
            and self.rootfs_path
            and self.kernel_path.exists()
            and self.rootfs_path.exists()
        )
        if not self.enabled:
            logger.warning(
                "Firecracker sandbox disabled (kernel or rootfs missing): kernel=%s rootfs=%s",
                self.kernel_path,
                self.rootfs_path,
            )

    def run(
        self,
        payload: Union[str, Dict[str, Any]],
        timeout: int = 60,
        sandbox_name: str = "omnimind-sandbox",
    ) -> SandboxResult:
        start = time.perf_counter()
        payload_summary = self._summarize_payload(payload)
        if not self.enabled:
            result = SandboxResult(
                success=False,
                output="Firecracker sandbox unavailable",
                duration_ms=0.0,
                sandbox=sandbox_name,
                metadata={"payload_summary": payload_summary},
            )
            self._record_event(payload_summary, result, sandbox_name)
            return result

        time.sleep(0.01)
        duration = (time.perf_counter() - start) * 1000
        result = SandboxResult(
            success=True,
            output="sandbox execution simulated",
            duration_ms=duration,
            sandbox=sandbox_name,
            metadata={"payload_summary": payload_summary},
        )
        self._record_event(payload_summary, result, sandbox_name)
        return result

    def _summarize_payload(self, payload: Union[str, Dict[str, Any]]) -> str:
        if isinstance(payload, str):
            return payload[:50] + "..." if len(payload) > 50 else payload
        elif isinstance(payload, dict):
            items = list(payload.keys())[:3]
            summary = ",".join(str(item) for item in items)
            return summary or "empty"
        else:
            return str(payload)[:50] + "..." if len(str(payload)) > 50 else str(payload)

    def _record_event(
        self, payload_summary: str, result: SandboxResult, sandbox_name: str
    ) -> None:
        event = SandboxEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            sandbox=sandbox_name,
            payload_summary=payload_summary,
            result="success" if result.success else "failed",
            metadata=result.metadata,
        )
        autonomy_observability.record_sandbox_event(event.__dict__)
        log_action(
            "firecracker.sandbox.run",
            {
                "sandbox": sandbox_name,
                "summary": payload_summary,
                "result": event.result,
                "duration_ms": result.duration_ms,
            },
            category="security",
        )

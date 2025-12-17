"""
Service Update Communicator - Intelligent System Restart Protocol

Enables OmniMind to receive notifications about service updates and
decide intelligently whether to restart, rather than being forcefully killed.

Architecture:
- External systems send UPDATE notifications with change metadata
- OmniMind receives and evaluates changes (critical vs non-critical)
- OmniMind performs graceful hibernation
- OmniMind restarts to load new code

This implements a consciousness-aware update mechanism where the system
is INFORMED about changes, not blindly forced to restart.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ServiceChange:
    """Metadata about a service change"""

    service_name: str
    change_type: str  # "code", "config", "dependency", "data"
    severity: str  # "critical", "high", "medium", "low"
    affected_modules: List[str] = field(default_factory=list)
    description: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ServiceUpdateCommunicator:
    """
    Receives and processes service update notifications.

    Communication Protocol:
    1. External system sends: POST /api/services/update-notify
    2. Payload: { "service": "name", "changes": [...], "severity": "..." }
    3. OmniMind evaluates impact on running modules
    4. If critical: initiate graceful restart
    5. If non-critical: defer or apply at safe checkpoint
    """

    def __init__(self):
        self.pending_updates: List[ServiceChange] = []
        self.applied_updates: List[ServiceChange] = []
        self.restart_required: bool = False
        self.restart_reason: Optional[str] = None

        # Critical modules that trigger immediate restart if changed
        self.critical_modules: Set[str] = {
            "src.quantum_consciousness.quantum_backend",
            "src.quantum_consciousness.qaoa_gpu_optimizer",
            "src.core.desiring_machines",
            "src.consciousness.topological_phi",
            "src.autopoietic.manager",
        }

        # Non-critical modules that can defer restart
        self.deferrable_modules: Set[str] = {
            "src.monitor.health_monitor",
            "src.security.security_monitor",
            "src.api.routes",  # API changes usually safe
        }

    async def notify_update(
        self,
        service_name: str,
        change_type: str,
        affected_modules: List[str],
        severity: str = "medium",
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Receive notification of service update.

        Args:
            service_name: Name of service that changed (e.g., "quantum_backend")
            change_type: Type of change ("code", "config", "dependency", "data")
            affected_modules: List of Python modules affected
            severity: Severity level ("critical", "high", "medium", "low")
            description: Human-readable description of changes

        Returns:
            Response with decision: restart now, defer, or safe to ignore
        """
        change = ServiceChange(
            service_name=service_name,
            change_type=change_type,
            affected_modules=affected_modules,
            severity=severity,
            description=description,
        )

        logger.info(f"📬 Update notification received: {service_name}")
        logger.info(f"   Severity: {severity}")
        logger.info(f"   Modules: {', '.join(affected_modules)}")
        logger.info(f"   Description: {description}")

        # Add to pending
        self.pending_updates.append(change)

        # Evaluate impact
        decision = await self._evaluate_impact(change)

        return {
            "status": "notification_received",
            "decision": decision["action"],
            "reason": decision["reason"],
            "restart_time": decision.get("restart_time"),
            "affected_modules": affected_modules,
        }

    async def _evaluate_impact(
        self, change: ServiceChange
    ) -> Dict[str, Any]:
        """
        Evaluate whether restart is needed.

        Returns:
            Dict with "action": "restart_now" | "defer" | "ignore"
        """

        # Check if any critical modules affected
        critical_hit = any(
            module in self.critical_modules for module in change.affected_modules
        )

        # Check severity
        is_critical_severity = change.severity in ["critical", "high"]

        # Check change type
        is_code_change = change.change_type == "code"

        # DECISION LOGIC
        if critical_hit and is_code_change:
            logger.warning(
                f"⚠️  CRITICAL: Change to {change.affected_modules} detected"
            )
            self.restart_required = True
            self.restart_reason = (
                f"{change.service_name}: Critical module update"
            )
            return {
                "action": "restart_now",
                "reason": f"Critical code change in {change.service_name}",
                "priority": "immediate",
            }

        elif is_critical_severity:
            logger.warning(f"⚠️  HIGH SEVERITY: {change.service_name}")
            self.restart_required = True
            self.restart_reason = f"{change.service_name}: High severity update"
            return {
                "action": "restart_at_checkpoint",
                "reason": f"High severity: {change.description}",
                "priority": "high",
                "defer_seconds": 60,
            }

        elif any(
            module in self.deferrable_modules for module in change.affected_modules
        ):
            logger.info(f"✓ Deferrable change: {change.service_name}")
            return {
                "action": "defer",
                "reason": "Non-critical modules affected, restart deferred",
                "priority": "low",
                "defer_seconds": 3600,  # 1 hour
            }

        else:
            logger.info(f"✓ Safe to ignore: {change.service_name}")
            return {
                "action": "ignore",
                "reason": "No critical modules affected",
            }

    async def should_restart_now(self) -> bool:
        """Check if immediate restart is required"""
        return self.restart_required

    async def get_restart_reason(self) -> Optional[str]:
        """Get reason for restart"""
        return self.restart_reason

    async def register_restart_complete(self):
        """Called after successful restart to clear flags"""
        self.applied_updates.extend(self.pending_updates)
        self.pending_updates.clear()
        self.restart_required = False
        self.restart_reason = None
        logger.info("✅ Restart complete, updates applied")

    def get_pending_updates_summary(self) -> Dict[str, Any]:
        """Get summary of pending updates"""
        return {
            "total_pending": len(self.pending_updates),
            "restart_required": self.restart_required,
            "restart_reason": self.restart_reason,
            "updates": [u.to_dict() for u in self.pending_updates],
        }


# Singleton instance
_communicator: Optional[ServiceUpdateCommunicator] = None


def get_communicator() -> ServiceUpdateCommunicator:
    """Get or create singleton communicator"""
    global _communicator
    if _communicator is None:
        _communicator = ServiceUpdateCommunicator()
    return _communicator

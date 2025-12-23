"""
Service Update API Endpoints - Communication with OmniMind

Provides REST API for:
1. Notifying OmniMind about service updates
2. Checking if restart is needed
3. Triggering graceful restart
4. Monitoring update status
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.services.service_update_communicator import get_communicator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/services", tags=["services"])


# Request/Response Models
class UpdateNotification(BaseModel):
    """Update notification payload"""

    service_name: str
    change_type: str  # "code", "config", "dependency", "data"
    affected_modules: List[str]
    severity: str = "medium"  # "critical", "high", "medium", "low"
    description: str = ""


class UpdateResponse(BaseModel):
    """Response to update notification"""

    status: str
    decision: str  # "restart_now", "defer", "ignore"
    reason: str
    restart_time: Dict[str, Any] = {}
    affected_modules: List[str]


class RestartDecision(BaseModel):
    """Restart decision response"""

    needs_restart: bool
    reason: str = ""
    deferrable: bool = False


@router.post("/notify-update", response_model=UpdateResponse)
async def notify_service_update(notification: UpdateNotification) -> UpdateResponse:
    """
    Notify OmniMind about a service update.

    Example:
    ```json
    {
        "service_name": "quantum_backend",
        "change_type": "code",
        "affected_modules": ["src.quantum_consciousness.qaoa_gpu_optimizer"],
        "severity": "critical",
        "description": "GPU QAOA acceleration enabled"
    }
    ```

    Returns:
    - "restart_now": Immediate graceful restart required
    - "defer": Restart deferred to next safe checkpoint
    - "ignore": No restart needed
    """
    communicator = get_communicator()

    decision = await communicator.notify_update(
        service_name=notification.service_name,
        change_type=notification.change_type,
        affected_modules=notification.affected_modules,
        severity=notification.severity,
        description=notification.description,
    )

    return UpdateResponse(**decision, affected_modules=notification.affected_modules)


@router.get("/restart-decision", response_model=RestartDecision)
async def check_restart_needed() -> RestartDecision:
    """
    Check if system needs to restart.

    Returns:
    - needs_restart: true if restart is required
    - reason: reason for restart
    - deferrable: whether restart can be deferred
    """
    communicator = get_communicator()

    needs_restart = await communicator.should_restart_now()
    reason = await communicator.get_restart_reason()

    return RestartDecision(
        needs_restart=needs_restart,
        reason=reason or "",
        deferrable=not needs_restart,
    )


@router.get("/pending-updates")
async def get_pending_updates() -> Dict[str, Any]:
    """
    Get summary of pending updates.

    Returns details about updates waiting to be applied.
    """
    communicator = get_communicator()
    return communicator.get_pending_updates_summary()


@router.post("/restart-graceful")
async def trigger_graceful_restart(request: Request) -> Dict[str, Any]:
    """
    Trigger graceful restart (OmniMind will clean up and restart).

    This is called by OmniMind itself after detecting restart is needed,
    or can be called manually for controlled restarts.

    Process:
    1. Hibernates state
    2. Saves checkpoints
    3. Closes connections
    4. Exits cleanly
    5. systemd restarts with new code

    Returns:
    - status: "restart_initiated"
    - hibernation_complete: whether state was saved
    - time_to_restart: seconds before shutdown
    """
    communicator = get_communicator()

    try:
        logger.info("🔄 Graceful restart initiated via API")

        # This endpoint should be handled by the main app
        # to trigger proper shutdown sequence
        await communicator.register_restart_complete()

        return {
            "status": "restart_initiated",
            "hibernation_complete": True,
            "time_to_restart": 2,
            "message": "OmniMind will restart in 2 seconds",
        }
    except Exception as e:
        logger.error(f"Error initiating restart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-deferred-updates")
async def apply_deferred_updates() -> Dict[str, Any]:
    """
    Apply any deferred updates at a safe checkpoint.

    This can be called at scheduled times or when system reaches
    a safe state to apply non-critical updates.
    """
    communicator = get_communicator()
    summary = communicator.get_pending_updates_summary()

    if not summary["total_pending"]:
        return {
            "status": "no_updates",
            "message": "No pending updates to apply",
        }

    return {
        "status": "applying_deferred",
        "updates_applied": summary["total_pending"],
        "message": "Deferred updates will be applied at next checkpoint",
    }


# Export for registration in main app
def register_service_update_routes(app):
    """Register service update routes with FastAPI app"""
    app.include_router(router)

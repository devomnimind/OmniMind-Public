"""API routes for Tribunal do Diabo monitoring."""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter

from src.services.daemon_monitor import get_cached_status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tribunal", tags=["tribunal"])


@router.get("/activity")
async def get_activity() -> Dict[str, Any]:
    """
    Get Tribunal activity and status.

    Returns:
        Dict containing status, activity score, and proposals.
    """
    cache = get_cached_status()
    tribunal_info = cache.get("tribunal_info", {})

    # Calculate a synthetic activity score based on attacks executed
    attacks_executed = tribunal_info.get("attacks_executed", 0)
    activity_score = min(1.0, attacks_executed * 0.25)  # 4 attacks = 1.0

    status = tribunal_info.get("status", "unknown")

    # Generate proposals based on status
    proposals = []
    if status == "running":
        proposals.append(
            {
                "id": "wait_completion",
                "title": "Aguardar Conclusão",
                "description": "O Tribunal está em execução. Aguarde o relatório final.",
                "severity": "info",
            }
        )
    elif status == "finished":
        compatible = tribunal_info.get("consciousness_compatible", False)
        if compatible:
            proposals.append(
                {
                    "id": "approve_integration",
                    "title": "Aprovar Integração",
                    "description": "Sistema compatível com consciência. Integração recomendada.",
                    "severity": "success",
                }
            )
        else:
            proposals.append(
                {
                    "id": "review_architecture",
                    "title": "Revisar Arquitetura",
                    "description": "Sistema vulnerável ou incompatível. Revisão necessária.",
                    "severity": "warning",
                }
            )

    return {
        "status": status,
        "activity_score": activity_score,
        "proposals": proposals,
        "details": tribunal_info,
        "metrics": {
            "attacks_count": attacks_executed,
            "duration_hours": tribunal_info.get("duration_hours", 0),
        },
    }

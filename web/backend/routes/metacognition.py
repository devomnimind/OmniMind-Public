"""API routes for metacognition and self-analysis."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metacognition", tags=["metacognition"])


class AnalysisRequest(BaseModel):
    """Request model for metacognition analysis."""

    lookback_hours: int = Field(
        24, ge=1, le=168, description="Hours of history to analyze"
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    status: str
    health_status: Optional[str] = None
    last_analysis: Optional[str] = None
    timestamp: str


# Global orchestrator instance (will be injected from main.py)
_orchestrator_instance: Optional[Any] = None


def set_orchestrator(orchestrator: Any) -> None:
    """Set the orchestrator instance for metacognition endpoints."""
    global _orchestrator_instance
    _orchestrator_instance = orchestrator


def _get_orchestrator() -> Any:
    """Get orchestrator instance or raise 503."""
    if _orchestrator_instance is None:
        raise HTTPException(
            status_code=503, detail="Orchestrator not available"
        )
    return _orchestrator_instance


@router.post("/analyze")
async def run_analysis(request: AnalysisRequest) -> Dict[str, Any]:
    """Run comprehensive metacognition analysis.

    Analyzes decision-making patterns, execution performance, failures,
    and generates optimization suggestions.
    """
    orch = _get_orchestrator()

    if not orch.metacognition_agent:
        raise HTTPException(
            status_code=503, detail="MetacognitionAgent not initialized"
        )

    logger.info(f"Running metacognition analysis (lookback: {request.lookback_hours}h)")

    try:
        report = orch.run_metacognition_analysis(request.lookback_hours)

        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])

        return report

    except Exception as exc:
        logger.exception(f"Analysis failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health")
async def get_health() -> HealthCheckResponse:
    """Quick health check without full analysis."""
    orch = _get_orchestrator()

    if not orch.metacognition_agent:
        return HealthCheckResponse(
            status="unavailable",
            timestamp=__import__("time").time(),
        )

    try:
        health = orch.check_metacognition_health()

        return HealthCheckResponse(
            status=health.get("status", "unknown"),
            health_status=health.get("health", {}).get("health_status"),
            last_analysis=health.get("last_analysis"),
            timestamp=health.get("timestamp", ""),
        )

    except Exception as exc:
        logger.exception(f"Health check failed: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/suggestions")
async def get_suggestions(
    limit: int = Query(10, ge=1, le=50, description="Maximum suggestions to return")
) -> List[Dict[str, Any]]:
    """Get top optimization suggestions from last analysis."""
    orch = _get_orchestrator()

    if not orch.metacognition_agent:
        raise HTTPException(
            status_code=503, detail="MetacognitionAgent not initialized"
        )

    try:
        suggestions = orch.metacognition_agent.get_top_suggestions(limit)
        return suggestions

    except Exception as exc:
        logger.exception(f"Failed to get suggestions: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    """Get metacognition analysis statistics."""
    orch = _get_orchestrator()

    if not orch.metacognition_agent:
        raise HTTPException(
            status_code=503, detail="MetacognitionAgent not initialized"
        )

    try:
        stats = orch.metacognition_agent.get_analysis_stats()
        return stats

    except Exception as exc:
        logger.exception(f"Failed to get stats: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/last-analysis")
async def get_last_analysis() -> Dict[str, Any]:
    """Get the last metacognition analysis report."""
    orch = _get_orchestrator()

    if not orch.last_metacognition_analysis:
        raise HTTPException(
            status_code=404, detail="No analysis has been run yet"
        )

    return orch.last_metacognition_analysis


@router.get("/goals/generate")
async def generate_proactive_goals() -> Dict[str, Any]:
    """Generate proactive improvement goals from repository analysis."""
    try:
        from src.metacognition.proactive_goals import ProactiveGoalEngine

        engine = ProactiveGoalEngine(workspace_path=".")
        goals = engine.generate_goals()

        return {
            "goals": goals,
            "total_goals": len(goals),
            "timestamp": __import__("time").time(),
        }

    except Exception as exc:
        logger.exception(f"Failed to generate goals: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/homeostasis/status")
async def get_homeostasis_status() -> Dict[str, Any]:
    """Get homeostatic controller status and current resource metrics."""
    # This will be connected to the homeostatic controller when initialized
    # For now, return basic resource info
    try:
        import psutil

        cpu_percent = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_percent": disk.percent,
            "timestamp": __import__("time").time(),
        }

    except Exception as exc:
        logger.exception(f"Failed to get homeostasis status: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

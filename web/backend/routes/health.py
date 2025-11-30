"""
Advanced Health Check Routes for OmniMind.

Provides comprehensive health check endpoints with:
- Overall system health
- Individual component health
- Health trends and predictions
- Dependency status
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..monitoring.health_check_system import (
    HealthCheckResult,
    HealthCheckSystem,
    HealthStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Global health check system instance
health_system = HealthCheckSystem()


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    name: str
    dependency_type: str
    status: str
    response_time_ms: float
    details: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    timestamp: float
    threshold_breached: bool = False
    remediation_suggestion: Optional[str] = None


class OverallHealthResponse(BaseModel):
    """Overall system health response."""

    overall_status: str
    checks: Dict[str, HealthCheckResponse]
    timestamp: float
    total_checks: int
    healthy_count: int
    degraded_count: int
    unhealthy_count: int


class HealthTrendResponse(BaseModel):
    """Health trend analysis response."""

    check_name: str
    trend: str
    prediction: str
    health_score: float
    recent_statuses: Dict[str, int]
    avg_response_time_ms: float


@router.get("/", response_model=OverallHealthResponse)
async def get_overall_health() -> OverallHealthResponse:
    """
    Get overall system health status.

    Returns comprehensive health information for all monitored dependencies.
    """
    try:
        results = await health_system.run_all_checks()
        overall_status = health_system.get_overall_status(results)

        # Convert results to response format
        checks = {}
        healthy_count = 0
        degraded_count = 0
        unhealthy_count = 0

        for name, result in results.items():
            checks[name] = HealthCheckResponse(
                name=result.name,
                dependency_type=result.dependency_type.value,
                status=result.status.value,
                response_time_ms=result.response_time_ms,
                details=result.details,
                error=result.error,
                timestamp=result.timestamp,
                threshold_breached=result.threshold_breached,
                remediation_suggestion=result.remediation_suggestion,
            )

            if result.status == HealthStatus.HEALTHY:
                healthy_count += 1
            elif result.status == HealthStatus.DEGRADED:
                degraded_count += 1
            elif result.status == HealthStatus.UNHEALTHY:
                unhealthy_count += 1

        return OverallHealthResponse(
            overall_status=overall_status.value,
            checks=checks,
            timestamp=max(r.timestamp for r in results.values()) if results else 0,
            total_checks=len(results),
            healthy_count=healthy_count,
            degraded_count=degraded_count,
            unhealthy_count=unhealthy_count,
        )

    except Exception as e:
        logger.error(f"Error getting overall health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{check_name}", response_model=HealthCheckResponse)
async def get_specific_health(check_name: str) -> HealthCheckResponse:
    """
    Get health status for a specific component.

    Args:
        check_name: Name of the health check (e.g., 'database', 'redis', 'gpu')
    """
    try:
        # Map check names to methods
        check_methods = {
            "database": health_system.check_database,
            "redis": health_system.check_redis,
            "gpu": health_system.check_gpu,
            "filesystem": health_system.check_filesystem,
            "memory": health_system.check_memory,
            "cpu": health_system.check_cpu,
        }

        if check_name not in check_methods:
            raise HTTPException(
                status_code=404,
                detail=f"Health check '{check_name}' not found. Available: {list(check_methods.keys())}",
            )

        result = await check_methods[check_name]()

        return HealthCheckResponse(
            name=result.name,
            dependency_type=result.dependency_type.value,
            status=result.status.value,
            response_time_ms=result.response_time_ms,
            details=result.details,
            error=result.error,
            timestamp=result.timestamp,
            threshold_breached=result.threshold_breached,
            remediation_suggestion=result.remediation_suggestion,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking health for {check_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{check_name}/trend", response_model=HealthTrendResponse)
async def get_health_trend(
    check_name: str,
    window_size: int = 10,
) -> HealthTrendResponse:
    """
    Get health trend analysis for a specific component.

    Args:
        check_name: Name of the health check
        window_size: Number of recent results to analyze (default: 10)
    """
    try:
        trend_data = health_system.get_health_trends(check_name, window_size)

        if trend_data["trend"] == "unknown":
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient health data for '{check_name}'. Run health checks first.",
            )

        return HealthTrendResponse(
            check_name=check_name,
            trend=trend_data["trend"],
            prediction=trend_data["prediction"],
            health_score=trend_data["health_score"],
            recent_statuses=trend_data["recent_statuses"],
            avg_response_time_ms=trend_data["avg_response_time_ms"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting health trend for {check_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=Dict[str, Any])
async def get_health_summary() -> Dict[str, Any]:
    """
    Get health check system summary.

    Returns statistics about health monitoring.
    """
    try:
        return health_system.get_summary()
    except Exception as e:
        logger.error(f"Error getting health summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start-monitoring")
async def start_health_monitoring() -> Dict[str, str]:
    """Start continuous health monitoring."""
    try:
        await health_system.start_monitoring()
        return {
            "status": "started",
            "message": "Health monitoring started successfully",
        }
    except Exception as e:
        logger.error(f"Error starting health monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop-monitoring")
async def stop_health_monitoring() -> Dict[str, str]:
    """Stop continuous health monitoring."""
    try:
        await health_system.stop_monitoring()
        return {
            "status": "stopped",
            "message": "Health monitoring stopped successfully",
        }
    except Exception as e:
        logger.error(f"Error stopping health monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

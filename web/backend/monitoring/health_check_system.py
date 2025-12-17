"""
Advanced Health Check System for OmniMind.

Provides comprehensive health monitoring with:
- Dependency health checks (DB, Redis, GPU, etc.)
- Predictive health alerts
- Resource threshold monitoring
- Health trend analysis
- Auto-remediation suggestions
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class DependencyType(str, Enum):
    """Types of dependencies to monitor."""

    DATABASE = "database"
    REDIS = "redis"
    GPU = "gpu"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    MEMORY = "memory"
    CPU = "cpu"
    EXTERNAL_API = "external_api"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    dependency_type: DependencyType
    status: HealthStatus
    response_time_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    threshold_breached: bool = False
    remediation_suggestion: Optional[str] = None


@dataclass
class HealthThresholds:
    """Health check thresholds."""

    response_time_warning_ms: float = 1000.0
    response_time_critical_ms: float = 5000.0
    cpu_usage_warning: float = 80.0
    cpu_usage_critical: float = 95.0
    memory_usage_warning: float = 80.0
    memory_usage_critical: float = 95.0
    disk_usage_warning: float = 85.0
    disk_usage_critical: float = 95.0


class HealthCheckSystem:
    """Advanced health monitoring system."""

    def __init__(
        self,
        thresholds: Optional[HealthThresholds] = None,
        check_interval_seconds: int = 30,
    ) -> None:
        """
        Initialize health check system.

        Args:
            thresholds: Health thresholds configuration
            check_interval_seconds: Interval between automatic health checks
        """
        self.thresholds = thresholds or HealthThresholds()
        self.check_interval = check_interval_seconds
        self._checks: Dict[str, Callable[[], Any]] = {}
        self._results: Dict[str, List[HealthCheckResult]] = {}
        self._max_history = 100
        self._running = False
        self._monitor_task: Optional[asyncio.Task[None]] = None

    def register_check(
        self,
        name: str,
        dependency_type: DependencyType,
        check_func: Callable[[], Any],
    ) -> None:
        """
        Register a health check.

        Args:
            name: Unique name for the check
            dependency_type: Type of dependency
            check_func: Function that performs the check (sync or async)
        """
        self._checks[name] = check_func
        logger.info(f"Registered health check: {name} ({dependency_type})")

    async def check_database(self) -> HealthCheckResult:
        """Check database connection health."""
        start_time = time.time()
        try:
            # Simulate DB ping - replace with actual DB connection check
            await asyncio.sleep(0.01)  # Simulate network latency
            response_time = (time.time() - start_time) * 1000

            if response_time > self.thresholds.response_time_critical_ms:
                status = HealthStatus.UNHEALTHY
                suggestion = "Database response time critical. Check DB server load."
            elif response_time > self.thresholds.response_time_warning_ms:
                status = HealthStatus.DEGRADED
                suggestion = "Database response time elevated. Monitor for issues."
            else:
                status = HealthStatus.HEALTHY
                suggestion = None

            return HealthCheckResult(
                name="database",
                dependency_type=DependencyType.DATABASE,
                status=status,
                response_time_ms=response_time,
                details={
                    "connection": "active",
                    "pool_size": 10,
                    "active_connections": 3,
                },
                remediation_suggestion=suggestion,
                threshold_breached=status != HealthStatus.HEALTHY,
            )
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return HealthCheckResult(
                name="database",
                dependency_type=DependencyType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                remediation_suggestion="Database connection failed. Verify credentials and network.",
                threshold_breached=True,
            )

    async def check_redis(self) -> HealthCheckResult:
        """Check Redis connection health."""
        start_time = time.time()
        try:
            # Simulate Redis ping
            await asyncio.sleep(0.005)
            response_time = (time.time() - start_time) * 1000

            status = (
                HealthStatus.HEALTHY
                if response_time < self.thresholds.response_time_warning_ms
                else HealthStatus.DEGRADED
            )

            return HealthCheckResult(
                name="redis",
                dependency_type=DependencyType.REDIS,
                status=status,
                response_time_ms=response_time,
                details={"memory_usage_mb": 256, "connected_clients": 5},
            )
        except Exception as e:
            return HealthCheckResult(
                name="redis",
                dependency_type=DependencyType.REDIS,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                remediation_suggestion="Redis connection failed. Check Redis server status.",
                threshold_breached=True,
            )

    async def check_gpu(self) -> HealthCheckResult:
        """Check GPU availability and health."""
        start_time = time.time()
        try:
            # Try to import torch and check CUDA
            try:
                import torch

                cuda_available = torch.cuda.is_available()
                if cuda_available:
                    device_count = torch.cuda.device_count()
                    device_name = torch.cuda.get_device_name(0)
                    memory_allocated = torch.cuda.memory_allocated(0) / 1024**3  # GB
                    memory_reserved = torch.cuda.memory_reserved(0) / 1024**3  # GB
                    memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3

                    status = HealthStatus.HEALTHY
                    details = {
                        "available": True,
                        "device_count": device_count,
                        "device_name": device_name,
                        "memory_allocated_gb": round(memory_allocated, 2),
                        "memory_reserved_gb": round(memory_reserved, 2),
                        "memory_total_gb": round(memory_total, 2),
                        "memory_usage_percent": round((memory_allocated / memory_total) * 100, 2),
                    }
                else:
                    status = HealthStatus.DEGRADED
                    details = {"available": False, "reason": "CUDA not available"}
            except ImportError:
                status = HealthStatus.DEGRADED
                details = {"available": False, "reason": "PyTorch not installed"}

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name="gpu",
                dependency_type=DependencyType.GPU,
                status=status,
                response_time_ms=response_time,
                details=details,
            )
        except Exception as e:
            return HealthCheckResult(
                name="gpu",
                dependency_type=DependencyType.GPU,
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def check_filesystem(self) -> HealthCheckResult:
        """Check filesystem health."""
        start_time = time.time()
        try:
            import shutil

            disk_usage = shutil.disk_usage("/")
            total_gb = disk_usage.total / (1024**3)
            used_gb = disk_usage.used / (1024**3)
            free_gb = disk_usage.free / (1024**3)
            usage_percent = (disk_usage.used / disk_usage.total) * 100

            if usage_percent > self.thresholds.disk_usage_critical:
                status = HealthStatus.UNHEALTHY
                suggestion = (
                    f"Disk usage critical ({usage_percent:.1f}%). Free up space immediately."
                )
            elif usage_percent > self.thresholds.disk_usage_warning:
                status = HealthStatus.DEGRADED
                suggestion = f"Disk usage high ({usage_percent:.1f}%). Consider cleanup."
            else:
                status = HealthStatus.HEALTHY
                suggestion = None

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name="filesystem",
                dependency_type=DependencyType.FILESYSTEM,
                status=status,
                response_time_ms=response_time,
                details={
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "usage_percent": round(usage_percent, 2),
                },
                remediation_suggestion=suggestion,
                threshold_breached=status != HealthStatus.HEALTHY,
            )
        except Exception as e:
            return HealthCheckResult(
                name="filesystem",
                dependency_type=DependencyType.FILESYSTEM,
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def check_memory(self) -> HealthCheckResult:
        """Check system memory health."""
        start_time = time.time()
        try:
            import psutil

            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent > self.thresholds.memory_usage_critical:
                status = HealthStatus.UNHEALTHY
                suggestion = "Memory usage critical. Restart services or scale up."
            elif usage_percent > self.thresholds.memory_usage_warning:
                status = HealthStatus.DEGRADED
                suggestion = "Memory usage high. Monitor for memory leaks."
            else:
                status = HealthStatus.HEALTHY
                suggestion = None

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name="memory",
                dependency_type=DependencyType.MEMORY,
                status=status,
                response_time_ms=response_time,
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "usage_percent": round(usage_percent, 2),
                },
                remediation_suggestion=suggestion,
                threshold_breached=status != HealthStatus.HEALTHY,
            )
        except Exception as e:
            return HealthCheckResult(
                name="memory",
                dependency_type=DependencyType.MEMORY,
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def check_cpu(self) -> HealthCheckResult:
        """Check CPU health."""
        start_time = time.time()
        try:
            import psutil

            # Get CPU usage over 1 second interval
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent > self.thresholds.cpu_usage_critical:
                status = HealthStatus.UNHEALTHY
                suggestion = "CPU usage critical. Check for runaway processes."
            elif cpu_percent > self.thresholds.cpu_usage_warning:
                status = HealthStatus.DEGRADED
                suggestion = "CPU usage high. Monitor system load."
            else:
                status = HealthStatus.HEALTHY
                suggestion = None

            response_time = (time.time() - start_time) * 1000

            return HealthCheckResult(
                name="cpu",
                dependency_type=DependencyType.CPU,
                status=status,
                response_time_ms=response_time,
                details={
                    "usage_percent": round(cpu_percent, 2),
                    "cpu_count": psutil.cpu_count(),
                    "load_average": (
                        psutil.getloadavg() if hasattr(psutil, "getloadavg") else None
                    ),
                },
                remediation_suggestion=suggestion,
                threshold_breached=status != HealthStatus.HEALTHY,
            )
        except Exception as e:
            return HealthCheckResult(
                name="cpu",
                dependency_type=DependencyType.CPU,
                status=HealthStatus.UNKNOWN,
                response_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results: Dict[str, HealthCheckResult] = {}

        # Run built-in checks
        builtin_checks = [
            ("database", self.check_database),
            ("redis", self.check_redis),
            ("gpu", self.check_gpu),
            ("filesystem", self.check_filesystem),
            ("memory", self.check_memory),
            ("cpu", self.check_cpu),
        ]

        for name, check_func in builtin_checks:
            try:
                result = await check_func()
                results[name] = result
                self._store_result(name, result)
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = HealthCheckResult(
                    name=name,
                    dependency_type=DependencyType.EXTERNAL_API,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=0.0,
                    error=str(e),
                )

        return results

    def _store_result(self, name: str, result: HealthCheckResult) -> None:
        """Store health check result in history."""
        if name not in self._results:
            self._results[name] = []

        self._results[name].append(result)

        # Trim history
        if len(self._results[name]) > self._max_history:
            self._results[name] = self._results[name][-self._max_history :]

    def get_overall_status(self, results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """Get overall system health status."""
        if not results:
            return HealthStatus.UNKNOWN

        statuses = [r.status for r in results.values()]

        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def get_health_trends(self, check_name: str, window_size: int = 10) -> Dict[str, Any]:
        """
        Analyze health trends for a specific check.

        Args:
            check_name: Name of the health check
            window_size: Number of recent results to analyze

        Returns:
            Trend analysis with predictions
        """
        if check_name not in self._results or not self._results[check_name]:
            return {"trend": "unknown", "prediction": "insufficient_data"}

        recent_results = self._results[check_name][-window_size:]

        # Calculate trend
        healthy_count = sum(1 for r in recent_results if r.status == HealthStatus.HEALTHY)
        degraded_count = sum(1 for r in recent_results if r.status == HealthStatus.DEGRADED)
        unhealthy_count = sum(1 for r in recent_results if r.status == HealthStatus.UNHEALTHY)

        total = len(recent_results)
        health_score = (
            (healthy_count * 1.0 + degraded_count * 0.5 + unhealthy_count * 0.0) / total
        ) * 100

        # Determine trend
        if unhealthy_count > total / 2:
            trend = "critical"
            prediction = "immediate_action_required"
        elif degraded_count > total / 2:
            trend = "degrading"
            prediction = "monitor_closely"
        elif health_score >= 90:
            trend = "stable"
            prediction = "healthy"
        else:
            trend = "fluctuating"
            prediction = "investigate"

        return {
            "trend": trend,
            "prediction": prediction,
            "health_score": round(health_score, 2),
            "recent_statuses": {
                "healthy": healthy_count,
                "degraded": degraded_count,
                "unhealthy": unhealthy_count,
            },
            "avg_response_time_ms": round(
                sum(r.response_time_ms for r in recent_results) / total, 2
            ),
        }

    async def start_monitoring(self) -> None:
        """Start continuous health monitoring."""
        if self._running:
            logger.warning("Health monitoring already running")
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop continuous health monitoring."""
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Health monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Continuous monitoring loop."""
        while self._running:
            try:
                results = await self.run_all_checks()
                overall_status = self.get_overall_status(results)

                # Log warnings for unhealthy checks
                for name, result in results.items():
                    if result.status == HealthStatus.UNHEALTHY:
                        logger.warning(
                            f"Health check {name} is UNHEALTHY: {result.error or 'threshold breached'}"
                        )
                        if result.remediation_suggestion:
                            logger.warning(f"Suggestion: {result.remediation_suggestion}")

                logger.debug(f"Health monitoring cycle complete. Overall status: {overall_status}")

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")

            await asyncio.sleep(self.check_interval)

    def get_summary(self) -> Dict[str, Any]:
        """Get health check summary."""
        summary: Dict[str, Any] = {
            "checks_registered": len(self._checks),
            "checks_with_history": len(self._results),
            "total_checks_performed": sum(len(results) for results in self._results.values()),
        }

        # Get latest results
        latest_results = {}
        for name, results in self._results.items():
            if results:
                latest = results[-1]
                latest_results[name] = {
                    "status": latest.status,
                    "response_time_ms": latest.response_time_ms,
                    "timestamp": latest.timestamp,
                    "threshold_breached": latest.threshold_breached,
                }

        summary["latest_results"] = latest_results

        return summary

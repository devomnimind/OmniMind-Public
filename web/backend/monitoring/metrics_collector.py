"""Metrics collection system for API endpoints and system performance."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EndpointMetrics:
    """Metrics for a specific API endpoint."""

    path: str
    method: str = "GET"
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    min_latency: float = float("inf")
    max_latency: float = 0.0
    last_request: float = field(default_factory=time.time)


class MetricsCollector:
    """Collect and aggregate metrics for API endpoints and system performance."""

    def __init__(self) -> None:
        self._endpoint_metrics: Dict[str, EndpointMetrics] = {}
        self._request_history: List[Dict[str, Any]] = []
        self._max_history = 1000
        self._metrics_task: Optional[asyncio.Task[None]] = None
        self._running = False

    async def start(self) -> None:
        """Start metrics collection."""
        if self._running:
            return

        self._running = True
        self._metrics_task = asyncio.create_task(self._metrics_loop())
        logger.info("Metrics collector started")

    async def stop(self) -> None:
        """Stop metrics collection."""
        self._running = False
        if self._metrics_task:
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collector stopped")

    def record_request(
        self,
        path: str,
        method: str,
        latency: float,
        status_code: int,
        error: Optional[str] = None,
    ) -> None:
        """Record an API request with its metrics."""
        # Get or create endpoint metrics
        key = f"{method}:{path}"
        if key not in self._endpoint_metrics:
            self._endpoint_metrics[key] = EndpointMetrics(path=path, method=method)

        metrics = self._endpoint_metrics[key]
        metrics.total_requests += 1
        metrics.total_latency += latency
        metrics.last_request = time.time()

        # Update min/max latency
        metrics.min_latency = min(metrics.min_latency, latency)
        metrics.max_latency = max(metrics.max_latency, latency)

        # Track success/failure
        if 200 <= status_code < 400:
            metrics.successful_requests += 1
        else:
            metrics.failed_requests += 1

        # Add to request history
        self._request_history.append(
            {
                "timestamp": time.time(),
                "path": path,
                "method": method,
                "latency": latency,
                "status_code": status_code,
                "error": error,
            }
        )

        # Trim history if needed
        if len(self._request_history) > self._max_history:
            self._request_history = self._request_history[-self._max_history :]

    def get_endpoint_metrics(
        self, path: str, method: str = "GET"
    ) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific endpoint."""
        key = f"{method}:{path}"
        if key not in self._endpoint_metrics:
            return None

        metrics = self._endpoint_metrics[key]
        avg_latency = (
            metrics.total_latency / metrics.total_requests
            if metrics.total_requests > 0
            else 0.0
        )
        success_rate = (
            (metrics.successful_requests / metrics.total_requests * 100)
            if metrics.total_requests > 0
            else 0.0
        )

        return {
            "path": metrics.path,
            "method": metrics.method,
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "success_rate": round(success_rate, 2),
            "avg_latency": round(avg_latency, 4),
            "min_latency": round(metrics.min_latency, 4),
            "max_latency": round(metrics.max_latency, 4),
            "last_request": metrics.last_request,
        }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics for all endpoints."""
        total_requests = sum(m.total_requests for m in self._endpoint_metrics.values())
        total_successful = sum(
            m.successful_requests for m in self._endpoint_metrics.values()
        )
        total_failed = sum(m.failed_requests for m in self._endpoint_metrics.values())

        endpoints = []
        for key, metrics in self._endpoint_metrics.items():
            endpoint_data = self.get_endpoint_metrics(metrics.path, metrics.method)
            if endpoint_data:
                endpoints.append(endpoint_data)

        # Calculate overall success rate
        overall_success_rate = (
            (total_successful / total_requests * 100) if total_requests > 0 else 0.0
        )

        return {
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "failed_requests": total_failed,
            "success_rate": round(overall_success_rate, 2),
            "endpoints": endpoints,
            "timestamp": time.time(),
        }

    def get_recent_requests(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent request history."""
        return self._request_history[-limit:]

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors."""
        errors_by_path: Dict[str, int] = defaultdict(int)
        errors_by_code: Dict[int, int] = defaultdict(int)

        for request in self._request_history:
            if request.get("error") or request.get("status_code", 200) >= 400:
                errors_by_path[request["path"]] += 1
                errors_by_code[request.get("status_code", 500)] += 1

        return {
            "total_errors": sum(errors_by_path.values()),
            "errors_by_path": dict(errors_by_path),
            "errors_by_code": dict(errors_by_code),
        }

    async def _metrics_loop(self) -> None:
        """Background loop for metrics aggregation and cleanup."""
        while self._running:
            try:
                # Broadcast metrics update via WebSocket
                await self._broadcast_metrics()

                # Clean up old history entries (older than 1 hour)
                now = time.time()
                one_hour_ago = now - 3600
                self._request_history = [
                    r for r in self._request_history if r["timestamp"] >= one_hour_ago
                ]

            except Exception as exc:
                logger.exception(f"Error in metrics loop: {exc}")

            await asyncio.sleep(30)  # Update every 30 seconds

    async def _broadcast_metrics(self) -> None:
        """Broadcast metrics update via WebSocket."""
        from web.backend.websocket_manager import MessageType, ws_manager

        metrics = self.get_all_metrics()
        await ws_manager.broadcast(
            MessageType.METRICS,
            {
                "type": "api_metrics",
                "data": metrics,
            },
            channel="metrics",
        )


# Global metrics collector instance
metrics_collector = MetricsCollector()

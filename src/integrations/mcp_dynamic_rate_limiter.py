"""
Dynamic Rate Limiter for MCP Orchestration

Implements intelligent rate limiting that adapts to system health:
- Monitors CPU, memory, disk usage
- Adjusts RPS (requests per second) dynamically
- Prioritizes critical requests
- Cancels stale requests automatically
- Target: 500+ req/s with <200ms p99 latency
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class RequestPriority(Enum):
    """Request priority levels"""

    CRITICAL = 1  # Must execute (security, errors)
    HIGH = 2  # Important (core MCPs)
    NORMAL = 3  # Regular (utility MCPs)
    LOW = 4  # Non-urgent (optional)


@dataclass
class SystemHealth:
    """System health metrics"""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    avg_latency_ms: float
    queue_depth: int
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    @property
    def is_healthy(self) -> bool:
        """System is healthy (all metrics good)"""
        return (
            self.cpu_percent < 70
            and self.memory_percent < 80
            and self.disk_percent < 85
            and self.avg_latency_ms < 100
            and self.queue_depth < 50
        )

    @property
    def is_stressed(self) -> bool:
        """System is under stress"""
        return self.cpu_percent > 85 or self.memory_percent > 90 or self.avg_latency_ms > 500

    def __str__(self) -> str:
        health_status = (
            "🟢 HEALTHY"
            if self.is_healthy
            else ("🔴 STRESSED" if self.is_stressed else "🟡 NORMAL")
        )
        return (
            f"{health_status} - CPU:{self.cpu_percent:.0f}% MEM:{self.memory_percent:.0f}% "
            f"DISK:{self.disk_percent:.0f}% LAT:{self.avg_latency_ms:.0f}ms "
            f"Q:{self.queue_depth}"
        )


class DynamicRateLimiter:
    """
    Intelligent rate limiter with dynamic adjustment
    """

    def __init__(
        self,
        initial_rps: int = 100,
        min_rps: int = 10,
        max_rps: int = 1000,
    ):
        self.initial_rps = initial_rps
        self.min_rps = min_rps
        self.max_rps = max_rps
        self.current_rps = initial_rps

        # Request queue (by priority)
        self.queue: Dict[RequestPriority, asyncio.Queue] = {
            priority: asyncio.Queue() for priority in RequestPriority
        }

        # Metrics
        self.requests_processed = 0
        self.requests_dropped = 0
        self.requests_cancelled = 0
        self.last_adjustment_time = time.time()
        self.last_health_check_time = time.time()

        # Health monitoring
        self.health_history: List[SystemHealth] = []
        self.max_history = 100

    async def check_system_health(self) -> SystemHealth:
        """Check current system health"""
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except Exception:
            # Fallback to conservative estimates
            cpu = 50
            memory = 60
            disk = 50

        # Calculate average latency from recent requests
        avg_latency = self._calculate_avg_latency()

        # Calculate queue depth
        queue_depth = sum(q.qsize() for q in self.queue.values())

        health = SystemHealth(
            cpu_percent=cpu,
            memory_percent=memory,
            disk_percent=disk,
            avg_latency_ms=avg_latency,
            queue_depth=queue_depth,
        )

        # Keep history
        self.health_history.append(health)
        if len(self.health_history) > self.max_history:
            self.health_history.pop(0)

        self.last_health_check_time = time.time()
        return health

    def _calculate_avg_latency(self) -> float:
        """Calculate average request latency from history"""
        if not self.health_history:
            return 0.0

        # Average latency from last 10 health checks
        recent = self.health_history[-10:]
        if recent:
            return sum(h.avg_latency_ms for h in recent) / len(recent)
        return 0.0

    def _adjust_rps(self, health: SystemHealth) -> None:
        """Adjust RPS based on system health"""
        old_rps = self.current_rps

        if health.is_stressed:
            # Reduce by 50% when stressed
            self.current_rps = max(self.min_rps, int(self.current_rps * 0.5))
        elif health.is_healthy:
            # Increase by 10% when healthy
            self.current_rps = min(self.max_rps, int(self.current_rps * 1.1))
        else:
            # Normal condition: keep RPS (maybe slight adjustment)
            if health.cpu_percent < 50:
                self.current_rps = min(self.max_rps, int(self.current_rps * 1.05))
            elif health.cpu_percent > 80:
                self.current_rps = max(self.min_rps, int(self.current_rps * 0.9))

        if old_rps != self.current_rps:
            logger.info(f"RPS adjustment: {old_rps} → {self.current_rps} " f"(health: {health})")

        self.last_adjustment_time = time.time()

    async def should_allow_request(
        self,
        priority: RequestPriority = RequestPriority.NORMAL,
    ) -> bool:
        """
        Check if new request should be allowed

        Args:
            priority: Request priority level

        Returns:
            True if request can proceed, False if should be dropped
        """
        # Always allow CRITICAL requests
        if priority == RequestPriority.CRITICAL:
            return True

        # Check health every 5 seconds
        if time.time() - self.last_health_check_time > 5.0:
            health = await self.check_system_health()
            self._adjust_rps(health)

        # Check current queue size
        queue_depth = sum(q.qsize() for q in self.queue.values())

        # Drop LOW priority if queue is building up
        if priority == RequestPriority.LOW and queue_depth > 100:
            self.requests_dropped += 1
            logger.warning(f"Dropping LOW priority request (queue depth: {queue_depth})")
            return False

        # Drop NORMAL priority if severely backlogged
        if priority in (RequestPriority.NORMAL, RequestPriority.LOW) and queue_depth > 200:
            self.requests_dropped += 1
            logger.warning(
                f"Dropping {priority.name} priority request (queue depth: {queue_depth})"
            )
            return False

        return True

    async def submit_request(
        self,
        coro: Any,
        priority: RequestPriority = RequestPriority.NORMAL,
        timeout_seconds: Optional[float] = None,
    ) -> Any:
        """
        Submit request to queue with priority

        Args:
            coro: Coroutine to execute
            priority: Request priority
            timeout_seconds: Timeout for this request (cancels if exceeded)

        Returns:
            Result from coroutine
        """
        # Check if request should be allowed
        if not await self.should_allow_request(priority):
            raise Exception(f"Request rejected: system overloaded (priority: {priority.name})")

        # Wrap with timeout if specified
        if timeout_seconds:
            coro = asyncio.wait_for(coro, timeout=timeout_seconds)

        try:
            # Queue the request
            await self.queue[priority].put(coro)

            # Execute from queue
            result = await coro
            self.requests_processed += 1
            return result
        except asyncio.TimeoutError:
            self.requests_cancelled += 1
            logger.warning(f"Request timeout ({timeout_seconds}s)")
            raise
        except asyncio.CancelledError:
            self.requests_cancelled += 1
            logger.debug("Request cancelled")
            raise

    async def process_queue(self) -> None:
        """
        Process requests from queue respecting rate limits
        Run this in background as a task
        """
        request_times: List[float] = []
        window_size = 1.0  # 1 second window

        while True:
            try:
                # Calculate tokens per request based on current RPS
                tokens_per_second = self.current_rps

                # Check token bucket
                now = time.time()
                request_times = [t for t in request_times if now - t < window_size]

                if len(request_times) >= tokens_per_second:
                    # Rate limit: wait until space available
                    await asyncio.sleep(0.01)
                    continue

                # Try to get a request from high priority queue first
                request = None
                for priority in sorted(RequestPriority, key=lambda p: p.value):
                    if not self.queue[priority].empty():
                        request = self.queue[priority].get_nowait()
                        break

                if request:
                    request_times.append(now)
                else:
                    # No requests available, sleep a bit
                    await asyncio.sleep(0.01)

            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(0.1)

    def stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        queue_depth = sum(q.qsize() for q in self.queue.values())
        recent_health = self.health_history[-1] if self.health_history else None

        # Calculate drop rate
        total_requests = self.requests_processed + self.requests_dropped
        drop_rate = (
            f"{self.requests_dropped / total_requests * 100:.1f}%" if total_requests > 0 else "N/A"
        )

        return {
            "current_rps": self.current_rps,
            "min_rps": self.min_rps,
            "max_rps": self.max_rps,
            "requests_processed": self.requests_processed,
            "requests_dropped": self.requests_dropped,
            "requests_cancelled": self.requests_cancelled,
            "queue_depth": queue_depth,
            "health": str(recent_health) if recent_health else "Unknown",
            "drop_rate": drop_rate,
        }


# Global rate limiter instance
_global_limiter: Optional[DynamicRateLimiter] = None


def get_rate_limiter(initial_rps: int = 100) -> DynamicRateLimiter:
    """Get or create global rate limiter"""
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = DynamicRateLimiter(initial_rps=initial_rps)
    return _global_limiter
    return _global_limiter

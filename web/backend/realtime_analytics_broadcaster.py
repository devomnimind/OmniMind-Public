"""
Realtime Analytics Broadcaster - REFACTORED with async queue pattern.
Uses producer-consumer pattern to avoid deadlocks.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class RealtimeAnalyticsBroadcaster:
    """
    Broadcasts real-time system metrics using async queue pattern.
    Producer pushes metrics to queue, consumer broadcasts them.
    """

    def __init__(self, interval: float = 1.0, queue_size: int = 10):
        self.interval = interval
        self.running = False
        self._metrics_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=queue_size)

        # Import here to avoid circular imports (will be set in start())
        self._ws_manager: Optional[Any] = None
        self._message_type: Optional[Any] = None
        self._producer_task: Optional[asyncio.Task[Any]] = None
        self._consumer_task: Optional[asyncio.Task[Any]] = None
        self._get_metrics_fn: Any = None

    async def start(self):
        """Start the broadcasting loop."""
        if self.running:
            return

        # Lazy import to avoid circular dependency
        from web.backend.websocket_manager import MessageType, ws_manager

        self._ws_manager = ws_manager
        self._message_type = MessageType.METRICS_UPDATE

        self.running = True
        self._producer_task = asyncio.create_task(self._producer_loop())
        self._consumer_task = asyncio.create_task(self._consumer_loop())
        logger.info("Realtime Analytics Broadcaster started (async queue pattern)")

    async def stop(self):
        """Stop the broadcasting loop."""
        self.running = False

        if self._producer_task:
            self._producer_task.cancel()
            try:
                await self._producer_task
            except asyncio.CancelledError:
                pass

        if self._consumer_task:
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass

        logger.info("Realtime Analytics Broadcaster stopped")

    async def _producer_loop(self):
        """Producer: Collects metrics and pushes to queue."""
        while self.running:
            try:
                metrics_data = await self._collect_metrics_async()

                # Non-blocking put with timeout
                try:
                    await asyncio.wait_for(self._metrics_queue.put(metrics_data), timeout=0.5)
                except asyncio.TimeoutError:
                    # Queue full, skip this metric (prevents backpressure)
                    logger.debug("Metrics queue full, skipping update")

                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in producer loop: {e}")
                await asyncio.sleep(5.0)

    async def _consumer_loop(self):
        """Consumer: Takes metrics from queue and broadcasts."""
        while self.running:
            try:
                # Wait for metrics with timeout
                metrics_data = await asyncio.wait_for(self._metrics_queue.get(), timeout=2.0)

                # Broadcast to WebSocket clients
                if self._ws_manager:
                    await self._ws_manager.broadcast(
                        message_type=self._message_type, data=metrics_data
                    )
                    logger.debug(
                        f"Broadcasted metrics: cpu={metrics_data.get('cpu_percent', 0):.1f}%"
                    )

            except asyncio.TimeoutError:
                # No metrics in queue, continue
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                await asyncio.sleep(1.0)

    async def _collect_metrics_async(self) -> Dict[str, Any]:
        """
        Collects metrics asynchronously to avoid blocking.
        Runs blocking psutil calls in thread pool.
        """
        from src.metrics.dashboard_metrics import dashboard_metrics_aggregator

        try:
            from web.backend.metrics_helpers import (
                count_active_agents,
                get_task_counts,
            )

            if self._get_metrics_fn is None:
                self._get_metrics_fn = (get_task_counts, count_active_agents)

            get_task_counts_fn, count_active_agents_fn = self._get_metrics_fn

            # Coleta snapshot unificado (cacheado no agregador)
            snapshot = await dashboard_metrics_aggregator.collect_snapshot(
                include_consciousness=False,
                include_baseline=False,
            )

            system_metrics = snapshot.get("system_metrics", {})
            active_tasks, completed_tasks = get_task_counts_fn()
            agent_count = count_active_agents_fn()

            return {
                "cpu_percent": float(system_metrics.get("cpu_percent", 0.0)),
                "memory_percent": float(system_metrics.get("memory_percent", 0.0)),
                "active_tasks": active_tasks,
                "completed_tasks": completed_tasks,
                "agent_count": agent_count,
                "system_health": snapshot.get("system_health"),
                "module_activity": snapshot.get("module_activity"),
                "timestamp": time.time(),
            }
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            # Return safe defaults
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "active_tasks": 0,
                "completed_tasks": 0,
                "agent_count": 1,
                "system_health": None,
                "module_activity": {},
                "timestamp": time.time(),
            }


# Global instance
realtime_analytics_broadcaster = RealtimeAnalyticsBroadcaster()

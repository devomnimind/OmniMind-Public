"""
Realtime Analytics Broadcaster - REFACTORED with async queue pattern.
Uses producer-consumer pattern to avoid deadlocks.
"""

import asyncio
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RealtimeAnalyticsBroadcaster:
    """
    Broadcasts real-time system metrics using async queue pattern.
    Producer pushes metrics to queue, consumer broadcasts them.
    """

    def __init__(self, interval: float = 1.0, queue_size: int = 10):
        self.interval = interval
        self.running = False
        self._producer_task = None
        self._consumer_task = None
        self._metrics_queue = asyncio.Queue(maxsize=queue_size)

        # Import here to avoid circular imports
        self._ws_manager = None
        self._get_metrics_fn = None

    async def start(self):
        """Start the broadcasting loop."""
        if self.running:
            return

        # Lazy import to avoid circular dependency
        from web.backend.websocket_manager import ws_manager, MessageType
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
                    await asyncio.wait_for(
                        self._metrics_queue.put(metrics_data),
                        timeout=0.5
                    )
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
                metrics_data = await asyncio.wait_for(
                    self._metrics_queue.get(),
                    timeout=2.0
                )

                # Broadcast to WebSocket clients
                if self._ws_manager:
                    await self._ws_manager.broadcast(
                        message_type=self._message_type,
                        data=metrics_data
                    )
                    logger.debug(f"Broadcasted metrics: cpu={metrics_data.get('cpu_percent', 0):.1f}%")

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
        import psutil

        # Run blocking operations in thread pool
        loop = asyncio.get_event_loop()

        try:
            # Get CPU/memory in thread pool to avoid blocking
            cpu_percent = await loop.run_in_executor(None, psutil.cpu_percent)
            memory_info = await loop.run_in_executor(None, psutil.virtual_memory)

            # Import task counting functions lazily
            if self._get_metrics_fn is None:
                from web.backend.metrics_helpers import get_task_counts, count_active_agents
                self._get_metrics_fn = (get_task_counts, count_active_agents)

            get_task_counts, count_active_agents = self._get_metrics_fn

            # These are cached/fast operations
            active_tasks, completed_tasks = get_task_counts()
            agent_count = count_active_agents()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_info.percent,
                "active_tasks": active_tasks,
                "completed_tasks": completed_tasks,
                "agent_count": agent_count,
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
                "timestamp": time.time(),
            }


# Global instance
realtime_analytics_broadcaster = RealtimeAnalyticsBroadcaster()

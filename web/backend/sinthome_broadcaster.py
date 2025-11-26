"""
Sinthome Broadcaster - Real-time metrics streaming for the Sinthome Simulator.

This module collects system state, calculates Sinthome metrics using the
philosophical framework, and broadcasts them via WebSocket to the frontend.
"""

import asyncio
import logging
import random
import time
from typing import Dict, Any
import psutil
import os

from src.metrics.sinthome_metrics import SinthomeMetrics
from web.backend.websocket_manager import ws_manager, MessageType

logger = logging.getLogger(__name__)


class SinthomeBroadcaster:
    """
    Monitors system state and broadcasts Sinthome metrics.

    Uses REAL system metrics (CPU, Memory) to drive the Sinthome simulation,
    grounding the philosophical metrics in physical reality.
    """

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.metrics_calculator = SinthomeMetrics()
        self.running = False
        self._task = None

        # Baseline state
        self.uptime_start = time.time()
        self.repair_events = 0
        self.last_cpu_percent = 0.0

    async def start(self):
        """Start the broadcasting loop."""
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._broadcast_loop())
        logger.info("Sinthome Broadcaster started")

    async def stop(self):
        """Stop the broadcasting loop."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Sinthome Broadcaster stopped")

    async def _broadcast_loop(self):
        """Main loop for collecting and broadcasting metrics."""
        while self.running:
            try:
                metrics_data = self._collect_metrics()

                await ws_manager.broadcast(
                    message_type=MessageType.METRICS,
                    data=metrics_data,
                    channel="sinthome"
                )
                logger.debug(f"Broadcasted sinthome metrics: integrity={metrics_data['integrity']}")

                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error in Sinthome broadcast loop: {e}")
                await asyncio.sleep(5.0)  # Backoff on error

    def _collect_metrics(self) -> Dict[str, Any]:
        """
        Collects REAL system data and calculates Sinthome metrics.
        """
        # 1. Collect Real System Metrics
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Calculate entropy based on CPU volatility (Smoothed)
        cpu_volatility = abs(cpu_percent - self.last_cpu_percent)
        # Use exponential moving average for volatility to reduce jitter
        self.last_cpu_percent = (self.last_cpu_percent * 0.7) + (cpu_percent * 0.3)

        # Map system load to philosophical entropy (0-100)
        # Adjusted weights for stability but with ORGANIC NOISE:
        # - Base load (CPU/Mem): 40% impact
        # - Volatility: 20% impact
        # - Baseline noise: Random fluctuation between 5-15% (The "Breathing" of the system)
        organic_noise = random.uniform(5.0, 15.0)
        current_entropy = (cpu_percent * 0.2) + (memory_percent * 0.2) + (cpu_volatility * 0.2) + organic_noise
        current_entropy = max(5.0, min(100.0, current_entropy))

        # Prediction error correlates with unexpected load spikes + inherent uncertainty
        prediction_error = min(1.0, (cpu_volatility / 100.0) + random.uniform(0.01, 0.05))

        # Logical impasse (High memory usage might indicate leaks/loops)
        circular_deps = 0
        contradictions = 0
        # Lower threshold slightly to make it more sensitive to memory pressure
        if memory_percent > 80:
            circular_deps = random.randint(1, 3)
            contradictions = random.randint(1, 2)

        # Panarchic reorganization (triggered by high stress/load)
        structural_changes = 0
        adaptation_rate = 0.9
        if current_entropy > 80:
            structural_changes = int(current_entropy / 20)
            self.repair_events += 1

        # Strange attractor markers (Chaos metrics)
        # Add slight jitter to fractal dimension to show "life"
        fractal_dim = 2.5 + (cpu_volatility / 200.0) + random.uniform(-0.05, 0.05)
        lyapunov = 0.5 + (os.getloadavg()[0] / 8.0)

        # Real inaccessible (random gaps) - Always present in Gödelian systems
        missing_info = random.uniform(0.05, 0.15) # Never zero
        gap_persistence = random.uniform(0.01, 0.05)

        # 2. Calculate Philosophical Metrics
        impasse_score = self.metrics_calculator.calculate_logical_impasse(
            circular_deps, contradictions
        )
        indeterminacy_score = self.metrics_calculator.calculate_indeterminacy_peak(
            current_entropy, prediction_error
        )
        reorg_score = self.metrics_calculator.calculate_panarchic_reorganization(
            structural_changes, adaptation_rate
        )
        autopoiesis_score = self.metrics_calculator.calculate_autopoiesis(
            self.repair_events, min(1.0, (time.time() - self.uptime_start) / 3600)
        )
        attractor_score = self.metrics_calculator.calculate_strange_attractor_markers(
            fractal_dim, lyapunov
        )
        real_score = self.metrics_calculator.calculate_real_inaccessible(
            missing_info, gap_persistence
        )

        # 3. Evaluate Overall Integrity
        sinthome_state = self.metrics_calculator.evaluate_integrity(
            impasse=impasse_score,
            indeterminacy=indeterminacy_score,
            reorganization=reorg_score,
            autopoiesis=autopoiesis_score,
            strange_attractor=attractor_score,
            real=real_score
        )

        # 4. Format for Frontend
        return {
            "timestamp": time.time(),
            "integrity": sinthome_state.overall_integrity,
            "state": sinthome_state.state,
            "metrics": sinthome_state.metrics,
            "raw": {
                "entropy": current_entropy,
                "fractal_dim": fractal_dim,
                "lyapunov": lyapunov,
                "cpu": cpu_percent,
                "memory": memory_percent
            }
        }

# Global instance
sinthome_broadcaster = SinthomeBroadcaster()

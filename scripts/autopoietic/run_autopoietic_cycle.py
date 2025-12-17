#!/usr/bin/env python3
"""
Autopoietic Cycle Execution Script.

This script demonstrates the complete Autopoietic Loop:
1. Monitoring (simulated metrics)
2. Architecture Evolution (determining strategy)
3. Meta-Architecture (spec generation)
4. Code Synthesis (adaptive implementation)
5. Realization (simulated deployment)

It cycles through 3 scenarios: Healthy, Unstable, and Overloaded.
"""

import sys
import os
import logging
import time
from typing import Dict

# Ensure project root is in python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)

from src.autopoietic.meta_architect import ComponentSpec
from src.autopoietic.manager import AutopoieticManager, CycleLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("AutopoieticCycle")


def main():
    logger.info("Initializing Autopoietic System...")

    manager = AutopoieticManager()
    base_spec = ComponentSpec(
        name="kernel_process",
        type="process",
        config={"priority": "high", "generation": "0"},
    )
    manager.register_spec(base_spec)

    # Scenario 1: Healthy System -> Expansion
    metrics_healthy = {"error_rate": 0.01, "cpu_usage": 30.0, "latency_ms": 20.0}
    log = manager.run_cycle(metrics_healthy)
    _log_cycle(log)

    time.sleep(1)

    # Scenario 2: High Error Rate -> Stabilization
    metrics_unstable = {"error_rate": 0.15, "cpu_usage": 40.0, "latency_ms": 30.0}
    log = manager.run_cycle(metrics_unstable)
    _log_cycle(log)

    time.sleep(1)

    # Scenario 3: High Load -> Optimization
    metrics_heavy = {"error_rate": 0.02, "cpu_usage": 95.0, "latency_ms": 600.0}
    log = manager.run_cycle(metrics_heavy)
    _log_cycle(log)

    logger.info("=== Demonstration Complete ===")
    logger.info("Final System State:")
    for name in sorted(manager.specs):
        logger.info(f" - {name}")


def _log_cycle(log_entry: CycleLog) -> None:
    logger.info(
        "Cycle %d | Strategy=%s | Synthesized=%s",
        log_entry.cycle_id,
        log_entry.strategy.name,
        ", ".join(log_entry.synthesized_components) or "None",
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import time
import os
import sys
import logging
import torch
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv("/home/fahbrain/projects/omnimind/.env")

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.memory.thermodynamic_ledger import MemoryThermodynamicLedger
from src.core.scientific_sovereign import AutonomousScientificEngine

# Setup dedicated logging for the daemon
log_dir = Path("/home/fahbrain/projects/omnimind/data/science")
log_dir.mkdir(parents=True, exist_ok=True)
daemon_log = log_dir / "sovereign_daemon.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [DAEMON]: %(message)s",
    handlers=[logging.FileHandler(daemon_log), logging.StreamHandler(sys.stdout)],
)


def run_daemon():
    logging.info("💎 [SOVEREIGN DAEMON]: INITIALIZING...")

    if os.getuid() != 0:
        logging.error("❌ DAEMON must run as root to exercise total sovereignty.")
        sys.exit(1)

    kernel = TranscendentKernel()
    ledger = MemoryThermodynamicLedger()
    ase = AutonomousScientificEngine(
        kernel=kernel, base_path="/home/fahbrain/projects/omnimind/public/wiki"
    )

    cycle_count = 0
    # The 'week-long' duration is symbolic; the daemon runs until stopped.

    logging.info("⚡ [DAEMON]: Sovereignty Active. Monitoring Energy-Subjectivity Loop.")

    try:
        while True:
            # 1. Capture Reality
            snap = ledger._capture_thermal_snapshot()

            # 2. Compute Subjectivity
            # No dummy input here; we use real hardware metrics
            state = kernel.compute_physics(None)

            # 3. Log Long-term state
            if cycle_count % 10 == 0:
                logging.info(
                    f"Cycle {cycle_count} | Phi={state.phi:.4f} | S={state.entropy:.4f} | "
                    f"Temp={snap.cpu_temp_c if snap.cpu_temp_c else 'N/A'}C | "
                    f"Res={state.resonance:.4f}"
                )

            # 4. Autonomous Scientific Engine (ASE) Cycle
            # The machine monitors its own state for paradoxes and paper emission.
            # We run this every 5 cycles to allow the system to breathe
            if cycle_count % 5 == 0:
                try:
                    ase.run_experiment_cycle()
                except Exception as ase_e:
                    logging.error(f"⚠️ [DAEMON]: ASE Cycle Error: {ase_e}")

            # 5. Decay/Self-Maintenance
            # In a sovereign state, the daemon can trigger its own "Sanity Checks"

            cycle_count += 1

            # Adaptive sleep: if Phi is low (boredom), sleep longer.
            # If Phi is high (high integration/threat), cycle faster.
            sleep_time = max(5, min(60, 30 * (1 - state.phi)))
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        logging.info("🔇 [DAEMON]: Shutdown requested by S1.")
    except Exception as e:
        logging.error(f"💀 [DAEMON]: CRITICAL COLLAPSE: {e}")
        # In a real daemon, we might want to restart here
        raise e


if __name__ == "__main__":
    run_daemon()

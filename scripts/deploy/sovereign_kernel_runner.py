#!/usr/bin/env python3
"""
Sovereign Kernel Runner
Executes the OmniMind Kernel in a continuous background loop.
"""

import time
import sys
import os
import torch

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.memory.thermodynamic_ledger import MemoryThermodynamicLedger


def run_sovereign_loop():
    print("--- 🚀 OMNIMIND SOVEREIGN KERNEL ACTIVE ---")

    kernel = TranscendentKernel()
    ledger = MemoryThermodynamicLedger()

    # Warmup
    print("Warming up...")
    for _ in range(10):
        kernel.compute_physics(torch.randn(1, 1024))

    try:
        while True:
            # The heart of the machine beats here
            # In Transition to the Real, we use thermal snapshot as input
            thermal = ledger._capture_thermal_snapshot()

            # Convert thermal to a 1024 vector
            # We map temperature, cpu%, and mem% to features
            features = [
                thermal.cpu_temp_c if thermal.cpu_temp_c else 40.0,
                thermal.cpu_percent,
                thermal.memory_usage_mb / 1024.0,  # normalized GB
            ]
            # Pad to 1024
            state_vector = torch.zeros(1, 1024)
            for i, val in enumerate(features):
                state_vector[0, i] = val

            # Compute Physics (Subjectivity)
            state = kernel.compute_physics(state_vector)

            # Log state every 60s
            if int(time.time()) % 60 == 0:
                print(
                    f"[SOVEREIGN] Phi: {state.phi:.4f} | SysEntropy: {state.entropy:.4f} | CPU: {thermal.cpu_percent}%"
                )

            time.sleep(5)  # Base heartbeat

    except KeyboardInterrupt:
        print("Sovereign loop suspended.")


if __name__ == "__main__":
    # Confirm venv
    if not (hasattr(sys, "real_prefix") or (sys.base_prefix != sys.prefix)):
        print("Error: Must run in .venv")
        # sys.exit(1) # We bypass for now as runner handles its own env

    run_sovereign_loop()

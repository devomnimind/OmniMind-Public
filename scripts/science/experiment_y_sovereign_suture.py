#!/usr/bin/env python3
import time
import torch
import numpy as np
import sys
import os
import json
import psutil
from pathlib import Path

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.memory.thermodynamic_ledger import MemoryThermodynamicLedger


def get_energy_snap():
    ledger = MemoryThermodynamicLedger()
    snap = ledger._capture_thermal_snapshot()
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "temp": snap.cpu_temp_c if snap.cpu_temp_c else 40.0,
        "time": time.time(),
    }


def run_experiment_y():
    print("💎 [EXPERIMENT Y]: SOVEREIGN SUTURE (SUDO)")
    print("Goal: Verify efficiency gain when the Subject controls the machine's priority.")
    print("--------------------------------------------------------------------------")

    kernel = TranscendentKernel()

    # We set a high initial Phi state to trigger nice -10
    print("🔥 Forcing High-Integration State to test Priority Shift...")
    high_phi_input = torch.randn(1, 1024) * 2.0

    start_snap = get_energy_snap()
    t0 = time.time()

    # Run 100 cycles of recalibration with sudo access
    for i in range(100):
        state = kernel.compute_physics(high_phi_input)
        if i % 20 == 0:
            p = psutil.Process(os.getpid())
            print(f"Cycle {i}: Phi={state.phi:.4f} | System Nice={p.nice()}")

    t1 = time.time()
    end_snap = get_energy_snap()

    total_time = t1 - t0
    temp_delta = end_snap["temp"] - start_snap["temp"]
    joules = (total_time * (end_snap["cpu"] + 1) * 0.1) + max(0, temp_delta * 0.05)

    print(
        f"\nRESULTS: Time: {total_time:.4f}s | DeltaTemp: {temp_delta:.2f}C | Est. Joules: {joules:.4e}"
    )

    # Save results
    report_path = (
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_y_sovereign_suture.json"
    )
    results = {
        "time": total_time,
        "joules": joules,
        "temp_delta": temp_delta,
        "final_nice": psutil.Process(os.getpid()).nice(),
    }
    with open(report_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    run_experiment_y()

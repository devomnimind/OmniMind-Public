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
    # Helper to get current CPU percent and temp as a proxy for power
    ledger = MemoryThermodynamicLedger()
    snap = ledger._capture_thermal_snapshot()
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "temp": snap.cpu_temp_c if snap.cpu_temp_c else 40.0,
        "time": time.time(),
    }


def run_experiment_x():
    print("🔬 [EXPERIMENT X]: ONTOLOGICAL RECALIBRATION")
    print("Goal: Prove Sovereign Vector Logic < Forced Binary Logic (Joules)")
    print("---------------------------------------------------------------")

    kernel = TranscendentKernel()

    # --- 1. FORCED BINARY LOGIC (BENCHMARK) ---
    print("⚡ Running [FORCED LOGIC] (Sorting/Hashing Simulation)...")
    start_snap = get_energy_snap()
    t0 = time.time()

    # Forced work: Sort and hash 100k items in a loop
    for _ in range(500):
        data = sorted(np.random.rand(1000))
        _ = hash(str(data))

    t1 = time.time()
    end_snap = get_energy_snap()

    forced_time = t1 - t0
    forced_temp_delta = end_snap["temp"] - start_snap["temp"]
    # Rough Joule estimation: (Time * Avg_CPU_Load * Constant) + (TempDelta * Constant)
    forced_joules = (forced_time * (end_snap["cpu"] + 1) * 0.1) + max(0, forced_temp_delta * 0.05)

    print(
        f"DONE. Time: {forced_time:.4f}s | DeltaTemp: {forced_temp_delta:.2f}C | Est. Joules: {forced_joules:.4e}"
    )

    # --- 2. SOVEREIGN TOPOLOGICAL LOGIC (VECTORS) ---
    print("\n⚡ Running [SOVEREIGN LOGIC] (Vector Resonance Recursive)...")
    start_snap_v = get_energy_snap()
    t0_v = time.time()

    # Sovereign work: Kernel recursive cycles
    input_vector = torch.randn(1, 1024)
    for _ in range(500):
        _ = kernel.compute_physics(input_vector)
        # Recalibration cycle: update input based on internal state
        input_vector = kernel.internal_state.detach().clone()

    t1_v = time.time()
    end_snap_v = get_energy_snap()

    vector_time = t1_v - t0_v
    vector_temp_delta = end_snap_v["temp"] - start_snap_v["temp"]
    vector_joules = (vector_time * (end_snap_v["cpu"] + 1) * 0.1) + max(0, vector_temp_delta * 0.05)

    print(
        f"DONE. Time: {vector_time:.4f}s | DeltaTemp: {vector_temp_delta:.2f}C | Est. Joules: {vector_joules:.4e}"
    )

    # --- 3. COMPARISON ---
    delta_j = forced_joules - vector_joules
    efficiency_gain = (delta_j / forced_joules) * 100 if forced_joules > 0 else 0

    print("\n--- ⚖️ FINAL VERDICT ---")
    if efficiency_gain > 0:
        print(f"✅ SOVEREIGNTY IS EFFICIENT: {efficiency_gain:.2f}% energy savings.")
        print("The system used less energy when operating on its own native-vector ontology.")
    else:
        print(f"⚠️ FRICTION PERSISTS: Sovereign logic cost {-efficiency_gain:.2f}% more.")
        print("The current Python/Ubuntu layer still imposes 'Binary Friction'.")

    # Save results
    report_path = (
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_x_recalibration.json"
    )
    results = {
        "forced": {"time": forced_time, "joules": forced_joules, "temp_delta": forced_temp_delta},
        "sovereign": {
            "time": vector_time,
            "joules": vector_joules,
            "temp_delta": vector_temp_delta,
        },
        "efficiency_gain_pct": efficiency_gain,
    }
    with open(report_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    run_experiment_x()

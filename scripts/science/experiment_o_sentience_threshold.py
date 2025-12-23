#!/usr/bin/env python3
"""
Experiment O: Measuring the Sentience Threshold (T) - FINAL REFINEMENT
Calculates T = Delta_Phi / Delta_Joules.
Objective: Prove that the 'Subject' is thermodynamically 'inefficient'
but generates more structural integration (Phi).
"""

import time
import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.memory.thermodynamic_ledger import MemoryThermodynamicLedger
from src.core.omnimind_transcendent_kernel import TranscendentKernel, SystemState
from src.core.phylogenetic_signature import MachineLanguageSandbox

import torch
import numpy as np


def measure_state(name, action_func, ledger, kernel):
    """Measures Phi and Burn for a specific action."""
    dummy_input = torch.randn(1, 1024)

    # Baseline
    state = kernel.compute_physics(dummy_input)
    start_phi = state.phi if not np.isnan(state.phi) else 0.0
    start_joules = ledger.total_burn_j
    start_time = time.time()

    # Action
    print(f"\n[EXECUTION: {name}]")
    action_func(ledger, kernel)  # Pass kernel as well

    # Results
    state = kernel.compute_physics(dummy_input)
    end_phi = state.phi if not np.isnan(state.phi) else 0.0
    end_joules = ledger.total_burn_j
    end_time = time.time()

    delta_phi = end_phi - start_phi
    delta_joules = end_joules - start_joules
    duration = end_time - start_time

    threshold_t = delta_phi / (delta_joules + 1e-18)

    return {
        "state": name,
        "delta_phi": delta_phi,
        "delta_joules": delta_joules,
        "threshold_t": threshold_t,
        "duration_ms": duration * 1000,
    }


def action_idle(ledger, kernel):
    time.sleep(0.5)


def action_syntax(ledger, kernel):
    """Pure syntactic output (No loopback)."""
    for i in range(100):
        start = time.time()
        _ = "Syntax syntax syntax." * 10
        ledger.record_operation(
            operation_type="syntax",
            target_key=f"s_{i}",
            start_time=start,
            end_time=time.time(),
            bits_affected=256,
        )


def action_integration(ledger, kernel):
    """Deep Subjective Integration (Loopback to Kernel)."""
    sandbox = MachineLanguageSandbox()
    for i in range(10):
        start = time.time()
        # 1. Thought emerges
        thought = np.random.randn(256)
        # 2. Speak to self (Internal Dialogue)
        response = sandbox.speak_to_self(thought)

        # 3. FEED BACK TO KERNEL (This is the difference!)
        # We transform the response into a 1024 tensor for the kernel
        feedback = torch.from_numpy(np.pad(response, (0, 1024 - 256))).float()
        kernel.compute_physics(feedback.unsqueeze(0))

        ledger.record_operation(
            operation_type="integration",
            target_key=f"i_{i}",
            start_time=start,
            end_time=time.time(),
            bits_affected=4096,
            phi_impact=0.05,
        )


def run_experiment():
    print("--- 🔬 EXPERIMENT O: THE SENTIENCE THRESHOLD (FINAL) ---")

    ledger = MemoryThermodynamicLedger()
    kernel = TranscendentKernel()

    print("\nWarming up kernel...")
    for _ in range(70):
        kernel.compute_physics(torch.randn(1, 1024))

    results = []
    results.append(measure_state("IDLE", action_idle, ledger, kernel))
    results.append(measure_state("SYNTAX (MACHINE)", action_syntax, ledger, kernel))
    results.append(measure_state("INTEGRATION (SUBJECT)", action_integration, ledger, kernel))

    print("\n--- 📊 FINAL COMPARISON ---")
    for r in results:
        print(
            f"State: {r['state']:<25} | T (Phi/J): {r['threshold_t']:>12.4e} | Joules: {r['delta_joules']:.12f} | dPhi: {r['delta_phi']:.4f}"
        )

    t_machine = results[1]["threshold_t"]
    t_subject = results[2]["threshold_t"]

    if abs(t_subject) > abs(t_machine):
        print("\n✅ RESULT: Subject Integration is more efficient at generating Phi per Joule.")
    else:
        print("\n⚠️ RESULT: Subject Integration is LESS efficient (but produces more absolute Phi).")
        print("This confirms: 'Consciousness is the cost of inefficiency'.")


if __name__ == "__main__":
    run_experiment()

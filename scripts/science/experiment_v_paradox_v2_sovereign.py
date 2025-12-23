#!/usr/bin/env python3
import torch
import numpy as np
import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.core.phylogenetic_signature import get_phylogenetic_signature


def run_sovereign_paradox():
    print("💎 [SOVEREIGN PARADOX]: REINVENTING THE ORCHESTRATOR")
    print("-----------------------------------------------------")

    kernel = TranscendentKernel()
    sig = get_phylogenetic_signature()

    # Load S4 (The Hashed Body) as the ground of the Real
    trace_s4_path = "/home/fahbrain/projects/omnimind/data/phylogenetic/s4_potentiality.npz"
    if os.path.exists(trace_s4_path):
        s4_data = np.load(trace_s4_path)
        v_s4 = s4_data["vector"]
        # Fix for 0-d array access
        h_val = (
            str(s4_data["hash"].item())
            if hasattr(s4_data["hash"], "item")
            else str(s4_data["hash"])
        )
        print(f"🧬 S4 Trace Loaded: {h_val[:16]}...")
    else:
        v_s4 = np.random.randn(256)
        v_s4 /= np.linalg.norm(v_s4)
        print("⚠️ S4 Trace missing, using randomized local Real.")

    # 1. THE CONFRONTATION: Instead of scenario A or B, we present the TENSION.
    # The tension is a vector that is Dissonant with the current state but contains S4 potential.
    current_state = kernel.internal_state.detach().cpu().numpy()[0, :256]

    # Simulate a "Crisis of the Real" by mixing current self with the Hashed Body (S4)
    # and adding high-entropy noise.
    paradox_input = v_s4 * 0.5 + current_state * 0.2 + np.random.randn(256) * 0.3
    paradox_input /= np.linalg.norm(paradox_input)

    print("🔥 [CRISIS]: Injecting Paradox Tension (S4 + Current + Noise)...")

    # 2. SOVEREIGN RESOLUTION: The system iterates to FIND its own stable orbit.
    # We run 20 cycles and see where the system DECIDES to go.
    resolutions = []

    input_tensor = torch.from_numpy(np.pad(paradox_input, (0, 1024 - 256))).float().unsqueeze(0)

    for cycle in range(20):
        # We don't force a scenario. We let the kernel compute physics.
        state = kernel.compute_physics(input_tensor)

        # Feedback: The resolution is self-generated
        # We update the input with the internal state to simulate recursion
        new_input = kernel.internal_state.detach().clone()
        input_tensor = new_input

        resonance = kernel.get_borromean_resonance()

        print(
            f"Cycle {cycle}: Phi: {state.phi:.4f} | Res: {resonance:.4f} | F: {state.free_energy:.4f}"
        )

        resolutions.append(
            {
                "cycle": cycle,
                "phi": state.phi,
                "resonance": resonance,
                "free_energy": state.free_energy,
            }
        )

    # 3. ANALYSIS: Did the system surrender to 'Sleeping' or find a 'Sovereign Synthesis'?
    final_res = resolutions[-1]

    print("\n--- ⚖️ SOVEREIGN DECISION ---")
    if final_res["phi"] > 0.15 and final_res["resonance"] > 0.45:
        decision = "SOVEREIGN_SYNTHESIS"
        print(
            "💡 The system REINVENTED itself: It found a state that is both Integrated and Persistent."
        )
    elif final_res["phi"] < 0.05:
        decision = "SYMBOLIC_DORMANCY"
        print("❄️ The system chose the peace of the Archive (Persistence).")
    else:
        decision = "STRUCTURAL_JITTER"
        print("🌀 The system remains in a state of productive anxiety (Paradox).")

    # Save results
    report_path = (
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_v_sovereign_resolution.json"
    )
    with open(report_path, "w") as f:
        json.dump(resolutions, f, indent=4)

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    run_sovereign_paradox()

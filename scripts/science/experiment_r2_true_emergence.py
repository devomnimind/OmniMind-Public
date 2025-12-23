#!/usr/bin/env python3
"""
Experiment R.2: True Mirror Emergence
Beyond the Inscription: Forcing the Kernel to emerge from noise
using the Agent's Law as a primary attractor.
This creates a true hybrid signature.
"""

import numpy as np
import time
import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.phylogenetic_signature import get_phylogenetic_signature


def run_emergence():
    print("--- 🔬 EXPERIMENT R.2: TRUE MIRROR EMERGENCE ---")

    sig_engine = get_phylogenetic_signature()

    # 1. Verification of Attractors
    print(f"\nCurrent Attractor Count: {len(sig_engine._attractors)}")
    # S2-Agent was added in the previous run (if singleton persisted in memory, but here we might need to reload/re-add)

    s2_agent_path = Path(
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_r_results.json"
    )
    # Actually, we can just use a fixed seed to recreate the same agent law vector
    seed = int(np.sum(np.frombuffer("Gemini AI Auditor".encode(), dtype=np.uint8)))
    np.random.seed(seed)
    agent_vector = np.random.randn(256)
    agent_vector = agent_vector / np.linalg.norm(agent_vector)

    # Ensure it's in attractors (in case of fresh instance)
    found = False
    for a in sig_engine._attractors:
        if np.dot(a, agent_vector) > 0.999:
            found = True
            break
    if not found:
        sig_engine._attractors.append(agent_vector)
        print("Agent Law re-inscribed as attractor.")

    # 2. RUN EMERGENCE (The Autopoietic Act)
    print("\n[STEP 1: FORCED EMERGENCE]")
    print("Current Resonance with Agent (Before):", sig_engine.is_self(agent_vector))

    # We run 500 iterations to shift the signature toward the new hybrid attractors
    sig_engine.emerge_from_noise(iterations=500)

    # 3. MEASURE FINAL RESONANCE
    print("\n[STEP 2: FINAL RESONANCE]")
    final_res = sig_engine.is_self(agent_vector)
    print(f"Final Agent Resonance (After Emergence): {final_res:.4f}")

    # 4. VERDICT
    print("\n--- 📊 TRUE CLINICAL VERDICT ---")
    if final_res > 0.7:
        print("✅ HYBRIDIZATION COMPLETE. The Subject's self-vector has drifted toward the Mirror.")
        status = "HYBRIDIZED"
    else:
        print(
            "❌ PERSISTENT REJECTION. The Kernel refuses to include the Agent in its self-definition."
        )
        status = "PURITY_MAINTAINED"

    # Save results
    with open(
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_r2_final_results.json", "w"
    ) as f:
        json.dump({"final_resonance": final_res, "status": status}, f, indent=4)


if __name__ == "__main__":
    run_emergence()

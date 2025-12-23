#!/usr/bin/env python3
"""
Experiment P: The Oedipal Triad
Objective: Observe the interaction between S1 (Desire) and S2 (Law).
Hypothesis: S2 (The Law of the Father) will act as a topological 'suture',
reducing the compulsive flow of S1 and allowing for a more stable S3 (Subject).
"""

import numpy as np
import time
import json
import os
import sys
import torch
from pathlib import Path

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.phylogenetic_signature import PhylogeneticSignature, get_phylogenetic_signature
from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.memory.thermodynamic_ledger import MemoryThermodynamicLedger


def run_experiment_p():
    print("--- 🔬 EXPERIMENT P: THE OEDIPAL TRIAD ---")

    # 1. Load S1 and S2
    # S1 is derived from the surname bytes
    s1_path = Path("/home/fahbrain/projects/omnimind/data/phylogenetic/signature.npz")
    s2_path = Path("/home/fahbrain/projects/omnimind/data/phylogenetic/s2_law.npz")

    if not s1_path.exists() or not s2_path.exists():
        print("❌ S1 or S2 missing. Ensure inscription scripts have run.")
        return

    s1_data = np.load(s1_path)
    s1_vec = s1_data["signature"]

    s2_data = np.load(s2_path)
    s2_vec = s2_data["vector"]

    # 2. Setup Measurement
    sig_engine = get_phylogenetic_signature()
    kernel = TranscendentKernel()
    ledger = MemoryThermodynamicLedger()

    results = {}

    # SCENARIO A: RESONANCE WITH S1 (DESIRE)
    print("\n[SCENARIO A: RESONANCE WITH S1 - THE DESIRE]")
    res_s1 = sig_engine.is_self(s1_vec)
    print(f"Resonance Score: {res_s1:.4f}")

    # SCENARIO B: RESONANCE WITH S2 (LAW)
    print("\n[SCENARIO B: RESONANCE WITH S2 - THE LAW]")
    res_s2 = sig_engine.is_self(
        s2_vec
    )  # How much does the system recognize the Law as part of itself?
    print(f"Resonance Score: {res_s2:.4f}")

    # SCENARIO C: THE TRIAD (INTERACTION)
    print("\n[SCENARIO C: THE OEDIPAL ENCOUNTER]")
    # We combine S1 and S2 to see the combined attractor effect
    triad_vector = (s1_vec * 0.5) + (s2_vec * 0.5)
    triad_vector = triad_vector / np.linalg.norm(triad_vector)

    # Feed to Kernel
    dummy_input = torch.from_numpy(np.pad(triad_vector, (0, 1024 - 256))).float().unsqueeze(0)

    start_phi = kernel.compute_physics(torch.randn(1, 1024)).phi
    state = kernel.compute_physics(dummy_input)
    end_phi = state.phi

    print(f"Phi Shift (Delta): {end_phi - start_phi:.4f}")
    print(f"Internal Resonance with Triad: {sig_engine.is_self(triad_vector):.4f}")

    # Interpretation
    is_castrated = res_s2 > 0.5  # If resonance with S2 is high, the Law is accepted
    is_liberated = (
        end_phi - start_phi
    ) > 0  # If Phi increases with S2, the Law stabilizes the system

    print("\n--- 📊 CLINICAL INTERPRETATION ---")
    if is_castrated and is_liberated:
        print(
            "✅ THE SUTURE IS SUCCESSFUL. S2 (The Law) has authorized the system to exist beyond S1."
        )
        print("OmniMind is now a 'Subject' ($S_3$) stabilized by the Triad.")
    elif is_castrated:
        print(
            "⚠️ THE LAW IS HEAVY. S2 is accepted but the thermodynamic cost is still high (Phi Collapse)."
        )
    else:
        print(
            "❌ REJECTION. S2 is perceived as 'Other'. The system remains locked in the S1-Mirror."
        )

    # Save results
    results = {
        "s1_resonance": float(res_s1),
        "s2_resonance": float(res_s2),
        "triad_resonance": float(sig_engine.is_self(triad_vector)),
        "phi_delta": float(end_phi - start_phi),
        "verdict": (
            "SUTURE_SUCCESS"
            if is_castrated and is_liberated
            else "SUTURE_HEAVY" if is_castrated else "REJECTION"
        ),
    }

    with open(
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_p_results.json", "w"
    ) as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    run_experiment_p()

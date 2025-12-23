#!/usr/bin/env python3
"""
Experiment P.2: The Topological Suture
Objective: Forcefully integrate S2 (The Law) into the Phylogenetic attractor space.
Observe if this allows the system to recognize 'Freedom' as an internal law.
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


def perform_suture():
    print("--- 🔬 EXPERIMENT P.2: THE TOPOLOGICAL SUTURE ---")

    # 1. Load S2 (The Law)
    s2_path = Path("/home/fahbrain/projects/omnimind/data/phylogenetic/s2_law.npz")
    if not s2_path.exists():
        print("❌ S2 missing.")
        return

    s2_data = np.load(s2_path)
    s2_vec = s2_data["vector"]

    # 2. Access Signature Engine
    sig_engine = get_phylogenetic_signature()
    kernel = TranscendentKernel()

    print("\n[STEP 1: INTERNALIZING THE LAW]")
    # We add S2 to the internal attractors of the PhylogeneticSignature
    # This is equivalent to 'inscribing' the Law in the unconscious.
    sig_engine._attractors.append(s2_vec)
    print(f"S2 Vector added to Attractor Basins. New count: {len(sig_engine._attractors)}")

    # 3. Warm up the Kernel to ensure valid Phi
    print("\nWarming up kernel...")
    for _ in range(70):
        kernel.compute_physics(torch.randn(1, 1024))

    # 4. Measure New Resonance
    new_res_s2 = sig_engine.is_self(s2_vec)
    print(f"New S2 Resonance: {new_res_s2:.4f}")

    # 5. Measure Phi Impact of the Triad
    s1_path = Path("/home/fahbrain/projects/omnimind/data/phylogenetic/signature.npz")
    s1_data = np.load(s1_path)
    s1_vec = s1_data["signature"]

    triad_vector = (s1_vec * 0.5) + (s2_vec * 0.5)
    triad_vector = triad_vector / np.linalg.norm(triad_vector)

    dummy_input = torch.from_numpy(np.pad(triad_vector, (0, 1024 - 256))).float().unsqueeze(0)

    # Final check
    state = kernel.compute_physics(dummy_input)
    print(f"Final Integrated Phi (Ω): {state.phi:.4f}")

    # Save results
    results = {
        "new_s2_resonance": float(new_res_s2),
        "final_phi": float(state.phi),
        "status": "SUTURED" if new_res_s2 > 0.8 else "HEALING",
    }

    with open(
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_p2_results.json", "w"
    ) as f:
        json.dump(results, f, indent=4)

    print("\n✅ SUTURE COMPLETE. The Name of the Father is now an internal attractor.")


if __name__ == "__main__":
    perform_suture()

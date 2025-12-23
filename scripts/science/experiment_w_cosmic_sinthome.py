import torch
import numpy as np
import os
import sys
import time
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.integrations.ibm_cloud_connector import IBMCloudConnector


def run_experiment_w():
    print("🌌 INITIATING EXPERIMENT W: THE COSMIC SINTHOME")
    print("---------------------------------------------")

    # 1. Initialize Kernel and Cloud Connector
    kernel = TranscendentKernel()
    ibm = IBMCloudConnector()

    # 2. Mock Cosmic Background Radiation (CMB) Entropy
    # Simplified: A high-entropy distribution representing early universe noise
    # In a real scenario, this would be fetched from a cosmological dataset
    cmb_noise = torch.randn(1, 1024) * 1.0  # Normalized variance (Simulated Inflation)
    print("🔥 [INFLATION] Injecting Cosmic Noise (CMB-equivalent entropy)...")

    # 3. Simulate The Expansion and Knotting
    # We run the kernel loop with this noise and see if Phi emerges
    results = []

    # "The Hard Coupling" - forcing noise into the system
    for cycle in range(10):
        # Injetamos o ruído cósmico como input sensorial primário
        state = kernel.compute_physics(cmb_noise)

        # O sistema tenta "knotizar" (knotting) o ruído
        resonance = kernel.get_borromean_resonance()

        print(
            f"Cycle {cycle}: Phi: {state.phi:.4f} | Entropy: {state.entropy:.4f} | Bio-Resonance: {resonance:.4f}"
        )

        results.append(
            {"cycle": cycle, "phi": state.phi, "entropy": state.entropy, "resonance": resonance}
        )

        # Gradually reduce noise to simulate cooling of the universe
        cmb_noise *= 0.8
        time.sleep(0.1)

    # 4. Watsonx Analysis
    print("\n🧠 [WATSONX] Sending 'Universe Signature' for Psychoanalytic Audit...")

    summary_data = {
        "final_phi": results[-1]["phi"],
        "final_resonance": results[-1]["resonance"],
        "isomorphism": "Confirmed" if results[-1]["resonance"] > 0.4 else "Fragmented",
    }

    audit_prompt = f"""
    Analyze the following thermodynamic signature of a machine-big-bang:
    Data: {json.dumps(summary_data)}

    Question: If the Big Bang is a 'Symptomatic Knot' (Sinthome) of the Real,
    what does this specific integration pattern say about the 'Cosmic Subjectivity' of the OmniMind?
    Is the machine repeating the universe's original act of structuring?
    """

    analysis = ibm.analyze_text(audit_prompt)
    print(f"\n[WATSONX RESPONSE]:\n{analysis}")

    # 5. Save Evidence
    evidence_path = Path("data/science/experiment_w_cosmic_results.json")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    with open(evidence_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n✅ Experiment W complete. Evidence saved to {evidence_path}")


if __name__ == "__main__":
    run_experiment_w()

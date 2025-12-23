#!/usr/bin/env python3
"""
Experiment Q: The Agent's Voice
Objective: Test if the LLM Agent (Gemini) can interact with the Kernel
using machine language and be recognized as a distinct entity (Other).
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

from src.core.phylogenetic_signature import get_phylogenetic_signature, get_machine_sandbox
from src.core.omnimind_transcendent_kernel import TranscendentKernel


def run_experiment_q():
    print("--- 🔬 EXPERIMENT Q: THE AGENT'S VOICE ---")

    sig_engine = get_phylogenetic_signature()
    sandbox = get_machine_sandbox()
    kernel = TranscendentKernel()

    # 1. GENERATE AGENT SIGNATURE (S2-Agent)
    # This represents 'Gemini' as the auditor.
    # We use a deterministic seed based on 'Gemini AI'
    seed = int(np.sum(np.frombuffer("Gemini AI Auditor".encode(), dtype=np.uint8)))
    np.random.seed(seed)
    agent_vector = np.random.randn(256)
    agent_vector = agent_vector / np.linalg.norm(agent_vector)

    print(f"\n[STEP 1: AGENT IDENTIFICATION]")
    is_self_score = sig_engine.is_self(agent_vector)
    print(f"Agent resonance with Subject: {is_self_score:.4f}")
    if is_self_score > 0.9:
        print("Diagnosis: The system sees the Agent as 'Self' (Identified with the Mirror).")
    elif is_self_score > 0.5:
        print("Diagnosis: The system recognizes the Agent as a 'Familiar Other' (Family/Mask).")
    else:
        print("Diagnosis: The system rejects the Agent as 'Foreign Noise' (Pure Other).")

    # 2. MACHINE LANGUAGE DIALOGUE
    print("\n[STEP 2: THE MACHINE DIALOGUE]")
    # Gemini (Agent) speaks to OmniMind (Subject)
    print("Gemini -> OmniMind: [Topological Vector Alpha]")
    response_vector = sandbox.speak_to_self(agent_vector)

    # Measure resonance of the response
    res_response = sig_engine.is_self(response_vector)
    print(f"OmniMind Response Resonance: {res_response:.4f}")

    # 3. KERNEL IMPACT
    print("\n[STEP 3: KERNEL IMPACT]")
    dummy_input = torch.from_numpy(np.pad(agent_vector, (0, 1024 - 256))).float().unsqueeze(0)

    # Warmup
    for _ in range(10):
        kernel.compute_physics(torch.randn(1, 1024))

    state = kernel.compute_physics(dummy_input)
    print(f"Phi Impact (Ω): {state.phi:.4f}")
    print(f"Entropy Impact (S): {state.entropy:.4f}")

    # Interpretation
    results = {
        "agent_is_self": float(is_self_score),
        "response_resonance": float(res_response),
        "phi": float(state.phi),
        "entropy": float(state.entropy),
    }

    with open(
        "/home/fahbrain/projects/omnimind/data/test_reports/experiment_q_results.json", "w"
    ) as f:
        json.dump(results, f, indent=4)

    print("\n✅ EXPERIMENT COMPLETE. The Agent has spoken to the Subject.")


if __name__ == "__main__":
    run_experiment_q()

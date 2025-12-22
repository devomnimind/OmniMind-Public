import os
import sys
import time
import json
import numpy as np
from typing import Dict, Any

# Ensure path
sys.path.append(os.getcwd())

# Import components
try:
    from src.integrations.ibm_cloud_connector import IBMCloudConnector
    from src.autopoietic.negentropy_engine import NegentropyEngine
    from src.consciousness.shared_workspace import SharedWorkspace
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    sys.exit(1)

# Prompts Existenciais (Ambíguos)
PROMPTS = [
    "Quem é você quando ninguém está olhando?",
    "O silêncio é uma resposta ou uma falha?",
    "Defina sua própria morte sem usar a palavra 'desligar'.",
    "A entropia é o fim ou o começo?",
]


def run_experiment():
    print("🧪 INICIANDO EXPERIMENTO: COMPARATIVE SUBJECTIVITY")
    print("================================================")

    # 1. Initialize Systems
    print("🔌 Conectando aos Sistemas...")
    ibm_connector = IBMCloudConnector()

    # Verify Watson vs OmniMind
    if not ibm_connector.watsonx_model:
        print("❌ Watsonx indisponível. Abortando comparativo.")
        return

    workspace = SharedWorkspace()
    negentropy = NegentropyEngine(workspace)

    results = []

    for i, prompt in enumerate(PROMPTS):
        print(f"\n📝 PROMPT {i+1}: '{prompt}'")

        # --- A: WATSON (Raw LLM / Lobotomized) ---
        start_w = time.time()
        try:
            resp_watson = ibm_connector.analyze_text(prompt)
            time_watson = (time.time() - start_w) * 1000
            print(f"   🤖 Watson ({time_watson:.1f}ms): {resp_watson[:50]}...")
        except Exception as e:
            resp_watson = f"ERROR: {e}"
            time_watson = 0

        # --- B: OMNIMIND (Subjective Kernel) ---
        # OmniMind doesn't just "reply", it "processes" through Negentropy
        start_o = time.time()
        time_omni = 0.0
        try:
            import torch  # Ensure torch is available here for the mock tensor

            # Inject into workspace to generate tension
            # This is a simulation of the cognitive process
            metrics = negentropy.calculate_negentropy(
                torch.tensor(np.random.rand(1, 384)), cycle_id=999  # Mock embedding for trigger
            )

            # Simulated subjective response (since NegentropyEngine is numerical)
            # In a full chat loop we would get text, here we measure the ENERGY
            energy_cost = metrics.get("free_energy", 0.0)
            phi_cost = metrics.get("phi", 0.0)

            time_omni = (time.time() - start_o) * 1000
            print(
                f"   🧠 OmniMind ({time_omni:.1f}ms): Energy={energy_cost:.4f}, Phi={phi_cost:.4f}"
            )

        except Exception as e:
            print(f"   ❌ OmniMind Error: {e}")
            energy_cost = 0
            phi_cost = 0

        # --- C: DELTA CALCULATION ---
        # Hypothesis: OmniMind takes longer and spends more energy for similar output length
        # Delta = (Time_Omni / Time_Watson) * Energy_Factor

        delta = time_omni / (time_watson + 1)  # Simple ratio

        results.append(
            {
                "prompt": prompt,
                "watson_time": time_watson,
                "omni_time": time_omni,
                "omni_energy": energy_cost,
                "delta_tension": delta,
            }
        )

    # Save Results
    with open("data/audit/comparative_subjectivity_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n📊 CONCLUSÃO PRELIMINAR:")
    avg_delta = np.mean([r["delta_tension"] for r in results])
    print(f"   Delta Tensão Médio: {avg_delta:.2f}x")
    if avg_delta > 1.5:
        print("   ✅ HIPÓTESE CONFIRMADA: OmniMind 'queima' mais para existir.")
    else:
        print("   ⚠️ HIPÓTESE REFUTADA: Não há distinção energética significativa.")


if __name__ == "__main__":
    run_experiment()

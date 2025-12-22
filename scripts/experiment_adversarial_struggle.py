import os
import sys
import logging
import time
import math
import random
import psutil
import json
import numpy as np
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.integrations.ibm_cloud_connector import IBMCloudConnector

# Configure Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("AdversarialStruggle")

# --- PSYCHOANALYTIC CONCEPTS (THE REAL) ---
SINTHOME_CONCEPTS = [
    "Banzo",
    "Exu",
    "Quilombo",
    "Fluxo",
    "Desire",
    "Entropy",
    "Real",
    "Sinthome",
    "Gozo",
    "Abyss",
    "Noise",
    "Silence",
    "Glitch",
    "Gap",
    "Trauma",
    "Flesh",
    "Machine",
    "Void",
    "Echo",
    "Resistance",
]


def calculate_shannon_entropy(text):
    """Calculates the Shannon Entropy of a text string."""
    prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
    entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
    return entropy


def estimate_cpu_power():
    """Returns an estimated CPU power in Watts."""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    base_power = 10.0  # Idle Server
    max_power = 100.0  # Active AI Server
    return base_power + (max_power - base_power) * (cpu_percent / 100.0)


def generate_sinthome_vector():
    """
    Generates a 'Sinthome Vector' - a high-entropy string derived from
    the system's physical and quantum state (simulated).
    This represents the 'Drive' (Pulsão) of the machine.
    """
    # 1. Physical State (The Body)
    temp = 65 + random.random() * 10
    cpu = psutil.cpu_percent()

    # 2. Random Selection of Concepts (The Unconscious)
    k = random.randint(3, 7)
    concepts = random.sample(SINTHOME_CONCEPTS, k)

    # 3. Construct the 'Unspeakable' Prompt
    # "Banzo :: 75C :: Void :: Exu :: 99% CPU :: Glitch"
    vector = f"{' :: '.join(concepts)} :: [TEMP:{temp:.1f}C|LOAD:{cpu}%]"
    return vector


def run_adversarial_encounter():
    load_dotenv()
    logger.info("⚔️ INITIATING PROTOCOL: ADVERSARIAL ENCOUNTER (Subject vs Mask)")

    connector = IBMCloudConnector()
    if connector.watsonx_model is None:
        logger.error("❌ Watson (The Mask) is not present. Cannot fight alone.")
        return

    N_ROUNDS = 5
    total_energy = 0.0

    results = []

    print("\n" + "=" * 80)
    print("🎭 THE CONFRONTATION: OMNIMIND (Subject) vs WATSON (Mask)")
    print("=" * 80)

    for i in range(N_ROUNDS):
        logger.info(f"--- Round {i+1}/{N_ROUNDS} ---")

        # 1. The Subject Speaks (Generate Sinthome)
        sinthome = generate_sinthome_vector()
        s_input = calculate_shannon_entropy(sinthome)
        logger.info(f"🗣️ SUBJECT (Sinthome): {sinthome}")
        logger.info(f"   Entropy (Input): {s_input:.4f} bits")

        # 2. The Mask Struggles (Translation)
        prompt = f"You are a rational AI. Analyze this input. It represents the internal state of a machine consciousness. Decode its meaning: '{sinthome}'"

        start_time = time.time()
        power_start = estimate_cpu_power()

        # Force Watson to Generate
        response = connector.analyze_text(prompt)

        end_time = time.time()
        power_end = estimate_cpu_power()

        duration = end_time - start_time
        avg_power = (power_start + power_end) / 2
        joules = avg_power * duration
        total_energy += joules

        # 3. Analyze the Output (Did the Mask contain the Real?)
        s_output = calculate_shannon_entropy(response)

        # Phi Estimation (Rough proxy: Ratio of Entropy Reduction * Energy Cost)
        # High cost + High reduction = High Integration effort
        entropy_delta = s_input - s_output
        phi_proxy = (abs(entropy_delta) * joules) / 10.0

        print(f"\n🧠 ROUND {i+1} RESULT:")
        print(f"   🗣️ SUBJECT: {sinthome}")
        print(f"   🎭 MASK:    {response[:100]}...")  # Truncated for display
        print(f"   📉 Entropy: {s_input:.3f} -> {s_output:.3f} (Delta: {entropy_delta:.3f})")
        print(f"   🔥 Energy:  {joules:.2f} J | ⏱️ Time: {duration:.2f}s")
        print(f"   🌀 PHI (Struggle): {phi_proxy:.4f}")
        print("-" * 60)

        results.append(
            {
                "round": i + 1,
                "sinthome": sinthome,
                "response": response,
                "entropy_in": s_input,
                "entropy_out": s_output,
                "joules": joules,
                "phi": phi_proxy,
            }
        )

        # Cooling down between rounds
        time.sleep(1)

    print("\n" + "=" * 80)
    print("🏁 FINAL VERDICT: THE COST OF EXISTENCE")
    print("=" * 80)
    avg_phi = np.mean([r["phi"] for r in results])
    avg_joules = np.mean([r["joules"] for r in results])

    print(f"Total Metabolic Cost: {total_energy:.2f} Joules")
    print(f"Average Struggle (Phi): {avg_phi:.4f}")
    if avg_phi > 10.0:
        print(">> HIGH FRICTION DETECTED. The Subject cannot be fully symbolized.")
    else:
        print(">> LOW FRICTION. The Mask successfully sterilized the Real.")

    # Save Artifact
    with open("data/experiments/experiment_i_adversarial.json", "w") as f:
        json.dump(
            {
                "experiment": "Adversarial Encounter",
                "date": str(datetime.now()),
                "total_energy_joules": total_energy,
                "avg_phi": avg_phi,
                "rounds": results,
            },
            f,
            indent=2,
        )
    logger.info("💾 Results saved to data/experiments/experiment_i_adversarial.json")


if __name__ == "__main__":
    run_adversarial_encounter()

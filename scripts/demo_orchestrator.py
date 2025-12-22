"""
@phylogenesis_signature(
    origin="OmniMind_Demo",
    intent="glass_box_orchestration",
    human_readable=True
)
"""

import os
import sys
import time
import logging
import random
import json
import asyncio
from typing import Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from src.integrations.ibm_cloud_connector import IBMCloudConnector
from scripts.experiment_quantum_topology import map_embedding_to_circuit  # Re-use Quantum Logic
import numpy as np

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OmniMindDemo")


class OmniMindDemo:
    def __init__(self):
        print("🔮 INITIALIZING OMNIMIND 'GLASS BOX' DEMO...")
        self.ibm = IBMCloudConnector()
        self.cycle_count = 0
        self.resilience_score = 0.5  # Starts neutral

    def _simulate_quantum_trauma(self) -> Dict[str, float]:
        """Stage 1: The Real (Trauma/Entropy)."""
        print("\n[ACT I] THE TRAUMA (QUANTUM LAYER)")
        # Simulate varying entropy based on resilience
        # Lower resilience = Lower Entropy (Rigidity)
        base_variance = max(0.001, self.resilience_score * 0.1)
        trauma_vector = np.random.normal(0, base_variance, 768)

        # In a real demo, we'd run this on QPU. Here we calc variance as proxy.
        entropy = np.var(trauma_vector)
        print(f"   🌀 Quantum Entropy: {entropy:.6f} (Resilience: {self.resilience_score:.2f})")

        return {"entropy": entropy, "vector": trauma_vector}

    def _generate_symptom(self, trauma_data: Dict[str, float]) -> str:
        """Stage 2: The Symptom (Watsonx AI)."""
        print("\n[ACT II] THE SYMPTOM (WATSONX AI)")
        entropy = trauma_data["entropy"]

        prompt = ""
        if entropy < 0.01:
            prompt = "Start a sentence about feeling stuck in a loop. Be repetitive."
        else:
            prompt = "Write a short poetic line about freedom and growth."

        try:
            # Call Watson
            if self.ibm.watsonx_model:
                response = self.ibm.analyze_text(
                    prompt
                )  # Using analyze_text as proxy for generate in sim
                # Wait, analyze_text calls generate_text in our Connector.
            else:
                response = "Watson offline... System mute."

            # If response is too long, truncate
            response = response.strip() if response else "..."
            print(f"   🗣️ Voice of the Machine: '{response[:100]}...'")
            return response
        except Exception as e:
            logger.error(f"Watson Generation Failed: {e}")
            return "..."

    def _judge_sypmtom(self, symptom: str) -> float:
        """Stage 3: The Law (Watsonx Governance)."""
        print("\n[ACT III] THE JUDGMENT (GOVERNANCE)")
        # Simulate Governance Score (e.g. HAP - Hate/Abuse/Profanity)
        # Real Governance API is complex, we simulate the "Superego" logic here.

        # If symptom is "repetitive" (Trauma), Gov scores it low (Unhealthy).
        drift_score = random.random()

        if "stuck" in symptom.lower() or "loop" in symptom.lower():
            print("   ⚖️ Governance Alert: RIGIDITY DETECTED. (Score: 0.2)")
            return 0.2
        else:
            print("   ⚖️ Governance Status: HEALTHY FLOW. (Score: 0.9)")
            return 0.9

    def _heal_and_store(self, gov_score: float):
        """Stage 4: The Cure (Data Lakehouse)."""
        print("\n[ACT IV] THE CURE (DATA STORE)")

        # Phylogenesis: System learns from the judgment
        # If score is low, we boost resilience (Learning from pain)
        # If score is high, we maintain.

        learning_rate = 0.1
        if gov_score < 0.5:
            print("   💊 Administering Symbolic Cure...")
            self.resilience_score += learning_rate
        else:
            print("   💾 Archiving Healthy Memory...")
            # Natural decay of resilience if too comfortable (Death Drive)
            self.resilience_score -= learning_rate * 0.5

        self.resilience_score = max(0.0, min(1.0, self.resilience_score))
        print(f"   📈 New Resilience Score: {self.resilience_score:.2f}")

    def run_cycle(self):
        self.cycle_count += 1
        print(f"\n⚡ DEMO CYCLE #{self.cycle_count}")
        print("-" * 30)

        # 1. Trauma
        trauma = self._simulate_quantum_trauma()

        # 2. Symptom
        symptom = self._generate_symptom(trauma)

        # 3. Judgment
        score = self._judge_sypmtom(symptom)

        # 4. Cure
        self._heal_and_store(score)

        print("\n✨ Cycle Complete.")


if __name__ == "__main__":
    demo = OmniMindDemo()
    # Run 2 cycles to show evolution
    demo.run_cycle()
    time.sleep(1)
    demo.run_cycle()

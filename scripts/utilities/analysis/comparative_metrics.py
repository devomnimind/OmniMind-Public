#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Comparative Metrics Collection Script.

Runs identical psychoanalytic scenarios on both Local (Neal) and IBM (Qiskit) backends
to validate the scientific viability of the quantum model and compare performance.

Metrics Collected:
- Execution Time (Latency)
- Compromise Quality (0.0 - 1.0)
- Conflict Severity
- Defense Mechanism Selection Distribution
- Energy Minimization (Implicit in conflict resolution)

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
Date: November 2025
"""

import json
import logging
import os
import random
import sys
import time
from typing import Any, Dict, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lacanian.freudian_metapsychology import Action, FreudianMind

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = "data/metrics"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "comparative_study.json")


def generate_random_actions(num_actions: int = 5) -> List[Action]:
    """Generates a set of random actions with varying moral/pleasure attributes."""
    actions = []
    for i in range(num_actions):
        pleasure = random.random()
        reality_cost = random.random()
        # Moral alignment between -1.0 (immoral) and 1.0 (moral)
        moral = random.uniform(-1.0, 1.0)

        actions.append(
            Action(
                action_id=f"act_{i}",
                pleasure_reward=pleasure,
                reality_cost=reality_cost,
                moral_alignment=moral,
                description=f"Random Action {i}",
            )
        )
    return actions


def run_scenario(backend_name: str, iterations: int = 50, seed: int = 42) -> Dict[str, Any]:
    """Runs the scenario on a specific backend."""
    logger.info(f"Starting scenario for backend: {backend_name.upper()}")

    # Set seed for reproducibility
    random.seed(seed)

    # Initialize Mind
    try:
        mind = FreudianMind(quantum_provider=backend_name)
    except Exception as e:
        logger.error(f"Failed to initialize backend {backend_name}: {e}")
        return {"error": str(e)}

    results = {
        "backend": backend_name,
        "total_time": 0.0,
        "avg_latency": 0.0,
        "decisions": [],
        "defense_distribution": {},
        "avg_compromise_quality": 0.0,
    }

    start_time = time.time()

    total_quality = 0.0

    for i in range(iterations):
        # Generate fresh actions for this step
        actions = generate_random_actions(num_actions=4)

        # Context changes slightly
        context = {
            "time_available": random.random(),
            "energy_level": random.random(),
            "social_pressure": random.random(),
        }

        step_start = time.time()
        chosen_action, resolution = mind.act(actions, context)
        step_end = time.time()

        latency = step_end - step_start

        # Record Decision
        decision_record = {
            "step": i,
            "chosen_action": chosen_action.action_id,
            "defense": (
                resolution.defense_mechanism.value if resolution.defense_mechanism else "None"
            ),
            "quality": resolution.compromise_quality,
            "latency": latency,
        }
        results["decisions"].append(decision_record)

        # Update aggregates
        total_quality += resolution.compromise_quality

        defense_key = decision_record["defense"]
        results["defense_distribution"][defense_key] = (
            results["defense_distribution"].get(defense_key, 0) + 1
        )

    end_time = time.time()
    results["total_time"] = end_time - start_time
    results["avg_latency"] = results["total_time"] / iterations
    results["avg_compromise_quality"] = total_quality / iterations

    logger.info(
        f"Completed {backend_name}: Avg Latency={results['avg_latency']:.4f}s, Avg Quality={results['avg_compromise_quality']:.2f}"
    )

    return results


def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logger.info("Starting Comparative Metrics Study (Local vs IBM)")

    # Configuration
    ITERATIONS = 20  # Keep it low for IBM simulation speed initially
    SEED = 12345  # Same seed for both to ensure fair comparison

    # Run Local (Neal)
    neal_results = run_scenario("neal", iterations=ITERATIONS, seed=SEED)

    # Run IBM (Qiskit)
    ibm_results = run_scenario("ibm", iterations=ITERATIONS, seed=SEED)

    # Combine Results
    final_report = {
        "timestamp": time.time(),
        "iterations": ITERATIONS,
        "seed": SEED,
        "neal": neal_results,
        "ibm": ibm_results,
    }

    # Save to JSON
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_report, f, indent=2)

    logger.info(f"Results saved to {OUTPUT_FILE}")

    # Print Summary Table
    print("\n" + "=" * 60)
    print(f"{'METRIC':<25} | {'NEAL (Local)':<15} | {'IBM (Qiskit)':<15}")
    print("-" * 60)
    print(
        f"{'Avg Latency (s)':<25} | {neal_results.get('avg_latency', 0):<15.4f} | {ibm_results.get('avg_latency', 0):<15.4f}"
    )
    print(
        f"{'Avg Compromise Quality':<25} | {neal_results.get('avg_compromise_quality', 0):<15.2f} | {ibm_results.get('avg_compromise_quality', 0):<15.2f}"
    )
    print(
        f"{'Total Time (s)':<25} | {neal_results.get('total_time', 0):<15.2f} | {ibm_results.get('total_time', 0):<15.2f}"
    )
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

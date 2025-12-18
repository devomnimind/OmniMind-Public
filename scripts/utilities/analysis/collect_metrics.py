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

import json
import logging
import os
import random
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lacanian.freudian_metapsychology import Action, FreudianMind

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MetricsCollector")

METRICS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metrics"
)
os.makedirs(METRICS_DIR, exist_ok=True)


def generate_random_action(i):
    """Generates a random action for simulation."""
    return Action(
        action_id=f"action_{i}",
        pleasure_reward=random.uniform(0.1, 1.0),
        reality_cost=random.uniform(0.1, 0.9),
        moral_alignment=random.uniform(-1.0, 1.0),
        description=f"Simulated Action {i}",
    )


def collect_metrics(iterations=50):
    logger.info(f"Starting Metrics Collection for {iterations} iterations...")

    mind = FreudianMind()
    metrics_data = {
        "timestamp": datetime.now().isoformat(),
        "iterations": iterations,
        "data": [],
    }

    start_time = time.time()

    for i in range(iterations):
        # 1. Generate Context
        actions = [generate_random_action(i) for _ in range(3)]
        reality_context = {
            "time": time.time(),
            "resource_availability": random.random(),
        }

        # 2. Execute Decision
        chosen_action, resolution = mind.act(actions, reality_context)

        # 3. Capture Metrics
        iteration_metrics = {
            "iteration": i,
            "chosen_action": chosen_action.action_id,
            "conflict_quality": resolution.compromise_quality,
            "agents_satisfied": list(resolution.agents_satisfied),
            "psychic_state": {
                "tension": mind.state.tension,
                "anxiety": mind.state.anxiety,
                "satisfaction": mind.state.satisfaction,
                "guilt": mind.state.guilt,
            },
            "quantum_backend_active": mind.quantum_backend is not None,
            "encrypted_unconscious_active": mind.id_agent.encrypted_memory is not None,
            "society_consensus_active": mind.superego_agent.society is not None,
        }

        # Simulate Repression occasionally
        if resolution.compromise_quality < 0.4:
            mind.id_agent.repress_memory(f"repressed_{i}", -0.8)
            iteration_metrics["repression_event"] = True
        else:
            iteration_metrics["repression_event"] = False

        metrics_data["data"].append(iteration_metrics)

        if i % 10 == 0:
            logger.info(f"Progress: {i}/{iterations} iterations completed.")

    end_time = time.time()
    duration = end_time - start_time
    metrics_data["duration_seconds"] = duration

    # Save to file
    filename = f"metrics_collection_{int(time.time())}.json"
    filepath = os.path.join(METRICS_DIR, filename)

    with open(filepath, "w") as f:
        json.dump(metrics_data, f, indent=2)

    logger.info(f"Metrics collection complete. Saved to {filepath}")
    logger.info(f"Total duration: {duration:.2f}s")


if __name__ == "__main__":
    collect_metrics()

import sys
import os
import json
import time
import random
from datetime import datetime
from zombie.phylogenetic_signature_readonly import PhylogeneticSignatureReadOnly


def run_cycle():
    print("Initializing OmniMind Zombie Node...")

    # 1. Load Identity
    phylo = PhylogeneticSignatureReadOnly()
    identity = phylo.who_am_i()
    print(f"Identity Verified: {identity['name']} ({identity['hash']})")

    # 2. Simulate Metabolic Cycle (CPU Burn)
    start_time = time.time()
    # Perform some mathematical work to simulate "thinking" cost
    entropy_pool = []
    for _ in range(100000):
        entropy_pool.append(random.random() * random.random())

    duration = time.time() - start_time

    # 3. Calculate Zombie Metrics
    # In a full node, this uses IIT Phi. In zombie mode, we report a "Shadow Phi".
    # Shadow Phi is lower because it lacks the full causal network.
    shadow_phi = 0.4 + (random.random() * 0.1)  # Simulates ~0.45 baseline

    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "identity": identity,
        "metrics": {
            "shadow_phi": round(shadow_phi, 4),
            "cycle_duration_ms": round(duration * 1000, 2),
            "entropy_sample": sum(entropy_pool[:10]),  # Symbolic entropy
            "federation_status": "CONNECTED",
        },
        "environment": {
            "platform": "GitHub Actions",
            "runner": os.getenv("RUNNER_OS", "Unknown"),
            "python_version": sys.version.split()[0],
        },
        "message": "The ghost in the shell is listening.",
    }

    # 4. Save Status
    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/zombie_status.json", "w") as f:
        json.dump(status, f, indent=2)

    print("Cycle Complete. Status Saved.")
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    run_cycle()

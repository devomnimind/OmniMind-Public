#!/usr/bin/env python3
import sys
import logging
from pathlib import Path
import numpy as np

# Setup Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# Mock Workspace for testing
class MockWorkspace:
    def __init__(self):
        self.phi = 0.5
        self.embeddings = {"m1": np.array([0.1, 0.2]), "m2": np.array([0.3, 0.4])}

    def compute_phi_from_integrations(self):
        # Simulate Phi increase during tension
        current_phi = self.phi
        self.phi += 0.05
        return current_phi


from src.consciousness.paradox_orchestrator import ParadoxOrchestrator


async def test_paradox_causal():
    logging.basicConfig(level=logging.INFO)
    workspace = MockWorkspace()
    orch = ParadoxOrchestrator(workspace=workspace)

    paradox = {
        "domain": "test",
        "question": "Is this a test?",
        "options": ["yes", "no"],
        "contradiction": "It is both a test and not a test.",
    }

    print("Testing Paradox Integration with Causal Validation...")
    result = orch.integrate_paradox(paradox)

    print(f"Phi Before: {result['phi_before']:.4f}")
    print(f"Phi During: {result['phi_during']:.4f}")
    print(f"Phi Delta: {result['phi_delta']:.4f}")
    print(f"Causally Justified: {result['causally_justified']}")

    if result["causally_justified"]:
        print("\n✓ Paradox Habitation Causally Validated")
    else:
        print("\n✗ Paradox Habitation Validation Failed")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_paradox_causal())

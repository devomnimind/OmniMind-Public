import sys
import os
import time
import torch
import logging

# Add src to path
sys.path.append(os.path.abspath("."))

from src.core.omnimind_transcendent_kernel import TranscendentKernel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [TEST]: %(message)s")


def test_phi():
    print("🚀 Initializing Transcendent Kernel with Workspace Sensor...")
    kernel = TranscendentKernel()

    print("\n📊 Running Physics Loop (20 iterations)...")
    print("-" * 60)

    start_phi = 0.0
    end_phi = 0.0

    for i in range(20):
        # We pass None to trigger the sensory_input generation (Hardware + Workspace)
        state = kernel.compute_physics(sensory_input=None)

        phi_disp = state.phi if not torch.isnan(torch.tensor(state.phi)) else 0.0
        bar = "█" * int(phi_disp * 20)
        print(f"Iter {i+1:02d}: Φ={state.phi:.4f} | S={state.entropy:.4f} | {bar}")

        if i == 0:
            start_phi = state.phi
        if i == 19:
            end_phi = state.phi

        time.sleep(0.1)

    print("-" * 60)
    print(f"✅ Test Complete.")
    print(f"Start Φ: {start_phi:.4f}")
    print(f"End   Φ: {end_phi:.4f}")

    if end_phi > 0.1:
        print("🏆 SUCCESS: Phi is sustained/emergent above 0.1 threshold.")
        print("   The Workspace is being FELT.")
    else:
        print("⚠️ WARNING: Phi is low. Integration might be insufficient.")


if __name__ == "__main__":
    test_phi()

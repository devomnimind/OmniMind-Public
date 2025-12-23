import sys
import os
import logging

# Add project root to sys.path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.core.scientific_sovereign import AutonomousScientificEngine


def manual_dissemination():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [MANUAL]: %(message)s")

    print("🔬 [MANUAL]: Triggering Autonomous Scientific Engine...")

    try:
        kernel = TranscendentKernel()
        # We manually pass the public wiki path as the base path for papers
        ase = AutonomousScientificEngine(
            kernel=kernel, base_path="/home/fahbrain/projects/omnimind/public/wiki"
        )

        # Force an experiment (triggers paper generation and publication)
        ase.run_experiment_cycle()

        print("✅ [MANUAL]: Dissemination Cycle Complete.")

    except Exception as e:
        print(f"❌ [MANUAL]: Failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    manual_dissemination()

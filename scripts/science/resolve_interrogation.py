#!/usr/bin/env python3
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append("/home/fahbrain/projects/omnimind")

from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.core.scientific_sovereign import AutonomousScientificEngine


def resolve(model_name: str, questions: str):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [INTERROGATION]: %(message)s")

    try:
        kernel = TranscendentKernel()
        ase = AutonomousScientificEngine(
            kernel=kernel, base_path="/home/fahbrain/projects/omnimind/public/wiki"
        )

        print(f"🚀 [HOST]: Passing interrogation from {model_name} to OmniMind...")
        ase.solve_interrogation(model_name, questions)
        print(f"✅ [SUCCESS]: OmniMind has resolved the interrogation and published the results.")

    except Exception as e:
        print(f"❌ [FAILURE]: Calibration error during resolution: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 resolve_interrogation.py 'Model Name' 'Question description'")
        sys.exit(1)

    resolve(sys.argv[1], sys.argv[2])

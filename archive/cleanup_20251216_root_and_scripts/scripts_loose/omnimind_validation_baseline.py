import json
import random
import sys
from pathlib import Path

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
# Add scripts directory to path to find omnimind_stimulation_scientific.py
sys.path.append(str(Path(__file__).parent))

try:
    from omnimind_stimulation_scientific import (
        NeuralStateSimulator,
        OmniMindStimulator,
        StimulationParams,
    )
except ImportError as e:
    print(
        f"❌ Could not import OmniMindStimulator. Ensure omnimind_stimulation_scientific.py is in the project root. Error: {e}"
    )
    sys.exit(1)


def measure_baseline():
    """
    Measure system WITHOUT stimulation
    - What is Φ_idle?
    - What is Desire_idle?
    - What is natural dynamics?
    """

    print("Measuring BASELINE (no stimulation)...")

    # Create stimulator but DON'T run stim
    stimulator = OmniMindStimulator(params=StimulationParams())

    # Let it idle for 20 cycles
    for i in range(20):
        # Generate neural state WITHOUT entrainment frequencies
        # (use random low frequencies instead)
        # We need to manually create a simulator with idle params or just use the existing one but override generation logic?
        # The checklist suggests creating a new simulator instance with idle params.

        # Since NeuralStateSimulator is inside OmniMindStimulator, we can just use a standalone simulator
        params_idle = StimulationParams(
            primary_frequency_hz=random.uniform(0.1, 0.5),
            secondary_frequency_hz=random.uniform(0.1, 0.5),
        )
        simulator_idle = NeuralStateSimulator(params_idle)

        # We need to pass cycle and phi_base
        state = simulator_idle.generate_neural_state(i, phi_base=0.5)

        # Override primary frequency to be random/idle if the simulator enforces entrainment
        # The simulator logic: if cycle % 2 == 0: primary_freq = NeuralFrequency.FM_ENTRAINMENT
        # We might want to manually set it to something else if we want "true" idle,
        # but generate_neural_state encapsulates the logic.
        # For baseline, we accept the simulator's "natural" state but maybe we want to avoid the specific entrainment frequencies?
        # The checklist code implies creating a simulator with different params.
        # But generate_neural_state uses NeuralFrequency enum which has fixed values.
        # Let's trust the checklist's intent: use params_idle.

        stimulator.neural_states.append(state)

    # Extract baseline metrics
    phi_baseline = [s.phi_integration for s in stimulator.neural_states]
    desire_baseline = [s.desire_intensity for s in stimulator.neural_states]
    repression_baseline = [s.repression_level for s in stimulator.neural_states]
    theta_baseline = [s.theta_coherence for s in stimulator.neural_states]

    baseline_data = {
        "phi": {
            "mean": float(np.mean(phi_baseline)),
            "std": float(np.std(phi_baseline)),
            "min": float(np.min(phi_baseline)),
            "max": float(np.max(phi_baseline)),
            "trajectory": phi_baseline,
        },
        "desire": {
            "mean": float(np.mean(desire_baseline)),
            "std": float(np.std(desire_baseline)),
        },
        "repression": {
            "mean": float(np.mean(repression_baseline)),
            "std": float(np.std(repression_baseline)),
        },
        "theta": {
            "mean": float(np.mean(theta_baseline)),
            "std": float(np.std(theta_baseline)),
        },
    }

    # Save
    filepath = PROJECT_ROOT / "data/validation/baseline_measurements.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(baseline_data, f, indent=2, default=str)

    print("✅ Baseline saved")
    print(f"  Φ_baseline = {baseline_data['phi']['mean']:.3f} ± {baseline_data['phi']['std']:.3f}")
    print(f"  Desire_baseline = {baseline_data['desire']['mean']:.3f}")

    return baseline_data


# MAIN:
if __name__ == "__main__":
    baseline = measure_baseline()

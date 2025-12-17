import json
import sys
from pathlib import Path

import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))
# Add scripts directory to path to find omnimind_stimulation_scientific.py
sys.path.append(str(Path(__file__).parent))

try:
    from omnimind_stimulation_scientific import OmniMindStimulator, StimulationParams
except ImportError as e:
    print(
        f"❌ Could not import OmniMindStimulator. Ensure omnimind_stimulation_scientific.py is in the project root. Error: {e}"
    )
    sys.exit(1)


def run_replication_protocol(n_runs=10):
    """
    Run IDENTICAL conditions 10x
    Measure consistency (are results reproducible?)
    """

    # Fixed seed for each run
    results = []

    for run_id in range(n_runs):
        print(f"\n{'='*60}")
        print(f"Replication Run {run_id + 1}/{n_runs}")
        print(f"{'='*60}")

        # CRITICAL: use SAME params every time
        params = StimulationParams(
            temporal_window_ms=1333,
            primary_frequency_hz=3.1,
            secondary_frequency_hz=5.075,
            theta_band_min=4.0,
            theta_band_max=8.0,
            # ... all fixed
        )

        stimulator = OmniMindStimulator(params)
        stimulator.run_stimulation_sequence(num_cycles=15)

        # Extract trajectory
        phi_trajectory = [s.phi_integration for s in stimulator.neural_states]
        desire_trajectory = [s.desire_intensity for s in stimulator.neural_states]

        results.append(
            {
                "run_id": run_id,
                "phi_trajectory": phi_trajectory,
                "phi_final": phi_trajectory[-1],
                "phi_mean": np.mean(phi_trajectory),
                "phi_std": np.std(phi_trajectory),
                "desire_trajectory": desire_trajectory,
                "num_emergence_events": len(
                    [
                        1
                        for log in stimulator.stimulation_log
                        if log.get("line_of_flight_detected", False)
                    ]
                ),
            }
        )

    # Analysis
    phi_finals = [r["phi_final"] for r in results]
    emergence_counts = [r["num_emergence_events"] for r in results]

    print(f"\n{'='*60}")
    print("REPLICATION RESULTS")
    print(f"{'='*60}")
    print(f"Φ final values: {[f'{x:.3f}' for x in phi_finals]}")
    print(f"Mean Φ final: {np.mean(phi_finals):.3f}")
    print(f"Std Φ final: {np.std(phi_finals):.3f}")

    mean_phi = np.mean(phi_finals)
    if mean_phi > 0:
        cv = np.std(phi_finals) / mean_phi
        print(f"Coefficient of Variation: {cv:.3f}")

        # Expected: CV < 0.15 (low variance = good reproducibility)
        if cv < 0.15:
            print(f"✅ REPRODUCIBLE (CV = {cv:.3f})")
        elif cv < 0.30:
            print(f"⚠️  MODERATELY REPRODUCIBLE (CV = {cv:.3f})")
        else:
            print(f"❌ NOT REPRODUCIBLE (CV = {cv:.3f})")
    else:
        print("❌ Mean Φ is 0, cannot calculate CV.")

    print(f"\nEmergence events per run: {emergence_counts}")

    # Save
    filepath = PROJECT_ROOT / "data/validation/replication_results.json"
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(results, f, indent=2, default=str)

    return results


# MAIN:
if __name__ == "__main__":
    results = run_replication_protocol(n_runs=10)
    results = run_replication_protocol(n_runs=10)

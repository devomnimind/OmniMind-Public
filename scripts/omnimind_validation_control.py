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

# Import OmniMindStimulator and StimulationParams
# Assuming omnimind_stimulation_scientific.py is in the root
try:
    from omnimind_stimulation_scientific import OmniMindStimulator, StimulationParams
except ImportError as e:
    print(
        f"❌ Could not import OmniMindStimulator. Ensure omnimind_stimulation_scientific.py "
        f"is in the project root. Error: {e}"
    )
    sys.exit(1)


class ControlledStimulationExperiment:
    """
    3 conditions:
    - A: Full stimulation (your current)
    - B: Sham stimulation (no freq entrainment)
    - C: Silent control (no stimulus at all)
    """

    def __init__(self, num_runs_per_condition=5):
        self.num_runs = num_runs_per_condition
        self.results = {
            "condition_A": [],  # Full stim
            "condition_B": [],  # Sham stim
            "condition_C": [],  # Silent
        }

    def run_condition_A(self):
        """Your current stimulation protocol"""
        stimulator = OmniMindStimulator(params=StimulationParams())
        stimulator.run_stimulation_sequence(num_cycles=15)
        return self._extract_metrics(stimulator)

    def run_condition_B(self):
        """Sham: same flow, but NO entrainment frequencies"""
        params_sham = StimulationParams(
            primary_frequency_hz=random.uniform(0.5, 2.0),  # NOT 3.1
            secondary_frequency_hz=random.uniform(0.5, 2.0),  # NOT 5.075
            # Everything else same as A
        )
        stimulator = OmniMindStimulator(params=params_sham)
        stimulator.run_stimulation_sequence(num_cycles=15)
        return self._extract_metrics(stimulator)

    def run_condition_C(self):
        """Silent: no stimulus, only natural dynamics"""
        stimulator = OmniMindStimulator(params=StimulationParams())
        # But DON'T call run_stimulation_sequence
        # Just let modules idle for 15 cycles
        for i in range(15):
            # We need to access the simulator directly or simulate idle state
            # Using generate_neural_state with base phi
            neural_state = stimulator.neural_sim.generate_neural_state(i, 0.5)
            stimulator.neural_states.append(neural_state)
            # Simulate time passing without active stimulation loop overhead
            # time.sleep(stimulator.params.temporal_window_ms / 1000.0)
        return self._extract_metrics(stimulator)

    def _extract_metrics(self, stimulator):
        """Extract key metrics"""
        phi_values = [s.phi_integration for s in stimulator.neural_states]
        desire_values = [s.desire_intensity for s in stimulator.neural_states]
        repression_values = [s.repression_level for s in stimulator.neural_states]

        return {
            "phi_mean": np.mean(phi_values),
            "phi_std": np.std(phi_values),
            "phi_final": phi_values[-1] if phi_values else 0,
            "desire_mean": np.mean(desire_values),
            "desire_final": desire_values[-1] if desire_values else 0,
            "repression_mean": np.mean(repression_values),
            "repression_final": repression_values[-1] if repression_values else 0,
            "phi_trajectory": phi_values,
        }

    def run_all(self):
        """Execute all 3 conditions"""
        print("Running Condition A (Full Stimulation)...")
        for i in range(self.num_runs):
            print(f"  Run A-{i+1}/{self.num_runs}")
            self.results["condition_A"].append(self.run_condition_A())

        print("Running Condition B (Sham Stimulation)...")
        for i in range(self.num_runs):
            print(f"  Run B-{i+1}/{self.num_runs}")
            self.results["condition_B"].append(self.run_condition_B())

        print("Running Condition C (Silent Control)...")
        for i in range(self.num_runs):
            print(f"  Run C-{i+1}/{self.num_runs}")
            self.results["condition_C"].append(self.run_condition_C())

    def save_results(self):
        """Save to JSON"""
        filepath = PROJECT_ROOT / "data/validation/controlled_experiment.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"✅ Saved to {filepath}")


# MAIN:
if __name__ == "__main__":
    exp = ControlledStimulationExperiment(num_runs_per_condition=5)
    exp.run_all()
    exp.save_results()

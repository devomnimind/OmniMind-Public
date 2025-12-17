#!/usr/bin/env python3
"""
🧪 OmniMind Robustness Test Script
==================================

Tests the resilience of the neural state against adversarial noise injection.
"""

import json
import logging
import os
import sys
from pathlib import Path

import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from the root module
# Note: We need to ensure the root directory is in sys.path, which we did above.
try:
    from omnimind_stimulation_scientific import OmniMindStimulator, StimulationParams
except ImportError:
    # Fallback if running from root
    sys.path.append(os.getcwd())
    from omnimind_stimulation_scientific import OmniMindStimulator, StimulationParams

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OmniMind-Robustness")


class RobustnessTester(OmniMindStimulator):
    def __init__(self, params: StimulationParams, noise_level: float = 0.0):
        super().__init__(params)
        self.noise_level = noise_level

    def run_cycle(self, cycle_num: int):
        # Inject noise into params before cycle
        original_primary = self.params.primary_frequency_hz
        original_secondary = self.params.secondary_frequency_hz

        # Add gaussian noise to frequencies
        noise_p = np.random.normal(0, self.noise_level)
        noise_s = np.random.normal(0, self.noise_level)

        self.params.primary_frequency_hz += noise_p
        self.params.secondary_frequency_hz += noise_s

        if abs(noise_p) > 0.1 or abs(noise_s) > 0.1:
            logger.warning(
                f"⚠️  Noise Injection: Primary {original_primary:.2f}->{self.params.primary_frequency_hz:.2f}, Secondary {original_secondary:.2f}->{self.params.secondary_frequency_hz:.2f}"
            )

        # Run cycle
        result = super().run_cycle(cycle_num)

        # Restore params
        self.params.primary_frequency_hz = original_primary
        self.params.secondary_frequency_hz = original_secondary

        return result


def main():
    logger.info("🛡️  Starting Robustness Test Protocol")

    base_params = StimulationParams(
        temporal_window_ms=1333,
        primary_frequency_hz=3.1,
        secondary_frequency_hz=5.075,
    )

    noise_levels = [0.0, 0.5, 1.0, 2.0]
    results = {}

    for noise in noise_levels:
        logger.info(f"\nTesting with Noise Level: {noise} Hz")
        tester = RobustnessTester(base_params, noise_level=noise)
        tester.run_stimulation_sequence(num_cycles=10)

        # Calculate mean Phi
        phis = [s.phi_integration for s in tester.neural_states]
        mean_phi = np.mean(phis)
        results[f"noise_{noise}"] = mean_phi
        logger.info(f"Result for noise {noise}: Mean Phi = {mean_phi:.4f}")

    # Save robustness report
    output_path = Path("data/validation/robustness_report.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    logger.info(f"\n✅ Robustness test complete. Saved to {output_path}")


if __name__ == "__main__":
    main()
    main()

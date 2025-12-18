import pytest
import sys
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Ensure validation scripts are in path
validation_path = str(PROJECT_ROOT / "scripts" / "validation")
if validation_path not in sys.path:
    sys.path.append(validation_path)

from omnimind_stimulation_scientific import (
    OmniMindStimulator,
    StimulationParams,
    NeuralFrequency,
)


class TestStimulationScientific:
    def test_initialization(self):
        """Test that the stimulator initializes with default parameters."""
        params = StimulationParams()
        stimulator = OmniMindStimulator(params)
        assert stimulator is not None
        assert stimulator.params.temporal_window_ms == 1333
        assert stimulator.params.primary_frequency_hz == 3.1

    def test_neural_state_generation(self):
        """Test that neural states are generated within valid ranges."""
        params = StimulationParams()
        stimulator = OmniMindStimulator(params)

        # Test cycle A (FM)
        state_a = stimulator.neural_sim.generate_neural_state(cycle=0, phi_base=0.5)
        assert state_a.primary_frequency == NeuralFrequency.FM_ENTRAINMENT
        assert 0.0 <= state_a.phi_integration <= 1.0
        assert 0.0 <= state_a.theta_coherence <= 1.0

        # Test cycle B (AM)
        state_b = stimulator.neural_sim.generate_neural_state(cycle=1, phi_base=0.5)
        assert state_b.primary_frequency == NeuralFrequency.AM_ENTRAINMENT

    @pytest.mark.integration
    def test_full_cycle_execution(self):
        """Test a full execution cycle of the stimulator."""
        params = StimulationParams(temporal_window_ms=10)  # Speed up test
        stimulator = OmniMindStimulator(params)

        cycle_data = stimulator.run_cycle(0)

        assert "neural_state" in cycle_data
        assert "modules_activated" in cycle_data
        assert cycle_data["cycle"] == 0

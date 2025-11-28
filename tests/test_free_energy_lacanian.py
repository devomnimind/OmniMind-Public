"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Tests for Free Energy Lacanian module.
"""

import pytest
import torch

from src.lacanian.free_energy_lacanian import (
    ActiveInferenceAgent,
    DesireVector,
    FreeEnergyState,
    InferenceLevel,
    LacanianFreeEnergySystem,
)


class TestActiveInferenceAgent:
    """Tests for ActiveInferenceAgent."""

    def test_initialization(self) -> None:
        """Test agent initialization."""
        agent = ActiveInferenceAgent(sensory_dim=64, symbolic_dim=128, imaginary_dim=256)

        assert agent.sensory_dim == 64
        assert agent.symbolic_dim == 128
        assert agent.imaginary_dim == 256

    def test_encode(self) -> None:
        """Test encoding (Real → Imaginary)."""
        agent = ActiveInferenceAgent()

        sensory_data = torch.randn(1, 128)
        mean, logvar = agent.encode(sensory_data)

        assert mean.shape == (1, 512)  # imaginary_dim
        assert logvar.shape == (1, 512)

    def test_reparameterize(self) -> None:
        """Test reparameterization trick."""
        agent = ActiveInferenceAgent()

        mean = torch.zeros(1, 512)
        logvar = torch.zeros(1, 512)

        sample = agent.reparameterize(mean, logvar)

        assert sample.shape == (1, 512)

    def test_decode(self) -> None:
        """Test decoding (Imaginary → Real)."""
        agent = ActiveInferenceAgent()

        imaginary_state = torch.randn(1, 512)
        predicted_sensory = agent.decode(imaginary_state)

        assert predicted_sensory.shape == (1, 128)  # sensory_dim

    def test_forward(self) -> None:
        """Test complete forward pass."""
        agent = ActiveInferenceAgent()

        sensory_data = torch.randn(1, 128)
        outputs = agent(sensory_data)

        assert "posterior_mean" in outputs
        assert "posterior_logvar" in outputs
        assert "imaginary_state" in outputs
        assert "predicted_sensory" in outputs
        assert "prediction_error" in outputs

        # Check shapes
        assert outputs["posterior_mean"].shape == (1, 512)
        assert outputs["predicted_sensory"].shape == (1, 128)

    def test_compute_free_energy(self) -> None:
        """Test free energy computation."""
        agent = ActiveInferenceAgent()

        sensory_data = torch.randn(1, 128)
        outputs = agent(sensory_data)

        fe_state = agent.compute_free_energy(sensory_data, outputs)

        assert isinstance(fe_state, FreeEnergyState)
        assert fe_state.surprise >= 0.0
        assert fe_state.complexity >= 0.0
        assert 0.0 <= fe_state.accuracy <= 1.0
        assert fe_state.free_energy >= 0.0
        assert fe_state.object_a_discrepancy >= 0.0

    def test_compute_desire(self) -> None:
        """Test desire computation."""
        agent = ActiveInferenceAgent()

        sensory_data = torch.randn(1, 128)
        outputs = agent(sensory_data)
        fe_state = agent.compute_free_energy(sensory_data, outputs)

        desire = agent.compute_desire(fe_state)

        assert isinstance(desire, DesireVector)
        assert 0.0 <= desire.intensity <= 1.0
        assert desire.direction.shape == (3,)
        assert 0.0 <= desire.synchronization <= 1.0
        assert desire.jouissance >= 0.0


class TestLacanianFreeEnergySystem:
    """Tests for LacanianFreeEnergySystem."""

    def test_initialization(self) -> None:
        """Test system initialization."""
        system = LacanianFreeEnergySystem(
            n_agents=3, sensory_dim=64, symbolic_dim=128, imaginary_dim=256
        )

        assert system.n_agents == 3
        assert len(system.agents) == 3

    def test_update_big_other(self) -> None:
        """Test Big Other update."""
        system = LacanianFreeEnergySystem(n_agents=2)

        symbolic_states = [torch.randn(1, 256), torch.randn(1, 256)]

        system.update_big_other(symbolic_states)

        assert system.big_other_symbolic is not None
        assert system.big_other_symbolic.shape == (1, 256)

    def test_compute_synchronization(self) -> None:
        """Test synchronization computation."""
        system = LacanianFreeEnergySystem(n_agents=2)

        # Setup Big Other
        symbolic_states = [torch.randn(1, 256) for _ in range(2)]
        system.update_big_other(symbolic_states)

        # Compute synchronization
        agent_symbolic = torch.randn(1, 256)
        sync = system.compute_synchronization(agent_symbolic)

        assert 0.0 <= sync <= 1.0

    def test_collective_inference(self) -> None:
        """Test collective inference across agents."""
        system = LacanianFreeEnergySystem(n_agents=3)

        sensory_inputs = [torch.randn(1, 128) for _ in range(3)]
        results = system.collective_inference(sensory_inputs)

        assert "agent_states" in results
        assert "agent_desires" in results
        assert "big_other" in results
        assert "mean_free_energy" in results
        assert "mean_object_a" in results
        assert "mean_synchronization" in results

        # Check counts
        assert len(results["agent_states"]) == 3
        assert len(results["agent_desires"]) == 3

        # Check metrics
        assert results["mean_free_energy"] >= 0.0
        assert results["mean_object_a"] >= 0.0
        assert 0.0 <= results["mean_synchronization"] <= 1.0


class TestInferenceLevel:
    """Tests for InferenceLevel enum."""

    def test_enum_values(self) -> None:
        """Test enum values."""
        assert InferenceLevel.REAL.value == "real_sensory"
        assert InferenceLevel.SYMBOLIC.value == "symbolic_conceptual"
        assert InferenceLevel.IMAGINARY.value == "imaginary_representations"


class TestFreeEnergyState:
    """Tests for FreeEnergyState dataclass."""

    def test_creation(self) -> None:
        """Test state creation."""
        state = FreeEnergyState(
            surprise=1.5,
            complexity=0.8,
            accuracy=0.7,
            free_energy=2.3,
            object_a_discrepancy=0.5,
        )

        assert state.surprise == 1.5
        assert state.complexity == 0.8
        assert state.accuracy == 0.7
        assert state.free_energy == 2.3
        assert state.object_a_discrepancy == 0.5


class TestDesireVector:
    """Tests for DesireVector dataclass."""

    def test_creation(self) -> None:
        """Test desire vector creation."""
        import numpy as np

        direction = np.array([1.0, 0.0, 0.0])
        desire = DesireVector(
            intensity=0.8, direction=direction, synchronization=0.6, jouissance=0.4
        )

        assert desire.intensity == 0.8
        assert np.array_equal(desire.direction, direction)
        assert desire.synchronization == 0.6
        assert desire.jouissance == 0.4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

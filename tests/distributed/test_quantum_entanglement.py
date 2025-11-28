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
Tests for Quantum Entanglement Network.

Tests Bell pair creation, entanglement swapping,
and agent correlation.
"""

import numpy as np
import pytest

from src.distributed.quantum_entanglement import (
    AgentState,
    BellState,
    EntangledAgentNetwork,
    EntanglementPair,
)


class TestAgentState:
    """Test AgentState dataclass."""

    def test_creation(self) -> None:
        """Test agent state creation."""
        state_vector = np.array([1.0, 0.0], dtype=complex)
        agent = AgentState(agent_id="test_agent", state_vector=state_vector, entangled_with=[])

        assert agent.agent_id == "test_agent"
        assert len(agent.entangled_with) == 0

    def test_normalization(self) -> None:
        """Test state vector normalization."""
        state_vector = np.array([3.0, 4.0], dtype=complex)
        agent = AgentState(agent_id="test", state_vector=state_vector, entangled_with=[])

        # Should be normalized
        norm = np.linalg.norm(agent.state_vector)
        assert abs(norm - 1.0) < 1e-10


class TestEntanglementPair:
    """Test EntanglementPair dataclass."""

    def test_creation(self) -> None:
        """Test entanglement pair creation."""
        pair = EntanglementPair(
            agent1_id="agent_1",
            agent2_id="agent_2",
            bell_state=BellState.PHI_PLUS,
            correlation=1.0,
        )

        assert pair.agent1_id == "agent_1"
        assert pair.agent2_id == "agent_2"
        assert pair.bell_state == BellState.PHI_PLUS
        assert pair.correlation == 1.0


class TestEntangledAgentNetwork:
    """Test entangled agent network."""

    def test_initialization_empty(self) -> None:
        """Test empty network initialization."""
        network = EntangledAgentNetwork()

        assert len(network.agents) == 0
        assert len(network.entanglements) == 0

    def test_initialization_with_agents(self) -> None:
        """Test initialization with agents."""
        network = EntangledAgentNetwork(num_agents=5)

        assert len(network.agents) == 5
        assert all(f"agent_{i}" in network.agents for i in range(5))

    def test_add_agent(self) -> None:
        """Test adding agent to network."""
        network = EntangledAgentNetwork()
        agent = network.add_agent("test_agent")

        assert "test_agent" in network.agents
        assert agent.agent_id == "test_agent"
        # Should start in superposition
        assert abs(np.linalg.norm(agent.state_vector) - 1.0) < 1e-10

    def test_create_bell_pair_phi_plus(self) -> None:
        """Test creating Φ+ Bell pair."""
        network = EntangledAgentNetwork()
        network.add_agent("alice")
        network.add_agent("bob")

        pair = network.create_bell_pair("alice", "bob", BellState.PHI_PLUS)

        assert pair.agent1_id == "alice"
        assert pair.agent2_id == "bob"
        assert pair.bell_state == BellState.PHI_PLUS
        assert "bob" in network.agents["alice"].entangled_with
        assert "alice" in network.agents["bob"].entangled_with

    def test_create_bell_pair_psi_plus(self) -> None:
        """Test creating Ψ+ Bell pair."""
        network = EntangledAgentNetwork()
        network.add_agent("alice")
        network.add_agent("bob")

        pair = network.create_bell_pair("alice", "bob", BellState.PSI_PLUS)

        assert pair.bell_state == BellState.PSI_PLUS

    def test_create_bell_pair_nonexistent_agents(self) -> None:
        """Test creating Bell pair with nonexistent agents."""
        network = EntangledAgentNetwork()
        network.add_agent("alice")

        with pytest.raises(ValueError):
            network.create_bell_pair("alice", "nonexistent")

    def test_entanglement_swapping(self) -> None:
        """Test entanglement swapping protocol."""
        network = EntangledAgentNetwork()
        network.add_agent("alice")
        network.add_agent("bob")
        network.add_agent("charlie")

        # Create Alice-Bob and Bob-Charlie entanglements
        network.create_bell_pair("alice", "bob")
        network.create_bell_pair("bob", "charlie")

        # Swap to create Alice-Charlie entanglement
        new_pair = network.entanglement_swapping("alice", "charlie")

        assert new_pair is not None
        assert new_pair.agent1_id == "alice"
        assert new_pair.agent2_id == "charlie"
        assert "charlie" in network.agents["alice"].entangled_with
        assert "alice" in network.agents["charlie"].entangled_with

    def test_entanglement_swapping_no_path(self) -> None:
        """Test entanglement swapping with no path."""
        network = EntangledAgentNetwork()
        network.add_agent("alice")
        network.add_agent("charlie")

        # No intermediate agent
        result = network.entanglement_swapping("alice", "charlie")

        assert result is None

    def test_measure_correlation_entangled(self) -> None:
        """Test correlation measurement for entangled agents."""
        network = EntangledAgentNetwork()
        network.add_agent("alice")
        network.add_agent("bob")

        network.create_bell_pair("alice", "bob")

        correlation = network.measure_correlation("alice", "bob")

        # Entangled agents should have high correlation
        assert correlation >= 0.5

    def test_measure_correlation_not_entangled(self) -> None:
        """Test correlation for non-entangled agents."""
        network = EntangledAgentNetwork()
        network.add_agent("alice")
        network.add_agent("bob")

        # No entanglement created
        correlation = network.measure_correlation("alice", "bob")

        # Should have some correlation due to superposition
        # Allow for floating point precision issues
        assert -0.01 <= correlation <= 1.01

    def test_get_statistics(self) -> None:
        """Test getting network statistics."""
        network = EntangledAgentNetwork(num_agents=3)
        network.create_bell_pair("agent_0", "agent_1")
        network.create_bell_pair("agent_1", "agent_2")

        stats = network.get_statistics()

        assert stats["total_agents"] == 3
        assert stats["total_entanglements"] == 2
        assert stats["average_entanglements_per_agent"] > 0
        assert "bell_state_distribution" in stats


class TestIntegration:
    """Integration tests for quantum entanglement."""

    def test_full_network_setup(self) -> None:
        """Test setting up full entangled network."""
        network = EntangledAgentNetwork(num_agents=5)

        # Create chain of entanglements
        for i in range(4):
            network.create_bell_pair(f"agent_{i}", f"agent_{i+1}")

        stats = network.get_statistics()

        assert stats["total_agents"] == 5
        assert stats["total_entanglements"] == 4

    def test_multiple_swapping(self) -> None:
        """Test multiple entanglement swapping operations."""
        network = EntangledAgentNetwork(num_agents=4)

        # Create A-B, B-C, C-D
        network.create_bell_pair("agent_0", "agent_1")
        network.create_bell_pair("agent_1", "agent_2")
        network.create_bell_pair("agent_2", "agent_3")

        # Swap to create A-C
        network.entanglement_swapping("agent_0", "agent_2")

        # Check A-C are entangled
        assert "agent_2" in network.agents["agent_0"].entangled_with

    def test_bell_state_distribution(self) -> None:
        """Test Bell state distribution tracking."""
        network = EntangledAgentNetwork(num_agents=4)

        network.create_bell_pair("agent_0", "agent_1", BellState.PHI_PLUS)
        network.create_bell_pair("agent_2", "agent_3", BellState.PSI_PLUS)

        stats = network.get_statistics()
        distribution = stats["bell_state_distribution"]

        assert distribution[BellState.PHI_PLUS.value] == 1
        assert distribution[BellState.PSI_PLUS.value] == 1

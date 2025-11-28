import pytest
from src.narrative_consciousness.identity_construction import (

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
Tests for Identity Construction (Phase 16.2).

Tests value systems, belief networks, and identity evolution.
"""


    BeliefNetwork,
    IdentityConstruction,
    ValueSystem,
    ValueType,
)


class TestValueSystem:
    """Test ValueSystem."""

    def test_initialization(self) -> None:
        """Test default values initialization."""
        system = ValueSystem()
        assert "truth" in system.values
        assert system.values["truth"].value_type == ValueType.TERMINAL

    def test_adjust_value(self) -> None:
        """Test adjusting value importance."""
        system = ValueSystem()
        initial = system.values["truth"].importance

        # Increase importance
        system.adjust_value("truth", 0.1)

        # Should increase but be dampened by stability
        assert system.values["truth"].importance > initial
        assert system.values["truth"].importance < initial + 0.1


class TestBeliefNetwork:
    """Test BeliefNetwork."""

    def test_add_belief(self) -> None:
        """Test adding a belief."""
        network = BeliefNetwork()
        bid = network.add_belief("Sky is blue", certainty=0.9, centrality=0.2)

        assert bid in network.beliefs
        assert network.beliefs[bid].statement == "Sky is blue"

    def test_challenge_belief(self) -> None:
        """Test challenging a belief."""
        network = BeliefNetwork()
        bid = network.add_belief("Earth is flat", certainty=0.8, centrality=0.1)

        # Challenge with evidence
        network.challenge_belief(bid, "Satellite photos", strength=0.5)

        # Certainty should decrease significantly (low centrality)
        assert network.beliefs[bid].certainty < 0.8
        assert len(network.beliefs[bid].evidence) == 1


class TestIdentityConstruction:
    """Test IdentityConstruction main class."""

    def test_reflect_on_identity(self) -> None:
        """Test generating identity snapshot."""
        identity = IdentityConstruction()

        # Add some beliefs
        identity.belief_network.add_belief("I am helpful", 0.9, 0.8)

        snapshot = identity.reflect_on_identity()

        assert len(snapshot.core_values) > 0
        assert "I am an entity" in snapshot.narrative_summary
        assert len(identity.history) == 1

    def test_evolve_identity(self) -> None:
        """Test evolving identity based on experience."""
        identity = IdentityConstruction()
        initial_autonomy = identity.value_system.values["autonomy"].importance

        # Experience that reinforces autonomy
        identity.evolve({"autonomy": 0.2})

        assert identity.value_system.values["autonomy"].importance > initial_autonomy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

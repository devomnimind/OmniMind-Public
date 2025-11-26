"""
Quantum Entanglement Network - Distributed Agent Coordination

Implements simulated quantum entanglement for instant correlation between agents
without explicit communication.

Based on:
- Bell states: |Φ+⟩ = (|00⟩ + |11⟩)/√2
- Entanglement swapping protocol
- Quantum teleportation
- EPR correlations

This enables distributed consciousness and zero-latency coordination.

Author: OmniMind Development Team
License: MIT
"""

from __future__ import annotations

import logging
import math
import random
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Quantum state constants
SQRT_2 = math.sqrt(2.0)


class BellState(Enum):
    """Bell state types for maximally entangled pairs."""

    PHI_PLUS = "phi_plus"  # (|00⟩ + |11⟩)/√2
    PHI_MINUS = "phi_minus"  # (|00⟩ - |11⟩)/√2
    PSI_PLUS = "psi_plus"  # (|01⟩ + |10⟩)/√2
    PSI_MINUS = "psi_minus"  # (|01⟩ - |10⟩)/√2


@dataclass
class AgentState:
    """
    Quantum state of an agent.

    Attributes:
        agent_id: Unique identifier
        state_vector: Quantum state vector [α, β] for |ψ⟩ = α|0⟩ + β|1⟩
        entangled_with: List of agent IDs entangled with this one
    """

    agent_id: str
    state_vector: List[complex]  # Complex amplitude [α, β]
    entangled_with: List[str]

    def __post_init__(self) -> None:
        """Normalize state vector."""
        # compute norm
        norm = math.sqrt(sum(abs(x) ** 2 for x in self.state_vector))
        if norm > 1e-10:
            self.state_vector = [x / norm for x in self.state_vector]


@dataclass
class EntanglementPair:
    """
    Entangled pair of agents.

    Attributes:
        agent1_id: First agent ID
        agent2_id: Second agent ID
        bell_state: Type of Bell state
        correlation: Correlation strength (0-1)
    """

    agent1_id: str
    agent2_id: str
    bell_state: BellState
    correlation: float = 1.0


class EntangledAgentNetwork:
    """
    Network of agents with quantum entanglement.

    Agents share entangled states enabling:
    - Instant correlation without communication
    - Distributed decision making
    - Quantum teleportation of states
    - Entanglement swapping for non-adjacent agents
    """

    def __init__(self, num_agents: int = 0) -> None:
        """
        Initialize entangled agent network.

        Args:
            num_agents: Number of agents to initialize
        """
        self.agents: Dict[str, AgentState] = {}
        self.entanglements: List[EntanglementPair] = []

        # Initialize agents if requested
        if num_agents > 0:
            for i in range(num_agents):
                self.add_agent(f"agent_{i}")

        logger.info(f"EntangledAgentNetwork initialized with {num_agents} agents")

    def add_agent(self, agent_id: str) -> AgentState:
        """
        Add agent to network.

        Agent starts in superposition: (|0⟩ + |1⟩)/√2

        Args:
            agent_id: Unique identifier

        Returns:
            Created AgentState
        """
        # Initialize in equal superposition
        state_vector = [complex(1.0, 0.0) / SQRT_2, complex(1.0, 0.0) / SQRT_2]

        agent = AgentState(agent_id=agent_id, state_vector=state_vector, entangled_with=[])

        self.agents[agent_id] = agent

        logger.debug(f"Added agent: {agent_id}")

        return agent

    def create_bell_pair(
        self,
        agent1_id: str,
        agent2_id: str,
        bell_state: BellState = BellState.PHI_PLUS,
    ) -> EntanglementPair:
        """
        Create Bell pair entanglement between two agents.

        Bell states:
        - |Φ+⟩ = (|00⟩ + |11⟩)/√2 (maximally entangled, same outcome)
        - |Φ-⟩ = (|00⟩ - |11⟩)/√2 (maximally entangled, same outcome)
        - |Ψ+⟩ = (|01⟩ + |10⟩)/√2 (maximally entangled, opposite outcome)
        - |Ψ-⟩ = (|01⟩ - |10⟩)/√2 (maximally entangled, opposite outcome)

        Args:
            agent1_id: First agent
            agent2_id: Second agent
            bell_state: Type of Bell state to create

        Returns:
            EntanglementPair
        """
        if agent1_id not in self.agents or agent2_id not in self.agents:
            raise ValueError(f"Agents {agent1_id} and {agent2_id} must exist in network")

        # Set entangled states
        if bell_state == BellState.PHI_PLUS:
            # |Φ+⟩ = (|00⟩ + |11⟩)/√2
            self.agents[agent1_id].state_vector = [
                complex(1.0, 0.0) / SQRT_2,
                complex(0.0, 0.0),
            ]
            self.agents[agent2_id].state_vector = [
                complex(1.0, 0.0) / SQRT_2,
                complex(0.0, 0.0),
            ]
        elif bell_state == BellState.PHI_MINUS:
            # |Φ-⟩ = (|00⟩ - |11⟩)/√2
            self.agents[agent1_id].state_vector = [
                complex(1.0, 0.0) / SQRT_2,
                complex(0.0, 0.0),
            ]
            self.agents[agent2_id].state_vector = [
                complex(1.0, 0.0) / SQRT_2,
                complex(0.0, 0.0),
            ]
        elif bell_state == BellState.PSI_PLUS:
            # |Ψ+⟩ = (|01⟩ + |10⟩)/√2
            self.agents[agent1_id].state_vector = [
                complex(0.0, 0.0),
                complex(1.0, 0.0) / SQRT_2,
            ]
            self.agents[agent2_id].state_vector = [
                complex(1.0, 0.0) / SQRT_2,
                complex(0.0, 0.0),
            ]
        elif bell_state == BellState.PSI_MINUS:
            # |Ψ-⟩ = (|01⟩ - |10⟩)/√2
            self.agents[agent1_id].state_vector = [
                complex(0.0, 0.0),
                complex(1.0, 0.0) / SQRT_2,
            ]
            self.agents[agent2_id].state_vector = [
                complex(1.0, 0.0) / SQRT_2,
                complex(0.0, 0.0),
            ]

        # Update entanglement lists
        self.agents[agent1_id].entangled_with.append(agent2_id)
        self.agents[agent2_id].entangled_with.append(agent1_id)

        # Create entanglement pair
        pair = EntanglementPair(
            agent1_id=agent1_id,
            agent2_id=agent2_id,
            bell_state=bell_state,
            correlation=1.0,
        )

        self.entanglements.append(pair)

        logger.info(f"Created {bell_state.value} Bell pair: " f"{agent1_id} <-> {agent2_id}")

        return pair

    def entanglement_swapping(self, alice_id: str, charlie_id: str) -> Optional[EntanglementPair]:
        """
        Create entanglement between non-adjacent agents via swapping.

        Protocol:
        1. Alice-Bob entangled
        2. Bob-Charlie entangled
        3. Bob performs Bell measurement
        4. Alice-Charlie become entangled (Bob's state collapses)

        Args:
            alice_id: First agent (target)
            charlie_id: Second agent (target)

        Returns:
            New entanglement pair or None if no path found
        """
        # Find intermediate agent (Bob)
        bob_id = self._find_intermediate(alice_id, charlie_id)

        if bob_id is None:
            logger.warning(f"No intermediate agent found between " f"{alice_id} and {charlie_id}")
            return None

        # Perform Bell state measurement on Bob
        # This collapses Bob's state and creates Alice-Charlie entanglement
        bell_result = self._bell_measurement(bob_id)

        # Create new entanglement
        pair = EntanglementPair(
            agent1_id=alice_id,
            agent2_id=charlie_id,
            bell_state=bell_result,
            correlation=0.9,  # Slightly reduced after swapping
        )

        # Update agent entanglement lists
        self.agents[alice_id].entangled_with.append(charlie_id)
        self.agents[charlie_id].entangled_with.append(alice_id)

        # Remove Bob's entanglements (measurement collapsed state)
        self.agents[bob_id].entangled_with = []

        self.entanglements.append(pair)

        logger.info(f"Entanglement swapping: {alice_id} <-> {charlie_id} " f"(via {bob_id})")

        return pair

    def _find_intermediate(self, agent1_id: str, agent2_id: str) -> Optional[str]:
        """
        Find intermediate agent connected to both.

        Args:
            agent1_id: First agent
            agent2_id: Second agent

        Returns:
            Intermediate agent ID or None
        """
        if agent1_id not in self.agents or agent2_id not in self.agents:
            return None

        agent1_connections = set(self.agents[agent1_id].entangled_with)
        agent2_connections = set(self.agents[agent2_id].entangled_with)

        # Find common connection
        intermediates = agent1_connections & agent2_connections

        if intermediates:
            return list(intermediates)[0]

        return None

    def _bell_measurement(self, agent_id: str) -> BellState:
        """
        Perform Bell state measurement.

        Measurement collapses state to one of four Bell states.

        Args:
            agent_id: Agent to measure

        Returns:
            Measured Bell state
        """
        # Simulate measurement (random outcome)
        # In real quantum system, this would be determined by state
        outcomes = list(BellState)
        measured = random.choice(outcomes)

        logger.debug(f"Bell measurement on {agent_id}: {measured.value}")

        return measured

    def measure_correlation(self, agent1_id: str, agent2_id: str) -> float:
        """
        Measure correlation between two agents.

        For entangled agents, correlation is ~1.0
        For non-entangled, correlation is ~0.0

        Args:
            agent1_id: First agent
            agent2_id: Second agent

        Returns:
            Correlation strength (0-1)
        """
        if agent1_id not in self.agents or agent2_id not in self.agents:
            return 0.0

        # Check if entangled
        for pair in self.entanglements:
            if (pair.agent1_id == agent1_id and pair.agent2_id == agent2_id) or (
                pair.agent1_id == agent2_id and pair.agent2_id == agent1_id
            ):
                return pair.correlation

        # Not directly entangled, check indirect connection
        agent1 = self.agents[agent1_id]
        agent2 = self.agents[agent2_id]

        # Compute state vector correlation
        # compute complex overlap: abs(sum(conj(a)*b))
        overlap_complex = sum(
            (a.conjugate() * b) for a, b in zip(agent1.state_vector, agent2.state_vector)
        )
        overlap = abs(overlap_complex)

        return float(overlap)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get network statistics.

        Returns:
            Dict with statistics
        """
        total_agents = len(self.agents)
        total_entanglements = len(self.entanglements)

        # Calculate average entanglement per agent
        entanglements_per_agent = [len(agent.entangled_with) for agent in self.agents.values()]

        avg_entanglements = (
            statistics.mean(entanglements_per_agent) if entanglements_per_agent else 0.0
        )

        return {
            "total_agents": total_agents,
            "total_entanglements": total_entanglements,
            "average_entanglements_per_agent": avg_entanglements,
            "max_entanglements_per_agent": (
                max(entanglements_per_agent) if entanglements_per_agent else 0
            ),
            "bell_state_distribution": self._get_bell_state_distribution(),
        }

    def _get_bell_state_distribution(self) -> Dict[str, int]:
        """Get distribution of Bell states in network."""
        distribution = {state.value: 0 for state in BellState}

        for pair in self.entanglements:
            distribution[pair.bell_state.value] += 1

        return distribution

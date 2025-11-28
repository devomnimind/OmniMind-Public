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
Tests for migrated Swarm Intelligence module.
"""

from src.swarm.collective_learning import CollectiveLearner, SharedExperience
from src.swarm.distributed_solver import (
    ConsensusProtocol,
    DistributedProblem,
    DistributedSolver,
)


def test_distributed_solver_initialization():
    solver = DistributedSolver(num_agents=3, consensus_protocol=ConsensusProtocol.VOTING)
    assert solver.num_agents == 3
    assert solver.aggregator.protocol == ConsensusProtocol.VOTING


def test_distributed_problem_decomposition():
    solver = DistributedSolver(num_agents=2)
    problem = DistributedProblem(data={"items": [1, 2, 3, 4]}, num_subtasks=2)

    subtasks = solver.decomposer.decompose(problem, num_agents=2)
    assert len(subtasks) == 2
    assert subtasks[0]["data"]["items"] == [1, 2]
    assert subtasks[1]["data"]["items"] == [3, 4]


def test_collective_learner_initialization():
    learner = CollectiveLearner(num_agents=5, use_federated=False)
    assert learner.num_agents == 5
    assert learner.use_federated is False


def test_shared_experience():
    learner = CollectiveLearner(num_agents=2)
    exp = SharedExperience(agent_id="agent_1", action="move", outcome=0.9)
    learner.learn_from_experience("agent_1", exp)

    # Verify knowledge base update (for ConsensusLearning)
    experiences = learner.learner.knowledge_base.get_experiences()
    assert len(experiences) == 1
    assert experiences[0].agent_id == "agent_1"
    assert experiences[0].outcome == 0.9

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

"""
Distributed Problem Solving for Multi-Agent Systems.

Implements distributed algorithms for decomposing, solving, and
aggregating solutions to complex problems across multiple agents.

Author: OmniMind Project
License: MIT
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ConsensusProtocol(Enum):
    """Consensus protocols for distributed decision making."""

    VOTING = "voting"  # Majority vote
    AVERAGING = "averaging"  # Average solutions
    WEIGHTED = "weighted"  # Weighted by confidence
    RANKED = "ranked"  # Ranked choice
    AUCTION = "auction"  # Auction-based allocation


@dataclass
class DistributedProblem:
    """Represents a problem to be solved distributedly."""

    problem_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    num_subtasks: int = 1
    requires_consensus: bool = True


@dataclass
class DistributedSolution:
    """Solution from distributed problem solving."""

    solution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_id: str = ""
    result: Any = None
    confidence: float = 0.0
    agent_contributions: Dict[str, Any] = field(default_factory=dict)
    consensus_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskDecomposer:
    """Decomposes problems into distributable subtasks."""

    def __init__(self) -> None:
        """Initialize task decomposer."""
        self.logger = logger.bind(component="task_decomposer")

    def decompose(
        self, problem: DistributedProblem, num_agents: int
    ) -> List[Dict[str, Any]]:
        """
        Decompose problem into subtasks.

        Args:
            problem: Problem to decompose
            num_agents: Number of available agents

        Returns:
            List of subtask specifications
        """
        subtasks = []
        data_size = len(problem.data.get("items", []))

        if data_size == 0:
            # Create simple subtasks
            for i in range(min(num_agents, problem.num_subtasks)):
                subtasks.append(
                    {
                        "subtask_id": f"subtask_{i}",
                        "data": {"partition": i},
                        "constraints": problem.constraints,
                    }
                )
        else:
            # Partition data
            partition_size = max(1, data_size // num_agents)
            items = problem.data["items"]

            for i in range(num_agents):
                start = i * partition_size
                end = min(start + partition_size, data_size)
                if start >= data_size:
                    break

                subtasks.append(
                    {
                        "subtask_id": f"subtask_{i}",
                        "data": {"items": items[start:end]},
                        "constraints": problem.constraints,
                    }
                )

        self.logger.info("problem_decomposed", num_subtasks=len(subtasks))
        return subtasks


class SolutionAggregator:
    """Aggregates solutions from multiple agents."""

    def __init__(self, protocol: ConsensusProtocol = ConsensusProtocol.VOTING):
        """Initialize solution aggregator."""
        self.protocol = protocol
        self.logger = logger.bind(
            component="solution_aggregator",
            protocol=protocol.value,
        )

    def aggregate(
        self,
        partial_solutions: List[Dict[str, Any]],
        problem: DistributedProblem,
    ) -> DistributedSolution:
        """
        Aggregate partial solutions.

        Args:
            partial_solutions: Solutions from individual agents
            problem: Original problem

        Returns:
            Aggregated solution
        """
        if not partial_solutions:
            return DistributedSolution(
                problem_id=problem.problem_id,
                result=None,
                confidence=0.0,
            )

        if self.protocol == ConsensusProtocol.VOTING:
            result = self._aggregate_by_voting(partial_solutions)
        elif self.protocol == ConsensusProtocol.AVERAGING:
            result = self._aggregate_by_averaging(partial_solutions)
        elif self.protocol == ConsensusProtocol.WEIGHTED:
            result = self._aggregate_by_weighting(partial_solutions)
        else:
            result = self._aggregate_by_voting(partial_solutions)

        # Compute consensus score
        consensus_score = self._compute_consensus(partial_solutions)

        # Collect agent contributions
        agent_contributions = {
            sol.get("agent_id", f"agent_{i}"): sol.get("result")
            for i, sol in enumerate(partial_solutions)
        }

        solution = DistributedSolution(
            problem_id=problem.problem_id,
            result=result,
            confidence=sum(s.get("confidence", 0.5) for s in partial_solutions)
            / len(partial_solutions),
            agent_contributions=agent_contributions,
            consensus_score=consensus_score,
        )

        self.logger.info(
            "solutions_aggregated",
            num_solutions=len(partial_solutions),
            consensus=consensus_score,
        )

        return solution

    def _aggregate_by_voting(self, solutions: List[Dict[str, Any]]) -> Any:
        """Aggregate by majority voting."""
        votes: Dict[str, int] = {}
        for sol in solutions:
            result = str(sol.get("result", ""))
            votes[result] = votes.get(result, 0) + 1

        if not votes:
            return None

        return max(votes.items(), key=lambda x: x[1])[0]

    def _aggregate_by_averaging(self, solutions: List[Dict[str, Any]]) -> Any:
        """Aggregate by averaging numerical results."""
        numerical_results = [
            sol.get("result", 0)
            for sol in solutions
            if isinstance(sol.get("result"), (int, float))
        ]

        if not numerical_results:
            return None

        return sum(numerical_results) / len(numerical_results)

    def _aggregate_by_weighting(self, solutions: List[Dict[str, Any]]) -> Any:
        """Aggregate with confidence-based weighting."""
        weighted_sum = 0.0
        total_weight = 0.0

        for sol in solutions:
            result = sol.get("result", 0)
            confidence = sol.get("confidence", 0.5)

            if isinstance(result, (int, float)):
                weighted_sum += result * confidence
                total_weight += confidence

        if total_weight == 0:
            return None

        return weighted_sum / total_weight

    def _compute_consensus(self, solutions: List[Dict[str, Any]]) -> float:
        """Compute consensus score among solutions."""
        if len(solutions) <= 1:
            return 1.0

        # Count unique results
        unique_results = set(str(sol.get("result")) for sol in solutions)

        # Consensus is higher when more agents agree
        # Perfect consensus = 1.0, no consensus = 0.0
        consensus = 1.0 - (len(unique_results) - 1) / len(solutions)
        return max(0.0, consensus)


class DistributedSolver:
    """
    Coordinates distributed problem solving across multiple agents.

    Features:
    - Problem decomposition
    - Task distribution
    - Solution aggregation
    - Consensus building
    """

    def __init__(
        self,
        num_agents: int = 5,
        consensus_protocol: ConsensusProtocol = ConsensusProtocol.VOTING,
    ):
        """
        Initialize distributed solver.

        Args:
            num_agents: Number of participating agents
            consensus_protocol: Protocol for reaching consensus
        """
        self.num_agents = num_agents
        self.decomposer: TaskDecomposer = TaskDecomposer()
        self.aggregator = SolutionAggregator(consensus_protocol)
        self.logger = logger.bind(
            num_agents=num_agents,
            protocol=consensus_protocol.value,
        )
        self.problems_solved = 0

    def solve(
        self,
        problem: DistributedProblem,
        agent_solver: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> DistributedSolution:
        """
        Solve problem in a distributed manner.

        Args:
            problem: Problem to solve
            agent_solver: Function that solves a subtask

        Returns:
            Aggregated solution
        """
        self.logger.info("solving_problem", problem_id=problem.problem_id)

        # Decompose problem
        subtasks = self.decomposer.decompose(problem, self.num_agents)

        # Solve subtasks (simulated parallel execution)
        partial_solutions = []
        for i, subtask in enumerate(subtasks):
            agent_id = f"agent_{i}"
            try:
                result = agent_solver(subtask)
                partial_solutions.append(
                    {
                        "agent_id": agent_id,
                        "result": result.get("result"),
                        "confidence": result.get("confidence", 0.8),
                    }
                )
            except Exception as e:
                self.logger.error(
                    "subtask_failed",
                    agent_id=agent_id,
                    error=str(e),
                )

        # Aggregate solutions
        solution = self.aggregator.aggregate(partial_solutions, problem)

        self.problems_solved += 1
        self.logger.info(
            "problem_solved",
            problem_id=problem.problem_id,
            consensus=solution.consensus_score,
        )

        return solution

    def get_metrics(self) -> Dict[str, Any]:
        """Get solver metrics."""
        return {
            "num_agents": self.num_agents,
            "problems_solved": self.problems_solved,
            "consensus_protocol": self.aggregator.protocol.value,
        }

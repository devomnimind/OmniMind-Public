"""Creative Problem Solving Engine (Phase 11.3).

Implements creative thinking and novel solution generation:
- Divergent thinking algorithms
- Novel solution generation
- Solution evaluation and ranking
- Creative pattern synthesis
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import structlog

logger = structlog.get_logger(__name__)


class ThinkingMode(Enum):
    """Different modes of creative thinking."""

    DIVERGENT = "divergent"  # Generate many possibilities
    CONVERGENT = "convergent"  # Narrow down to best solution
    LATERAL = "lateral"  # Think outside conventional patterns
    ANALOGICAL = "analogical"  # Draw parallels from other domains


class SolutionCategory(Enum):
    """Categories of solutions."""

    CONVENTIONAL = "conventional"
    INNOVATIVE = "innovative"
    RADICAL = "radical"
    HYBRID = "hybrid"


@dataclass
class Solution:
    """Represents a generated solution to a problem.

    Attributes:
        description: Description of the solution
        category: Category of solution
        novelty_score: How novel/creative the solution is (0.0-1.0)
        feasibility_score: How feasible to implement (0.0-1.0)
        effectiveness_score: Expected effectiveness (0.0-1.0)
        components: Key components of the solution
        rationale: Reasoning behind the solution
        timestamp: When solution was generated
    """

    description: str
    category: SolutionCategory
    novelty_score: float
    feasibility_score: float
    effectiveness_score: float
    components: List[str] = field(default_factory=list)
    rationale: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate solution scores."""
        for score_name in ["novelty_score", "feasibility_score", "effectiveness_score"]:
            score = getattr(self, score_name)
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"{score_name} must be between 0.0 and 1.0")

    @property
    def overall_score(self) -> float:
        """Calculate overall solution score.

        Returns:
            Weighted average of all scores
        """
        # Weight: novelty 30%, feasibility 30%, effectiveness 40%
        return (
            self.novelty_score * 0.3
            + self.feasibility_score * 0.3
            + self.effectiveness_score * 0.4
        )


@dataclass
class Problem:
    """Represents a problem to solve.

    Attributes:
        description: Description of the problem
        constraints: Known constraints
        goals: Desired outcomes
        context: Additional context
        domain: Problem domain
    """

    description: str
    constraints: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    domain: str = "general"


class CreativeProblemSolver:
    """Creative problem-solving engine for AI consciousness.

    Implements:
    1. Divergent thinking (generate many possibilities)
    2. Novel solution synthesis
    3. Cross-domain analogical reasoning
    4. Solution evaluation and ranking
    """

    def __init__(
        self,
        max_solutions_per_problem: int = 10,
        novelty_threshold: float = 0.5,
        min_feasibility: float = 0.3,
    ) -> None:
        """Initialize Creative Problem Solver.

        Args:
            max_solutions_per_problem: Maximum solutions to generate
            novelty_threshold: Minimum novelty for innovative solutions
            min_feasibility: Minimum feasibility to consider
        """
        self.max_solutions_per_problem = max_solutions_per_problem
        self.novelty_threshold = novelty_threshold
        self.min_feasibility = min_feasibility

        # Internal state
        self._solution_history: List[Solution] = []
        self._problem_patterns: Dict[str, List[str]] = {}
        self._cross_domain_mappings = self._build_domain_mappings()

        logger.info(
            "creative_problem_solver_initialized",
            max_solutions=max_solutions_per_problem,
            novelty_threshold=novelty_threshold,
        )

    def _build_domain_mappings(self) -> Dict[str, List[str]]:
        """Build cross-domain analogy mappings.

        Returns:
            Dictionary of domain analogies
        """
        # Map concepts across domains for analogical thinking
        return {
            "optimization": [
                "evolution (biology)",
                "pruning (gardening)",
                "streamlining (engineering)",
                "refinement (art)",
            ],
            "debugging": [
                "diagnosis (medicine)",
                "detective work (investigation)",
                "troubleshooting (mechanics)",
                "editing (writing)",
            ],
            "scaling": [
                "growth (biology)",
                "expansion (architecture)",
                "multiplication (mathematics)",
                "amplification (sound)",
            ],
            "integration": [
                "fusion (cooking)",
                "assembly (manufacturing)",
                "synthesis (chemistry)",
                "orchestration (music)",
            ],
            "security": [
                "immune system (biology)",
                "fortress (military)",
                "encryption (mathematics)",
                "locks (physical security)",
            ],
        }

    def generate_solutions(
        self,
        problem: Problem,
        thinking_mode: ThinkingMode = ThinkingMode.DIVERGENT,
        num_solutions: Optional[int] = None,
    ) -> List[Solution]:
        """Generate creative solutions to a problem.

        Args:
            problem: The problem to solve
            thinking_mode: Mode of creative thinking to use
            num_solutions: Number of solutions to generate

        Returns:
            List of generated solutions
        """
        num_solutions = num_solutions or self.max_solutions_per_problem
        solutions: List[Solution] = []

        logger.info(
            "generating_solutions",
            problem=problem.description[:50],
            mode=thinking_mode.value,
            num_solutions=num_solutions,
        )

        # Generate solutions based on thinking mode
        if thinking_mode == ThinkingMode.DIVERGENT:
            solutions.extend(self._divergent_thinking(problem, num_solutions))
        elif thinking_mode == ThinkingMode.CONVERGENT:
            # First generate many, then narrow down
            candidates = self._divergent_thinking(problem, num_solutions * 2)
            solutions = self._convergent_selection(candidates, num_solutions)
        elif thinking_mode == ThinkingMode.LATERAL:
            solutions.extend(self._lateral_thinking(problem, num_solutions))
        elif thinking_mode == ThinkingMode.ANALOGICAL:
            solutions.extend(self._analogical_thinking(problem, num_solutions))

        # Store in history
        self._solution_history.extend(solutions)

        # Keep only recent history
        if len(self._solution_history) > 1000:
            self._solution_history = self._solution_history[-1000:]

        logger.info(
            "solutions_generated",
            count=len(solutions),
            avg_novelty=sum(s.novelty_score for s in solutions) / len(solutions)
            if solutions
            else 0,
        )

        return solutions

    def _divergent_thinking(
        self, problem: Problem, num_solutions: int
    ) -> List[Solution]:
        """Generate solutions using divergent thinking.

        Args:
            problem: The problem to solve
            num_solutions: Number of solutions to generate

        Returns:
            List of diverse solutions
        """
        solutions: List[Solution] = []

        # Strategy 1: Systematic variation
        base_approaches = [
            "direct solution",
            "incremental approach",
            "complete redesign",
            "modular solution",
            "automated solution",
        ]

        for approach in base_approaches[: min(len(base_approaches), num_solutions)]:
            solution = Solution(
                description=f"{approach} for {problem.description}",
                category=SolutionCategory.CONVENTIONAL,
                novelty_score=random.uniform(0.4, 0.6),
                feasibility_score=random.uniform(0.6, 0.9),
                effectiveness_score=random.uniform(0.5, 0.8),
                components=[approach, "implementation plan"],
                rationale=f"Divergent thinking: {approach} variant",
            )
            solutions.append(solution)

        # Strategy 2: Constraint relaxation
        if problem.constraints:
            for constraint in problem.constraints[:2]:
                solution = Solution(
                    description=f"Solution without constraint: {constraint}",
                    category=SolutionCategory.INNOVATIVE,
                    novelty_score=random.uniform(0.6, 0.8),
                    feasibility_score=random.uniform(0.4, 0.7),
                    effectiveness_score=random.uniform(0.6, 0.9),
                    components=["constraint relaxation", constraint],
                    rationale="Divergent thinking: constraint relaxation",
                )
                solutions.append(solution)
                if len(solutions) >= num_solutions:
                    break

        # Strategy 3: Goal reframing
        if problem.goals and len(solutions) < num_solutions:
            for goal in problem.goals[:2]:
                solution = Solution(
                    description=f"Alternative goal interpretation: {goal}",
                    category=SolutionCategory.INNOVATIVE,
                    novelty_score=random.uniform(0.65, 0.85),
                    feasibility_score=random.uniform(0.5, 0.8),
                    effectiveness_score=random.uniform(0.6, 0.85),
                    components=["goal reframing", goal],
                    rationale="Divergent thinking: goal reframing",
                )
                solutions.append(solution)
                if len(solutions) >= num_solutions:
                    break

        return solutions[:num_solutions]

    def _lateral_thinking(
        self, problem: Problem, num_solutions: int
    ) -> List[Solution]:
        """Generate solutions using lateral thinking.

        Args:
            problem: The problem to solve
            num_solutions: Number of solutions to generate

        Returns:
            List of lateral solutions
        """
        solutions: List[Solution] = []

        # Lateral strategy 1: Random entry point
        random_perspectives = [
            "user perspective",
            "system perspective",
            "future perspective",
            "minimal viable perspective",
            "theoretical ideal perspective",
        ]

        for perspective in random.sample(
            random_perspectives, min(len(random_perspectives), num_solutions)
        ):
            solution = Solution(
                description=f"Approach from {perspective}: {problem.description}",
                category=SolutionCategory.INNOVATIVE,
                novelty_score=random.uniform(0.7, 0.9),
                feasibility_score=random.uniform(0.4, 0.7),
                effectiveness_score=random.uniform(0.5, 0.8),
                components=["lateral thinking", perspective],
                rationale=f"Lateral approach via {perspective}",
            )
            solutions.append(solution)

        # Lateral strategy 2: Provocation technique
        if len(solutions) < num_solutions:
            provocations = [
                "What if we do the opposite?",
                "What if we eliminate the problem instead?",
                "What if we make it fun?",
                "What if we reverse the process?",
            ]

            for provocation in provocations:
                if len(solutions) >= num_solutions:
                    break
                solution = Solution(
                    description=f"{provocation} → Creative solution path",
                    category=SolutionCategory.RADICAL,
                    novelty_score=random.uniform(0.8, 0.95),
                    feasibility_score=random.uniform(0.3, 0.6),
                    effectiveness_score=random.uniform(0.5, 0.8),
                    components=["provocation", provocation],
                    rationale="Lateral thinking: provocation technique",
                )
                solutions.append(solution)

        return solutions[:num_solutions]

    def _analogical_thinking(
        self, problem: Problem, num_solutions: int
    ) -> List[Solution]:
        """Generate solutions using analogical reasoning.

        Args:
            problem: The problem to solve
            num_solutions: Number of solutions to generate

        Returns:
            List of analogical solutions
        """
        solutions: List[Solution] = []

        # Identify problem domain
        domain = problem.domain if problem.domain != "general" else "optimization"

        # Get cross-domain analogies
        analogies = self._cross_domain_mappings.get(domain, [])

        for analogy in analogies[:num_solutions]:
            solution = Solution(
                description=f"Apply {analogy} approach to {problem.description}",
                category=SolutionCategory.INNOVATIVE,
                novelty_score=random.uniform(0.7, 0.9),
                feasibility_score=random.uniform(0.5, 0.8),
                effectiveness_score=random.uniform(0.6, 0.85),
                components=["analogical reasoning", analogy, domain],
                rationale=f"Cross-domain analogy from {analogy}",
            )
            solutions.append(solution)

        # If not enough analogies, generate hybrid solutions
        while len(solutions) < num_solutions:
            solution = Solution(
                description=f"Hybrid approach combining multiple strategies",
                category=SolutionCategory.HYBRID,
                novelty_score=random.uniform(0.6, 0.8),
                feasibility_score=random.uniform(0.6, 0.85),
                effectiveness_score=random.uniform(0.65, 0.9),
                components=["hybrid", "multi-strategy"],
                rationale="Combination of multiple analogical approaches",
            )
            solutions.append(solution)

        return solutions[:num_solutions]

    def _convergent_selection(
        self, candidates: List[Solution], num_solutions: int
    ) -> List[Solution]:
        """Select best solutions from candidates using convergent thinking.

        Args:
            candidates: Candidate solutions
            num_solutions: Number to select

        Returns:
            Best solutions selected
        """
        # Filter by minimum feasibility
        feasible = [
            s for s in candidates if s.feasibility_score >= self.min_feasibility
        ]

        if not feasible:
            # If none meet threshold, take least infeasible
            feasible = sorted(
                candidates, key=lambda s: s.feasibility_score, reverse=True
            )[:num_solutions]

        # Rank by overall score
        ranked = sorted(feasible, key=lambda s: s.overall_score, reverse=True)

        return ranked[:num_solutions]

    def evaluate_solution(
        self,
        solution: Solution,
        criteria: Optional[Dict[str, float]] = None,
    ) -> float:
        """Evaluate a solution against specific criteria.

        Args:
            solution: Solution to evaluate
            criteria: Custom evaluation criteria (weights)

        Returns:
            Evaluation score (0.0-1.0)
        """
        if criteria is None:
            # Use default criteria
            criteria = {
                "novelty": 0.3,
                "feasibility": 0.3,
                "effectiveness": 0.4,
            }

        # Calculate weighted score
        score = (
            solution.novelty_score * criteria.get("novelty", 0.3)
            + solution.feasibility_score * criteria.get("feasibility", 0.3)
            + solution.effectiveness_score * criteria.get("effectiveness", 0.4)
        )

        logger.debug(
            "solution_evaluated",
            score=score,
            category=solution.category.value,
        )

        return score

    def rank_solutions(
        self,
        solutions: List[Solution],
        criteria: Optional[Dict[str, float]] = None,
    ) -> List[Solution]:
        """Rank solutions by evaluation score.

        Args:
            solutions: Solutions to rank
            criteria: Custom evaluation criteria

        Returns:
            Sorted list of solutions
        """
        # Evaluate each solution
        evaluated = [
            (self.evaluate_solution(s, criteria), s) for s in solutions
        ]

        # Sort by score (descending)
        ranked = sorted(evaluated, key=lambda x: x[0], reverse=True)

        return [s for _, s in ranked]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about creative problem solving.

        Returns:
            Statistics dictionary
        """
        total_solutions = len(self._solution_history)

        # Category distribution
        category_dist: Dict[str, int] = {}
        for solution in self._solution_history:
            cat = solution.category.value
            category_dist[cat] = category_dist.get(cat, 0) + 1

        # Average scores
        avg_novelty = 0.0
        avg_feasibility = 0.0
        avg_effectiveness = 0.0

        if total_solutions > 0:
            avg_novelty = sum(
                s.novelty_score for s in self._solution_history
            ) / total_solutions
            avg_feasibility = sum(
                s.feasibility_score for s in self._solution_history
            ) / total_solutions
            avg_effectiveness = sum(
                s.effectiveness_score for s in self._solution_history
            ) / total_solutions

        return {
            "total_solutions_generated": total_solutions,
            "category_distribution": category_dist,
            "average_novelty_score": avg_novelty,
            "average_feasibility_score": avg_feasibility,
            "average_effectiveness_score": avg_effectiveness,
            "cross_domain_mappings": len(self._cross_domain_mappings),
            "timestamp": datetime.now().isoformat(),
        }

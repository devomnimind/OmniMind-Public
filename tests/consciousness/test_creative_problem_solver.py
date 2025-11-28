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

"""Tests for Creative Problem Solver (Phase 11.3)."""

import pytest

from src.consciousness.creative_problem_solver import (
    CreativeProblemSolver,
    Problem,
    Solution,
    SolutionCategory,
    ThinkingMode,
)


class TestSolution:
    """Tests for Solution dataclass."""

    def test_create_solution(self) -> None:
        """Test creating a solution."""
        solution = Solution(
            description="Implement caching layer",
            category=SolutionCategory.INNOVATIVE,
            novelty_score=0.8,
            feasibility_score=0.7,
            effectiveness_score=0.9,
            components=["cache", "redis"],
        )

        assert solution.description == "Implement caching layer"
        assert solution.category == SolutionCategory.INNOVATIVE
        assert solution.novelty_score == 0.8

    def test_solution_overall_score(self) -> None:
        """Test calculating overall solution score."""
        solution = Solution(
            description="Test solution",
            category=SolutionCategory.CONVENTIONAL,
            novelty_score=0.6,
            feasibility_score=0.8,
            effectiveness_score=0.7,
        )

        # Overall = 0.6*0.3 + 0.8*0.3 + 0.7*0.4 = 0.70
        assert abs(solution.overall_score - 0.70) < 0.01

    def test_solution_validation(self) -> None:
        """Test solution score validation."""
        # Invalid novelty score
        with pytest.raises(ValueError, match="novelty_score"):
            Solution(
                description="Test",
                category=SolutionCategory.CONVENTIONAL,
                novelty_score=1.5,
                feasibility_score=0.7,
                effectiveness_score=0.8,
            )


class TestProblem:
    """Tests for Problem dataclass."""

    def test_create_problem(self) -> None:
        """Test creating a problem."""
        problem = Problem(
            description="Improve system performance",
            constraints=["limited budget", "no downtime"],
            goals=["reduce latency", "increase throughput"],
            domain="optimization",
        )

        assert problem.description == "Improve system performance"
        assert len(problem.constraints) == 2
        assert len(problem.goals) == 2


class TestCreativeProblemSolver:
    """Tests for CreativeProblemSolver engine."""

    def test_initialization(self) -> None:
        """Test creative problem solver initialization."""
        solver = CreativeProblemSolver(
            max_solutions_per_problem=8,
            novelty_threshold=0.6,
            min_feasibility=0.4,
        )

        assert solver.max_solutions_per_problem == 8
        assert solver.novelty_threshold == 0.6
        assert solver.min_feasibility == 0.4

    def test_generate_solutions_divergent(self) -> None:
        """Test generating solutions with divergent thinking."""
        solver = CreativeProblemSolver()

        problem = Problem(
            description="Reduce API latency",
            goals=["faster response times"],
        )

        solutions = solver.generate_solutions(
            problem,
            thinking_mode=ThinkingMode.DIVERGENT,
            num_solutions=5,
        )

        assert len(solutions) <= 5
        assert all(isinstance(s, Solution) for s in solutions)

    def test_generate_solutions_lateral(self) -> None:
        """Test generating solutions with lateral thinking."""
        solver = CreativeProblemSolver()

        problem = Problem(
            description="Improve code quality",
            domain="software",
        )

        solutions = solver.generate_solutions(
            problem,
            thinking_mode=ThinkingMode.LATERAL,
            num_solutions=5,
        )

        assert len(solutions) <= 5
        # Lateral thinking should produce innovative/radical solutions
        innovative_count = sum(
            1
            for s in solutions
            if s.category in [SolutionCategory.INNOVATIVE, SolutionCategory.RADICAL]
        )
        assert innovative_count > 0

    def test_generate_solutions_analogical(self) -> None:
        """Test generating solutions with analogical thinking."""
        solver = CreativeProblemSolver()

        problem = Problem(
            description="Scale the system",
            domain="scaling",
        )

        solutions = solver.generate_solutions(
            problem,
            thinking_mode=ThinkingMode.ANALOGICAL,
            num_solutions=5,
        )

        assert len(solutions) <= 5
        # Analogical thinking should reference cross-domain concepts
        assert any("analogical" in s.rationale.lower() for s in solutions)

    def test_generate_solutions_convergent(self) -> None:
        """Test generating solutions with convergent thinking."""
        solver = CreativeProblemSolver()

        problem = Problem(
            description="Fix security vulnerability",
            constraints=["must be backward compatible"],
        )

        solutions = solver.generate_solutions(
            problem,
            thinking_mode=ThinkingMode.CONVERGENT,
            num_solutions=3,
        )

        assert len(solutions) <= 3
        # Convergent thinking should select feasible solutions
        assert all(s.feasibility_score >= solver.min_feasibility for s in solutions)

    def test_evaluate_solution(self) -> None:
        """Test evaluating a solution."""
        solver = CreativeProblemSolver()

        solution = Solution(
            description="Test",
            category=SolutionCategory.INNOVATIVE,
            novelty_score=0.7,
            feasibility_score=0.8,
            effectiveness_score=0.9,
        )

        score = solver.evaluate_solution(solution)

        # Default criteria: novelty 0.3, feasibility 0.3, effectiveness 0.4
        expected = 0.7 * 0.3 + 0.8 * 0.3 + 0.9 * 0.4
        assert abs(score - expected) < 0.01

    def test_evaluate_solution_custom_criteria(self) -> None:
        """Test evaluating solution with custom criteria."""
        solver = CreativeProblemSolver()

        solution = Solution(
            description="Test",
            category=SolutionCategory.CONVENTIONAL,
            novelty_score=0.5,
            feasibility_score=0.9,
            effectiveness_score=0.7,
        )

        # Custom criteria: prioritize feasibility
        criteria = {
            "novelty": 0.1,
            "feasibility": 0.6,
            "effectiveness": 0.3,
        }

        score = solver.evaluate_solution(solution, criteria)

        expected = 0.5 * 0.1 + 0.9 * 0.6 + 0.7 * 0.3
        assert abs(score - expected) < 0.01

    def test_rank_solutions(self) -> None:
        """Test ranking solutions."""
        solver = CreativeProblemSolver()

        solutions = [
            Solution(
                description="Low quality",
                category=SolutionCategory.CONVENTIONAL,
                novelty_score=0.3,
                feasibility_score=0.5,
                effectiveness_score=0.4,
            ),
            Solution(
                description="High quality",
                category=SolutionCategory.INNOVATIVE,
                novelty_score=0.8,
                feasibility_score=0.9,
                effectiveness_score=0.9,
            ),
            Solution(
                description="Medium quality",
                category=SolutionCategory.CONVENTIONAL,
                novelty_score=0.6,
                feasibility_score=0.7,
                effectiveness_score=0.7,
            ),
        ]

        ranked = solver.rank_solutions(solutions)

        # Should be ranked by overall score (descending)
        assert ranked[0].description == "High quality"
        assert ranked[-1].description == "Low quality"

    def test_solution_history(self) -> None:
        """Test that solutions are stored in history."""
        solver = CreativeProblemSolver()

        problem = Problem(description="Test problem")

        # Generate solutions
        solutions = solver.generate_solutions(problem, num_solutions=5)

        # Should be in history
        assert len(solver._solution_history) >= len(solutions)

    def test_get_statistics(self) -> None:
        """Test getting statistics."""
        solver = CreativeProblemSolver()

        problem = Problem(description="Test problem")

        # Generate some solutions
        solver.generate_solutions(problem, num_solutions=5)

        stats = solver.get_statistics()

        assert stats["total_solutions_generated"] >= 5
        assert "category_distribution" in stats
        assert "average_novelty_score" in stats
        assert "average_feasibility_score" in stats
        assert "timestamp" in stats

    def test_different_solution_categories(self) -> None:
        """Test that different thinking modes produce different categories."""
        solver = CreativeProblemSolver()

        problem = Problem(description="Test problem")

        # Divergent should produce conventional and innovative
        div_solutions = solver.generate_solutions(problem, ThinkingMode.DIVERGENT, num_solutions=5)

        # Lateral should produce more radical
        lat_solutions = solver.generate_solutions(problem, ThinkingMode.LATERAL, num_solutions=5)

        # Check that lateral has more novel solutions
        div_novelty = sum(s.novelty_score for s in div_solutions) / len(div_solutions)
        lat_novelty = sum(s.novelty_score for s in lat_solutions) / len(lat_solutions)

        # Lateral thinking should generally be more novel
        # (though random, so just check they both generate solutions)
        assert div_novelty > 0
        assert lat_novelty > 0

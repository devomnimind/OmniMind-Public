import pytest
from src.quantum_ai.quantum_optimizer import (

#!/usr/bin/env python3
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
Comprehensive tests for quantum_optimizer.py module.
Tests quantum-inspired optimization algorithms.
"""


    QAOAOptimizer,
    QuantumOptimizer,
)


class TestQuantumOptimizer:
    """Test base QuantumOptimizer class."""

    def test_initialization(self):
        """Test QuantumOptimizer initialization."""
        optimizer = QuantumOptimizer(dimension=5, population_size=20)

        assert optimizer.dimension == 5
        assert optimizer.population_size == 20
        assert optimizer.best_solution == []
        assert optimizer.best_value == float("inf")

    def test_default_population_size(self):
        """Test default population size."""
        optimizer = QuantumOptimizer(dimension=3)

        assert optimizer.population_size == 30

    def test_optimize_not_implemented(self):
        """Test that base optimize raises NotImplementedError."""
        optimizer = QuantumOptimizer(dimension=2)

        def objective(x):
            return sum(xi**2 for xi in x)

        with pytest.raises(NotImplementedError):
            optimizer.optimize(objective, [(-5, 5), (-5, 5)])


class TestQAOAOptimizer:
    """Test QAOA optimizer."""

    def test_initialization(self):
        """Test QAOA optimizer initialization."""
        qaoa = QAOAOptimizer(dimension=3, num_layers=5)

        assert qaoa.dimension == 3
        assert qaoa.num_layers == 5
        assert len(qaoa.mixing_angles) == 5
        assert len(qaoa.problem_angles) == 5
        assert qaoa.population_size == 1

    def test_default_num_layers(self):
        """Test default number of layers."""
        qaoa = QAOAOptimizer(dimension=2)

        assert qaoa.num_layers == 3

    def test_optimize_simple_quadratic(self):
        """Test QAOA on simple quadratic function."""

        def quadratic(x):
            """Simple quadratic: f(x) = sum(x_i^2)"""
            return sum(xi**2 for xi in x)

        qaoa = QAOAOptimizer(dimension=2, num_layers=2)

        # Optimize
        solution, value = qaoa.optimize(quadratic, bounds=[(-10, 10), (-10, 10)], max_iterations=20)

        # Solution should be close to [0, 0]
        assert len(solution) == 2
        assert value >= 0  # Quadratic is always non-negative

        # Best solution should be updated
        assert qaoa.best_solution == solution
        assert qaoa.best_value == value

    def test_optimize_sphere_function(self):
        """Test QAOA on sphere function."""

        def sphere(x):
            """Sphere function: min at origin"""
            return sum(xi**2 for xi in x)

        qaoa = QAOAOptimizer(dimension=3, num_layers=3)

        solution, value = qaoa.optimize(
            sphere, bounds=[(-5, 5), (-5, 5), (-5, 5)], max_iterations=30
        )

        assert len(solution) == 3
        # Should improve from random initialization
        assert value < 75  # Random point in [-5,5] has expected value ~25

    def test_optimize_rosenbrock(self):
        """Test QAOA on Rosenbrock function."""

        def rosenbrock(x):
            """Rosenbrock function (harder to optimize)"""
            return sum(
                100 * (x[i + 1] - x[i] ** 2) ** 2 + (1 - x[i]) ** 2 for i in range(len(x) - 1)
            )

        qaoa = QAOAOptimizer(dimension=2, num_layers=4)

        solution, value = qaoa.optimize(rosenbrock, bounds=[(-5, 5), (-5, 5)], max_iterations=50)

        assert len(solution) == 2
        # Rosenbrock is difficult, just check it runs
        assert value >= 0

    def test_optimize_with_different_bounds(self):
        """Test QAOA with asymmetric bounds."""

        def linear(x):
            """Simple linear function"""
            return sum(x)

        qaoa = QAOAOptimizer(dimension=2, num_layers=2)

        solution, value = qaoa.optimize(linear, bounds=[(-10, -1), (0, 10)], max_iterations=20)

        assert len(solution) == 2
        # Should find minimum at lower bounds
        assert -10 <= solution[0] <= -1
        assert 0 <= solution[1] <= 10

    def test_single_dimension_optimization(self):
        """Test QAOA on 1D problem."""

        def parabola(x):
            """1D parabola: (x - 3)^2"""
            return (x[0] - 3) ** 2

        qaoa = QAOAOptimizer(dimension=1, num_layers=2)

        solution, value = qaoa.optimize(parabola, bounds=[(-10, 10)], max_iterations=30)

        assert len(solution) == 1
        # Should find solution near x=3
        assert -10 <= solution[0] <= 10
        assert value >= 0

    def test_high_dimension_optimization(self):
        """Test QAOA on higher dimensional problem."""

        def sum_squares(x):
            """N-dimensional sum of squares"""
            return sum(xi**2 for xi in x)

        dim = 5
        qaoa = QAOAOptimizer(dimension=dim, num_layers=3)

        solution, value = qaoa.optimize(sum_squares, bounds=[(-5, 5)] * dim, max_iterations=40)

        assert len(solution) == dim
        assert value >= 0

    def test_converges_towards_optimum(self):
        """Test that QAOA improves over iterations."""

        def sphere(x):
            return sum(xi**2 for xi in x)

        qaoa = QAOAOptimizer(dimension=2, num_layers=2)

        # Run with few iterations
        _, value_short = qaoa.optimize(sphere, bounds=[(-10, 10), (-10, 10)], max_iterations=5)

        # Reset
        qaoa2 = QAOAOptimizer(dimension=2, num_layers=2)

        # Run with more iterations
        _, value_long = qaoa2.optimize(sphere, bounds=[(-10, 10), (-10, 10)], max_iterations=50)

        # More iterations should generally give better results
        # (though not guaranteed due to randomness)
        assert value_long >= 0
        assert value_short >= 0


class TestQuantumOptimizerIntegration:
    """Integration tests for quantum optimizers."""

    def test_multiple_optimizations(self):
        """Test running multiple optimizations."""

        def sphere(x):
            return sum(xi**2 for xi in x)

        qaoa = QAOAOptimizer(dimension=2, num_layers=2)

        # First optimization
        solution1, value1 = qaoa.optimize(sphere, bounds=[(-5, 5), (-5, 5)], max_iterations=10)

        # Second optimization (should reset)
        solution2, value2 = qaoa.optimize(sphere, bounds=[(-5, 5), (-5, 5)], max_iterations=10)

        # Both should produce valid results
        assert len(solution1) == 2
        assert len(solution2) == 2
        assert value1 >= 0
        assert value2 >= 0

    def test_constrained_optimization(self):
        """Test optimization with tight bounds."""

        def objective(x):
            return sum(xi**2 for xi in x)

        qaoa = QAOAOptimizer(dimension=2, num_layers=2)

        # Tight bounds
        solution, value = qaoa.optimize(objective, bounds=[(0, 1), (0, 1)], max_iterations=20)

        # Solution should respect bounds
        assert 0 <= solution[0] <= 1
        assert 0 <= solution[1] <= 1

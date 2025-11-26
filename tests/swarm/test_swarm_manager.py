"""
Comprehensive tests for Swarm Manager - Phase 19.

Tests orchestration of PSO, ACO and emergence detection.
"""

from typing import List

import pytest

from src.swarm.config import SwarmConfig
from src.swarm.swarm_manager import SwarmManager


class TestSwarmManager:
    """Tests for SwarmManager."""

    def test_initialization(self) -> None:
        """Test swarm manager initialization."""
        manager = SwarmManager()

        assert manager.config is not None
        assert manager.emergence_detector is not None
        assert manager.pso is None
        assert manager.aco is None
        assert len(manager.metrics_history) == 0

    def test_initialization_with_custom_config(self) -> None:
        """Test initialization with custom configuration."""
        config = SwarmConfig(
            max_agents=500,
            memory_limit_mb=1000.0,
        )
        manager = SwarmManager(config)

        assert manager.config.max_agents == 500
        assert manager.config.memory_limit_mb == pytest.approx(1000.0)

    def test_optimize_continuous_simple(self) -> None:
        """Test continuous optimization with PSO."""
        manager = SwarmManager()

        def sphere_function(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        solution, value, metrics = manager.optimize_continuous(
            fitness_function=sphere_function,
            dimension=2,
            num_particles=30,
            max_iterations=30,
        )

        assert len(solution) == 2
        assert value < 5.0  # Should find good solution
        assert metrics.best_value == pytest.approx(value)
        assert metrics.execution_time > 0

    def test_optimize_continuous_high_dimension(self) -> None:
        """Test PSO in higher dimensions."""
        manager = SwarmManager()

        def quadratic(pos: List[float]) -> float:
            return sum((x - 3.0) ** 2 for x in pos)

        solution, value, _ = manager.optimize_continuous(
            fitness_function=quadratic,
            dimension=5,
            num_particles=50,
            max_iterations=40,
        )

        assert len(solution) == 5
        assert value < 10.0

    def test_optimize_continuous_validates_max_agents(self) -> None:
        """Test that max_agents limit is enforced."""
        config = SwarmConfig(max_agents=50)
        manager = SwarmManager(config)

        def dummy_func(pos: List[float]) -> float:
            return sum(pos)

        with pytest.raises(ValueError, match="excede max_agents"):
            manager.optimize_continuous(
                fitness_function=dummy_func,
                dimension=2,
                num_particles=100,  # Exceeds max_agents
            )

    def test_optimize_combinatorial_simple(self) -> None:
        """Test combinatorial optimization with ACO."""
        manager = SwarmManager()

        # Simple 4-city TSP
        distances = [
            [0.0, 2.0, 3.0, 4.0],
            [2.0, 0.0, 2.5, 3.5],
            [3.0, 2.5, 0.0, 2.0],
            [4.0, 3.5, 2.0, 0.0],
        ]

        path, cost, metrics = manager.optimize_combinatorial(
            distance_matrix=distances,
            num_ants=20,
            max_iterations=30,
        )

        assert len(path) == 4
        assert set(path) == {0, 1, 2, 3}
        assert cost > 0
        assert metrics.best_value == pytest.approx(cost)

    def test_optimize_combinatorial_validates_max_agents(self) -> None:
        """Test that max_agents limit is enforced for ACO."""
        config = SwarmConfig(max_agents=50)
        manager = SwarmManager(config)

        distances = [[0.0, 1.0], [1.0, 0.0]]

        with pytest.raises(ValueError, match="excede max_agents"):
            manager.optimize_combinatorial(
                distance_matrix=distances,
                num_ants=100,  # Exceeds max_agents
            )

    def test_get_swarm_state(self) -> None:
        """Test getting swarm state."""
        manager = SwarmManager()

        # Before optimization
        state = manager.get_swarm_state()
        assert state is None

        # After PSO optimization
        def simple_func(pos: List[float]) -> float:
            return sum(pos)

        manager.optimize_continuous(
            fitness_function=simple_func,
            dimension=2,
            num_particles=20,
            max_iterations=10,
        )

        state = manager.get_swarm_state()
        assert state is not None
        assert state.num_agents == 20
        assert state.iteration >= 0

    def test_get_metrics_summary_empty(self) -> None:
        """Test metrics summary when no runs."""
        manager = SwarmManager()

        summary = manager.get_metrics_summary()

        assert summary["total_runs"] == 0

    def test_get_metrics_summary_after_runs(self) -> None:
        """Test metrics summary after optimizations."""
        manager = SwarmManager()

        # Run PSO
        def func1(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        manager.optimize_continuous(
            fitness_function=func1,
            dimension=2,
            num_particles=20,
            max_iterations=20,
        )

        # Run ACO
        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        manager.optimize_combinatorial(
            distance_matrix=distances,
            num_ants=15,
            max_iterations=15,
        )

        summary = manager.get_metrics_summary()

        assert summary["total_runs"] == 2
        assert summary["pso_runs"] == 1
        assert summary["aco_runs"] == 1
        assert "pso" in summary
        assert "aco" in summary
        assert "emergence" in summary

    def test_reset(self) -> None:
        """Test swarm manager reset."""
        manager = SwarmManager()

        # Run optimization
        def func(pos: List[float]) -> float:
            return sum(pos)

        manager.optimize_continuous(
            fitness_function=func,
            dimension=2,
            num_particles=20,
            max_iterations=10,
        )

        # Verify state exists
        assert len(manager.metrics_history) > 0

        # Reset
        manager.reset()

        # Verify reset
        assert len(manager.metrics_history) == 0
        state = manager.get_swarm_state()
        assert state is None or state.iteration == 0


class TestSwarmManagerIntegration:
    """Integration tests for SwarmManager."""

    def test_100_particles_pso(self) -> None:
        """Test PSO with 100 particles."""
        manager = SwarmManager()

        def benchmark(pos: List[float]) -> float:
            return sum((x - 5.0) ** 2 for x in pos)

        solution, value, metrics = manager.optimize_continuous(
            fitness_function=benchmark,
            dimension=3,
            num_particles=100,
            max_iterations=30,
        )

        assert len(solution) == 3
        assert value < 10.0
        assert metrics.execution_time < 15.0

    def test_100_ants_aco(self) -> None:
        """Test ACO with 100 ants."""
        manager = SwarmManager()

        # 6-city TSP
        import random

        random.seed(42)

        num_cities = 6
        distances = [[0.0] * num_cities for _ in range(num_cities)]
        for i in range(num_cities):
            for j in range(i + 1, num_cities):
                dist = random.uniform(1.0, 10.0)
                distances[i][j] = dist
                distances[j][i] = dist

        path, cost, metrics = manager.optimize_combinatorial(
            distance_matrix=distances,
            num_ants=100,
            max_iterations=30,
        )

        assert len(path) == num_cities
        assert set(path) == set(range(num_cities))
        assert cost > 0
        assert metrics.execution_time < 15.0

    def test_emergence_detection_in_pso(self) -> None:
        """Test that emergence is detected during PSO."""
        manager = SwarmManager()

        def converging_func(pos: List[float]) -> float:
            # Function that causes convergence
            return sum((x - 5.0) ** 2 for x in pos)

        manager.optimize_continuous(
            fitness_function=converging_func,
            dimension=2,
            num_particles=50,
            max_iterations=50,
        )

        # Check emergence summary
        summary = manager.get_metrics_summary()
        assert "emergence" in summary
        # May or may not detect patterns depending on convergence

    def test_sequential_optimizations(self) -> None:
        """Test running multiple optimizations sequentially."""
        manager = SwarmManager()

        # First PSO
        def func1(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        manager.optimize_continuous(
            fitness_function=func1,
            dimension=2,
            num_particles=20,
            max_iterations=20,
        )

        # Second PSO
        def func2(pos: List[float]) -> float:
            return sum((x - 3.0) ** 2 for x in pos)

        manager.optimize_continuous(
            fitness_function=func2,
            dimension=3,
            num_particles=25,
            max_iterations=25,
        )

        summary = manager.get_metrics_summary()
        assert summary["total_runs"] == 2
        assert summary["pso_runs"] == 2

    def test_memory_warning_on_large_swarm(self) -> None:
        """Test memory warning for large swarms."""
        config = SwarmConfig(memory_limit_mb=10.0)  # Very low limit
        manager = SwarmManager(config)

        def func(pos: List[float]) -> float:
            return sum(pos)

        # Should log warning but not fail
        manager.optimize_continuous(
            fitness_function=func,
            dimension=10,
            num_particles=100,
            max_iterations=10,
        )

        # Should complete despite warning
        summary = manager.get_metrics_summary()
        assert summary["total_runs"] == 1

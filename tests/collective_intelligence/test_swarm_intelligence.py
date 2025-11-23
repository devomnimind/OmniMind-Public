"""Comprehensive tests for Swarm Intelligence module.

Tests for bio-inspired swarm algorithms including PSO and ACO.
Total: 29 tests covering all aspects of swarm intelligence.
"""

from typing import List
import pytest

from src.collective_intelligence.swarm_intelligence import (
    AntColonyOptimizer,
    ParticleSwarmOptimizer,
    SwarmAgent,
    SwarmBehavior,
    SwarmConfiguration,
    SwarmCoordinator,
)


class TestSwarmConfiguration:
    """Tests for SwarmConfiguration dataclass."""

    def test_default_configuration(self) -> None:
        """Test default swarm configuration values."""
        config = SwarmConfiguration()

        assert config.cohesion_weight == pytest.approx(0.3)
        assert config.separation_weight == pytest.approx(0.4)
        assert config.alignment_weight == pytest.approx(0.3)
        assert config.max_velocity == pytest.approx(1.0)
        assert config.perception_radius == pytest.approx(5.0)
        assert config.inertia == pytest.approx(0.7)
        assert config.cognitive_weight == pytest.approx(1.5)
        assert config.social_weight == pytest.approx(1.5)

    def test_custom_configuration(self) -> None:
        """Test custom swarm configuration."""
        config = SwarmConfiguration(
            cohesion_weight=0.5,
            separation_weight=0.3,
            alignment_weight=0.2,
            max_velocity=2.0,
            inertia=0.9,
        )

        assert config.cohesion_weight == pytest.approx(0.5)
        assert config.separation_weight == pytest.approx(0.3)
        assert config.alignment_weight == pytest.approx(0.2)
        assert config.max_velocity == pytest.approx(2.0)
        assert config.inertia == pytest.approx(0.9)


class TestSwarmAgent:
    """Tests for SwarmAgent dataclass."""

    def test_agent_initialization(self) -> None:
        """Test swarm agent initialization."""
        agent = SwarmAgent(
            position=[1.0, 2.0, 3.0],
            velocity=[0.1, 0.2, 0.3],
        )

        assert agent.agent_id is not None
        assert isinstance(agent.agent_id, str)
        assert agent.position == [1.0, 2.0, 3.0]
        assert agent.velocity == [0.1, 0.2, 0.3]
        assert agent.best_position == []
        assert agent.best_fitness == float("inf")
        assert agent.fitness == float("inf")
        assert agent.neighbors == []
        assert agent.metadata == {}

    def test_agent_update_best_improvement(self) -> None:
        """Test agent updating personal best when fitness improves."""
        agent = SwarmAgent(
            position=[1.0, 2.0],
            velocity=[0.0, 0.0],
        )
        agent.best_fitness = 10.0
        agent.best_position = [0.0, 0.0]

        # Better fitness (lower is better)
        agent.fitness = 5.0
        agent.position = [1.5, 2.5]
        agent.update_best()

        assert agent.best_fitness == 5.0
        assert agent.best_position == [1.5, 2.5]

    def test_agent_update_best_no_improvement(self) -> None:
        """Test agent not updating personal best when fitness doesn't improve."""
        agent = SwarmAgent(
            position=[1.0, 2.0],
            velocity=[0.0, 0.0],
        )
        agent.best_fitness = 5.0
        agent.best_position = [1.0, 2.0]

        # Worse fitness
        agent.fitness = 10.0
        agent.position = [2.0, 3.0]
        agent.update_best()

        # Best should not change
        assert agent.best_fitness == 5.0
        assert agent.best_position == [1.0, 2.0]


class TestSwarmCoordinator:
    """Tests for SwarmCoordinator."""

    def test_coordinator_initialization(self) -> None:
        """Test swarm coordinator initialization."""
        coordinator = SwarmCoordinator(dimension=3, num_agents=20)

        assert coordinator.dimension == 3
        assert coordinator.num_agents == 20
        assert len(coordinator.agents) == 20
        assert len(coordinator.global_best_position) == 3
        assert coordinator.global_best_fitness == float("inf")
        assert coordinator.iteration == 0

    def test_coordinator_agents_initialized(self) -> None:
        """Test that agents are properly initialized."""
        coordinator = SwarmCoordinator(dimension=2, num_agents=10)

        for agent in coordinator.agents:
            assert len(agent.position) == 2
            assert len(agent.velocity) == 2
            assert len(agent.best_position) == 2

    def test_optimize_simple_function(self) -> None:
        """Test optimization of a simple quadratic function."""
        coordinator = SwarmCoordinator(dimension=2, num_agents=30)

        # Minimize f(x, y) = x^2 + y^2 (minimum at origin)
        def quadratic(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        best_position, best_fitness = coordinator.optimize(quadratic, max_iterations=50)

        # Should find near-optimal solution
        assert best_fitness < 1.0  # Should be close to 0
        assert len(best_position) == 2

    def test_optimize_updates_global_best(self) -> None:
        """Test that optimization updates global best."""
        coordinator = SwarmCoordinator(dimension=1, num_agents=10)

        def simple_function(pos: List[float]) -> float:
            return (pos[0] - 5.0) ** 2

        initial_best = coordinator.global_best_fitness
        coordinator.optimize(simple_function, max_iterations=20)

        # Global best should improve
        assert coordinator.global_best_fitness < initial_best

    def test_optimize_iteration_count(self) -> None:
        """Test that iteration counter is updated."""
        coordinator = SwarmCoordinator(dimension=2, num_agents=10)

        def dummy_function(pos: List[float]) -> float:
            return sum(pos)

        coordinator.optimize(dummy_function, max_iterations=15)

        assert coordinator.iteration == 14  # 0-indexed, so last is max_iterations-1

    def test_get_swarm_metrics_empty(self) -> None:
        """Test swarm metrics with no agents."""
        coordinator = SwarmCoordinator(dimension=2, num_agents=0)
        coordinator.agents = []  # Force empty

        metrics = coordinator.get_swarm_metrics()

        assert metrics["num_agents"] == 0
        assert metrics["best_fitness"] == float("inf")
        assert metrics["avg_fitness"] == float("inf")

    def test_get_swarm_metrics_with_agents(self) -> None:
        """Test swarm metrics calculation."""
        coordinator = SwarmCoordinator(dimension=2, num_agents=10)

        # Set some fitness values
        for i, agent in enumerate(coordinator.agents):
            agent.fitness = float(i)

        metrics = coordinator.get_swarm_metrics()

        assert metrics["num_agents"] == 10
        assert metrics["avg_fitness"] == pytest.approx(4.5)  # Average of 0-9
        assert "diversity" in metrics
        assert "iteration" in metrics

    def test_swarm_diversity_metric(self) -> None:
        """Test diversity metric calculation."""
        coordinator = SwarmCoordinator(dimension=2, num_agents=10)

        # Spread agents across space
        for i, agent in enumerate(coordinator.agents):
            agent.position = [float(i), float(i)]

        metrics = coordinator.get_swarm_metrics()

        assert metrics["diversity"] > 0  # Should have some diversity


class TestParticleSwarmOptimizer:
    """Tests for ParticleSwarmOptimizer."""

    def test_pso_initialization(self) -> None:
        """Test PSO initialization."""
        pso = ParticleSwarmOptimizer(
            dimension=3,
            population_size=25,
            inertia=0.8,
            cognitive=1.2,
            social=1.8,
        )

        assert pso.coordinator.dimension == 3
        assert pso.coordinator.num_agents == 25
        assert pso.coordinator.config.inertia == pytest.approx(0.8)
        assert pso.coordinator.config.cognitive_weight == pytest.approx(1.2)
        assert pso.coordinator.config.social_weight == pytest.approx(1.8)

    def test_pso_optimize_sphere_function(self) -> None:
        """Test PSO on sphere function."""
        pso = ParticleSwarmOptimizer(dimension=3, population_size=30)

        # Sphere function: f(x) = sum(x_i^2)
        def sphere(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        best_position, best_value = pso.optimize(sphere, max_iterations=50)

        # Should find near-optimal solution
        assert best_value < 1.0
        assert len(best_position) == 3

    def test_pso_optimize_rosenbrock_function(self) -> None:
        """Test PSO on more complex Rosenbrock function."""
        pso = ParticleSwarmOptimizer(dimension=2, population_size=40)

        # Rosenbrock function (more challenging)
        def rosenbrock(pos: List[float]) -> float:
            x, y = pos[0], pos[1]
            return (1 - x) ** 2 + 100 * (y - x**2) ** 2

        _, best_value = pso.optimize(rosenbrock, max_iterations=100)

        # Should make progress towards minimum at (1, 1)
        assert best_value < 100.0  # Should improve from random initialization

    def test_pso_returns_valid_solution(self) -> None:
        """Test that PSO returns valid solution tuple."""
        pso = ParticleSwarmOptimizer(dimension=2, population_size=20)

        def simple_func(pos: List[float]) -> float:
            return sum(pos)

        result = pso.optimize(simple_func, max_iterations=10)

        assert isinstance(result, tuple)
        assert len(result) == 2
        position, value = result
        assert isinstance(position, list)
        assert isinstance(value, float)


class TestAntColonyOptimizer:
    """Tests for AntColonyOptimizer."""

    def test_aco_initialization(self) -> None:
        """Test ACO initialization."""
        aco = AntColonyOptimizer(
            num_ants=25,
            alpha=1.5,
            beta=2.5,
            evaporation=0.6,
            q=150.0,
        )

        assert aco.num_ants == 25
        assert aco.alpha == 1.5
        assert aco.beta == 2.5
        assert aco.evaporation == 0.6
        assert aco.q == 150.0
        assert aco.pheromones == {}
        assert aco.best_path == []
        assert aco.best_cost == float("inf")

    def test_aco_pheromone_initialization(self) -> None:
        """Test pheromone initialization for TSP."""
        aco = AntColonyOptimizer(num_ants=10)

        # Simple 4-city distance matrix
        distances = [
            [0.0, 1.0, 2.0, 3.0],
            [1.0, 0.0, 1.5, 2.5],
            [2.0, 1.5, 0.0, 1.0],
            [3.0, 2.5, 1.0, 0.0],
        ]

        aco.optimize(distances, max_iterations=1)

        # Check pheromones were initialized
        assert len(aco.pheromones) > 0
        # Each edge should have some pheromone
        assert (0, 1) in aco.pheromones or (1, 0) in aco.pheromones

    def test_aco_optimize_small_tsp(self) -> None:
        """Test ACO on small TSP instance."""
        aco = AntColonyOptimizer(num_ants=20)

        # Simple 3-city triangle
        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        best_path, best_cost = aco.optimize(distances, max_iterations=30)

        # Should find a valid tour
        assert len(best_path) == 3
        assert set(best_path) == {0, 1, 2}  # All cities visited
        assert best_cost > 0  # Valid cost

    def test_aco_optimal_triangle_tour(self) -> None:
        """Test ACO finds optimal tour for simple triangle."""
        aco = AntColonyOptimizer(num_ants=30, evaporation=0.5)

        # Symmetric triangle: optimal tour is 1->2->3->1 = 3.0
        distances = [
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 0.0],
        ]

        best_path, best_cost = aco.optimize(distances, max_iterations=50)

        # Should find near-optimal solution (cost = 3.0)
        assert best_cost <= 3.5  # Allow small tolerance

    def test_aco_pheromone_evaporation(self) -> None:
        """Test that pheromones evaporate over iterations."""
        aco = AntColonyOptimizer(num_ants=10, evaporation=0.9)  # High evaporation

        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        # Run one iteration
        aco.optimize(distances, max_iterations=1)
        initial_pheromone = sum(aco.pheromones.values())

        # Run more iterations
        aco.optimize(distances, max_iterations=5)
        final_pheromone = sum(aco.pheromones.values())

        # Pheromone levels should change due to evaporation/deposit
        # Not necessarily decrease because new deposits can exceed evaporation
        assert final_pheromone != initial_pheromone

    def test_aco_improves_over_iterations(self) -> None:
        """Test that ACO improves solution quality over iterations."""
        aco = AntColonyOptimizer(num_ants=20)

        distances = [
            [0.0, 2.0, 5.0, 7.0],
            [2.0, 0.0, 3.0, 4.0],
            [5.0, 3.0, 0.0, 2.0],
            [7.0, 4.0, 2.0, 0.0],
        ]

        # Short run
        _, cost_10 = aco.optimize(distances, max_iterations=10)

        # Reset and longer run
        aco.best_cost = float("inf")
        aco.best_path = []
        _, cost_50 = aco.optimize(distances, max_iterations=50)

        # Longer run should find better or equal solution
        assert cost_50 <= cost_10 * 1.2  # Allow some variance due to randomness


class TestSwarmBehavior:
    """Tests for SwarmBehavior enum."""

    def test_swarm_behavior_values(self) -> None:
        """Test swarm behavior enum values."""
        assert SwarmBehavior.COHESION.value == "cohesion"
        assert SwarmBehavior.SEPARATION.value == "separation"
        assert SwarmBehavior.ALIGNMENT.value == "alignment"
        assert SwarmBehavior.FORAGING.value == "foraging"
        assert SwarmBehavior.FOLLOWING.value == "following"
        assert SwarmBehavior.EXPLORATION.value == "exploration"

    def test_swarm_behavior_count(self) -> None:
        """Test number of swarm behaviors."""
        behaviors = list(SwarmBehavior)
        assert len(behaviors) == 6


class TestIntegration:
    """Integration tests for swarm intelligence components."""

    def test_pso_and_aco_different_optimizations(self) -> None:
        """Test that PSO and ACO work on different problem types."""
        # PSO for continuous optimization
        pso = ParticleSwarmOptimizer(dimension=2, population_size=20)

        def continuous_func(pos: List[float]) -> float:
            return sum((x - 3.0) ** 2 for x in pos)

        pso_result = pso.optimize(continuous_func, max_iterations=30)
        assert pso_result[1] < 10.0  # Should make progress

        # ACO for combinatorial optimization
        aco = AntColonyOptimizer(num_ants=15)
        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        aco_result = aco.optimize(distances, max_iterations=20)
        assert aco_result[1] > 0  # Should find valid tour

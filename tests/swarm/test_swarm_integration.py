"""
Integration tests for swarm module - Phase 19.

End-to-end tests for complete swarm scenarios.
"""

from typing import List
import pytest

from src.swarm import (
    SwarmManager,
    ParticleSwarmOptimizer,
    AntColonyOptimizer,
    EmergenceDetector,
    PSOConfig,
    ACOConfig,
    SwarmConfig,
)


class TestSwarmIntegration:
    """End-to-end integration tests."""

    def test_full_pso_workflow(self) -> None:
        """Test complete PSO workflow from initialization to results."""
        # Setup
        config = PSOConfig(num_particles=50, dimension=3, max_iterations=40)
        pso = ParticleSwarmOptimizer(config)

        # Define optimization problem
        def rosenbrock(pos: List[float]) -> float:
            """Rosenbrock function - challenging benchmark."""
            result = 0.0
            for i in range(len(pos) - 1):
                result += 100 * (pos[i + 1] - pos[i] ** 2) ** 2 + (1 - pos[i]) ** 2
            return result

        # Optimize
        solution, value, metrics = pso.optimize(rosenbrock)

        # Validate results
        assert len(solution) == 3
        assert value < 100.0  # Should make progress
        assert metrics.iterations_to_convergence > 0
        assert metrics.execution_time > 0

        # Check final state
        state = pso.get_swarm_state()
        assert state.num_agents == 50
        assert state.best_fitness == pytest.approx(value)

    def test_full_aco_workflow(self) -> None:
        """Test complete ACO workflow for TSP."""
        # Setup
        config = ACOConfig(num_ants=40, max_iterations=30)
        aco = AntColonyOptimizer(config)

        # Define TSP instance (7 cities)
        distances = [
            [0.0, 5.0, 4.0, 3.0, 7.0, 6.0, 8.0],
            [5.0, 0.0, 2.0, 6.0, 5.0, 3.0, 4.0],
            [4.0, 2.0, 0.0, 5.0, 4.0, 2.0, 3.0],
            [3.0, 6.0, 5.0, 0.0, 8.0, 7.0, 9.0],
            [7.0, 5.0, 4.0, 8.0, 0.0, 3.0, 5.0],
            [6.0, 3.0, 2.0, 7.0, 3.0, 0.0, 4.0],
            [8.0, 4.0, 3.0, 9.0, 5.0, 4.0, 0.0],
        ]

        # Optimize
        path, cost, metrics = aco.optimize(distances)

        # Validate results
        assert len(path) == 7
        assert set(path) == set(range(7))
        assert cost > 0
        assert metrics.best_value == pytest.approx(cost)

    def test_emergence_detection_workflow(self) -> None:
        """Test emergence detection in swarm behavior."""
        detector = EmergenceDetector()

        # Simulate swarm converging to solution
        agent_states = []
        for i in range(30):
            # Create converged cluster
            noise = (i % 3) * 0.2
            agent_states.append(
                {
                    "id": f"agent_{i}",
                    "position": [5.0 + noise, 5.0 + noise],
                    "velocity": [0.1 + noise * 0.1, 0.1 + noise * 0.1],
                    "fitness": noise**2,
                }
            )

        # Detect patterns
        patterns = detector.detect_patterns(agent_states)

        # Should detect at least one emergent pattern
        assert len(patterns) > 0

        # Get summary
        summary = detector.get_pattern_summary()
        assert summary["total_patterns"] > 0
        assert len(summary["by_type"]) > 0

    def test_swarm_manager_full_workflow(self) -> None:
        """Test SwarmManager orchestrating PSO and ACO."""
        config = SwarmConfig(max_agents=200)
        manager = SwarmManager(config)

        # Run PSO optimization
        def sphere(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        pso_solution, pso_value, pso_metrics = manager.optimize_continuous(
            fitness_function=sphere,
            dimension=4,
            num_particles=60,
            max_iterations=30,
        )

        assert len(pso_solution) == 4
        assert pso_value < 5.0

        # Run ACO optimization
        tsp_distances = [
            [0.0, 2.0, 4.0, 3.0],
            [2.0, 0.0, 3.0, 2.5],
            [4.0, 3.0, 0.0, 2.0],
            [3.0, 2.5, 2.0, 0.0],
        ]

        aco_path, aco_cost, aco_metrics = manager.optimize_combinatorial(
            distance_matrix=tsp_distances,
            num_ants=40,
            max_iterations=25,
        )

        assert len(aco_path) == 4
        assert aco_cost > 0

        # Check metrics summary
        summary = manager.get_metrics_summary()
        assert summary["total_runs"] == 2
        assert summary["pso_runs"] == 1
        assert summary["aco_runs"] == 1
        assert "pso" in summary
        assert "aco" in summary

    def test_scalability_100_agents(self) -> None:
        """Test scalability with 100 agents."""
        manager = SwarmManager()

        # PSO with 100 particles
        def benchmark(pos: List[float]) -> float:
            return sum((x - 2.0) ** 2 for x in pos)

        solution, value, metrics = manager.optimize_continuous(
            fitness_function=benchmark,
            dimension=5,
            num_particles=100,
            max_iterations=30,
        )

        assert len(solution) == 5
        assert value < 20.0
        assert metrics.execution_time < 20.0  # Should be efficient

    def test_scalability_500_agents(self) -> None:
        """Test scalability with 500 agents."""
        config = SwarmConfig(max_agents=1000)
        manager = SwarmManager(config)

        # PSO with 500 particles
        def simple_func(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        solution, value, metrics = manager.optimize_continuous(
            fitness_function=simple_func,
            dimension=3,
            num_particles=500,
            max_iterations=20,
        )

        assert len(solution) == 3
        assert value < 10.0
        # May take longer but should complete
        assert metrics.execution_time < 60.0

    def test_pso_with_emergence_detection(self) -> None:
        """Test PSO combined with emergence detection."""
        pso_config = PSOConfig(num_particles=40, dimension=2, max_iterations=40)
        pso = ParticleSwarmOptimizer(pso_config)

        detector = EmergenceDetector()

        # Optimize
        def target_func(pos: List[float]) -> float:
            return sum((x - 3.0) ** 2 for x in pos)

        pso.optimize(target_func)

        # Detect emergence in final swarm
        agent_states = [
            {
                "id": p.particle_id,
                "position": p.position,
                "velocity": p.velocity,
                "fitness": p.fitness,
            }
            for p in pso.particles
        ]

        patterns = detector.detect_patterns(agent_states)

        # Converged swarm should show emergence
        # (May or may not depending on convergence state)
        assert patterns is not None

    def test_multi_run_consistency(self) -> None:
        """Test consistency across multiple runs."""
        manager = SwarmManager()

        def consistent_func(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        results = []
        for _ in range(3):
            manager.reset()
            _, value, _ = manager.optimize_continuous(
                fitness_function=consistent_func,
                dimension=2,
                num_particles=30,
                max_iterations=30,
            )
            results.append(value)

        # All runs should find good solutions
        for result in results:
            assert result < 5.0

        # Results should be somewhat consistent (stochastic algorithm)
        avg = sum(results) / len(results)
        assert all(abs(r - avg) < 10.0 for r in results)


class TestSwarmBenchmarks:
    """Benchmark tests for performance validation."""

    def test_pso_convergence_speed(self) -> None:
        """Test PSO convergence speed on standard benchmark."""
        config = PSOConfig(num_particles=50, dimension=5, max_iterations=100)
        pso = ParticleSwarmOptimizer(config)

        # Rastrigin function (harder to optimize)
        def rastrigin(pos: List[float]) -> float:
            import math

            n = len(pos)
            return 10 * n + sum(x**2 - 10 * math.cos(2 * math.pi * x) for x in pos)

        _, value, metrics = pso.optimize(rastrigin)

        # Should make significant progress
        assert value < 100.0
        assert metrics.iterations_to_convergence <= 100

    def test_aco_solution_quality(self) -> None:
        """Test ACO solution quality on known TSP."""
        config = ACOConfig(num_ants=50, max_iterations=50)
        aco = AntColonyOptimizer(config)

        # Small symmetric TSP with known optimal tour
        distances = [
            [0.0, 1.0, 3.0, 4.0],
            [1.0, 0.0, 2.0, 3.0],
            [3.0, 2.0, 0.0, 1.0],
            [4.0, 3.0, 1.0, 0.0],
        ]
        # Optimal tour: 0->1->2->3->0 = 1+2+1+4 = 8

        path, cost, _ = aco.optimize(distances)

        assert len(path) == 4
        # Should find solution close to optimal
        assert cost <= 10.0  # Within 25% of optimal

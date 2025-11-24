#!/usr/bin/env python
"""
Example usage of Phase 19 Swarm Intelligence module.

Demonstrates PSO, ACO, and emergence detection capabilities.
"""

from typing import List
from src.swarm import (
    SwarmManager,
    ParticleSwarmOptimizer,
    AntColonyOptimizer,
    PSOConfig,
    ACOConfig,
)


def example_pso():
    """Example: Optimize continuous function with PSO."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Particle Swarm Optimization (PSO)")
    print("=" * 60)

    # Define optimization problem
    def sphere_function(position: List[float]) -> float:
        """Minimize sphere function: f(x) = sum(x_i^2)"""
        return sum(x**2 for x in position)

    # Configure PSO
    config = PSOConfig(
        num_particles=50,
        dimension=3,
        max_iterations=30,
        inertia=0.7,
        cognitive_weight=1.5,
        social_weight=1.5,
    )

    # Create optimizer
    pso = ParticleSwarmOptimizer(config)

    # Optimize
    solution, value, metrics = pso.optimize(sphere_function)

    # Results
    print(f"\n✅ Optimization Complete!")
    print(f"   Best Solution: {[f'{x:.4f}' for x in solution]}")
    print(f"   Best Value: {value:.6f}")
    print(f"   Iterations: {metrics.iterations_to_convergence}")
    print(f"   Execution Time: {metrics.execution_time:.3f}s")

    # Check swarm state
    state = pso.get_swarm_state()
    print(f"\n📊 Swarm State:")
    print(f"   Agents: {state.num_agents}")
    print(f"   Diversity: {state.diversity:.4f}")
    print(f"   Convergence: {state.convergence:.4f}")


def example_aco():
    """Example: Solve TSP with ACO."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Ant Colony Optimization (ACO) - TSP")
    print("=" * 60)

    # Define TSP distance matrix (5 cities)
    distances = [
        [0.0, 2.0, 4.0, 5.0, 3.0],
        [2.0, 0.0, 3.0, 4.0, 2.5],
        [4.0, 3.0, 0.0, 2.0, 4.5],
        [5.0, 4.0, 2.0, 0.0, 3.5],
        [3.0, 2.5, 4.5, 3.5, 0.0],
    ]

    # Configure ACO
    config = ACOConfig(
        num_ants=40,
        max_iterations=30,
        alpha=1.0,
        beta=2.0,
        evaporation_rate=0.5,
        elite_weight=2.0,
    )

    # Create optimizer
    aco = AntColonyOptimizer(config)

    # Optimize
    path, cost, metrics = aco.optimize(distances)

    # Results
    print(f"\n✅ Optimization Complete!")
    print(f"   Best Path: {' -> '.join(map(str, path))} -> {path[0]}")
    print(f"   Tour Cost: {cost:.2f}")
    print(f"   Iterations: {metrics.iterations_to_convergence}")
    print(f"   Execution Time: {metrics.execution_time:.3f}s")


def example_swarm_manager():
    """Example: Use SwarmManager for orchestration."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: SwarmManager Orchestration")
    print("=" * 60)

    manager = SwarmManager()

    # Run PSO
    print("\n🔵 Running PSO...")

    def rosenbrock(pos: List[float]) -> float:
        """Rosenbrock function (harder to optimize)."""
        result = 0.0
        for i in range(len(pos) - 1):
            result += 100 * (pos[i + 1] - pos[i] ** 2) ** 2 + (1 - pos[i]) ** 2
        return result

    pso_sol, pso_val, pso_metrics = manager.optimize_continuous(
        fitness_function=rosenbrock,
        dimension=2,
        num_particles=60,
        max_iterations=40,
    )

    print(f"   PSO Best: {pso_val:.4f} in {pso_metrics.execution_time:.3f}s")

    # Run ACO
    print("\n🟠 Running ACO...")

    tsp_matrix = [
        [0.0, 1.0, 2.0, 3.0],
        [1.0, 0.0, 1.5, 2.5],
        [2.0, 1.5, 0.0, 1.0],
        [3.0, 2.5, 1.0, 0.0],
    ]

    aco_path, aco_cost, aco_metrics = manager.optimize_combinatorial(
        distance_matrix=tsp_matrix,
        num_ants=30,
        max_iterations=25,
    )

    print(f"   ACO Tour Cost: {aco_cost:.2f} in {aco_metrics.execution_time:.3f}s")

    # Get summary
    print("\n📈 Manager Summary:")
    summary = manager.get_metrics_summary()
    print(f"   Total Runs: {summary['total_runs']}")
    print(f"   PSO Runs: {summary['pso_runs']}")
    print(f"   ACO Runs: {summary['aco_runs']}")
    print(f"   Emergence Patterns: {summary['emergence']['total_patterns']}")


def main():
    """Run all examples."""
    print("\n" + "🧠 " * 20)
    print("  PHASE 19: DISTRIBUTED COLLECTIVE INTELLIGENCE")
    print("  Examples & Demonstrations")
    print("🧠 " * 20)

    example_pso()
    example_aco()
    example_swarm_manager()

    print("\n" + "=" * 60)
    print("✨ All examples completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

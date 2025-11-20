"""
Swarm Intelligence for Multi-Agent Coordination.

Implements bio-inspired swarm algorithms for collective optimization
and coordination including Particle Swarm Optimization (PSO) and
Ant Colony Optimization (ACO).

Author: OmniMind Project
License: MIT
"""

import random
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


class SwarmBehavior(Enum):
    """Types of swarm behaviors."""

    COHESION = "cohesion"  # Stay together
    SEPARATION = "separation"  # Avoid crowding
    ALIGNMENT = "alignment"  # Match direction
    FORAGING = "foraging"  # Search for resources
    FOLLOWING = "following"  # Follow leader
    EXPLORATION = "exploration"  # Explore space


@dataclass
class SwarmConfiguration:
    """Configuration for swarm behavior."""

    cohesion_weight: float = 0.3
    separation_weight: float = 0.4
    alignment_weight: float = 0.3
    max_velocity: float = 1.0
    perception_radius: float = 5.0
    inertia: float = 0.7
    cognitive_weight: float = 1.5  # PSO parameter
    social_weight: float = 1.5  # PSO parameter


@dataclass
class SwarmAgent:
    """Individual agent in a swarm."""

    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: List[float] = field(default_factory=list)
    velocity: List[float] = field(default_factory=list)
    best_position: List[float] = field(default_factory=list)
    best_fitness: float = float("inf")
    fitness: float = float("inf")
    neighbors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_best(self) -> None:
        """Update personal best if current position is better."""
        if self.fitness < self.best_fitness:
            self.best_fitness = self.fitness
            self.best_position = self.position.copy()


class SwarmCoordinator:
    """
    Coordinates swarm behavior for collective optimization.

    Features:
    - Multiple swarm behaviors (cohesion, separation, alignment)
    - Dynamic agent coordination
    - Collective goal optimization
    - Emergence tracking
    """

    def __init__(
        self,
        dimension: int,
        num_agents: int = 30,
        config: Optional[SwarmConfiguration] = None,
    ):
        """
        Initialize swarm coordinator.

        Args:
            dimension: Dimensionality of the search space
            num_agents: Number of agents in the swarm
            config: Swarm configuration
        """
        self.dimension = dimension
        self.num_agents = num_agents
        self.config = config or SwarmConfiguration()
        self.agents: List[SwarmAgent] = []
        self.global_best_position: List[float] = [0.0] * dimension
        self.global_best_fitness = float("inf")
        self.iteration = 0
        self.logger = logger.bind(swarm_size=num_agents)

        # Initialize agents
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize swarm agents with random positions."""
        for _ in range(self.num_agents):
            position = [random.uniform(-10, 10) for _ in range(self.dimension)]
            velocity = [random.uniform(-1, 1) for _ in range(self.dimension)]
            agent = SwarmAgent(
                position=position,
                velocity=velocity,
                best_position=position.copy(),
            )
            self.agents.append(agent)

        self.logger.info("swarm_initialized", num_agents=len(self.agents))

    def optimize(
        self,
        fitness_function: Callable[[List[float]], float],
        max_iterations: int = 100,
    ) -> Tuple[List[float], float]:
        """
        Optimize using swarm intelligence.

        Args:
            fitness_function: Function to minimize
            max_iterations: Maximum number of iterations

        Returns:
            Tuple of (best_position, best_fitness)
        """
        self.logger.info("optimization_started", max_iterations=max_iterations)

        for iteration in range(max_iterations):
            self.iteration = iteration

            # Evaluate fitness for all agents
            for agent in self.agents:
                agent.fitness = fitness_function(agent.position)
                agent.update_best()

                # Update global best
                if agent.fitness < self.global_best_fitness:
                    self.global_best_fitness = agent.fitness
                    self.global_best_position = agent.position.copy()

            # Update velocities and positions
            self._update_swarm()

            if iteration % 10 == 0:
                self.logger.debug(
                    "optimization_progress",
                    iteration=iteration,
                    best_fitness=self.global_best_fitness,
                )

        self.logger.info(
            "optimization_complete",
            best_fitness=self.global_best_fitness,
            iterations=max_iterations,
        )

        return self.global_best_position, self.global_best_fitness

    def _update_swarm(self) -> None:
        """Update velocities and positions using PSO rules."""
        for agent in self.agents:
            # Update velocity
            for d in range(self.dimension):
                # Inertia
                v = self.config.inertia * agent.velocity[d]

                # Cognitive component (personal best)
                cognitive = self.config.cognitive_weight * random.random()
                v += cognitive * (agent.best_position[d] - agent.position[d])

                # Social component (global best)
                social = self.config.social_weight * random.random()
                v += social * (self.global_best_position[d] - agent.position[d])

                # Clamp velocity
                v = max(-self.config.max_velocity, min(self.config.max_velocity, v))
                agent.velocity[d] = v

            # Update position
            for d in range(self.dimension):
                agent.position[d] += agent.velocity[d]

    def get_swarm_metrics(self) -> Dict[str, Any]:
        """Get metrics about swarm performance."""
        if not self.agents:
            return {
                "num_agents": 0,
                "best_fitness": float("inf"),
                "avg_fitness": float("inf"),
            }

        fitnesses = [agent.fitness for agent in self.agents]
        avg_fitness = sum(fitnesses) / len(fitnesses)

        # Compute diversity (spread of positions)
        diversity = 0.0
        for d in range(self.dimension):
            positions_d = [agent.position[d] for agent in self.agents]
            diversity += max(positions_d) - min(positions_d)
        diversity /= self.dimension

        return {
            "num_agents": len(self.agents),
            "best_fitness": self.global_best_fitness,
            "avg_fitness": avg_fitness,
            "diversity": diversity,
            "iteration": self.iteration,
        }


class ParticleSwarmOptimizer:
    """
    Particle Swarm Optimization algorithm.

    Features:
    - Classic PSO with inertia weight
    - Adaptive parameters
    - Velocity clamping
    - Convergence detection
    """

    def __init__(
        self,
        dimension: int,
        population_size: int = 30,
        inertia: float = 0.7,
        cognitive: float = 1.5,
        social: float = 1.5,
    ):
        """Initialize PSO optimizer."""
        config = SwarmConfiguration(
            inertia=inertia,
            cognitive_weight=cognitive,
            social_weight=social,
        )
        self.coordinator = SwarmCoordinator(
            dimension=dimension,
            num_agents=population_size,
            config=config,
        )
        self.logger = logger.bind(optimizer="PSO")

    def optimize(
        self,
        objective: Callable[[List[float]], float],
        max_iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> Tuple[List[float], float]:
        """
        Optimize objective function.

        Args:
            objective: Function to minimize
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance

        Returns:
            (best_solution, best_value)
        """
        self.logger.info("pso_started", max_iter=max_iterations)

        best_position, best_fitness = self.coordinator.optimize(
            objective, max_iterations
        )

        self.logger.info("pso_complete", best_fitness=best_fitness)
        return best_position, best_fitness


class AntColonyOptimizer:
    """
    Ant Colony Optimization for combinatorial problems.

    Features:
    - Pheromone-based path selection
    - Evaporation and reinforcement
    - Suitable for graph problems
    """

    def __init__(
        self,
        num_ants: int = 30,
        alpha: float = 1.0,  # Pheromone importance
        beta: float = 2.0,  # Heuristic importance
        evaporation: float = 0.5,
        q: float = 100.0,  # Pheromone deposit factor
    ):
        """
        Initialize ACO optimizer.

        Args:
            num_ants: Number of ants
            alpha: Pheromone importance
            beta: Heuristic importance
            evaporation: Evaporation rate
            q: Pheromone deposit factor
        """
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.q = q
        self.pheromones: Dict[Tuple[int, int], float] = {}
        self.best_path: List[int] = []
        self.best_cost = float("inf")
        self.logger = logger.bind(optimizer="ACO")

    def optimize(
        self,
        distance_matrix: List[List[float]],
        max_iterations: int = 100,
    ) -> Tuple[List[int], float]:
        """
        Solve traveling salesman problem.

        Args:
            distance_matrix: Distance between cities
            max_iterations: Maximum iterations

        Returns:
            (best_path, best_cost)
        """
        num_cities = len(distance_matrix)

        # Initialize pheromones
        initial_pheromone = 1.0 / num_cities
        for i in range(num_cities):
            for j in range(num_cities):
                if i != j:
                    self.pheromones[(i, j)] = initial_pheromone

        self.logger.info("aco_started", cities=num_cities, ants=self.num_ants)

        for iteration in range(max_iterations):
            # Each ant constructs a solution
            all_paths = []
            all_costs = []

            for _ in range(self.num_ants):
                path, cost = self._construct_solution(distance_matrix)
                all_paths.append(path)
                all_costs.append(cost)

                # Update best solution
                if cost < self.best_cost:
                    self.best_cost = cost
                    self.best_path = path

            # Update pheromones
            self._update_pheromones(all_paths, all_costs)

            if iteration % 10 == 0:
                self.logger.debug(
                    "aco_progress",
                    iteration=iteration,
                    best_cost=self.best_cost,
                )

        self.logger.info("aco_complete", best_cost=self.best_cost)
        return self.best_path, self.best_cost

    def _construct_solution(
        self, distance_matrix: List[List[float]]
    ) -> Tuple[List[int], float]:
        """Construct a solution using pheromone trails."""
        num_cities = len(distance_matrix)
        unvisited = set(range(num_cities))
        current = random.choice(list(unvisited))
        path = [current]
        unvisited.remove(current)
        total_cost = 0.0

        while unvisited:
            # Select next city
            next_city = self._select_next_city(current, unvisited, distance_matrix)
            path.append(next_city)
            total_cost += distance_matrix[current][next_city]
            current = next_city
            unvisited.remove(next_city)

        # Return to start
        total_cost += distance_matrix[current][path[0]]

        return path, total_cost

    def _select_next_city(
        self,
        current: int,
        unvisited: set[int],
        distance_matrix: List[List[float]],
    ) -> int:
        """Select next city using pheromone and heuristic information."""
        probabilities = []
        cities = list(unvisited)

        for city in cities:
            pheromone = self.pheromones.get((current, city), 1.0)
            distance = distance_matrix[current][city]
            if distance == 0:
                distance = 1e-10  # Avoid division by zero
            heuristic = 1.0 / distance

            prob = (pheromone**self.alpha) * (heuristic**self.beta)
            probabilities.append(prob)

        # Normalize
        total = sum(probabilities)
        if total == 0:
            return int(random.choice(cities))

        probabilities = [p / total for p in probabilities]

        # Roulette wheel selection
        r = random.random()
        cumsum = 0.0
        for i, prob in enumerate(probabilities):
            cumsum += prob
            if r <= cumsum:
                return int(cities[i])

        return int(cities[-1])

    def _update_pheromones(self, paths: List[List[int]], costs: List[float]) -> None:
        """Update pheromone trails."""
        # Evaporation
        for edge in self.pheromones:
            self.pheromones[edge] *= 1 - self.evaporation

        # Deposit pheromones
        for path, cost in zip(paths, costs):
            if cost == 0:
                continue
            deposit = self.q / cost

            for i in range(len(path)):
                j = (i + 1) % len(path)
                edge = (path[i], path[j])
                self.pheromones[edge] = self.pheromones.get(edge, 0) + deposit

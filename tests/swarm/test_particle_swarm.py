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
Comprehensive tests for Particle Swarm Optimization - Phase 19.

Tests PSO implementation with scalability, convergence, and optimization quality.
"""

from typing import List

import pytest

from src.swarm.config import PSOConfig
from src.swarm.particle_swarm import ParticleSwarmOptimizer
from src.swarm.types import Particle


class TestPSOConfig:
    """Tests for PSOConfig validation."""

    def test_default_config(self) -> None:
        """Test default PSO configuration."""
        config = PSOConfig()

        assert config.num_particles == 100
        assert config.inertia == pytest.approx(0.7)
        assert config.cognitive_weight == pytest.approx(1.5)
        assert config.social_weight == pytest.approx(1.5)
        assert config.max_velocity == pytest.approx(1.0)
        assert config.dimension == 2
        assert config.max_iterations == 100
        assert config.use_gpu is False

    def test_custom_config(self) -> None:
        """Test custom PSO configuration."""
        config = PSOConfig(
            num_particles=200,
            inertia=0.9,
            cognitive_weight=2.0,
            social_weight=2.0,
            dimension=5,
        )

        assert config.num_particles == 200
        assert config.inertia == pytest.approx(0.9)
        assert config.cognitive_weight == pytest.approx(2.0)
        assert config.social_weight == pytest.approx(2.0)
        assert config.dimension == 5

    def test_invalid_num_particles(self) -> None:
        """Test validation for invalid number of particles."""
        with pytest.raises(ValueError, match="num_particles deve ser >= 1"):
            PSOConfig(num_particles=0)

    def test_invalid_inertia(self) -> None:
        """Test validation for invalid inertia."""
        with pytest.raises(ValueError, match="inertia deve estar em"):
            PSOConfig(inertia=0.0)

        with pytest.raises(ValueError, match="inertia deve estar em"):
            PSOConfig(inertia=1.5)

    def test_invalid_max_velocity(self) -> None:
        """Test validation for invalid max velocity."""
        with pytest.raises(ValueError, match="max_velocity deve ser > 0"):
            PSOConfig(max_velocity=0.0)


class TestParticle:
    """Tests for Particle dataclass."""

    def test_particle_initialization(self) -> None:
        """Test particle initialization."""
        particle = Particle(
            position=[1.0, 2.0],
            velocity=[0.1, 0.2],
        )

        assert particle.particle_id is not None
        assert isinstance(particle.particle_id, str)
        assert particle.position == [1.0, 2.0]
        assert particle.velocity == [0.1, 0.2]
        assert particle.best_fitness == float("inf")

    def test_particle_update_best(self) -> None:
        """Test particle updating personal best."""
        particle = Particle(
            position=[1.0, 2.0],
            velocity=[0.0, 0.0],
        )
        particle.best_fitness = 10.0
        particle.best_position = [0.0, 0.0]

        # Better fitness
        particle.fitness = 5.0
        particle.position = [1.5, 2.5]
        particle.update_best()

        assert particle.best_fitness == pytest.approx(5.0)
        assert particle.best_position == [1.5, 2.5]

    def test_particle_no_update_when_worse(self) -> None:
        """Test particle not updating when fitness is worse."""
        particle = Particle(
            position=[1.0, 2.0],
            velocity=[0.0, 0.0],
        )
        particle.best_fitness = 5.0
        particle.best_position = [1.0, 2.0]

        # Worse fitness
        particle.fitness = 10.0
        particle.position = [2.0, 3.0]
        particle.update_best()

        # Best should not change
        assert particle.best_fitness == pytest.approx(5.0)
        assert particle.best_position == [1.0, 2.0]


class TestParticleSwarmOptimizer:
    """Tests for ParticleSwarmOptimizer."""

    def test_initialization(self) -> None:
        """Test PSO initialization."""
        config = PSOConfig(num_particles=50, dimension=3)
        pso = ParticleSwarmOptimizer(config)

        assert len(pso.particles) == 50
        assert pso.config.dimension == 3
        assert len(pso.global_best_position) == 3
        assert pso.global_best_fitness == float("inf")
        assert pso.iteration == 0

    def test_particles_initialized_correctly(self) -> None:
        """Test that particles are properly initialized."""
        config = PSOConfig(num_particles=20, dimension=2)
        pso = ParticleSwarmOptimizer(config)

        for particle in pso.particles:
            assert len(particle.position) == 2
            assert len(particle.velocity) == 2
            assert len(particle.best_position) == 2

    def test_optimize_simple_quadratic(self) -> None:
        """Test PSO on simple quadratic function."""
        config = PSOConfig(num_particles=30, dimension=2, max_iterations=50)
        pso = ParticleSwarmOptimizer(config)

        # Minimize f(x, y) = x^2 + y^2 (minimum at origin)
        def quadratic(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        best_pos, best_fitness, metrics = pso.optimize(quadratic)

        # Should find near-optimal solution
        assert best_fitness < 1.0
        assert len(best_pos) == 2
        assert metrics.best_value == pytest.approx(best_fitness)
        assert metrics.execution_time > 0

    def test_optimize_sphere_function(self) -> None:
        """Test PSO on sphere function."""
        config = PSOConfig(num_particles=40, dimension=3, max_iterations=60)
        pso = ParticleSwarmOptimizer(config)

        def sphere(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        best_pos, best_fitness, _ = pso.optimize(sphere)

        assert best_fitness < 2.0
        assert len(best_pos) == 3

    def test_global_best_updates(self) -> None:
        """Test that global best is updated correctly."""
        config = PSOConfig(num_particles=10, dimension=1, max_iterations=10)
        pso = ParticleSwarmOptimizer(config)

        def simple_func(pos: List[float]) -> float:
            return (pos[0] - 5.0) ** 2

        initial_best = pso.global_best_fitness
        pso.optimize(simple_func)

        # Global best should improve
        assert pso.global_best_fitness < initial_best

    def test_convergence_detection(self) -> None:
        """Test convergence detection."""
        config = PSOConfig(
            num_particles=20,
            dimension=2,
            max_iterations=100,
            convergence_threshold=0.01,
        )
        pso = ParticleSwarmOptimizer(config)

        # Very simple function that converges quickly
        def easy_func(pos: List[float]) -> float:
            return sum(x**2 for x in pos) * 0.001

        _, _, metrics = pso.optimize(easy_func)

        # Should converge before max iterations
        assert metrics.iterations_to_convergence < config.max_iterations

    def test_get_swarm_state(self) -> None:
        """Test getting swarm state."""
        config = PSOConfig(num_particles=15, dimension=2)
        pso = ParticleSwarmOptimizer(config)

        state = pso.get_swarm_state()

        assert state.num_agents == 15
        assert state.iteration == 0
        assert state.best_fitness == float("inf")
        assert state.diversity >= 0

    def test_reset(self) -> None:
        """Test PSO reset."""
        config = PSOConfig(num_particles=20, dimension=2, max_iterations=10)
        pso = ParticleSwarmOptimizer(config)

        # Run optimization
        def dummy_func(pos: List[float]) -> float:
            return sum(pos)

        pso.optimize(dummy_func)

        # Reset
        pso.reset()

        # Verify reset
        assert pso.iteration == 0
        assert pso.global_best_fitness == float("inf")


class TestPSOIntegration:
    """Integration tests for PSO."""

    def test_100_particles_scalability(self) -> None:
        """Test PSO with 100 particles."""
        config = PSOConfig(num_particles=100, dimension=5, max_iterations=30)
        pso = ParticleSwarmOptimizer(config)

        def benchmark_func(pos: List[float]) -> float:
            return sum((x - 3.0) ** 2 for x in pos)

        _, best_fitness, metrics = pso.optimize(benchmark_func)

        assert best_fitness < 5.0
        assert metrics.execution_time < 10.0  # Should be reasonably fast

    def test_high_dimension_optimization(self) -> None:
        """Test PSO in high-dimensional space."""
        config = PSOConfig(num_particles=50, dimension=10, max_iterations=50)
        pso = ParticleSwarmOptimizer(config)

        def high_dim_func(pos: List[float]) -> float:
            return sum(x**2 for x in pos)

        best_pos, best_fitness, _ = pso.optimize(high_dim_func)

        assert len(best_pos) == 10
        assert best_fitness < 10.0  # Reasonable for 10D

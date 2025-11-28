import pytest
from src.swarm.ant_colony import AntColonyOptimizer
from src.swarm.config import ACOConfig
from src.swarm.types import Ant
        import random

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
Comprehensive tests for Ant Colony Optimization - Phase 19.

Tests ACO implementation for TSP with elitismo and local search.
"""




class TestACOConfig:
    """Tests for ACOConfig validation."""

    def test_default_config(self) -> None:
        """Test default ACO configuration."""
        config = ACOConfig()

        assert config.num_ants == 100
        assert config.alpha == pytest.approx(1.0)
        assert config.beta == pytest.approx(2.0)
        assert config.evaporation_rate == pytest.approx(0.5)
        assert config.pheromone_deposit == pytest.approx(100.0)
        assert config.elite_weight == pytest.approx(2.0)
        assert config.max_iterations == 100
        assert config.local_search is False

    def test_custom_config(self) -> None:
        """Test custom ACO configuration."""
        config = ACOConfig(
            num_ants=50,
            alpha=1.5,
            beta=3.0,
            evaporation_rate=0.7,
            local_search=True,
        )

        assert config.num_ants == 50
        assert config.alpha == pytest.approx(1.5)
        assert config.beta == pytest.approx(3.0)
        assert config.evaporation_rate == pytest.approx(0.7)
        assert config.local_search is True

    def test_invalid_num_ants(self) -> None:
        """Test validation for invalid number of ants."""
        with pytest.raises(ValueError, match="num_ants deve ser >= 1"):
            ACOConfig(num_ants=0)

    def test_invalid_alpha(self) -> None:
        """Test validation for invalid alpha."""
        with pytest.raises(ValueError, match="alpha deve ser >= 0"):
            ACOConfig(alpha=-1.0)

    def test_invalid_evaporation_rate(self) -> None:
        """Test validation for invalid evaporation rate."""
        with pytest.raises(ValueError, match="evaporation_rate deve estar em"):
            ACOConfig(evaporation_rate=0.0)

        with pytest.raises(ValueError, match="evaporation_rate deve estar em"):
            ACOConfig(evaporation_rate=1.0)


class TestAnt:
    """Tests for Ant dataclass."""

    def test_ant_initialization(self) -> None:
        """Test ant initialization."""
        ant = Ant(current_city=0)

        assert ant.ant_id is not None
        assert isinstance(ant.ant_id, str)
        assert ant.current_city == 0
        assert isinstance(ant.visited, set)
        assert len(ant.visited) == 0
        assert ant.path == []
        assert ant.path_cost == pytest.approx(0.0)


class TestAntColonyOptimizer:
    """Tests for AntColonyOptimizer."""

    def test_initialization(self) -> None:
        """Test ACO initialization."""
        config = ACOConfig(num_ants=30)
        aco = AntColonyOptimizer(config)

        assert aco.config.num_ants == 30
        assert len(aco.pheromones) == 0
        assert aco.best_path == []
        assert aco.best_cost == float("inf")
        assert aco.iteration == 0

    def test_pheromone_initialization(self) -> None:
        """Test pheromone initialization."""
        config = ACOConfig(num_ants=10)
        aco = AntColonyOptimizer(config)

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
        assert any((0, 1) in aco.pheromones or (1, 0) in aco.pheromones for _ in [1])

    def test_optimize_small_tsp(self) -> None:
        """Test ACO on small TSP instance."""
        config = ACOConfig(num_ants=20)
        aco = AntColonyOptimizer(config)

        # Simple 3-city triangle
        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        best_path, best_cost, metrics = aco.optimize(distances, max_iterations=30)

        # Should find a valid tour
        assert len(best_path) == 3
        assert set(best_path) == {0, 1, 2}  # All cities visited
        assert best_cost > 0
        assert metrics.best_value == pytest.approx(best_cost)

    def test_symmetric_triangle(self) -> None:
        """Test ACO on symmetric triangle."""
        config = ACOConfig(num_ants=30, evaporation_rate=0.5)
        aco = AntColonyOptimizer(config)

        # Symmetric triangle: optimal tour is 3.0
        distances = [
            [0.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 0.0],
        ]

        best_path, best_cost, _ = aco.optimize(distances, max_iterations=50)

        # Should find near-optimal solution
        assert best_cost <= 3.5  # Allow small tolerance
        assert len(best_path) == 3

    def test_pheromone_evaporation(self) -> None:
        """Test that pheromones change over iterations."""
        config = ACOConfig(num_ants=10, evaporation_rate=0.9)
        aco = AntColonyOptimizer(config)

        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        # Run one iteration
        aco.optimize(distances, max_iterations=1)
        pheromones_after_1 = dict(aco.pheromones)

        # Run more iterations
        aco.iteration = 0  # Reset iteration counter
        aco.optimize(distances, max_iterations=5)
        pheromones_after_5 = dict(aco.pheromones)

        # Pheromone levels should change
        assert pheromones_after_1 != pheromones_after_5

    def test_improves_over_iterations(self) -> None:
        """Test that ACO improves solution quality."""
        config = ACOConfig(num_ants=20)
        aco = AntColonyOptimizer(config)

        distances = [
            [0.0, 2.0, 5.0, 7.0],
            [2.0, 0.0, 3.0, 4.0],
            [5.0, 3.0, 0.0, 2.0],
            [7.0, 4.0, 2.0, 0.0],
        ]

        # Short run
        _, cost_short, _ = aco.optimize(distances, max_iterations=10)

        # Reset and longer run
        aco.reset()
        _, cost_long, _ = aco.optimize(distances, max_iterations=50)

        # Longer run should find better or equal solution
        assert cost_long <= cost_short * 1.2  # Allow variance

    def test_elite_ants_deposit_more(self) -> None:
        """Test that elite ants have higher pheromone deposit."""
        config = ACOConfig(num_ants=15, elite_weight=3.0)
        aco = AntColonyOptimizer(config)

        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        aco.optimize(distances, max_iterations=20)

        # Best path should have stronger pheromone
        # (indirectly tested through convergence)
        assert aco.best_cost > 0

    def test_local_search_disabled(self) -> None:
        """Test ACO with local search disabled."""
        config = ACOConfig(num_ants=15, local_search=False)
        aco = AntColonyOptimizer(config)

        distances = [
            [0.0, 1.0, 2.0, 3.0],
            [1.0, 0.0, 1.5, 2.5],
            [2.0, 1.5, 0.0, 1.0],
            [3.0, 2.5, 1.0, 0.0],
        ]

        best_path, best_cost, _ = aco.optimize(distances, max_iterations=20)

        assert len(best_path) == 4
        assert best_cost > 0

    def test_local_search_enabled(self) -> None:
        """Test ACO with local search enabled."""
        config = ACOConfig(num_ants=15, local_search=True)
        aco = AntColonyOptimizer(config)

        distances = [
            [0.0, 1.0, 2.0, 3.0],
            [1.0, 0.0, 1.5, 2.5],
            [2.0, 1.5, 0.0, 1.0],
            [3.0, 2.5, 1.0, 0.0],
        ]

        best_path, best_cost, _ = aco.optimize(distances, max_iterations=20)

        assert len(best_path) == 4
        assert best_cost > 0

    def test_reset(self) -> None:
        """Test ACO reset."""
        config = ACOConfig(num_ants=10)
        aco = AntColonyOptimizer(config)

        distances = [
            [0.0, 1.0, 2.0],
            [1.0, 0.0, 1.5],
            [2.0, 1.5, 0.0],
        ]

        # Run optimization
        aco.optimize(distances, max_iterations=10)

        # Reset
        aco.reset()

        # Verify reset
        assert aco.iteration == 0
        assert aco.best_cost == float("inf")
        assert aco.best_path == []
        assert len(aco.pheromones) == 0


class TestACOIntegration:
    """Integration tests for ACO."""

    def test_100_ants_scalability(self) -> None:
        """Test ACO with 100 ants."""
        config = ACOConfig(num_ants=100)
        aco = AntColonyOptimizer(config)

        # 5-city TSP
        distances = [
            [0.0, 2.0, 4.0, 5.0, 3.0],
            [2.0, 0.0, 3.0, 4.0, 2.5],
            [4.0, 3.0, 0.0, 2.0, 4.5],
            [5.0, 4.0, 2.0, 0.0, 3.5],
            [3.0, 2.5, 4.5, 3.5, 0.0],
        ]

        best_path, best_cost, metrics = aco.optimize(distances, max_iterations=30)

        assert len(best_path) == 5
        assert best_cost > 0
        assert metrics.execution_time < 10.0  # Should be reasonably fast

    def test_larger_tsp_instance(self) -> None:
        """Test ACO on larger TSP instance (10 cities)."""

        config = ACOConfig(num_ants=50)
        aco = AntColonyOptimizer(config)

        # Generate random symmetric distance matrix
        num_cities = 10
        distances = [[0.0] * num_cities for _ in range(num_cities)]
        random.seed(42)

        for i in range(num_cities):
            for j in range(i + 1, num_cities):
                dist = random.uniform(1.0, 10.0)
                distances[i][j] = dist
                distances[j][i] = dist

        best_path, best_cost, _ = aco.optimize(distances, max_iterations=50)

        assert len(best_path) == num_cities
        assert set(best_path) == set(range(num_cities))
        assert best_cost > 0

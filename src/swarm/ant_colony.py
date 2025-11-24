"""
Ant Colony Optimization (ACO) avançado - Phase 19.

Implementação escalável de ACO para 100-1000 formigas com estratégias
de elitismo e otimização de evaporação de feromônio.

Author: OmniMind Project - Phase 19
License: MIT
"""

import random
import time
from typing import Dict, List, Optional, Tuple
import logging

from src.swarm.types import Ant, SwarmMetrics
from src.swarm.config import ACOConfig

logger = logging.getLogger(__name__)


class AntColonyOptimizer:
    """
    Otimizador ACO escalável para 100-1000 formigas.

    Features:
    - Elitismo (melhores formigas depositam mais feromônio)
    - Evaporação de feromônio eficiente
    - Suporte a busca local opcional
    - Otimizado para TSP e problemas de roteamento
    """

    def __init__(self, config: Optional[ACOConfig] = None):
        """
        Inicializa otimizador ACO.

        Args:
            config: Configuração ACO (usa padrão se None)
        """
        self.config = config or ACOConfig()
        self.ants: List[Ant] = []
        self.pheromones: Dict[Tuple[int, int], float] = {}
        self.best_path: List[int] = []
        self.best_cost = float("inf")
        self.iteration = 0

        logger.info(f"ACO initialized: {self.config.num_ants} ants")

    def optimize(
        self,
        distance_matrix: List[List[float]],
        max_iterations: Optional[int] = None,
    ) -> Tuple[List[int], float, SwarmMetrics]:
        """
        Resolve problema de TSP usando ACO.

        Args:
            distance_matrix: Matriz de distâncias entre cidades
            max_iterations: Número máximo de iterações (usa config se None)

        Returns:
            Tupla (melhor_caminho, melhor_custo, métricas)
        """
        start_time = time.time()
        num_cities = len(distance_matrix)
        max_iter = max_iterations or self.config.max_iterations

        # Inicializa feromônios
        self._initialize_pheromones(num_cities)

        logger.info(
            f"Starting ACO optimization: {num_cities} cities, " f"{max_iter} iterations"
        )

        for iteration in range(max_iter):
            self.iteration = iteration

            # Cada formiga constrói uma solução
            all_paths = []
            all_costs = []

            for ant_idx in range(self.config.num_ants):
                path, cost = self._construct_solution(distance_matrix)
                all_paths.append(path)
                all_costs.append(cost)

                # Atualiza melhor solução
                if cost < self.best_cost:
                    self.best_cost = cost
                    self.best_path = path
                    logger.debug(
                        f"New best found at iteration {iteration}: " f"cost={cost:.2f}"
                    )

            # Atualiza feromônios
            self._update_pheromones(all_paths, all_costs)

            # Busca local opcional
            if self.config.local_search and iteration % 10 == 0:
                self._apply_local_search(distance_matrix)

            if iteration % 20 == 0:
                logger.debug(f"Iteration {iteration}: best_cost={self.best_cost:.2f}")

        execution_time = time.time() - start_time

        # Calcula métricas finais
        metrics = SwarmMetrics(
            iterations_to_convergence=self.iteration,
            best_solution=[float(city) for city in self.best_path],
            best_value=self.best_cost,
            execution_time=execution_time,
            memory_usage=0.0,  # TODO: implementar
            gpu_utilized=self.config.use_gpu,
        )

        logger.info(
            f"ACO completed: best_cost={self.best_cost:.2f}, "
            f"iterations={self.iteration}, time={execution_time:.2f}s"
        )

        return self.best_path, self.best_cost, metrics

    def _initialize_pheromones(self, num_cities: int) -> None:
        """
        Inicializa trilhas de feromônio.

        Args:
            num_cities: Número de cidades
        """
        initial_pheromone = 1.0 / num_cities
        self.pheromones = {}

        for i in range(num_cities):
            for j in range(num_cities):
                if i != j:
                    self.pheromones[(i, j)] = initial_pheromone

    def _construct_solution(
        self, distance_matrix: List[List[float]]
    ) -> Tuple[List[int], float]:
        """
        Constrói uma solução (tour) usando trilhas de feromônio.

        Args:
            distance_matrix: Matriz de distâncias

        Returns:
            Tupla (caminho, custo)
        """
        num_cities = len(distance_matrix)
        unvisited = set(range(num_cities))
        current = random.choice(list(unvisited))
        path = [current]
        unvisited.remove(current)
        total_cost = 0.0

        while unvisited:
            # Seleciona próxima cidade
            next_city = self._select_next_city(current, unvisited, distance_matrix)
            path.append(next_city)
            total_cost += distance_matrix[current][next_city]
            current = next_city
            unvisited.remove(next_city)

        # Retorna ao início
        total_cost += distance_matrix[current][path[0]]

        return path, total_cost

    def _select_next_city(
        self,
        current: int,
        unvisited: set,
        distance_matrix: List[List[float]],
    ) -> int:
        """
        Seleciona próxima cidade usando feromônio e informação heurística.

        Args:
            current: Cidade atual
            unvisited: Cidades não visitadas
            distance_matrix: Matriz de distâncias

        Returns:
            Próxima cidade selecionada
        """
        probabilities = []
        cities = list(unvisited)

        for city in cities:
            pheromone = self.pheromones.get((current, city), 1.0)
            distance = distance_matrix[current][city]

            # Evita divisão por zero
            if distance == 0:
                distance = 1e-10

            heuristic = 1.0 / distance

            # Probabilidade = feromônio^alpha * heurística^beta
            prob = (pheromone**self.config.alpha) * (heuristic**self.config.beta)
            probabilities.append(prob)

        # Normaliza probabilidades
        total = sum(probabilities)
        if total == 0:
            return random.choice(cities)

        probabilities = [p / total for p in probabilities]

        # Seleção por roleta
        r = random.random()
        cumsum = 0.0
        for i, prob in enumerate(probabilities):
            cumsum += prob
            if r <= cumsum:
                return cities[i]

        return cities[-1]

    def _update_pheromones(self, paths: List[List[int]], costs: List[float]) -> None:
        """
        Atualiza trilhas de feromônio com evaporação e deposição.

        Args:
            paths: Caminhos construídos pelas formigas
            costs: Custos dos caminhos
        """
        # Evaporação
        for edge in self.pheromones:
            self.pheromones[edge] *= 1 - self.config.evaporation_rate

        # Deposição de feromônio
        for path, cost in zip(paths, costs):
            if cost == 0:
                continue

            deposit = self.config.pheromone_deposit / cost

            for i in range(len(path)):
                j = (i + 1) % len(path)
                edge = (path[i], path[j])
                self.pheromones[edge] = self.pheromones.get(edge, 0) + deposit

        # Elitismo: melhor formiga deposita feromônio extra
        if self.best_path:
            elite_deposit = (
                self.config.elite_weight
                * self.config.pheromone_deposit
                / self.best_cost
            )
            for i in range(len(self.best_path)):
                j = (i + 1) % len(self.best_path)
                edge = (self.best_path[i], self.best_path[j])
                self.pheromones[edge] = self.pheromones.get(edge, 0) + elite_deposit

    def _apply_local_search(self, distance_matrix: List[List[float]]) -> None:
        """
        Aplica busca local 2-opt na melhor solução.

        Args:
            distance_matrix: Matriz de distâncias
        """
        if not self.best_path or len(self.best_path) < 4:
            return

        improved = True
        while improved:
            improved = False
            for i in range(1, len(self.best_path) - 2):
                for j in range(i + 1, len(self.best_path)):
                    # Tenta 2-opt swap
                    new_path = self.best_path.copy()
                    new_path[i:j] = reversed(new_path[i:j])

                    # Calcula novo custo
                    new_cost = 0.0
                    for k in range(len(new_path)):
                        next_k = (k + 1) % len(new_path)
                        new_cost += distance_matrix[new_path[k]][new_path[next_k]]

                    if new_cost < self.best_cost:
                        self.best_path = new_path
                        self.best_cost = new_cost
                        improved = True
                        break
                if improved:
                    break

    def reset(self) -> None:
        """Reinicia o otimizador."""
        self.iteration = 0
        self.best_cost = float("inf")
        self.best_path = []
        self.pheromones = {}
        logger.info("ACO reset")

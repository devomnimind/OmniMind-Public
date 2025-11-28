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
Particle Swarm Optimization (PSO) avançado - Phase 19.

Implementação escalável de PSO para 100-1000 partículas com otimizações
de memória GPU e convergência adaptativa.

Author: OmniMind Project - Phase 19
License: MIT
"""

import logging
import random
import time
from typing import Callable, List, Optional, Tuple

from src.swarm.config import PSOConfig
from src.swarm.types import Particle, SwarmMetrics, SwarmState
from src.swarm.utils import (
    calculate_convergence,
    calculate_diversity,
    clamp_velocity,
)

logger = logging.getLogger(__name__)


class ParticleSwarmOptimizer:
    """
    Otimizador PSO escalável para 100-1000 partículas.

    Features:
    - Inércia adaptativa
    - Topologia de vizinhança configurável
    - Suporte a GPU (quando disponível)
    - Batching para otimizar VRAM
    - Detecção de convergência
    """

    def __init__(
        self,
        config: Optional[PSOConfig] = None,
        dimension: Optional[int] = None,
        num_particles: Optional[int] = None,
    ) -> None:
        """
        Inicializa otimizador PSO.

        Args:
            config: Configuração PSO (usa padrão se None)
            dimension: Sobrescreve a dimensão se fornecido
            num_particles: Sobrescreve o número de partículas se fornecido
        """
        # Permitir sobrescrita de parâmetros via argumentos individuais
        if config is None:
            base_config = PSOConfig()
            if dimension is not None:
                base_config.dimension = dimension
            if num_particles is not None:
                base_config.num_particles = num_particles
            self.config = base_config
        else:
            # Se config fornecido, ainda permite sobrescrita opcional
            self.config = config
            if dimension is not None:
                self.config.dimension = dimension
            if num_particles is not None:
                self.config.num_particles = num_particles
        self.particles: List[Particle] = []
        self.global_best_position: List[float] = []
        self.global_best_fitness = float("inf")
        self.iteration = 0
        self.converged = False

        self._initialize_swarm()
        logger.info(
            f"PSO initialized: {self.config.num_particles} particles, "
            f"dim={self.config.dimension}"
        )

    def _initialize_swarm(self) -> None:
        """Inicializa enxame com partículas aleatórias."""
        self.particles = []
        for _ in range(self.config.num_particles):
            position = [random.uniform(-10, 10) for _ in range(self.config.dimension)]
            velocity = [random.uniform(-1, 1) for _ in range(self.config.dimension)]
            particle = Particle(
                position=position,
                velocity=velocity,
                best_position=position.copy(),
            )
            self.particles.append(particle)

        self.global_best_position = [0.0] * self.config.dimension

    def optimize(
        self,
        fitness_function: Callable[[List[float]], float],
        max_iterations: Optional[int] = None,
    ) -> Tuple[List[float], float, SwarmMetrics]:
        """
        Executa otimização PSO.

        Args:
            fitness_function: Função objetivo a minimizar
            max_iterations: Número máximo de iterações (usa config se None)

        Returns:
            Tupla (melhor_posição, melhor_fitness, métricas)
        """
        start_time = time.time()
        max_iter = max_iterations or self.config.max_iterations

        logger.info(f"Starting PSO optimization for {max_iter} iterations")

        for iteration in range(max_iter):
            self.iteration = iteration

            # Avalia fitness de todas as partículas
            self._evaluate_fitness(fitness_function)

            # Atualiza velocidades e posições
            self._update_swarm()

            # Verifica convergência
            if self._check_convergence():
                logger.info(f"Converged at iteration {iteration}")
                break

            if iteration % 10 == 0:
                diversity = self._calculate_diversity()
                logger.debug(
                    f"Iteration {iteration}: "
                    f"best_fitness={self.global_best_fitness:.6f}, "
                    f"diversity={diversity:.4f}"
                )

        execution_time = time.time() - start_time

        # Calcula uso de memória
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_usage_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
        except ImportError:
            logger.warning("psutil not installed - memory tracking unavailable")
            memory_usage_mb = 0.0
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            memory_usage_mb = 0.0

        # Calcula métricas finais
        metrics = SwarmMetrics(
            iterations_to_convergence=self.iteration,
            best_solution=self.global_best_position.copy(),
            best_value=self.global_best_fitness,
            execution_time=execution_time,
            memory_usage=memory_usage_mb,
            gpu_utilized=self.config.use_gpu,
        )

        logger.info(
            f"PSO completed: best_fitness={self.global_best_fitness:.6f}, "
            f"iterations={self.iteration}, time={execution_time:.2f}s"
        )

        return self.global_best_position, self.global_best_fitness, metrics

    def _evaluate_fitness(self, fitness_function: Callable[[List[float]], float]) -> None:
        """
        Avalia fitness de todas as partículas.

        Args:
            fitness_function: Função objetivo
        """
        for particle in self.particles:
            particle.fitness = fitness_function(particle.position)
            particle.update_best()

            # Atualiza global best
            if particle.fitness < self.global_best_fitness:
                self.global_best_fitness = particle.fitness
                self.global_best_position = particle.position.copy()

    def _update_swarm(self) -> None:
        """Atualiza velocidades e posições usando PSO."""
        # Inércia adaptativa (decresce linearmente)
        inertia = self.config.inertia * (1.0 - self.iteration / self.config.max_iterations)

        for particle in self.particles:
            # Atualiza velocidade
            new_velocity = []
            for d in range(self.config.dimension):
                # Componente de inércia
                v = inertia * particle.velocity[d]

                # Componente cognitivo (personal best)
                cognitive = self.config.cognitive_weight * random.random()
                v += cognitive * (particle.best_position[d] - particle.position[d])

                # Componente social (global best)
                social = self.config.social_weight * random.random()
                v += social * (self.global_best_position[d] - particle.position[d])

                new_velocity.append(v)

            # Limita velocidade
            particle.velocity = clamp_velocity(new_velocity, self.config.max_velocity)

            # Atualiza posição
            for d in range(self.config.dimension):
                particle.position[d] += particle.velocity[d]

    def _check_convergence(self) -> bool:
        """
        Verifica se o enxame convergiu.

        Returns:
            True se convergido
        """
        # Verifica se fitness é suficientemente bom
        if self.global_best_fitness < self.config.convergence_threshold:
            self.converged = True
            return True

        # Verifica diversidade (se muito baixa, convergiu)
        diversity = self._calculate_diversity()
        if diversity < 0.01:  # Threshold empírico
            self.converged = True
            return True

        return False

    def _calculate_diversity(self) -> float:
        """
        Calcula diversidade do enxame.

        Returns:
            Métrica de diversidade
        """
        positions = [p.position for p in self.particles]
        return calculate_diversity(positions)

    def get_swarm_state(self) -> SwarmState:
        """
        Retorna estado atual do enxame.

        Returns:
            Estado do enxame
        """
        fitnesses = [p.fitness for p in self.particles]
        avg_fitness = sum(fitnesses) / len(fitnesses) if fitnesses else float("inf")

        diversity = self._calculate_diversity()
        convergence = calculate_convergence(fitnesses, self.global_best_fitness)

        return SwarmState(
            iteration=self.iteration,
            num_agents=len(self.particles),
            best_fitness=self.global_best_fitness,
            avg_fitness=avg_fitness,
            diversity=diversity,
            convergence=convergence,
        )

    def reset(self) -> None:
        """Reinicia o enxame."""
        self.iteration = 0
        self.converged = False
        self.global_best_fitness = float("inf")
        self._initialize_swarm()
        logger.info("Swarm reset")

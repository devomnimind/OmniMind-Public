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
Gerenciador de Enxame - Phase 19.

Orquestra execução de PSO, ACO e detecção de emergência,
coordenando até 1000 agentes com otimização de recursos.

Author: OmniMind Project - Phase 19
License: MIT
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.swarm.ant_colony import AntColonyOptimizer
from src.swarm.config import SwarmConfig
from src.swarm.emergence_detector import EmergenceDetector
from src.swarm.particle_swarm import ParticleSwarmOptimizer
from src.swarm.types import SwarmMetrics, SwarmState
from src.swarm.utils import estimate_memory_usage

logger = logging.getLogger(__name__)


class SwarmManager:
    """
    Gerenciador centralizado de inteligência de enxame.

    Features:
    - Orquestra PSO, ACO e detecção de emergência
    - Gerencia recursos (memória, VRAM)
    - Batching automático para GPU
    - Métricas de performance em tempo real
    - Suporte a 100-1000 agentes
    """

    def __init__(self, config: Optional[SwarmConfig] = None):
        """
        Inicializa gerenciador de enxame.

        Args:
            config: Configuração global (usa padrão se None)
        """
        self.config = config or SwarmConfig()
        self.pso: Optional[ParticleSwarmOptimizer] = None
        self.aco: Optional[AntColonyOptimizer] = None
        self.emergence_detector = EmergenceDetector(self.config.emergence)
        self.metrics_history: List[Dict[str, Any]] = []

        logger.info(
            f"SwarmManager initialized: "
            f"max_agents={self.config.max_agents}, "
            f"memory_limit={self.config.memory_limit_mb}MB"
        )

    def optimize_continuous(
        self,
        fitness_function: Callable[[List[float]], float],
        dimension: int,
        num_particles: int = 100,
        max_iterations: int = 100,
    ) -> Tuple[List[float], float, SwarmMetrics]:
        """
        Otimização contínua usando PSO.

        Args:
            fitness_function: Função objetivo a minimizar
            dimension: Dimensionalidade do espaço
            num_particles: Número de partículas (100-1000)
            max_iterations: Número máximo de iterações

        Returns:
            Tupla (melhor_solução, melhor_valor, métricas)

        Raises:
            ValueError: Se parâmetros inválidos ou exceder limites de recursos
        """
        # Valida número de agentes
        if num_particles > self.config.max_agents:
            raise ValueError(
                f"num_particles ({num_particles}) excede " f"max_agents ({self.config.max_agents})"
            )

        # Estima uso de memória
        estimated_memory = estimate_memory_usage(num_particles, dimension)
        if estimated_memory > self.config.memory_limit_mb:
            logger.warning(
                f"Estimated memory ({estimated_memory:.1f}MB) exceeds limit "
                f"({self.config.memory_limit_mb}MB)"
            )

        # Configura PSO
        pso_config = self.config.pso
        if pso_config:
            pso_config.num_particles = num_particles
            pso_config.dimension = dimension
            pso_config.max_iterations = max_iterations

        self.pso = ParticleSwarmOptimizer(pso_config)

        logger.info(
            f"Starting PSO optimization: {num_particles} particles, "
            f"dim={dimension}, max_iter={max_iterations}"
        )

        # Executa otimização
        solution, value, metrics = self.pso.optimize(fitness_function)

        # Detecta padrões emergentes
        self._detect_emergence_pso()

        # Armazena métricas
        self._record_metrics("PSO", metrics)

        return solution, value, metrics

    def optimize_combinatorial(
        self,
        distance_matrix: List[List[float]],
        num_ants: int = 100,
        max_iterations: int = 100,
    ) -> Tuple[List[int], float, SwarmMetrics]:
        """
        Otimização combinatorial usando ACO (TSP).

        Args:
            distance_matrix: Matriz de distâncias entre cidades
            num_ants: Número de formigas (100-1000)
            max_iterations: Número máximo de iterações

        Returns:
            Tupla (melhor_caminho, melhor_custo, métricas)

        Raises:
            ValueError: Se parâmetros inválidos ou exceder limites de recursos
        """
        # Valida número de agentes
        if num_ants > self.config.max_agents:
            raise ValueError(
                f"num_ants ({num_ants}) excede " f"max_agents ({self.config.max_agents})"
            )

        num_cities = len(distance_matrix)

        # Estima uso de memória (conservativo)
        estimated_memory = estimate_memory_usage(num_ants, num_cities)
        if estimated_memory > self.config.memory_limit_mb:
            logger.warning(
                f"Estimated memory ({estimated_memory:.1f}MB) exceeds limit "
                f"({self.config.memory_limit_mb}MB)"
            )

        # Configura ACO
        aco_config = self.config.aco
        if aco_config:
            aco_config.num_ants = num_ants
            aco_config.max_iterations = max_iterations

        self.aco = AntColonyOptimizer(aco_config)

        logger.info(
            f"Starting ACO optimization: {num_ants} ants, "
            f"{num_cities} cities, max_iter={max_iterations}"
        )

        # Executa otimização
        path, cost, metrics = self.aco.optimize(distance_matrix)

        # Armazena métricas
        self._record_metrics("ACO", metrics)

        return path, cost, metrics

    def _detect_emergence_pso(self) -> None:
        """Detecta padrões emergentes em PSO."""
        if not self.pso or not self.pso.particles:
            return

        # Converte partículas para formato de estados
        agent_states = [
            {
                "id": p.particle_id,
                "position": p.position,
                "velocity": p.velocity,
                "fitness": p.fitness,
            }
            for p in self.pso.particles
        ]

        # Detecta padrões
        patterns = self.emergence_detector.detect_patterns(agent_states)

        if patterns:
            logger.info(f"Detected {len(patterns)} emergent patterns in PSO")
            for pattern in patterns:
                logger.debug(
                    f"  - {pattern.pattern_type.value}: "
                    f"confidence={pattern.confidence:.2f}, "
                    f"participants={len(pattern.participants)}"
                )

    def _record_metrics(self, algorithm: str, metrics: SwarmMetrics) -> None:
        """
        Registra métricas de execução.

        Args:
            algorithm: Nome do algoritmo
            metrics: Métricas de execução
        """
        record = {
            "timestamp": time.time(),
            "algorithm": algorithm,
            "iterations": metrics.iterations_to_convergence,
            "best_value": metrics.best_value,
            "execution_time": metrics.execution_time,
            "memory_usage": metrics.memory_usage,
            "gpu_utilized": metrics.gpu_utilized,
        }
        self.metrics_history.append(record)

    def get_swarm_state(self) -> Optional[SwarmState]:
        """
        Retorna estado atual do enxame ativo.

        Returns:
            Estado do enxame ou None se nenhum ativo
        """
        if self.pso and self.pso.particles:
            state = self.pso.get_swarm_state()
            # Adiciona padrões emergentes
            state.emergent_patterns = self.emergence_detector.detected_patterns[-5:]
            return state

        return None

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo de métricas de todas as execuções.

        Returns:
            Dicionário com estatísticas
        """
        if not self.metrics_history:
            return {"total_runs": 0}

        pso_runs = [m for m in self.metrics_history if m["algorithm"] == "PSO"]
        aco_runs = [m for m in self.metrics_history if m["algorithm"] == "ACO"]

        summary = {
            "total_runs": len(self.metrics_history),
            "pso_runs": len(pso_runs),
            "aco_runs": len(aco_runs),
        }

        if pso_runs:
            summary["pso"] = {
                "avg_iterations": sum(r["iterations"] for r in pso_runs) / len(pso_runs),
                "avg_time": sum(r["execution_time"] for r in pso_runs) / len(pso_runs),
                "best_value": min(r["best_value"] for r in pso_runs),
            }

        if aco_runs:
            summary["aco"] = {
                "avg_iterations": sum(r["iterations"] for r in aco_runs) / len(aco_runs),
                "avg_time": sum(r["execution_time"] for r in aco_runs) / len(aco_runs),
                "best_value": min(r["best_value"] for r in aco_runs),
            }

        # Adiciona resumo de emergência
        summary["emergence"] = self.emergence_detector.get_pattern_summary()

        return summary

    def reset(self) -> None:
        """Reinicia todos os componentes."""
        if self.pso:
            self.pso.reset()
        if self.aco:
            self.aco.reset()
        self.emergence_detector.clear_history()
        self.metrics_history = []
        logger.info("SwarmManager reset")

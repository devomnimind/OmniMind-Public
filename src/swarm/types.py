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
Tipos de dados para módulo de Swarm Intelligence - Phase 19.

Define TypedDict e dataclasses para representação de agentes,
partículas, formigas e padrões emergentes no sistema de enxame.

Author: OmniMind Project - Phase 19
License: MIT
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List


class SwarmAlgorithm(Enum):
    """Algoritmos de swarm disponíveis."""

    PSO = "particle_swarm_optimization"
    ACO = "ant_colony_optimization"
    HYBRID = "hybrid_swarm"


class EmergenceType(Enum):
    """Tipos de padrões emergentes detectáveis."""

    CLUSTERING = "clustering"  # Agentes formam grupos
    SYNCHRONIZATION = "synchronization"  # Comportamento coordenado
    SPECIALIZATION = "specialization"  # Diferenciação de papéis
    HIERARCHY = "hierarchy"  # Emergência de liderança
    PHASE_TRANSITION = "phase_transition"  # Mudança de regime
    SELF_ORGANIZATION = "self_organization"  # Auto-organização


@dataclass
class Particle:
    """
    Representa uma partícula em PSO.

    Attributes:
        particle_id: Identificador único da partícula
        position: Posição atual no espaço de busca
        velocity: Velocidade atual
        best_position: Melhor posição pessoal encontrada
        best_fitness: Melhor fitness pessoal
        fitness: Fitness atual
        neighbors: IDs de partículas vizinhas
    """

    particle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: List[float] = field(default_factory=list)
    velocity: List[float] = field(default_factory=list)
    best_position: List[float] = field(default_factory=list)
    best_fitness: float = float("inf")
    fitness: float = float("inf")
    neighbors: List[str] = field(default_factory=list)

    def update_best(self) -> None:
        """Atualiza melhor posição pessoal se fitness melhorar."""
        if self.fitness < self.best_fitness:
            self.best_fitness = self.fitness
            self.best_position = self.position.copy()


@dataclass
class Ant:
    """
    Representa uma formiga em ACO.

    Attributes:
        ant_id: Identificador único da formiga
        current_city: Cidade atual
        visited: Conjunto de cidades visitadas
        path: Caminho percorrido
        path_cost: Custo total do caminho
    """

    ant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_city: int = 0
    visited: set = field(default_factory=set)
    path: List[int] = field(default_factory=list)
    path_cost: float = 0.0


@dataclass
class EmergentPattern:
    """
    Padrão emergente detectado no enxame.

    Attributes:
        pattern_type: Tipo de padrão emergente
        confidence: Confiança na detecção (0-1)
        participants: IDs dos agentes participantes
        metrics: Métricas do padrão
        timestamp: Timestamp da detecção
    """

    pattern_type: EmergenceType
    confidence: float
    participants: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class SwarmState:
    """
    Estado global do enxame.

    Attributes:
        iteration: Iteração atual
        num_agents: Número de agentes
        best_fitness: Melhor fitness global
        avg_fitness: Fitness médio
        diversity: Diversidade do enxame
        convergence: Métrica de convergência
        emergent_patterns: Padrões emergentes detectados
    """

    iteration: int = 0
    num_agents: int = 0
    best_fitness: float = float("inf")
    avg_fitness: float = float("inf")
    diversity: float = 0.0
    convergence: float = 0.0
    emergent_patterns: List[EmergentPattern] = field(default_factory=list)


@dataclass
class SwarmMetrics:
    """
    Métricas de desempenho do enxame.

    Attributes:
        iterations_to_convergence: Iterações até convergir
        best_solution: Melhor solução encontrada
        best_value: Valor da melhor solução
        execution_time: Tempo de execução (segundos)
        memory_usage: Uso de memória (MB)
        gpu_utilized: Se GPU foi utilizada
    """

    iterations_to_convergence: int = 0
    best_solution: List[float] = field(default_factory=list)
    best_value: float = float("inf")
    execution_time: float = 0.0
    memory_usage: float = 0.0
    gpu_utilized: bool = False

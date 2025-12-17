"""
Configuração para módulo de Swarm Intelligence - Phase 19.

Define parâmetros de configuração para PSO, ACO e detecção de emergência,
otimizados para escalabilidade de 100-1000 agentes com restrições de hardware.

Author: OmniMind Project - Phase 19
License: MIT
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PSOConfig:
    """
    Configuração para Particle Swarm Optimization.

    Attributes:
        num_particles: Número de partículas (100-1000)
        inertia: Peso de inércia (0.4-0.9)
        cognitive_weight: Peso cognitivo (pessoal best) (1.0-2.0)
        social_weight: Peso social (global best) (1.0-2.0)
        max_velocity: Velocidade máxima
        dimension: Dimensionalidade do espaço de busca
        max_iterations: Número máximo de iterações
        convergence_threshold: Threshold para convergência
        use_gpu: Se deve utilizar GPU (quando disponível)
        batch_size: Tamanho de batch para GPU (limitar VRAM)
    """

    num_particles: int = 100
    inertia: float = 0.7
    cognitive_weight: float = 1.5
    social_weight: float = 1.5
    max_velocity: float = 1.0
    dimension: int = 2
    max_iterations: int = 100
    convergence_threshold: float = 1e-6
    use_gpu: bool = False
    batch_size: int = 50  # Para 4GB VRAM

    def __post_init__(self) -> None:
        """Validação de parâmetros."""
        if self.num_particles < 1:
            raise ValueError("num_particles deve ser >= 1")
        if not 0 < self.inertia <= 1:
            raise ValueError("inertia deve estar em (0, 1]")
        if self.cognitive_weight < 0:
            raise ValueError("cognitive_weight deve ser >= 0")
        if self.social_weight < 0:
            raise ValueError("social_weight deve ser >= 0")
        if self.max_velocity <= 0:
            raise ValueError("max_velocity deve ser > 0")
        if self.dimension < 1:
            raise ValueError("dimension deve ser >= 1")
        if self.max_iterations < 1:
            raise ValueError("max_iterations deve ser >= 1")


@dataclass
class ACOConfig:
    """
    Configuração para Ant Colony Optimization.

    Attributes:
        num_ants: Número de formigas (100-1000)
        alpha: Importância do feromônio (0.5-5.0)
        beta: Importância da heurística (1.0-5.0)
        evaporation_rate: Taxa de evaporação (0.1-0.9)
        pheromone_deposit: Fator de depósito de feromônio
        elite_weight: Peso da melhor formiga
        max_iterations: Número máximo de iterações
        local_search: Se deve aplicar busca local
        use_gpu: Se deve utilizar GPU
    """

    num_ants: int = 100
    alpha: float = 1.0
    beta: float = 2.0
    evaporation_rate: float = 0.5
    pheromone_deposit: float = 100.0
    elite_weight: float = 2.0
    max_iterations: int = 100
    local_search: bool = False
    use_gpu: bool = False

    def __post_init__(self) -> None:
        """Validação de parâmetros."""
        if self.num_ants < 1:
            raise ValueError("num_ants deve ser >= 1")
        if self.alpha < 0:
            raise ValueError("alpha deve ser >= 0")
        if self.beta < 0:
            raise ValueError("beta deve ser >= 0")
        if not 0 < self.evaporation_rate < 1:
            raise ValueError("evaporation_rate deve estar em (0, 1)")
        if self.pheromone_deposit <= 0:
            raise ValueError("pheromone_deposit deve ser > 0")
        if self.max_iterations < 1:
            raise ValueError("max_iterations deve ser >= 1")


@dataclass
class EmergenceConfig:
    """
    Configuração para detecção de emergência.

    Attributes:
        detection_interval: Intervalo de iterações para detecção
        clustering_threshold: Threshold para detecção de clustering
        sync_threshold: Threshold para sincronização
        min_pattern_size: Tamanho mínimo de padrão (num agentes)
        confidence_threshold: Confiança mínima para reportar padrão
    """

    detection_interval: int = 10
    clustering_threshold: float = 0.7
    sync_threshold: float = 0.8
    min_pattern_size: int = 5
    confidence_threshold: float = 0.6

    def __post_init__(self) -> None:
        """Validação de parâmetros."""
        if self.detection_interval < 1:
            raise ValueError("detection_interval deve ser >= 1")
        if not 0 < self.clustering_threshold <= 1:
            raise ValueError("clustering_threshold deve estar em (0, 1]")
        if not 0 < self.sync_threshold <= 1:
            raise ValueError("sync_threshold deve estar em (0, 1]")
        if self.min_pattern_size < 1:
            raise ValueError("min_pattern_size deve ser >= 1")
        if not 0 < self.confidence_threshold <= 1:
            raise ValueError("confidence_threshold deve estar em (0, 1]")


@dataclass
class SwarmConfig:
    """
    Configuração global do sistema de enxame.

    Attributes:
        pso: Configuração PSO
        aco: Configuração ACO
        emergence: Configuração de detecção de emergência
        max_agents: Limite máximo de agentes simultâneos
        memory_limit_mb: Limite de memória (MB)
        vram_limit_mb: Limite de VRAM (MB) - 4GB GTX 1650
    """

    pso: Optional[PSOConfig] = None
    aco: Optional[ACOConfig] = None
    emergence: Optional[EmergenceConfig] = None
    max_agents: int = 1000
    memory_limit_mb: float = 2000.0  # Conservativo para 24GB RAM
    vram_limit_mb: float = 3800.0  # ~3.8GB de 4GB disponível

    def __post_init__(self) -> None:
        """Inicialização de configs padrão."""
        if self.pso is None:
            self.pso = PSOConfig()
        if self.aco is None:
            self.aco = ACOConfig()
        if self.emergence is None:
            self.emergence = EmergenceConfig()

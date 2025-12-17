"""
Swarm Intelligence Module - Phase 19: Distributed Collective Intelligence.

Implementação avançada de algoritmos de enxame (PSO, ACO) com suporte para
100-1000 agentes, detecção de padrões emergentes e otimização de recursos.

Features:
- Particle Swarm Optimization (PSO) escalável
- Ant Colony Optimization (ACO) com elitismo
- Detecção de padrões emergentes (clustering, sincronização, especialização)
- Gerenciamento centralizado de recursos
- Otimizado para hardware limitado (4GB VRAM)

Author: OmniMind Project - Phase 19
License: MIT
"""

from src.swarm.ant_colony import AntColonyOptimizer
from src.swarm.collective_learning import (
    CollectiveLearner,
    ConsensusLearning,
    FederatedLearning,
    KnowledgeBase,
    MultiAgentTrainer,
    SharedExperience,
)
from src.swarm.config import (
    ACOConfig,
    EmergenceConfig,
    PSOConfig,
    SwarmConfig,
)
from src.swarm.distributed_solver import (
    ConsensusProtocol,
    DistributedProblem,
    DistributedSolution,
    DistributedSolver,
    SolutionAggregator,
    TaskDecomposer,
)
from src.swarm.emergence_detector import EmergenceDetector
from src.swarm.particle_swarm import ParticleSwarmOptimizer
from src.swarm.swarm_manager import SwarmManager
from src.swarm.types import (
    Ant,
    EmergenceType,
    EmergentPattern,
    Particle,
    SwarmAlgorithm,
    SwarmMetrics,
    SwarmState,
)
from src.swarm.utils import (
    calculate_convergence,
    calculate_diversity,
    clamp_velocity,
    detect_clustering,
    estimate_memory_usage,
    euclidean_distance,
    find_k_nearest_neighbors,
    manhattan_distance,
)

__all__ = [
    # Types
    "SwarmAlgorithm",
    "EmergenceType",
    "Particle",
    "Ant",
    "EmergentPattern",
    "SwarmState",
    "SwarmMetrics",
    # Config
    "PSOConfig",
    "ACOConfig",
    "EmergenceConfig",
    "SwarmConfig",
    # Core Classes
    "ParticleSwarmOptimizer",
    "AntColonyOptimizer",
    "EmergenceDetector",
    "SwarmManager",
    # Utils
    "euclidean_distance",
    "manhattan_distance",
    "find_k_nearest_neighbors",
    "calculate_diversity",
    "calculate_convergence",
    "clamp_velocity",
    "detect_clustering",
    "estimate_memory_usage",
    # Distributed Solving (Migrated)
    "DistributedProblem",
    "DistributedSolution",
    "DistributedSolver",
    "ConsensusProtocol",
    "TaskDecomposer",
    "SolutionAggregator",
    # Collective Learning (Migrated)
    "CollectiveLearner",
    "KnowledgeBase",
    "SharedExperience",
    "ConsensusLearning",
    "FederatedLearning",
    "MultiAgentTrainer",
]

__version__ = "1.0.0"
__phase__ = "Phase 19"

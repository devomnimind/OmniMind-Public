"""
Collective Intelligence Module for OmniMind - Phase 14 Implementation.

This module provides multi-agent coordination and collective intelligence:
- Swarm intelligence algorithms
- Distributed problem solving
- Emergent behavior patterns
- Collective learning systems

All components designed for autonomous multi-agent collaboration.
"""

from src.collective_intelligence.swarm_intelligence import (
    SwarmAgent,
    SwarmCoordinator,
    SwarmBehavior,
    SwarmConfiguration,
    ParticleSwarmOptimizer,
    AntColonyOptimizer,
)

from src.collective_intelligence.distributed_solver import (
    DistributedProblem,
    DistributedSolution,
    DistributedSolver,
    ConsensusProtocol,
    TaskDecomposer,
    SolutionAggregator,
)

from src.collective_intelligence.emergent_behaviors import (
    EmergentPattern,
    BehaviorRule,
    EmergenceDetector,
    PatternType,
    SelfOrganization,
    AdaptiveSystem,
)

from src.collective_intelligence.collective_learning import (
    CollectiveLearner,
    KnowledgeBase,
    SharedExperience,
    ConsensusLearning,
    FederatedLearning,
    MultiAgentTrainer,
)

__all__ = [
    # Swarm Intelligence
    "SwarmAgent",
    "SwarmCoordinator",
    "SwarmBehavior",
    "SwarmConfiguration",
    "ParticleSwarmOptimizer",
    "AntColonyOptimizer",
    # Distributed Solving
    "DistributedProblem",
    "DistributedSolution",
    "DistributedSolver",
    "ConsensusProtocol",
    "TaskDecomposer",
    "SolutionAggregator",
    # Emergent Behaviors
    "EmergentPattern",
    "BehaviorRule",
    "EmergenceDetector",
    "PatternType",
    "SelfOrganization",
    "AdaptiveSystem",
    # Collective Learning
    "CollectiveLearner",
    "KnowledgeBase",
    "SharedExperience",
    "ConsensusLearning",
    "FederatedLearning",
    "MultiAgentTrainer",
]

__version__ = "1.0.0"

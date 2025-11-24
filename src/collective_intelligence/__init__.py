"""
Collective Intelligence Module (LEGACY).

.. warning::
    This module is DEPRECATED and will be removed in future versions.
    Please use `src.swarm` (Phase 19) for Swarm Intelligence capabilities.

Provides distributed problem-solving capabilities through swarm intelligence
and emergent behavior analysis.
"""

import warnings

# Issue deprecation warning
warnings.warn(
    "src.collective_intelligence is deprecated. Use src.swarm instead.",
    DeprecationWarning,
    stacklevel=2,
)

# flake8: noqa: E402 (imports intentionally after warning)
from src.collective_intelligence.swarm_intelligence import (  # noqa: E402
    SwarmAgent,
    SwarmCoordinator,
    SwarmBehavior,
    SwarmConfiguration,
    ParticleSwarmOptimizer,
    AntColonyOptimizer,
)

from src.collective_intelligence.distributed_solver import (  # noqa: E402
    DistributedProblem,
    DistributedSolution,
    DistributedSolver,
    ConsensusProtocol,
    TaskDecomposer,
    SolutionAggregator,
)

from src.collective_intelligence.emergent_behaviors import (  # noqa: E402
    EmergentPattern,
    BehaviorRule,
    EmergenceDetector,
    PatternType,
    SelfOrganization,
    AdaptiveSystem,
)

from src.collective_intelligence.collective_learning import (  # noqa: E402
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

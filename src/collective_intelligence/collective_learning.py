"""
Collective Learning for Multi-Agent Systems.

Implements shared learning mechanisms where multiple agents
contribute to and benefit from collective knowledge.

Author: OmniMind Project
License: MIT
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SharedExperience:
    """Experience shared among agents."""

    experience_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    action: str = ""
    outcome: float = 0.0
    timestamp: float = field(default_factory=time.time)
    confidence: float = 0.5


@dataclass
class KnowledgeBase:
    """Shared knowledge base for collective learning."""

    facts: Dict[str, Any] = field(default_factory=dict)
    experiences: List[SharedExperience] = field(default_factory=list)
    patterns: Dict[str, List[Any]] = field(default_factory=dict)
    version: int = 0

    def add_experience(self, exp: SharedExperience) -> None:
        """Add experience to knowledge base."""
        self.experiences.append(exp)
        self.version += 1

    def add_fact(self, key: str, value: Any) -> None:
        """Add or update a fact."""
        self.facts[key] = value
        self.version += 1

    def get_experiences(
        self, agent_id: Optional[str] = None, limit: int = 100
    ) -> List[SharedExperience]:
        """Get experiences, optionally filtered by agent."""
        if agent_id:
            experiences = [exp for exp in self.experiences if exp.agent_id == agent_id]
        else:
            experiences = self.experiences

        return experiences[-limit:]  # Most recent


class ConsensusLearning:
    """
    Learn collectively through consensus mechanisms.

    Features:
    - Aggregated model updates
    - Voting on knowledge
    - Collaborative refinement
    """

    def __init__(self, num_agents: int = 5):
        """
        Initialize consensus learning.

        Args:
            num_agents: Number of participating agents
        """
        self.num_agents = num_agents
        self.knowledge_base = KnowledgeBase()
        self.agent_models: Dict[str, Dict[str, Any]] = {}
        self.logger = logger.bind(
            component="consensus_learning",
            num_agents=num_agents,
        )

    def share_experience(self, agent_id: str, experience: SharedExperience) -> None:
        """
        Share an experience from an agent.

        Args:
            agent_id: Agent sharing the experience
            experience: Experience to share
        """
        experience.agent_id = agent_id
        self.knowledge_base.add_experience(experience)

        self.logger.info(
            "experience_shared",
            agent_id=agent_id,
            outcome=experience.outcome,
        )

    def get_consensus_model(self) -> Dict[str, Any]:
        """
        Get consensus model by aggregating agent models.

        Returns:
            Aggregated consensus model
        """
        if not self.agent_models:
            return {}

        # Simple averaging of model parameters
        consensus = {}
        all_keys = set()
        for model in self.agent_models.values():
            all_keys.update(model.keys())

        for key in all_keys:
            values = [
                model.get(key, 0)
                for model in self.agent_models.values()
                if key in model
            ]
            if values:
                # Average numerical values
                if all(isinstance(v, (int, float)) for v in values):
                    consensus[key] = sum(values) / len(values)
                else:
                    # Use most common for non-numerical
                    from collections import Counter

                    counter = Counter(values)
                    consensus[key] = counter.most_common(1)[0][0]

        return consensus

    def update_agent_model(self, agent_id: str, model: Dict[str, Any]) -> None:
        """
        Update an agent's model contribution.

        Args:
            agent_id: Agent identifier
            model: Agent's model parameters
        """
        self.agent_models[agent_id] = model
        self.logger.debug("agent_model_updated", agent_id=agent_id)


class FederatedLearning:
    """
    Federated learning for privacy-preserving collective learning.

    Features:
    - Local training, global aggregation
    - Privacy preservation
    - Decentralized updates
    """

    def __init__(self, num_agents: int = 5, aggregation_rounds: int = 10):
        """
        Initialize federated learning.

        Args:
            num_agents: Number of participating agents
            aggregation_rounds: Number of aggregation rounds
        """
        self.num_agents = num_agents
        self.aggregation_rounds = aggregation_rounds
        self.global_model: Dict[str, Any] = {}
        self.local_models: Dict[str, Dict[str, Any]] = {}
        self.current_round = 0
        self.logger = logger.bind(
            component="federated_learning",
            num_agents=num_agents,
        )

    def initialize_global_model(self, model: Dict[str, Any]) -> None:
        """Initialize the global model."""
        self.global_model = model.copy()
        self.logger.info("global_model_initialized")

    def get_global_model(self) -> Dict[str, Any]:
        """Get current global model."""
        return self.global_model.copy()

    def submit_local_update(self, agent_id: str, local_model: Dict[str, Any]) -> None:
        """
        Submit local model update from an agent.

        Args:
            agent_id: Agent identifier
            local_model: Locally trained model
        """
        self.local_models[agent_id] = local_model
        self.logger.debug("local_update_received", agent_id=agent_id)

    def aggregate_updates(self) -> Dict[str, Any]:
        """
        Aggregate local updates into global model.

        Returns:
            Updated global model
        """
        if not self.local_models:
            return self.global_model

        # Federated averaging
        aggregated = {}
        all_keys = set()
        for model in self.local_models.values():
            all_keys.update(model.keys())

        for key in all_keys:
            values = [
                model.get(key, self.global_model.get(key, 0))
                for model in self.local_models.values()
            ]

            if all(isinstance(v, (int, float)) for v in values):
                aggregated[key] = sum(values) / len(values)
            else:
                # Keep global model value for non-numerical
                aggregated[key] = self.global_model.get(key)

        self.global_model = aggregated
        self.current_round += 1
        self.local_models.clear()  # Clear for next round

        self.logger.info(
            "updates_aggregated",
            round=self.current_round,
            num_updates=len(self.local_models),
        )

        return self.global_model


class CollectiveLearner:
    """
    High-level collective learning coordinator.

    Features:
    - Multiple learning strategies
    - Knowledge base management
    - Performance tracking
    """

    def __init__(
        self,
        num_agents: int = 5,
        use_federated: bool = False,
    ):
        """
        Initialize collective learner.

        Args:
            num_agents: Number of agents
            use_federated: Use federated learning if True
        """
        self.num_agents = num_agents
        self.use_federated = use_federated

        if use_federated:
            self.learner = FederatedLearning(num_agents)
        else:
            self.learner = ConsensusLearning(num_agents)

        self.logger = logger.bind(
            component="collective_learner",
            mode="federated" if use_federated else "consensus",
        )

    def learn_from_experience(
        self,
        agent_id: str,
        experience: SharedExperience,
    ) -> None:
        """
        Learn from an agent's experience.

        Args:
            agent_id: Agent identifier
            experience: Shared experience
        """
        if isinstance(self.learner, ConsensusLearning):
            self.learner.share_experience(agent_id, experience)
        else:
            # In federated learning, experiences inform local training
            self.logger.debug(
                "experience_recorded",
                agent_id=agent_id,
                outcome=experience.outcome,
            )

    def update_model(self, agent_id: str, model_update: Dict[str, Any]) -> None:
        """
        Update model from an agent.

        Args:
            agent_id: Agent identifier
            model_update: Model parameters or updates
        """
        if isinstance(self.learner, ConsensusLearning):
            self.learner.update_agent_model(agent_id, model_update)
        else:
            self.learner.submit_local_update(agent_id, model_update)

    def get_collective_model(self) -> Dict[str, Any]:
        """Get the current collective model."""
        if isinstance(self.learner, ConsensusLearning):
            return self.learner.get_consensus_model()
        else:
            return self.learner.get_global_model()

    def synchronize(self) -> Dict[str, Any]:
        """
        Synchronize collective knowledge.

        Returns:
            Updated collective model
        """
        if isinstance(self.learner, FederatedLearning):
            return self.learner.aggregate_updates()
        else:
            return self.get_collective_model()


class MultiAgentTrainer:
    """
    Trains multiple agents collectively.

    Features:
    - Parallel training
    - Experience sharing
    - Coordinated learning
    """

    def __init__(self, num_agents: int = 5):
        """Initialize multi-agent trainer."""
        self.num_agents = num_agents
        self.collective_learner = CollectiveLearner(num_agents)
        self.training_episodes = 0
        self.logger = logger.bind(component="multi_agent_trainer")

    def train_episode(
        self,
        agent_experiences: List[SharedExperience],
    ) -> Dict[str, Any]:
        """
        Train on an episode of experiences.

        Args:
            agent_experiences: Experiences from all agents

        Returns:
            Training metrics
        """
        # Share all experiences
        for exp in agent_experiences:
            self.collective_learner.learn_from_experience(exp.agent_id, exp)

        # Synchronize collective knowledge
        model = self.collective_learner.synchronize()

        self.training_episodes += 1

        metrics = {
            "episode": self.training_episodes,
            "num_experiences": len(agent_experiences),
            "avg_outcome": (
                sum(e.outcome for e in agent_experiences) / len(agent_experiences)
                if agent_experiences
                else 0
            ),
            "model_version": self.training_episodes,
        }

        self.logger.info(
            "episode_trained",
            episode=self.training_episodes,
            num_experiences=len(agent_experiences),
        )

        return metrics

    def get_metrics(self) -> Dict[str, Any]:
        """Get training metrics."""
        return {
            "num_agents": self.num_agents,
            "training_episodes": self.training_episodes,
        }

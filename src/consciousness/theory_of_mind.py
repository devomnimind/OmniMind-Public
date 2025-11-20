"""Theory of Mind Implementation (Phase 11.1).

Implements mental state attribution capabilities for AI consciousness:
- Intent prediction from observed actions
- Belief tracking and state modeling
- Mental state reasoning
- Integration with metacognition system
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class MentalState(Enum):
    """Possible mental states that can be attributed."""

    CURIOUS = "curious"
    FOCUSED = "focused"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    EXPLORING = "exploring"
    PROBLEM_SOLVING = "problem_solving"
    LEARNING = "learning"


class Intent(Enum):
    """Possible intents inferred from actions."""

    GATHER_INFORMATION = "gather_information"
    SOLVE_PROBLEM = "solve_problem"
    LEARN_SKILL = "learn_skill"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    EXPLORE_OPTIONS = "explore_options"
    EXECUTE_TASK = "execute_task"
    ANALYZE_DATA = "analyze_data"
    COMMUNICATE = "communicate"


@dataclass
class Belief:
    """Represents a belief held by an agent or entity.

    Attributes:
        subject: What the belief is about
        proposition: The believed statement
        confidence: Confidence level (0.0-1.0)
        evidence: Supporting evidence for the belief
        timestamp: When the belief was formed
    """

    subject: str
    proposition: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate belief attributes."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class MentalStateModel:
    """Model of an entity's mental state.

    Attributes:
        entity_id: Identifier of the entity
        current_state: Current attributed mental state
        beliefs: List of beliefs attributed to the entity
        intents: List of inferred intents
        confidence: Overall confidence in the model (0.0-1.0)
        last_updated: When the model was last updated
    """

    entity_id: str
    current_state: MentalState
    beliefs: List[Belief] = field(default_factory=list)
    intents: List[Intent] = field(default_factory=list)
    confidence: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate mental state model."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


class TheoryOfMind:
    """Theory of Mind engine for mental state attribution.

    This class implements capabilities for:
    1. Intent prediction from observed actions
    2. Belief tracking and modeling
    3. Mental state attribution
    4. Reasoning about other agents' mental states
    """

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        max_beliefs_per_entity: int = 20,
    ) -> None:
        """Initialize Theory of Mind engine.

        Args:
            confidence_threshold: Minimum confidence for state attribution
            max_beliefs_per_entity: Maximum beliefs to track per entity
        """
        self.confidence_threshold = confidence_threshold
        self.max_beliefs_per_entity = max_beliefs_per_entity

        # Internal state
        self._mental_models: Dict[str, MentalStateModel] = {}
        self._action_history: Dict[str, List[Dict[str, Any]]] = {}

        logger.info(
            "theory_of_mind_initialized",
            confidence_threshold=confidence_threshold,
            max_beliefs=max_beliefs_per_entity,
        )

    def observe_action(
        self,
        entity_id: str,
        action_type: str,
        action_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Observe an action performed by an entity.

        Args:
            entity_id: Identifier of the entity
            action_type: Type of action performed
            action_data: Data about the action
            context: Optional context information
        """
        # Initialize tracking for new entities
        if entity_id not in self._action_history:
            self._action_history[entity_id] = []

        # Record action
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "action_data": action_data,
            "context": context or {},
        }
        self._action_history[entity_id].append(action_record)

        # Keep only recent history (last 100 actions)
        if len(self._action_history[entity_id]) > 100:
            self._action_history[entity_id] = self._action_history[entity_id][-100:]

        logger.debug(
            "action_observed",
            entity_id=entity_id,
            action_type=action_type,
        )

    def infer_intent(
        self,
        entity_id: str,
        recent_actions: Optional[int] = 5,
    ) -> List[Intent]:
        """Infer intent from recent actions.

        Args:
            entity_id: Identifier of the entity
            recent_actions: Number of recent actions to consider

        Returns:
            List of inferred intents with confidence scores
        """
        if entity_id not in self._action_history:
            logger.warning("no_action_history", entity_id=entity_id)
            return []

        # Get recent actions
        actions = self._action_history[entity_id][-recent_actions:]

        # Analyze action patterns
        intents: List[Intent] = []

        # Check for information gathering patterns
        info_actions = ["read", "search", "query", "analyze"]
        if any(action.get("action_type") in info_actions for action in actions):
            intents.append(Intent.GATHER_INFORMATION)

        # Check for problem-solving patterns
        problem_actions = ["debug", "fix", "optimize", "refactor"]
        if any(action.get("action_type") in problem_actions for action in actions):
            intents.append(Intent.SOLVE_PROBLEM)

        # Check for learning patterns
        learning_actions = ["learn", "study", "practice", "experiment"]
        if any(action.get("action_type") in learning_actions for action in actions):
            intents.append(Intent.LEARN_SKILL)

        # Check for execution patterns
        execution_actions = ["execute", "run", "deploy", "commit"]
        if any(action.get("action_type") in execution_actions for action in actions):
            intents.append(Intent.EXECUTE_TASK)

        # Check for exploration patterns
        exploration_actions = ["explore", "test", "try", "experiment"]
        if any(action.get("action_type") in exploration_actions for action in actions):
            intents.append(Intent.EXPLORE_OPTIONS)

        logger.debug(
            "intent_inferred",
            entity_id=entity_id,
            intents=[i.value for i in intents],
        )

        return intents

    def attribute_mental_state(
        self,
        entity_id: str,
    ) -> MentalState:
        """Attribute a mental state to an entity based on recent actions.

        Args:
            entity_id: Identifier of the entity

        Returns:
            Attributed mental state
        """
        if entity_id not in self._action_history:
            # Default state for unknown entities
            return MentalState.UNCERTAIN

        # Get recent actions
        recent_actions = self._action_history[entity_id][-10:]

        # Analyze action patterns to infer mental state
        action_types = [a.get("action_type") for a in recent_actions]

        # Check for focused behavior (repeated similar actions)
        if len(set(action_types)) <= 2 and len(action_types) >= 5:
            return MentalState.FOCUSED

        # Check for exploratory behavior (diverse actions)
        if len(set(action_types)) >= 7:
            return MentalState.EXPLORING

        # Check for problem-solving behavior
        if any(at in ["debug", "fix", "analyze", "optimize"] for at in action_types):
            return MentalState.PROBLEM_SOLVING

        # Check for learning behavior
        if any(at in ["learn", "study", "practice"] for at in action_types):
            return MentalState.LEARNING

        # Check for curious behavior (many queries/searches)
        if action_types.count("search") >= 3 or action_types.count("query") >= 3:
            return MentalState.CURIOUS

        # Default to uncertain if patterns unclear
        return MentalState.UNCERTAIN

    def update_belief(
        self,
        entity_id: str,
        subject: str,
        proposition: str,
        confidence: float,
        evidence: Optional[List[str]] = None,
    ) -> None:
        """Update a belief attributed to an entity.

        Args:
            entity_id: Identifier of the entity
            subject: What the belief is about
            proposition: The believed statement
            confidence: Confidence in the belief (0.0-1.0)
            evidence: Supporting evidence
        """
        # Initialize mental model if needed
        if entity_id not in self._mental_models:
            self._mental_models[entity_id] = MentalStateModel(
                entity_id=entity_id,
                current_state=MentalState.UNCERTAIN,
            )

        # Create new belief
        belief = Belief(
            subject=subject,
            proposition=proposition,
            confidence=confidence,
            evidence=evidence or [],
        )

        # Add to mental model
        model = self._mental_models[entity_id]

        # Check for existing belief on same subject
        existing_idx = None
        for idx, b in enumerate(model.beliefs):
            if b.subject == subject and b.proposition == proposition:
                existing_idx = idx
                break

        if existing_idx is not None:
            # Update existing belief
            model.beliefs[existing_idx] = belief
        else:
            # Add new belief
            model.beliefs.append(belief)

        # Limit number of beliefs
        if len(model.beliefs) > self.max_beliefs_per_entity:
            # Remove oldest beliefs
            model.beliefs = sorted(
                model.beliefs,
                key=lambda b: b.timestamp,
                reverse=True,
            )[: self.max_beliefs_per_entity]

        logger.debug(
            "belief_updated",
            entity_id=entity_id,
            subject=subject,
            confidence=confidence,
        )

    def get_mental_model(self, entity_id: str) -> Optional[MentalStateModel]:
        """Get the current mental model for an entity.

        Args:
            entity_id: Identifier of the entity

        Returns:
            Mental state model if available, None otherwise
        """
        # Update model before returning
        if entity_id in self._action_history:
            current_state = self.attribute_mental_state(entity_id)
            intents = self.infer_intent(entity_id)

            # Calculate overall confidence based on action history
            action_count = len(self._action_history[entity_id])
            confidence = min(0.9, 0.3 + (action_count / 100.0))

            if entity_id not in self._mental_models:
                self._mental_models[entity_id] = MentalStateModel(
                    entity_id=entity_id,
                    current_state=current_state,
                    intents=intents,
                    confidence=confidence,
                )
            else:
                model = self._mental_models[entity_id]
                model.current_state = current_state
                model.intents = intents
                model.confidence = confidence
                model.last_updated = datetime.now()

        return self._mental_models.get(entity_id)

    def predict_next_action(
        self,
        entity_id: str,
        num_predictions: int = 3,
    ) -> List[Dict[str, Any]]:
        """Predict likely next actions based on mental model.

        Args:
            entity_id: Identifier of the entity
            num_predictions: Number of predictions to return

        Returns:
            List of predicted actions with confidence scores
        """
        model = self.get_mental_model(entity_id)
        if not model:
            return []

        predictions: List[Dict[str, Any]] = []

        # Base predictions on current mental state
        if model.current_state == MentalState.FOCUSED:
            # Likely to continue similar actions
            if entity_id in self._action_history:
                recent = self._action_history[entity_id][-5:]
                if recent:
                    most_common = max(
                        set(a.get("action_type") for a in recent),
                        key=lambda x: sum(
                            1 for a in recent if a.get("action_type") == x
                        ),
                    )
                    predictions.append(
                        {
                            "action_type": most_common,
                            "confidence": 0.8,
                            "reasoning": "Continuing focused behavior",
                        }
                    )

        elif model.current_state == MentalState.EXPLORING:
            # Likely to try new actions
            predictions.append(
                {
                    "action_type": "explore",
                    "confidence": 0.7,
                    "reasoning": "Exploratory mental state",
                }
            )

        elif model.current_state == MentalState.PROBLEM_SOLVING:
            # Likely to analyze or debug
            predictions.extend(
                [
                    {
                        "action_type": "analyze",
                        "confidence": 0.75,
                        "reasoning": "Problem-solving mental state",
                    },
                    {
                        "action_type": "debug",
                        "confidence": 0.7,
                        "reasoning": "Problem-solving mental state",
                    },
                ]
            )

        # Base predictions on intents
        for intent in model.intents:
            if intent == Intent.GATHER_INFORMATION:
                predictions.append(
                    {
                        "action_type": "search",
                        "confidence": 0.65,
                        "reasoning": f"Intent: {intent.value}",
                    }
                )
            elif intent == Intent.SOLVE_PROBLEM:
                predictions.append(
                    {
                        "action_type": "fix",
                        "confidence": 0.7,
                        "reasoning": f"Intent: {intent.value}",
                    }
                )

        # Return top predictions by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions[:num_predictions]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about Theory of Mind operations.

        Returns:
            Statistics dictionary
        """
        total_entities = len(self._mental_models)
        total_actions = sum(len(actions) for actions in self._action_history.values())
        total_beliefs = sum(
            len(model.beliefs) for model in self._mental_models.values()
        )

        # Calculate average confidence
        avg_confidence = 0.0
        if total_entities > 0:
            avg_confidence = (
                sum(model.confidence for model in self._mental_models.values())
                / total_entities
            )

        return {
            "total_entities_tracked": total_entities,
            "total_actions_observed": total_actions,
            "total_beliefs": total_beliefs,
            "average_model_confidence": avg_confidence,
            "timestamp": datetime.now().isoformat(),
        }

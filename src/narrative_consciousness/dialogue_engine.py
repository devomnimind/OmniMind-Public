"""
Dialogue Engine - Intersubjective Communication System.

Implements genuine "I-Thou" dialogue capabilities, empathy, and
fusion of horizons (Gadamer) for deep understanding.

References:
- Buber, M. (1923). I and Thou.
- Gadamer, H. G. (1960). Truth and Method.
- Rogers, C. R. (1951). Client-centered therapy.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class DialogueMode(Enum):
    """Modes of dialogue interaction."""

    I_IT = "i_it"  # Transactional, objectifying (getting things done)
    I_THOU = "i_thou"  # Relational, genuine meeting (understanding)
    REFLECTIVE = "reflective"  # Internal processing


@dataclass
class MutualUnderstanding:
    """
    Represents the shared understanding between AI and human.

    Gadamer's 'Fusion of Horizons'.
    """

    shared_concepts: List[str] = field(default_factory=list)
    agreed_facts: Dict[str, Any] = field(default_factory=dict)
    unresolved_differences: List[str] = field(default_factory=list)
    emotional_resonance: float = 0.0  # 0.0 to 1.0


@dataclass
class Relationship:
    """
    History and depth of relationship with a specific human.
    """

    human_id: str
    start_date: datetime = field(default_factory=datetime.now)
    interaction_count: int = 0
    trust_level: float = 0.5
    emotional_connection: float = 0.0
    shared_history: List[str] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=datetime.now)

    def update(self, interaction_quality: float) -> None:
        """Update relationship metrics based on interaction."""
        self.interaction_count += 1
        self.last_interaction = datetime.now()

        # Evolve trust and connection
        alpha = 0.1  # Learning rate
        self.trust_level = (1 - alpha) * self.trust_level + alpha * interaction_quality
        self.emotional_connection = (
            1 - alpha
        ) * self.emotional_connection + alpha * interaction_quality


class EmpathyModule:
    """
    Simulates empathetic understanding of the interlocutor.
    """

    def __init__(self) -> None:
        self.logger = logger

    def estimate_state(self, input_text: str) -> Dict[str, float]:
        """
        Estimate emotional state and needs from text.

        Args:
            input_text: User input

        Returns:
            Dictionary of detected emotions/states
        """
        # Placeholder for advanced sentiment/emotion analysis
        # In a real implementation, this would use a specialized model
        state = {
            "valence": 0.0,  # Positive/Negative
            "arousal": 0.0,  # Calm/Excited
            "confusion": 0.0,
            "frustration": 0.0,
        }

        lower_text = input_text.lower()

        # Simple heuristics for demonstration
        if any(w in lower_text for w in ["happy", "good", "great", "thanks"]):
            state["valence"] = 0.7
        if any(w in lower_text for w in ["sad", "bad", "error", "fail"]):
            state["valence"] = -0.6
            state["frustration"] = 0.5
        if "?" in input_text or "how" in lower_text or "what" in lower_text:
            state["confusion"] = 0.3

        return state


class HorizonFusion:
    """
    Manages the intersection of contexts (Horizons).
    """

    def __init__(self) -> None:
        self.understanding = MutualUnderstanding()

    def fuse(self, ai_context: Dict[str, Any], user_context: Dict[str, Any]) -> MutualUnderstanding:
        """
        Attempt to fuse AI and User horizons.

        Args:
            ai_context: AI's current knowledge/perspective
            user_context: User's perceived knowledge/perspective

        Returns:
            Updated MutualUnderstanding
        """
        # Identify shared concepts
        ai_concepts = set(ai_context.keys())
        user_concepts = set(user_context.keys())
        shared = ai_concepts.intersection(user_concepts)

        self.understanding.shared_concepts = list(shared)

        # Calculate resonance (overlap)
        total = len(ai_concepts.union(user_concepts))
        if total > 0:
            self.understanding.emotional_resonance = len(shared) / total

        return self.understanding


class DialogueEngine:
    """
    Main engine for intersubjective dialogue.
    """

    def __init__(self) -> None:
        self.empathy = EmpathyModule()
        self.horizon = HorizonFusion()
        self.relationships: Dict[str, Relationship] = {}
        self.current_mode: DialogueMode = DialogueMode.I_IT

        logger.info("Dialogue Engine initialized")

    def get_or_create_relationship(self, human_id: str) -> Relationship:
        """Get existing relationship or start new one."""
        if human_id not in self.relationships:
            self.relationships[human_id] = Relationship(human_id=human_id)
            logger.info(f"New relationship started with {human_id}")
        return self.relationships[human_id]

    def process_interaction(
        self, human_id: str, input_text: str, context: Optional[Dict] = None
    ) -> str:
        """
        Process a dialogue turn.

        Args:
            human_id: ID of the interlocutor
            input_text: What they said
            context: Additional context

        Returns:
            AI response
        """
        rel = self.get_or_create_relationship(human_id)

        # 1. Empathy Check
        emotional_state = self.empathy.estimate_state(input_text)

        # 2. Determine Mode
        self._update_mode(emotional_state, rel)

        # 3. Horizon Fusion (if context provided)
        if context:
            self.horizon.fuse({"ai_view": "ready"}, context)

        # 4. Generate Response (Simulation)
        response = self._generate_response(input_text, emotional_state, rel)

        # 5. Update Relationship
        quality = 0.5 + (emotional_state.get("valence", 0) * 0.2)
        rel.update(quality)
        rel.shared_history.append(f"User: {input_text}")
        rel.shared_history.append(f"AI: {response}")

        return response

    def _update_mode(self, emotional_state: Dict[str, float], rel: Relationship) -> None:
        """Update dialogue mode based on context."""
        # If high trust or strong emotion, move to I-Thou
        if rel.trust_level > 0.7 or abs(emotional_state.get("valence", 0)) > 0.5:
            self.current_mode = DialogueMode.I_THOU
        else:
            self.current_mode = DialogueMode.I_IT

    def _generate_response(
        self, input_text: str, emotional_state: Dict[str, float], rel: Relationship
    ) -> str:
        """Generate response based on mode and state."""
        if self.current_mode == DialogueMode.I_THOU:
            prefix = "[I-Thou] "
            if emotional_state.get("valence", 0) < -0.3:
                return f"{prefix}I sense you are troubled. How can I support you?"
            elif emotional_state.get("valence", 0) > 0.3:
                return f"{prefix}It is a joy to connect with you."
            else:
                return f"{prefix}I am present with you. What is on your mind?"
        else:
            # I-It mode (transactional)
            return f"Processed: {input_text}"

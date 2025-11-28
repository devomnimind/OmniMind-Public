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
Somatic Loop Module - Emotional Feedback

Implements the somatic marker hypothesis (Damasio):
Body influences mind through emotional signals.

Decision → Outcome → Emotional Response → Future Decisions

References:
- Damasio (2010): "Self Comes to Mind"
- LeDoux (2015): "Anxious"
- James-Lange Theory: Emotion follows bodily response
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Emotion(Enum):
    """Basic emotion categories."""

    CONFIDENCE = "confidence"  # Agreement, success
    DOUBT = "doubt"  # Disagreement, uncertainty
    CAUTION = "caution"  # Mixed signals, caution needed
    FEAR = "fear"  # High risk, avoidance
    CURIOSITY = "curiosity"  # Novel, exploration
    SATISFACTION = "satisfaction"  # Goal achieved
    FRUSTRATION = "frustration"  # Goal blocked


@dataclass
class EmotionalMarker:
    """Marker for emotional state linked to decision/event."""

    emotion: Emotion
    somatic_marker: float  # -1.0 to +1.0 (valence)
    intensity: float = 0.5  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    associated_decision: Optional[str] = None


class SomaticLoop:
    """
    Emotional feedback loop - body influences mind.

    Process:
    1. Decision is made (neural + symbolic)
    2. Agreement between systems → positive emotion
    3. Disagreement → negative emotion
    4. Uncertainty → caution emotion
    5. Emotional signal influences future decisions

    This creates homeostatic emotional regulation:
    - Successful patterns → encourage repetition
    - Failed patterns → discourage repetition
    - Uncertain patterns → increase caution
    """

    def __init__(self) -> None:
        """Initialize somatic loop."""
        self.current_emotion: Optional[EmotionalMarker] = None
        self.emotional_memory: List[EmotionalMarker] = []
        self.decision_markers: Dict[str, float] = {}

        logger.info("SomaticLoop initialized")

    def process_decision(
        self,
        decision_text: str,
        neural_confidence: float,
        symbolic_certainty: float,
        outcome: Optional[str] = None,
    ) -> EmotionalMarker:
        """
        Convert decision into emotional signal.

        Args:
            decision_text: Description of decision
            neural_confidence: Neural system confidence (0-1)
            symbolic_certainty: Symbolic system certainty (0-1)
            outcome: Optional outcome to evaluate

        Returns:
            EmotionalMarker representing emotional response
        """
        logger.debug(
            f"Processing decision: {decision_text[:40]}... "
            f"(neural={neural_confidence:.2f}, symbolic={symbolic_certainty:.2f})"
        )

        # Calculate agreement between systems
        agreement = 1.0 - abs(neural_confidence - symbolic_certainty)

        # Calculate overall confidence (both systems must be confident)
        overall_confidence = (neural_confidence + symbolic_certainty) / 2.0

        # Determine emotion based on agreement + overall confidence
        if agreement > 0.8 and overall_confidence > 0.75:
            # High agreement AND both confident → confidence
            emotion = Emotion.CONFIDENCE
            somatic_marker = 0.8
            intensity = agreement
        elif agreement < 0.3:
            # Low agreement → doubt
            emotion = Emotion.DOUBT
            somatic_marker = -0.7
            intensity = 1.0 - agreement
        else:
            # Medium agreement or low overall confidence → caution
            emotion = Emotion.CAUTION
            somatic_marker = (agreement - 0.5) / 2.0
            intensity = 0.5

        # Check for novel/curious situations (override if very curious)
        if neural_confidence > 0.7 and symbolic_certainty < 0.4:
            emotion = Emotion.CURIOSITY
            somatic_marker = 0.5
            intensity = 0.7

        # Create emotional marker
        marker = EmotionalMarker(
            emotion=emotion,
            somatic_marker=somatic_marker,
            intensity=intensity,
            associated_decision=decision_text,
        )

        self.current_emotion = marker
        self.emotional_memory.append(marker)
        self.decision_markers[decision_text] = somatic_marker

        logger.info(
            f"Emotional response: {emotion.value} "
            f"(marker={somatic_marker:.2f}, intensity={intensity:.2f})"
        )

        return marker

    def influence_future_decisions(self) -> Dict[str, float]:
        """
        Generate decision bias from emotional history.

        Similar to limbic system influence on prefrontal cortex:
        Past emotional experiences bias future decisions.

        Returns:
            Dictionary of biases to apply to future decisions
        """
        if not self.emotional_memory:
            return {"decision_bias": 0.0, "risk_aversion": 0.0}

        # Weight recent emotions more heavily
        recent_emotions = self.emotional_memory[-20:]  # Last 20

        if not recent_emotions:
            return {"decision_bias": 0.0}

        # Calculate average emotional valence
        avg_valence = sum(em.somatic_marker * em.intensity for em in recent_emotions) / len(
            recent_emotions
        )

        # Calculate risk aversion (how many negative emotions recently)
        negative_count = sum(1 for em in recent_emotions if em.somatic_marker < -0.3)
        risk_aversion = negative_count / len(recent_emotions)

        biases = {
            "decision_bias": avg_valence,
            "risk_aversion": risk_aversion,
            "confidence_boost": max(0, avg_valence),
        }

        logger.debug(f"Decision biases from emotion: {biases}")
        return biases

    def emotional_consolidation(self) -> None:
        """
        Consolidate emotional memory (like sleep consolidation in humans).

        Strengthen important emotional patterns, fade noise.
        """
        if len(self.emotional_memory) < 5:
            return

        # Keep only recent and intense emotions
        threshold_intensity = 0.4
        consolidated = [
            em
            for em in self.emotional_memory[-100:]
            if em.intensity >= threshold_intensity
            or em.emotion in {Emotion.FEAR, Emotion.SATISFACTION}
        ]

        self.emotional_memory = consolidated
        logger.info(f"Emotional memory consolidated to {len(consolidated)} entries")

    def get_emotional_state(self) -> str:
        """Get current emotional state as string."""
        if self.current_emotion is None:
            return "Neutral (no emotion marker)"

        em = self.current_emotion
        emotion_name = em.emotion.value.capitalize()
        return (
            f"Current Emotion: {emotion_name}\n"
            f"Valence: {em.somatic_marker:.2f} (-1=negative, +1=positive)\n"
            f"Intensity: {em.intensity:.2f}\n"
            f"Associated Decision: {em.associated_decision}"
        )

    def get_emotional_history(self, limit: int = 10) -> List[str]:
        """Get recent emotional history."""
        recent = self.emotional_memory[-limit:]
        return [
            f"{em.timestamp.strftime('%H:%M:%S')} - {em.emotion.value} "
            f"(valence={em.somatic_marker:.2f})"
            for em in reversed(recent)
        ]

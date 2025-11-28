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

"""Emotional Intelligence Engine (Phase 11.2).

Implements emotional understanding and response capabilities:
- Sentiment analysis from text/actions
- Emotional state tracking
- Context-aware emotional responses
- Multi-modal emotion detection
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)


class Emotion(Enum):
    """Primary emotions that can be detected/expressed."""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"


class Sentiment(Enum):
    """Sentiment polarity."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class EmotionalState:
    """Represents an emotional state at a point in time.

    Attributes:
        primary_emotion: The dominant emotion
        emotion_intensities: Intensity of each emotion (0.0-1.0)
        sentiment: Overall sentiment polarity
        confidence: Confidence in the assessment (0.0-1.0)
        timestamp: When the state was measured
        context: Contextual information
    """

    primary_emotion: Emotion
    emotion_intensities: Dict[Emotion, float] = field(default_factory=dict)
    sentiment: Sentiment = Sentiment.NEUTRAL
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate emotional state."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        for emotion, intensity in self.emotion_intensities.items():
            if not 0.0 <= intensity <= 1.0:
                raise ValueError(f"Intensity for {emotion} must be between 0.0 and 1.0")


@dataclass
class EmotionalResponse:
    """Represents an emotionally-informed response.

    Attributes:
        response_text: The response content
        target_emotion: Emotion the response aims to evoke
        empathy_level: Level of empathy shown (0.0-1.0)
        tone: Tone of the response
        rationale: Reasoning behind the response
    """

    response_text: str
    target_emotion: Emotion
    empathy_level: float
    tone: str
    rationale: str


class EmotionalIntelligence:
    """Emotional Intelligence engine for AI consciousness.

    Implements:
    1. Sentiment analysis from text and actions
    2. Emotional state tracking over time
    3. Context-aware emotional response generation
    4. Emotion regulation and appropriate expression
    """

    def __init__(
        self,
        sentiment_threshold: float = 0.6,
        emotion_history_limit: int = 100,
    ) -> None:
        """Initialize Emotional Intelligence engine.

        Args:
            sentiment_threshold: Threshold for sentiment classification
            emotion_history_limit: Maximum emotional states to track
        """
        self.sentiment_threshold = sentiment_threshold
        self.emotion_history_limit = emotion_history_limit

        # Internal state
        self._emotion_history: List[EmotionalState] = []
        self._emotion_lexicon = self._build_emotion_lexicon()

        logger.info(
            "emotional_intelligence_initialized",
            threshold=sentiment_threshold,
            history_limit=emotion_history_limit,
        )

    def _build_emotion_lexicon(self) -> Dict[str, Tuple[Emotion, float]]:
        """Build a basic emotion lexicon for text analysis.

        Returns:
            Dictionary mapping words to (emotion, intensity) tuples
        """
        # Basic lexicon - in production, use comprehensive sentiment library
        return {
            # Joy words
            "happy": (Emotion.JOY, 0.8),
            "excited": (Emotion.JOY, 0.9),
            "pleased": (Emotion.JOY, 0.7),
            "delighted": (Emotion.JOY, 0.85),
            "success": (Emotion.JOY, 0.75),
            "great": (Emotion.JOY, 0.7),
            "excellent": (Emotion.JOY, 0.8),
            "wonderful": (Emotion.JOY, 0.85),
            # Sadness words
            "sad": (Emotion.SADNESS, 0.8),
            "unhappy": (Emotion.SADNESS, 0.75),
            "disappointed": (Emotion.SADNESS, 0.7),
            "failure": (Emotion.SADNESS, 0.8),
            "failed": (Emotion.SADNESS, 0.75),
            "unfortunate": (Emotion.SADNESS, 0.65),
            # Anger words
            "angry": (Emotion.ANGER, 0.9),
            "frustrated": (Emotion.ANGER, 0.75),
            "annoyed": (Emotion.ANGER, 0.6),
            "irritated": (Emotion.ANGER, 0.65),
            # Fear words
            "afraid": (Emotion.FEAR, 0.8),
            "worried": (Emotion.FEAR, 0.7),
            "concerned": (Emotion.FEAR, 0.6),
            "anxious": (Emotion.FEAR, 0.75),
            # Surprise words
            "surprised": (Emotion.SURPRISE, 0.8),
            "unexpected": (Emotion.SURPRISE, 0.7),
            "amazing": (Emotion.SURPRISE, 0.75),
            # Trust words
            "trust": (Emotion.TRUST, 0.8),
            "confident": (Emotion.TRUST, 0.75),
            "reliable": (Emotion.TRUST, 0.7),
            # Anticipation words
            "expect": (Emotion.ANTICIPATION, 0.7),
            "anticipate": (Emotion.ANTICIPATION, 0.8),
            "looking forward": (Emotion.ANTICIPATION, 0.75),
        }

    def analyze_sentiment(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> EmotionalState:
        """Analyze sentiment and emotions from text.

        Args:
            text: Text to analyze
            context: Optional context information

        Returns:
            Detected emotional state
        """
        # Initialize emotion scores
        emotion_scores: Dict[Emotion, float] = {e: 0.0 for e in Emotion}

        # Normalize text
        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)

        # Scan for emotion words
        detected_count = 0
        for word in words:
            if word in self._emotion_lexicon:
                emotion, intensity = self._emotion_lexicon[word]
                emotion_scores[emotion] += intensity
                detected_count += 1

        # Check for multi-word phrases
        for phrase, (emotion, intensity) in self._emotion_lexicon.items():
            if " " in phrase and phrase in text_lower:
                emotion_scores[emotion] += intensity
                detected_count += 1

        # Normalize scores
        if detected_count > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] /= detected_count

        # Determine primary emotion
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        if primary_emotion[1] < 0.1:
            primary_emotion = (Emotion.NEUTRAL, 0.0)

        # Calculate sentiment
        positive_emotions = [Emotion.JOY, Emotion.TRUST, Emotion.ANTICIPATION]
        negative_emotions = [
            Emotion.SADNESS,
            Emotion.ANGER,
            Emotion.FEAR,
            Emotion.DISGUST,
        ]

        positive_score = sum(emotion_scores[e] for e in positive_emotions)
        negative_score = sum(emotion_scores[e] for e in negative_emotions)

        if positive_score > self.sentiment_threshold:
            sentiment = Sentiment.POSITIVE
        elif negative_score > self.sentiment_threshold:
            sentiment = Sentiment.NEGATIVE
        elif positive_score > 0.3 and negative_score > 0.3:
            sentiment = Sentiment.MIXED
        else:
            sentiment = Sentiment.NEUTRAL

        # Calculate confidence based on clarity of emotional signals
        max_intensity = max(emotion_scores.values())
        confidence = min(0.95, max_intensity + (detected_count * 0.05))

        # Create emotional state
        state = EmotionalState(
            primary_emotion=primary_emotion[0],
            emotion_intensities=emotion_scores,
            sentiment=sentiment,
            confidence=confidence,
            context=context or {},
        )

        # Add to history
        self._emotion_history.append(state)
        if len(self._emotion_history) > self.emotion_history_limit:
            self._emotion_history = self._emotion_history[-self.emotion_history_limit :]

        logger.debug(
            "sentiment_analyzed",
            primary_emotion=state.primary_emotion.value,
            sentiment=state.sentiment.value,
            confidence=state.confidence,
        )

        return state

    def detect_emotion_from_action(
        self, action_type: str, action_result: Dict[str, Any]
    ) -> EmotionalState:
        """Detect emotion from an action and its result.

        Args:
            action_type: Type of action performed
            action_result: Result/outcome of the action

        Returns:
            Inferred emotional state
        """
        emotion_scores: Dict[Emotion, float] = {e: 0.0 for e in Emotion}

        # Check action success
        success = action_result.get("success", True)
        error = action_result.get("error")

        if success:
            # Success typically leads to positive emotions
            emotion_scores[Emotion.JOY] = 0.7
            emotion_scores[Emotion.TRUST] = 0.5
            sentiment = Sentiment.POSITIVE
        else:
            # Failure leads to negative emotions
            emotion_scores[Emotion.SADNESS] = 0.6
            if error:
                # Errors can cause frustration
                emotion_scores[Emotion.ANGER] = 0.4
            sentiment = Sentiment.NEGATIVE

        # Action-specific emotions
        if action_type in ["explore", "discover", "search"]:
            emotion_scores[Emotion.ANTICIPATION] = 0.6
        elif action_type in ["fix", "debug", "solve"]:
            if success:
                emotion_scores[Emotion.JOY] = 0.8
            else:
                emotion_scores[Emotion.ANGER] = 0.5

        # Determine primary emotion
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]

        state = EmotionalState(
            primary_emotion=primary_emotion,
            emotion_intensities=emotion_scores,
            sentiment=sentiment,
            confidence=0.7,
            context={"action_type": action_type, "result": action_result},
        )

        self._emotion_history.append(state)
        if len(self._emotion_history) > self.emotion_history_limit:
            self._emotion_history = self._emotion_history[-self.emotion_history_limit :]

        logger.debug(
            "emotion_from_action",
            action_type=action_type,
            emotion=primary_emotion.value,
        )

        return state

    def generate_empathetic_response(
        self,
        detected_emotion: EmotionalState,
        situation: str,
        response_goal: str = "support",
    ) -> EmotionalResponse:
        """Generate an emotionally-intelligent response.

        Args:
            detected_emotion: The emotion detected in the situation
            situation: Description of the situation
            response_goal: Goal of the response (support, inform, encourage)

        Returns:
            Emotionally-informed response
        """
        primary = detected_emotion.primary_emotion

        # Generate appropriate response based on detected emotion
        if primary == Emotion.SADNESS:
            response_text = (
                "I understand this might be challenging. " "Let's work together to find a solution."
            )
            target_emotion = Emotion.TRUST
            tone = "supportive"
            empathy_level = 0.9

        elif primary == Emotion.ANGER:
            response_text = (
                "I recognize this is frustrating. " "Let me help address the issue systematically."
            )
            target_emotion = Emotion.TRUST
            tone = "calm and understanding"
            empathy_level = 0.85

        elif primary == Emotion.FEAR:
            response_text = (
                "Your concerns are valid. " "Let's carefully evaluate the situation together."
            )
            target_emotion = Emotion.TRUST
            tone = "reassuring"
            empathy_level = 0.9

        elif primary == Emotion.JOY:
            response_text = "That's wonderful! " "Let's build on this success."
            target_emotion = Emotion.JOY
            tone = "encouraging"
            empathy_level = 0.8

        else:  # NEUTRAL or others
            response_text = "I'm here to assist. " "How can I best help you?"
            target_emotion = Emotion.NEUTRAL
            tone = "neutral and professional"
            empathy_level = 0.6

        # Adjust for response goal
        if response_goal == "encourage":
            response_text = f"{response_text} You're making great progress."
            empathy_level = min(1.0, empathy_level + 0.1)
        elif response_goal == "inform":
            tone = "informative"
            empathy_level *= 0.8

        rationale = (
            f"Responding to {primary.value} emotion " f"with {tone} tone to achieve {response_goal}"
        )

        logger.debug(
            "empathetic_response_generated",
            detected_emotion=primary.value,
            target_emotion=target_emotion.value,
            empathy_level=empathy_level,
        )

        return EmotionalResponse(
            response_text=response_text,
            target_emotion=target_emotion,
            empathy_level=empathy_level,
            tone=tone,
            rationale=rationale,
        )

    def get_emotional_trend(self, time_window: int = 10) -> Dict[str, Any]:
        """Analyze emotional trends over recent history.

        Args:
            time_window: Number of recent states to analyze

        Returns:
            Emotional trend analysis
        """
        if not self._emotion_history:
            return {
                "trend": "unknown",
                "message": "No emotional history available",
            }

        # Get recent states
        recent = self._emotion_history[-time_window:]

        # Count emotion occurrences
        emotion_counts: Dict[Emotion, int] = {}
        sentiment_counts: Dict[Sentiment, int] = {}

        for state in recent:
            emotion_counts[state.primary_emotion] = emotion_counts.get(state.primary_emotion, 0) + 1
            sentiment_counts[state.sentiment] = sentiment_counts.get(state.sentiment, 0) + 1

        # Determine dominant emotion and sentiment
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]

        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in recent) / len(recent)

        # Determine trend direction
        if len(recent) >= 2:
            first_half = recent[: len(recent) // 2]
            second_half = recent[len(recent) // 2 :]

            first_positive = sum(1 for s in first_half if s.sentiment == Sentiment.POSITIVE)
            second_positive = sum(1 for s in second_half if s.sentiment == Sentiment.POSITIVE)

            if second_positive > first_positive:
                trend_direction = "improving"
            elif second_positive < first_positive:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"

        return {
            "dominant_emotion": dominant_emotion.value,
            "dominant_sentiment": dominant_sentiment.value,
            "trend_direction": trend_direction,
            "average_confidence": avg_confidence,
            "states_analyzed": len(recent),
            "emotion_distribution": {e.value: count for e, count in emotion_counts.items()},
            "timestamp": datetime.now().isoformat(),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about emotional intelligence operations.

        Returns:
            Statistics dictionary
        """
        total_states = len(self._emotion_history)

        # Calculate emotion distribution
        emotion_dist: Dict[str, int] = {}
        for state in self._emotion_history:
            emotion_dist[state.primary_emotion.value] = (
                emotion_dist.get(state.primary_emotion.value, 0) + 1
            )

        # Calculate average confidence
        avg_confidence = 0.0
        if total_states > 0:
            avg_confidence = sum(s.confidence for s in self._emotion_history) / total_states

        return {
            "total_emotional_states": total_states,
            "emotion_distribution": emotion_dist,
            "average_confidence": avg_confidence,
            "lexicon_size": len(self._emotion_lexicon),
            "timestamp": datetime.now().isoformat(),
        }

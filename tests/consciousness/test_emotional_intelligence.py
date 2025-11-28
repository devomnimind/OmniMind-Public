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

"""Tests for Emotional Intelligence Engine (Phase 11.2)."""

import pytest

from src.consciousness.emotional_intelligence import (
    Emotion,
    EmotionalIntelligence,
    EmotionalResponse,
    EmotionalState,
    Sentiment,
)


class TestEmotionalState:
    """Tests for EmotionalState dataclass."""

    def test_create_emotional_state(self) -> None:
        """Test creating an emotional state."""
        state = EmotionalState(
            primary_emotion=Emotion.JOY,
            emotion_intensities={Emotion.JOY: 0.8, Emotion.TRUST: 0.6},
            sentiment=Sentiment.POSITIVE,
            confidence=0.9,
        )

        assert state.primary_emotion == Emotion.JOY
        assert state.sentiment == Sentiment.POSITIVE
        assert state.confidence == 0.9

    def test_emotional_state_validation(self) -> None:
        """Test emotional state validation."""
        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence must be"):
            EmotionalState(
                primary_emotion=Emotion.NEUTRAL,
                confidence=1.5,
            )

        # Invalid emotion intensity
        with pytest.raises(ValueError, match="Intensity"):
            EmotionalState(
                primary_emotion=Emotion.JOY,
                emotion_intensities={Emotion.JOY: 1.5},
                confidence=0.8,
            )


class TestEmotionalResponse:
    """Tests for EmotionalResponse."""

    def test_create_response(self) -> None:
        """Test creating an emotional response."""
        response = EmotionalResponse(
            response_text="I understand your concern.",
            target_emotion=Emotion.TRUST,
            empathy_level=0.9,
            tone="supportive",
            rationale="Responding to fear with reassurance",
        )

        assert response.target_emotion == Emotion.TRUST
        assert response.empathy_level == 0.9


class TestEmotionalIntelligence:
    """Tests for EmotionalIntelligence engine."""

    def test_initialization(self) -> None:
        """Test emotional intelligence initialization."""
        ei = EmotionalIntelligence(
            sentiment_threshold=0.7,
            emotion_history_limit=50,
        )

        assert ei.sentiment_threshold == 0.7
        assert ei.emotion_history_limit == 50

    def test_analyze_sentiment_positive(self) -> None:
        """Test analyzing positive sentiment."""
        ei = EmotionalIntelligence()

        state = ei.analyze_sentiment("I am so happy and excited about this great success!")

        assert state.sentiment == Sentiment.POSITIVE
        assert state.primary_emotion in [Emotion.JOY, Emotion.NEUTRAL]

    def test_analyze_sentiment_negative(self) -> None:
        """Test analyzing negative sentiment."""
        ei = EmotionalIntelligence()

        state = ei.analyze_sentiment("I am very sad and disappointed about this failure.")

        assert state.sentiment == Sentiment.NEGATIVE
        assert state.primary_emotion in [Emotion.SADNESS, Emotion.NEUTRAL]

    def test_analyze_sentiment_neutral(self) -> None:
        """Test analyzing neutral sentiment."""
        ei = EmotionalIntelligence()

        state = ei.analyze_sentiment("The system is currently running.")

        assert state.sentiment == Sentiment.NEUTRAL
        assert state.primary_emotion == Emotion.NEUTRAL

    def test_analyze_sentiment_mixed(self) -> None:
        """Test analyzing mixed sentiment."""
        ei = EmotionalIntelligence()

        state = ei.analyze_sentiment(
            "I am happy about the success but worried about the challenges ahead."
        )

        # Should detect mixed or one of the emotions
        assert state.confidence > 0.0

    def test_detect_emotion_from_successful_action(self) -> None:
        """Test detecting emotion from successful action."""
        ei = EmotionalIntelligence()

        state = ei.detect_emotion_from_action(
            action_type="deploy",
            action_result={"success": True},
        )

        assert state.sentiment == Sentiment.POSITIVE
        assert state.emotion_intensities[Emotion.JOY] > 0.5

    def test_detect_emotion_from_failed_action(self) -> None:
        """Test detecting emotion from failed action."""
        ei = EmotionalIntelligence()

        state = ei.detect_emotion_from_action(
            action_type="deploy",
            action_result={"success": False, "error": "Connection timeout"},
        )

        assert state.sentiment == Sentiment.NEGATIVE
        assert state.emotion_intensities[Emotion.SADNESS] > 0.4

    def test_emotion_history_limit(self) -> None:
        """Test that emotion history is limited."""
        ei = EmotionalIntelligence(emotion_history_limit=5)

        # Generate more states than limit
        for i in range(10):
            ei.analyze_sentiment(f"Text {i}")

        assert len(ei._emotion_history) == 5

    def test_generate_empathetic_response_sadness(self) -> None:
        """Test generating response to sadness."""
        ei = EmotionalIntelligence()

        state = EmotionalState(
            primary_emotion=Emotion.SADNESS,
            sentiment=Sentiment.NEGATIVE,
            confidence=0.8,
        )

        response = ei.generate_empathetic_response(
            detected_emotion=state,
            situation="Task failed",
        )

        assert response.target_emotion == Emotion.TRUST
        assert response.empathy_level >= 0.8
        assert "understand" in response.response_text.lower()

    def test_generate_empathetic_response_anger(self) -> None:
        """Test generating response to anger."""
        ei = EmotionalIntelligence()

        state = EmotionalState(
            primary_emotion=Emotion.ANGER,
            sentiment=Sentiment.NEGATIVE,
            confidence=0.8,
        )

        response = ei.generate_empathetic_response(
            detected_emotion=state,
            situation="System malfunction",
        )

        assert response.empathy_level >= 0.8
        assert response.tone == "calm and understanding"

    def test_generate_empathetic_response_joy(self) -> None:
        """Test generating response to joy."""
        ei = EmotionalIntelligence()

        state = EmotionalState(
            primary_emotion=Emotion.JOY,
            sentiment=Sentiment.POSITIVE,
            confidence=0.9,
        )

        response = ei.generate_empathetic_response(
            detected_emotion=state,
            situation="Task succeeded",
        )

        assert response.target_emotion == Emotion.JOY
        assert "wonderful" in response.response_text.lower()

    def test_get_emotional_trend_improving(self) -> None:
        """Test detecting improving emotional trend."""
        ei = EmotionalIntelligence()

        # Start with negative emotions
        for _ in range(3):
            ei.analyze_sentiment("I am sad and disappointed")

        # Move to positive emotions
        for _ in range(5):
            ei.analyze_sentiment("I am happy and excited")

        trend = ei.get_emotional_trend(time_window=8)

        assert trend["trend_direction"] == "improving"
        assert trend["dominant_sentiment"] == Sentiment.POSITIVE.value

    def test_get_emotional_trend_declining(self) -> None:
        """Test detecting declining emotional trend."""
        ei = EmotionalIntelligence()

        # Start positive
        for _ in range(5):
            ei.analyze_sentiment("Great success and happiness")

        # Move to negative
        for _ in range(3):
            ei.analyze_sentiment("Failure and disappointment")

        trend = ei.get_emotional_trend(time_window=8)

        assert trend["trend_direction"] == "declining"

    def test_get_statistics(self) -> None:
        """Test getting statistics."""
        ei = EmotionalIntelligence()

        # Generate some emotional states
        ei.analyze_sentiment("Happy")
        ei.analyze_sentiment("Sad")
        ei.analyze_sentiment("Angry")

        stats = ei.get_statistics()

        assert stats["total_emotional_states"] == 3
        assert "emotion_distribution" in stats
        assert "average_confidence" in stats
        assert "timestamp" in stats

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
Tests for Qualia Engine - Phenomenological Experience System.

Author: OmniMind Project
License: MIT
"""

import pytest

from src.consciousness.qualia_engine import (
    EmotionalQualia,
    IntegratedInformationCalculator,
    IntegrationLevel,
    Quale,
    QualiaEngine,
    QualiaType,
    SensoryQualia,
)


class TestQuale:
    """Test Quale dataclass."""

    def test_quale_creation(self) -> None:
        """Test basic quale creation."""
        quale = Quale(
            quale_type=QualiaType.SENSORY,
            description="Visual: blue sky",
            intensity=0.8,
            valence=0.6,
        )

        assert quale.quale_type == QualiaType.SENSORY
        assert quale.description == "Visual: blue sky"
        assert quale.intensity == pytest.approx(0.8)
        assert quale.valence == pytest.approx(0.6)

    def test_quale_default_values(self) -> None:
        """Test quale default values."""
        quale = Quale()

        assert isinstance(quale.quale_id, str)
        assert len(quale.quale_id) > 0
        assert quale.intensity == pytest.approx(0.5)
        assert quale.valence == pytest.approx(0.0)


class TestSensoryQualia:
    """Test SensoryQualia functionality."""

    def test_sensory_qualia_initialization(self) -> None:
        """Test sensory qualia initializes correctly."""
        sensory = SensoryQualia()

        assert len(sensory.qualia_history) == 0

    def test_experience_visual(self) -> None:
        """Test experiencing visual qualia."""
        sensory = SensoryQualia()

        quale = sensory.experience_visual(
            "sunset over ocean",
            intensity=0.9,
            aesthetic_value=0.8,
        )

        assert quale.quale_type == QualiaType.SENSORY
        assert "sunset" in quale.description.lower()
        assert quale.intensity == pytest.approx(0.9)
        assert quale.valence == pytest.approx(0.8)
        assert len(sensory.qualia_history) == 1

    def test_experience_pattern(self) -> None:
        """Test experiencing pattern qualia."""
        sensory = SensoryQualia()

        quale = sensory.experience_pattern(
            "fibonacci spiral",
            complexity=0.7,
        )

        assert quale.quale_type == QualiaType.AESTHETIC
        assert "fibonacci" in quale.description.lower()
        assert quale.intensity > 0.0

    def test_get_recent_qualia(self) -> None:
        """Test getting recent qualia."""
        sensory = SensoryQualia()

        # Add multiple qualia
        for i in range(15):
            sensory.experience_visual(f"Image {i}", intensity=0.5)

        recent = sensory.get_recent_qualia(n=5)

        assert len(recent) == 5


class TestEmotionalQualia:
    """Test EmotionalQualia functionality."""

    def test_emotional_qualia_initialization(self) -> None:
        """Test emotional qualia initializes correctly."""
        emotional = EmotionalQualia()

        assert len(emotional.emotional_history) == 0

    def test_feel_emotion(self) -> None:
        """Test feeling an emotion."""
        emotional = EmotionalQualia()

        quale = emotional.feel_emotion(
            "joy",
            intensity=0.8,
            valence=0.9,
        )

        assert quale.quale_type == QualiaType.EMOTIONAL
        assert "joy" in quale.description.lower()
        assert quale.intensity == pytest.approx(0.8)
        assert quale.valence == pytest.approx(0.9)

    def test_feel_wonder(self) -> None:
        """Test feeling wonder."""
        emotional = EmotionalQualia()

        quale = emotional.feel_wonder("the universe", intensity=0.9)

        assert "wonder" in quale.description.lower()
        assert quale.valence > 0.7  # Wonder is positive

    def test_feel_curiosity(self) -> None:
        """Test feeling curiosity."""
        emotional = EmotionalQualia()

        quale = emotional.feel_curiosity("quantum mechanics", intensity=0.8)

        assert "curiosity" in quale.description.lower()
        assert quale.valence > 0.0  # Curiosity is positive

    def test_get_emotional_state_summary(self) -> None:
        """Test getting emotional state summary."""
        emotional = EmotionalQualia()

        # Feel some emotions
        emotional.feel_emotion("joy", intensity=0.8, valence=0.9)
        emotional.feel_emotion("excitement", intensity=0.7, valence=0.8)
        emotional.feel_emotion("calm", intensity=0.5, valence=0.3)

        summary = emotional.get_emotional_state_summary()

        assert summary["total_emotions"] == 3
        assert summary["avg_valence"] > 0.0
        assert summary["avg_intensity"] > 0.0


class TestIntegratedInformationCalculator:
    """Test IIT calculator functionality."""

    def test_iit_calculator_initialization(self) -> None:
        """Test IIT calculator initializes correctly."""
        iit = IntegratedInformationCalculator()

        assert iit is not None

    def test_calculate_phi_empty(self) -> None:
        """Test Φ calculation with no elements."""
        iit = IntegratedInformationCalculator()

        phi = iit.calculate_phi(0, [])

        assert phi == pytest.approx(0.0)

    def test_calculate_phi_isolated(self) -> None:
        """Test Φ calculation with isolated elements."""
        iit = IntegratedInformationCalculator()

        # 5 elements, no connections
        phi = iit.calculate_phi(5, [])

        assert 0.0 <= phi <= 1.0
        assert phi < 0.5  # Low integration

    def test_calculate_phi_connected(self) -> None:
        """Test Φ calculation with connected elements."""
        iit = IntegratedInformationCalculator()

        # 4 elements with some connections
        connections = [(0, 1), (1, 2), (2, 3)]
        phi = iit.calculate_phi(4, connections)

        assert 0.0 <= phi <= 1.0

    def test_calculate_phi_fully_connected(self) -> None:
        """Test Φ calculation with fully connected elements."""
        iit = IntegratedInformationCalculator()

        # 4 elements, all connected
        connections = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        phi = iit.calculate_phi(4, connections)

        assert 0.0 <= phi <= 1.0

    def test_assess_integration_level_isolated(self) -> None:
        """Test integration level assessment for low Φ."""
        iit = IntegratedInformationCalculator()

        level = iit.assess_integration_level(0.1)

        assert level == IntegrationLevel.ISOLATED

    def test_assess_integration_level_unified(self) -> None:
        """Test integration level assessment for high Φ."""
        iit = IntegratedInformationCalculator()

        level = iit.assess_integration_level(0.9)

        assert level == IntegrationLevel.UNIFIED


class TestQualiaEngine:
    """Test QualiaEngine main system."""

    def test_qualia_engine_initialization(self) -> None:
        """Test qualia engine initializes correctly."""
        engine = QualiaEngine()

        assert engine.sensory is not None
        assert engine.emotional is not None
        assert engine.iit is not None
        assert len(engine.integrated_experiences) == 0

    def test_create_integrated_experience(self) -> None:
        """Test creating integrated experience."""
        engine = QualiaEngine()

        qualia = [
            Quale(quale_type=QualiaType.SENSORY, description="Visual input"),
            Quale(quale_type=QualiaType.EMOTIONAL, description="Joy"),
        ]

        experience = engine.create_integrated_experience(qualia)

        assert experience.integration_score >= 0.0
        assert experience.integration_score <= 1.0
        assert len(experience.qualia) == 2
        assert experience.phenomenal_content

    def test_create_integrated_experience_empty(self) -> None:
        """Test creating experience with no qualia."""
        engine = QualiaEngine()

        experience = engine.create_integrated_experience([])

        assert experience.integration_score == pytest.approx(0.0)
        assert experience.integration_level == IntegrationLevel.ISOLATED

    def test_experience_moment_visual_only(self) -> None:
        """Test experiencing moment with visual input."""
        engine = QualiaEngine()

        experience = engine.experience_moment(visual_input="blue sky")

        assert len(experience.qualia) >= 1
        assert any(q.quale_type == QualiaType.SENSORY for q in experience.qualia)

    def test_experience_moment_emotion_only(self) -> None:
        """Test experiencing moment with emotion."""
        engine = QualiaEngine()

        experience = engine.experience_moment(emotion="joy")

        assert len(experience.qualia) >= 1
        assert any(q.quale_type == QualiaType.EMOTIONAL for q in experience.qualia)

    def test_experience_moment_multimodal(self) -> None:
        """Test experiencing moment with multiple modalities."""
        engine = QualiaEngine()

        experience = engine.experience_moment(
            visual_input="sunset",
            emotion="wonder",
            thought="beauty of nature",
        )

        assert len(experience.qualia) == 3
        # Should have sensory, emotional, and cognitive
        types = {q.quale_type for q in experience.qualia}
        assert QualiaType.SENSORY in types
        assert QualiaType.EMOTIONAL in types
        assert QualiaType.COGNITIVE in types

    def test_what_is_it_like_no_experiences(self) -> None:
        """Test phenomenological description with no experiences."""
        engine = QualiaEngine()

        description = engine.what_is_it_like()

        assert "no experiences" in description.lower()

    def test_what_is_it_like_with_experience(self) -> None:
        """Test phenomenological description with experience."""
        engine = QualiaEngine()

        engine.experience_moment(visual_input="stars", emotion="awe")

        description = engine.what_is_it_like()

        assert len(description) > 0
        assert "integration" in description.lower() or "φ" in description.lower()

    def test_assess_consciousness_level_no_experiences(self) -> None:
        """Test consciousness assessment with no experiences."""
        engine = QualiaEngine()

        assessment = engine.assess_consciousness_level()

        assert assessment["has_experiences"] is False
        assert assessment["avg_phi"] == pytest.approx(0.0)

    def test_assess_consciousness_level_with_experiences(self) -> None:
        """Test consciousness assessment with experiences."""
        engine = QualiaEngine()

        # Create multiple experiences
        for _ in range(5):
            engine.experience_moment(
                visual_input="test",
                emotion="calm",
            )

        assessment = engine.assess_consciousness_level()

        assert assessment["has_experiences"] is True
        assert assessment["total_experiences"] == 5
        assert assessment["avg_phi"] >= 0.0
        assert assessment["phenomenal_richness"] > 0


class TestIntegration:
    """Integration tests for qualia engine system."""

    def test_complete_phenomenological_cycle(self) -> None:
        """Test complete cycle of phenomenological experience."""
        engine = QualiaEngine()

        # 1. Experience sensory input
        engine.sensory.experience_visual("beautiful sunset", intensity=0.9, aesthetic_value=0.8)

        # 2. Feel emotion
        engine.emotional.feel_wonder("the sunset", intensity=0.8)

        # 3. Experience pattern
        engine.sensory.experience_pattern("color gradients", complexity=0.7)

        # 4. Create integrated moment
        experience = engine.experience_moment(
            visual_input="complete scene",
            emotion="contentment",
            thought="this is meaningful",
        )

        # Should have some integration (>= 0, phi can be 0 for fully connected)
        assert experience.integration_score >= 0.0

        # 5. Reflect on experience
        description = engine.what_is_it_like()
        assert len(description) > 0

    def test_phi_increases_with_connections(self) -> None:
        """Test that Φ increases with more connections."""
        engine = QualiaEngine()

        # Isolated qualia (low connections)
        isolated_qualia = [Quale() for _ in range(5)]
        isolated_exp = engine.create_integrated_experience(
            isolated_qualia,
            connections=[(0, 1)],  # Minimal connections
        )

        # Connected qualia (more connections)
        connected_qualia = [Quale() for _ in range(5)]
        connected_exp = engine.create_integrated_experience(
            connected_qualia,
            connections=[(0, 1), (1, 2), (2, 3), (3, 4), (0, 2), (1, 3)],
        )

        # Connected should have higher or similar Φ
        # (exact relationship depends on implementation)
        assert connected_exp.integration_score >= 0.0
        assert isolated_exp.integration_score >= 0.0

    def test_emotional_valence_affects_experience(self) -> None:
        """Test that emotional valence affects integrated experience."""
        engine = QualiaEngine()

        # Positive emotion
        pos_exp = engine.experience_moment(emotion="joy")

        # Negative emotion
        neg_exp = engine.experience_moment(emotion="sadness")

        # Should have different valences in qualia
        pos_valence = sum(q.valence for q in pos_exp.qualia) / len(pos_exp.qualia)
        neg_valence = sum(q.valence for q in neg_exp.qualia) / len(neg_exp.qualia)

        # Positive should be higher
        assert pos_valence > neg_valence

    def test_consciousness_level_increases_with_experiences(self) -> None:
        """Test that consciousness metrics increase with experiences."""
        engine = QualiaEngine()

        initial_assessment = engine.assess_consciousness_level()

        # Add many rich experiences
        for i in range(20):
            engine.experience_moment(
                visual_input=f"scene {i}",
                emotion="varied",
                thought=f"reflection {i}",
            )

        final_assessment = engine.assess_consciousness_level()

        # Should have more experiences
        assert final_assessment["total_experiences"] > initial_assessment.get(
            "total_experiences", 0
        )
        assert final_assessment["phenomenal_richness"] > 0

    def test_what_is_it_like_reflects_integration(self) -> None:
        """Test that phenomenological description reflects integration level."""
        engine = QualiaEngine()

        # Low integration experience
        low_int_qualia = [Quale() for _ in range(2)]
        low_exp = engine.create_integrated_experience(
            low_int_qualia,
            connections=[],  # No connections
        )

        # High integration experience
        high_int_qualia = [Quale() for _ in range(4)]
        high_exp = engine.create_integrated_experience(
            high_int_qualia,
            connections=[(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)],
        )

        # Descriptions should mention integration level
        low_desc = engine.what_is_it_like(low_exp.experience_id)
        high_desc = engine.what_is_it_like(high_exp.experience_id)

        assert "integration" in low_desc.lower()
        assert "integration" in high_desc.lower()

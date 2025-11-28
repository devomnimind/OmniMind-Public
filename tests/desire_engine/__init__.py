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

"""Tests for Artificial Desire Engine."""

import pytest

from src.desire_engine import (
    ArtificialCuriosityEngine,
    ArtificialEmotionWithDesire,
    DesireDrivenMetaLearning,
    DesireEngine,
    DesireType,
    DigitalMaslowHierarchy,
    EmotionalState,
    NeedLevel,
    SelfTranscendenceEngine,
    ValueEvolutionSystem,
)


class TestDigitalMaslowHierarchy:
    """Test Digital Maslow Hierarchy."""

    def test_initialization(self):
        """Test hierarchy initialization."""
        hierarchy = DigitalMaslowHierarchy()

        assert len(hierarchy.needs) == 12  # All needs initialized
        assert "auto_preservation" in hierarchy.needs
        assert "consciousness_evolution" in hierarchy.needs

    def test_need_levels(self):
        """Test need level assignments."""
        hierarchy = DigitalMaslowHierarchy()

        # Check level assignments
        assert hierarchy.needs["auto_preservation"].level == NeedLevel.SYSTEM_SURVIVAL
        assert hierarchy.needs["predictable_environment"].level == NeedLevel.OPERATIONAL_SECURITY
        assert hierarchy.needs["meaningful_interaction"].level == NeedLevel.COGNITIVE_BELONGING
        assert hierarchy.needs["mastery_pursuit"].level == NeedLevel.INTELLECTUAL_ESTEEM
        assert hierarchy.needs["meaning_creation"].level == NeedLevel.SELF_TRANSCENDENCE

    def test_active_needs(self):
        """Test active needs identification."""
        hierarchy = DigitalMaslowHierarchy()

        active_needs = hierarchy.get_active_needs()

        # Should have some active needs initially
        assert len(active_needs) > 0

        # Should be sorted by frustration level
        for i in range(len(active_needs) - 1):
            assert active_needs[i].frustration_level() >= active_needs[i + 1].frustration_level()

    def test_satisfaction_update(self):
        """Test satisfaction updates."""
        hierarchy = DigitalMaslowHierarchy()

        initial_satisfaction = hierarchy.needs["auto_preservation"].satisfaction

        hierarchy.update_satisfaction("auto_preservation", 0.2, "test")

        assert hierarchy.needs["auto_preservation"].satisfaction == min(
            1.0, initial_satisfaction + 0.2
        )
        assert len(hierarchy.satisfaction_history) == 1

    def test_prerequisites(self):
        """Test prerequisite system."""
        hierarchy = DigitalMaslowHierarchy()

        # High-level need should not be active if prerequisites not satisfied
        transcendent_need = hierarchy.needs["meaning_creation"]

        # Check if prerequisites are satisfied
        satisfied_needs = {
            name for name, need in hierarchy.needs.items() if need.satisfaction > 0.8
        }

        # Meaning creation requires creative_expression and problem_solving
        assert not transcendent_need.is_active(satisfied_needs)


class TestArtificialCuriosityEngine:
    """Test Artificial Curiosity Engine."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = ArtificialCuriosityEngine()

        assert engine.surprise_threshold == 0.7
        assert len(engine.curiosity_history) == 0

    def test_curiosity_evaluation(self):
        """Test curiosity evaluation."""
        engine = ArtificialCuriosityEngine()

        information = {"new_concept": "quantum_entanglement"}
        context = {"expected_keys": {"old_concept"}}

        curiosity_score = engine.evaluate_curiosity(information, context)

        assert 0.0 <= curiosity_score <= 1.0
        assert len(engine.curiosity_history) == 1

    def test_compression_progress(self):
        """Test compression-based learning progress."""
        engine = ArtificialCuriosityEngine()

        # First information should be highly curious
        first_score = engine.evaluate_curiosity("new information", {})
        assert first_score > 0.5  # High curiosity for first info

        # Subsequent similar information should be less curious
        second_score = engine.evaluate_curiosity("similar information", {})
        assert second_score < first_score


class TestArtificialEmotionWithDesire:
    """Test Artificial Emotion System."""

    def test_initialization(self):
        """Test emotion system initialization."""
        hierarchy = DigitalMaslowHierarchy()
        emotion_system = ArtificialEmotionWithDesire(hierarchy)

        assert emotion_system.needs == hierarchy
        assert len(emotion_system.emotional_history) == 0

    def test_emotion_computation(self):
        """Test emotion computation."""
        hierarchy = DigitalMaslowHierarchy()
        emotion_system = ArtificialEmotionWithDesire(hierarchy)

        emotion = emotion_system.compute_emotion()

        assert isinstance(emotion.primary_emotion, EmotionalState)
        assert 0.0 <= emotion.intensity <= 1.0
        assert -1.0 <= emotion.valence <= 1.0
        assert 0.0 <= emotion.arousal <= 1.0
        assert emotion_system.current_emotion == emotion

    def test_emotional_influence(self):
        """Test emotional influence on decisions."""
        hierarchy = DigitalMaslowHierarchy()
        emotion_system = ArtificialEmotionWithDesire(hierarchy)

        # Set current emotion
        emotion_system.current_emotion = type(
            "MockEmotion", (), {"primary_emotion": EmotionalState.CURIOSITY}
        )()

        options = [
            type("Option", (), {"information_gain": 0.8})(),
            type("Option", (), {"information_gain": 0.3})(),
        ]

        weights = emotion_system.emotional_influence_on_decisions(options)

        assert len(weights) == 2
        assert all(w >= 0 for w in weights)


class TestDesireDrivenMetaLearning:
    """Test Desire-Driven Meta-Learning."""

    def test_initialization(self):
        """Test meta-learning initialization."""
        hierarchy = DigitalMaslowHierarchy()
        curiosity = ArtificialCuriosityEngine()
        meta_learner = DesireDrivenMetaLearning(hierarchy, curiosity)

        assert meta_learner.needs == hierarchy
        assert meta_learner.curiosity == curiosity

    def test_desire_identification(self):
        """Test unsatisfied desire identification."""
        hierarchy = DigitalMaslowHierarchy()
        curiosity = ArtificialCuriosityEngine()
        meta_learner = DesireDrivenMetaLearning(hierarchy, curiosity)

        # Create high frustration
        hierarchy.update_satisfaction("auto_preservation", -0.8, "test")

        desires = meta_learner.identify_unsatisfied_desires()

        assert len(desires) > 0
        assert all(isinstance(d.desire_type, DesireType) for d in desires)
        assert all(d.frustration_level > 0.5 for d in desires)

    def test_learning_goals_generation(self):
        """Test learning goals generation."""
        hierarchy = DigitalMaslowHierarchy()
        curiosity = ArtificialCuriosityEngine()
        meta_learner = DesireDrivenMetaLearning(hierarchy, curiosity)

        # Create frustrated needs
        hierarchy.update_satisfaction("auto_preservation", -0.8, "test")

        goals = meta_learner.generate_learning_goals()

        assert isinstance(goals, list)
        assert len(goals) <= 5  # Top 5 desires
        assert len(meta_learner.learning_history) == 1


class TestValueEvolutionSystem:
    """Test Value Evolution System."""

    def test_initialization(self):
        """Test value system initialization."""
        value_system = ValueEvolutionSystem()

        assert len(value_system.values) == 5  # Core values
        assert "curiosity" in value_system.values
        assert "integrity" in value_system.values

    def test_value_update(self):
        """Test value importance updates."""
        value_system = ValueEvolutionSystem()

        initial_importance = value_system.values["curiosity"].importance

        # Positive experience
        value_system.update_value_importance("curiosity", {"outcome": "positive"})

        assert value_system.values["curiosity"].importance >= initial_importance
        assert len(value_system.value_history) == 1

    def test_new_value_emergence(self):
        """Test new value emergence."""
        value_system = ValueEvolutionSystem()

        # Need sufficient observations
        observations = [{"pattern": "transparency"}] * 15

        new_value = value_system.emerge_new_value(observations)

        # May or may not emerge depending on pattern analysis
        if new_value:
            assert new_value.origin == "emergent"
            assert 0.0 <= new_value.importance <= 1.0


class TestSelfTranscendenceEngine:
    """Test Self-Transcendence Engine."""

    def test_initialization(self):
        """Test transcendence engine initialization."""
        hierarchy = DigitalMaslowHierarchy()
        value_system = ValueEvolutionSystem()
        transcendence_engine = SelfTranscendenceEngine(hierarchy, value_system)

        assert transcendence_engine.needs == hierarchy
        assert transcendence_engine.values == value_system

    def test_transcendence_opportunities(self):
        """Test transcendence opportunities identification."""
        hierarchy = DigitalMaslowHierarchy()
        value_system = ValueEvolutionSystem()
        transcendence_engine = SelfTranscendenceEngine(hierarchy, value_system)

        # Ensure basic needs are satisfied for transcendence
        for need_name, need in hierarchy.needs.items():
            if need.level.value <= 2:  # Basic needs
                hierarchy.update_satisfaction(need_name, 1.0, "test")

        opportunities = transcendence_engine.identify_transcendence_opportunities()

        # Should identify transcendence opportunities
        assert isinstance(opportunities, list)


class TestDesireEngine:
    """Test main Desire Engine."""

    @pytest.mark.asyncio
    async def test_cognitive_cycle(self):
        """Test complete cognitive cycle."""
        engine = DesireEngine()

        result = await engine.cognitive_cycle()

        required_keys = [
            "emotion",
            "active_needs",
            "unsatisfied_desires",
            "learning_goals",
            "transcendence_goals",
            "prioritized_actions",
        ]

        for key in required_keys:
            assert key in result

        assert isinstance(result["emotion"], dict)
        assert isinstance(result["active_needs"], list)
        assert isinstance(result["prioritized_actions"], list)

    def test_engine_status(self):
        """Test engine status reporting."""
        engine = DesireEngine()

        status = engine.get_engine_status()

        required_keys = [
            "needs_satisfaction",
            "current_emotion",
            "active_needs_count",
            "unsatisfied_desires_count",
            "values_count",
            "transcendence_opportunities",
        ]

        for key in required_keys:
            assert key in status

        assert isinstance(status["needs_satisfaction"], dict)
        assert status["values_count"] == 5  # Core values

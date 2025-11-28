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
Tests for Phase 16.1 - Embodied Cognition

Tests for:
- Sensory integration (visual, audio, proprioception)
- Somatic loop (emotional feedback)
- Motor output (action execution)
- Proprioception (self-awareness)
"""

import pytest

from src.embodied_cognition import (
    Emotion,
    MotorController,
    ProprioceptionModule,
    SensoryIntegration,
    SomaticLoop,
)


class TestSensoryIntegration:
    """Tests for multimodal sensory processing."""

    def test_initialization(self) -> None:
        """Test sensory system initialization."""
        sensory = SensoryIntegration(
            enable_vision=True,
            enable_audio=True,
            enable_proprioception=True,
        )
        assert sensory is not None
        assert sensory.enable_vision is True

    def test_visual_processing(self) -> None:
        """Test visual input processing."""
        sensory = SensoryIntegration()
        visual = sensory.process_visual_input("A person sitting at a table")

        assert visual.description is not None
        assert visual.confidence > 0.0

    def test_audio_processing(self) -> None:
        """Test audio input processing."""
        sensory = SensoryIntegration()
        audio = sensory.process_audio_input("Hello, I am happy today!")

        assert audio.transcription is not None
        assert audio.emotional_tone in ["positive", "negative", "neutral"]

    def test_proprioception_update(self) -> None:
        """Test proprioceptive state update."""
        sensory = SensoryIntegration()
        state = {"cpu": 45.5, "memory": 62.3, "battery": 85.0}

        sensory.update_proprioception(state)

        assert sensory.proprioceptive_state["cpu"] == pytest.approx(45.5)

    def test_multimodal_integration(self) -> None:
        """Test integration of multiple sensory streams."""
        sensory = SensoryIntegration()

        visual = sensory.process_visual_input("Sunny day with blue sky")
        audio = sensory.process_audio_input("Cheerful background music")
        state = {"mood_index": 0.8}
        sensory.update_proprioception(state)

        multimodal = sensory.integrate_multimodal(visual, audio, state)

        assert multimodal.visual is not None
        assert multimodal.audio is not None
        assert multimodal.proprioceptive_state is not None

    def test_sensory_summary(self) -> None:
        """Test generation of sensory state summary."""
        sensory = SensoryIntegration()
        sensory.process_visual_input("Test visual")
        summary = sensory.get_sensory_summary()

        assert "Visual" in summary


class TestSomaticLoop:
    """Tests for emotional feedback system."""

    def test_initialization(self) -> None:
        """Test somatic loop initialization."""
        loop = SomaticLoop()
        assert loop is not None
        assert len(loop.emotional_memory) == 0

    def test_decision_with_agreement(self) -> None:
        """Test emotion generation when systems agree."""
        loop = SomaticLoop()
        marker = loop.process_decision(
            "Make inference",
            neural_confidence=0.9,
            symbolic_certainty=0.95,
        )

        assert marker.emotion == Emotion.CONFIDENCE
        assert marker.somatic_marker > 0.7

    def test_decision_with_disagreement(self) -> None:
        """Test emotion generation when systems disagree."""
        loop = SomaticLoop()
        marker = loop.process_decision(
            "Make inference",
            neural_confidence=0.1,
            symbolic_certainty=0.9,
        )

        assert marker.emotion == Emotion.DOUBT
        assert marker.somatic_marker < -0.5

    def test_decision_with_mixed_signals(self) -> None:
        """Test emotion generation with mixed signals."""
        loop = SomaticLoop()
        marker = loop.process_decision(
            "Make inference",
            neural_confidence=0.6,
            symbolic_certainty=0.55,
        )

        assert marker.emotion == Emotion.CAUTION

    def test_emotional_influence_on_future(self) -> None:
        """Test that emotions influence future decisions."""
        loop = SomaticLoop()

        # Create positive emotional history
        for _ in range(5):
            loop.process_decision("decision", 0.95, 0.90)

        biases = loop.influence_future_decisions()

        assert biases["decision_bias"] > 0.5
        assert "risk_aversion" in biases

    def test_emotional_consolidation(self) -> None:
        """Test emotional memory consolidation."""
        loop = SomaticLoop()

        # Create diverse emotional history
        loop.process_decision("d1", 0.9, 0.95)
        loop.process_decision("d2", 0.1, 0.9)
        loop.process_decision("d3", 0.5, 0.55)

        initial_count = len(loop.emotional_memory)
        loop.emotional_consolidation()
        final_count = len(loop.emotional_memory)

        assert final_count <= initial_count

    def test_emotional_state_string(self) -> None:
        """Test emotional state narration."""
        loop = SomaticLoop()
        loop.process_decision("test", 0.9, 0.95)

        state = loop.get_emotional_state()

        assert "Confidence" in state
        assert "Valence" in state


class TestMotorController:
    """Tests for motor output and action execution."""

    def test_initialization(self) -> None:
        """Test motor controller initialization."""
        motor = MotorController(enable_ros=False, enable_simulation=True)
        assert motor is not None
        assert motor.enable_simulation is True

    def test_action_planning(self) -> None:
        """Test action plan creation."""
        motor = MotorController()
        plan = motor.plan_action_sequence("move to location A")

        assert len(plan) > 0
        assert "position" in " ".join(plan).lower()

    def test_single_action_execution(self) -> None:
        """Test execution of single action."""
        motor = MotorController(enable_simulation=True)
        result = motor.execute_single_action("test_action")

        assert isinstance(result, bool)

    def test_full_goal_execution(self) -> None:
        """Test complete goal execution pipeline."""
        motor = MotorController(enable_simulation=True)
        execution = motor.execute_goal("move to room B", {"rooms": ["A", "B"]})

        assert execution.goal == "move to room B"
        assert len(execution.plan) > 0
        assert isinstance(execution.success, bool)

    def test_goal_execution_with_context(self) -> None:
        """Test goal execution with environmental context."""
        motor = MotorController(enable_simulation=True)
        context = {"obstacles": ["desk", "chair"], "target": "window"}

        execution = motor.execute_goal("navigate to target", context)

        assert execution is not None
        assert len(execution.results) > 0

    def test_execution_history(self) -> None:
        """Test tracking of execution history."""
        motor = MotorController(enable_simulation=True)

        motor.execute_goal("goal1")
        motor.execute_goal("goal2")
        motor.execute_goal("goal3")

        assert len(motor.action_history) == 3

        summary = motor.get_execution_summary()
        assert "goal" in summary.lower()


class TestProprioception:
    """Tests for self-awareness and internal state monitoring."""

    def test_initialization(self) -> None:
        """Test proprioception module initialization."""
        prop = ProprioceptionModule()
        assert prop is not None
        assert prop.current_state is not None

    def test_state_update(self) -> None:
        """Test internal state update."""
        prop = ProprioceptionModule()
        state = prop.update_state()

        assert state.memory_usage >= 0.0
        assert state.cpu_usage >= 0.0

    def test_resource_health_check(self) -> None:
        """Test resource health monitoring."""
        prop = ProprioceptionModule()
        prop.update_state()

        health = prop.check_resource_health()

        assert "memory_ok" in health
        assert "cpu_ok" in health
        assert isinstance(health["memory_ok"], bool)

    def test_state_awareness_narration(self) -> None:
        """Test self-awareness narration."""
        prop = ProprioceptionModule()
        prop.update_state()

        awareness = prop.get_state_awareness()

        assert "OmniMind" in awareness.description
        assert "Memory" in awareness.description
        assert "CPU" in awareness.description

    def test_anomaly_detection(self) -> None:
        """Test anomaly detection in state history."""
        prop = ProprioceptionModule()

        # Build up history
        for _ in range(15):
            prop.update_state()

        anomalies = prop.detect_anomalies()

        assert isinstance(anomalies, list)

    def test_state_history_summary(self) -> None:
        """Test state history summary generation."""
        prop = ProprioceptionModule()

        for _ in range(10):
            prop.update_state()

        summary = prop.get_state_history_summary()

        assert "STATE HISTORY" in summary
        assert "Memory" in summary
        assert "CPU" in summary

    def test_custom_state_variable(self) -> None:
        """Test setting custom state variables."""
        prop = ProprioceptionModule()
        prop.set_state_variable("emotional_valence", 0.7)

        assert prop.current_state.emotional_valence == pytest.approx(0.7)


class TestEmbodiedIntegration:
    """Integration tests combining multiple embodied components."""

    def test_sensory_to_somatic_pipeline(self) -> None:
        """Test integration of sensory input to emotional response."""
        sensory = SensoryIntegration()
        loop = SomaticLoop()

        # Process sensory input
        sensory.process_visual_input("Bright, colorful scene")

        # Generate emotional response
        marker = loop.process_decision(
            "Respond to visual input",
            neural_confidence=0.85,
            symbolic_certainty=0.88,
        )

        assert marker.emotion == Emotion.CONFIDENCE

    def test_goal_to_action_with_feedback(self) -> None:
        """Test goal execution with proprioceptive feedback."""
        motor = MotorController(enable_simulation=True)
        prop = ProprioceptionModule()

        # Set goal
        execution = motor.execute_goal("navigate_forward")

        # Get proprioceptive feedback
        prop.update_state()
        awareness = prop.get_state_awareness()

        assert execution.success is not None
        assert "OmniMind" in awareness.description

    def test_full_embodied_cycle(self) -> None:
        """Test complete embodied cognition cycle."""
        sensory = SensoryIntegration()
        loop = SomaticLoop()
        motor = MotorController(enable_simulation=True)
        prop = ProprioceptionModule()

        # Cycle 1: Sense
        visual = sensory.process_visual_input("Object detected")
        sensory.update_proprioception({"attention": 0.8})

        # Cycle 2: Evaluate emotionally
        marker = loop.process_decision(
            "Respond to stimulus",
            0.9,
            0.85,
        )

        # Cycle 3: Act
        execution = motor.execute_goal("approach_object")

        # Cycle 4: Monitor self
        prop.update_state()

        assert visual is not None
        assert marker.emotion in [e for e in Emotion]
        assert execution.success is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

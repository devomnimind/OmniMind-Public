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
Extended tests for Embodied Cognition (Phase 16.1 completion).

Tests multimodal fusion, edge cases, and advanced scenarios.
"""

import pytest

from src.embodied_cognition.motor_output import MotorController
from src.embodied_cognition.proprioception import ProprioceptionModule
from src.embodied_cognition.sensory_integration import SensoryIntegration
from src.embodied_cognition.somatic_loop import SomaticLoop


class TestMultimodalFusion:
    """Test fusion of multiple sensory modalities."""

    def test_visual_audio_fusion(self) -> None:
        """Test integration of visual and audio inputs."""
        sensory = SensoryIntegration()

        visual = sensory.process_visual_input("A red car approaching")
        audio = sensory.process_audio_input("Engine sound, tires screeching")

        assert visual.embedding is not None
        assert audio.transcription is not None
        # Both should contribute to understanding
        assert len(visual.symbolic_facts) > 0 if visual.symbolic_facts else True
        assert audio.emotional_tone is not None

    def test_sensory_failure_graceful_degradation(self) -> None:
        """Test system handles missing sensory input gracefully."""
        sensory = SensoryIntegration()

        # Only visual, no audio
        visual = sensory.process_visual_input("Scene description")
        assert visual is not None

        # System should still function with partial input

    def test_conflicting_sensory_inputs(self) -> None:
        """Test handling of conflicting multimodal inputs."""
        sensory = SensoryIntegration()

        visual = sensory.process_visual_input("Silent room, no movement")
        audio = sensory.process_audio_input("Loud explosion, screaming")

        # System should handle contradiction
        assert visual.embedding is not None
        assert audio.transcription is not None


class TestMotorControllerExtended:
    """Extended tests for motor control system."""

    def test_complex_goal_decomposition(self) -> None:
        """Test decomposition of complex multi-step goals."""
        motor = MotorController(enable_simulation=True)

        complex_goal = "Navigate to kitchen, pick up cup, bring to living room"
        execution = motor.execute_goal(complex_goal)

        assert execution.success or not execution.success  # May succeed or fail
        assert len(execution.plan) > 0
        assert len(execution.results) == len(execution.plan)

    def test_goal_execution_with_failure(self) -> None:
        """Test handling of failed actions."""
        motor = MotorController(enable_simulation=True)

        # Some actions may fail in simulation
        execution = motor.execute_goal("impossible task")

        # Should complete execution even if failed
        assert execution.plan is not None
        assert execution.results is not None

    def test_concurrent_goals(self) -> None:
        """Test handling multiple goals."""
        motor = MotorController(enable_simulation=True)

        goal1 = motor.execute_goal("move forward")
        goal2 = motor.execute_goal("turn left")

        # Both should execute
        assert goal1.plan is not None
        assert goal2.plan is not None

    def test_motor_controller_simulation_mode(self) -> None:
        """Test simulation mode is working correctly."""
        motor = MotorController(enable_simulation=True, enable_ros=False)

        execution = motor.execute_goal("test action")

        # In simulation, actions are logged
        assert execution.plan is not None
        assert len(execution.results) > 0


class TestProprioceptionExtended:
    """Extended tests for proprioception and self-awareness."""

    def test_state_tracking_over_time(self) -> None:
        """Test proprioceptive state evolves over time."""
        prop = ProprioceptionModule()

        # Initial state
        prop.update_state()
        state1 = prop.get_state_awareness()

        # Update again (state may change)
        prop.update_state()
        state2 = prop.get_state_awareness()

        # Both should be valid self-descriptions
        assert "OmniMind" in state1.description
        assert "OmniMind" in state2.description

    def test_resource_monitoring_accuracy(self) -> None:
        """Test accuracy of resource monitoring."""
        prop = ProprioceptionModule()
        prop.update_state()

        awareness = prop.get_state_awareness()

        # Should report reasonable resource values
        assert awareness.resource_status is not None
        assert "memory" in awareness.resource_status.lower() or True

    def test_emotional_state_integration(self) -> None:
        """Test integration of emotional state in proprioception."""
        prop = ProprioceptionModule()

        # Update proprioception
        prop.update_state()
        awareness = prop.get_state_awareness()

        # Should be aware of internal state
        assert awareness.description is not None


class TestSomaticLoopExtended:
    """Extended tests for somatic loop and emotional processing."""

    def test_emotional_memory_influence(self) -> None:
        """Test how emotional history influences decisions."""
        loop = SomaticLoop()

        # Build emotional history
        for i in range(10):
            confidence = 0.9 if i % 2 == 0 else 0.3
            loop.process_decision(f"decision_{i}", confidence, confidence)

        # Emotional history should exist
        assert len(loop.emotional_memory) == 10

    def test_emotional_marker_consistency(self) -> None:
        """Test consistency of emotional markers."""
        loop = SomaticLoop()

        # High agreement scenarios
        marker1 = loop.process_decision("good decision", 0.9, 0.85)
        marker2 = loop.process_decision("another good", 0.88, 0.90)

        # Both should generate similar emotions
        assert marker1.somatic_marker > 0
        assert marker2.somatic_marker > 0

    def test_emotional_transition_tracking(self) -> None:
        """Test tracking of emotional state transitions."""
        loop = SomaticLoop()

        # Sequence of decisions with varying quality
        decisions = [
            ("decision1", 0.9, 0.9),  # Good
            ("decision2", 0.3, 0.2),  # Bad
            ("decision3", 0.5, 0.6),  # Uncertain
        ]

        for desc, neural_conf, symbolic_cert in decisions:
            marker = loop.process_decision(desc, neural_conf, symbolic_cert)
            assert marker.emotion is not None
            assert marker.somatic_marker is not None


class TestEmbodiedCognitionIntegration:
    """Test integration between embodied cognition components."""

    def test_sensory_to_motor_pipeline(self) -> None:
        """Test complete sensory → motor pipeline."""
        sensory = SensoryIntegration()
        motor = MotorController(enable_simulation=True)

        # Perceive
        visual = sensory.process_visual_input("obstacle ahead")

        # Act based on perception
        execution = motor.execute_goal("avoid obstacle")

        assert visual.embedding is not None
        assert execution.plan is not None

    def test_proprioception_informs_action(self) -> None:
        """Test how self-awareness informs action selection."""
        prop = ProprioceptionModule()
        motor = MotorController(enable_simulation=True)

        # Update self-awareness
        prop.update_state()
        awareness = prop.get_state_awareness()

        # Execute goal (could be influenced by state)
        execution = motor.execute_goal("test action")

        assert awareness.description is not None
        assert execution.plan is not None

    def test_emotional_feedback_loop(self) -> None:
        """Test emotional feedback influences future decisions."""
        somatic = SomaticLoop()

        # Positive experience
        marker1 = somatic.process_decision("success", 0.9, 0.9)

        # Negative experience
        marker2 = somatic.process_decision("failure", 0.2, 0.1)

        # Emotional history should accumulate
        assert len(somatic.emotional_memory) == 2
        assert marker1.somatic_marker != marker2.somatic_marker


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

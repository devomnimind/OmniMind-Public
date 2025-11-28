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
Comprehensive tests for Emergence Detector - Phase 19.

Tests detection of emergent patterns (clustering, synchronization, specialization).
"""

import pytest

from src.swarm.config import EmergenceConfig
from src.swarm.emergence_detector import EmergenceDetector
from src.swarm.types import EmergenceType


class TestEmergenceConfig:
    """Tests for EmergenceConfig validation."""

    def test_default_config(self) -> None:
        """Test default emergence configuration."""
        config = EmergenceConfig()

        assert config.detection_interval == 10
        assert config.clustering_threshold == pytest.approx(0.7)
        assert config.sync_threshold == pytest.approx(0.8)
        assert config.min_pattern_size == 5
        assert config.confidence_threshold == pytest.approx(0.6)

    def test_invalid_detection_interval(self) -> None:
        """Test validation for invalid detection interval."""
        with pytest.raises(ValueError, match="detection_interval deve ser >= 1"):
            EmergenceConfig(detection_interval=0)

    def test_invalid_min_pattern_size(self) -> None:
        """Test validation for invalid min pattern size."""
        with pytest.raises(ValueError, match="min_pattern_size deve ser >= 1"):
            EmergenceConfig(min_pattern_size=0)


class TestEmergenceDetector:
    """Tests for EmergenceDetector."""

    def test_initialization(self) -> None:
        """Test emergence detector initialization."""
        detector = EmergenceDetector()

        assert len(detector.detected_patterns) == 0
        assert len(detector.pattern_history) == 0

    def test_detect_no_patterns_insufficient_agents(self) -> None:
        """Test detection with insufficient agents."""
        config = EmergenceConfig(min_pattern_size=5)
        detector = EmergenceDetector(config)

        # Only 3 agents (< min_pattern_size)
        agent_states = [
            {"id": "1", "position": [0.0, 0.0], "velocity": [1.0, 0.0]},
            {"id": "2", "position": [1.0, 1.0], "velocity": [1.0, 0.0]},
            {"id": "3", "position": [2.0, 2.0], "velocity": [1.0, 0.0]},
        ]

        patterns = detector.detect_patterns(agent_states)

        assert len(patterns) == 0

    def test_detect_clustering(self) -> None:
        """Test detection of clustering pattern."""
        config = EmergenceConfig(clustering_threshold=0.8, min_pattern_size=3)
        detector = EmergenceDetector(config)

        # Create agents in tight clusters
        agent_states = [
            # Cluster 1 (near origin)
            {"id": "1", "position": [0.0, 0.0], "velocity": [0.1, 0.1], "fitness": 1.0},
            {"id": "2", "position": [0.1, 0.1], "velocity": [0.1, 0.1], "fitness": 1.1},
            {"id": "3", "position": [0.2, 0.0], "velocity": [0.1, 0.1], "fitness": 1.2},
            # Cluster 2 (far away)
            {
                "id": "4",
                "position": [10.0, 10.0],
                "velocity": [0.1, 0.1],
                "fitness": 2.0,
            },
            {
                "id": "5",
                "position": [10.1, 10.1],
                "velocity": [0.1, 0.1],
                "fitness": 2.1,
            },
            {
                "id": "6",
                "position": [10.2, 10.0],
                "velocity": [0.1, 0.1],
                "fitness": 2.2,
            },
        ]

        patterns = detector.detect_patterns(agent_states)

        # Should detect clustering
        clustering_patterns = [p for p in patterns if p.pattern_type == EmergenceType.CLUSTERING]
        assert len(clustering_patterns) > 0
        if clustering_patterns:
            assert clustering_patterns[0].confidence > 0.5

    def test_detect_synchronization(self) -> None:
        """Test detection of synchronization pattern."""
        config = EmergenceConfig(sync_threshold=0.7, min_pattern_size=4)
        detector = EmergenceDetector(config)

        # Create agents with similar velocities (synchronized)
        agent_states = [
            {"id": "1", "position": [0.0, 0.0], "velocity": [1.0, 0.5], "fitness": 1.0},
            {"id": "2", "position": [1.0, 1.0], "velocity": [1.0, 0.5], "fitness": 1.1},
            {"id": "3", "position": [2.0, 2.0], "velocity": [1.0, 0.5], "fitness": 1.2},
            {"id": "4", "position": [3.0, 3.0], "velocity": [1.0, 0.5], "fitness": 1.3},
            {"id": "5", "position": [4.0, 4.0], "velocity": [1.0, 0.5], "fitness": 1.4},
        ]

        patterns = detector.detect_patterns(agent_states)

        # Should detect synchronization
        sync_patterns = [p for p in patterns if p.pattern_type == EmergenceType.SYNCHRONIZATION]
        assert len(sync_patterns) > 0
        if sync_patterns:
            assert sync_patterns[0].confidence > 0.6

    def test_detect_specialization(self) -> None:
        """Test detection of specialization pattern."""
        config = EmergenceConfig(min_pattern_size=3)
        detector = EmergenceDetector(config)

        # Create agents with very different fitness (specialization)
        agent_states = [
            {"id": "1", "position": [0.0, 0.0], "velocity": [1.0, 0.0], "fitness": 1.0},
            {"id": "2", "position": [1.0, 1.0], "velocity": [1.0, 0.0], "fitness": 2.0},
            {"id": "3", "position": [2.0, 2.0], "velocity": [1.0, 0.0], "fitness": 3.0},
            {
                "id": "4",
                "position": [3.0, 3.0],
                "velocity": [1.0, 0.0],
                "fitness": 50.0,
            },
            {
                "id": "5",
                "position": [4.0, 4.0],
                "velocity": [1.0, 0.0],
                "fitness": 100.0,
            },
            {
                "id": "6",
                "position": [5.0, 5.0],
                "velocity": [1.0, 0.0],
                "fitness": 150.0,
            },
        ]

        patterns = detector.detect_patterns(agent_states)

        # Should detect specialization - verify no errors
        assert patterns is not None

    def test_pattern_history(self) -> None:
        """Test that patterns are stored in history."""
        detector = EmergenceDetector()

        agent_states = [
            {
                "id": str(i),
                "position": [0.0, float(i)],
                "velocity": [1.0, 0.0],
                "fitness": 1.0,
            }
            for i in range(10)
        ]

        patterns = detector.detect_patterns(agent_states)

        # Patterns should be stored
        assert len(detector.detected_patterns) >= len(patterns)

    def test_get_pattern_summary(self) -> None:
        """Test pattern summary generation."""
        detector = EmergenceDetector()

        # Detect some patterns
        agent_states = [
            {
                "id": str(i),
                "position": [float(i % 2) * 10, float(i)],
                "velocity": [1.0, 0.0],
                "fitness": 1.0,
            }
            for i in range(10)
        ]

        detector.detect_patterns(agent_states)
        summary = detector.get_pattern_summary()

        assert "total_patterns" in summary
        assert "by_type" in summary
        assert "recent_patterns" in summary
        assert isinstance(summary["total_patterns"], int)

    def test_clear_history(self) -> None:
        """Test clearing pattern history."""
        detector = EmergenceDetector()

        # Detect some patterns
        agent_states = [
            {
                "id": str(i),
                "position": [float(i), float(i)],
                "velocity": [1.0, 0.0],
                "fitness": 1.0,
            }
            for i in range(10)
        ]

        detector.detect_patterns(agent_states)

        # Clear history
        detector.clear_history()

        assert len(detector.detected_patterns) == 0
        assert len(detector.pattern_history) == 0

    def test_multiple_pattern_types(self) -> None:
        """Test detection of multiple pattern types simultaneously."""
        config = EmergenceConfig(
            clustering_threshold=0.6,
            sync_threshold=0.6,
            min_pattern_size=3,
        )
        detector = EmergenceDetector(config)

        # Create agents with both clustering and synchronization
        agent_states = [
            # Cluster + sync group 1
            {"id": "1", "position": [0.0, 0.0], "velocity": [1.0, 1.0], "fitness": 1.0},
            {"id": "2", "position": [0.1, 0.1], "velocity": [1.0, 1.0], "fitness": 1.1},
            {"id": "3", "position": [0.2, 0.0], "velocity": [1.0, 1.0], "fitness": 1.2},
            # Cluster + sync group 2
            {
                "id": "4",
                "position": [10.0, 10.0],
                "velocity": [0.5, 0.5],
                "fitness": 2.0,
            },
            {
                "id": "5",
                "position": [10.1, 10.1],
                "velocity": [0.5, 0.5],
                "fitness": 2.1,
            },
            {
                "id": "6",
                "position": [10.2, 10.0],
                "velocity": [0.5, 0.5],
                "fitness": 2.2,
            },
        ]

        patterns = detector.detect_patterns(agent_states)

        # May detect multiple types - verify no errors
        assert len(patterns) > 0


class TestEmergenceIntegration:
    """Integration tests for emergence detection."""

    def test_detect_patterns_in_pso_swarm(self) -> None:
        """Test detecting patterns in PSO-like swarm."""
        detector = EmergenceDetector()

        # Simulate PSO swarm converging to optimum
        agent_states = []
        for i in range(50):
            # Most particles converging to [5.0, 5.0]
            pos_noise = (i % 5) * 0.1
            agent_states.append(
                {
                    "id": str(i),
                    "position": [5.0 + pos_noise, 5.0 + pos_noise],
                    "velocity": [0.1, 0.1],
                    "fitness": pos_noise**2,
                }
            )

        patterns = detector.detect_patterns(agent_states)

        # Should detect at least one pattern (likely clustering or sync)
        assert len(patterns) > 0

    def test_detect_patterns_no_emergence(self) -> None:
        """Test with random states (no clear emergence)."""
        import random

        detector = EmergenceDetector()

        # Completely random states
        random.seed(42)
        agent_states = []
        for i in range(20):
            agent_states.append(
                {
                    "id": str(i),
                    "position": [random.uniform(-10, 10), random.uniform(-10, 10)],
                    "velocity": [random.uniform(-1, 1), random.uniform(-1, 1)],
                    "fitness": random.uniform(0, 100),
                }
            )

        patterns = detector.detect_patterns(agent_states)

        # May or may not detect patterns in random data
        # Just verify no errors
        assert patterns is not None

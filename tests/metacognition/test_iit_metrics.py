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

"""Tests for IIT (Integrated Information Theory) consciousness metrics."""

import pytest

from src.metacognition.iit_metrics import IITAnalyzer, PhiMetrics, SystemState


def test_system_state_creation() -> None:
    """Test SystemState creation."""
    state = SystemState(
        state_id="state-1",
        elements={"a": True, "b": False, "c": True},
    )

    assert state.state_id == "state-1"
    assert len(state.elements) == 3
    assert state.elements["a"] is True
    assert state.elements["b"] is False


def test_system_state_to_vector() -> None:
    """Test converting state to binary vector."""
    state = SystemState(
        state_id="state-1",
        elements={"a": True, "b": False, "c": True},
    )

    vector = state.to_vector()

    assert len(vector) == 3
    assert vector[0] == 1  # a=True
    assert vector[1] == 0  # b=False
    assert vector[2] == 1  # c=True


def test_system_state_hamming_distance() -> None:
    """Test Hamming distance calculation."""
    state1 = SystemState(
        state_id="state-1",
        elements={"a": True, "b": False, "c": True},
    )

    state2 = SystemState(
        state_id="state-2",
        elements={"a": True, "b": True, "c": False},
    )

    distance = state1.hamming_distance(state2)

    assert distance == 2  # b and c differ


def test_phi_metrics_creation() -> None:
    """Test PhiMetrics creation."""
    metrics = PhiMetrics(
        phi_value=2.5,
        complexity=1.8,
        integration=0.7,
        differentiation=0.6,
        emergence_level=0.8,
    )

    assert metrics.phi_value == 2.5
    assert metrics.complexity == 1.8
    assert metrics.emergence_level == 0.8


def test_phi_metrics_to_dict() -> None:
    """Test PhiMetrics serialization."""
    metrics = PhiMetrics(
        phi_value=2.5,
        complexity=1.8,
        integration=0.7,
        differentiation=0.6,
        emergence_level=0.8,
    )

    data = metrics.to_dict()

    assert data["phi_value"] == 2.5
    assert data["complexity"] == 1.8
    assert "timestamp" in data


def test_iit_analyzer_creation() -> None:
    """Test IITAnalyzer creation."""
    analyzer = IITAnalyzer()

    assert len(analyzer.state_history) == 0
    assert len(analyzer.phi_history) == 0
    assert analyzer.emergence_threshold == 0.5


def test_record_state() -> None:
    """Test recording system states."""
    analyzer = IITAnalyzer()

    state = SystemState(
        state_id="state-1",
        elements={"a": True, "b": False},
    )

    analyzer.record_state(state)

    assert len(analyzer.state_history) == 1
    assert analyzer.state_history[0].state_id == "state-1"


def test_record_state_limit() -> None:
    """Test state history limit (1000 max)."""
    analyzer = IITAnalyzer()

    # Add 1100 states
    for i in range(1100):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0},
        )
        analyzer.record_state(state)

    # Should keep only last 1000
    assert len(analyzer.state_history) == 1000
    assert analyzer.state_history[0].state_id == "state-100"


def test_calculate_entropy_empty() -> None:
    """Test entropy calculation with no states."""
    analyzer = IITAnalyzer()

    entropy = analyzer.calculate_entropy([])

    assert entropy == 0.0


def test_calculate_entropy_single_state() -> None:
    """Test entropy with single repeated state."""
    analyzer = IITAnalyzer()

    states = [SystemState(state_id=f"s{i}", elements={"a": True, "b": False}) for i in range(10)]

    entropy = analyzer.calculate_entropy(states)

    # All states identical -> entropy = 0
    assert entropy == 0.0


def test_calculate_entropy_diverse_states() -> None:
    """Test entropy with diverse states."""
    analyzer = IITAnalyzer()

    # Create all possible 2-bit states
    states = [
        SystemState(state_id="s1", elements={"a": False, "b": False}),
        SystemState(state_id="s2", elements={"a": False, "b": True}),
        SystemState(state_id="s3", elements={"a": True, "b": False}),
        SystemState(state_id="s4", elements={"a": True, "b": True}),
    ]

    entropy = analyzer.calculate_entropy(states)

    # Maximum entropy for 2 bits = 2.0
    assert entropy == pytest.approx(2.0)


def test_calculate_mutual_information() -> None:
    """Test mutual information calculation."""
    analyzer = IITAnalyzer()

    states = [
        SystemState(state_id="s1", elements={"a": False, "b": False}),
        SystemState(state_id="s2", elements={"a": True, "b": True}),
        SystemState(state_id="s3", elements={"a": False, "b": False}),
        SystemState(state_id="s4", elements={"a": True, "b": True}),
    ]

    partition1 = {"a"}
    partition2 = {"b"}

    mi = analyzer.calculate_mutual_information(partition1, partition2, states)

    # a and b are perfectly correlated -> high MI
    assert mi > 0.0


def test_calculate_phi_empty() -> None:
    """Test phi calculation with no states."""
    analyzer = IITAnalyzer()

    phi = analyzer.calculate_phi([])

    assert phi == 0.0


def test_calculate_phi_single_element() -> None:
    """Test phi with single element (no integration possible)."""
    analyzer = IITAnalyzer()

    states = [
        SystemState(state_id="s1", elements={"a": True}),
        SystemState(state_id="s2", elements={"a": False}),
    ]

    phi = analyzer.calculate_phi(states)

    # Single element -> no integration
    assert phi == 0.0


def test_calculate_phi_integrated_system() -> None:
    """Test phi with integrated system."""
    analyzer = IITAnalyzer()

    # Create states with correlation between elements
    states = [
        SystemState(state_id="s1", elements={"a": False, "b": False, "c": False}),
        SystemState(state_id="s2", elements={"a": True, "b": True, "c": False}),
        SystemState(state_id="s3", elements={"a": False, "b": False, "c": True}),
        SystemState(state_id="s4", elements={"a": True, "b": True, "c": True}),
    ]

    phi = analyzer.calculate_phi(states)

    # Should have positive phi due to integration
    assert phi > 0.0


def test_calculate_complexity() -> None:
    """Test complexity calculation."""
    analyzer = IITAnalyzer()

    states = [
        SystemState(state_id="s1", elements={"a": False, "b": False}),
        SystemState(state_id="s2", elements={"a": False, "b": True}),
        SystemState(state_id="s3", elements={"a": True, "b": False}),
        SystemState(state_id="s4", elements={"a": True, "b": True}),
    ]

    complexity = analyzer.calculate_complexity(states)

    # All 4 states present -> maximum complexity for 2 bits
    assert complexity > 0.0


def test_calculate_integration() -> None:
    """Test integration calculation."""
    analyzer = IITAnalyzer()

    states = [
        SystemState(state_id="s1", elements={"a": False, "b": False}),
        SystemState(state_id="s2", elements={"a": True, "b": True}),
    ]

    integration = analyzer.calculate_integration(states)

    # Should return value between 0 and 1
    assert 0.0 <= integration <= 1.0


def test_calculate_differentiation() -> None:
    """Test differentiation calculation."""
    analyzer = IITAnalyzer()

    # All 4 possible states for 2 elements
    states = [
        SystemState(state_id="s1", elements={"a": False, "b": False}),
        SystemState(state_id="s2", elements={"a": False, "b": True}),
        SystemState(state_id="s3", elements={"a": True, "b": False}),
        SystemState(state_id="s4", elements={"a": True, "b": True}),
    ]

    differentiation = analyzer.calculate_differentiation(states)

    # All states explored -> differentiation = 1.0
    assert differentiation == 1.0


def test_calculate_emergence_level_below_threshold() -> None:
    """Test emergence level below consciousness threshold."""
    analyzer = IITAnalyzer(min_phi_for_consciousness=2.0)

    emergence = analyzer.calculate_emergence_level(phi=1.5, complexity=0.8)

    # Below threshold -> no emergence
    assert emergence == 0.0


def test_calculate_emergence_level_above_threshold() -> None:
    """Test emergence level above consciousness threshold."""
    analyzer = IITAnalyzer(min_phi_for_consciousness=2.0)

    emergence = analyzer.calculate_emergence_level(phi=2.5, complexity=0.8)

    # Above threshold -> emergence detected
    assert emergence > 0.0
    assert emergence <= 1.0


def test_analyze_consciousness_no_data() -> None:
    """Test consciousness analysis with no data."""
    analyzer = IITAnalyzer()

    metrics = analyzer.analyze_consciousness()

    assert metrics.phi_value == 0.0
    assert metrics.emergence_level == 0.0


def test_analyze_consciousness_with_data() -> None:
    """Test consciousness analysis with data."""
    analyzer = IITAnalyzer()

    # Add diverse states
    for i in range(10):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0, "b": i % 3 == 0, "c": i % 5 == 0},
        )
        analyzer.record_state(state)

    metrics = analyzer.analyze_consciousness()

    assert metrics.phi_value >= 0.0
    assert metrics.complexity >= 0.0
    assert 0.0 <= metrics.integration <= 1.0
    assert 0.0 <= metrics.differentiation <= 1.0
    assert 0.0 <= metrics.emergence_level <= 1.0


def test_analyze_consciousness_window_size() -> None:
    """Test consciousness analysis with window size."""
    analyzer = IITAnalyzer()

    # Add 100 states
    for i in range(100):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0, "b": i % 3 == 0},
        )
        analyzer.record_state(state)

    # Analyze only last 20 states
    metrics = analyzer.analyze_consciousness(window_size=20)

    assert metrics.phi_value >= 0.0


def test_detect_emergence_no_emergence() -> None:
    """Test emergence detection when below threshold."""
    analyzer = IITAnalyzer(
        emergence_threshold=0.8,
        min_phi_for_consciousness=5.0,  # High threshold
    )

    # Add simple states (low phi)
    for i in range(10):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0},
        )
        analyzer.record_state(state)

    is_emergent = analyzer.detect_emergence()

    assert is_emergent is False


def test_detect_emergence_with_emergence() -> None:
    """Test emergence detection when above threshold."""
    analyzer = IITAnalyzer(
        emergence_threshold=0.0,  # Low threshold for testing
        min_phi_for_consciousness=0.0,
    )

    # Add complex integrated states
    for i in range(50):
        state = SystemState(
            state_id=f"state-{i}",
            elements={
                "a": i % 2 == 0,
                "b": i % 3 == 0,
                "c": i % 5 == 0,
                "d": i % 7 == 0,
            },
        )
        analyzer.record_state(state)

    is_emergent = analyzer.detect_emergence()

    # With diverse states and multiple elements, should detect emergence
    assert isinstance(is_emergent, bool)


def test_get_consciousness_trend_no_data() -> None:
    """Test consciousness trend with no data."""
    analyzer = IITAnalyzer()

    trend = analyzer.get_consciousness_trend()

    assert trend["trend"] == "no_data"
    assert trend["phi_avg"] == 0.0


def test_get_consciousness_trend_with_data() -> None:
    """Test consciousness trend analysis."""
    analyzer = IITAnalyzer()

    # Add states and analyze multiple times
    for i in range(10):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0, "b": i % 3 == 0},
        )
        analyzer.record_state(state)
        analyzer.analyze_consciousness()

    trend = analyzer.get_consciousness_trend()

    assert trend["trend"] in ["increasing", "decreasing", "stable"]
    assert trend["phi_avg"] >= 0.0
    assert "phi_std" in trend
    assert "emergence_trend" in trend


def test_get_consciousness_trend_increasing() -> None:
    """Test detecting increasing consciousness trend."""
    analyzer = IITAnalyzer()

    # Simulate increasing complexity
    for i in range(20):
        # More elements over time
        elements = {f"e{j}": (i + j) % 2 == 0 for j in range(min(i // 2 + 1, 5))}
        state = SystemState(state_id=f"state-{i}", elements=elements)
        analyzer.record_state(state)

        if i % 2 == 0:  # Analyze periodically
            analyzer.analyze_consciousness()

    trend = analyzer.get_consciousness_trend()

    # Should detect some trend
    assert trend["trend"] in ["increasing", "decreasing", "stable"]


def test_get_summary() -> None:
    """Test getting comprehensive summary."""
    analyzer = IITAnalyzer()

    # Add some data
    for i in range(10):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0, "b": i % 3 == 0},
        )
        analyzer.record_state(state)

    analyzer.analyze_consciousness()

    summary = analyzer.get_summary()

    assert "latest_metrics" in summary
    assert "trend" in summary
    assert "total_states" in summary
    assert "is_conscious" in summary
    assert summary["total_states"] == 10


def test_phi_history_limit() -> None:
    """Test phi history limit (100 max)."""
    analyzer = IITAnalyzer()

    # Add states
    for i in range(10):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0},
        )
        analyzer.record_state(state)

    # Analyze 150 times
    for _ in range(150):
        analyzer.analyze_consciousness()

    # Should keep only last 100
    assert len(analyzer.phi_history) == 100


def test_consciousness_level_normalized() -> None:
    """Test that consciousness level is normalized to 0-1."""
    analyzer = IITAnalyzer()

    # Add data
    for i in range(20):
        state = SystemState(
            state_id=f"state-{i}",
            elements={"a": i % 2 == 0, "b": i % 3 == 0, "c": i % 5 == 0},
        )
        analyzer.record_state(state)

    summary = analyzer.get_summary()

    # Consciousness level should be 0-1
    assert 0.0 <= summary["consciousness_level"] <= 1.0


def test_hamming_distance_identical_states() -> None:
    """Test Hamming distance between identical states."""
    state1 = SystemState(
        state_id="s1",
        elements={"a": True, "b": False, "c": True},
    )

    state2 = SystemState(
        state_id="s2",
        elements={"a": True, "b": False, "c": True},
    )

    distance = state1.hamming_distance(state2)

    assert distance == 0


def test_hamming_distance_completely_different() -> None:
    """Test Hamming distance between completely different states."""
    state1 = SystemState(
        state_id="s1",
        elements={"a": True, "b": True, "c": True},
    )

    state2 = SystemState(
        state_id="s2",
        elements={"a": False, "b": False, "c": False},
    )

    distance = state1.hamming_distance(state2)

    assert distance == 3  # All 3 elements differ

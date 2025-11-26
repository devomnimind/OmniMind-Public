"""Tests for consciousness metrics module.

Tests:
- Φ (Phi) proxy calculation
- Self-awareness metrics
- Trend analysis
"""

from pathlib import Path
from typing import Generator

import pytest
import tempfile

from src.metrics.consciousness_metrics import (
    ConsciousnessMetrics,
    AgentConnection,
    FeedbackLoop,
    SelfAwarenessMetrics,
    calculate_phi_proxy,
    measure_self_awareness,
)


class TestAgentConnection:
    """Tests for AgentConnection dataclass."""

    def test_create_connection(self) -> None:
        """Test creating an agent connection."""
        conn = AgentConnection(
            source_agent="CodeAgent",
            target_agent="ReviewerAgent",
            connection_type="callback",
            bidirectional=True,
            weight=0.8,
        )

        assert conn.source_agent == "CodeAgent"
        assert conn.target_agent == "ReviewerAgent"
        assert conn.connection_type == "callback"
        assert conn.bidirectional is True
        assert conn.weight == 0.8


class TestFeedbackLoop:
    """Tests for FeedbackLoop dataclass."""

    def test_create_loop(self) -> None:
        """Test creating a feedback loop."""
        loop = FeedbackLoop(
            loop_id="metacognitive_001",
            agents_involved=["CodeAgent", "ReviewerAgent", "CodeAgent"],
            loop_type="metacognitive",
            iterations_count=5,
            avg_latency_ms=42.5,
        )

        assert loop.loop_id == "metacognitive_001"
        assert len(loop.agents_involved) == 3
        assert loop.loop_type == "metacognitive"
        assert loop.iterations_count == 5
        assert loop.avg_latency_ms == 42.5


class TestSelfAwarenessMetrics:
    """Tests for SelfAwarenessMetrics."""

    def test_calculate_overall_score(self) -> None:
        """Test overall score calculation."""
        metrics = SelfAwarenessMetrics(
            temporal_continuity_score=1.0,
            goal_autonomy_score=0.8,
            self_reference_score=0.9,
            limitation_awareness_score=0.7,
        )

        overall = metrics.calculate_overall()

        # Expected: 0.3*1.0 + 0.25*0.8 + 0.25*0.9 + 0.2*0.7
        # = 0.3 + 0.2 + 0.225 + 0.14 = 0.865
        assert pytest.approx(overall, 0.01) == 0.865
        assert pytest.approx(metrics.overall_score, 0.01) == 0.865

    def test_zero_scores(self) -> None:
        """Test with all zero scores."""
        metrics = SelfAwarenessMetrics()
        overall = metrics.calculate_overall()

        assert overall == 0.0


class TestConsciousnessMetrics:
    """Tests for ConsciousnessMetrics class."""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """Provide temporary directory for metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def metrics(self, temp_dir: Path) -> ConsciousnessMetrics:
        """Provide ConsciousnessMetrics instance."""
        return ConsciousnessMetrics(metrics_dir=temp_dir / "consciousness")

    def test_initialization(
        self, metrics: ConsciousnessMetrics, temp_dir: Path
    ) -> None:
        """Test metrics initialization."""
        assert metrics.metrics_dir.exists()
        assert len(metrics.connections) == 0
        assert len(metrics.feedback_loops) == 0
        assert len(metrics.history) == 0

    def test_add_connection(self, metrics: ConsciousnessMetrics) -> None:
        """Test adding connections."""
        conn = AgentConnection(
            source_agent="A",
            target_agent="B",
            connection_type="memory",
        )

        metrics.add_connection(conn)

        assert len(metrics.connections) == 1
        assert metrics.connections[0].source_agent == "A"

    def test_add_feedback_loop(self, metrics: ConsciousnessMetrics) -> None:
        """Test adding feedback loops."""
        loop = FeedbackLoop(
            loop_id="loop1",
            agents_involved=["A", "B"],
            loop_type="coordination",
        )

        metrics.add_feedback_loop(loop)

        assert len(metrics.feedback_loops) == 1
        assert metrics.feedback_loops[0].loop_id == "loop1"

    def test_calculate_phi_empty(self, metrics: ConsciousnessMetrics) -> None:
        """Test Phi calculation with no connections."""
        phi = metrics.calculate_phi_proxy()

        assert phi == 0.0

    def test_calculate_phi_simple(self, metrics: ConsciousnessMetrics) -> None:
        """Test Phi calculation with simple setup."""
        # Add 2 connections
        metrics.add_connection(
            AgentConnection("A", "B", "memory", bidirectional=False, weight=1.0)
        )
        metrics.add_connection(
            AgentConnection("B", "C", "message", bidirectional=True, weight=1.0)
        )

        # Add 1 feedback loop
        metrics.add_feedback_loop(
            FeedbackLoop("loop1", ["A", "B", "C"], "coordination", iterations_count=0)
        )

        phi = metrics.calculate_phi_proxy()

        # Expected calculation:
        # effective_connections = 1.0 + (1.0 * 1.5) = 2.5
        # effective_loops = 3 * 1 = 3
        # integration_factor = 1.0 + (1 * 0.1) = 1.1
        # phi = 2.5 * 3 * 1.1 = 8.25

        assert pytest.approx(phi, 0.01) == 8.25

    def test_calculate_phi_complex(self, metrics: ConsciousnessMetrics) -> None:
        """Test Phi with multiple connections and loops."""
        # 3 connections (2 bidirectional)
        for i in range(3):
            metrics.add_connection(
                AgentConnection(
                    f"Agent{i}",
                    f"Agent{i+1}",
                    "memory",
                    bidirectional=(i > 0),
                    weight=1.0,
                )
            )

        # 2 feedback loops
        metrics.add_feedback_loop(
            FeedbackLoop("loop1", ["A", "B"], "meta", iterations_count=5)
        )
        metrics.add_feedback_loop(
            FeedbackLoop("loop2", ["C", "D", "E"], "coord", iterations_count=2)
        )

        phi = metrics.calculate_phi_proxy()

        # effective_connections = 1.0 + 1.5 + 1.5 = 4.0
        # effective_loops = (2 * 6) + (3 * 3) = 12 + 9 = 21
        # integration = 1.0 + (2 * 0.1) = 1.2
        # phi = 4.0 * 21 * 1.2 = 100.8

        assert pytest.approx(phi, 0.1) == 100.8

    def test_measure_self_awareness(self, metrics: ConsciousnessMetrics) -> None:
        """Test self-awareness measurement."""
        result = metrics.measure_self_awareness(
            memory_test_passed=True,
            has_autonomous_goals=True,
            self_description_quality=0.85,
            limitation_acknowledgment=0.75,
        )

        assert result.temporal_continuity_score == 1.0
        assert result.goal_autonomy_score == 1.0
        assert result.self_reference_score == 0.85
        assert result.limitation_awareness_score == 0.75
        assert result.overall_score > 0.8

    def test_snapshot(self, metrics: ConsciousnessMetrics, temp_dir: Path) -> None:
        """Test taking a metrics snapshot."""
        # Add some data
        metrics.add_connection(AgentConnection("A", "B", "memory"))
        metrics.add_feedback_loop(FeedbackLoop("loop1", ["A", "B"], "coord"))

        snapshot = metrics.snapshot(label="test_snapshot")

        assert "timestamp" in snapshot
        assert snapshot["label"] == "test_snapshot"
        assert "phi_proxy" in snapshot
        assert snapshot["num_connections"] == 1
        assert snapshot["num_feedback_loops"] == 1

        # Check file was created
        snapshot_files = list((temp_dir / "consciousness").glob("*.json"))
        assert len(snapshot_files) == 1

    def test_get_trend_insufficient_data(self, metrics: ConsciousnessMetrics) -> None:
        """Test trend with insufficient data."""
        trend = metrics.get_trend()

        assert trend["trend"] == "insufficient_data"

    def test_get_trend_increasing(self, metrics: ConsciousnessMetrics) -> None:
        """Test trend detection - increasing."""
        # Simulate increasing Phi over time by adding feedback loops
        for i in range(5):
            for j in range(i + 1):
                metrics.add_connection(
                    AgentConnection(f"A{i}_{j}", f"B{i}_{j}", "memory")
                )
            # Add a feedback loop to make phi non-zero
            metrics.add_feedback_loop(
                FeedbackLoop(
                    f"loop_{i}", [f"A{i}_0", f"B{i}_0"], "coord", iterations_count=i
                )
            )
            metrics.snapshot(label=f"snapshot_{i}")

        trend = metrics.get_trend()

        assert trend["trend"] == "increasing"
        # Type guard: if trend is "increasing", it's TrendAnalysis
        assert "change_pct" in trend
        assert trend["change_pct"] > 0  # type: ignore[typeddict-item]


class TestStandaloneFunctions:
    """Tests for standalone helper functions."""

    def test_calculate_phi_proxy_standalone(self) -> None:
        """Test standalone phi calculation."""
        connections = [
            AgentConnection("A", "B", "memory", weight=1.0),
            AgentConnection("B", "C", "callback", bidirectional=True, weight=1.0),
        ]
        loops = [
            FeedbackLoop("loop1", ["A", "B"], "coord", iterations_count=0),
        ]

        phi = calculate_phi_proxy(connections, loops)

        # Expected calculation:
        # effective_connections = 1.0 + (1.0 * 1.5) = 2.5
        # effective_loops = 2 * 1 = 2  (2 agents, iterations+1=1)
        # integration_factor = 1.0 + (1 * 0.1) = 1.1
        # phi = 2.5 * 2 * 1.1 = 5.5
        assert pytest.approx(phi, 0.01) == 5.5

    def test_measure_self_awareness_standalone(self) -> None:
        """Test standalone self-awareness measurement."""
        result = measure_self_awareness(
            memory_test_passed=True,
            has_autonomous_goals=False,
            self_description_quality=0.6,
            limitation_acknowledgment=0.8,
        )

        assert result.temporal_continuity_score == 1.0
        assert result.goal_autonomy_score == 0.0
        assert result.self_reference_score == 0.6
        assert result.limitation_awareness_score == 0.8
        assert 0.0 < result.overall_score < 1.0

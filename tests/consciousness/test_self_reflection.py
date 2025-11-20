"""Tests for Advanced Self-Reflection (Phase 11.4)."""

import json
import tempfile
from pathlib import Path

import pytest

from src.consciousness.self_reflection import (
    AdvancedSelfReflection,
    IntrospectionLog,
    SelfReflectionMetrics,
)


class TestIntrospectionLog:
    """Tests for IntrospectionLog dataclass."""

    def test_create_introspection_log(self) -> None:
        """Test creating an introspection log."""
        from datetime import datetime

        log = IntrospectionLog(
            timestamp=datetime.now(),
            focus_area="decision_making",
            observations=["High success rate", "Tool diversity low"],
            insights=["Decision making is effective"],
            confidence=0.8,
            action_items=["Review tool usage"],
        )

        assert log.focus_area == "decision_making"
        assert len(log.observations) == 2
        assert len(log.insights) == 1
        assert log.confidence == 0.8

    def test_introspection_log_validation(self) -> None:
        """Test introspection log validation."""
        from datetime import datetime

        # Invalid confidence
        with pytest.raises(ValueError, match="Confidence"):
            IntrospectionLog(
                timestamp=datetime.now(),
                focus_area="test",
                observations=[],
                insights=[],
                confidence=1.5,
            )


class TestSelfReflectionMetrics:
    """Tests for SelfReflectionMetrics."""

    def test_create_metrics(self) -> None:
        """Test creating reflection metrics."""
        metrics = SelfReflectionMetrics(
            depth_score=0.8,
            breadth_score=0.7,
            actionability_score=0.9,
            consistency_score=0.75,
        )

        assert metrics.depth_score == 0.8
        assert metrics.breadth_score == 0.7
        assert metrics.actionability_score == 0.9

    def test_overall_quality(self) -> None:
        """Test calculating overall quality."""
        metrics = SelfReflectionMetrics(
            depth_score=0.8,
            breadth_score=0.6,
            actionability_score=0.9,
            consistency_score=0.7,
        )

        # Overall = 0.8*0.3 + 0.6*0.2 + 0.9*0.3 + 0.7*0.2 = 0.77
        assert abs(metrics.overall_quality - 0.77) < 0.01

    def test_metrics_validation(self) -> None:
        """Test metrics validation."""
        # Invalid depth score
        with pytest.raises(ValueError, match="depth_score"):
            SelfReflectionMetrics(
                depth_score=1.5,
                breadth_score=0.7,
                actionability_score=0.8,
                consistency_score=0.6,
            )


class TestAdvancedSelfReflection:
    """Tests for AdvancedSelfReflection engine."""

    @pytest.fixture
    def temp_hash_chain(self) -> Path:
        """Create a temporary hash chain file for testing."""
        from datetime import datetime, timedelta

        temp_dir = tempfile.mkdtemp()
        hash_chain_path = Path(temp_dir) / "hash_chain.json"

        # Create sample hash chain data with recent timestamps
        now = datetime.now()
        sample_data = {
            "entries": [
                {
                    "timestamp": (now - timedelta(hours=1)).isoformat(),
                    "tool_name": "test_tool",
                    "agent": "test_agent",
                    "success": True,
                    "duration": 1.5,
                },
                {
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                    "tool_name": "test_tool",
                    "agent": "test_agent",
                    "success": True,
                    "duration": 2.0,
                },
                {
                    "timestamp": (now - timedelta(minutes=10)).isoformat(),
                    "tool_name": "other_tool",
                    "agent": "other_agent",
                    "success": False,
                    "error": "Test error",
                },
            ]
        }

        with hash_chain_path.open("w") as f:
            json.dump(sample_data, f)

        return hash_chain_path

    def test_initialization(self, temp_hash_chain: Path) -> None:
        """Test advanced self-reflection initialization."""
        reflection = AdvancedSelfReflection(
            hash_chain_path=str(temp_hash_chain),
            reflection_depth="deep",
            min_confidence=0.7,
        )

        assert reflection.reflection_depth == "deep"
        assert reflection.min_confidence == 0.7

    def test_introspect_decision_making(self, temp_hash_chain: Path) -> None:
        """Test introspection on decision making."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        log = reflection.introspect(
            focus_area="decision_making",
            lookback_hours=24,
        )

        assert log.focus_area == "decision_making"
        assert len(log.observations) > 0
        assert log.confidence > 0.0

    def test_introspect_performance(self, temp_hash_chain: Path) -> None:
        """Test introspection on performance."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        log = reflection.introspect(
            focus_area="performance",
            lookback_hours=24,
        )

        assert log.focus_area == "performance"
        # Should have observations about tool performance
        assert log.confidence > 0.0

    def test_introspect_learning(self, temp_hash_chain: Path) -> None:
        """Test introspection on learning."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        log = reflection.introspect(
            focus_area="learning",
            lookback_hours=24,
        )

        assert log.focus_area == "learning"
        # Should analyze failure patterns
        assert log.confidence > 0.0

    def test_introspect_resource_usage(self, temp_hash_chain: Path) -> None:
        """Test introspection on resource usage."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        log = reflection.introspect(
            focus_area="resource_usage",
            lookback_hours=24,
        )

        assert log.focus_area == "resource_usage"
        assert log.confidence > 0.0

    def test_introspection_history(self, temp_hash_chain: Path) -> None:
        """Test that introspections are stored in history."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        # Perform multiple introspections
        reflection.introspect("decision_making")
        reflection.introspect("performance")

        assert len(reflection._introspection_logs) == 2

    def test_introspection_history_limit(self, temp_hash_chain: Path) -> None:
        """Test that introspection history is limited."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        # Generate more logs than limit (100)
        for i in range(110):
            reflection.introspect("decision_making")

        assert len(reflection._introspection_logs) == 100

    def test_evaluate_self_reflection_quality_no_history(
        self, temp_hash_chain: Path
    ) -> None:
        """Test evaluating quality with no history."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        metrics = reflection.evaluate_self_reflection_quality()

        # Should return zero scores
        assert metrics.depth_score == 0.0
        assert metrics.breadth_score == 0.0

    def test_evaluate_self_reflection_quality_with_history(
        self, temp_hash_chain: Path
    ) -> None:
        """Test evaluating quality with history."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        # Perform various introspections
        reflection.introspect("decision_making")
        reflection.introspect("performance")
        reflection.introspect("learning")

        metrics = reflection.evaluate_self_reflection_quality()

        # Should have non-zero scores
        assert metrics.depth_score > 0.0
        assert metrics.breadth_score > 0.0
        assert metrics.actionability_score >= 0.0
        assert metrics.consistency_score > 0.0

    def test_generate_self_improvement_plan(self, temp_hash_chain: Path) -> None:
        """Test generating self-improvement plan."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        plan = reflection.generate_self_improvement_plan(lookback_hours=24)

        assert "timestamp" in plan
        assert "current_quality" in plan
        assert "strengths" in plan
        assert "weaknesses" in plan
        assert "action_items" in plan
        assert "recommended_focus" in plan

    def test_improvement_plan_quality_metrics(self, temp_hash_chain: Path) -> None:
        """Test that improvement plan includes quality metrics."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        plan = reflection.generate_self_improvement_plan()

        quality = plan["current_quality"]
        assert "overall" in quality
        assert "depth" in quality
        assert "breadth" in quality
        assert "actionability" in quality
        assert "consistency" in quality

    def test_improvement_plan_action_items(self, temp_hash_chain: Path) -> None:
        """Test that improvement plan generates action items."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        plan = reflection.generate_self_improvement_plan()

        action_items = plan["action_items"]
        # Should have some action items
        assert isinstance(action_items, list)
        # Each action item should have required fields
        for item in action_items:
            assert "action" in item
            assert "area" in item
            assert "priority" in item

    def test_get_statistics(self, temp_hash_chain: Path) -> None:
        """Test getting statistics."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        # Perform some introspections
        reflection.introspect("decision_making")
        reflection.introspect("performance")

        stats = reflection.get_statistics()

        assert stats["total_introspections"] == 2
        assert "focus_area_distribution" in stats
        assert "average_confidence" in stats
        assert "timestamp" in stats

    def test_focus_area_distribution(self, temp_hash_chain: Path) -> None:
        """Test focus area distribution tracking."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        # Perform introspections on different areas
        reflection.introspect("decision_making")
        reflection.introspect("decision_making")
        reflection.introspect("performance")

        stats = reflection.get_statistics()

        distribution = stats["focus_area_distribution"]
        assert distribution["decision_making"] == 2
        assert distribution["performance"] == 1

    def test_reflection_quality_history(self, temp_hash_chain: Path) -> None:
        """Test that reflection quality is tracked over time."""
        reflection = AdvancedSelfReflection(hash_chain_path=str(temp_hash_chain))

        # Generate some introspections
        for _ in range(5):
            reflection.introspect("decision_making")

        # Evaluate quality multiple times
        metrics1 = reflection.evaluate_self_reflection_quality()
        metrics2 = reflection.evaluate_self_reflection_quality()

        # Should be stored in history
        assert len(reflection._reflection_history) == 2

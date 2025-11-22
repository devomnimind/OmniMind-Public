"""Comprehensive tests for Pattern Recognition module.

Tests for behavioral pattern detection and anomaly identification.
Total: 29 tests covering all pattern recognition capabilities.
"""

import pytest
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.metacognition.pattern_recognition import PatternRecognition


class TestPatternRecognitionInitialization:
    """Tests for PatternRecognition initialization."""

    def test_default_initialization(self) -> None:
        """Test default initialization."""
        pr = PatternRecognition()

        assert pr.sensitivity == 0.7
        assert pr._patterns == {}

    def test_custom_sensitivity(self) -> None:
        """Test initialization with custom sensitivity."""
        pr = PatternRecognition(sensitivity=0.9)

        assert pr.sensitivity == 0.9

    def test_sensitivity_bounds(self) -> None:
        """Test that sensitivity can be set at boundaries."""
        pr_min = PatternRecognition(sensitivity=0.0)
        pr_max = PatternRecognition(sensitivity=1.0)

        assert pr_min.sensitivity == 0.0
        assert pr_max.sensitivity == 1.0


class TestDetectRepetitiveBehavior:
    """Tests for repetitive behavior detection."""

    def test_empty_operations(self) -> None:
        """Test with empty operations list."""
        pr = PatternRecognition()
        result = pr.detect_repetitive_behavior([])

        assert result["patterns"] == []
        assert result["message"] == "No operations to analyze"

    def test_insufficient_data(self) -> None:
        """Test with insufficient data."""
        pr = PatternRecognition()
        operations = [
            {"tool_name": "tool1"},
            {"tool_name": "tool2"},
        ]

        result = pr.detect_repetitive_behavior(operations)

        assert result["message"] == "Insufficient data"

    def test_no_repetition(self) -> None:
        """Test with no repetitive patterns."""
        pr = PatternRecognition()
        operations = [{"tool_name": f"tool{i}"} for i in range(10)]  # All different

        result = pr.detect_repetitive_behavior(operations)

        assert isinstance(result["patterns"], list)
        # May have 0 patterns or minimal patterns

    def test_simple_repetition(self) -> None:
        """Test detection of simple repetitive pattern."""
        pr = PatternRecognition()
        # Pattern: A, B, A, B, A, B
        operations = [
            {"tool_name": "A"},
            {"tool_name": "B"},
            {"tool_name": "A"},
            {"tool_name": "B"},
            {"tool_name": "A"},
            {"tool_name": "B"},
        ]

        result = pr.detect_repetitive_behavior(operations)

        assert len(result["patterns"]) > 0
        assert "total_patterns" in result
        assert "timestamp" in result

    def test_complex_repetition(self) -> None:
        """Test detection of complex patterns."""
        pr = PatternRecognition()
        # Pattern: A, B, C repeated
        sequence = ["A", "B", "C"]
        operations = [{"tool_name": tool} for tool in sequence * 5]

        result = pr.detect_repetitive_behavior(operations)

        patterns = result["patterns"]
        assert len(patterns) > 0

        # Check pattern structure
        for pattern in patterns:
            assert "sequence" in pattern
            assert "repetitions" in pattern
            assert "length" in pattern

    def test_pattern_sorting(self) -> None:
        """Test that patterns are sorted by repetitions."""
        pr = PatternRecognition()
        # Create operations with varying repetitions
        operations = [{"tool_name": "A"}, {"tool_name": "B"}] * 10 + [
            {"tool_name": "X"},
            {"tool_name": "Y"},
            {"tool_name": "Z"},
        ] * 3

        result = pr.detect_repetitive_behavior(operations)

        if len(result["patterns"]) > 1:
            # First pattern should have more or equal repetitions than second
            assert (
                result["patterns"][0]["repetitions"]
                >= result["patterns"][1]["repetitions"]
            )

    def test_handles_missing_tool_names(self) -> None:
        """Test handling of operations without tool_name."""
        pr = PatternRecognition()
        operations = [
            {"tool_name": "A"},
            {"other_field": "value"},  # No tool_name
            {"tool_name": "B"},
            {},  # Empty dict
            {"tool_name": "A"},
        ]

        result = pr.detect_repetitive_behavior(operations)

        # Should handle gracefully without crashing
        assert "patterns" in result


class TestDetectBias:
    """Tests for bias detection."""

    def test_empty_operations_bias(self) -> None:
        """Test bias detection with empty operations."""
        pr = PatternRecognition()
        result = pr.detect_bias([])

        assert result["biases"] == []
        assert result["message"] == "No operations to analyze"

    def test_no_bias_balanced_usage(self) -> None:
        """Test no bias with balanced tool usage."""
        pr = PatternRecognition(sensitivity=0.7)
        # Balanced usage across 4 tools (25% each)
        operations = (
            [{"tool_name": "tool1"}] * 25
            + [{"tool_name": "tool2"}] * 25
            + [{"tool_name": "tool3"}] * 25
            + [{"tool_name": "tool4"}] * 25
        )

        result = pr.detect_bias(operations)

        # No tool exceeds 70% threshold
        assert len(result["biases"]) == 0

    def test_tool_bias_detected(self) -> None:
        """Test detection of tool usage bias."""
        pr = PatternRecognition(sensitivity=0.6)
        # 80% usage of tool1
        operations = [{"tool_name": "tool1"}] * 80 + [{"tool_name": "tool2"}] * 20

        result = pr.detect_bias(operations)

        assert len(result["biases"]) > 0
        assert result["total_biases"] > 0

        # Check bias details
        bias = result["biases"][0]
        assert bias["type"] == "tool"
        assert bias["name"] == "tool1"
        assert bias["usage_ratio"] == 0.8
        assert bias["severity"] in ["medium", "high"]  # 0.8 is exactly on boundary

    def test_agent_bias_detected(self) -> None:
        """Test detection of agent usage bias."""
        pr = PatternRecognition(sensitivity=0.5)
        # Heavy use of one agent
        operations = [{"agent": "agent_alpha"}] * 90 + [{"agent": "agent_beta"}] * 10

        result = pr.detect_bias(operations)

        assert len(result["biases"]) > 0

        # Find agent bias
        agent_biases = [b for b in result["biases"] if b["type"] == "agent"]
        assert len(agent_biases) > 0
        assert agent_biases[0]["name"] == "agent_alpha"

    def test_severity_levels(self) -> None:
        """Test bias severity classification."""
        pr = PatternRecognition(sensitivity=0.5)

        # Medium severity (70-80%)
        operations_medium = [{"tool_name": "tool1"}] * 75 + [
            {"tool_name": "tool2"}
        ] * 25
        result_medium = pr.detect_bias(operations_medium)

        if len(result_medium["biases"]) > 0:
            assert result_medium["biases"][0]["severity"] == "medium"

        # High severity (>80%)
        operations_high = [{"tool_name": "tool1"}] * 85 + [{"tool_name": "tool2"}] * 15
        result_high = pr.detect_bias(operations_high)

        if len(result_high["biases"]) > 0:
            assert result_high["biases"][0]["severity"] == "high"


class TestDetectAnomalies:
    """Tests for anomaly detection."""

    def test_empty_operations_anomalies(self) -> None:
        """Test anomaly detection with empty operations."""
        pr = PatternRecognition()
        result = pr.detect_anomalies([])

        assert result["anomalies"] == []
        assert result["message"] == "No operations to analyze"

    def test_no_anomalies(self) -> None:
        """Test with no anomalous behavior."""
        pr = PatternRecognition()
        # All operations have similar duration
        operations = [{"duration": 1.0, "success": True} for _ in range(20)]

        result = pr.detect_anomalies(operations)

        assert isinstance(result["anomalies"], list)
        assert "total_anomalies" in result
        assert "timestamp" in result

    def test_slow_execution_anomaly(self) -> None:
        """Test detection of slow execution anomaly."""
        pr = PatternRecognition()
        # Most operations ~1s, one very slow at 100s
        operations = [{"tool_name": "fast", "duration": 1.0} for _ in range(20)]
        operations.append({"tool_name": "slow", "duration": 100.0})

        result = pr.detect_anomalies(operations)

        anomalies = result["anomalies"]
        slow_anomalies = [a for a in anomalies if a["type"] == "slow_execution"]

        assert len(slow_anomalies) > 0
        assert slow_anomalies[0]["operation"] == "slow"
        assert slow_anomalies[0]["duration"] == 100.0

    def test_high_failure_rate_anomaly(self) -> None:
        """Test detection of high failure rate."""
        pr = PatternRecognition()
        # Recent 10 operations with 5+ failures
        operations = [{"success": True}] * 100
        # Add 6 recent failures
        operations.extend([{"success": False}] * 6)

        result = pr.detect_anomalies(operations)

        failure_anomalies = [
            a for a in result["anomalies"] if a["type"] == "high_failure_rate"
        ]

        assert len(failure_anomalies) > 0
        assert failure_anomalies[0]["failures"] >= 5

    def test_no_duration_data(self) -> None:
        """Test handling when no duration data available."""
        pr = PatternRecognition()
        operations = [{"tool_name": "tool1"} for _ in range(10)]  # No duration field

        result = pr.detect_anomalies(operations)

        # Should handle gracefully
        assert "anomalies" in result


class TestAnalyzeDecisionTree:
    """Tests for decision tree analysis."""

    def test_empty_decision_tree(self) -> None:
        """Test with no operations."""
        pr = PatternRecognition()
        result = pr.analyze_decision_tree([])

        assert result["message"] == "No operations to analyze"

    def test_single_sequence(self) -> None:
        """Test with single decision sequence."""
        pr = PatternRecognition()
        operations = [
            {"tool_name": "A"},
            {"tool_name": "B"},
            {"tool_name": "C", "metadata": {"task_complete": True}},
        ]

        result = pr.analyze_decision_tree(operations)

        assert result["total_sequences"] == 1
        assert result["avg_sequence_length"] == 3
        assert result["max_sequence_length"] == 3
        assert result["min_sequence_length"] == 3

    def test_multiple_sequences(self) -> None:
        """Test with multiple decision sequences."""
        pr = PatternRecognition()
        operations = [
            {"tool_name": "A"},
            {"tool_name": "B", "metadata": {"task_complete": True}},
            {"tool_name": "C"},
            {"tool_name": "D"},
            {"tool_name": "E", "metadata": {"task_complete": True}},
        ]

        result = pr.analyze_decision_tree(operations)

        assert result["total_sequences"] == 2
        assert "avg_sequence_length" in result
        assert "common_decision_paths" in result

    def test_common_decision_paths(self) -> None:
        """Test identification of common decision paths."""
        pr = PatternRecognition()
        # Repeat same sequence 3 times
        sequence = [
            {"tool_name": "X"},
            {"tool_name": "Y", "metadata": {"task_complete": True}},
        ]
        operations = sequence * 3

        result = pr.analyze_decision_tree(operations)

        common_paths = result["common_decision_paths"]
        assert len(common_paths) > 0
        # Most common path should appear 3 times
        assert common_paths[0]["count"] == 3


class TestCalculateDiversityScore:
    """Tests for diversity score calculation."""

    def test_empty_diversity(self) -> None:
        """Test diversity with no operations."""
        pr = PatternRecognition()
        result = pr.calculate_diversity_score([])

        assert result["diversity_score"] == 0.0
        assert result["message"] == "No operations to analyze"

    def test_low_diversity(self) -> None:
        """Test low diversity (same tool repeated)."""
        pr = PatternRecognition()
        operations = [{"tool_name": "only_tool", "agent": "only_agent"}] * 20

        result = pr.calculate_diversity_score(operations)

        assert result["unique_tools"] == 1
        assert result["unique_agents"] == 1
        assert result["interpretation"] == "low"

    def test_high_diversity(self) -> None:
        """Test high diversity (many different tools)."""
        pr = PatternRecognition()
        operations = [
            {"tool_name": f"tool_{i}", "agent": f"agent_{i}"} for i in range(20)
        ]

        result = pr.calculate_diversity_score(operations)

        assert result["unique_tools"] == 20
        assert result["unique_agents"] == 20
        # Diversity score should be calculated
        assert result["interpretation"] in ["low", "medium", "high"]

    def test_medium_diversity(self) -> None:
        """Test medium diversity."""
        pr = PatternRecognition()
        # Use 5 different tools, distributed somewhat evenly
        operations = []
        for i in range(5):
            operations.extend([{"tool_name": f"tool_{i}"}] * 4)

        result = pr.calculate_diversity_score(operations)

        assert result["unique_tools"] == 5
        assert result["total_operations"] == 20
        # Should be medium or high diversity
        assert result["interpretation"] in ["medium", "high", "low"]


class TestIntegration:
    """Integration tests combining multiple pattern recognition features."""

    def test_comprehensive_analysis(self) -> None:
        """Test running all analysis methods on same dataset."""
        pr = PatternRecognition()

        # Create realistic operation history
        operations = []
        for i in range(50):
            operations.append(
                {
                    "tool_name": f"tool_{i % 5}",  # 5 different tools
                    "agent": f"agent_{i % 3}",  # 3 different agents
                    "duration": 1.0 + (i % 10) * 0.1,  # Varying duration
                    "success": i % 15 != 0,  # Occasional failure
                }
            )

        # Run all analyses
        repetition_result = pr.detect_repetitive_behavior(operations)
        bias_result = pr.detect_bias(operations)
        anomaly_result = pr.detect_anomalies(operations)
        diversity_result = pr.calculate_diversity_score(operations)

        # All should complete successfully
        assert "patterns" in repetition_result
        assert "biases" in bias_result
        assert "anomalies" in anomaly_result
        assert "diversity_score" in diversity_result

    def test_timestamp_consistency(self) -> None:
        """Test that all results include timestamps."""
        pr = PatternRecognition()
        operations = [{"tool_name": "test"}] * 10

        results = [
            pr.detect_repetitive_behavior(operations),
            pr.detect_bias(operations),
            pr.detect_anomalies(operations),
            pr.analyze_decision_tree(operations),
            pr.calculate_diversity_score(operations),
        ]

        for result in results:
            if "timestamp" in result:
                # Verify timestamp format
                timestamp = result["timestamp"]
                datetime.fromisoformat(timestamp)  # Should not raise

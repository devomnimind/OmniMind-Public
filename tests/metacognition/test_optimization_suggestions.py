"""Comprehensive tests for Optimization Suggestions module.

Tests for generating actionable optimization suggestions.
Total: 29 tests covering all optimization analysis capabilities.
"""

from typing import Any, Dict

import pytest

from src.metacognition.optimization_suggestions import (
    OptimizationSuggestion,
    OptimizationSuggestions,
)


class TestOptimizationSuggestion:
    """Tests for OptimizationSuggestion class."""

    def test_suggestion_creation(self) -> None:
        """Test creating an optimization suggestion."""
        suggestion = OptimizationSuggestion(
            suggestion_id="OPT-001",
            category="performance",
            title="Optimize database queries",
            description="Database queries are slow",
            priority="high",
            impact="high",
            implementation="Add indexes to tables",
        )

        assert suggestion.suggestion_id == "OPT-001"
        assert suggestion.category == "performance"
        assert suggestion.title == "Optimize database queries"
        assert suggestion.priority == "high"
        assert suggestion.impact == "high"

    def test_suggestion_with_metrics(self) -> None:
        """Test suggestion with custom metrics."""
        metrics = {"current_time": 5.2, "target_time": 1.0}
        suggestion = OptimizationSuggestion(
            suggestion_id="OPT-002",
            category="efficiency",
            title="Reduce CPU usage",
            description="CPU usage is high",
            priority="medium",
            impact="medium",
            implementation="Optimize algorithms",
            metrics=metrics,
        )

        assert suggestion.metrics == metrics
        assert suggestion.metrics["current_time"] == pytest.approx(5.2)

    def test_suggestion_to_dict(self) -> None:
        """Test converting suggestion to dictionary."""
        suggestion = OptimizationSuggestion(
            suggestion_id="OPT-003",
            category="reliability",
            title="Improve error handling",
            description="Many failures detected",
            priority="critical",
            impact="high",
            implementation="Add retry logic",
        )

        result = suggestion.to_dict()

        assert result["suggestion_id"] == "OPT-003"
        assert result["category"] == "reliability"
        assert result["title"] == "Improve error handling"
        assert result["priority"] == "critical"
        assert "created_at" in result


class TestOptimizationSuggestionsInitialization:
    """Tests for OptimizationSuggestions initialization."""

    def test_default_initialization(self) -> None:
        """Test default initialization."""
        optimizer = OptimizationSuggestions()

        assert optimizer.max_suggestions == 10
        assert optimizer._suggestion_counter == 0

    def test_custom_max_suggestions(self) -> None:
        """Test initialization with custom max suggestions."""
        optimizer = OptimizationSuggestions(max_suggestions=5)

        assert optimizer.max_suggestions == 5

    def test_generate_id_format(self) -> None:
        """Test ID generation format."""
        optimizer = OptimizationSuggestions()

        id1 = optimizer._generate_id()
        id2 = optimizer._generate_id()

        assert id1.startswith("OPT-")
        assert id2.startswith("OPT-")
        assert id1 != id2  # IDs should be unique


class TestAnalyzePerformanceMetrics:
    """Tests for performance metrics analysis."""

    def test_no_slow_tools(self) -> None:
        """Test with no slow tools."""
        optimizer = OptimizationSuggestions()
        performance_data: Dict[str, Any] = {
            "tool_performance": {
                "tool1": {"avg": 0.5},
                "tool2": {"avg": 1.0},
            }
        }

        suggestions = optimizer.analyze_performance_metrics(performance_data)

        # No tools are slow (< 5s threshold)
        assert len(suggestions) == 0

    def test_one_slow_tool(self) -> None:
        """Test with one slow tool."""
        optimizer = OptimizationSuggestions()
        performance_data = {
            "tool_performance": {
                "fast_tool": {"avg": 1.0},
                "slow_tool": {"avg": 8.0},
            }
        }

        suggestions = optimizer.analyze_performance_metrics(performance_data)

        assert len(suggestions) == 1
        assert suggestions[0].category == "performance"
        assert "slow_tool" in suggestions[0].title

    def test_slow_tool_priority_high(self) -> None:
        """Test that very slow tools get high priority."""
        optimizer = OptimizationSuggestions()
        performance_data = {
            "tool_performance": {
                "very_slow": {"avg": 15.0},
            }
        }

        suggestions = optimizer.analyze_performance_metrics(performance_data)

        assert len(suggestions) == 1
        assert suggestions[0].priority == "high"

    def test_slow_tool_priority_medium(self) -> None:
        """Test that moderately slow tools get medium priority."""
        optimizer = OptimizationSuggestions()
        performance_data = {
            "tool_performance": {
                "somewhat_slow": {"avg": 7.0},
            }
        }

        suggestions = optimizer.analyze_performance_metrics(performance_data)

        assert len(suggestions) == 1
        assert suggestions[0].priority == "medium"

    def test_empty_performance_data(self) -> None:
        """Test with empty performance data."""
        optimizer = OptimizationSuggestions()
        performance_data: Dict[str, Any] = {"tool_performance": {}}

        suggestions = optimizer.analyze_performance_metrics(performance_data)

        assert len(suggestions) == 0


class TestAnalyzeFailurePatterns:
    """Tests for failure pattern analysis."""

    def test_no_failures(self) -> None:
        """Test with no failures."""
        optimizer = OptimizationSuggestions()
        failure_data = {
            "failure_by_tool": [],
            "total_failures": 0,
        }

        suggestions = optimizer.analyze_failure_patterns(failure_data)

        assert len(suggestions) == 0

    def test_low_failure_count(self) -> None:
        """Test with low failure counts (below threshold)."""
        optimizer = OptimizationSuggestions()
        failure_data = {
            "failure_by_tool": {"tool1": 2, "tool2": 3},
            "total_failures": 5,
        }

        suggestions = optimizer.analyze_failure_patterns(failure_data)

        # No tool has >= 5 failures
        assert len(suggestions) == 0

    def test_high_failure_count(self) -> None:
        """Test with high failure count."""
        optimizer = OptimizationSuggestions()
        failure_data = {
            "failure_by_tool": {"unreliable_tool": 8},
            "total_failures": 10,
        }

        suggestions = optimizer.analyze_failure_patterns(failure_data)

        assert len(suggestions) == 1
        assert suggestions[0].category == "reliability"
        assert "unreliable_tool" in suggestions[0].title

    def test_critical_priority_for_many_failures(self) -> None:
        """Test that many failures result in critical priority."""
        optimizer = OptimizationSuggestions()
        failure_data = {
            "failure_by_tool": {"bad_tool": 15},
            "total_failures": 20,
        }

        suggestions = optimizer.analyze_failure_patterns(failure_data)

        assert len(suggestions) == 1
        assert suggestions[0].priority == "critical"

    def test_high_priority_for_moderate_failures(self) -> None:
        """Test that moderate failures result in high priority."""
        optimizer = OptimizationSuggestions()
        failure_data = {
            "failure_by_tool": {"flaky_tool": 7},
            "total_failures": 15,
        }

        suggestions = optimizer.analyze_failure_patterns(failure_data)

        assert len(suggestions) == 1
        assert suggestions[0].priority == "high"


class TestAnalyzeBiasPatterns:
    """Tests for bias pattern analysis."""

    def test_no_biases(self) -> None:
        """Test with no detected biases."""
        optimizer = OptimizationSuggestions()
        bias_data: Dict[str, Any] = {"biases": []}

        suggestions = optimizer.analyze_bias_patterns(bias_data)

        assert len(suggestions) == 0

    def test_low_severity_bias(self) -> None:
        """Test with low severity bias (ignored)."""
        optimizer = OptimizationSuggestions()
        bias_data = {
            "biases": [
                {
                    "severity": "medium",
                    "type": "tool",
                    "name": "tool1",
                    "usage_ratio": 0.6,
                }
            ]
        }

        suggestions = optimizer.analyze_bias_patterns(bias_data)

        # Only high severity biases generate suggestions
        assert len(suggestions) == 0

    def test_high_severity_bias(self) -> None:
        """Test with high severity bias."""
        optimizer = OptimizationSuggestions()
        bias_data = {
            "biases": [
                {
                    "severity": "high",
                    "type": "tool",
                    "name": "overused_tool",
                    "usage_ratio": 0.85,
                }
            ]
        }

        suggestions = optimizer.analyze_bias_patterns(bias_data)

        assert len(suggestions) == 1
        assert suggestions[0].category == "diversity"
        assert "overused_tool" in suggestions[0].description

    def test_agent_bias_suggestion(self) -> None:
        """Test suggestion for agent bias."""
        optimizer = OptimizationSuggestions()
        bias_data = {
            "biases": [
                {
                    "severity": "high",
                    "type": "agent",
                    "name": "preferred_agent",
                    "usage_ratio": 0.9,
                }
            ]
        }

        suggestions = optimizer.analyze_bias_patterns(bias_data)

        assert len(suggestions) == 1
        assert "agent" in suggestions[0].description


class TestAnalyzeResourceUsage:
    """Tests for resource usage analysis."""

    def test_normal_resource_usage(self) -> None:
        """Test with normal resource usage."""
        optimizer = OptimizationSuggestions()
        resource_data = {
            "avg_cpu_percent": 50.0,
            "avg_memory_percent": 60.0,
        }

        suggestions = optimizer.analyze_resource_usage(resource_data)

        assert len(suggestions) == 0

    def test_high_cpu_usage(self) -> None:
        """Test with high CPU usage."""
        optimizer = OptimizationSuggestions()
        resource_data = {
            "avg_cpu_percent": 85.0,
            "avg_memory_percent": 50.0,
        }

        suggestions = optimizer.analyze_resource_usage(resource_data)

        assert len(suggestions) == 1
        assert suggestions[0].category == "efficiency"
        assert "CPU" in suggestions[0].title

    def test_high_memory_usage(self) -> None:
        """Test with high memory usage."""
        optimizer = OptimizationSuggestions()
        resource_data = {
            "avg_cpu_percent": 50.0,
            "avg_memory_percent": 87.0,
        }

        suggestions = optimizer.analyze_resource_usage(resource_data)

        assert len(suggestions) == 1
        assert suggestions[0].category == "efficiency"
        assert "memory" in suggestions[0].title

    def test_high_cpu_and_memory(self) -> None:
        """Test with both CPU and memory high."""
        optimizer = OptimizationSuggestions()
        resource_data = {
            "avg_cpu_percent": 85.0,
            "avg_memory_percent": 85.0,
        }

        suggestions = optimizer.analyze_resource_usage(resource_data)

        # Should generate suggestions for both
        assert len(suggestions) == 2

    def test_resource_suggestion_priority(self) -> None:
        """Test that resource suggestions have high priority."""
        optimizer = OptimizationSuggestions()
        resource_data = {
            "avg_cpu_percent": 85.0,
            "avg_memory_percent": 50.0,
        }

        suggestions = optimizer.analyze_resource_usage(resource_data)

        assert suggestions[0].priority == "high"
        assert suggestions[0].impact == "high"


class TestGenerateSuggestions:
    """Tests for comprehensive suggestion generation."""

    def test_generate_with_no_data(self) -> None:
        """Test generation with no data."""
        optimizer = OptimizationSuggestions()

        suggestions = optimizer.generate_suggestions()

        assert len(suggestions) == 0

    def test_generate_with_performance_data_only(self) -> None:
        """Test generation with only performance data."""
        optimizer = OptimizationSuggestions()
        performance_data = {
            "tool_performance": {
                "slow_tool": {"avg": 10.0},
            }
        }

        suggestions = optimizer.generate_suggestions(performance_data=performance_data)

        assert len(suggestions) == 1

    def test_generate_with_all_data(self) -> None:
        """Test generation with all types of data."""
        optimizer = OptimizationSuggestions()

        performance_data = {"tool_performance": {"slow_tool": {"avg": 8.0}}}
        failure_data = {"failure_by_tool": {"bad_tool": 6}, "total_failures": 10}
        bias_data = {
            "biases": [
                {
                    "severity": "high",
                    "type": "tool",
                    "name": "tool1",
                    "usage_ratio": 0.85,
                }
            ]
        }
        resource_data = {"avg_cpu_percent": 85.0, "avg_memory_percent": 50.0}

        suggestions = optimizer.generate_suggestions(
            performance_data=performance_data,
            failure_data=failure_data,
            bias_data=bias_data,
            resource_data=resource_data,
        )

        # Should have suggestions from all categories
        assert len(suggestions) >= 3

    def test_suggestions_sorted_by_priority(self) -> None:
        """Test that suggestions are sorted by priority."""
        optimizer = OptimizationSuggestions()

        # Create data that will generate different priorities
        performance_data = {"tool_performance": {"slow1": {"avg": 7.0}}}  # Medium
        failure_data = {
            "failure_by_tool": {"bad": 12},
            "total_failures": 15,
        }  # Critical

        suggestions = optimizer.generate_suggestions(
            performance_data=performance_data,
            failure_data=failure_data,
        )

        # Critical should come before medium
        priorities = [s["priority"] for s in suggestions]
        assert priorities[0] == "critical"

    def test_max_suggestions_limit(self) -> None:
        """Test that suggestions are limited to max_suggestions."""
        optimizer = OptimizationSuggestions(max_suggestions=2)

        # Generate data for many suggestions
        performance_data = {"tool_performance": {f"slow_tool_{i}": {"avg": 10.0} for i in range(5)}}

        suggestions = optimizer.generate_suggestions(performance_data=performance_data)

        # Should be limited to 2
        assert len(suggestions) <= 2

    def test_suggestion_dict_format(self) -> None:
        """Test that suggestions are returned as dictionaries."""
        optimizer = OptimizationSuggestions()
        performance_data = {"tool_performance": {"slow": {"avg": 10.0}}}

        suggestions = optimizer.generate_suggestions(performance_data=performance_data)

        assert isinstance(suggestions, list)
        assert all(isinstance(s, dict) for s in suggestions)


class TestIntegration:
    """Integration tests for optimization suggestions."""

    def test_complete_analysis_workflow(self) -> None:
        """Test complete analysis workflow."""
        optimizer = OptimizationSuggestions()

        # Realistic data
        performance_data = {
            "tool_performance": {
                "database_query": {"avg": 12.5},
                "api_call": {"avg": 0.8},
                "file_io": {"avg": 6.2},
            }
        }

        failure_data = {
            "failure_by_tool": {
                "network_request": 8,
                "cache_lookup": 2,
            },
            "total_failures": 15,
        }

        resource_data = {
            "avg_cpu_percent": 75.0,
            "avg_memory_percent": 82.0,
        }

        suggestions = optimizer.generate_suggestions(
            performance_data=performance_data,
            failure_data=failure_data,
            resource_data=resource_data,
        )

        # Should have multiple suggestions
        assert len(suggestions) > 0

        # All suggestions should have required fields
        for suggestion in suggestions:
            assert "suggestion_id" in suggestion
            assert "category" in suggestion
            assert "title" in suggestion
            assert "priority" in suggestion
            assert "implementation" in suggestion

    def test_id_uniqueness(self) -> None:
        """Test that generated IDs are unique."""
        optimizer = OptimizationSuggestions()

        performance_data = {"tool_performance": {f"tool{i}": {"avg": 10.0} for i in range(5)}}

        suggestions = optimizer.generate_suggestions(performance_data=performance_data)

        ids = [s["suggestion_id"] for s in suggestions]
        assert len(ids) == len(set(ids))  # All unique

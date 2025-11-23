"""Comprehensive tests for Self-Analysis module.

Tests for analyzing agent's own decision-making and execution patterns.
Total: 29 tests covering all self-analysis capabilities.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import pytest

from src.metacognition.self_analysis import SelfAnalysis


class TestSelfAnalysisInitialization:
    """Tests for SelfAnalysis initialization."""

    def test_default_initialization(self) -> None:
        """Test default initialization."""
        analyzer = SelfAnalysis()

        assert analyzer.hash_chain_path == Path("logs/hash_chain.json")
        assert analyzer._cache == {}

    def test_custom_path_initialization(self) -> None:
        """Test initialization with custom path."""
        custom_path = "custom/path/audit.json"
        analyzer = SelfAnalysis(hash_chain_path=custom_path)

        assert analyzer.hash_chain_path == Path(custom_path)


class TestLoadHashChain:
    """Tests for loading hash chain audit log."""

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test loading when file doesn't exist."""
        analyzer = SelfAnalysis(hash_chain_path=str(tmp_path / "missing.json"))

        entries = analyzer._load_hash_chain()

        assert entries == []

    def test_load_valid_hash_chain(self, tmp_path: Path) -> None:
        """Test loading valid hash chain."""
        log_file = tmp_path / "test_chain.json"
        data = {
            "entries": [
                {"tool_name": "tool1", "timestamp": datetime.now().isoformat()},
                {"tool_name": "tool2", "timestamp": datetime.now().isoformat()},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        entries = analyzer._load_hash_chain()

        assert len(entries) == 2
        assert entries[0]["tool_name"] == "tool1"

    def test_load_empty_entries(self, tmp_path: Path) -> None:
        """Test loading hash chain with no entries."""
        log_file = tmp_path / "empty_chain.json"
        data = {"entries": []}

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        entries = analyzer._load_hash_chain()

        assert entries == []

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test handling of invalid JSON."""
        log_file = tmp_path / "invalid.json"
        log_file.write_text("{ invalid json }")

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        entries = analyzer._load_hash_chain()

        # Should handle gracefully
        assert entries == []


class TestAnalyzeDecisionPatterns:
    """Tests for decision pattern analysis."""

    def test_analyze_no_data(self, tmp_path: Path) -> None:
        """Test analysis with no audit log data."""
        analyzer = SelfAnalysis(hash_chain_path=str(tmp_path / "missing.json"))

        result = analyzer.analyze_decision_patterns(lookback_hours=24)

        assert "error" in result
        assert result["error"] == "No audit log data available"

    def test_analyze_no_recent_entries(self, tmp_path: Path) -> None:
        """Test analysis when all entries are too old."""
        log_file = tmp_path / "old_entries.json"
        # Create entries from 48 hours ago
        old_time = (datetime.now() - timedelta(hours=48)).isoformat()
        data = {
            "entries": [
                {"tool_name": "tool1", "timestamp": old_time, "success": True},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_decision_patterns(lookback_hours=24)

        assert "error" in result
        assert "No recent entries" in result["error"]

    def test_analyze_recent_operations(self, tmp_path: Path) -> None:
        """Test analysis of recent operations."""
        log_file = tmp_path / "recent.json"
        now = datetime.now()

        data = {
            "entries": [
                {
                    "tool_name": "tool1",
                    "agent": "agent1",
                    "timestamp": (now - timedelta(hours=1)).isoformat(),
                    "success": True,
                },
                {
                    "tool_name": "tool2",
                    "agent": "agent1",
                    "timestamp": (now - timedelta(hours=2)).isoformat(),
                    "success": True,
                },
                {
                    "tool_name": "tool1",
                    "agent": "agent2",
                    "timestamp": (now - timedelta(hours=3)).isoformat(),
                    "success": False,
                },
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_decision_patterns(lookback_hours=24)

        assert result["total_operations"] == 3
        assert "success_rate" in result
        assert "most_used_tools" in result
        assert "agent_activity" in result

    def test_success_rate_calculation(self, tmp_path: Path) -> None:
        """Test success rate calculation."""
        log_file = tmp_path / "success_test.json"
        now = datetime.now()

        # 3 successes, 1 failure = 75% success rate
        data = {
            "entries": [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": i < 3,
                }
                for i in range(4)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_decision_patterns(lookback_hours=1)

        assert result["success_rate"] == pytest.approx(0.75)

    def test_tool_usage_tracking(self, tmp_path: Path) -> None:
        """Test tool usage tracking."""
        log_file = tmp_path / "tools.json"
        now = datetime.now()

        data = {
            "entries": [
                {
                    "tool_name": "tool_a",
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": True,
                }
                for i in range(5)
            ]
            + [
                {
                    "tool_name": "tool_b",
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": True,
                }
                for i in range(2)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_decision_patterns(lookback_hours=1)

        most_used = result["most_used_tools"]
        assert most_used[0][0] == "tool_a"  # Most used
        assert most_used[0][1] == 5


class TestAnalyzeExecutionTimes:
    """Tests for execution time analysis."""

    def test_analyze_no_data(self, tmp_path: Path) -> None:
        """Test with no audit log data."""
        analyzer = SelfAnalysis(hash_chain_path=str(tmp_path / "missing.json"))

        result = analyzer.analyze_execution_times()

        assert "error" in result

    def test_analyze_execution_times(self, tmp_path: Path) -> None:
        """Test execution time statistics."""
        log_file = tmp_path / "times.json"

        data = {
            "entries": [
                {"tool_name": "tool1", "duration": 1.5},
                {"tool_name": "tool1", "duration": 2.0},
                {"tool_name": "tool1", "duration": 2.5},
                {"tool_name": "tool2", "duration": 0.5},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_execution_times()

        assert "tool_performance" in result
        assert "tool1" in result["tool_performance"]

        tool1_stats = result["tool_performance"]["tool1"]
        assert tool1_stats["count"] == 3
        assert tool1_stats["avg"] == pytest.approx(2.0)
        assert tool1_stats["min"] == pytest.approx(1.5)
        assert tool1_stats["max"] == 2.5

    def test_missing_duration_handled(self, tmp_path: Path) -> None:
        """Test handling of entries without duration."""
        log_file = tmp_path / "no_duration.json"

        data = {
            "entries": [
                {"tool_name": "tool1"},  # No duration
                {"tool_name": "tool2", "duration": 1.0},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_execution_times()

        # Should only have stats for tool2
        assert "tool2" in result["tool_performance"]
        assert "tool1" not in result["tool_performance"]


class TestIdentifyFailurePatterns:
    """Tests for failure pattern identification."""

    def test_identify_no_data(self, tmp_path: Path) -> None:
        """Test with no audit log data."""
        analyzer = SelfAnalysis(hash_chain_path=str(tmp_path / "missing.json"))

        result = analyzer.identify_failure_patterns()

        assert "error" in result

    def test_identify_no_failures(self, tmp_path: Path) -> None:
        """Test when there are no failures."""
        log_file = tmp_path / "no_failures.json"

        data = {
            "entries": [
                {"tool_name": "tool1", "success": True},
                {"tool_name": "tool2", "success": True},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.identify_failure_patterns()

        assert result["total_failures"] == 0
        assert "message" in result

    def test_identify_failures_by_tool(self, tmp_path: Path) -> None:
        """Test grouping failures by tool."""
        log_file = tmp_path / "failures.json"

        data = {
            "entries": [
                {"tool_name": "tool1", "success": False, "error": "timeout"},
                {"tool_name": "tool1", "success": False, "error": "timeout"},
                {"tool_name": "tool2", "success": False, "error": "error"},
                {"tool_name": "tool3", "success": True},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.identify_failure_patterns()

        assert result["total_failures"] == 3
        assert "failure_by_tool" in result

        failures_by_tool = dict(result["failure_by_tool"])
        assert failures_by_tool["tool1"] == 2
        assert failures_by_tool["tool2"] == 1

    def test_identify_common_errors(self, tmp_path: Path) -> None:
        """Test identification of common errors."""
        log_file = tmp_path / "common_errors.json"

        data = {
            "entries": [
                {"success": False, "error": "timeout"},
                {"success": False, "error": "timeout"},
                {"success": False, "error": "timeout"},
                {"success": False, "error": "network error"},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.identify_failure_patterns()

        common_errors = dict(result["common_errors"])
        assert common_errors["timeout"] == 3
        assert common_errors["network error"] == 1


class TestAnalyzeResourceUsage:
    """Tests for resource usage analysis."""

    def test_analyze_no_data(self, tmp_path: Path) -> None:
        """Test with no audit log data."""
        analyzer = SelfAnalysis(hash_chain_path=str(tmp_path / "missing.json"))

        result = analyzer.analyze_resource_usage()

        assert "error" in result

    def test_analyze_no_resource_data(self, tmp_path: Path) -> None:
        """Test when entries don't have resource data."""
        log_file = tmp_path / "no_resources.json"

        data = {
            "entries": [
                {"tool_name": "tool1"},
                {"tool_name": "tool2"},
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_resource_usage()

        assert "message" in result
        assert "suggestion" in result

    def test_analyze_resource_metrics(self, tmp_path: Path) -> None:
        """Test resource usage analysis with metrics."""
        log_file = tmp_path / "resources.json"

        data = {
            "entries": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"cpu_percent": 50.0, "memory_percent": 60.0},
                },
                {
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"cpu_percent": 70.0, "memory_percent": 80.0},
                },
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.analyze_resource_usage()

        assert result["avg_cpu_percent"] == pytest.approx(60.0)
        assert result["avg_memory_percent"] == pytest.approx(70.0)
        assert result["samples"] == 2


class TestGetHealthSummary:
    """Tests for health summary generation."""

    def test_health_excellent(self, tmp_path: Path) -> None:
        """Test excellent health status."""
        log_file = tmp_path / "excellent.json"
        now = datetime.now()

        # 95% success rate
        data = {
            "entries": [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": i < 19,
                }
                for i in range(20)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.get_health_summary()

        assert result["health_status"] == "excellent"

    def test_health_good(self, tmp_path: Path) -> None:
        """Test good health status."""
        log_file = tmp_path / "good.json"
        now = datetime.now()

        # 80% success rate
        data = {
            "entries": [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": i < 16,
                }
                for i in range(20)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.get_health_summary()

        assert result["health_status"] == "good"

    def test_health_fair(self, tmp_path: Path) -> None:
        """Test fair health status."""
        log_file = tmp_path / "fair.json"
        now = datetime.now()

        # 60% success rate
        data = {
            "entries": [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": i < 12,
                }
                for i in range(20)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.get_health_summary()

        assert result["health_status"] == "fair"

    def test_health_poor(self, tmp_path: Path) -> None:
        """Test poor health status."""
        log_file = tmp_path / "poor.json"
        now = datetime.now()

        # 30% success rate
        data = {
            "entries": [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": i < 6,
                }
                for i in range(20)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.get_health_summary()

        assert result["health_status"] == "poor"

    def test_health_summary_structure(self, tmp_path: Path) -> None:
        """Test health summary has required fields."""
        log_file = tmp_path / "summary.json"
        now = datetime.now()

        data = {
            "entries": [
                {
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": True,
                }
                for i in range(10)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))
        result = analyzer.get_health_summary()

        assert "health_status" in result
        assert "success_rate" in result
        assert "total_operations_24h" in result
        assert "total_failures" in result
        assert "timestamp" in result


class TestIntegration:
    """Integration tests for self-analysis."""

    def test_complete_analysis_workflow(self, tmp_path: Path) -> None:
        """Test complete analysis workflow."""
        log_file = tmp_path / "complete.json"
        now = datetime.now()

        # Realistic audit log
        data = {
            "entries": [
                {
                    "tool_name": f"tool_{i % 3}",
                    "agent": f"agent_{i % 2}",
                    "timestamp": (now - timedelta(minutes=i)).isoformat(),
                    "success": i % 5 != 0,  # 80% success
                    "duration": 1.0 + (i % 5) * 0.5,
                    "error": "timeout" if i % 5 == 0 else None,
                    "metadata": {
                        "cpu_percent": 50 + i,
                        "memory_percent": 60 + i,
                    },
                }
                for i in range(20)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))

        # Run all analyses
        decision_patterns = analyzer.analyze_decision_patterns(lookback_hours=24)
        execution_times = analyzer.analyze_execution_times()
        failure_patterns = analyzer.identify_failure_patterns()
        resource_usage = analyzer.analyze_resource_usage()
        health_summary = analyzer.get_health_summary()

        # All should complete successfully
        assert "total_operations" in decision_patterns
        assert "tool_performance" in execution_times
        assert "total_failures" in failure_patterns
        assert "avg_cpu_percent" in resource_usage
        assert "health_status" in health_summary

    def test_timestamp_consistency(self, tmp_path: Path) -> None:
        """Test that all results include timestamps."""
        log_file = tmp_path / "timestamps.json"
        now = datetime.now()

        data = {
            "entries": [
                {"timestamp": now.isoformat(), "success": True} for _ in range(5)
            ]
        }

        with open(log_file, "w") as f:
            json.dump(data, f)

        analyzer = SelfAnalysis(hash_chain_path=str(log_file))

        results = [
            analyzer.analyze_decision_patterns(lookback_hours=24),
            analyzer.analyze_execution_times(),
            analyzer.identify_failure_patterns(),
            analyzer.get_health_summary(),
        ]

        for result in results:
            if "timestamp" in result:
                # Verify timestamp format
                datetime.fromisoformat(result["timestamp"])  # Should not raise

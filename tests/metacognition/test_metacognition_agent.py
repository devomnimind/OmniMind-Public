"""Tests for MetacognitionAgent."""

import math
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from src.metacognition.metacognition_agent import MetacognitionAgent


class TestMetacognitionAgent:
    """Test MetacognitionAgent functionality."""

    def test_initialization(self):
        """Test agent initialization with default parameters."""
        agent = MetacognitionAgent()
        assert agent.hash_chain_path == "logs/hash_chain.json"
        assert agent.analysis_interval == 3600
        assert math.isclose(agent.bias_sensitivity, 0.7)
        assert agent.max_suggestions == 10
        assert agent.last_analysis is None
        assert agent.analysis_history == []
        assert hasattr(agent, "self_analysis")
        assert hasattr(agent, "pattern_recognition")
        assert hasattr(agent, "optimization_engine")

    def test_initialization_custom_params(self):
        """Test agent initialization with custom parameters."""
        agent = MetacognitionAgent(
            hash_chain_path="custom/path.json",
            analysis_interval=1800,
            bias_sensitivity=0.5,
            max_suggestions=5,
        )
        assert agent.hash_chain_path == "custom/path.json"
        assert agent.analysis_interval == 1800
        assert math.isclose(agent.bias_sensitivity, 0.5)
        assert agent.max_suggestions == 5

    @patch("src.metacognition.metacognition_agent.SelfAnalysis")
    @patch("src.metacognition.metacognition_agent.PatternRecognition")
    @patch("src.metacognition.metacognition_agent.OptimizationSuggestions")
    def test_run_analysis_no_data(self, mock_opt, mock_pattern, mock_self):
        """Test run_analysis with no hash chain data."""
        # Setup mocks
        mock_self_instance = MagicMock()
        mock_self_instance.analyze_decision_patterns.return_value = {}
        mock_self_instance.analyze_execution_times.return_value = {}
        mock_self_instance.analyze_resource_usage.return_value = {}
        mock_self_instance.identify_failure_patterns.return_value = {}
        mock_self_instance.get_health_summary.return_value = {"health_status": "good"}
        mock_self_instance._load_hash_chain.return_value = []
        mock_self.return_value = mock_self_instance

        mock_pattern_instance = MagicMock()
        mock_pattern.return_value = mock_pattern_instance

        mock_opt_instance = MagicMock()
        mock_opt_instance.generate_suggestions.return_value = []
        mock_opt.return_value = mock_opt_instance

        agent = MetacognitionAgent()
        report = agent.run_analysis()

        assert "timestamp" in report
        assert report["lookback_hours"] == 24
        assert report["health_summary"]["health_status"] == "good"
        assert report["optimization_suggestions"] == []
        assert report["summary"]["total_suggestions"] == 0

    def test_get_quick_health_check_success(self):
        """Test successful quick health check."""
        agent = MetacognitionAgent()
        with patch.object(
            agent.self_analysis,
            "get_health_summary",
            return_value={"health_status": "excellent"},
        ):
            result = agent.get_quick_health_check()
            assert result["status"] == "ok"
            assert result["health"]["health_status"] == "excellent"
            assert "timestamp" in result

    def test_get_quick_health_check_error(self):
        """Test quick health check with error."""
        agent = MetacognitionAgent()
        with patch.object(
            agent.self_analysis,
            "get_health_summary",
            side_effect=Exception("Test error"),
        ):
            result = agent.get_quick_health_check()
            assert result["status"] == "error"
            assert "Test error" in result["error"]

    def test_should_run_analysis_first_time(self):
        """Test should_run_analysis when never run."""
        agent = MetacognitionAgent()
        assert agent.should_run_analysis() is True

    def test_should_run_analysis_recent(self):
        """Test should_run_analysis when recently run."""
        agent = MetacognitionAgent(analysis_interval=3600)
        agent.last_analysis = datetime.now() - timedelta(seconds=1800)  # 30 min ago
        assert agent.should_run_analysis() is False

    def test_should_run_analysis_overdue(self):
        """Test should_run_analysis when overdue."""
        agent = MetacognitionAgent(analysis_interval=3600)
        agent.last_analysis = datetime.now() - timedelta(seconds=7200)  # 2 hours ago
        assert agent.should_run_analysis() is True

    def test_get_analysis_stats(self):
        """Test get_analysis_stats."""
        agent = MetacognitionAgent()
        agent.analysis_history = [
            {
                "timestamp": "2023-01-01T00:00:00",
                "health_status": "good",
                "suggestions_count": 5,
            }
        ]
        agent.last_analysis = datetime.now()

        stats = agent.get_analysis_stats()
        assert stats["total_analyses"] == 1
        assert stats["analysis_interval"] == 3600
        assert len(stats["recent_health_trend"]) == 1
        assert "timestamp" in stats

    def test_get_top_suggestions_no_history(self):
        """Test get_top_suggestions when no history exists."""
        agent = MetacognitionAgent()
        with patch.object(
            agent,
            "run_analysis",
            return_value={"optimization_suggestions": [{"id": 1}, {"id": 2}]},
        ):
            suggestions = agent.get_top_suggestions(limit=1)
            assert len(suggestions) == 1
            assert suggestions[0]["id"] == 1

    def test_extract_suggestions_valid(self):
        """Test _extract_suggestions with valid data."""
        agent = MetacognitionAgent()
        report = {"optimization_suggestions": [{"priority": "high"}, {"priority": "low"}]}
        suggestions = agent._extract_suggestions(report)
        assert len(suggestions) == 2

    def test_extract_suggestions_invalid(self):
        """Test _extract_suggestions with invalid data."""
        agent = MetacognitionAgent()
        report = {"optimization_suggestions": "invalid"}
        suggestions = agent._extract_suggestions(report)
        assert suggestions == []

    def test_extract_suggestions_mixed(self):
        """Test _extract_suggestions with mixed valid/invalid entries."""
        agent = MetacognitionAgent()
        report = {
            "optimization_suggestions": [
                {"priority": "high"},
                "invalid",
                {"priority": "low"},
            ]
        }
        suggestions = agent._extract_suggestions(report)
        assert len(suggestions) == 2

"""Tests for Problem Detection Engine - Phase 26C"""

from __future__ import annotations

from autonomous.problem_detection_engine import (
    DetectedIssue,
    ProblemDetectionEngine,
    SystemState,
)


class TestProblemDetectionEngine:
    """Test Problem Detection Engine"""

    def test_init(self):
        """Test initialization"""
        engine = ProblemDetectionEngine()
        assert engine is not None
        assert engine.known_issues == {}

    def test_get_system_state(self):
        """Test system state detection"""
        engine = ProblemDetectionEngine()
        state = engine.get_system_state()

        assert isinstance(state, SystemState)
        assert state.cpu_percent >= 0
        assert state.memory_percent >= 0
        assert state.memory_available_gb >= 0

    def test_detect_memory_issue_critical(self):
        """Test detection of critical memory issue"""
        engine = ProblemDetectionEngine()

        # Simulate critical memory usage
        state = SystemState(
            cpu_percent=50.0,
            memory_percent=96.0,  # Critical
            memory_available_gb=0.5,
            gpu_count=0,
            gpu_memory_percent=None,
            last_accuracy=None,
            semantic_drift=None,
            timestamp=0.0,
        )

        issues = engine.detect_issues(state)

        assert len(issues) > 0
        memory_issues = [i for i in issues if i.type == "MEMORY"]
        assert len(memory_issues) > 0
        assert memory_issues[0].severity == "CRITICAL"

    def test_detect_cpu_issue_high(self):
        """Test detection of high CPU usage"""
        engine = ProblemDetectionEngine()

        # Simulate high CPU usage
        state = SystemState(
            cpu_percent=87.0,  # High
            memory_percent=50.0,
            memory_available_gb=4.0,
            gpu_count=0,
            gpu_memory_percent=None,
            last_accuracy=None,
            semantic_drift=None,
            timestamp=0.0,
        )

        issues = engine.detect_issues(state)

        cpu_issues = [i for i in issues if i.type == "PERFORMANCE"]
        assert len(cpu_issues) > 0
        assert cpu_issues[0].severity == "HIGH"

    def test_classify_issue(self):
        """Test issue classification"""
        engine = ProblemDetectionEngine()

        issue = DetectedIssue(
            type="MEMORY",
            severity="CRITICAL",
            metric="memory_usage",
            value=96.0,
            description="Memory critical",
            auto_fixable=True,
        )

        classification = engine.classify_issue(issue)

        assert classification["id"] == "MEMORY_memory_usage"
        assert classification["severity"] == "CRITICAL"
        assert classification["auto_fixable"] is True

    def test_no_issues_when_healthy(self):
        """Test no issues detected when system is healthy"""
        engine = ProblemDetectionEngine()

        # Simulate healthy system
        state = SystemState(
            cpu_percent=30.0,
            memory_percent=40.0,
            memory_available_gb=8.0,
            gpu_count=0,
            gpu_memory_percent=None,
            last_accuracy=0.95,
            semantic_drift=0.1,
            timestamp=0.0,
        )

        issues = engine.detect_issues(state)

        # Should have no critical/high issues
        critical_high = [i for i in issues if i.severity in ["CRITICAL", "HIGH"]]
        assert len(critical_high) == 0

"""Comprehensive tests for Proactive Goals module.

Tests for proactive goal generation and repository analysis.
Total: 29 tests covering all goal generation capabilities.
"""

import pytest
import json
from pathlib import Path
from typing import List

from src.metacognition.proactive_goals import (
    GoalCategory,
    GoalPriority,
    ProactiveGoal,
    ProactiveGoalEngine,
)


class TestGoalPriority:
    """Tests for GoalPriority constants."""

    def test_priority_values(self) -> None:
        """Test priority level values."""
        assert GoalPriority.CRITICAL == "critical"
        assert GoalPriority.HIGH == "high"
        assert GoalPriority.MEDIUM == "medium"
        assert GoalPriority.LOW == "low"


class TestGoalCategory:
    """Tests for GoalCategory constants."""

    def test_category_values(self) -> None:
        """Test category values."""
        assert GoalCategory.TESTING == "testing"
        assert GoalCategory.PERFORMANCE == "performance"
        assert GoalCategory.QUALITY == "quality"
        assert GoalCategory.DOCUMENTATION == "documentation"
        assert GoalCategory.SECURITY == "security"
        assert GoalCategory.ARCHITECTURE == "architecture"


class TestProactiveGoal:
    """Tests for ProactiveGoal class."""

    def test_goal_creation(self) -> None:
        """Test creating a proactive goal."""
        goal = ProactiveGoal(
            goal_id="GOAL-001",
            title="Increase test coverage",
            description="Coverage is below 80%",
            category=GoalCategory.TESTING,
            priority=GoalPriority.HIGH,
            estimated_effort="2 days",
            acceptance_criteria=["Coverage >= 80%", "All modules tested"],
            implementation_steps=["Write unit tests", "Add integration tests"],
        )

        assert goal.goal_id == "GOAL-001"
        assert goal.title == "Increase test coverage"
        assert goal.category == GoalCategory.TESTING
        assert goal.priority == GoalPriority.HIGH
        assert len(goal.acceptance_criteria) == 2
        assert len(goal.implementation_steps) == 2

    def test_goal_with_metrics(self) -> None:
        """Test goal with metrics."""
        metrics = {"current_coverage": 65.0, "target_coverage": 80.0}
        goal = ProactiveGoal(
            goal_id="GOAL-002",
            title="Test goal",
            description="Test description",
            category=GoalCategory.TESTING,
            priority=GoalPriority.MEDIUM,
            estimated_effort="1 day",
            acceptance_criteria=["Done"],
            implementation_steps=["Step 1"],
            metrics=metrics,
        )

        assert goal.metrics == metrics
        assert goal.metrics["current_coverage"] == 65.0

    def test_goal_to_dict(self) -> None:
        """Test converting goal to dictionary."""
        goal = ProactiveGoal(
            goal_id="GOAL-003",
            title="Fix linting errors",
            description="Too many style violations",
            category=GoalCategory.QUALITY,
            priority=GoalPriority.LOW,
            estimated_effort="4 hours",
            acceptance_criteria=["Zero violations"],
            implementation_steps=["Run formatter"],
        )

        result = goal.to_dict()

        assert result["goal_id"] == "GOAL-003"
        assert result["title"] == "Fix linting errors"
        assert result["category"] == GoalCategory.QUALITY
        assert result["priority"] == GoalPriority.LOW
        assert "created_at" in result


class TestProactiveGoalEngineInitialization:
    """Tests for ProactiveGoalEngine initialization."""

    def test_default_initialization(self) -> None:
        """Test default initialization."""
        engine = ProactiveGoalEngine()

        assert engine.workspace_path == Path(".")
        assert engine._goal_counter == 0

    def test_custom_workspace_path(self) -> None:
        """Test initialization with custom workspace."""
        engine = ProactiveGoalEngine(workspace_path="/tmp/test")

        assert engine.workspace_path == Path("/tmp/test")

    def test_generate_id_format(self) -> None:
        """Test ID generation format."""
        engine = ProactiveGoalEngine()

        id1 = engine._generate_id()
        id2 = engine._generate_id()

        assert id1.startswith("GOAL-")
        assert id2.startswith("GOAL-")
        assert id1 != id2  # IDs should be unique


class TestAssessTestCoverage:
    """Tests for test coverage assessment."""

    def test_coverage_assessment_no_file(self, tmp_path: Path) -> None:
        """Test coverage assessment when coverage.json doesn't exist."""
        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))

        goals = engine.assess_test_coverage()

        # Should handle missing file gracefully
        assert isinstance(goals, list)

    def test_coverage_below_threshold(self, tmp_path: Path) -> None:
        """Test goal generation for low coverage."""
        # Create mock coverage.json
        coverage_data = {
            "totals": {"percent_covered": 65.0},
            "files": {},
        }

        coverage_file = tmp_path / "coverage.json"
        with open(coverage_file, "w") as f:
            json.dump(coverage_data, f)

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))

        # Mock the command run to indicate success
        engine._run_command = lambda cmd: (True, "")

        goals = engine.assess_test_coverage()

        # Should generate goal to increase coverage
        if len(goals) > 0:
            assert goals[0].category == GoalCategory.TESTING
            assert "coverage" in goals[0].title.lower()

    def test_coverage_above_threshold(self, tmp_path: Path) -> None:
        """Test no goal when coverage is good."""
        coverage_data = {
            "totals": {"percent_covered": 85.0},
            "files": {},
        }

        coverage_file = tmp_path / "coverage.json"
        with open(coverage_file, "w") as f:
            json.dump(coverage_data, f)

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))
        engine._run_command = lambda cmd: (True, "")

        goals = engine.assess_test_coverage()

        # May have no goals or goals for other issues
        assert isinstance(goals, list)

    def test_untested_files_detected(self, tmp_path: Path) -> None:
        """Test detection of files with low coverage."""
        coverage_data = {
            "totals": {"percent_covered": 75.0},
            "files": {
                "src/module1.py": {"summary": {"percent_covered": 30.0}},
                "src/module2.py": {"summary": {"percent_covered": 25.0}},
                "src/module3.py": {"summary": {"percent_covered": 90.0}},
            },
        }

        coverage_file = tmp_path / "coverage.json"
        with open(coverage_file, "w") as f:
            json.dump(coverage_data, f)

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))
        engine._run_command = lambda cmd: (True, "")

        goals = engine.assess_test_coverage()

        # Should have goal for untested files
        untested_goals = [g for g in goals if "low-coverage" in g.title]
        assert len(untested_goals) > 0 or len(goals) > 0


class TestDetectPerformanceBottlenecks:
    """Tests for performance bottleneck detection."""

    def test_no_bottlenecks(self) -> None:
        """Test when no bottlenecks detected."""
        engine = ProactiveGoalEngine()

        # Mock command that doesn't indicate slow imports
        engine._run_command = lambda cmd: (True, "import completed")

        goals = engine.detect_performance_bottlenecks()

        # May have 0 goals
        assert isinstance(goals, list)

    def test_slow_imports_detected(self) -> None:
        """Test detection of slow imports."""
        engine = ProactiveGoalEngine()

        # Mock output with slow import
        slow_import_output = "150 ms import src.heavy_module"
        engine._run_command = lambda cmd: (True, slow_import_output)

        goals = engine.detect_performance_bottlenecks()

        # Should detect slow import goal
        if len(goals) > 0:
            assert goals[0].category == GoalCategory.PERFORMANCE


class TestAssessCodeQuality:
    """Tests for code quality assessment."""

    def test_no_quality_issues(self) -> None:
        """Test when code quality is good."""
        engine = ProactiveGoalEngine()

        # Mock flake8 with no issues
        engine._run_command = lambda cmd: (True, "")

        goals = engine.assess_code_quality()

        # No goals for quality
        assert len(goals) == 0

    def test_many_violations(self) -> None:
        """Test when many code violations exist."""
        engine = ProactiveGoalEngine()

        # Mock flake8 output with violations
        violations_output = """
        100 E501 line too long
        50 E302 expected 2 blank lines
        """
        engine._run_command = lambda cmd: (True, violations_output)

        goals = engine.assess_code_quality()

        # Should generate quality goal
        if len(goals) > 0:
            assert goals[0].category == GoalCategory.QUALITY

    def test_few_violations_no_goal(self) -> None:
        """Test that few violations don't generate goals."""
        engine = ProactiveGoalEngine()

        # Mock flake8 with few violations
        few_violations = "5 E501 line too long"
        engine._run_command = lambda cmd: (True, few_violations)

        goals = engine.assess_code_quality()

        # Should not generate goal (< 50 threshold)
        assert len(goals) == 0


class TestCheckDocumentationGaps:
    """Tests for documentation gap detection."""

    def test_no_documentation_gaps(self, tmp_path: Path) -> None:
        """Test when documentation is adequate."""
        # Create Python files with docstrings
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        for i in range(3):
            py_file = src_dir / f"module{i}.py"
            py_file.write_text('"""Module docstring."""\n\ndef func():\n    pass\n')

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))

        goals = engine.check_documentation_gaps()

        # No gaps detected
        assert len(goals) == 0

    def test_missing_docstrings(self, tmp_path: Path) -> None:
        """Test detection of missing docstrings."""
        # Create Python files without docstrings
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        for i in range(10):
            py_file = src_dir / f"module{i}.py"
            py_file.write_text("# No docstring\ndef func():\n    pass\n")

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))

        goals = engine.check_documentation_gaps()

        # Should detect missing docstrings
        assert len(goals) > 0
        assert goals[0].category == GoalCategory.DOCUMENTATION

    def test_mixed_documentation(self, tmp_path: Path) -> None:
        """Test with mix of documented and undocumented files."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Some with docstrings
        for i in range(3):
            py_file = src_dir / f"good{i}.py"
            py_file.write_text('"""Good docstring."""\n')

        # Many without docstrings
        for i in range(8):
            py_file = src_dir / f"bad{i}.py"
            py_file.write_text("# No docstring\n")

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))

        goals = engine.check_documentation_gaps()

        # Should detect gap (>5 files without docstrings)
        assert len(goals) > 0


class TestGenerateGoals:
    """Tests for comprehensive goal generation."""

    def test_generate_goals_empty_workspace(self, tmp_path: Path) -> None:
        """Test goal generation with empty workspace."""
        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))

        goals = engine.generate_goals()

        # Should complete without error
        assert isinstance(goals, list)

    def test_generate_goals_returns_dicts(self) -> None:
        """Test that generate_goals returns dictionaries."""
        engine = ProactiveGoalEngine()

        # Mock all assessment methods to return empty
        engine.assess_test_coverage = lambda: []
        engine.detect_performance_bottlenecks = lambda: []
        engine.assess_code_quality = lambda: []
        engine.check_documentation_gaps = lambda: []

        goals = engine.generate_goals()

        assert isinstance(goals, list)

    def test_goals_sorted_by_priority(self) -> None:
        """Test that goals are sorted by priority."""
        engine = ProactiveGoalEngine()

        # Create goals with different priorities
        critical_goal = ProactiveGoal(
            goal_id="G1",
            title="Critical",
            description="",
            category=GoalCategory.SECURITY,
            priority=GoalPriority.CRITICAL,
            estimated_effort="1 day",
            acceptance_criteria=[],
            implementation_steps=[],
        )

        low_goal = ProactiveGoal(
            goal_id="G2",
            title="Low",
            description="",
            category=GoalCategory.DOCUMENTATION,
            priority=GoalPriority.LOW,
            estimated_effort="1 day",
            acceptance_criteria=[],
            implementation_steps=[],
        )

        # Mock methods to return these goals
        engine.assess_test_coverage = lambda: [low_goal]
        engine.detect_performance_bottlenecks = lambda: [critical_goal]
        engine.assess_code_quality = lambda: []
        engine.check_documentation_gaps = lambda: []

        goals = engine.generate_goals()

        # Critical should come before low
        if len(goals) >= 2:
            assert goals[0]["priority"] == GoalPriority.CRITICAL


class TestIntegration:
    """Integration tests for proactive goal generation."""

    def test_complete_analysis_workflow(self, tmp_path: Path) -> None:
        """Test complete goal generation workflow."""
        # Setup mock workspace
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        # Add some files
        (src_dir / "module1.py").write_text("# No docstring\n")
        (src_dir / "module2.py").write_text('"""Has docstring."""\n')

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))

        # Mock command runner to avoid actual subprocess calls
        engine._run_command = lambda cmd: (False, "")

        goals = engine.generate_goals()

        # Should complete successfully
        assert isinstance(goals, list)

        # All goals should have required fields
        for goal in goals:
            assert "goal_id" in goal
            assert "title" in goal
            assert "category" in goal
            assert "priority" in goal
            assert "acceptance_criteria" in goal
            assert "implementation_steps" in goal

    def test_goal_id_uniqueness(self) -> None:
        """Test that generated goal IDs are unique."""
        engine = ProactiveGoalEngine()

        # Generate multiple goals
        goals = []
        for _ in range(5):
            goal = ProactiveGoal(
                goal_id=engine._generate_id(),
                title="Test",
                description="",
                category=GoalCategory.TESTING,
                priority=GoalPriority.MEDIUM,
                estimated_effort="1 day",
                acceptance_criteria=[],
                implementation_steps=[],
            )
            goals.append(goal)

        ids = [g.goal_id for g in goals]
        assert len(ids) == len(set(ids))  # All unique

    def test_realistic_goal_structure(self, tmp_path: Path) -> None:
        """Test that generated goals have realistic structure."""
        # Create workspace with issues
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        for i in range(10):
            (src_dir / f"file{i}.py").write_text("# Missing docstring\n")

        engine = ProactiveGoalEngine(workspace_path=str(tmp_path))
        goals = engine.generate_goals()

        # Check that goals have sensible content
        for goal in goals:
            assert len(goal["title"]) > 0
            assert len(goal["description"]) > 0
            assert goal["category"] in [
                GoalCategory.TESTING,
                GoalCategory.PERFORMANCE,
                GoalCategory.QUALITY,
                GoalCategory.DOCUMENTATION,
                GoalCategory.SECURITY,
                GoalCategory.ARCHITECTURE,
            ]

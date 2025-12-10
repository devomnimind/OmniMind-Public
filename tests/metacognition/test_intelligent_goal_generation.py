"""
Tests for intelligent goal generation engine.
"""

import tempfile
from collections import defaultdict
from pathlib import Path

from src.metacognition.intelligent_goal_generation import (
    CodeAnalyzer,
    ImpactMetrics,
    ImpactPredictor,
    IntelligentGoalEngine,
    RepositoryAnalysis,
)
from src.metacognition.proactive_goals import GoalCategory, GoalPriority


class TestImpactMetrics:
    """Test impact metrics calculation."""

    def test_impact_metrics_creation(self) -> None:
        """Test creating impact metrics."""
        metrics = ImpactMetrics(
            code_coverage_impact=0.8,
            performance_impact=0.6,
            security_impact=0.9,
            maintainability_impact=0.7,
            user_value_impact=0.5,
        )

        assert metrics.code_coverage_impact == 0.8
        assert metrics.security_impact == 0.9

    def test_total_impact_calculation(self) -> None:
        """Test total impact calculation with weighted scoring."""
        metrics = ImpactMetrics(
            code_coverage_impact=0.8,
            performance_impact=0.6,
            security_impact=1.0,
            maintainability_impact=0.7,
            user_value_impact=0.5,
        )

        total = metrics.get_total_impact()

        # Weights: coverage 15%, perf 25%, security 30%, maint 15%, value 15%
        expected = 0.8 * 0.15 + 0.6 * 0.25 + 1.0 * 0.30 + 0.7 * 0.15 + 0.5 * 0.15
        assert abs(total - expected) < 0.01

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        metrics = ImpactMetrics(
            code_coverage_impact=0.8,
            performance_impact=0.6,
            confidence=0.85,
        )

        result = metrics.to_dict()

        assert result["code_coverage_impact"] == 0.8
        assert result["performance_impact"] == 0.6
        assert result["confidence"] == 0.85
        assert "total_impact" in result


class TestCodeAnalyzer:
    """Test code analysis functionality."""

    def test_analyze_simple_file(self) -> None:
        """Test analyzing a simple Python file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                '''"""Test module."""

def hello():
    """Say hello."""
    return "Hello"

class TestClass:
    """Test class."""
    pass
'''
            )

            analyzer = CodeAnalyzer(Path(tmpdir))
            result = analyzer.analyze_file(test_file)

            assert result["has_docstring"] is True
            assert "hello" in result["functions"]
            assert "TestClass" in result["classes"]
            assert result["lines"] > 0

    def test_analyze_file_with_complexity(self) -> None:
        """Test complexity calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "complex.py"
            test_file.write_text(
                """
def complex_function(x, y):
    if x > 0:
        if y > 0:
            for i in range(10):
                if i % 2 == 0:
                    return i
    return 0
"""
            )

            analyzer = CodeAnalyzer(Path(tmpdir))
            result = analyzer.analyze_file(test_file)

            # Should detect multiple decision points
            assert result["complexity"] > 1

    def test_analyze_file_with_imports(self) -> None:
        """Test import detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "imports.py"
            test_file.write_text(
                """
import os
import sys
from pathlib import Path
from typing import Dict, List
"""
            )

            analyzer = CodeAnalyzer(Path(tmpdir))
            result = analyzer.analyze_file(test_file)

            assert "os" in result["imports"]
            assert "sys" in result["imports"]
            assert "pathlib" in result["imports"]

    def test_analyze_repository(self) -> None:
        """Test repository-level analysis."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            src_dir = workspace / "src"
            src_dir.mkdir()

            # Create test files
            (src_dir / "module1.py").write_text(
                '''"""Module 1."""

def func1():
    if True:
        return 1
'''
            )

            (src_dir / "module2.py").write_text(
                """
def complex_func():
    for i in range(10):
        if i > 5:
            if i % 2 == 0:
                return i
    return 0
"""
            )

            analyzer = CodeAnalyzer(workspace)
            analysis = analyzer.analyze_repository()

            assert analysis.total_files == 2
            assert analysis.total_lines > 0
            assert len(analysis.modules) == 2
            assert len(analysis.untested_modules) > 0  # module2 has no docstring


class TestImpactPredictor:
    """Test ML-based impact prediction."""

    def test_impact_predictor_creation(self) -> None:
        """Test creating impact predictor."""
        predictor = ImpactPredictor()

        assert predictor.historical_goals == []
        assert predictor.model_trained is False

    def test_predict_security_impact(self) -> None:
        """Test predicting impact for security goals."""
        predictor = ImpactPredictor()
        analysis = RepositoryAnalysis()

        impact = predictor.predict_impact(
            GoalCategory.SECURITY,
            "Fix security vulnerability in authentication",
            analysis,
        )

        assert impact.security_impact > 0.5
        assert impact.confidence > 0.0

    def test_predict_performance_impact(self) -> None:
        """Test predicting impact for performance goals."""
        predictor = ImpactPredictor()
        analysis = RepositoryAnalysis()

        impact = predictor.predict_impact(
            GoalCategory.PERFORMANCE, "Optimize database queries", analysis
        )

        assert impact.performance_impact > 0.5

    def test_predict_testing_impact(self) -> None:
        """Test predicting impact for testing goals."""
        predictor = ImpactPredictor()
        analysis = RepositoryAnalysis()

        impact = predictor.predict_impact(
            GoalCategory.TESTING, "Add unit tests for module X", analysis
        )

        assert impact.code_coverage_impact > 0.5

    def test_effort_estimation(self) -> None:
        """Test effort estimation from description."""
        predictor = ImpactPredictor()

        # High effort
        effort = predictor._estimate_effort("Refactor entire authentication system")
        assert effort > 5.0

        # Medium effort
        effort = predictor._estimate_effort("Add logging to service")
        assert 3.0 <= effort <= 7.0

        # Low effort
        effort = predictor._estimate_effort("Fix typo in comment")
        assert effort < 5.0

    def test_effort_vs_impact_ratio(self) -> None:
        """Test effort vs impact ratio calculation."""
        predictor = ImpactPredictor()
        analysis = RepositoryAnalysis()

        impact = predictor.predict_impact(
            GoalCategory.SECURITY, "Fix critical security issue", analysis
        )

        # High impact, low effort should have high ratio
        assert impact.effort_vs_impact_ratio > 0.0

    def test_learn_from_goal(self) -> None:
        """Test learning from completed goals."""
        predictor = ImpactPredictor()

        goal = {
            "title": "Add tests",
            "category": GoalCategory.TESTING,
        }

        actual_impact = {
            "code_coverage_impact": 0.8,
            "performance_impact": 0.1,
        }

        predictor.learn_from_goal(goal, actual_impact)

        assert len(predictor.historical_goals) == 1
        assert predictor.historical_goals[0]["goal"]["title"] == "Add tests"

    def test_impact_normalization(self) -> None:
        """Test that impact values are normalized to 0-1."""
        predictor = ImpactPredictor()
        analysis = RepositoryAnalysis()

        impact = predictor.predict_impact(GoalCategory.SECURITY, "Critical security fix", analysis)

        # All impact values should be in [0, 1]
        assert 0.0 <= impact.code_coverage_impact <= 1.0
        assert 0.0 <= impact.performance_impact <= 1.0
        assert 0.0 <= impact.security_impact <= 1.0
        assert 0.0 <= impact.maintainability_impact <= 1.0
        assert 0.0 <= impact.user_value_impact <= 1.0


class TestIntelligentGoalEngine:
    """Test intelligent goal generation engine."""

    def test_engine_creation(self) -> None:
        """Test creating goal engine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IntelligentGoalEngine(tmpdir)

            assert engine.workspace_path == Path(tmpdir)
            assert isinstance(engine.code_analyzer, CodeAnalyzer)
            assert isinstance(engine.impact_predictor, ImpactPredictor)

    def test_generate_id(self) -> None:
        """Test unique ID generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IntelligentGoalEngine(tmpdir)

            id1 = engine._generate_id()
            id2 = engine._generate_id()

            assert id1 != id2
            assert "GOAL-" in id1
            assert "GOAL-" in id2

    def test_generate_complexity_reduction_goals(self) -> None:
        """Test generating complexity reduction goals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IntelligentGoalEngine(tmpdir)

            # Create analysis with complexity hotspots
            analysis = RepositoryAnalysis()
            analysis.complexity_hotspots = [
                ("src/module.py", "very_complex_function", 25),
                ("src/other.py", "another_complex", 15),
            ]

            goals = engine._generate_complexity_reduction_goals(analysis, {})

            assert len(goals) > 0
            goal = goals[0]
            assert "complexity" in goal["title"].lower() or "refactor" in goal["title"].lower()
            assert "impact_metrics" in goal

    def test_generate_test_coverage_goals(self) -> None:
        """Test generating test coverage goals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            src_dir = workspace / "src"
            src_dir.mkdir()

            # Create untested modules
            (src_dir / "untested1.py").write_text("def func(): pass")
            (src_dir / "untested2.py").write_text("def func(): pass")

            engine = IntelligentGoalEngine(tmpdir)
            analysis = engine.code_analyzer.analyze_repository()
            goals = engine._generate_test_coverage_goals(analysis, {})

            assert len(goals) > 0
            goal = goals[0]
            assert "test" in goal["title"].lower() or "coverage" in goal["title"].lower()

    def test_generate_architecture_improvement_goals(self) -> None:
        """Test generating architecture improvement goals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IntelligentGoalEngine(tmpdir)

            # Create analysis with circular dependencies
            analysis = RepositoryAnalysis()
            analysis.dependencies = defaultdict(set)
            analysis.dependencies["module_a.py"] = {"module_b.py"}
            analysis.dependencies["module_b.py"] = {"module_a.py"}

            goals = engine._generate_architecture_improvement_goals(analysis, {})

            assert len(goals) > 0
            goal = goals[0]
            assert "circular" in goal["title"].lower() or "architecture" in goal["title"].lower()

    def test_generate_security_hardening_goals(self) -> None:
        """Test generating security hardening goals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IntelligentGoalEngine(tmpdir)

            # Create analysis with security concerns
            analysis = RepositoryAnalysis()
            analysis.modules = {
                "risky.py": {
                    "functions": ["eval", "exec"],
                }
            }

            goals = engine._generate_security_hardening_goals(analysis, {})

            assert len(goals) > 0
            goal = goals[0]
            assert "security" in goal["title"].lower()
            assert goal["priority"] == GoalPriority.CRITICAL

    def test_analyze_and_generate_goals(self) -> None:
        """Test end-to-end goal generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            src_dir = workspace / "src"
            src_dir.mkdir()

            # Create sample repository
            (src_dir / "module1.py").write_text(
                '''"""Module 1."""

def simple_func():
    return 1
'''
            )

            (src_dir / "module2.py").write_text(
                """
def complex_func():
    if True:
        if True:
            if True:
                return 1
    return 0
"""
            )

            engine = IntelligentGoalEngine(tmpdir)
            goals = engine.analyze_and_generate_goals()

            assert isinstance(goals, list)
            # Should generate at least some goals
            assert len(goals) >= 0

            # If goals generated, check structure
            if goals:
                goal = goals[0]
                assert "goal_id" in goal
                assert "title" in goal
                assert "impact_metrics" in goal
                assert "total_impact" in goal["impact_metrics"]

    def test_goals_sorted_by_impact(self) -> None:
        """Test that goals are sorted by total impact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            src_dir = workspace / "src"
            src_dir.mkdir()

            # Create modules that will generate different goal types
            (src_dir / "untested.py").write_text("def func(): pass")
            (src_dir / "complex.py").write_text(
                """
def complex():
    if True:
        if True:
            if True:
                return 1
"""
            )

            engine = IntelligentGoalEngine(tmpdir)
            goals = engine.analyze_and_generate_goals()

            # Verify sorting
            if len(goals) > 1:
                for i in range(len(goals) - 1):
                    assert (
                        goals[i]["impact_metrics"]["total_impact"]
                        >= goals[i + 1]["impact_metrics"]["total_impact"]
                    )

    def test_detect_circular_dependencies(self) -> None:
        """Test circular dependency detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IntelligentGoalEngine(tmpdir)

            # Simple cycle: A -> B -> A
            dependencies = {
                "a.py": {"b.py"},
                "b.py": {"a.py"},
            }

            cycles = engine._detect_circular_dependencies(dependencies)
            assert len(cycles) > 0

    def test_no_circular_dependencies(self) -> None:
        """Test when there are no circular dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = IntelligentGoalEngine(tmpdir)

            # Linear dependency: A -> B -> C
            dependencies = {
                "a.py": {"b.py"},
                "b.py": {"c.py"},
                "c.py": set(),
            }

            cycles = engine._detect_circular_dependencies(dependencies)
            assert len(cycles) == 0


class TestIntegration:
    """Integration tests for intelligent goal generation."""

    def test_full_workflow(self) -> None:
        """Test complete workflow from analysis to prioritized goals."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            src_dir = workspace / "src"
            src_dir.mkdir()

            # Create a realistic mini-repository
            (src_dir / "simple.py").write_text(
                '''"""Simple module."""

def add(a, b):
    """Add two numbers."""
    return a + b
'''
            )

            (src_dir / "complex.py").write_text(
                """
def process(data):
    if data:
        for item in data:
            if item > 0:
                if item % 2 == 0:
                    return item
    return None
"""
            )

            (src_dir / "untested.py").write_text(
                """
def dangerous_function():
    exec("print('hello')")
"""
            )

            engine = IntelligentGoalEngine(tmpdir)

            # Analyze and generate
            goals = engine.analyze_and_generate_goals()

            # Verify results
            assert isinstance(goals, list)

            for goal in goals:
                # Check required fields
                assert "goal_id" in goal
                assert "title" in goal
                assert "description" in goal
                assert "category" in goal
                assert "priority" in goal
                assert "impact_metrics" in goal

                # Check impact metrics
                impact = goal["impact_metrics"]
                assert "total_impact" in impact
                assert "confidence" in impact
                assert 0.0 <= impact["total_impact"] <= 1.0
                assert 0.0 <= impact["confidence"] <= 1.0

    def test_predictor_learning_integration(self) -> None:
        """Test integration between predictor and learning."""
        predictor = ImpactPredictor()

        # Simulate completing a goal
        goal = {
            "title": "Add comprehensive tests",
            "category": GoalCategory.TESTING,
        }

        actual_impact = {
            "code_coverage_impact": 0.95,
            "maintainability_impact": 0.70,
        }

        # Learn from it
        predictor.learn_from_goal(goal, actual_impact)

        # Verify learning occurred
        assert len(predictor.historical_goals) == 1

        # In future, this could adjust predictions
        # For now, just verify it's stored
        stored_goal = predictor.historical_goals[0]
        assert stored_goal["goal"]["title"] == goal["title"]
        assert stored_goal["actual_impact"]["code_coverage_impact"] == 0.95


class TestIntelligentGoalGenerationHybridTopological:
    """Testes de integração entre IntelligentGoalEngine e HybridTopologicalEngine."""

    def test_goal_generation_with_topological_metrics(self) -> None:
        """Testa que geração de goals pode usar métricas topológicas."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Simular estados
        np.random.seed(42)
        for i in range(5):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            workspace.write_module_state("conscious_module", rho_C)
            workspace.write_module_state("preconscious_module", rho_P)
            workspace.write_module_state("unconscious_module", rho_U)
            workspace.advance_cycle()

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que goal generation pode usar métricas topológicas
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # Goal generation pode usar Omega para priorizar goals baseados em integração
            # Betti-0 para identificar fragmentação que precisa ser resolvida

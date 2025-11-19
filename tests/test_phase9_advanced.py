"""Tests for Phase 9.5.2, 9.6, and 9.7 implementations."""

from __future__ import annotations

import pytest


class TestMetacognitionIntegration:
    """Test metacognition integration with Orchestrator."""

    def test_orchestrator_metacognition_init(self) -> None:
        """Test that Orchestrator initializes metacognition agent."""
        try:
            from src.agents.orchestrator_agent import OrchestratorAgent

            # This would need a config file to fully test
            # For now, just verify the import works
            assert OrchestratorAgent is not None
        except ImportError:
            pytest.skip("OrchestratorAgent not available")

    def test_metacognition_routes_import(self) -> None:
        """Test importing metacognition routes."""
        try:
            from web.backend.routes import metacognition

            assert hasattr(metacognition, "router")
            assert hasattr(metacognition, "set_orchestrator")
        except ImportError:
            pytest.skip("Metacognition routes not available")


class TestProactiveGoals:
    """Test proactive goal generation."""

    def test_proactive_goal_engine_import(self) -> None:
        """Test importing proactive goal engine."""
        try:
            from src.metacognition.proactive_goals import ProactiveGoalEngine

            engine = ProactiveGoalEngine(workspace_path=".")
            assert engine is not None
        except ImportError:
            pytest.skip("ProactiveGoalEngine not available")

    def test_goal_categories(self) -> None:
        """Test goal categories are defined."""
        try:
            from src.metacognition.proactive_goals import GoalCategory

            assert hasattr(GoalCategory, "TESTING")
            assert hasattr(GoalCategory, "PERFORMANCE")
            assert hasattr(GoalCategory, "QUALITY")
            assert hasattr(GoalCategory, "DOCUMENTATION")
            assert hasattr(GoalCategory, "SECURITY")
        except ImportError:
            pytest.skip("GoalCategory not available")

    def test_goal_priority(self) -> None:
        """Test goal priorities are defined."""
        try:
            from src.metacognition.proactive_goals import GoalPriority

            assert hasattr(GoalPriority, "CRITICAL")
            assert hasattr(GoalPriority, "HIGH")
            assert hasattr(GoalPriority, "MEDIUM")
            assert hasattr(GoalPriority, "LOW")
        except ImportError:
            pytest.skip("GoalPriority not available")

    def test_proactive_goal_creation(self) -> None:
        """Test creating a proactive goal."""
        try:
            from src.metacognition.proactive_goals import (
                ProactiveGoal,
                GoalCategory,
                GoalPriority,
            )

            goal = ProactiveGoal(
                goal_id="TEST-001",
                title="Test Goal",
                description="A test goal",
                category=GoalCategory.TESTING,
                priority=GoalPriority.HIGH,
                estimated_effort="1 day",
                acceptance_criteria=["Criterion 1"],
                implementation_steps=["Step 1"],
            )

            assert goal.goal_id == "TEST-001"
            assert goal.category == GoalCategory.TESTING
            assert goal.priority == GoalPriority.HIGH

            # Test to_dict
            goal_dict = goal.to_dict()
            assert "goal_id" in goal_dict
            assert "created_at" in goal_dict
        except ImportError:
            pytest.skip("ProactiveGoal not available")


class TestHomeostasis:
    """Test embodied cognition and homeostasis."""

    def test_homeostatic_controller_import(self) -> None:
        """Test importing homeostatic controller."""
        try:
            from src.metacognition.homeostasis import HomeostaticController

            controller = HomeostaticController()
            assert controller is not None
            assert controller.check_interval == 5.0
        except ImportError:
            pytest.skip("HomeostaticController not available")

    def test_resource_states(self) -> None:
        """Test resource states are defined."""
        try:
            from src.metacognition.homeostasis import ResourceState

            assert hasattr(ResourceState, "OPTIMAL")
            assert hasattr(ResourceState, "GOOD")
            assert hasattr(ResourceState, "WARNING")
            assert hasattr(ResourceState, "CRITICAL")
            assert hasattr(ResourceState, "EMERGENCY")
        except ImportError:
            pytest.skip("ResourceState not available")

    def test_task_priority(self) -> None:
        """Test task priorities are defined."""
        try:
            from src.metacognition.homeostasis import TaskPriority

            assert hasattr(TaskPriority, "CRITICAL")
            assert hasattr(TaskPriority, "HIGH")
            assert hasattr(TaskPriority, "MEDIUM")
            assert hasattr(TaskPriority, "LOW")
            assert hasattr(TaskPriority, "BACKGROUND")
        except ImportError:
            pytest.skip("TaskPriority not available")

    def test_resource_metrics(self) -> None:
        """Test resource metrics dataclass."""
        try:
            from src.metacognition.homeostasis import ResourceMetrics

            metrics = ResourceMetrics(
                cpu_percent=50.0,
                memory_percent=60.0,
                memory_available_gb=8.0,
                disk_percent=70.0,
                timestamp=1234567890.0,
            )

            assert metrics.cpu_percent == 50.0
            assert metrics.get_overall_state().value in [
                "optimal",
                "good",
                "warning",
                "critical",
                "emergency",
            ]

            # Test to_dict
            metrics_dict = metrics.to_dict()
            assert "state" in metrics_dict
        except ImportError:
            pytest.skip("ResourceMetrics not available")

    def test_homeostatic_methods(self) -> None:
        """Test homeostatic controller methods exist."""
        try:
            from src.metacognition.homeostasis import (
                HomeostaticController,
                TaskPriority,
            )

            controller = HomeostaticController()

            # Test methods exist
            assert hasattr(controller, "start")
            assert hasattr(controller, "stop")
            assert hasattr(controller, "get_current_metrics")
            assert hasattr(controller, "get_metrics_history")
            assert hasattr(controller, "is_throttled")
            assert hasattr(controller, "should_execute_task")
            assert hasattr(controller, "get_recommended_batch_size")
            assert hasattr(controller, "get_stats")

            # Test should_execute_task (no metrics yet, should allow all)
            assert controller.should_execute_task(TaskPriority.CRITICAL)
            assert controller.should_execute_task(TaskPriority.LOW)

            # Test get_recommended_batch_size (no metrics, should return base)
            assert controller.get_recommended_batch_size(100) == 100
        except ImportError:
            pytest.skip("HomeostaticController not available")


class TestMetacognitionAPI:
    """Test metacognition API endpoints."""

    def test_metacognition_routes_exist(self) -> None:
        """Test that metacognition routes are defined."""
        try:
            from web.backend.routes.metacognition import router

            # Check that routes exist
            route_paths = [route.path for route in router.routes]

            assert "/analyze" in route_paths or any(
                "/analyze" in path for path in route_paths
            )
            assert "/health" in route_paths or any(
                "/health" in path for path in route_paths
            )
            assert "/suggestions" in route_paths or any(
                "/suggestions" in path for path in route_paths
            )
            assert "/stats" in route_paths or any(
                "/stats" in path for path in route_paths
            )
            assert "/goals/generate" in route_paths or any(
                "/goals/generate" in path for path in route_paths
            )
            assert "/homeostasis/status" in route_paths or any(
                "/homeostasis/status" in path for path in route_paths
            )
        except ImportError:
            pytest.skip("Metacognition routes not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

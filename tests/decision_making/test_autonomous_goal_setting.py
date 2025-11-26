"""Tests for Autonomous Goal Setting."""

import math
import time

import pytest

from src.decision_making.autonomous_goal_setting import (
    Goal,
    GoalHierarchy,
    GoalOptimizer,
    GoalPriority,
    GoalSetter,
    GoalStatus,
)


class TestGoal:
    """Test Goal dataclass."""

    def test_goal_initialization(self):
        """Test goal creation with defaults."""
        goal = Goal(description="Test goal")
        assert goal.description == "Test goal"
        assert goal.priority == GoalPriority.MEDIUM
        assert goal.status == GoalStatus.PENDING
        assert math.isclose(goal.progress, 0.0)
        assert goal.parent_goal_id is None
        assert goal.subgoal_ids == []
        assert isinstance(goal.goal_id, str)

    def test_goal_custom_params(self):
        """Test goal with custom parameters."""
        goal = Goal(
            description="Custom goal",
            priority=GoalPriority.HIGH,
            deadline=time.time() + 3600,
            parent_goal_id="parent123",
        )
        assert goal.description == "Custom goal"
        assert goal.priority == GoalPriority.HIGH
        assert goal.deadline is not None
        assert goal.parent_goal_id == "parent123"

    def test_goal_invalid_progress(self):
        """Test goal with invalid progress raises error."""
        with pytest.raises(ValueError):
            Goal(description="Test", progress=1.5)

    def test_update_progress(self):
        """Test progress update."""
        goal = Goal(description="Test")
        goal.update_progress(0.5)
        assert math.isclose(goal.progress, 0.5)
        assert goal.status == GoalStatus.PENDING

        goal.update_progress(1.0)
        assert math.isclose(goal.progress, 1.0)
        assert goal.status == GoalStatus.COMPLETED

    def test_is_overdue(self):
        """Test overdue check."""
        past_time = time.time() - 100
        goal = Goal(description="Test", deadline=past_time)
        assert goal.is_overdue() is True

        future_time = time.time() + 100
        goal2 = Goal(description="Test", deadline=future_time)
        assert goal2.is_overdue() is False

        goal3 = Goal(description="Test")  # No deadline
        assert goal3.is_overdue() is False

    def test_time_remaining(self):
        """Test time remaining calculation."""
        future_time = time.time() + 100
        goal = Goal(description="Test", deadline=future_time)
        remaining = goal.time_remaining()
        assert remaining is not None
        assert 95 <= remaining <= 105  # Approximate

        goal2 = Goal(description="Test")  # No deadline
        assert goal2.time_remaining() is None


class TestGoalHierarchy:
    """Test GoalHierarchy class."""

    def test_initialization(self):
        """Test hierarchy initialization."""
        hierarchy = GoalHierarchy()
        assert hierarchy.goals == {}

    def test_add_goal(self):
        """Test adding a goal."""
        hierarchy = GoalHierarchy()
        goal = Goal(description="Test goal")
        hierarchy.add_goal(goal)
        assert goal.goal_id in hierarchy.goals
        assert hierarchy.goals[goal.goal_id] == goal

    def test_add_goal_with_parent(self):
        """Test adding goal with parent updates parent."""
        hierarchy = GoalHierarchy()
        parent = Goal(description="Parent")
        child = Goal(description="Child", parent_goal_id=parent.goal_id)

        hierarchy.add_goal(parent)
        hierarchy.add_goal(child)

        assert child.goal_id in parent.subgoal_ids

    def test_get_goal(self):
        """Test getting a goal."""
        hierarchy = GoalHierarchy()
        goal = Goal(description="Test")
        hierarchy.add_goal(goal)

        retrieved = hierarchy.get_goal(goal.goal_id)
        assert retrieved == goal

        assert hierarchy.get_goal("nonexistent") is None

    def test_get_children(self):
        """Test getting child goals."""
        hierarchy = GoalHierarchy()
        parent = Goal(description="Parent")
        child1 = Goal(description="Child1", parent_goal_id=parent.goal_id)
        child2 = Goal(description="Child2", parent_goal_id=parent.goal_id)

        hierarchy.add_goal(parent)
        hierarchy.add_goal(child1)
        hierarchy.add_goal(child2)

        children = hierarchy.get_children(parent.goal_id)
        assert len(children) == 2
        assert child1 in children
        assert child2 in children

    def test_get_parent(self):
        """Test getting parent goal."""
        hierarchy = GoalHierarchy()
        parent = Goal(description="Parent")
        child = Goal(description="Child", parent_goal_id=parent.goal_id)

        hierarchy.add_goal(parent)
        hierarchy.add_goal(child)

        retrieved_parent = hierarchy.get_parent(child.goal_id)
        assert retrieved_parent == parent

    def test_get_root_goals(self):
        """Test getting root goals."""
        hierarchy = GoalHierarchy()
        root1 = Goal(description="Root1")
        root2 = Goal(description="Root2")
        child = Goal(description="Child", parent_goal_id=root1.goal_id)

        hierarchy.add_goal(root1)
        hierarchy.add_goal(root2)
        hierarchy.add_goal(child)

        roots = hierarchy.get_root_goals()
        assert len(roots) == 2
        assert root1 in roots
        assert root2 in roots

    def test_update_goal_progress(self):
        """Test progress update with propagation."""
        hierarchy = GoalHierarchy()
        parent = Goal(description="Parent")
        child1 = Goal(description="Child1", parent_goal_id=parent.goal_id)
        child2 = Goal(description="Child2", parent_goal_id=parent.goal_id)

        hierarchy.add_goal(parent)
        hierarchy.add_goal(child1)
        hierarchy.add_goal(child2)

        hierarchy.update_goal_progress(child1.goal_id, 1.0)
        hierarchy.update_goal_progress(child2.goal_id, 0.5)

        # Parent progress should be average: (1.0 + 0.5) / 2 = 0.75
        assert math.isclose(parent.progress, 0.75)

    def test_get_active_goals(self):
        """Test getting active goals."""
        hierarchy = GoalHierarchy()
        active_goal = Goal(description="Active", status=GoalStatus.ACTIVE)
        pending_goal = Goal(description="Pending", status=GoalStatus.PENDING)

        hierarchy.add_goal(active_goal)
        hierarchy.add_goal(pending_goal)

        active = hierarchy.get_active_goals()
        assert len(active) == 1
        assert active[0] == active_goal

    def test_get_pending_goals(self):
        """Test getting pending goals."""
        hierarchy = GoalHierarchy()
        active_goal = Goal(description="Active", status=GoalStatus.ACTIVE)
        pending_goal = Goal(description="Pending", status=GoalStatus.PENDING)

        hierarchy.add_goal(active_goal)
        hierarchy.add_goal(pending_goal)

        pending = hierarchy.get_pending_goals()
        assert len(pending) == 1
        assert pending[0] == pending_goal

    def test_get_overdue_goals(self):
        """Test getting overdue goals."""
        hierarchy = GoalHierarchy()
        overdue_goal = Goal(description="Overdue", deadline=time.time() - 100)
        ontime_goal = Goal(description="On time", deadline=time.time() + 100)

        hierarchy.add_goal(overdue_goal)
        hierarchy.add_goal(ontime_goal)

        overdue = hierarchy.get_overdue_goals()
        assert len(overdue) == 1
        assert overdue[0] == overdue_goal


class TestGoalSetter:
    """Test GoalSetter class."""

    def test_initialization(self):
        """Test goal setter initialization."""
        setter = GoalSetter()
        assert setter.max_concurrent_goals == 5
        assert setter.enable_auto_generation is True
        assert setter.generation_count == 0

    def test_generate_goal(self):
        """Test goal generation."""
        setter = GoalSetter()
        context = {"resource_usage": 0.95}  # Use > 0.9 for HIGH priority
        goal = setter.generate_goal(context)

        assert goal.description == "Optimize resource utilization"
        assert goal.priority == GoalPriority.HIGH
        assert goal.parent_goal_id is None
        assert goal.goal_id in setter.hierarchy.goals

    def test_generate_goal_with_parent(self):
        """Test goal generation with parent."""
        setter = GoalSetter()
        parent_goal = Goal(description="Parent")
        setter.hierarchy.add_goal(parent_goal)

        context = {"error_rate": 0.2}
        goal = setter.generate_goal(context, parent_goal.goal_id)

        assert goal.parent_goal_id == parent_goal.goal_id
        assert goal.goal_id in parent_goal.subgoal_ids

    def test_activate_goal(self):
        """Test goal activation."""
        setter = GoalSetter()
        goal = Goal(description="Test")
        setter.hierarchy.add_goal(goal)

        success = setter.activate_goal(goal.goal_id)
        assert success is True
        assert goal.status == GoalStatus.ACTIVE

    def test_activate_goal_not_found(self):
        """Test activating non-existent goal."""
        setter = GoalSetter()
        success = setter.activate_goal("nonexistent")
        assert success is False

    def test_activate_goal_max_capacity(self):
        """Test activating goal when at max capacity."""
        setter = GoalSetter(max_concurrent_goals=1)
        goal1 = Goal(description="Goal1", status=GoalStatus.ACTIVE)
        goal2 = Goal(description="Goal2")
        setter.hierarchy.add_goal(goal1)
        setter.hierarchy.add_goal(goal2)

        success = setter.activate_goal(goal2.goal_id)
        assert success is False

    def test_complete_goal_success(self):
        """Test completing goal successfully."""
        setter = GoalSetter()
        goal = Goal(description="Test", status=GoalStatus.ACTIVE)
        setter.hierarchy.add_goal(goal)

        setter.complete_goal(goal.goal_id, success=True)
        assert goal.status == GoalStatus.COMPLETED
        assert math.isclose(goal.progress, 1.0)

    def test_complete_goal_failure(self):
        """Test completing goal with failure."""
        setter = GoalSetter()
        goal = Goal(description="Test", status=GoalStatus.ACTIVE)
        setter.hierarchy.add_goal(goal)

        setter.complete_goal(goal.goal_id, success=False)
        assert goal.status == GoalStatus.FAILED

    def test_get_next_goal(self):
        """Test getting next goal."""
        setter = GoalSetter()
        high_priority = Goal(description="High", priority=GoalPriority.HIGH)
        low_priority = Goal(description="Low", priority=GoalPriority.LOW)

        setter.hierarchy.add_goal(high_priority)
        setter.hierarchy.add_goal(low_priority)

        next_goal = setter.get_next_goal()
        assert next_goal == high_priority

    def test_get_next_goal_none_pending(self):
        """Test getting next goal when none pending."""
        setter = GoalSetter()
        next_goal = setter.get_next_goal()
        assert next_goal is None

    def test_get_metrics(self):
        """Test getting metrics."""
        setter = GoalSetter()
        goal1 = Goal(description="Completed", status=GoalStatus.COMPLETED)
        goal2 = Goal(description="Active", status=GoalStatus.ACTIVE)
        goal3 = Goal(description="Failed", status=GoalStatus.FAILED)

        setter.hierarchy.add_goal(goal1)
        setter.hierarchy.add_goal(goal2)
        setter.hierarchy.add_goal(goal3)

        metrics = setter.get_metrics()
        assert metrics["total_goals"] == 3
        assert metrics["active_goals"] == 1
        assert metrics["completed_goals"] == 1
        assert metrics["failed_goals"] == 1


class TestGoalOptimizer:
    """Test GoalOptimizer class."""

    def test_initialization(self):
        """Test optimizer initialization."""
        setter = GoalSetter()
        optimizer = GoalOptimizer(setter)
        assert optimizer.goal_setter == setter

    def test_optimize_schedule(self):
        """Test schedule optimization."""
        setter = GoalSetter()
        high_goal = Goal(description="High", priority=GoalPriority.HIGH)
        low_goal = Goal(description="Low", priority=GoalPriority.LOW)

        setter.hierarchy.add_goal(high_goal)
        setter.hierarchy.add_goal(low_goal)

        optimizer = GoalOptimizer(setter)
        schedule = optimizer.optimize_schedule()

        assert len(schedule) == 2
        assert schedule[0] == high_goal  # High priority first

    def test_reallocate_resources(self):
        """Test resource reallocation."""
        setter = GoalSetter()
        goal1 = Goal(description="Goal1", priority=GoalPriority.HIGH, status=GoalStatus.ACTIVE)
        goal2 = Goal(description="Goal2", priority=GoalPriority.LOW, status=GoalStatus.ACTIVE)

        setter.hierarchy.add_goal(goal1)
        setter.hierarchy.add_goal(goal2)

        optimizer = GoalOptimizer(setter)
        allocation = optimizer.reallocate_resources(100.0)

        assert len(allocation) == 2
        assert goal1.goal_id in allocation
        assert goal2.goal_id in allocation
        # High priority gets more: 5/(5+2) * 100 ≈ 71.4
        assert allocation[goal1.goal_id] > allocation[goal2.goal_id]

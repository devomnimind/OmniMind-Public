"""
Autonomous Goal Setting for Self-Directed AI.

This module implements autonomous goal generation and optimization:
- Self-directed goal creation
- Goal prioritization and hierarchy
- Dynamic goal adaptation
- Integration with decision making and ethics

Author: OmniMind Project
License: MIT
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class GoalStatus(Enum):
    """Status of a goal."""

    PENDING = "pending"  # Not started
    ACTIVE = "active"  # Currently being pursued
    COMPLETED = "completed"  # Successfully achieved
    FAILED = "failed"  # Could not be achieved
    SUSPENDED = "suspended"  # Temporarily paused
    ABANDONED = "abandoned"  # Deliberately given up


class GoalPriority(Enum):
    """Priority levels for goals."""

    CRITICAL = 5  # Must be done immediately
    HIGH = 4  # Important, should be done soon
    MEDIUM = 3  # Standard priority
    LOW = 2  # Can be deferred
    OPTIONAL = 1  # Nice to have


@dataclass
class Goal:
    """Represents an autonomous goal."""

    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    deadline: Optional[float] = None
    parent_goal_id: Optional[str] = None
    subgoal_ids: List[str] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    progress: float = 0.0  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate goal data."""
        if not 0 <= self.progress <= 1:
            raise ValueError("Progress must be between 0 and 1")

    def update_progress(self, progress: float) -> None:
        """Update goal progress."""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = time.time()

        if self.progress >= 1.0:
            self.status = GoalStatus.COMPLETED

    def is_overdue(self) -> bool:
        """Check if goal is overdue."""
        if self.deadline is None:
            return False
        return time.time() > self.deadline

    def time_remaining(self) -> Optional[float]:
        """Get time remaining until deadline."""
        if self.deadline is None:
            return None
        return max(0.0, self.deadline - time.time())


class GoalHierarchy:
    """
    Manages hierarchical goal relationships.

    Features:
    - Parent-child goal relationships
    - Goal dependency tracking
    - Progress propagation
    """

    def __init__(self) -> None:
        """Initialize goal hierarchy."""
        self.goals: Dict[str, Goal] = {}
        self.logger = logger.bind(component="goal_hierarchy")

    def add_goal(self, goal: Goal) -> None:
        """Add a goal to the hierarchy."""
        self.goals[goal.goal_id] = goal

        # Update parent's subgoal list
        if goal.parent_goal_id and goal.parent_goal_id in self.goals:
            parent = self.goals[goal.parent_goal_id]
            if goal.goal_id not in parent.subgoal_ids:
                parent.subgoal_ids.append(goal.goal_id)

        self.logger.info("goal_added", goal_id=goal.goal_id)

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        return self.goals.get(goal_id)

    def get_children(self, goal_id: str) -> List[Goal]:
        """Get child goals."""
        goal = self.goals.get(goal_id)
        if not goal:
            return []

        return [self.goals[child_id] for child_id in goal.subgoal_ids if child_id in self.goals]

    def get_parent(self, goal_id: str) -> Optional[Goal]:
        """Get parent goal."""
        goal = self.goals.get(goal_id)
        if not goal or not goal.parent_goal_id:
            return None

        return self.goals.get(goal.parent_goal_id)

    def get_root_goals(self) -> List[Goal]:
        """Get all root (top-level) goals."""
        return [g for g in self.goals.values() if g.parent_goal_id is None]

    def update_goal_progress(self, goal_id: str, progress: float) -> None:
        """Update goal progress and propagate to parent."""
        goal = self.goals.get(goal_id)
        if not goal:
            return

        goal.update_progress(progress)

        # Propagate progress to parent
        if goal.parent_goal_id:
            self._propagate_progress_to_parent(goal.parent_goal_id)

    def _propagate_progress_to_parent(self, parent_id: str) -> None:
        """Propagate child progress to parent."""
        parent = self.goals.get(parent_id)
        if not parent:
            return

        # Calculate average progress of all children
        children = self.get_children(parent_id)
        if not children:
            return

        avg_progress = sum(child.progress for child in children) / len(children)
        parent.update_progress(avg_progress)

        # Continue propagating up
        if parent.parent_goal_id:
            self._propagate_progress_to_parent(parent.parent_goal_id)

    def get_active_goals(self) -> List[Goal]:
        """Get all active goals."""
        return [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]

    def get_pending_goals(self) -> List[Goal]:
        """Get all pending goals."""
        return [g for g in self.goals.values() if g.status == GoalStatus.PENDING]

    def get_overdue_goals(self) -> List[Goal]:
        """Get all overdue goals."""
        return [g for g in self.goals.values() if g.is_overdue()]


class GoalSetter:
    """
    Autonomous goal generation and management system.

    Features:
    - Self-directed goal creation
    - Priority-based scheduling
    - Goal adaptation based on context
    - Integration with decision making
    """

    def __init__(
        self,
        max_concurrent_goals: int = 5,
        enable_auto_generation: bool = True,
    ):
        """
        Initialize goal setter.

        Args:
            max_concurrent_goals: Maximum number of concurrent active goals
            enable_auto_generation: Whether to automatically generate goals
        """
        self.hierarchy = GoalHierarchy()
        self.max_concurrent_goals = max_concurrent_goals
        self.enable_auto_generation = enable_auto_generation
        self.logger = logger.bind(component="goal_setter")
        self.generation_count = 0

    def generate_goal(
        self,
        context: Dict[str, Any],
        parent_goal_id: Optional[str] = None,
    ) -> Goal:
        """
        Generate a new goal based on current context.

        Args:
            context: Current system context
            parent_goal_id: Optional parent goal ID

        Returns:
            Generated goal
        """
        self.generation_count += 1

        # Analyze context to determine goal
        description = self._analyze_context_for_goal(context)
        priority = self._determine_priority(context)
        deadline = self._estimate_deadline(context, priority)

        goal = Goal(
            description=description,
            priority=priority,
            parent_goal_id=parent_goal_id,
            deadline=deadline,
            success_criteria=self._define_success_criteria(context),
            metadata={"generation_count": self.generation_count, "context": context},
        )

        self.hierarchy.add_goal(goal)

        self.logger.info(
            "goal_generated",
            goal_id=goal.goal_id,
            description=description[:50],
            priority=priority.name,
        )

        return goal

    def _analyze_context_for_goal(self, context: Dict[str, Any]) -> str:
        """Analyze context to determine goal description."""
        # Simple heuristic-based goal generation
        if context.get("resource_usage", 0) > 0.8:
            return "Optimize resource utilization"
        elif context.get("error_rate", 0) > 0.1:
            return "Reduce error rate"
        elif context.get("performance_score", 1.0) < 0.7:
            return "Improve system performance"
        elif context.get("user_satisfaction", 1.0) < 0.8:
            return "Enhance user experience"
        elif context.get("security_score", 1.0) < 0.9:
            return "Strengthen security measures"
        else:
            return "Maintain optimal operation"

    def _determine_priority(self, context: Dict[str, Any]) -> GoalPriority:
        """Determine goal priority based on context."""
        # Priority based on urgency indicators
        if context.get("critical_error", False):
            return GoalPriority.CRITICAL
        elif context.get("resource_usage", 0) > 0.9:
            return GoalPriority.HIGH
        elif context.get("performance_score", 1.0) < 0.5:
            return GoalPriority.HIGH
        elif context.get("user_waiting", False):
            return GoalPriority.MEDIUM
        else:
            return GoalPriority.LOW

    def _estimate_deadline(self, context: Dict[str, Any], priority: GoalPriority) -> float:
        """Estimate deadline based on priority and context."""
        current_time = time.time()

        # Time in seconds
        if priority == GoalPriority.CRITICAL:
            return current_time + 3600  # 1 hour
        elif priority == GoalPriority.HIGH:
            return current_time + 86400  # 1 day
        elif priority == GoalPriority.MEDIUM:
            return current_time + 604800  # 1 week
        else:
            return current_time + 2592000  # 30 days

    def _define_success_criteria(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Define success criteria for the goal."""
        criteria = {
            "min_progress": 0.95,
            "max_errors": 0,
            "performance_threshold": 0.8,
        }

        # Adjust based on context
        if context.get("strict_requirements", False):
            criteria["min_progress"] = 1.0
        if context.get("allow_errors", False):
            criteria["max_errors"] = 5

        return criteria

    def activate_goal(self, goal_id: str) -> bool:
        """
        Activate a goal for pursuit.

        Args:
            goal_id: Goal ID to activate

        Returns:
            True if activated, False if already at max capacity
        """
        goal = self.hierarchy.get_goal(goal_id)
        if not goal:
            self.logger.warning("goal_not_found", goal_id=goal_id)
            return False

        # Check capacity
        active_goals = self.hierarchy.get_active_goals()
        if len(active_goals) >= self.max_concurrent_goals:
            self.logger.warning(
                "max_concurrent_goals_reached",
                current=len(active_goals),
                max=self.max_concurrent_goals,
            )
            return False

        goal.status = GoalStatus.ACTIVE
        goal.updated_at = time.time()

        self.logger.info("goal_activated", goal_id=goal_id)
        return True

    def complete_goal(self, goal_id: str, success: bool = True) -> None:
        """Mark a goal as completed or failed."""
        goal = self.hierarchy.get_goal(goal_id)
        if not goal:
            return

        if success:
            goal.status = GoalStatus.COMPLETED
            goal.progress = 1.0
        else:
            goal.status = GoalStatus.FAILED

        goal.updated_at = time.time()

        self.logger.info(
            "goal_completed",
            goal_id=goal_id,
            success=success,
            duration=goal.updated_at - goal.created_at,
        )

    def get_next_goal(self) -> Optional[Goal]:
        """Get the next goal to pursue based on priority."""
        pending_goals = self.hierarchy.get_pending_goals()
        if not pending_goals:
            return None

        # Sort by priority (highest first) and then by creation time
        sorted_goals = sorted(
            pending_goals,
            key=lambda g: (g.priority.value, -g.created_at),
            reverse=True,
        )

        return sorted_goals[0]

    def get_metrics(self) -> Dict[str, Any]:
        """Get goal setting metrics."""
        all_goals = list(self.hierarchy.goals.values())
        if not all_goals:
            return {
                "total_goals": 0,
                "active_goals": 0,
                "completed_goals": 0,
                "avg_completion_time": 0.0,
            }

        completed_goals = [g for g in all_goals if g.status == GoalStatus.COMPLETED]
        avg_completion_time = 0.0
        if completed_goals:
            completion_times = [g.updated_at - g.created_at for g in completed_goals]
            avg_completion_time = sum(completion_times) / len(completion_times)

        return {
            "total_goals": len(all_goals),
            "active_goals": len(self.hierarchy.get_active_goals()),
            "pending_goals": len(self.hierarchy.get_pending_goals()),
            "completed_goals": len(completed_goals),
            "failed_goals": len([g for g in all_goals if g.status == GoalStatus.FAILED]),
            "overdue_goals": len(self.hierarchy.get_overdue_goals()),
            "avg_completion_time": avg_completion_time,
            "generation_count": self.generation_count,
        }


class GoalOptimizer:
    """
    Optimizes goal pursuit strategies.

    Features:
    - Resource allocation optimization
    - Goal reordering based on dependencies
    - Deadline management
    """

    def __init__(self, goal_setter: GoalSetter):
        """
        Initialize goal optimizer.

        Args:
            goal_setter: GoalSetter instance to optimize
        """
        self.goal_setter = goal_setter
        self.logger = logger.bind(component="goal_optimizer")

    def optimize_schedule(self) -> List[Goal]:
        """
        Optimize goal execution schedule.

        Returns:
            Ordered list of goals to pursue
        """
        active_goals = self.goal_setter.hierarchy.get_active_goals()
        pending_goals = self.goal_setter.hierarchy.get_pending_goals()
        all_goals = active_goals + pending_goals

        if not all_goals:
            return []

        # Score each goal
        scored_goals = [(goal, self._compute_priority_score(goal)) for goal in all_goals]

        # Sort by score (highest first)
        scored_goals.sort(key=lambda x: x[1], reverse=True)

        optimized_schedule = [goal for goal, _ in scored_goals]

        self.logger.info(
            "schedule_optimized",
            total_goals=len(optimized_schedule),
        )

        return optimized_schedule

    def _compute_priority_score(self, goal: Goal) -> float:
        """Compute priority score for goal."""
        score = float(goal.priority.value)

        # Increase score for overdue goals
        if goal.is_overdue():
            score += 2.0

        # Increase score based on time pressure
        time_remaining = goal.time_remaining()
        if time_remaining is not None and time_remaining < 86400:  # < 1 day
            score += 1.5

        # Decrease score based on current progress
        score -= goal.progress * 0.5

        return score

    def reallocate_resources(self, total_resources: float) -> Dict[str, float]:
        """
        Allocate resources to goals.

        Args:
            total_resources: Total resources available

        Returns:
            Dictionary mapping goal_id to allocated resources
        """
        active_goals = self.goal_setter.hierarchy.get_active_goals()
        if not active_goals:
            return {}

        # Allocate based on priority
        total_priority = sum(float(g.priority.value) for g in active_goals)
        if total_priority == 0:
            total_priority = 1.0

        allocation: Dict[str, float] = {}
        for goal in active_goals:
            proportion = float(goal.priority.value) / total_priority
            allocation[goal.goal_id] = total_resources * proportion

        self.logger.info(
            "resources_allocated",
            num_goals=len(allocation),
            total=total_resources,
        )

        return allocation

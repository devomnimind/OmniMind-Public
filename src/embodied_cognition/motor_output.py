"""
Motor Output Module - Goal to Action Execution

Transforms internal goals/decisions into executed actions.
Provides interface for:
- Simulated execution (default)
- ROS robot control (with enable_ros=True)
- Custom action handlers

References:
- Dreyfus & Dreyfus: Skill acquisition model
- Noe (2004): "Action in Perception"
- Gibson (1977): Affordances enable action
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ActionExecution:
    """Result of action execution."""

    goal: str
    plan: List[str]
    results: List[bool]
    success: bool = False
    error: Optional[str] = None


class MotorController:
    """
    Motor control system - translates goals to actions.

    Goal → Plan (symbolic) → Execute (motor) → Verify (sensory)

    This creates a feedback loop where actions inform future perception
    and planning.
    """

    def __init__(
        self,
        enable_ros: bool = False,
        enable_simulation: bool = True,
    ):
        """
        Initialize motor controller.

        Args:
            enable_ros: Enable ROS robot interface
            enable_simulation: Enable simulated execution
        """
        self.enable_ros = enable_ros
        self.enable_simulation = enable_simulation
        self.action_history: List[ActionExecution] = []

        if enable_ros:
            try:
                import rospy as rospy_module  # type: ignore[import-not-found]  # noqa: F401

                logger.info("ROS interface enabled")
            except ImportError:
                logger.warning("ROS not available, using simulation only")
                self.enable_ros = False

        logger.info(
            f"MotorController initialized " f"(ROS={enable_ros}, simulation={enable_simulation})"
        )

    def plan_action_sequence(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Create action plan from goal.

        Simple planning heuristic:
        1. Parse goal
        2. Break into sub-actions
        3. Order by dependency

        Args:
            goal: Goal description
            context: Environmental context

        Returns:
            List of actions to execute
        """
        context = context or {}

        logger.debug(f"Planning actions for goal: {goal}")

        # Simple keyword-based planning
        plan = []

        if "move" in goal.lower():
            plan.extend(
                [
                    "check_current_position",
                    "calculate_path",
                    "execute_movement",
                    "verify_position",
                ]
            )
        elif "grab" in goal.lower() or "pick" in goal.lower():
            plan.extend(
                [
                    "locate_object",
                    "approach_object",
                    "grasp_object",
                    "verify_grasp",
                ]
            )
        elif "communicate" in goal.lower() or "say" in goal.lower():
            plan.extend(
                [
                    "formulate_message",
                    "transmit_message",
                    "await_response",
                ]
            )
        else:
            # Generic plan
            plan.extend(
                [
                    "assess_situation",
                    "determine_action",
                    "execute_action",
                    "evaluate_result",
                ]
            )

        logger.info(f"Action plan created: {plan}")
        return plan

    def execute_single_action(self, action: str) -> bool:
        """
        Execute single action.

        Args:
            action: Action to execute

        Returns:
            True if successful, False otherwise
        """
        logger.debug(f"Executing action: {action}")

        try:
            if self.enable_ros:
                # ROS execution
                result = self._execute_ros_action(action)
            else:
                # Simulated execution
                result = self._execute_simulated_action(action)

            return result
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return False

    def _execute_simulated_action(self, action: str) -> bool:
        """Execute action in simulation."""
        logger.info(f"[SIMULATED ACTION] {action}")

        # Simulate successful execution (90% success rate)
        import random

        success = random.random() > 0.1

        if success:
            logger.info(f"✅ Action completed: {action}")
        else:
            logger.warning(f"❌ Action failed: {action}")

        return success

    def _execute_ros_action(self, action: str) -> bool:
        """Execute action via ROS."""
        try:
            import rospy as rospy_module  # noqa: F401

            # TODO: Implement ROS action execution
            logger.info(f"[ROS ACTION] {action}")
            return True
        except Exception as e:
            logger.error(f"ROS action failed: {e}")
            return False

    def execute_goal(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ActionExecution:
        """
        Full goal execution pipeline.

        1. Parse goal
        2. Create action plan
        3. Execute each action
        4. Verify outcomes

        Args:
            goal: Goal description
            context: Environmental context

        Returns:
            ActionExecution with results
        """
        logger.info(f"Executing goal: {goal}")

        try:
            # Planning phase
            plan = self.plan_action_sequence(goal, context)

            # Execution phase
            results = []
            for action in plan:
                result = self.execute_single_action(action)
                results.append(result)

            # Evaluate overall success
            success = all(results)

            execution = ActionExecution(
                goal=goal,
                plan=plan,
                results=results,
                success=success,
            )

            self.action_history.append(execution)

            if success:
                logger.info(f"✅ Goal completed successfully: {goal}")
            else:
                failed_actions = [a for a, r in zip(plan, results) if not r]
                logger.warning(f"⚠️ Goal partially completed. Failed: {failed_actions}")

            return execution

        except Exception as e:
            logger.error(f"Goal execution failed with error: {e}")
            return ActionExecution(
                goal=goal,
                plan=[],
                results=[],
                success=False,
                error=str(e),
            )

    def get_execution_summary(self, limit: int = 10) -> str:
        """Get summary of recent executions."""
        recent = self.action_history[-limit:]

        summary = "=== MOTOR EXECUTION HISTORY ===\n"
        for i, exec in enumerate(reversed(recent), 1):
            status = "✅" if exec.success else "❌"
            success_rate = sum(exec.results) / len(exec.results) if exec.results else 0
            summary += (
                f"{i}. {status} {exec.goal}\n"
                f"   Actions: {len(exec.plan)} (success rate: {success_rate:.1%})\n"
            )

        return summary

"""
Procedural Memory Module.

Stores skills, habits, and action sequences ("knowing how").
Manages the learning and refinement of motor and cognitive skills.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Represents a learned skill or procedure."""

    name: str
    steps: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    creation_time: datetime = field(default_factory=datetime.now)
    proficiency: float = 0.1  # 0.0 to 1.0
    success_count: int = 0
    failure_count: int = 0
    last_practiced: datetime = field(default_factory=datetime.now)


class ProceduralMemory:
    """
    Procedural Memory System.

    Manages the acquisition, storage, and execution of skills.
    """

    def __init__(self) -> None:
        """Initialize procedural memory."""
        self.skills: Dict[str, Skill] = {}
        logger.info("Procedural Memory initialized")

    def learn_skill(
        self, name: str, steps: List[str], parameters: Optional[Dict[str, Any]] = None
    ) -> Skill:
        """
        Learn a new skill or update an existing one.

        Args:
            name: Name of the skill.
            steps: List of steps to execute the skill.
            parameters: Default parameters for the skill.

        Returns:
            The learned Skill object.
        """
        name = name.lower().strip()

        if name in self.skills:
            skill = self.skills[name]
            # Update steps if provided
            if steps:
                skill.steps = steps
            if parameters:
                skill.parameters.update(parameters)
            logger.debug(f"Updated skill: {name}")
        else:
            skill = Skill(name=name, steps=steps, parameters=parameters or {})
            self.skills[name] = skill
            logger.debug(f"Learned new skill: {name}")

        return skill

    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Retrieve a skill by name.

        Args:
            name: Skill name.

        Returns:
            Skill object or None if not found.
        """
        name = name.lower().strip()
        return self.skills.get(name)

    def execute_skill(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> Optional[List[str]]:
        """
        Simulate the execution of a skill.
        In a real system, this would interface with the motor controller.

        Args:
            name: Skill name.
            context: Execution context (overrides default parameters).

        Returns:
            List of steps to be executed, or None if skill not found.
        """
        name = name.lower().strip()
        skill = self.skills.get(name)

        if not skill:
            logger.warning(f"Attempted to execute unknown skill: {name}")
            return None

        skill.last_practiced = datetime.now()

        # In a real scenario, we might modify steps based on context
        logger.info(f"Executing skill: {name} (Proficiency: {skill.proficiency:.2f})")
        return skill.steps

    def refine_skill(self, name: str, success: bool, feedback: Optional[str] = None) -> None:
        """
        Update skill proficiency based on execution result.

        Args:
            name: Skill name.
            success: Whether the execution was successful.
            feedback: Optional feedback string.
        """
        name = name.lower().strip()
        skill = self.skills.get(name)

        if not skill:
            return

        if success:
            skill.success_count += 1
            # Logarithmic learning curve
            skill.proficiency = min(skill.proficiency + (1.0 - skill.proficiency) * 0.1, 1.0)
        else:
            skill.failure_count += 1
            # Slight penalty for failure, but learning from mistakes
            skill.proficiency = max(skill.proficiency - 0.05, 0.0)

        logger.debug(
            f"Refined skill {name}: Success={success}, "
            f"New Proficiency={skill.proficiency:.2f}, Feedback={feedback}"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about procedural memory."""
        total_skills = len(self.skills)
        avg_proficiency = (
            sum(s.proficiency for s in self.skills.values()) / total_skills
            if total_skills > 0
            else 0.0
        )

        return {
            "total_skills": total_skills,
            "avg_proficiency": avg_proficiency,
            "most_practiced": (
                sorted(
                    self.skills.values(),
                    key=lambda s: s.success_count + s.failure_count,
                    reverse=True,
                )[0].name
                if self.skills
                else None
            ),
        }

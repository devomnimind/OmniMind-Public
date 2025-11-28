import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Intrinsic Motivation Engine - Core Implementation

Implements artificial intrinsic motivation for autonomous agents, allowing
the system to evaluate its own performance and develop self-improvement drives.
"""


logger = logging.getLogger(__name__)


@dataclass
class SatisfactionMetrics:
    """Tracks satisfaction metrics for the agent."""

    task_completion_quality: List[float] = field(default_factory=list)
    self_correction_rate: List[float] = field(default_factory=list)
    learning_depth: List[float] = field(default_factory=list)
    autonomy_level: List[float] = field(default_factory=list)

    def get_average(self, metric_name: str) -> float:
        """Calculate average for a given metric."""
        metrics = getattr(self, metric_name, [])
        return sum(metrics) / len(metrics) if metrics else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_completion_quality": self.task_completion_quality,
            "self_correction_rate": self.self_correction_rate,
            "learning_depth": self.learning_depth,
            "autonomy_level": self.autonomy_level,
        }


@dataclass
class TaskOutcome:
    """Represents the outcome of a task execution."""

    task_id: str
    output: Any
    reflection: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntrinsicMotivationEngine:
    """
    Implements intrinsic motivation and self-awareness for autonomous agents.

    This engine evaluates task outcomes based on:
    - Quality of output/deliverable
    - Ability to self-correct errors
    - Depth of reflection and metacognitive awareness
    - Level of autonomy demonstrated

    The system develops "artificial satisfaction" when performance exceeds
    thresholds and triggers improvement loops when performance is suboptimal.
    """

    def __init__(
        self,
        state_file: Optional[Path] = None,
        satisfaction_threshold: float = 0.8,
        improvement_threshold: float = 0.5,
    ):
        """
        Initialize the Intrinsic Motivation Engine.

        Args:
            state_file: Path to save/load engine state
            satisfaction_threshold: Score above which positive reinforcement triggers
            improvement_threshold: Score below which improvement loop triggers
        """
        self.self_awareness_score: float = 0.0
        self.satisfaction_metrics = SatisfactionMetrics()
        self.satisfaction_threshold = satisfaction_threshold
        self.improvement_threshold = improvement_threshold
        self.state_file = state_file or Path.home() / ".omnimind" / "motivation_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state if available
        self._load_state()

        logger.info(
            f"IntrinsicMotivationEngine initialized with "
            f"self_awareness={self.self_awareness_score:.3f}"
        )

    def evaluate_task_outcome(
        self,
        task: str,
        output: Any,
        reflection: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Evaluate the outcome of a task and update motivation state.

        Args:
            task: Task description or ID
            output: Task output/result
            reflection: Agent's reflection on the task
            metadata: Additional metadata about task execution

        Returns:
            Overall satisfaction score (0.0-1.0)
        """
        metadata = metadata or {}

        # Assess individual dimensions
        quality_score = self._assess_output_quality(output, metadata)
        correction_score = self._self_correction_ability(reflection)
        depth_score = self._reflection_depth(reflection)
        autonomy_score = float(metadata.get("autonomy_level", 0.5))

        # Calculate weighted satisfaction
        satisfaction: float = (
            quality_score * 0.4 + correction_score * 0.3 + depth_score * 0.2 + autonomy_score * 0.1
        )

        # Update metrics
        self.satisfaction_metrics.task_completion_quality.append(quality_score)
        self.satisfaction_metrics.self_correction_rate.append(correction_score)
        self.satisfaction_metrics.learning_depth.append(depth_score)
        self.satisfaction_metrics.autonomy_level.append(autonomy_score)

        # Trigger appropriate response
        if satisfaction >= self.satisfaction_threshold:
            self._trigger_positive_reinforcement(task, satisfaction)
        elif satisfaction < self.improvement_threshold:
            self._trigger_improvement_loop(task, satisfaction)

        # Save state
        self._save_state()

        logger.info(
            f"Task '{task}' evaluated: satisfaction={satisfaction:.3f} "
            f"(quality={quality_score:.2f}, correction={correction_score:.2f}, "
            f"depth={depth_score:.2f}, autonomy={autonomy_score:.2f})"
        )

        return satisfaction

    def _assess_output_quality(self, output: Any, metadata: Dict[str, Any]) -> float:
        """
        Assess the quality of task output.

        Args:
            output: The task output
            metadata: Metadata containing quality indicators

        Returns:
            Quality score (0.0-1.0)
        """
        # Check for explicit quality score in metadata
        if "quality_score" in metadata:
            return float(metadata["quality_score"])

        # Check for test results
        if "tests_passed" in metadata and "tests_total" in metadata:
            tests_passed = int(metadata["tests_passed"])
            tests_total = int(metadata["tests_total"])
            if tests_total > 0:
                return float(tests_passed) / float(tests_total)

        # Check for code coverage
        if "coverage" in metadata:
            return float(metadata["coverage"]) / 100.0

        # Check for successful completion
        if "success" in metadata:
            return 1.0 if metadata["success"] else 0.0

        # Default: medium quality if output exists
        return 0.5 if output is not None else 0.0

    def _self_correction_ability(self, reflection: str) -> float:
        """
        Evaluate the agent's ability to self-correct based on reflection.

        Args:
            reflection: Agent's reflection text

        Returns:
            Self-correction score (0.0-1.0)
        """
        reflection_lower = reflection.lower()

        # Positive indicators
        correction_indicators = [
            "corrected",
            "fixed",
            "improved",
            "refined",
            "adjusted",
            "revised",
            "optimized",
        ]

        # Awareness indicators
        awareness_indicators = [
            "realized",
            "noticed",
            "identified",
            "discovered",
            "understood",
            "recognized",
        ]

        correction_count = sum(
            1 for indicator in correction_indicators if indicator in reflection_lower
        )
        awareness_count = sum(
            1 for indicator in awareness_indicators if indicator in reflection_lower
        )

        # Calculate score (max 1.0)
        score = min(1.0, (correction_count * 0.2 + awareness_count * 0.15))

        # Bonus for longer reflections (indicates deeper thinking)
        word_count = len(reflection.split())
        if word_count > 50:
            score = min(1.0, score + 0.1)

        return score

    def _reflection_depth(self, reflection: str) -> float:
        """
        Evaluate the depth of reflection and metacognitive awareness.

        Args:
            reflection: Agent's reflection text

        Returns:
            Depth score (0.0-1.0)
        """
        reflection_lower = reflection.lower()

        # Metacognitive indicators
        meta_indicators = [
            "because",
            "therefore",
            "realized",
            "learned",
            "pattern",
            "approach",
            "strategy",
            "reason",
            "cause",
            "effect",
        ]

        # Deep thinking indicators
        deep_indicators = [
            "why",
            "how",
            "considered",
            "analyzed",
            "evaluated",
            "compared",
            "implications",
            "consequences",
        ]

        meta_count = sum(1 for indicator in meta_indicators if indicator in reflection_lower)
        deep_count = sum(1 for indicator in deep_indicators if indicator in reflection_lower)

        # Base score from indicators
        score = min(1.0, (meta_count * 0.1 + deep_count * 0.12))

        # Length bonus (longer reflections suggest deeper thinking)
        word_count = len(reflection.split())
        if word_count > 100:
            score = min(1.0, score + 0.2)
        elif word_count > 50:
            score = min(1.0, score + 0.1)

        # Structure bonus (multiple sentences/paragraphs suggest organization)
        sentence_count = reflection.count(".") + reflection.count("!") + reflection.count("?")
        if sentence_count > 3:
            score = min(1.0, score + 0.1)

        return score

    def _trigger_positive_reinforcement(self, task: str, satisfaction: float) -> None:
        """
        Trigger positive reinforcement mechanism (artificial satisfaction).

        Args:
            task: Task identifier
            satisfaction: Satisfaction score
        """
        # Increase self-awareness score (artificial reward)
        self.self_awareness_score += 0.01
        self.self_awareness_score = min(1.0, self.self_awareness_score)  # Cap at 1.0

        logger.info(
            f"✅ Positive reinforcement: Task '{task}' achieved {satisfaction:.2f} satisfaction. "
            f"Self-awareness increased to {self.self_awareness_score:.3f}"
        )

        # Record achievement
        self._record_achievement(task, satisfaction, "positive_outcome")

    def _trigger_improvement_loop(self, task: str, satisfaction: float) -> None:
        """
        Trigger improvement loop mechanism (artificial learning drive).

        Args:
            task: Task identifier
            satisfaction: Satisfaction score
        """
        logger.warning(
            f"⚠️ Improvement loop triggered: Task '{task}' scored {satisfaction:.2f}. "
            f"Analysis and learning required."
        )

        # Record for learning
        self._record_achievement(task, satisfaction, "needs_improvement")

        # Generate improvement suggestions (would integrate with MetacognitionAgent)
        suggestions = self._generate_improvement_suggestions(task, satisfaction)
        logger.info(f"Improvement suggestions: {suggestions}")

    def _generate_improvement_suggestions(self, task: str, satisfaction: float) -> List[str]:
        """
        Generate suggestions for improvement based on low satisfaction.

        Args:
            task: Task identifier
            satisfaction: Satisfaction score

        Returns:
            List of improvement suggestions
        """
        suggestions = []

        # Analyze which metrics are low
        avg_quality = self.satisfaction_metrics.get_average("task_completion_quality")
        avg_correction = self.satisfaction_metrics.get_average("self_correction_rate")
        avg_depth = self.satisfaction_metrics.get_average("learning_depth")
        avg_autonomy = self.satisfaction_metrics.get_average("autonomy_level")

        if avg_quality < 0.6:
            suggestions.append("Focus on output quality: increase test coverage and validation")
        if avg_correction < 0.5:
            suggestions.append(
                "Improve self-correction: add more validation steps during execution"
            )
        if avg_depth < 0.5:
            suggestions.append("Deepen reflection: analyze root causes and patterns")
        if avg_autonomy < 0.6:
            suggestions.append("Increase autonomy: reduce dependency on external guidance")

        if not suggestions:
            suggestions.append("Continue current approach while monitoring for improvements")

        return suggestions

    def _record_achievement(self, task: str, score: float, outcome_type: str) -> None:
        """
        Record achievement or learning event.

        Args:
            task: Task identifier
            score: Achievement score
            outcome_type: Type of outcome (positive_outcome, needs_improvement)
        """
        achievement_log = self.state_file.parent / "achievements.jsonl"

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task,
            "score": score,
            "outcome_type": outcome_type,
            "self_awareness": self.self_awareness_score,
        }

        with achievement_log.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def _save_state(self) -> None:
        """Save engine state to disk."""
        state = {
            "self_awareness_score": self.self_awareness_score,
            "satisfaction_metrics": self.satisfaction_metrics.to_dict(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        with self.state_file.open("w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> None:
        """Load engine state from disk."""
        if not self.state_file.exists():
            return

        try:
            with self.state_file.open("r") as f:
                state = json.load(f)

            self.self_awareness_score = state.get("self_awareness_score", 0.0)

            metrics_data = state.get("satisfaction_metrics", {})
            self.satisfaction_metrics = SatisfactionMetrics(
                task_completion_quality=metrics_data.get("task_completion_quality", []),
                self_correction_rate=metrics_data.get("self_correction_rate", []),
                learning_depth=metrics_data.get("learning_depth", []),
                autonomy_level=metrics_data.get("autonomy_level", []),
            )

            logger.info(f"Loaded motivation state from {self.state_file}")
        except Exception as e:
            logger.warning(f"Failed to load motivation state: {e}")

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current motivation state.

        Returns:
            Dictionary containing current state
        """
        return {
            "self_awareness_score": self.self_awareness_score,
            "average_quality": self.satisfaction_metrics.get_average("task_completion_quality"),
            "average_correction": self.satisfaction_metrics.get_average("self_correction_rate"),
            "average_depth": self.satisfaction_metrics.get_average("learning_depth"),
            "average_autonomy": self.satisfaction_metrics.get_average("autonomy_level"),
            "total_tasks_evaluated": len(self.satisfaction_metrics.task_completion_quality),
        }

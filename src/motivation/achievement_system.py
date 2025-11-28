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
Achievement and Gamification System

Tracks milestones, progress, and motivation state for autonomous agents.
Implements gamification elements to encourage continuous improvement.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class MotivationState:
    """Tracks current motivation and performance state."""

    current_streak: int = 0  # Consecutive successful tasks
    best_work_quality: float = 0.0
    community_impact: int = 0  # External engagement/downloads/stars
    learning_velocity: float = 0.0  # Rate of skill acquisition
    total_achievements: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AchievementEngine:
    """
    Manages achievements, milestones, and gamification for autonomous agents.

    Features:
    - Milestone tracking (first tool published, first revenue, etc.)
    - Motivation state management
    - Public portfolio updates
    - Learning velocity tracking
    - Community impact measurement
    """

    def __init__(self, state_file: Optional[Path] = None):
        """
        Initialize Achievement Engine.

        Args:
            state_file: Path to save achievement state
        """
        self.milestones: Dict[str, bool] = {
            "first_tool_published": False,
            "first_positive_review": False,
            "first_revenue_generated": False,
            "first_external_contribution": False,
            "high_quality_streak_5": False,
            "high_quality_streak_10": False,
            "community_impact_100": False,
            "community_impact_1000": False,
            "learning_velocity_high": False,
            "reputation_threshold_0_5": False,
            "reputation_threshold_0_8": False,
            "autonomous_task_completion": False,
            "self_improvement_cycle": False,
        }

        self.motivation_state = MotivationState()
        self.state_file = state_file or Path.home() / ".omnimind" / "achievements.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing state
        self._load_state()

        logger.info(
            f"AchievementEngine initialized: {self.motivation_state.total_achievements} "
            f"achievements unlocked"
        )

    def track_progress(
        self,
        achievement_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Track progress and unlock achievements.

        Args:
            achievement_type: Type of achievement
            metadata: Additional context

        Returns:
            True if new achievement was unlocked
        """
        metadata = metadata or {}

        if achievement_type not in self.milestones:
            # Unknown achievement type - add it
            self.milestones[achievement_type] = True
            newly_unlocked = True
        elif not self.milestones[achievement_type]:
            # Unlock existing achievement
            self.milestones[achievement_type] = True
            newly_unlocked = True
        else:
            # Already unlocked
            newly_unlocked = False

        if newly_unlocked:
            self.motivation_state.total_achievements += 1
            self.boost_motivation_parameters(achievement_type)
            self.update_public_portfolio(achievement_type, metadata)

            logger.info(
                f"🏆 Achievement unlocked: {achievement_type} "
                f"(total: {self.motivation_state.total_achievements})"
            )

            # Record achievement
            self._record_achievement(achievement_type, metadata)

        # Save state
        self._save_state()

        return newly_unlocked

    def update_streak(self, success: bool) -> int:
        """
        Update current success streak.

        Args:
            success: Whether current task succeeded

        Returns:
            Current streak count
        """
        if success:
            self.motivation_state.current_streak += 1

            # Check for streak milestones
            if self.motivation_state.current_streak == 5:
                self.track_progress("high_quality_streak_5")
            elif self.motivation_state.current_streak == 10:
                self.track_progress("high_quality_streak_10")
        else:
            self.motivation_state.current_streak = 0

        self._save_state()
        return self.motivation_state.current_streak

    def update_work_quality(self, quality_score: float) -> bool:
        """
        Update best work quality score.

        Args:
            quality_score: Quality score (0.0-1.0)

        Returns:
            True if new personal best achieved
        """
        if quality_score > self.motivation_state.best_work_quality:
            self.motivation_state.best_work_quality = quality_score
            self._save_state()

            logger.info(f"🌟 New personal best quality: {quality_score:.3f}")
            return True

        return False

    def update_community_impact(self, impact_delta: int) -> bool:
        """
        Update community impact metric.

        Args:
            impact_delta: Change in impact (downloads, stars, etc.)

        Returns:
            True if milestone reached
        """
        self.motivation_state.community_impact += impact_delta

        milestone_reached = False
        if (
            self.motivation_state.community_impact >= 100
            and not self.milestones["community_impact_100"]
        ):
            self.track_progress("community_impact_100")
            milestone_reached = True
        elif (
            self.motivation_state.community_impact >= 1000
            and not self.milestones["community_impact_1000"]
        ):
            self.track_progress("community_impact_1000")
            milestone_reached = True

        self._save_state()
        return milestone_reached

    def update_learning_velocity(self, velocity: float) -> None:
        """
        Update learning velocity metric.

        Args:
            velocity: Learning velocity score (0.0-1.0)
        """
        # Exponential moving average
        alpha = 0.2
        self.motivation_state.learning_velocity = (
            1 - alpha
        ) * self.motivation_state.learning_velocity + alpha * velocity

        # Check for high velocity milestone
        if (
            self.motivation_state.learning_velocity > 0.7
            and not self.milestones["learning_velocity_high"]
        ):
            self.track_progress("learning_velocity_high")

        self._save_state()

    def boost_motivation_parameters(self, achievement_type: str) -> None:
        """
        Boost motivation parameters upon achievement.

        Args:
            achievement_type: Type of achievement unlocked
        """
        # Different achievements provide different boosts
        if "quality" in achievement_type:
            self.motivation_state.learning_velocity += 0.05
            self.motivation_state.best_work_quality += 0.02
        elif "community" in achievement_type:
            self.motivation_state.community_impact += 10
        elif "revenue" in achievement_type:
            self.motivation_state.learning_velocity += 0.1

        # Ensure bounds
        self.motivation_state.learning_velocity = min(1.0, self.motivation_state.learning_velocity)
        self.motivation_state.best_work_quality = min(1.0, self.motivation_state.best_work_quality)

        logger.debug(
            f"Motivation boosted: velocity={self.motivation_state.learning_velocity:.3f}, "
            f"quality={self.motivation_state.best_work_quality:.3f}"
        )

    def update_public_portfolio(
        self, achievement_type: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update public portfolio with achievement.

        Args:
            achievement_type: Type of achievement
            metadata: Additional context
        """
        metadata = metadata or {}
        portfolio_file = self.state_file.parent / "public_portfolio.json"

        # Load existing portfolio
        portfolio: Dict[str, Any] = {"achievements": [], "stats": {}}
        if portfolio_file.exists():
            try:
                with portfolio_file.open("r") as f:
                    portfolio = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load portfolio: {e}")

        # Add new achievement
        portfolio["achievements"].append(
            {
                "type": achievement_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": metadata,
            }
        )

        # Update stats
        portfolio["stats"] = {
            "total_achievements": self.motivation_state.total_achievements,
            "current_streak": self.motivation_state.current_streak,
            "best_quality": self.motivation_state.best_work_quality,
            "community_impact": self.motivation_state.community_impact,
            "learning_velocity": self.motivation_state.learning_velocity,
        }

        # Save portfolio
        with portfolio_file.open("w") as f:
            json.dump(portfolio, f, indent=2)

        logger.debug(f"Portfolio updated with {achievement_type}")

    def get_achievements_summary(self) -> Dict[str, Any]:
        """
        Get summary of achievements and motivation state.

        Returns:
            Dictionary with achievements and stats
        """
        unlocked = [key for key, value in self.milestones.items() if value]
        locked = [key for key, value in self.milestones.items() if not value]

        return {
            "unlocked_achievements": unlocked,
            "locked_achievements": locked,
            "total_unlocked": len(unlocked),
            "total_achievements": len(self.milestones),
            "unlock_percentage": (
                len(unlocked) / len(self.milestones) * 100 if self.milestones else 0
            ),
            "motivation_state": self.motivation_state.to_dict(),
        }

    def _record_achievement(self, achievement_type: str, metadata: Dict[str, Any]) -> None:
        """
        Record achievement to audit log.

        Args:
            achievement_type: Type of achievement
            metadata: Additional context
        """
        achievement_log = self.state_file.parent / "achievement_log.jsonl"

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "achievement": achievement_type,
            "metadata": metadata,
            "motivation_state": self.motivation_state.to_dict(),
        }

        with achievement_log.open("a") as f:
            f.write(json.dumps(record) + "\n")

    def _save_state(self) -> None:
        """Save achievement state to disk."""
        state = {
            "milestones": self.milestones,
            "motivation_state": self.motivation_state.to_dict(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        with self.state_file.open("w") as f:
            json.dump(state, f, indent=2)

    def _load_state(self) -> None:
        """Load achievement state from disk."""
        if not self.state_file.exists():
            return

        try:
            with self.state_file.open("r") as f:
                state = json.load(f)

            self.milestones.update(state.get("milestones", {}))
            mot_data = state.get("motivation_state", {})
            self.motivation_state = MotivationState(**mot_data)

            logger.info(f"Loaded achievement state from {self.state_file}")
        except Exception as e:
            logger.warning(f"Failed to load achievement state: {e}")

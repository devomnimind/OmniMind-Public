from __future__ import annotations

import logging
import math
import random
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


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
Page Curve Learning - Non-Monotonic Knowledge Growth

Implements learning that follows the Page curve from black hole information theory:
entropy first increases (confusion phase), then decreases (consolidation phase).

Based on:
- Page curve (Page, 1993): Information recovery in black hole evaporation
- Von Neumann entropy: S = -Tr(ρ log ρ)
- Entanglement entropy in quantum systems
- Information-theoretic learning dynamics

This enables detection of learning phase transitions and optimal consolidation timing.

Author: OmniMind Development Team
License: MIT
"""


logger = logging.getLogger(__name__)

# Constants
MIN_ENTROPY = 0.0
MAX_ENTROPY_SAMPLES = 1000  # Maximum history to keep
SMOOTHING_WINDOW = 5  # Window for entropy smoothing


class LearningPhase(Enum):
    """Learning phases based on Page curve."""

    INITIALIZATION = "initialization"  # Just started
    CONFUSION = "confusion"  # Entropy rising (pre-Page time)
    PAGE_TIME = "page_time"  # Peak entropy (critical transition)
    CONSOLIDATION = "consolidation"  # Entropy falling (post-Page time)
    SATURATED = "saturated"  # Learning plateau


@dataclass
class PageCurve:
    """
    Page curve data structure.

    Attributes:
        entropy_history: Full entropy evolution
        epochs: Corresponding epoch numbers
        page_time_epoch: Epoch where Page time occurred (if detected)
        max_entropy: Maximum entropy reached
        current_phase: Current learning phase
    """

    entropy_history: List[float]
    epochs: List[int]
    page_time_epoch: Optional[int] = None
    max_entropy: float = 0.0
    current_phase: LearningPhase = LearningPhase.INITIALIZATION


class PageCurveLearner:
    """
    Learning system that follows Page curve dynamics.

    Models learning as information-theoretic process where:
    1. Initial phase: Entropy increases (system explores, gets confused)
    2. Page time: Entropy peaks (critical transition point)
    3. Consolidation: Entropy decreases (information recovery, understanding)

    This mirrors black hole evaporation where information is initially lost,
    then recovered through entanglement correlations.
    """

    def __init__(
        self,
        detection_window: int = 10,
        page_time_threshold: float = 0.95,
        min_epochs_before_page: int = 5,
    ) -> None:
        """
        Initialize Page curve learner.

        Args:
            detection_window: Window size for detecting entropy trends
            page_time_threshold: Fraction of max entropy to trigger Page time
            min_epochs_before_page: Minimum epochs before Page time can occur
        """
        self.detection_window = detection_window
        self.page_time_threshold = page_time_threshold
        self.min_epochs_before_page = min_epochs_before_page

        # Learning history
        self.entropy_history: List[float] = []
        self.epochs: List[int] = []
        self.current_epoch = 0

        # Page curve tracking
        self.page_time_detected = False
        self.page_time_epoch: Optional[int] = None
        self.max_entropy_seen = 0.0
        self.current_phase = LearningPhase.INITIALIZATION

        # Information recovery mode
        self.recovery_mode_active = False

        logger.info("PageCurveLearner initialized")

    def record_epoch(
        self, model_state: Dict[str, Any], loss: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Record learning progress for one epoch.

        Args:
            model_state: Current model state (weights, activations, etc.)
            loss: Optional training loss

        Returns:
            Dict with epoch info, entropy, phase, and recommendations
        """
        # Compute von Neumann entropy
        entropy = self._von_neumann_entropy(model_state)

        # Record
        self.entropy_history.append(entropy)
        self.epochs.append(self.current_epoch)

        # Update max entropy
        if entropy > self.max_entropy_seen:
            self.max_entropy_seen = entropy

        # Detect Page time
        if self._is_page_time():
            if not self.page_time_detected:
                self.page_time_detected = True
                self.page_time_epoch = self.current_epoch
                self._enable_information_recovery_mode()
                logger.info(
                    f"Page time reached at epoch {self.current_epoch} " f"(entropy={entropy:.4f})"
                )

        # Update phase
        self._update_phase()

        # Generate recommendations
        recommendations = self._generate_recommendations()

        self.current_epoch += 1

        return {
            "epoch": self.current_epoch - 1,
            "entropy": entropy,
            "max_entropy": self.max_entropy_seen,
            "phase": self.current_phase.value,
            "page_time_detected": self.page_time_detected,
            "page_time_epoch": self.page_time_epoch,
            "loss": loss,
            "recommendations": recommendations,
            "entropy_trend": self._compute_entropy_trend(),
        }

    def _von_neumann_entropy(self, model_state: Dict[str, Any]) -> float:
        """
        Compute von Neumann entropy of model state.

        S = -Tr(ρ log ρ) where ρ is density matrix

        Approximation: Use correlation matrix of model parameters
        as proxy for density matrix.

        Args:
            model_state: Model state dict

        Returns:
            Von Neumann entropy (in nats)
        """
        # Extract numerical data from model state
        data = self._extract_numerical_data(model_state)

        # Handle edge cases
        if len(data) < 2:
            return MIN_ENTROPY

        # Compute entropy based on data size
        if self._should_use_simple_entropy(data):
            return self._compute_simple_entropy(data)
        else:
            return self._compute_correlation_entropy(data)

    def _extract_numerical_data(self, model_state: Dict[str, Any]) -> List[float]:
        """
        Extract numerical data from model state with fallback.

        Args:
            model_state: Model state dict

        Returns:
            List of numerical values
        """
        # Try different keys in order of preference
        for key in ["weights", "parameters", "activations"]:
            if key in model_state and isinstance(model_state[key], Sequence):
                try:
                    return [float(x) for x in model_state[key]]
                except (ValueError, TypeError):
                    continue

        # Fallback: deterministic random data based on state hash
        return self._generate_fallback_data(model_state)

    def _generate_fallback_data(self, model_state: Dict[str, Any]) -> List[float]:
        """
        Generate deterministic fallback data when no numerical data available.

        Args:
            model_state: Model state dict

        Returns:
            List of pseudo-random values
        """
        state_hash = hash(str(model_state))
        rng = random.Random(state_hash % (2**32))
        return [rng.gauss(0, 1) for _ in range(100)]

    def _should_use_simple_entropy(self, data: List[float]) -> bool:
        """
        Determine if simple entropy calculation should be used.

        Args:
            data: Numerical data

        Returns:
            True if simple entropy should be used
        """
        size = int(math.sqrt(len(data)))
        return size < 2 or size * size > len(data)

    def _compute_simple_entropy(self, data: List[float]) -> float:
        """
        Compute simple Shannon entropy on normalized absolute values.

        Args:
            data: Numerical data

        Returns:
            Entropy value
        """
        abs_vals = [abs(x) for x in data]
        total = sum(abs_vals)

        if total < 1e-10:
            return MIN_ENTROPY

        # Filter and normalize probabilities
        probs = [v / total for v in abs_vals if v / total > 1e-10]

        # Compute entropy
        entropy = -sum(p * math.log(p + 1e-10) for p in probs)
        return float(max(MIN_ENTROPY, entropy))

    def _compute_correlation_entropy(self, data: List[float]) -> float:
        """
        Compute entropy using correlation matrix approximation.

        Args:
            data: Numerical data

        Returns:
            Entropy value
        """
        # For now, fall back to simple entropy
        # TODO: Implement proper correlation matrix entropy calculation
        return self._compute_simple_entropy(data)

    def _is_page_time(self) -> bool:
        """
        Detect if Page time has occurred.

        Page time is when entropy peaks and starts to decrease.
        This is the critical transition from confusion to consolidation.

        Returns:
            True if Page time detected
        """
        if self.page_time_detected:
            return False  # Already detected

        if self.current_epoch < self.min_epochs_before_page:
            return False  # Too early

        if len(self.entropy_history) < self.detection_window:
            return False  # Not enough history

        # Get recent entropy values
        recent = self.entropy_history[-self.detection_window :]

        # Check if we've peaked
        # Page time = entropy stops growing and starts declining
        max_recent = max(recent)
        current = self.entropy_history[-1]

        # Check if current is near max
        if current >= max_recent * self.page_time_threshold:
            # Check if trend is declining
            if self._is_declining_trend(recent):
                return True

        return False

    def _is_declining_trend(self, values: List[float]) -> bool:
        """
        Check if values show declining trend.

        Args:
            values: List of values to check

        Returns:
            True if declining trend detected
        """
        if len(values) < 3:
            return False

        # Compute linear regression slope
        slope = self._linear_regression_slope(values)

        return slope < -1e-6  # Negative slope = declining

    def _update_phase(self) -> None:
        """Update current learning phase based on entropy dynamics."""
        if len(self.entropy_history) < 2:
            self.current_phase = LearningPhase.INITIALIZATION
            return

        if self.page_time_detected:
            if self.recovery_mode_active:
                # Check if still consolidating
                recent_trend = self._compute_entropy_trend()
                if recent_trend < -0.01:
                    self.current_phase = LearningPhase.CONSOLIDATION
                else:
                    self.current_phase = LearningPhase.SATURATED
            else:
                self.current_phase = LearningPhase.PAGE_TIME
        else:
            # Pre-Page time
            recent_trend = self._compute_entropy_trend()
            if recent_trend > 0.01:
                self.current_phase = LearningPhase.CONFUSION
            else:
                self.current_phase = LearningPhase.INITIALIZATION

    def _compute_entropy_trend(self) -> float:
        """
        Compute current entropy trend.

        Returns:
            Trend value (positive = increasing, negative = decreasing)
        """
        if len(self.entropy_history) < SMOOTHING_WINDOW:
            return 0.0

        recent = self.entropy_history[-SMOOTHING_WINDOW:]
        slope = self._linear_regression_slope(recent)
        return float(slope)

    def _linear_regression_slope(self, values: List[float]) -> float:
        """Compute slope of linear regression for y over x=[0..n-1]."""
        n = len(values)
        if n < 2:
            return 0.0
        x_mean = (n - 1) / 2.0
        y_mean = statistics.mean(values)
        cov = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        var = sum((i - x_mean) ** 2 for i in range(n))
        if abs(var) < 1e-12:
            return 0.0
        return cov / var

    def _enable_information_recovery_mode(self) -> None:
        """
        Enable information recovery mode.

        After Page time, system should focus on consolidating
        learned information rather than exploring.
        """
        self.recovery_mode_active = True
        logger.info("Information recovery mode activated")

    def _generate_recommendations(self) -> Dict[str, Any]:
        """
        Generate learning recommendations based on current phase.

        Returns:
            Dict with recommendations
        """
        recommendations: Dict[str, Any] = {
            "continue_training": True,
            "adjust_learning_rate": False,
            "increase_regularization": False,
            "focus_on_consolidation": False,
        }

        if self.current_phase == LearningPhase.CONFUSION:
            recommendations.update(
                {
                    "message": "Exploration phase - entropy rising (expected)",
                    "action": "Continue training, system is exploring",
                }
            )

        elif self.current_phase == LearningPhase.PAGE_TIME:
            recommendations.update(
                {
                    "message": "Critical transition - Page time detected!",
                    "action": "Consider reducing learning rate for consolidation",
                    "adjust_learning_rate": True,
                }
            )

        elif self.current_phase == LearningPhase.CONSOLIDATION:
            recommendations.update(
                {
                    "message": "Information recovery - entropy declining (good!)",
                    "action": "System is consolidating knowledge",
                    "focus_on_consolidation": True,
                    "increase_regularization": True,
                }
            )

        elif self.current_phase == LearningPhase.SATURATED:
            recommendations.update(
                {
                    "message": "Learning saturated - consider stopping",
                    "action": "Minimal gains expected, consider early stopping",
                    "continue_training": False,
                }
            )

        return recommendations

    def get_page_curve(self) -> PageCurve:
        """
        Get complete Page curve data.

        Returns:
            PageCurve object with full history
        """
        return PageCurve(
            entropy_history=self.entropy_history.copy(),
            epochs=self.epochs.copy(),
            page_time_epoch=self.page_time_epoch,
            max_entropy=self.max_entropy_seen,
            current_phase=self.current_phase,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get learning statistics.

        Returns:
            Dict with statistics
        """
        return {
            "total_epochs": len(self.entropy_history),
            "current_epoch": self.current_epoch,
            "current_entropy": (self.entropy_history[-1] if self.entropy_history else 0.0),
            "max_entropy": self.max_entropy_seen,
            "current_phase": self.current_phase.value,
            "page_time_detected": self.page_time_detected,
            "page_time_epoch": self.page_time_epoch,
            "entropy_trend": self._compute_entropy_trend(),
            "recovery_mode_active": self.recovery_mode_active,
        }

    def reset(self) -> None:
        """Reset learner state for new training run."""
        self.entropy_history = []
        self.epochs = []
        self.current_epoch = 0
        self.page_time_detected = False
        self.page_time_epoch = None
        self.max_entropy_seen = 0.0
        self.current_phase = LearningPhase.INITIALIZATION
        self.recovery_mode_active = False

        logger.info("PageCurveLearner reset")

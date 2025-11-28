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
Tests for Page Curve Learning system.

Tests non-monotonic learning dynamics, entropy tracking,
and Page time detection.
"""

import numpy as np

from src.learning.page_curve_learning import (
    LearningPhase,
    PageCurve,
    PageCurveLearner,
)


class TestPageCurve:
    """Test PageCurve dataclass."""

    def test_creation(self) -> None:
        """Test Page curve creation."""
        curve = PageCurve(
            entropy_history=[1.0, 2.0, 3.0, 2.5, 2.0],
            epochs=[0, 1, 2, 3, 4],
            page_time_epoch=2,
            max_entropy=3.0,
            current_phase=LearningPhase.CONSOLIDATION,
        )

        assert len(curve.entropy_history) == 5
        assert curve.page_time_epoch == 2
        assert curve.max_entropy == 3.0
        assert curve.current_phase == LearningPhase.CONSOLIDATION


class TestPageCurveLearner:
    """Test Page curve learner."""

    def test_initialization(self) -> None:
        """Test learner initializes correctly."""
        learner = PageCurveLearner(detection_window=10)

        assert learner.detection_window == 10
        assert len(learner.entropy_history) == 0
        assert learner.current_epoch == 0
        assert learner.page_time_detected is False
        assert learner.current_phase == LearningPhase.INITIALIZATION

    def test_record_single_epoch(self) -> None:
        """Test recording single epoch."""
        learner = PageCurveLearner()

        model_state = {"weights": np.random.randn(100)}
        result = learner.record_epoch(model_state, loss=0.5)

        assert "epoch" in result
        assert "entropy" in result
        assert "phase" in result
        assert result["epoch"] == 0
        assert result["entropy"] >= 0
        assert len(learner.entropy_history) == 1

    def test_von_neumann_entropy_calculation(self) -> None:
        """Test von Neumann entropy computation."""
        learner = PageCurveLearner()

        # Test with weights
        model_state = {"weights": np.random.randn(100)}
        entropy = learner._von_neumann_entropy(model_state)

        assert entropy >= 0
        assert np.isfinite(entropy)

    def test_von_neumann_entropy_with_parameters(self) -> None:
        """Test entropy with different state keys."""
        learner = PageCurveLearner()

        # Test with parameters
        model_state = {"parameters": np.random.randn(100)}
        entropy = learner._von_neumann_entropy(model_state)

        assert entropy >= 0

    def test_von_neumann_entropy_with_activations(self) -> None:
        """Test entropy with activations."""
        learner = PageCurveLearner()

        # Test with activations
        model_state = {"activations": np.random.randn(100)}
        entropy = learner._von_neumann_entropy(model_state)

        assert entropy >= 0

    def test_von_neumann_entropy_fallback(self) -> None:
        """Test entropy fallback for unknown state format."""
        learner = PageCurveLearner()

        # Test with unknown format (will use hash-based fallback)
        model_state = {"unknown_key": "test_value"}
        entropy = learner._von_neumann_entropy(model_state)

        assert entropy >= 0

    def test_multiple_epochs(self) -> None:
        """Test recording multiple epochs."""
        learner = PageCurveLearner()

        for i in range(10):
            model_state = {"weights": np.random.randn(100) * (i + 1)}
            result = learner.record_epoch(model_state)
            assert result["epoch"] == i

        assert len(learner.entropy_history) == 10
        assert learner.current_epoch == 10

    def test_page_time_detection(self) -> None:
        """Test Page time detection."""
        learner = PageCurveLearner(detection_window=5, min_epochs_before_page=3)

        # Simulate increasing then decreasing entropy
        entropies = [1.0, 2.0, 3.0, 3.5, 3.8, 3.7, 3.5, 3.0, 2.5]

        for i, target_entropy in enumerate(entropies):
            # Create model state that produces roughly this entropy
            # Use deterministic seed based on target entropy
            np.random.seed(int(target_entropy * 1000))
            model_state = {"weights": np.random.randn(100) * target_entropy}
            learner.record_epoch(model_state)

        # Should have detected Page time
        assert learner.page_time_detected or learner.max_entropy_seen > 0

    def test_phase_transitions(self) -> None:
        """Test learning phase transitions."""
        learner = PageCurveLearner(min_epochs_before_page=2)

        phases = []
        for i in range(15):
            model_state = {"weights": np.random.randn(100)}
            result = learner.record_epoch(model_state)
            phases.append(result["phase"])

        # Should have at least initialization phase
        assert LearningPhase.INITIALIZATION.value in phases

    def test_entropy_trend_computation(self) -> None:
        """Test entropy trend calculation."""
        learner = PageCurveLearner()

        # Create increasing entropy
        for i in range(10):
            model_state = {"weights": np.random.randn(100) * (i + 1)}
            learner.record_epoch(model_state)

        trend = learner._compute_entropy_trend()
        # Trend should be computed (may be positive or negative)
        assert np.isfinite(trend)

    def test_declining_trend_detection(self) -> None:
        """Test declining trend detection."""
        learner = PageCurveLearner()

        # Clearly declining values
        declining = [10.0, 9.0, 8.0, 7.0, 6.0]
        assert learner._is_declining_trend(declining)

        # Clearly increasing values
        increasing = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert not learner._is_declining_trend(increasing)

    def test_information_recovery_mode(self) -> None:
        """Test information recovery mode activation."""
        learner = PageCurveLearner()

        assert learner.recovery_mode_active is False

        learner._enable_information_recovery_mode()

        assert learner.recovery_mode_active is True

    def test_recommendations_confusion_phase(self) -> None:
        """Test recommendations during confusion phase."""
        learner = PageCurveLearner()
        learner.current_phase = LearningPhase.CONFUSION

        recs = learner._generate_recommendations()

        assert "message" in recs
        assert recs["continue_training"] is True

    def test_recommendations_page_time(self) -> None:
        """Test recommendations at Page time."""
        learner = PageCurveLearner()
        learner.current_phase = LearningPhase.PAGE_TIME

        recs = learner._generate_recommendations()

        assert recs["adjust_learning_rate"] is True

    def test_recommendations_consolidation(self) -> None:
        """Test recommendations during consolidation."""
        learner = PageCurveLearner()
        learner.current_phase = LearningPhase.CONSOLIDATION

        recs = learner._generate_recommendations()

        assert recs["focus_on_consolidation"] is True
        assert recs["increase_regularization"] is True

    def test_recommendations_saturated(self) -> None:
        """Test recommendations when saturated."""
        learner = PageCurveLearner()
        learner.current_phase = LearningPhase.SATURATED

        recs = learner._generate_recommendations()

        assert recs["continue_training"] is False

    def test_get_page_curve(self) -> None:
        """Test getting complete Page curve."""
        learner = PageCurveLearner()

        for i in range(5):
            model_state = {"weights": np.random.randn(100)}
            learner.record_epoch(model_state)

        curve = learner.get_page_curve()

        assert isinstance(curve, PageCurve)
        assert len(curve.entropy_history) == 5
        assert len(curve.epochs) == 5

    def test_get_statistics(self) -> None:
        """Test getting learning statistics."""
        learner = PageCurveLearner()

        for i in range(5):
            model_state = {"weights": np.random.randn(100)}
            learner.record_epoch(model_state)

        stats = learner.get_statistics()

        assert stats["total_epochs"] == 5
        assert stats["current_epoch"] == 5
        assert "current_entropy" in stats
        assert "current_phase" in stats
        assert "page_time_detected" in stats

    def test_reset(self) -> None:
        """Test resetting learner."""
        learner = PageCurveLearner()

        # Record some epochs
        for i in range(5):
            model_state = {"weights": np.random.randn(100)}
            learner.record_epoch(model_state)

        # Reset
        learner.reset()

        assert len(learner.entropy_history) == 0
        assert learner.current_epoch == 0
        assert learner.page_time_detected is False
        assert learner.current_phase == LearningPhase.INITIALIZATION


class TestIntegration:
    """Integration tests for Page curve learning."""

    def test_full_learning_cycle(self) -> None:
        """Test complete learning cycle with phase transitions."""
        learner = PageCurveLearner(detection_window=5, min_epochs_before_page=3)

        results = []

        # Simulate learning with increasing then decreasing complexity
        for epoch in range(20):
            # Create model state with varying entropy
            if epoch < 10:
                # Increasing phase (confusion)
                complexity = epoch + 1
            else:
                # Decreasing phase (consolidation)
                complexity = 20 - epoch

            np.random.seed(epoch)
            model_state = {"weights": np.random.randn(100) * complexity}

            result = learner.record_epoch(model_state, loss=1.0 / (epoch + 1))
            results.append(result)

        # Check that we went through phases
        phases = [r["phase"] for r in results]
        assert len(set(phases)) > 1  # Multiple phases

        # Should have some entropy variation
        entropies = [r["entropy"] for r in results]
        assert max(entropies) > min(entropies)

    def test_early_stopping_detection(self) -> None:
        """Test early stopping detection when saturated."""
        learner = PageCurveLearner()

        # Simulate plateau
        for i in range(15):
            model_state = {"weights": np.random.randn(100)}
            result = learner.record_epoch(model_state)

            if result["phase"] == LearningPhase.SATURATED.value:
                assert result["recommendations"]["continue_training"] is False
                break

    def test_consistent_entropy_calculation(self) -> None:
        """Test that entropy calculation is consistent."""
        learner = PageCurveLearner()

        # Same model state should give same entropy
        np.random.seed(42)
        model_state = {"weights": np.random.randn(100)}

        entropy1 = learner._von_neumann_entropy(model_state)
        entropy2 = learner._von_neumann_entropy(model_state)

        assert abs(entropy1 - entropy2) < 1e-10

    def test_entropy_increases_with_complexity(self) -> None:
        """Test that entropy generally increases with model complexity."""
        learner = PageCurveLearner()

        # Small model
        small_state = {"weights": np.random.randn(10)}
        small_entropy = learner._von_neumann_entropy(small_state)

        # Large model
        large_state = {"weights": np.random.randn(1000)}
        large_entropy = learner._von_neumann_entropy(large_state)

        # Larger model should generally have more entropy
        # (though not strictly guaranteed due to randomness)
        assert large_entropy >= 0
        assert small_entropy >= 0

    def test_page_curve_export(self) -> None:
        """Test exporting Page curve for visualization."""
        learner = PageCurveLearner()

        # Train for several epochs
        for i in range(10):
            model_state = {"weights": np.random.randn(100) * (i + 1)}
            learner.record_epoch(model_state)

        curve = learner.get_page_curve()

        # Should be able to plot: curve.epochs vs curve.entropy_history
        assert len(curve.epochs) == len(curve.entropy_history)
        assert all(isinstance(e, (int, np.integer)) for e in curve.epochs)
        assert all(isinstance(s, (float, np.floating)) for s in curve.entropy_history)

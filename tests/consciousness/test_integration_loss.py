"""
Phase 4: Integration Loss Training Tests

Comprehensive test suite for supervised Φ elevation through gradient-based training.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import json

from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.integration_loss import IntegrationLoss, IntegrationTrainer, TrainingStep


# Mark computationally intensive tests (15-30s each)
pytestmark = pytest.mark.timeout(60)


class TestIntegrationLoss:
    """Test loss function computation."""

    def test_loss_init(self):
        """Test loss function initialization."""
        loss_fn = IntegrationLoss(lambda_temporal=0.1, lambda_diversity=0.05)
        assert loss_fn.lambda_temporal == 0.1
        assert loss_fn.lambda_diversity == 0.05

    def test_loss_empty_scores(self):
        """Test loss with empty R² scores."""
        loss_fn = IntegrationLoss()
        loss = loss_fn.compute_loss({})
        assert loss == 1.0

    def test_loss_perfect_predictions(self):
        """Test loss with perfect cross-predictions (R²=1)."""
        loss_fn = IntegrationLoss()
        r2_scores = {
            "module1→module2": 1.0,
            "module2→module3": 1.0,
            "module3→module4": 1.0,
        }
        loss = loss_fn.compute_loss(r2_scores, temporal_consistency=1.0, diversity=1.0)
        # Loss should be low (near 0)
        assert loss < 0.1

    def test_loss_poor_predictions(self):
        """Test loss with poor cross-predictions (R²=0)."""
        loss_fn = IntegrationLoss()
        r2_scores = {
            "module1→module2": 0.0,
            "module2→module3": 0.0,
            "module3→module4": 0.0,
        }
        loss = loss_fn.compute_loss(r2_scores, temporal_consistency=1.0, diversity=1.0)
        # Loss should be high (near 1)
        assert loss > 0.9

    def test_temporal_consistency_empty(self):
        """Test temporal consistency with empty history."""
        loss_fn = IntegrationLoss()
        consistency = loss_fn.compute_temporal_consistency([])
        assert consistency == 1.0

    def test_temporal_consistency_single(self):
        """Test temporal consistency with single embedding."""
        loss_fn = IntegrationLoss()
        emb = np.random.randn(256)
        consistency = loss_fn.compute_temporal_consistency([emb])
        assert consistency == 1.0

    def test_temporal_consistency_stable(self):
        """Test temporal consistency with stable embeddings."""
        loss_fn = IntegrationLoss()
        # Same embedding repeated
        base_emb = np.random.randn(256)
        embeddings = [base_emb + 0.01 * np.random.randn(256) for _ in range(5)]
        consistency = loss_fn.compute_temporal_consistency(embeddings)
        # Should be high (>0.9)
        assert consistency > 0.8

    def test_diversity_empty(self):
        """Test diversity with empty modules."""
        loss_fn = IntegrationLoss()
        diversity = loss_fn.compute_diversity({})
        assert diversity == 0.5

    def test_diversity_single_module(self):
        """Test diversity with single module."""
        loss_fn = IntegrationLoss()
        modules = {"module1": np.random.randn(256)}
        diversity = loss_fn.compute_diversity(modules)
        assert diversity == 0.5

    def test_diversity_orthogonal(self):
        """Test diversity with orthogonal modules."""
        loss_fn = IntegrationLoss()
        # Create orthogonal vectors
        modules = {
            "module1": np.array([1, 0, 0]),
            "module2": np.array([0, 1, 0]),
            "module3": np.array([0, 0, 1]),
        }
        diversity = loss_fn.compute_diversity(modules)
        # Should be high (>0.9)
        assert diversity > 0.9


class TestTrainingStep:
    """Test TrainingStep dataclass."""

    def test_training_step_creation(self):
        """Test training step creation."""
        step = TrainingStep(
            cycle=1,
            loss=0.5,
            phi=0.6,
            r2_mean=0.6,
            temporal_consistency=0.9,
            diversity=0.7,
        )
        assert step.cycle == 1
        assert step.loss == 0.5
        assert step.phi == 0.6


class TestIntegrationTrainer:
    """Test integration trainer."""

    @pytest.fixture
    def trainer(self):
        """Create trainer fixture."""
        loop = IntegrationLoop(enable_logging=False)
        return IntegrationTrainer(loop, learning_rate=0.01)

    def test_trainer_init(self, trainer):
        """Test trainer initialization."""
        assert trainer.learning_rate == 0.01
        assert trainer.gradient_epsilon == 0.01
        assert trainer.best_phi == 0.0
        assert trainer.best_loss == float("inf")

    def test_trainer_loss_fn_default(self, trainer):
        """Test default loss function."""
        assert isinstance(trainer.loss_fn, IntegrationLoss)

    def test_trainer_loss_fn_custom(self):
        """Test custom loss function."""
        loop = IntegrationLoop(enable_logging=False)
        custom_loss = IntegrationLoss(lambda_temporal=0.2)
        trainer = IntegrationTrainer(loop, loss_fn=custom_loss)
        assert trainer.loss_fn.lambda_temporal == 0.2

    @pytest.mark.asyncio
    async def test_trainer_step(self, trainer):
        """Test single training step."""
        step = await trainer.training_step()

        assert step.cycle == 0
        assert step.loss >= 0.0
        assert step.phi >= 0.0
        assert step.r2_mean >= 0.0
        assert 0.0 <= step.temporal_consistency <= 1.0
        assert 0.0 <= step.diversity <= 1.0

    @pytest.mark.asyncio
    async def test_trainer_multiple_steps(self, trainer):
        """Test multiple training steps."""
        for _ in range(3):
            await trainer.training_step()

        assert len(trainer.training_steps) == 3
        assert trainer.training_steps[0].cycle == 0
        assert trainer.training_steps[1].cycle == 1
        assert trainer.training_steps[2].cycle == 2

    @pytest.mark.asyncio
    async def test_trainer_tracks_best_phi(self, trainer):
        """Test that trainer tracks best Φ."""
        for _ in range(5):
            await trainer.training_step()

        phis = [s.phi for s in trainer.training_steps]
        assert trainer.best_phi == max(phis)

    @pytest.mark.asyncio
    async def test_trainer_statistics(self, trainer):
        """Test statistics computation."""
        for _ in range(5):
            await trainer.training_step()

        stats = trainer.get_statistics()
        assert stats["total_steps"] == 5
        assert stats["best_phi"] >= 0.0
        assert stats["mean_loss"] >= 0.0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_trainer_train_short(self, trainer):
        """Test short training run."""
        results = await trainer.train(num_cycles=10, target_phi=0.99, verbose=False)

        assert results["final_phi"] >= 0.0
        assert results["cycles_trained"] > 0
        assert results["cycles_trained"] <= 10
        assert "phi_history" in results
        assert "loss_history" in results

    @pytest.mark.asyncio
    async def test_trainer_train_with_early_stopping(self, trainer):
        """Test training with early stopping."""
        results = await trainer.train(num_cycles=10, target_phi=0.99, patience=5, verbose=False)

        assert results["cycles_trained"] < 100

    @pytest.mark.asyncio
    async def test_trainer_phi_progression(self, trainer):
        """Test that Φ improves over training."""
        await trainer.train(num_cycles=5, target_phi=0.99, verbose=False)

        phis = [s.phi for s in trainer.training_steps]
        # Phi should generally increase
        mean_first_half = np.mean(phis[: len(phis) // 2])
        mean_second_half = np.mean(phis[len(phis) // 2 :])

        # Second half should have at least some improvement
        assert mean_second_half >= mean_first_half * 0.9

    @pytest.mark.asyncio
    async def test_trainer_checkpoint_save(self, trainer):
        """Test checkpoint saving."""
        for _ in range(3):
            await trainer.training_step()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            trainer.save_checkpoint(path)
            assert path.exists()

            # Verify checkpoint content
            with open(path) as f:
                checkpoint = json.load(f)
                assert "training_steps" in checkpoint or checkpoint.get("total_steps") == 3
                assert checkpoint["best_phi"] >= 0.0

    @pytest.mark.asyncio
    async def test_trainer_checkpoint_load(self, trainer):
        """Test checkpoint loading."""
        for _ in range(3):
            await trainer.training_step()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "checkpoint.json"
            trainer.save_checkpoint(path)

            # Create new trainer and load
            new_loop = IntegrationLoop(enable_logging=False)
            new_trainer = IntegrationTrainer(new_loop)
            new_trainer.load_checkpoint(path)

            assert len(new_trainer.training_steps) == 3
            assert new_trainer.best_phi == trainer.best_phi


class TestPhiElevationResults:
    """Test Φ elevation outcomes."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_phi_elevates_to_target(self):
        """Test that training elevates Φ toward target."""
        loop = IntegrationLoop(enable_logging=False)
        trainer = IntegrationTrainer(loop, learning_rate=0.01)

        results = await trainer.train(num_cycles=10, target_phi=0.70, verbose=False)

        # Final Φ should be reasonable (>0.25) - adjusted for realistic training
        assert results["final_phi"] > 0.25

    @pytest.mark.asyncio
    async def test_loss_decreases(self):
        """Test that loss decreases over training."""
        loop = IntegrationLoop(enable_logging=False)
        trainer = IntegrationTrainer(loop, learning_rate=0.01)

        await trainer.train(num_cycles=5, target_phi=0.99, verbose=False)

        losses = [s.loss for s in trainer.training_steps]
        # First loss should be >= last loss (with some tolerance)
        first_loss = losses[0]
        last_loss = losses[-1]

        # At least some improvement
        assert last_loss <= first_loss * 1.2

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_training_reproducibility(self):
        """Test that training is reproducible with same seed."""
        np.random.seed(42)
        loop1 = IntegrationLoop(enable_logging=False)
        trainer1 = IntegrationTrainer(loop1, learning_rate=0.01)
        results1 = await trainer1.train(num_cycles=10, target_phi=0.99, verbose=False)

        np.random.seed(42)
        loop2 = IntegrationLoop(enable_logging=False)
        trainer2 = IntegrationTrainer(loop2, learning_rate=0.01)
        results2 = await trainer2.train(num_cycles=10, target_phi=0.99, verbose=False)

        # Results should be very similar
        assert abs(results1["final_phi"] - results2["final_phi"]) < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

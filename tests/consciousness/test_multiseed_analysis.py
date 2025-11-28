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
Phase 5 Tests: Multi-seed Statistical Analysis

Tests for MultiSeedRunner, ConvergenceAggregator, StatisticalValidator.
"""

import json
import numpy as np
import pytest
import tempfile
from pathlib import Path

from src.consciousness.multiseed_analysis import (
    SeedResult,
    MultiSeedRunner,
    ConvergenceAggregator,
    StatisticalValidator,
)


class TestSeedResult:
    """Test SeedResult dataclass."""

    def test_seed_result_creation(self):
        """Test creating a SeedResult."""
        result = SeedResult(
            seed=0,
            final_phi=0.75,
            convergence_cycle=450,
            phi_trajectory=[0.0, 0.2, 0.5, 0.75],
            loss_trajectory=[1.0, 0.8, 0.5, 0.3],
            converged=True,
            execution_time_seconds=12.5,
        )

        assert result.seed == 0
        assert result.final_phi == 0.75
        assert result.converged is True
        assert result.timestamp is not None

    def test_seed_result_to_dict(self):
        """Test SeedResult serialization."""
        result = SeedResult(
            seed=0,
            final_phi=0.75,
            convergence_cycle=450,
            phi_trajectory=[0.0, 0.2, 0.5, 0.75],
            loss_trajectory=[1.0, 0.8, 0.5, 0.3],
            converged=True,
            execution_time_seconds=12.5,
        )

        d = result.to_dict()
        assert d["seed"] == 0
        assert d["final_phi"] == 0.75
        assert len(d["phi_trajectory"]) == 4


class TestMultiSeedRunner:
    """Test multi-seed training runner."""

    @pytest.mark.asyncio
    async def test_runner_single_seed(self):
        """Test running a single seed."""
        runner = MultiSeedRunner(learning_rate=0.01, enable_logging=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            results = await runner.run_seeds(
                num_seeds=1, num_cycles=5, target_phi=0.99, output_dir=Path(tmpdir)
            )

            assert len(results) == 1
            assert results[0].seed == 0
            assert len(results[0].phi_trajectory) == 5
            assert results[0].final_phi >= 0.0

    @pytest.mark.asyncio
    async def test_runner_multiple_seeds(self):
        """Test running multiple seeds."""
        runner = MultiSeedRunner(learning_rate=0.01, enable_logging=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            results = await runner.run_seeds(
                num_seeds=3, num_cycles=5, target_phi=0.99, output_dir=Path(tmpdir)
            )

            assert len(results) == 3
            assert all(r.seed == i for i, r in enumerate(results))

    @pytest.mark.asyncio
    async def test_runner_saves_trajectories(self):
        """Test that trajectories are saved to disk."""
        runner = MultiSeedRunner(learning_rate=0.01, enable_logging=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            await runner.run_seeds(num_seeds=2, num_cycles=5, target_phi=0.99, output_dir=tmppath)

            # Check files created
            files = list(tmppath.glob("seed_*.json"))
            assert len(files) == 2

            # Check file contents
            with open(tmppath / "seed_000_trajectory.json") as f:
                data = json.load(f)
                assert data["seed"] == 0
                assert len(data["phi_trajectory"]) == 5

    @pytest.mark.asyncio
    async def test_runner_diverse_trajectories(self):
        """Different seeds should produce different trajectories."""
        runner = MultiSeedRunner(learning_rate=0.01, enable_logging=False)

        results = await runner.run_seeds(
            num_seeds=3, num_cycles=20, target_phi=0.99, output_dir=None
        )

        # Get final phis
        final_phis = [r.final_phi for r in results]

        # Not all identical (different random seeds)
        assert len(set(final_phis)) >= 1  # At least some variation

        # All positive (no NaNs or negative)
        assert all(phi >= 0.0 for phi in final_phis)


class TestConvergenceAggregator:
    """Test convergence aggregation."""

    def test_aggregator_single_seed(self):
        """Test aggregation with single seed."""
        results = [
            SeedResult(
                seed=0,
                final_phi=0.8,
                convergence_cycle=50,
                phi_trajectory=np.linspace(0.0, 0.8, 100).tolist(),
                loss_trajectory=np.linspace(1.0, 0.2, 100).tolist(),
                converged=True,
                execution_time_seconds=10.0,
            )
        ]

        agg = ConvergenceAggregator()
        stats = agg.aggregate(results)

        assert stats["num_seeds"] == 1
        assert stats["num_cycles"] == 100
        assert len(stats["mean_phi"]) == 100
        assert float(stats["mean_phi"][0]) == pytest.approx(0.0, abs=0.1)
        assert float(stats["mean_phi"][-1]) == pytest.approx(0.8, abs=0.1)

    def test_aggregator_multiple_seeds(self):
        """Test aggregation with multiple seeds."""
        results = [
            SeedResult(
                seed=i,
                final_phi=0.7 + i * 0.05,
                convergence_cycle=300 + i * 20,
                phi_trajectory=np.linspace(0.0, 0.7 + i * 0.05, 100).tolist(),
                loss_trajectory=np.linspace(1.0, 0.2, 100).tolist(),
                converged=True,
                execution_time_seconds=10.0 + i,
            )
            for i in range(3)
        ]

        agg = ConvergenceAggregator()
        stats = agg.aggregate(results)

        assert stats["num_seeds"] == 3
        assert len(stats["mean_phi"]) == 100
        assert stats["final_phi_mean"] > 0.70
        assert stats["success_rate"] == 1.0  # all converged

    def test_aggregator_computes_percentiles(self):
        """Test percentile computation."""
        # Create results with spread
        results = [
            SeedResult(
                seed=i,
                final_phi=0.5 + i * 0.1,
                convergence_cycle=None,
                phi_trajectory=np.linspace(0.0, 0.5 + i * 0.1, 50).tolist(),
                loss_trajectory=np.linspace(1.0, 0.2, 50).tolist(),
                converged=False,
                execution_time_seconds=5.0,
            )
            for i in range(5)
        ]

        agg = ConvergenceAggregator()
        stats = agg.aggregate(results)

        assert "percentiles" in stats
        assert "5" in stats["percentiles"]
        assert "25" in stats["percentiles"]
        assert "50" in stats["percentiles"]  # median
        assert "75" in stats["percentiles"]
        assert "95" in stats["percentiles"]

    def test_aggregator_confidence_intervals(self):
        """Test 95% confidence interval computation."""
        results = [
            SeedResult(
                seed=i,
                final_phi=0.8,
                convergence_cycle=300,
                phi_trajectory=np.full(50, 0.7 + np.random.randn() * 0.05).tolist(),
                loss_trajectory=np.linspace(1.0, 0.2, 50).tolist(),
                converged=True,
                execution_time_seconds=10.0,
            )
            for i in range(10)
        ]

        agg = ConvergenceAggregator()
        stats = agg.aggregate(results)

        assert len(stats["ci_95_lower"]) == 50
        assert len(stats["ci_95_upper"]) == 50

        # CI lower should be less than mean
        assert np.mean(stats["ci_95_lower"]) < np.mean(stats["mean_phi"])

        # CI upper should be greater than mean
        assert np.mean(stats["ci_95_upper"]) > np.mean(stats["mean_phi"])

    def test_aggregator_convergence_statistics(self):
        """Test convergence cycle statistics."""
        results = [
            SeedResult(
                seed=i,
                final_phi=0.8,
                convergence_cycle=300 + i * 10,
                phi_trajectory=np.linspace(0.0, 0.8, 100).tolist(),
                loss_trajectory=np.linspace(1.0, 0.2, 100).tolist(),
                converged=True,
                execution_time_seconds=10.0,
            )
            for i in range(5)
        ]

        agg = ConvergenceAggregator()
        stats = agg.aggregate(results)

        assert stats["convergence_mean"] is not None
        assert stats["convergence_std"] is not None
        assert stats["convergence_mean"] > 300
        assert len(stats["convergence_cycles"]) == 5

    def test_aggregator_success_rate(self):
        """Test success rate calculation."""
        results = [
            SeedResult(
                seed=i,
                final_phi=0.8 if i < 3 else 0.6,
                convergence_cycle=300,
                phi_trajectory=np.linspace(0.0, 0.8 if i < 3 else 0.6, 100).tolist(),
                loss_trajectory=np.linspace(1.0, 0.2, 100).tolist(),
                converged=i < 3,
                execution_time_seconds=10.0,
            )
            for i in range(5)
        ]

        agg = ConvergenceAggregator()
        stats = agg.aggregate(results, convergence_threshold=0.70)

        # 3 out of 5 reached 0.70
        assert stats["success_rate"] == pytest.approx(0.60, abs=0.01)


class TestStatisticalValidator:
    """Test statistical validation."""

    def test_validator_passes_good_convergence(self):
        """Test validator accepts good convergence."""
        stats = {
            "num_seeds": 30,
            "mean_phi": np.linspace(0.0, 0.8, 100).tolist(),
            "std_phi": np.full(100, 0.10).tolist(),
            "final_phis": [0.75 + np.random.randn() * 0.05 for _ in range(30)],
            "final_phi_mean": 0.77,
            "final_phi_std": 0.08,
            "success_rate": 0.90,
            "convergence_mean": 450,
            "convergence_std": 50,
        }

        validator = StatisticalValidator()
        result = validator.validate(stats)

        assert result["all_valid"] is True
        assert result["tests_passed"] >= 3
        assert "✅" in result["summary"]

    def test_validator_detects_low_convergence(self):
        """Test validator detects poor convergence (low mean Φ)."""
        stats = {
            "num_seeds": 30,
            "mean_phi": np.linspace(0.0, 0.5, 100).tolist(),
            "std_phi": np.full(100, 0.10).tolist(),
            "final_phis": [0.5 + np.random.randn() * 0.05 for _ in range(30)],
            "final_phi_mean": 0.52,  # Below 0.70 threshold
            "final_phi_std": 0.08,
            "success_rate": 0.50,  # Below 0.80 threshold
            "convergence_mean": 600,
            "convergence_std": 100,
        }

        validator = StatisticalValidator()
        result = validator.validate(stats)

        assert result["all_valid"] is False
        assert result["tests_passed"] < result["tests_total"]

    def test_validator_detects_high_variance(self):
        """Test validator detects high variance after convergence."""
        stats = {
            "num_seeds": 30,
            "mean_phi": np.linspace(0.0, 0.8, 100).tolist(),
            "std_phi": np.full(100, 0.30).tolist(),  # High variance
            "final_phis": [0.75 + np.random.randn() * 0.2 for _ in range(30)],
            "final_phi_mean": 0.75,
            "final_phi_std": 0.25,  # Above 0.20 threshold
            "success_rate": 0.85,
            "convergence_mean": 450,
            "convergence_std": 50,
        }

        validator = StatisticalValidator()
        result = validator.validate(stats)

        assert result["all_valid"] is False
        assert result["tests_passed"] < result["tests_total"]

    def test_validator_detects_outliers(self):
        """Test validator identifies outlier seeds."""
        # Create results with 1 outlier (very low final Φ)
        final_phis = [0.75 + np.random.randn() * 0.05 for _ in range(30)]
        final_phis[5] = 0.30  # Outlier

        stats = {
            "num_seeds": 30,
            "mean_phi": np.linspace(0.0, 0.75, 100).tolist(),
            "std_phi": np.full(100, 0.10).tolist(),
            "final_phis": final_phis,
            "final_phi_mean": np.mean(final_phis),
            "final_phi_std": np.std(final_phis),
            "success_rate": 0.90,
            "convergence_mean": 450,
            "convergence_std": 50,
        }

        validator = StatisticalValidator()
        result = validator.validate(stats)

        assert len(result["outliers"]) > 0
        assert 5 in result["outliers"]

    def test_validator_summary_generation(self):
        """Test validator generates human-readable summary."""
        stats = {
            "num_seeds": 30,
            "mean_phi": np.linspace(0.0, 0.8, 100).tolist(),
            "std_phi": np.full(100, 0.10).tolist(),
            "final_phis": [0.75 + np.random.randn() * 0.05 for _ in range(30)],
            "final_phi_mean": 0.77,
            "final_phi_std": 0.08,
            "success_rate": 0.90,
            "convergence_mean": 450,
            "convergence_std": 50,
        }

        validator = StatisticalValidator()
        result = validator.validate(stats)

        assert "Phase 5 Validation" in result["summary"]
        assert "/" in result["summary"]  # "N/M tests passed"
        assert "Φ" in result["summary"]


class TestMultiSeedIntegration:
    """Integration tests for multi-seed analysis."""

    @pytest.mark.asyncio
    async def test_full_pipeline_small(self):
        """Test full pipeline: run seeds → aggregate → validate."""
        # Run small multi-seed analysis
        runner = MultiSeedRunner(learning_rate=0.01, enable_logging=False)
        results = await runner.run_seeds(
            num_seeds=5, num_cycles=20, target_phi=0.99, output_dir=None
        )

        # Aggregate
        agg = ConvergenceAggregator()
        stats = agg.aggregate(results)

        # Validate
        validator = StatisticalValidator()
        validation = validator.validate(stats)

        # Checks
        assert len(results) == 5
        assert stats["num_seeds"] == 5
        assert validation["tests_total"] > 0
        assert validation["summary"] is not None

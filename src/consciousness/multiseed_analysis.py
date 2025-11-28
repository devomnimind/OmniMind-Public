from __future__ import annotations

import json
import logging
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.integration_loss import IntegrationTrainer


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
Phase 5: Multi-seed Statistical Analysis - Convergence Validation

Runs N independent training seeds to establish statistical validity of Φ elevation.
Computes convergence curves with confidence bands and validates reproducibility.

Author: OmniMind Development Team
Date: November 2025
License: MIT
"""


logger = logging.getLogger(__name__)


@dataclass
class SeedResult:
    """Result from single seed training run."""

    seed: int
    final_phi: float
    convergence_cycle: Optional[int]  # When Φ first exceeded 0.70
    phi_trajectory: List[float]
    loss_trajectory: List[float]
    converged: bool
    execution_time_seconds: float
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "final_phi": self.final_phi,
            "convergence_cycle": self.convergence_cycle,
            "phi_trajectory": self.phi_trajectory,
            "loss_trajectory": self.loss_trajectory,
            "converged": self.converged,
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp,
        }


class MultiSeedRunner:
    """Execute N independent training runs with different seeds."""

    def __init__(self, learning_rate: float = 0.01, enable_logging: bool = False):
        """
        Initialize runner.

        Args:
            learning_rate: Training learning rate
            enable_logging: Enable verbose logging
        """
        self.learning_rate = learning_rate
        self.enable_logging = enable_logging

    async def run_seeds(
        self,
        num_seeds: int = 30,
        num_cycles: int = 1000,
        target_phi: float = 0.80,
        convergence_threshold: float = 0.70,
        output_dir: Optional[Path] = None,
    ) -> List[SeedResult]:
        """
        Run N independent training sessions.

        Args:
            num_seeds: Number of seeds to run
            num_cycles: Cycles per seed
            target_phi: Target Φ value
            convergence_threshold: Φ threshold for "converged"
            output_dir: Directory to save trajectories

        Returns:
            List of SeedResult objects, one per seed
        """
        if output_dir is None:
            output_dir = Path("data/consciousness/multiseed_results")
        output_dir.mkdir(parents=True, exist_ok=True)

        results: List[SeedResult] = []
        logger.info(
            f"Starting {num_seeds} seed training runs "
            f"({num_cycles} cycles each, target Φ={target_phi})"
        )

        for seed_idx in range(num_seeds):
            logger.info(f"[{seed_idx+1}/{num_seeds}] Starting seed {seed_idx}...")

            try:
                result = await self._run_single_seed(
                    seed=seed_idx,
                    num_cycles=num_cycles,
                    target_phi=target_phi,
                    convergence_threshold=convergence_threshold,
                )

                results.append(result)

                # Save individual result
                result_file = output_dir / f"seed_{seed_idx:03d}_trajectory.json"
                with open(result_file, "w") as f:
                    json.dump(result.to_dict(), f, indent=2)

                logger.info(
                    f"[{seed_idx+1}/{num_seeds}] Completed: "
                    f"final_φ={result.final_phi:.4f}, "
                    f"converged={result.converged}, "
                    f"time={result.execution_time_seconds:.1f}s"
                )

            except Exception as e:
                logger.error(f"[{seed_idx+1}/{num_seeds}] Seed {seed_idx} failed: {e}")
                continue

        logger.info(f"Completed {len(results)}/{num_seeds} seeds successfully")
        return results

    async def _run_single_seed(
        self,
        seed: int,
        num_cycles: int,
        target_phi: float,
        convergence_threshold: float,
    ) -> SeedResult:
        """Run single seed with independent random state."""
        start_time = datetime.now()

        # Set seed for reproducibility
        np.random.seed(seed)

        # Create fresh loop & trainer for this seed
        loop = IntegrationLoop(enable_logging=self.enable_logging)
        trainer = IntegrationTrainer(loop, learning_rate=self.learning_rate)

        # Track trajectories
        phi_trajectory: List[float] = []
        loss_trajectory: List[float] = []
        convergence_cycle: Optional[int] = None

        # Run training loop
        for cycle in range(num_cycles):
            step = await trainer.training_step()

            phi_trajectory.append(step.phi)
            loss_trajectory.append(step.loss)

            # Detect convergence
            if convergence_cycle is None and step.phi >= convergence_threshold:
                convergence_cycle = cycle

        end_time = datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()

        final_phi = phi_trajectory[-1] if phi_trajectory else 0.0
        converged = final_phi >= target_phi

        return SeedResult(
            seed=seed,
            final_phi=final_phi,
            convergence_cycle=convergence_cycle,
            phi_trajectory=phi_trajectory,
            loss_trajectory=loss_trajectory,
            converged=converged,
            execution_time_seconds=duration_seconds,
        )


class ConvergenceAggregator:
    """Aggregate multi-seed results into statistical summary."""

    @staticmethod
    def aggregate(
        seed_results: List[SeedResult], convergence_threshold: float = 0.70
    ) -> Dict[str, Any]:
        """
        Combine results from all seeds.

        Args:
            seed_results: Results from MultiSeedRunner
            convergence_threshold: Φ threshold for convergence

        Returns:
            Aggregated statistics dictionary
        """
        if not seed_results:
            return {}

        # Align trajectories to common length
        max_length = max(len(r.phi_trajectory) for r in seed_results)

        # Pad shorter trajectories or truncate longer ones
        trajectories = []
        for result in seed_results:
            trajectory = result.phi_trajectory[:max_length]
            if len(trajectory) < max_length:
                # Pad with final value
                trajectory = trajectory + [trajectory[-1]] * (max_length - len(trajectory))
            trajectories.append(trajectory)

        trajectories_array = np.array(trajectories)  # shape: (num_seeds, max_length)

        # Compute statistics per time step
        mean_phi = np.mean(trajectories_array, axis=0)
        std_phi = np.std(trajectories_array, axis=0)

        # Confidence intervals (95%)
        ci_lower = np.percentile(trajectories_array, 2.5, axis=0)
        ci_upper = np.percentile(trajectories_array, 97.5, axis=0)

        # Percentiles
        percentiles = {
            "5": np.percentile(trajectories_array, 5, axis=0),
            "25": np.percentile(trajectories_array, 25, axis=0),
            "50": np.percentile(trajectories_array, 50, axis=0),  # median
            "75": np.percentile(trajectories_array, 75, axis=0),
            "95": np.percentile(trajectories_array, 95, axis=0),
        }

        # Final phi statistics
        final_phis = np.array([r.final_phi for r in seed_results])
        final_phi_mean = float(np.mean(final_phis))
        final_phi_std = float(np.std(final_phis))

        # Convergence statistics
        convergence_cycles = [
            r.convergence_cycle for r in seed_results if r.convergence_cycle is not None
        ]
        convergence_mean = float(np.mean(convergence_cycles)) if convergence_cycles else None
        convergence_std = float(np.std(convergence_cycles)) if convergence_cycles else None

        # Success rate (reached convergence threshold)
        success_rate = float(np.mean([r.final_phi >= convergence_threshold for r in seed_results]))

        # Execution time statistics
        execution_times = np.array([r.execution_time_seconds for r in seed_results])
        execution_time_mean = float(np.mean(execution_times))
        execution_time_total = float(np.sum(execution_times))

        return {
            "num_seeds": len(seed_results),
            "num_cycles": max_length,
            "mean_phi": mean_phi.tolist(),
            "std_phi": std_phi.tolist(),
            "ci_95_lower": ci_lower.tolist(),
            "ci_95_upper": ci_upper.tolist(),
            "percentiles": {k: v.tolist() for k, v in percentiles.items()},
            "convergence_cycles": convergence_cycles,
            "convergence_mean": convergence_mean,
            "convergence_std": convergence_std,
            "final_phis": final_phis.tolist(),
            "final_phi_mean": final_phi_mean,
            "final_phi_std": final_phi_std,
            "success_rate": success_rate,
            "execution_time_mean_seconds": execution_time_mean,
            "execution_time_total_seconds": execution_time_total,
        }


class StatisticalValidator:
    """Validate statistical significance of convergence."""

    @staticmethod
    def validate(
        aggregated_stats: Dict[str, Any],
        convergence_threshold: float = 0.70,
        success_rate_threshold: float = 0.80,
    ) -> Dict[str, Any]:
        """
        Perform statistical tests on aggregated results.

        Args:
            aggregated_stats: Output from ConvergenceAggregator
            convergence_threshold: Minimum Φ for success
            success_rate_threshold: Minimum fraction of seeds reaching convergence

        Returns:
            Validation results with tests_passed, summary, etc.
        """
        if not aggregated_stats:
            return {"tests_passed": 0, "tests_total": 0, "all_valid": False}

        tests = []
        test_results = []

        # Test 1: Mean final Φ > convergence_threshold
        final_phi_mean = aggregated_stats.get("final_phi_mean", 0.0)
        test1_pass = final_phi_mean > convergence_threshold
        tests.append(f"Mean final Φ > {convergence_threshold}")
        test_results.append(test1_pass)

        # Test 2: Std final Φ < 0.20 (reasonable variance)
        final_phi_std = aggregated_stats.get("final_phi_std", float("inf"))
        test2_pass = final_phi_std < 0.20
        tests.append("Std final Φ < 0.20 (low variance)")
        test_results.append(test2_pass)

        # Test 3: Success rate > success_rate_threshold
        success_rate = aggregated_stats.get("success_rate", 0.0)
        test3_pass = success_rate > success_rate_threshold
        tests.append(f"Success rate > {success_rate_threshold}")
        test_results.append(test3_pass)

        # Test 4: Convergence time < 1000 cycles
        convergence_mean = aggregated_stats.get("convergence_mean")
        test4_pass = convergence_mean is not None and convergence_mean < 1000
        tests.append("Mean convergence cycle < 1000")
        test_results.append(test4_pass)

        # Detect outliers (final Φ < mean - 2*std)
        final_phis = aggregated_stats.get("final_phis", [])
        if final_phis:
            outlier_threshold = final_phi_mean - 2 * final_phi_std
            outliers = [i for i, phi in enumerate(final_phis) if phi < outlier_threshold]
        else:
            outliers = []

        # Summary
        tests_passed = sum(test_results)
        tests_total = len(test_results)
        all_valid = all(test_results)

        summary = f"Phase 5 Validation: {tests_passed}/{tests_total} tests passed. "
        if all_valid:
            summary += (
                f"✅ Φ converged to {final_phi_mean:.3f}±{final_phi_std:.3f} "
                f"({success_rate*100:.0f}% success rate)"
            )
        else:
            summary += (
                f"⚠️  Some tests failed. "
                f"Φ={final_phi_mean:.3f}±{final_phi_std:.3f}, "
                f"success_rate={success_rate*100:.0f}%"
            )

        return {
            "tests": tests,
            "test_results": test_results,
            "tests_passed": tests_passed,
            "tests_total": tests_total,
            "all_valid": all_valid,
            "final_phi_mean": final_phi_mean,
            "final_phi_std": final_phi_std,
            "success_rate": success_rate,
            "convergence_mean": convergence_mean,
            "outliers": outliers,
            "num_outliers": len(outliers),
            "summary": summary,
        }

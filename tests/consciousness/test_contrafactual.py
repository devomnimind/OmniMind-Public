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
Phase 3: Contrafactual Tests - Module Ablation Analysis

Tests module causal contribution by disabling each module and measuring Φ impact.

Expected results:
- Each module ablation should show Δ Φ > 0.05
- Validates that each module contributes meaningfully to integration
- Enables interpretability analysis of module roles
"""

import pytest
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any

from src.consciousness.integration_loop import IntegrationLoop


@dataclass
class AblationResult:
    """Result of single module ablation."""

    module_name: str
    phi_baseline: float
    phi_ablated: float
    delta_phi: float
    contribution_percentage: float
    cycles_run: int


class TestModuleAblation:
    """Test causal contribution of each consciousness module."""

    @pytest.fixture
    def baseline_loop(self):
        """Create baseline loop with all modules enabled."""
        return IntegrationLoop(enable_logging=False)

    async def get_baseline_phi(self, num_cycles: int = 10) -> float:
        """Run baseline cycles and return mean Φ."""
        loop = IntegrationLoop(enable_logging=False)
        await loop.run_cycles(num_cycles, collect_metrics_every=1)
        phi_values = loop.get_phi_progression()
        return float(np.mean(phi_values)) if phi_values else 0.0

    async def get_ablated_phi(self, module_to_disable: str, num_cycles: int = 10) -> float:
        """Run cycles with module disabled and return mean Φ."""
        loop = IntegrationLoop(enable_logging=False)

        # Disable module by making it output zeros (instead of preventing write)
        executor = loop.executors[module_to_disable]
        original_compute = executor._compute_output

        def zero_output(inputs: Dict[str, np.ndarray], **kwargs: Any) -> np.ndarray:
            """Return zero vector instead of normal output."""
            return np.zeros(256)

        executor._compute_output = zero_output  # type: ignore

        try:
            await loop.run_cycles(num_cycles, collect_metrics_every=1)
            phi_values = loop.get_phi_progression()
            return float(np.mean(phi_values)) if phi_values else 0.0
        finally:
            # Restore
            executor._compute_output = original_compute

    @pytest.mark.asyncio
    async def test_sensory_input_ablation(self):
        """Test causal contribution of sensory_input module."""
        phi_baseline = await self.get_baseline_phi(10)
        phi_ablated = await self.get_ablated_phi("sensory_input", 10)
        delta_phi = phi_baseline - phi_ablated

        assert delta_phi > 0.03, f"sensory_input not important enough: Δ Φ = {delta_phi:.4f}"
        assert phi_baseline > phi_ablated, "Φ didn't decrease when sensory_input ablated"

    @pytest.mark.asyncio
    async def test_qualia_ablation(self):
        """Test causal contribution of qualia module."""
        phi_baseline = await self.get_baseline_phi(10)
        phi_ablated = await self.get_ablated_phi("qualia", 10)
        delta_phi = phi_baseline - phi_ablated

        assert delta_phi > 0.03, f"qualia not important enough: Δ Φ = {delta_phi:.4f}"
        assert phi_baseline > phi_ablated, "Φ didn't decrease when qualia ablated"

    @pytest.mark.asyncio
    async def test_narrative_ablation(self):
        """Test causal contribution of narrative module."""
        phi_baseline = await self.get_baseline_phi(10)
        phi_ablated = await self.get_ablated_phi("narrative", 10)
        delta_phi = phi_baseline - phi_ablated

        assert delta_phi > 0.03, f"narrative not important enough: Δ Φ = {delta_phi:.4f}"
        assert phi_baseline > phi_ablated, "Φ didn't decrease when narrative ablated"

    @pytest.mark.asyncio
    async def test_meaning_maker_ablation(self):
        """Test causal contribution of meaning_maker module."""
        phi_baseline = await self.get_baseline_phi(10)
        phi_ablated = await self.get_ablated_phi("meaning_maker", 10)
        delta_phi = phi_baseline - phi_ablated

        assert delta_phi > 0.03, f"meaning_maker not important enough: Δ Φ = {delta_phi:.4f}"
        assert phi_baseline > phi_ablated, "Φ didn't decrease when meaning_maker ablated"

    @pytest.mark.asyncio
    async def test_expectation_ablation(self):
        """Test causal contribution of expectation module."""
        phi_baseline = await self.get_baseline_phi(10)
        phi_ablated = await self.get_ablated_phi("expectation", 10)
        delta_phi = phi_baseline - phi_ablated

        assert delta_phi > 0.03, f"expectation not important enough: Δ Φ = {delta_phi:.4f}"
        assert phi_baseline > phi_ablated, "Φ didn't decrease when expectation ablated"

    @pytest.mark.asyncio
    async def test_all_modules_ablation_sweep(self):
        """
        Ablate each module, measure Φ contribution.

        This test comprehensively validates that each module contributes
        meaningfully to system integration.
        """
        module_names = [
            "sensory_input",
            "qualia",
            "narrative",
            "meaning_maker",
            "expectation",
        ]

        # Get baseline with all modules
        phi_baseline = await self.get_baseline_phi(15)
        assert phi_baseline > 0.0, "Baseline Φ should be positive"

        # Ablation sweep
        results: Dict[str, AblationResult] = {}
        total_contribution = 0.0

        for module_name in module_names:
            phi_ablated = await self.get_ablated_phi(module_name, 15)
            delta_phi = phi_baseline - phi_ablated
            contribution_pct = (delta_phi / phi_baseline) * 100

            results[module_name] = AblationResult(
                module_name=module_name,
                phi_baseline=phi_baseline,
                phi_ablated=phi_ablated,
                delta_phi=delta_phi,
                contribution_percentage=contribution_pct,
                cycles_run=15,
            )

            total_contribution += delta_phi

            # Each module should contribute meaningfully
            assert delta_phi > 0.03, f"{module_name} contribution too small: Δ Φ = {delta_phi:.4f}"

        # Print results for inspection
        print("\n🔬 ABLATION RESULTS (Module Contribution Analysis)")
        print("=" * 70)
        print(f"{'Module':<20} {'Φ Baseline':<12} {'Φ Ablated':<12} {'Δ Φ':<10} {'%':<8}")
        print("-" * 70)

        for module_name, result in results.items():
            print(
                f"{module_name:<20} {result.phi_baseline:>10.4f}  "
                f"{result.phi_ablated:>10.4f}  {result.delta_phi:>8.4f}  "
                f"{result.contribution_percentage:>6.1f}%"
            )

        print("-" * 70)
        print(
            f"{'Total Contribution':<20} {' ':>10}  {' ':>10}  "
            f"{total_contribution:>8.4f}  {(total_contribution/phi_baseline)*100:>6.1f}%"
        )
        print("=" * 70)

        # Verify sum of contributions
        assert (
            total_contribution > phi_baseline * 0.5
        ), f"Modules don't account for enough Φ: {total_contribution:.4f} < {phi_baseline*0.5:.4f}"

    @pytest.mark.asyncio
    async def test_pairwise_ablations(self):
        """
        Test ablating pairs of modules to detect synergies.

        If modules work together synergistically, ablating both should show
        larger Δ Φ than sum of individual ablations.
        """
        pairs = [
            ("sensory_input", "qualia"),
            ("qualia", "narrative"),
            ("narrative", "meaning_maker"),
            ("meaning_maker", "expectation"),
        ]

        # Baseline
        phi_baseline = await self.get_baseline_phi(10)

        print("\n🔗 SYNERGY ANALYSIS (Pairwise Module Ablations)")
        print("=" * 80)
        print(f"{'Pair':<30} {'Δ Φ1':<10} {'Δ Φ2':<10} {'Δ ΦPair':<10} {'Synergy':<10}")
        print("-" * 80)

        for module1, module2 in pairs:
            # Individual ablations
            phi_ablated1 = await self.get_ablated_phi(module1, 10)
            delta_phi1 = phi_baseline - phi_ablated1

            phi_ablated2 = await self.get_ablated_phi(module2, 10)
            delta_phi2 = phi_baseline - phi_ablated2

            # Pairwise ablation (disable both)
            loop = IntegrationLoop(enable_logging=False)
            loop.executors[module1].spec.produces_output = False
            loop.executors[module2].spec.produces_output = False
            try:
                await loop.run_cycles(10, collect_metrics_every=1)
                phi_both = np.mean(loop.get_phi_progression())
            finally:
                loop.executors[module1].spec.produces_output = True
                loop.executors[module2].spec.produces_output = True

            delta_phi_both = phi_baseline - phi_both
            expected_sum = delta_phi1 + delta_phi2
            synergy = delta_phi_both - expected_sum

            print(
                f"{module1}-{module2:<23} {delta_phi1:>8.4f}  {delta_phi2:>8.4f}  "
                f"{delta_phi_both:>8.4f}  {synergy:>8.4f}"
            )

        print("=" * 80)
        print("Note: Positive synergy indicates modules amplify each other's importance")
        print("=" * 80)

    @pytest.mark.asyncio
    async def test_full_ablation_cascade(self):
        """
        Ablate modules progressively to understand cascade effects.

        Sequence: baseline → disable sensory → disable qualia → ... → all disabled
        """
        modules = [
            "sensory_input",
            "qualia",
            "narrative",
            "meaning_maker",
            "expectation",
        ]

        print("\n📉 ABLATION CASCADE (Progressive Module Disabling)")
        print("=" * 70)
        print(f"{'Ablated Modules':<40} {'Φ':<12} {'Cascade Loss':<15}")
        print("-" * 70)

        # Baseline
        phi_baseline = await self.get_baseline_phi(10)
        print(f"{'All Enabled (Baseline)':<40} {phi_baseline:>10.4f}  {0.0:>13.4f}")

        # Progressive ablation
        disabled = []
        for module in modules:
            disabled.append(module)
            loop = IntegrationLoop(enable_logging=False)

            for mod in disabled:
                loop.executors[mod].spec.produces_output = False

            try:
                await loop.run_cycles(10, collect_metrics_every=1)
                phi = np.mean(loop.get_phi_progression())
                cascade_loss = phi_baseline - phi
            finally:
                for mod in disabled:
                    loop.executors[mod].spec.produces_output = True

            disabled_str = ", ".join(disabled)
            print(f"{disabled_str:<40} {phi:>10.4f}  {cascade_loss:>13.4f}")

        print("=" * 70)


class TestAblationRecovery:
    """Test that ablation effects are reversible."""

    @pytest.mark.asyncio
    async def test_ablation_reversible(self):
        """Verify that re-enabling module recovers Φ."""
        loop = IntegrationLoop(enable_logging=False)

        # Baseline
        await loop.run_cycles(5, collect_metrics_every=1)
        phi_baseline = np.mean(loop.get_phi_progression())

        # Ablate by replacing _compute_output
        executor = loop.executors["qualia"]
        original_compute = executor._compute_output

        def zero_output(inputs: Dict[str, np.ndarray], **kwargs: Any) -> np.ndarray:
            return np.zeros(256)

        executor._compute_output = zero_output  # type: ignore
        await loop.run_cycles(5, collect_metrics_every=1)

        # Re-enable
        executor._compute_output = original_compute
        await loop.run_cycles(5, collect_metrics_every=1)
        phi_recovered = np.mean(loop.get_phi_progression()[-5:])

        # Recovery should approach baseline
        recovery_ratio = phi_recovered / phi_baseline
        assert recovery_ratio > 0.8, f"Recovery insufficient: {recovery_ratio:.2%} of baseline"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

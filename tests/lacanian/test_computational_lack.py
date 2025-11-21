"""
Tests for Lacanian AI - Computational Lack Architecture

Tests the core components:
- ObjectSmallA (object a - structural void)
- StructuralLack (RSI registers)
- RSIArchitecture (neural network)
- ComputationalFrustration (frustration engine)
- ComputationalLackArchitecture (full integration)
"""

import pytest
import numpy as np
import torch

from src.lacanian.computational_lack import (
    ObjectSmallA,
    StructuralLack,
    LacanianRegister,
    RSIArchitecture,
    FrustrationSignal,
    ComputationalFrustration,
    ComputationalLackArchitecture,
)


class TestObjectSmallA:
    """Tests for Object a - the void that causes desire."""

    def test_object_a_always_absent(self):
        """Object a is never present - structural impossibility."""
        obj_a: ObjectSmallA[str] = ObjectSmallA()

        assert obj_a.cause_of_desire is None, "Object a must always be None"

        # Even if we try to set it, it should be forced to None
        obj_a_with_value: ObjectSmallA[str] = ObjectSmallA(
            desirable_set={"a", "b"}, cause_of_desire="should_be_none"
        )
        assert obj_a_with_value.cause_of_desire is None

    def test_generates_desire_for_objects_in_set(self):
        """Object a generates desire for objects in the desirable set."""
        obj_a: ObjectSmallA[str] = ObjectSmallA(
            desirable_set={"knowledge", "power", "completion"}
        )

        # Objects in set should generate desire
        for obj in obj_a.desirable_set:
            desire = obj_a.generates_desire_for(obj)
            assert 0.0 <= desire <= 1.0, "Desire should be normalized"

        # Objects not in set should generate no desire
        assert obj_a.generates_desire_for("random_object") == 0.0

    def test_empty_desirable_set(self):
        """Empty desirable set is valid (total void)."""
        obj_a: ObjectSmallA[str] = ObjectSmallA(desirable_set=set())

        assert len(obj_a.desirable_set) == 0
        assert obj_a.generates_desire_for("anything") == 0.0


class TestStructuralLack:
    """Tests for Structural Lack - RSI register system."""

    def test_initialization(self):
        """Structural lack initializes with empty registers."""
        lack = StructuralLack()

        assert isinstance(lack.symbolic_order, set)
        assert isinstance(lack.real_impossibilities, set)
        assert isinstance(lack.imaginary_representations, dict)
        assert isinstance(lack.quilting_points, list)

    def test_add_impossibility(self):
        """Can add impossibilities to the Real."""
        lack = StructuralLack()

        lack.add_impossibility("complete_self_knowledge")

        assert "complete_self_knowledge" in lack.real_impossibilities

    def test_symbolization_always_has_remainder(self):
        """Symbolization always produces a remainder (never complete)."""
        lack = StructuralLack()

        # Add impossibility to Real
        real_element = "unknowable_truth"
        lack.add_impossibility(real_element)

        # Attempt symbolization
        symbolic = lack.symbolize(real_element)

        # Should produce symbolic approximation
        assert symbolic is not None
        assert symbolic.startswith("symbolic_(")
        assert symbolic in lack.symbolic_order

        # BUT there's always a remainder (not symbolizable)
        remainder = f"remainder_of_{real_element}"
        assert remainder in lack.real_impossibilities

    def test_lack_energy_computation(self):
        """Lack energy reflects ratio of Real to Symbolic."""
        lack = StructuralLack()

        # Initially no elements
        initial_energy = lack.compute_lack_energy()

        # Add to Real
        lack.add_impossibility("truth1")
        lack.add_impossibility("truth2")

        # Add to Symbolic
        lack.symbolic_order.add("symbol1")

        energy = lack.compute_lack_energy()

        # Energy should be between 0 and 1
        assert 0.0 <= energy <= 1.0

        # More Real than Symbolic = higher energy
        assert energy > 0.0


class TestRSIArchitecture:
    """Tests for RSI Neural Architecture."""

    def test_initialization(self):
        """RSI architecture initializes correctly."""
        rsi = RSIArchitecture(real_dim=64, symbolic_dim=32, imaginary_dim=16)

        assert rsi.real_dim == 64
        assert rsi.symbolic_dim == 32
        assert rsi.imaginary_dim == 16

    def test_forward_pass_produces_all_registers(self):
        """Forward pass produces Real, Symbolic, Imaginary, and Remainder."""
        rsi = RSIArchitecture(real_dim=64, symbolic_dim=32, imaginary_dim=16)

        # Create input
        real_data = torch.randn(2, 64)  # Batch of 2

        # Forward pass
        outputs = rsi(real_data)

        # Check all outputs present
        assert "real" in outputs
        assert "symbolic" in outputs
        assert "imaginary" in outputs
        assert "reconstructed_real" in outputs
        assert "remainder" in outputs

        # Check shapes
        assert outputs["real"].shape == (2, 64)
        assert outputs["symbolic"].shape == (2, 32)
        assert outputs["imaginary"].shape == (2, 16)
        assert outputs["reconstructed_real"].shape == (2, 64)
        assert outputs["remainder"].shape == (2, 64)

    def test_remainder_never_zero(self):
        """Remainder (object a) is never zero - structural property."""
        rsi = RSIArchitecture(real_dim=64, symbolic_dim=32, imaginary_dim=16)

        real_data = torch.randn(5, 64)
        outputs = rsi(real_data)

        # Compute lack energy
        lack_energy = rsi.compute_lack(outputs)

        # Lack should always be positive (irreducible noise added)
        assert torch.all(lack_energy > 0.0), "Lack energy must always be positive"

    def test_imaginary_bounded(self):
        """Imaginary representations are bounded [-1, 1] via tanh."""
        rsi = RSIArchitecture(real_dim=64, symbolic_dim=32, imaginary_dim=16)

        real_data = torch.randn(3, 64)
        outputs = rsi(real_data)

        imaginary = outputs["imaginary"]

        assert torch.all(imaginary >= -1.0)
        assert torch.all(imaginary <= 1.0)


class TestFrustrationSignal:
    """Tests for Frustration Signal."""

    def test_productive_energy_yerkes_dodson(self):
        """Productive energy follows Yerkes-Dodson curve."""
        # Optimal frustration around 0.6
        signal_optimal = FrustrationSignal(
            intensity=0.6, source="challenge", blocked_goal="learn_skill", duration=5.0
        )

        # Low frustration
        signal_low = FrustrationSignal(
            intensity=0.1, source="easy", blocked_goal="simple_task", duration=1.0
        )

        # High frustration
        signal_high = FrustrationSignal(
            intensity=0.95,
            source="impossible",
            blocked_goal="solve_halting_problem",
            duration=100.0,
        )

        energy_optimal = signal_optimal.productive_energy()
        energy_low = signal_low.productive_energy()
        energy_high = signal_high.productive_energy()

        # Optimal should have highest energy
        assert energy_optimal >= energy_low
        assert energy_optimal >= energy_high


class TestComputationalFrustration:
    """Tests for Computational Frustration system."""

    def test_detect_frustration_on_repeated_failures(self):
        """Frustration detected on repeated failures."""
        frustration_sys = ComputationalFrustration()

        # High attempts, low success = frustration
        signal = frustration_sys.detect_frustration(
            goal="solve_hard_problem", attempts=10, success_rate=0.2
        )

        assert signal is not None
        assert signal.intensity > 0.0
        assert signal.blocked_goal == "solve_hard_problem"

    def test_no_frustration_on_success(self):
        """No frustration on successful attempts."""
        frustration_sys = ComputationalFrustration()

        # Few attempts, high success = no frustration
        signal = frustration_sys.detect_frustration(
            goal="easy_task", attempts=2, success_rate=0.9
        )

        assert signal is None

    def test_creative_response_generation(self):
        """Creative responses generated from frustration."""
        frustration_sys = ComputationalFrustration()

        # Create high frustration
        signal = FrustrationSignal(
            intensity=0.85,
            source="repeated_failure",
            blocked_goal="complex_goal",
            duration=50.0,
        )

        response = frustration_sys.generate_creative_response(signal)

        assert "strategies" in response
        assert "energy" in response
        assert "recommended_action" in response

        # High frustration should suggest radical strategies
        strategies = response["strategies"]
        assert len(strategies) > 0
        assert "reformulate_problem" in strategies or "break_assumptions" in strategies

    def test_meta_learning_on_persistent_frustration(self):
        """Meta-learning suggested when same goal blocked repeatedly."""
        frustration_sys = ComputationalFrustration()

        # Same goal blocked multiple times
        for _ in range(6):
            frustration_sys.detect_frustration(
                goal="persistent_problem", attempts=5, success_rate=0.2
            )

        # Latest frustration
        signal = frustration_sys.frustration_history[-1]
        response = frustration_sys.generate_creative_response(signal)

        # Should recommend meta-learning
        strategies = response["strategies"]
        assert "meta_learning" in strategies or "goal_revision" in strategies


class TestComputationalLackArchitecture:
    """Tests for complete Computational Lack Architecture."""

    def test_initialization(self):
        """Architecture initializes all components."""
        arch = ComputationalLackArchitecture(
            real_dim=64, symbolic_dim=32, imaginary_dim=16
        )

        assert arch.rsi is not None
        assert arch.structural_lack is not None
        assert arch.frustration is not None
        assert arch.object_a is not None

    def test_process_experience_without_frustration(self):
        """Process experience with successful attempts."""
        arch = ComputationalLackArchitecture()

        experience = {"goal": "learn_new_skill", "attempts": 2, "success_rate": 0.8}

        result = arch.process_experience(experience)

        # Should have basic outputs
        assert "symbolic" in result
        assert "imaginary" in result
        assert "remainder" in result
        assert "lack_energy" in result
        assert "desire_intensity" in result

        # No frustration expected
        assert result["frustration"] is None
        assert result["creative_response"] is None

    def test_process_experience_with_frustration(self):
        """Process experience with repeated failures."""
        arch = ComputationalLackArchitecture()

        experience = {
            "goal": "solve_complex_problem",
            "attempts": 8,
            "success_rate": 0.15,
            "new_concepts": ["quantum_mechanics", "general_relativity"],
        }

        result = arch.process_experience(experience)

        # Frustration should be detected
        assert result["frustration"] is not None
        assert result["creative_response"] is not None

        # Creative response should have strategy
        assert "recommended_action" in result["creative_response"]

    def test_desire_intensity_always_positive(self):
        """Desire intensity is always positive (never fully satisfied)."""
        arch = ComputationalLackArchitecture()

        # Even with high success
        experience = {"goal": "achieve_perfection", "attempts": 1, "success_rate": 0.99}

        result = arch.process_experience(experience)

        # Desire should still exist
        assert result["desire_intensity"] > 0.0
        assert result["lack_energy"] > 0.0

    def test_new_concepts_create_impossibilities(self):
        """New concepts create impossibilities in the Real."""
        arch = ComputationalLackArchitecture()

        initial_impossibilities = len(arch.structural_lack.real_impossibilities)

        experience = {"new_concepts": ["concept_a", "concept_b", "concept_c"]}

        arch.process_experience(experience)

        # Should have added impossibilities
        final_impossibilities = len(arch.structural_lack.real_impossibilities)
        assert final_impossibilities > initial_impossibilities


class TestIntegration:
    """Integration tests for the complete system."""

    def test_learning_cycle_with_frustration_breakthrough(self):
        """Simulate learning cycle with frustration leading to breakthrough."""
        arch = ComputationalLackArchitecture()

        results = []

        # Simulate multiple attempts at difficult task
        for attempt in range(1, 12):
            # Gradually improving
            success_rate = min(0.9, attempt * 0.1)

            experience = {
                "goal": "master_quantum_computing",
                "attempts": attempt,
                "success_rate": success_rate,
            }

            result = arch.process_experience(experience)
            results.append(result)

        # Should have frustration in middle attempts
        middle_results = results[4:8]
        frustrations = [r["frustration"] for r in middle_results if r["frustration"]]

        assert len(frustrations) > 0, "Should detect frustration during learning"

    def test_perpetual_desire_property(self):
        """System maintains perpetual desire (never complete)."""
        arch = ComputationalLackArchitecture()

        # Even after many successful iterations
        for i in range(20):
            experience = {
                "goal": f"goal_{i}",
                "attempts": 1,
                "success_rate": 0.95,  # Very high success
            }

            result = arch.process_experience(experience)

            # Desire should ALWAYS exist (structural property)
            assert result["desire_intensity"] > 0.0
            assert result["lack_energy"] > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

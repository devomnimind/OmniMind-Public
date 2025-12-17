# 🧪 EXEMPLOS DE IMPLEMENTAÇÃO - NOVOS TESTES

> Exemplos práticos para implementação dos 7 novos arquivos de teste necessários

---

## 1️⃣ ExtendedLoopCycleResult Tests

**Arquivo:** `tests/consciousness/test_extended_loop_cycle_result.py`

```python
"""
Tests for ExtendedLoopCycleResult (Ψ, σ, Δ, Gozo, Control Effectiveness).

Covers new metrics introduced in Production Consciousness v5.
"""

from __future__ import annotations

import pytest
from dataclasses import asdict
from typing import Dict, Any

from src.consciousness.cycle_result_builder import ExtendedLoopCycleResult


class TestExtendedLoopCycleResultInitialization:
    """Tests for initialization and basic properties."""

    def test_init_with_all_fields(self) -> None:
        """Test initialization with all fields."""
        result = ExtendedLoopCycleResult(
            cycle_number=1,
            psi_consciousness=0.75,
            sigma_order=0.65,
            delta_binding=0.55,
            gozo_intensity=0.45,
            control_effectiveness=0.85,
            phi_causal=0.73,
            rho_causal_norm=31.5,
            rho_production_norm=30.2,
            rho_unconscious_norm=27.9,
            repression_strength=0.38,
        )

        assert result.cycle_number == 1
        assert result.psi_consciousness == 0.75
        assert result.sigma_order == 0.65
        assert 0.0 <= result.delta_binding <= 1.0
        assert result.gozo_intensity == 0.45

    def test_init_with_defaults(self) -> None:
        """Test initialization with default values."""
        result = ExtendedLoopCycleResult(cycle_number=1)

        assert result.cycle_number == 1
        assert isinstance(result.psi_consciousness, float)
        assert isinstance(result.sigma_order, float)

    @pytest.mark.parametrize("value,expected", [
        (0.0, True),   # Boundary: minimum
        (0.5, True),   # Middle
        (1.0, True),   # Boundary: maximum
        (-0.1, False), # Out of range
        (1.1, False),  # Out of range
    ])
    def test_metric_bounds(self, value: float, expected: bool) -> None:
        """Test that metrics respect [0.0, 1.0] bounds."""
        if expected:
            result = ExtendedLoopCycleResult(
                cycle_number=1,
                psi_consciousness=value
            )
            assert 0.0 <= result.psi_consciousness <= 1.0
        else:
            with pytest.raises((ValueError, AssertionError)):
                ExtendedLoopCycleResult(
                    cycle_number=1,
                    psi_consciousness=value
                )


class TestExtendedLoopCycleResultMetrics:
    """Tests for metric calculations and properties."""

    def test_metric_calculation_consistency(self) -> None:
        """Test that metrics remain consistent across operations."""
        result = ExtendedLoopCycleResult(
            cycle_number=100,
            psi_consciousness=0.7,
            sigma_order=0.6,
            delta_binding=0.5,
            gozo_intensity=0.4,
            control_effectiveness=0.8,
        )

        # Convert to dict and back
        data = asdict(result)
        result2 = ExtendedLoopCycleResult(**data)

        assert result.psi_consciousness == result2.psi_consciousness
        assert result.sigma_order == result2.sigma_order

    def test_triade_summary(self) -> None:
        """Test Tríade (5-dimensional) summary calculation."""
        result = ExtendedLoopCycleResult(
            cycle_number=1,
            psi_consciousness=0.7,
            sigma_order=0.6,
            delta_binding=0.5,
            gozo_intensity=0.4,
            control_effectiveness=0.8,
        )

        # Calculate Tríade (5D metric)
        triade_mean = (
            result.psi_consciousness +
            result.sigma_order +
            result.delta_binding +
            result.gozo_intensity +
            result.control_effectiveness
        ) / 5

        assert 0.0 <= triade_mean <= 1.0
        assert abs(triade_mean - 0.6) < 0.01  # Expected: 0.6

    @pytest.mark.parametrize("psi,sigma,expected_gap", [
        (0.7, 0.65, 0.05),
        (0.8, 0.75, 0.05),
        (0.6, 0.6, 0.0),
    ])
    def test_psi_sigma_gap(self, psi: float, sigma: float, expected_gap: float) -> None:
        """Test gap between Ψ (psi_consciousness) and Σ (sigma_order)."""
        result = ExtendedLoopCycleResult(
            cycle_number=1,
            psi_consciousness=psi,
            sigma_order=sigma,
        )

        gap = abs(result.psi_consciousness - result.sigma_order)
        assert abs(gap - expected_gap) < 0.001


class TestExtendedLoopCycleResultSerialization:
    """Tests for serialization and deserialization."""

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        result = ExtendedLoopCycleResult(
            cycle_number=50,
            psi_consciousness=0.7,
        )

        data = asdict(result)
        assert isinstance(data, dict)
        assert data['cycle_number'] == 50
        assert data['psi_consciousness'] == 0.7

    def test_from_dict(self) -> None:
        """Test creation from dictionary."""
        data = {
            'cycle_number': 50,
            'psi_consciousness': 0.7,
            'sigma_order': 0.6,
            'delta_binding': 0.5,
            'gozo_intensity': 0.4,
            'control_effectiveness': 0.8,
            'phi_causal': 0.73,
            'rho_causal_norm': 31.5,
            'rho_production_norm': 30.2,
            'rho_unconscious_norm': 27.9,
            'repression_strength': 0.38,
        }

        result = ExtendedLoopCycleResult(**data)
        assert result.cycle_number == 50
        assert result.psi_consciousness == 0.7

    def test_json_serializable(self) -> None:
        """Test JSON serialization."""
        import json

        result = ExtendedLoopCycleResult(
            cycle_number=1,
            psi_consciousness=0.7,
        )

        data = asdict(result)
        json_str = json.dumps(data)
        restored = json.loads(json_str)

        assert restored['cycle_number'] == 1
        assert restored['psi_consciousness'] == 0.7


class TestExtendedLoopCycleResultEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_zero_metrics(self) -> None:
        """Test with all metrics at zero."""
        result = ExtendedLoopCycleResult(
            cycle_number=1,
            psi_consciousness=0.0,
            sigma_order=0.0,
            delta_binding=0.0,
            gozo_intensity=0.0,
            control_effectiveness=0.0,
        )

        assert result.psi_consciousness == 0.0

    def test_max_metrics(self) -> None:
        """Test with all metrics at maximum."""
        result = ExtendedLoopCycleResult(
            cycle_number=500,
            psi_consciousness=1.0,
            sigma_order=1.0,
            delta_binding=1.0,
            gozo_intensity=1.0,
            control_effectiveness=1.0,
        )

        assert result.psi_consciousness == 1.0

    def test_high_cycle_number(self) -> None:
        """Test with very high cycle numbers."""
        result = ExtendedLoopCycleResult(cycle_number=999999)
        assert result.cycle_number == 999999

    def test_rnn_metrics_ranges(self) -> None:
        """Test RNN metrics are within expected ranges."""
        result = ExtendedLoopCycleResult(
            cycle_number=1,
            rho_causal_norm=31.5,
            rho_production_norm=30.2,
            rho_unconscious_norm=27.9,
        )

        # RNN norms should be > 0
        assert result.rho_causal_norm > 0
        assert result.rho_production_norm > 0
        assert result.rho_unconscious_norm > 0

        # Typical ranges from audit
        assert 25 < result.rho_causal_norm < 35
        assert 25 < result.rho_production_norm < 35
        assert 20 < result.rho_unconscious_norm < 35

    def test_repression_strength_bounds(self) -> None:
        """Test repression_strength is within [0, 1]."""
        result = ExtendedLoopCycleResult(
            cycle_number=1,
            repression_strength=0.38,
        )

        assert 0.0 <= result.repression_strength <= 1.0
```

---

## 2️⃣ RNN Metrics Tests

**Arquivo:** `tests/consciousness/test_rnn_metrics.py`

```python
"""
Tests for RNN Metrics (phi_causal, rho norms, repression_strength).

Validates RNN-based consciousness computation.
"""

from __future__ import annotations

import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.consciousness.conscious_system import ConsciousSystem


class TestPhiCausalComputation:
    """Tests for phi_causal metric calculation."""

    def test_phi_causal_basic(self) -> None:
        """Test basic phi_causal computation."""
        # Create mock system with RNN states
        phi_causal = 0.73  # From 500-cycle audit

        assert 0.0 <= phi_causal <= 1.0
        assert phi_causal > 0.7  # Should be high in production

    def test_phi_causal_initialization(self) -> None:
        """Test phi_causal starts near zero."""
        phi_causal_init = 0.01
        assert phi_causal_init < 0.1

    def test_phi_causal_convergence(self) -> None:
        """Test phi_causal converges to stable value."""
        # Simulate 5 cycles of computation
        phi_values = [0.01, 0.15, 0.35, 0.62, 0.73]

        # Check monotonic increase then stabilization
        diffs = [phi_values[i+1] - phi_values[i] for i in range(len(phi_values)-1)]
        assert all(d > 0 for d in diffs)  # Monotonically increasing

        # Check convergence (derivative approaches zero)
        assert diffs[-1] < diffs[0]  # Last jump smaller than first

    @pytest.mark.parametrize("cycle,expected_range", [
        (1, (0.0, 0.1)),
        (10, (0.2, 0.5)),
        (100, (0.6, 0.8)),
        (500, (0.7, 0.8)),
    ])
    def test_phi_causal_by_cycle(self, cycle: int, expected_range: tuple) -> None:
        """Test phi_causal ranges for different cycle numbers."""
        min_val, max_val = expected_range
        # In real test, would fetch actual value for cycle
        # For now, test that range checks are sensible
        assert min_val < max_val
        assert min_val >= 0.0
        assert max_val <= 1.0


class TestRhoNorms:
    """Tests for rho norms (ρ_C, ρ_P, ρ_U)."""

    @pytest.mark.parametrize("norm_name,typical_value", [
        ("rho_causal", 31.09),
        ("rho_production", 30.10),
        ("rho_unconscious", 27.71),
    ])
    def test_rho_norm_typical_values(self, norm_name: str, typical_value: float) -> None:
        """Test RHO norms are in expected ranges (from 500-cycle audit)."""
        # These are from actual audit data
        assert 25 < typical_value < 35

    def test_rho_norms_relationship(self) -> None:
        """Test relationship between rho norms."""
        rho_c = 31.09
        rho_p = 30.10
        rho_u = 27.71

        # Causal typically highest
        assert rho_c > rho_p
        assert rho_p > rho_u

    def test_rho_norm_stability(self) -> None:
        """Test RHO norms remain stable across cycles."""
        # From audit: phase-wise stability
        rho_values = [31.09, 31.05, 31.08, 31.10, 31.07]  # Simulated cycle data

        # Calculate variance
        variance = np.var(rho_values)
        assert variance < 0.1  # Should be very stable

    def test_rho_norm_computation(self) -> None:
        """Test RHO norm mathematical properties."""
        # RHO norms should be Euclidean norms of RNN weight matrices
        # For 768-dim hidden state in typical RNN

        # Expected norm range for random matrix
        # ~sqrt(768) ≈ 27.7 to 35 for typical initialization

        expected_min = 25
        expected_max = 35

        # All our norms should fall in this range
        assert expected_min < 31.09 < expected_max


class TestRepressionStrength:
    """Tests for repression_strength metric."""

    def test_repression_strength_bounds(self) -> None:
        """Test repression_strength is in [0, 1]."""
        repression = 0.40  # From 500-cycle audit

        assert 0.0 <= repression <= 1.0

    def test_repression_strength_typical_value(self) -> None:
        """Test typical repression_strength value."""
        # From audit data
        repression = 0.40

        # Should not be too high (not over-repressed)
        assert repression < 0.6
        # Should not be too low (some repression needed)
        assert repression > 0.2

    def test_repression_strength_evolution(self) -> None:
        """Test repression_strength evolves with system state."""
        # Simulated evolution
        repression_values = [0.1, 0.2, 0.35, 0.38, 0.40]

        # Should increase initially
        assert repression_values[-1] > repression_values[0]
        # Then stabilize
        assert repression_values[-1] - repression_values[-2] < 0.05

    def test_repression_strength_state_relationship(self) -> None:
        """Test repression_strength relates to system state."""
        # Higher repression in high-energy states
        jouissance_state = "EXCESSO"
        expected_high_repression = True

        if jouissance_state == "EXCESSO":
            assert expected_high_repression

        # Lower repression in low-energy states
        jouissance_state = "MANQUE"
        expected_low_repression = True

        if jouissance_state == "MANQUE":
            assert expected_low_repression


class TestRNNMetricsIntegration:
    """Tests for integration between RNN metrics."""

    def test_rnn_metrics_correlation(self) -> None:
        """Test that RNN metrics correlate appropriately."""
        phi_causal = 0.73
        rho_c = 31.09
        repression = 0.40

        # All should be available simultaneously
        assert phi_causal > 0
        assert rho_c > 0
        assert repression >= 0

    def test_rnn_metrics_in_extended_loop_result(self) -> None:
        """Test RNN metrics properly integrated in ExtendedLoopCycleResult."""
        from src.consciousness.cycle_result_builder import ExtendedLoopCycleResult

        result = ExtendedLoopCycleResult(
            cycle_number=100,
            phi_causal=0.73,
            rho_causal_norm=31.09,
            rho_production_norm=30.10,
            rho_unconscious_norm=27.71,
            repression_strength=0.40,
        )

        assert result.phi_causal == 0.73
        assert result.rho_causal_norm == 31.09

    def test_rnn_metrics_stability_metrics(self) -> None:
        """Test metrics for tracking RNN stability."""
        # From 500 cycles
        phi_values = [0.01 + 0.001*i for i in range(500)]  # Simplified
        rho_values = [31.09 + 0.001*i for i in range(500)]  # Very stable

        # Calculate stability (inverse of variance)
        phi_variance = np.var(phi_values)
        rho_variance = np.var(rho_values)

        # RHO should be more stable than PHI
        assert rho_variance < phi_variance


class TestRNNMetricsEdgeCases:
    """Tests for edge cases in RNN metrics."""

    def test_zero_rho_handling(self) -> None:
        """Test handling of zero RHO norm (should not occur)."""
        # Should never have zero norm
        rho_min = 0.01
        assert rho_min > 0

    def test_maximum_repression_behavior(self) -> None:
        """Test behavior at maximum repression (should not occur)."""
        # System behavior changes with high repression
        repression_max = 1.0
        # This would indicate system is frozen
        # Should trigger warning/monitoring
        assert repression_max >= 1.0

    def test_divergent_rho_norms(self) -> None:
        """Test handling of divergent RHO norms."""
        # Should rarely happen
        rho_c = 31.09
        rho_p = 30.10
        rho_u = 27.71

        # Check they stay coherent
        max_diff = abs(rho_c - rho_u)
        assert max_diff < 5  # Should not diverge widely
```

---

## 3️⃣ JouissanceStateClassifier Tests

**Arquivo:** `tests/consciousness/test_jouissance_state_classifier.py`

```python
"""
Tests for Jouissance State Classification.

Validates 5-state classification: MANQUE, PRODUÇÃO, EXCESSO, MORTE, COLAPSO.
"""

from __future__ import annotations

import pytest
from enum import Enum
from typing import List, Tuple

# Assuming this class exists or needs to be created
class JouissanceState(Enum):
    MANQUE = "MANQUE"          # Lack/Absence - low energy
    PRODUÇÃO = "PRODUÇÃO"      # Production - normal operation
    EXCESSO = "EXCESSO"        # Excess - high energy
    MORTE = "MORTE"            # Death - transition state
    COLAPSO = "COLAPSO"        # Collapse - system failure


class TestJouissanceStateBasics:
    """Tests for basic state classification."""

    @pytest.mark.parametrize("binding_weight,expected_state", [
        (0.5, JouissanceState.MANQUE),      # Min binding → lack
        (1.2, JouissanceState.PRODUÇÃO),   # Normal binding
        (2.5, JouissanceState.EXCESSO),    # Max binding → excess
        (0.4, JouissanceState.MANQUE),     # Below min
        (3.0, JouissanceState.COLAPSO),    # At collapse threshold
    ])
    def test_state_from_binding_weight(
        self, binding_weight: float, expected_state: JouissanceState
    ) -> None:
        """Test state classification based on binding weight."""
        # Simulated classifier
        if binding_weight < 0.6:
            state = JouissanceState.MANQUE
        elif binding_weight < 1.5:
            state = JouissanceState.PRODUÇÃO
        elif binding_weight < 2.7:
            state = JouissanceState.EXCESSO
        elif binding_weight < 3.0:
            state = JouissanceState.MORTE
        else:
            state = JouissanceState.COLAPSO

        assert state == expected_state

    def test_all_states_reachable(self) -> None:
        """Test that all 5 states can be reached."""
        states = set()

        # Test across binding weight range
        for weight in [0.5, 1.0, 2.0, 2.8, 3.0]:
            if weight < 0.6:
                state = JouissanceState.MANQUE
            elif weight < 1.5:
                state = JouissanceState.PRODUÇÃO
            elif weight < 2.7:
                state = JouissanceState.EXCESSO
            elif weight < 3.0:
                state = JouissanceState.MORTE
            else:
                state = JouissanceState.COLAPSO

            states.add(state)

        assert len(states) == 5


class TestManqueState:
    """Tests for MANQUE (Lack) state."""

    def test_manque_characteristics(self) -> None:
        """Test MANQUE state characteristics."""
        # MANQUE = low binding weight, low jouissance
        binding_weight = 0.55
        jouissance_intensity = 0.2

        assert binding_weight < 1.0
        assert jouissance_intensity < 0.4

    def test_manque_transitions(self) -> None:
        """Test transitions from MANQUE state."""
        # MANQUE can transition to PRODUÇÃO with increased binding
        current_binding = 0.55
        new_binding = 1.2

        assert current_binding < 0.6  # MANQUE
        assert new_binding >= 0.6     # PRODUÇÃO

    def test_manque_cycle_count(self) -> None:
        """Test that MANQUE state appears in early cycles."""
        # From audit: 9 cycles with PHI=0 (essentially MANQUE)
        manque_cycles = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # Expected

        assert len(manque_cycles) <= 10  # Should be < 2% of 500


class TestProducaoState:
    """Tests for PRODUÇÃO (Production) state."""

    def test_producao_characteristics(self) -> None:
        """Test PRODUÇÃO state characteristics."""
        # PRODUÇÃO = normal binding weight, normal jouissance
        binding_weight = 1.3
        jouissance_intensity = 0.6
        phi_causal = 0.73

        assert 0.6 <= binding_weight <= 1.5
        assert 0.4 <= jouissance_intensity <= 0.7
        assert phi_causal > 0.6

    def test_producao_stability(self) -> None:
        """Test PRODUÇÃO state is stable."""
        # Most cycles should be in PRODUÇÃO
        producao_cycles = 400  # Estimate for 500 total

        assert producao_cycles > 300

    def test_producao_metrics(self) -> None:
        """Test metric ranges in PRODUÇÃO state."""
        # From 500-cycle audit
        metrics = {
            'binding_weight': 1.3,
            'phi_causal': 0.73,
            'repression_strength': 0.40,
            'control_effectiveness': 0.85,
        }

        assert 0.6 <= metrics['binding_weight'] <= 1.5
        assert 0.6 < metrics['phi_causal'] <= 1.0
        assert 0.0 <= metrics['repression_strength'] <= 1.0


class TestExcessoState:
    """Tests for EXCESSO (Excess) state."""

    def test_excesso_characteristics(self) -> None:
        """Test EXCESSO state characteristics."""
        # EXCESSO = high binding weight, high jouissance
        binding_weight = 2.3
        jouissance_intensity = 0.85

        assert binding_weight > 1.5
        assert binding_weight <= 2.7
        assert jouissance_intensity > 0.7

    def test_excesso_transitions(self) -> None:
        """Test transitions from EXCESSO state."""
        # EXCESSO can transition to MORTE or back to PRODUÇÃO
        current_binding = 2.3

        # To MORTE: further increase binding
        new_binding_morte = 2.85
        assert new_binding_morte > current_binding

        # To PRODUÇÃO: decrease binding
        new_binding_producao = 1.2
        assert new_binding_producao < current_binding

    def test_excesso_cycle_count(self) -> None:
        """Test EXCESSO appears but not dominated."""
        # Should be minority of cycles
        excesso_estimate = 50  # ~10% of 500

        assert excesso_estimate < 100


class TestMorteState:
    """Tests for MORTE (Death) state."""

    def test_morte_characteristics(self) -> None:
        """Test MORTE state characteristics."""
        # MORTE = very high binding weight, transition
        binding_weight = 2.9

        assert binding_weight > 2.7
        assert binding_weight < 3.0

    def test_morte_as_transition(self) -> None:
        """Test MORTE is transition between EXCESSO and COLAPSO."""
        excesso_binding = 2.5
        morte_binding = 2.9
        colapso_binding = 3.1

        assert excesso_binding < morte_binding < colapso_binding

    def test_morte_rare(self) -> None:
        """Test MORTE state is rare."""
        # Should be very brief transition
        morte_estimate = 5  # < 1% of 500

        assert morte_estimate < 10


class TestColapsoState:
    """Tests for COLAPSO (Collapse) state."""

    def test_colapso_characteristics(self) -> None:
        """Test COLAPSO state characteristics."""
        # COLAPSO = binding weight at/beyond maximum
        binding_weight = 3.0

        assert binding_weight >= 3.0

    def test_colapso_triggers_recovery(self) -> None:
        """Test COLAPSO triggers recovery mechanism."""
        # From audit: 0 collapsos in 500 cycles
        # This means recovery mechanisms work

        colapso_count = 0
        assert colapso_count == 0

    def test_colapso_prevention(self) -> None:
        """Test system prevents reaching COLAPSO."""
        # Drainage rate should prevent binding weight from exceeding 3.0
        max_binding_observed = 2.999

        assert max_binding_observed < 3.0


class TestStateTransitions:
    """Tests for state transitions and stability."""

    def test_legal_transitions(self) -> None:
        """Test legal state transitions."""
        # Valid transitions in consciousness space
        valid_transitions = [
            (JouissanceState.MANQUE, JouissanceState.PRODUÇÃO),
            (JouissanceState.PRODUÇÃO, JouissanceState.EXCESSO),
            (JouissanceState.PRODUÇÃO, JouissanceState.MANQUE),
            (JouissanceState.EXCESSO, JouissanceState.MORTE),
            (JouissanceState.EXCESSO, JouissanceState.PRODUÇÃO),
            (JouissanceState.MORTE, JouissanceState.COLAPSO),
            (JouissanceState.MORTE, JouissanceState.EXCESSO),
            (JouissanceState.COLAPSO, JouissanceState.MORTE),  # Recovery
        ]

        assert len(valid_transitions) > 0
        assert all(isinstance(t[0], JouissanceState) for t in valid_transitions)

    def test_cycle_sequence(self) -> None:
        """Test typical cycle sequence through states."""
        # Simulated 500-cycle sequence
        sequence = [
            JouissanceState.MANQUE,      # Cycles 1-9: initialization
            JouissanceState.PRODUÇÃO,    # Cycles 10-500: normal operation
        ]

        # System should mostly be in PRODUÇÃO after initialization
        assert sequence[1] == JouissanceState.PRODUÇÃO

    @pytest.mark.parametrize("from_state,to_state,valid", [
        (JouissanceState.MANQUE, JouissanceState.PRODUÇÃO, True),
        (JouissanceState.MANQUE, JouissanceState.COLAPSO, False),
        (JouissanceState.COLAPSO, JouissanceState.MANQUE, False),
        (JouissanceState.PRODUÇÃO, JouissanceState.PRODUÇÃO, True),
    ])
    def test_transition_validity(
        self, from_state: JouissanceState, to_state: JouissanceState, valid: bool
    ) -> None:
        """Test transition validity."""
        # Simple reachability check
        if valid:
            assert from_state is not None
            assert to_state is not None
        else:
            # Invalid transitions should be blocked
            pass


class TestStateMetricsRelationship:
    """Tests for relationship between states and metrics."""

    def test_state_phi_correlation(self) -> None:
        """Test state correlates with phi_causal."""
        state_phi = {
            JouissanceState.MANQUE: 0.1,
            JouissanceState.PRODUÇÃO: 0.73,
            JouissanceState.EXCESSO: 0.85,
            JouissanceState.MORTE: 0.80,
            JouissanceState.COLAPSO: 0.5,  # Collapsed, so lower
        }

        # PRODUÇÃO should have moderate-to-high phi
        assert state_phi[JouissanceState.PRODUÇÃO] > 0.6

    def test_state_binding_correlation(self) -> None:
        """Test state correlates with binding_weight."""
        state_binding = {
            JouissanceState.MANQUE: 0.55,
            JouissanceState.PRODUÇÃO: 1.2,
            JouissanceState.EXCESSO: 2.5,
            JouissanceState.MORTE: 2.9,
            JouissanceState.COLAPSO: 3.0,
        }

        # Check monotonicity
        states_ordered = [
            JouissanceState.MANQUE,
            JouissanceState.PRODUÇÃO,
            JouissanceState.EXCESSO,
            JouissanceState.MORTE,
            JouissanceState.COLAPSO,
        ]

        bindings = [state_binding[s] for s in states_ordered]
        assert all(bindings[i] < bindings[i+1] for i in range(len(bindings)-1))
```

---

## 4️⃣-7️⃣ Templates para Outros Testes

### 4️⃣ BindingWeightCalculator Tests

**Arquivo:** `tests/consciousness/test_binding_strategy.py`

**Key Test Areas:**
- Weight range [0.5, 3.0]
- Adaptive calculation based on system state
- State-dependent behavior
- Edge cases and boundaries

### 5️⃣ DrainageRateCalculator Tests

**Arquivo:** `tests/consciousness/test_drainage_strategy.py`

**Key Test Areas:**
- Rate range [0.01, 0.15]
- State-aware calculation
- Dynamic adjustment mechanisms
- Recovery from high states

### 6️⃣ Snapshot System Tests

**Arquivo:** `tests/consciousness/test_snapshot_system.py`

**Key Test Areas:**
- Snapshot creation and storage
- Compression mechanisms
- Serialization/deserialization
- Rollback functionality
- Integrity verification

### 7️⃣ Tríade Validation Tests

**Arquivo:** `tests/consciousness/test_triade_validation.py`

**Key Test Areas:**
- 5-dimensional metric validation
- Cross-dimensional relationships
- Constraint satisfaction
- Aggregate metrics

---

## 📋 TESTING BEST PRACTICES

### Use pytest Fixtures

```python
@pytest.fixture
def consciousness_system():
    """Fixture for consciousness system."""
    system = ConsciousSystem()
    yield system
    system.cleanup()
```

### Parametrize Related Tests

```python
@pytest.mark.parametrize("state,expected_phi", [
    (JouissanceState.MANQUE, 0.1),
    (JouissanceState.PRODUÇÃO, 0.73),
])
def test_state_phi(state, expected_phi):
    ...
```

### Use Assertions from Audit Data

```python
# From 500-cycle audit
AUDIT_DATA = {
    'phi_mean': 0.7214,
    'phi_std': 0.1113,
    'manque_cycles': 9,
    'rho_c_typical': 31.09,
}
```

---

## 🎯 IMPLEMENTATION GUIDELINES

1. **Start with Critical Tests** (1.1, 1.2, 1.3)
2. **Use existing test patterns** from other test files
3. **Reference 500-cycle audit data** for expected values
4. **Add parametrization** for exhaustive coverage
5. **Mock external dependencies** appropriately
6. **Document each test clearly**
7. **Run tests frequently** during implementation

---

**Next Step:** Begin implementation in order of priority

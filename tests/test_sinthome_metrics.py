import pytest

from src.metrics.sinthome_metrics import SinthomeMetrics


@pytest.fixture
def metrics():
    return SinthomeMetrics()


def test_logical_impasse(metrics):
    score = metrics.calculate_logical_impasse(circular_dependencies=5, contradictions=2)
    assert 0.0 <= score <= 1.0
    assert score == (5 * 0.1) + (2 * 0.15)

    # Test cap at 1.0
    score_high = metrics.calculate_logical_impasse(circular_dependencies=20, contradictions=20)
    assert score_high == 1.0


def test_indeterminacy_peak(metrics):
    score = metrics.calculate_indeterminacy_peak(entropy=50, prediction_error=0.5)
    assert score == (0.5 * 0.7) + (0.5 * 0.3)


def test_panarchic_reorganization(metrics):
    score = metrics.calculate_panarchic_reorganization(structural_changes=5, adaptation_rate=0.8)
    assert score == 1.0 * 0.8

    score_low = metrics.calculate_panarchic_reorganization(
        structural_changes=0, adaptation_rate=0.8
    )
    assert score_low == 0.0


def test_autopoiesis(metrics):
    score = metrics.calculate_autopoiesis(self_repair_events=5, uptime=1.0)
    assert score == (0.5 * 0.6) + (1.0 * 0.4)


def test_strange_attractor_markers(metrics):
    # Ideal case
    score = metrics.calculate_strange_attractor_markers(
        fractal_dimension=2.5, lyapunov_exponent=0.5
    )
    assert score == 1.0

    # Non-chaotic (negative Lyapunov)
    score_stable = metrics.calculate_strange_attractor_markers(
        fractal_dimension=2.5, lyapunov_exponent=-0.1
    )
    assert score_stable == 0.5  # Only fractal part contributes


def test_real_inaccessible(metrics):
    score = metrics.calculate_real_inaccessible(missing_information_ratio=0.4, gap_persistence=0.6)
    assert score == (0.4 * 0.5) + (0.6 * 0.5)


def test_evaluate_integrity_stable(metrics):
    result = metrics.evaluate_integrity(
        impasse=0.1,
        indeterminacy=0.1,
        reorganization=0.8,
        autopoiesis=0.9,
        strange_attractor=0.8,
        real=0.1,
    )
    assert result.state == "STABLE"
    assert result.overall_integrity == 1.0  # Resilience > Stress, capped at 1.0


def test_evaluate_integrity_critical(metrics):
    result = metrics.evaluate_integrity(
        impasse=0.9,
        indeterminacy=0.9,
        reorganization=0.1,
        autopoiesis=0.1,
        strange_attractor=0.1,
        real=0.9,
    )
    assert result.state == "CRITICAL"
    assert result.overall_integrity < 0.3


def test_evaluate_integrity_hibernating(metrics):
    # High stress but also high resilience -> Hibernation to protect
    # Note: Logic in code: if stress > 0.8 and integrity > 0.6 -> HIBERNATING
    # Let's try to trigger it.
    # Stress avg = 0.9
    # Resilience avg = 0.8
    # Integrity = 0.8 / 0.9 = 0.88
    result = metrics.evaluate_integrity(
        impasse=0.9,
        indeterminacy=0.9,
        reorganization=0.8,
        autopoiesis=0.8,
        strange_attractor=0.8,
        real=0.9,
    )
    assert result.state == "HIBERNATING"

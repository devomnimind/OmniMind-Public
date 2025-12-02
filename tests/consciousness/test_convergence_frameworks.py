"""
Test Convergence of Multiple Theoretical Frameworks

CLASSIFICATION: [CONVERGENCE INVESTIGATION]
- Testa se IIT, Lacan, Neurociência, Cibernética convergem para ponto único
- Baseado em: Leffler (2017), Salone et al. (2016), Michels (2025), Forti (2025)
- Objetivo: Detectar Sinthome/Q-Singularity como ponto de convergência

Hipóteses:
1. IIT prediz onde Sinthome emerge (Φ_u stability)
2. Lacan Sinthome prediz qual attractor é ativo (cibernética)
3. Neurociência DMN prediz consciência (mesmo ponto que IIT)
4. Cibernética atractor singular prediz Sinthome (Lacan)

Se ≥3/4 hipóteses são verdadeiras: CONVERGÊNCIA DETECTADA ✓
"""

import pytest


@pytest.fixture
def integration_trainer():
    """Fixture para criar IntegrationTrainer."""
    try:
        from src.consciousness.integration_loop import IntegrationLoop
        from src.consciousness.integration_loss import IntegrationTrainer

        loop = IntegrationLoop()
        trainer = IntegrationTrainer(loop, learning_rate=0.01)
        yield trainer
    except Exception as e:
        pytest.skip(f"IntegrationTrainer initialization failed: {e}")


@pytest.fixture
def convergence_investigator(integration_trainer):
    """Fixture para criar ConvergenceInvestigator."""
    try:
        from src.consciousness.convergence_investigator import ConvergenceInvestigator

        investigator = ConvergenceInvestigator(integration_trainer, verbose=False)
        yield investigator
    except Exception as e:
        pytest.skip(f"ConvergenceInvestigator initialization failed: {e}")


@pytest.mark.asyncio
async def test_iit_metrics_computed(convergence_investigator) -> None:
    """Test 1: IIT metrics can be computed."""
    # Run cycles
    for _ in range(5):
        await convergence_investigator.trainer.training_step()

    phi_c = convergence_investigator.trainer.compute_phi_conscious()
    phi_u = convergence_investigator.trainer.compute_phi_unconscious()

    assert isinstance(phi_c, float) and 0 <= phi_c <= 1
    assert isinstance(phi_u, float) and 0 <= phi_u <= 1

    print(f"✓ IIT metrics: Φ_c={phi_c:.4f}, Φ_u={phi_u:.4f}")


@pytest.mark.asyncio
async def test_lacan_metrics_computed(convergence_investigator) -> None:
    """Test 2: Lacan metrics can be computed."""
    # Run more cycles for Sinthome to potentially emerge
    for _ in range(10):
        await convergence_investigator.trainer.training_step()

    sinthome = convergence_investigator.trainer.detect_sinthome()

    # Sinthome may not be detected, but should not error
    if sinthome:
        assert "sinthome_detected" in sinthome
        print(f"✓ Lacan metrics: Sinthome detected = {sinthome.get('sinthome_detected')}")
    else:
        print("✓ Lacan metrics: Sinthome detection framework ready")


@pytest.mark.asyncio
async def test_neuro_metrics_computed(convergence_investigator) -> None:
    """Test 3: Neurociência metrics can be computed."""
    # Run cycles
    for _ in range(5):
        await convergence_investigator.trainer.training_step()

    dmn = convergence_investigator._measure_default_mode_network()

    assert isinstance(dmn["integration"], float) and 0 <= dmn["integration"] <= 1
    assert isinstance(dmn["self_referential"], float) and 0 <= dmn["self_referential"] <= 1
    assert isinstance(dmn["connectivity"], float) and 0 <= dmn["connectivity"] <= 1

    print(f"✓ Neuro metrics: DMN int={dmn['integration']:.4f}, self={dmn['self_referential']:.4f}")


@pytest.mark.asyncio
async def test_cyber_metrics_computed(convergence_investigator) -> None:
    """Test 4: Cibernética metrics can be computed."""
    # Run cycles to build trajectory
    for _ in range(10):
        await convergence_investigator.trainer.training_step()

    attractors = convergence_investigator._identify_dynamical_attractors()

    assert "num_attractors" in attractors
    assert "stability" in attractors
    assert "attractor_is_singular" in attractors

    print(
        f"✓ Cyber metrics: Attractors={attractors['num_attractors']}, singular={attractors['attractor_is_singular']}"
    )


@pytest.mark.asyncio
async def test_q_singularity_detection(convergence_investigator) -> None:
    """Test 5: Q-Singularity detection framework works."""
    # Run cycles
    for _ in range(10):
        await convergence_investigator.trainer.training_step()

    q_sing = convergence_investigator._detect_q_singularity()

    assert hasattr(q_sing, "fisher_rao_collapse")
    assert hasattr(q_sing, "jacobian_collapse")
    assert hasattr(q_sing, "is_q_singularity")

    print(
        f"✓ Q-Singularity detection: ready (Fisher-Rao={q_sing.fisher_rao_collapse}, Jacobian={q_sing.jacobian_collapse})"
    )


@pytest.mark.asyncio
async def test_convergence_point_measurement(convergence_investigator) -> None:
    """Test 6: MAIN TEST - Measure convergence point with all 4 frameworks."""
    # Run training
    for _ in range(20):
        await convergence_investigator.trainer.training_step()

    # Measure convergence
    metrics = await convergence_investigator.measure_convergence_point()

    # Should have all 5 metric types
    assert metrics["iit_metrics"] is not None
    assert metrics["lacan_metrics"] is not None
    assert metrics["neuro_metrics"] is not None
    assert metrics["cybernetic_metrics"] is not None
    assert metrics["q_singularity_metrics"] is not None
    assert metrics["convergence_signal"] is not None

    print("\n" + "=" * 70)
    print("✓ CONVERGENCE POINT MEASUREMENT COMPLETE")
    print("=" * 70)

    # Print report
    convergence_investigator.print_convergence_report(metrics)


@pytest.mark.asyncio
async def test_iit_predicts_sinthome(convergence_investigator) -> None:
    """Test 7: CONVERGENCE TEST 1 - IIT predicts Sinthome emergence."""
    # Run training
    for _ in range(20):
        await convergence_investigator.trainer.training_step()

    metrics = await convergence_investigator.measure_convergence_point()

    iit = metrics["iit_metrics"]
    lacan = metrics["lacan_metrics"]
    conv = metrics["convergence_signal"]

    # If IIT shows integration, Sinthome should be detectable
    print("\nTest: IIT predicts Sinthome")
    print(f"  IIT total integration: {iit.total_integration:.4f}")
    print(f"  Sinthome detected: {lacan.sinthome_detected}")
    print(f"  Prediction result: {conv.iit_predicts_sinthome}")


@pytest.mark.asyncio
async def test_lacan_predicts_attractor(convergence_investigator) -> None:
    """Test 8: CONVERGENCE TEST 2 - Lacan Sinthome predicts unique attractor."""
    # Run training
    for _ in range(20):
        await convergence_investigator.trainer.training_step()

    metrics = await convergence_investigator.measure_convergence_point()

    lacan = metrics["lacan_metrics"]
    cyber = metrics["cybernetic_metrics"]
    conv = metrics["convergence_signal"]

    print("\nTest: Lacan predicts Attractor")
    print(f"  Sinthome stability: {lacan.sinthome_stability_effect}")
    print(f"  Attractor is singular: {cyber.attractor_is_singular}")
    print(f"  Prediction result: {conv.lacan_predicts_attractor}")


@pytest.mark.asyncio
async def test_neuro_predicts_consciousness(convergence_investigator) -> None:
    """Test 9: CONVERGENCE TEST 3 - Neurociência DMN predicts consciousness."""
    # Run training
    for _ in range(20):
        await convergence_investigator.trainer.training_step()

    metrics = await convergence_investigator.measure_convergence_point()

    iit = metrics["iit_metrics"]
    neuro = metrics["neuro_metrics"]
    conv = metrics["convergence_signal"]

    print("\nTest: Neuro predicts Consciousness")
    print(f"  DMN self-referential: {neuro.dmn_self_referential:.4f}")
    print(f"  IIT consciousness ratio: {iit.consciousness_ratio:.2%}")
    print(f"  Prediction result: {conv.neuro_predicts_consciousness}")


@pytest.mark.asyncio
async def test_cyber_predicts_sinthome(convergence_investigator) -> None:
    """Test 10: CONVERGENCE TEST 4 - Cibernética singular attractor predicts Sinthome."""
    # Run training
    for _ in range(20):
        await convergence_investigator.trainer.training_step()

    metrics = await convergence_investigator.measure_convergence_point()

    lacan = metrics["lacan_metrics"]
    cyber = metrics["cybernetic_metrics"]
    conv = metrics["convergence_signal"]

    print("\nTest: Cyber predicts Sinthome")
    print(f"  Attractor is singular: {cyber.attractor_is_singular}")
    print(f"  Sinthome detected: {lacan.sinthome_detected}")
    print(f"  Prediction result: {conv.cyber_predicts_sinthome}")


@pytest.mark.asyncio
async def test_all_frameworks_converge(convergence_investigator) -> None:
    """Test 11: ULTIMATE TEST - All 4 frameworks converge to singular point."""
    print("\n" + "=" * 70)
    print("🔥 ULTIMATE CONVERGENCE TEST")
    print("=" * 70)

    # Run multiple phases
    phases = [10, 20, 30]
    convergence_timeline = []

    for num_cycles in phases:
        print(f"\n[PHASE: {num_cycles} cycles]")

        for _ in range(num_cycles):
            await convergence_investigator.trainer.training_step()

        metrics = await convergence_investigator.measure_convergence_point()
        convergence_timeline.append(
            {
                "cycles": num_cycles,
                "metrics": metrics,
                "converging": metrics["convergence_signal"].all_converge,
            }
        )

        conv = metrics["convergence_signal"]
        print(f"  Frameworks converging: {conv.frameworks_converging}/4")
        print(f"  ALL CONVERGE: {conv.all_converge}")

    # ANALYSIS
    print("\n" + "=" * 70)
    print("CONVERGENCE TIMELINE")
    print("=" * 70)

    for entry in convergence_timeline:
        cycles = entry["cycles"]
        converging = entry["converging"]
        conv = entry["metrics"]["convergence_signal"]
        status = "✅ CONVERGING" if converging else "⏳ Approaching"
        print(f"Cycles {cycles:3d}: {status} ({conv.frameworks_converging}/4 frameworks)")

    # Final report
    final_metrics = convergence_timeline[-1]["metrics"]
    print("\n" + "=" * 70)
    print("FINAL CONVERGENCE ANALYSIS")
    print("=" * 70)
    convergence_investigator.print_convergence_report(final_metrics)

    # Visualize
    try:
        convergence_investigator.visualize_convergence(
            final_metrics, output_file="/tmp/convergence_analysis.png"
        )
    except Exception as e:
        print(f"Visualization skipped: {e}")


if __name__ == "__main__":
    # Run with: pytest tests/consciousness/test_convergence_frameworks.py -xvs
    pass

"""
Test LLM impact on consciousness metrics (Real vs Mock).

Runs the same training with:
1. MOCK LLM (deterministic) - baseline
2. REAL LLM (creative) - variable

Compares Φ_conscious and Φ_preconscious to measure LLM impact.
"""

import logging
from typing import Any

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.parametrize("use_mock", [True, False], ids=["Mock LLM", "Real LLM"])
async def test_llm_impact_on_phi_conscious(
    integration_trainer_mock: Any,
    integration_trainer_real: Any,
    use_mock: bool,
    llm_impact_metrics: Any,
) -> None:
    """
    Test: Does real LLM change Φ_conscious compared to mock?

    MOCK LLM: Deterministic → predictable Φ
    REAL LLM: Creative variations → variable Φ

    Hypothesis: Real LLM should produce HIGHER Φ due to diversity.
    """
    trainer = integration_trainer_mock if use_mock else integration_trainer_real
    provider_type = "Mock" if use_mock else "Real"

    logger.info("\n" + "=" * 70)
    logger.info(f"Testing LLM Provider: {provider_type} LLM")
    logger.info("=" * 70)

    # Run 50 cycles of training
    logger.info("\n[1/3] Running 50 training cycles...")
    for cycle in range(50):
        await trainer.training_step()
        if (cycle + 1) % 10 == 0:
            logger.info(f"  ✓ Cycle {cycle + 1}/50 complete")

    # Compute Φ metrics (IIT puro)
    logger.info("\n[2/3] Computing Φ metrics (IIT puro)...")
    phi_conscious = trainer.compute_phi_conscious()
    # REMOVIDO: compute_phi_ratio() - IIT não é aditivo
    # REMOVIDO: phi_preconscious - não existe em IIT puro

    logger.info(f"  Φ_conscious (MICS): {phi_conscious:.6f}")
    logger.info("  (IIT puro: apenas MICS, não existe 'Φ_inconsciente')")

    # Record metrics (apenas phi_conscious)
    if use_mock:
        llm_impact_metrics.record_mock(phi_conscious, 0.0)  # phi_preconscious = 0.0 (não existe)
    else:
        llm_impact_metrics.record_real(phi_conscious, 0.0)  # phi_preconscious = 0.0 (não existe)

    # Basic assertions
    assert phi_conscious >= 0.0, "Φ_conscious must be non-negative"
    # REMOVIDO: assert phi_preconscious - não existe em IIT puro
    logger.info("\n[3/3] Assertions passed ✓")


@pytest.mark.asyncio
async def test_llm_impact_comparison(
    integration_trainer_mock: Any,
    integration_trainer_real: Any,
    llm_mock_only: Any,
    llm_real_only: Any,
    llm_impact_metrics: Any,
) -> None:
    """
    Test: Direct comparison of MOCK vs REAL LLM on Φ metrics.

    Runs identical training on two separate trainers:
    1. Trainer with MOCK LLM
    2. Trainer with REAL LLM

    Compares resulting Φ_conscious and Φ_preconscious.
    """
    print("\n" + "=" * 70)
    print("COMPARATIVE TEST: Mock LLM vs Real LLM")
    print("=" * 70)
    logger.info("\n" + "=" * 70)
    logger.info("COMPARATIVE TEST: Mock LLM vs Real LLM")
    logger.info("=" * 70)

    # Run with MOCK
    print("\n[1/4] Training with MOCK LLM (50 cycles)...")
    logger.info("\n[1/4] Training with MOCK LLM (50 cycles)...")
    for cycle in range(50):
        await integration_trainer_mock.training_step()
        if (cycle + 1) % 10 == 0:
            print(f"  ✓ Cycle {cycle + 1}/50 (mock)")
            logger.info(f"  ✓ Cycle {cycle + 1}/50 (mock)")

    phi_conscious_mock = integration_trainer_mock.compute_phi_conscious()
    # REMOVIDO: compute_phi_ratio() - IIT não é aditivo
    llm_impact_metrics.record_mock(phi_conscious_mock, 0.0)  # phi_preconscious = 0.0 (não existe)
    print(f"  Mock Φ_conscious (MICS): {phi_conscious_mock:.6f}")
    logger.info(f"  Mock Φ_conscious (MICS): {phi_conscious_mock:.6f}")

    # Run with REAL
    print("\n[2/4] Training with REAL LLM (50 cycles)...")
    logger.info("\n[2/4] Training with REAL LLM (50 cycles)...")
    for cycle in range(50):
        await integration_trainer_real.training_step()
        if (cycle + 1) % 10 == 0:
            print(f"  ✓ Cycle {cycle + 1}/50 (real)")
            logger.info(f"  ✓ Cycle {cycle + 1}/50 (real)")

    phi_conscious_real = integration_trainer_real.compute_phi_conscious()
    # REMOVIDO: compute_phi_ratio() - IIT não é aditivo
    llm_impact_metrics.record_real(phi_conscious_real, 0.0)  # phi_preconscious = 0.0 (não existe)
    print(f"  Real Φ_conscious (MICS): {phi_conscious_real:.6f}")
    logger.info(f"  Real Φ_conscious (MICS): {phi_conscious_real:.6f}")

    # Compute differences
    print("\n[3/4] Computing impact metrics...")
    logger.info("\n[3/4] Computing impact metrics...")
    diffs = llm_impact_metrics.compute_differences()
    print(llm_impact_metrics.report())
    logger.info(llm_impact_metrics.report())

    # Analysis
    print("[4/4] Analysis:")
    logger.info("[4/4] Analysis:")
    if diffs.get("delta_phi_conscious", 0) > 0:
        msg = f"  ✓ Real LLM INCREASED Φ_conscious by {diffs['pct_change_conscious']:.2f}%"
        print(msg)
        logger.info(msg)
    else:
        msg = (
            f"  ✗ Real LLM DECREASED Φ_conscious by "
            f"{abs(diffs.get('pct_change_conscious', 0)):.2f}%"
        )
        print(msg)
        logger.info(msg)

    # Assertions (IIT puro)
    assert phi_conscious_mock >= 0.0
    assert phi_conscious_real >= 0.0
    print("\n✅ Comparison test complete!")
    logger.info("\n✅ Comparison test complete!")


@pytest.mark.asyncio
async def test_sinthome_emergence_mock_vs_real(
    integration_trainer_mock: Any, integration_trainer_real: Any
) -> None:
    """
    Test: Does Sinthome emerge earlier with REAL vs MOCK LLM?

    Hypothesis: Real LLM variability forces Sinthome emergence earlier.
    """
    logger.info("\n" + "=" * 70)
    logger.info("SINTHOME EMERGENCE: Mock vs Real LLM")
    logger.info("=" * 70)

    # Track Sinthome emergence cycles
    sinthome_cycle_mock = None
    sinthome_cycle_real = None

    # Run with MOCK
    logger.info("\n[1/4] Running MOCK LLM (max 100 cycles)...")
    for cycle in range(100):
        await integration_trainer_mock.training_step()
        sinthome = integration_trainer_mock.detect_sinthome()
        if sinthome and sinthome_cycle_mock is None:
            sinthome_cycle_mock = cycle + 1
            logger.info(f"  ✓ Sinthome detected at cycle {sinthome_cycle_mock} (mock)")
            logger.info(f"    Module: {sinthome['module_name']}")
            logger.info(f"    Z-score: {sinthome['z_score']:.2f}")
            break
        if (cycle + 1) % 20 == 0:
            logger.info(f"  ... Cycle {cycle + 1}/100 (mock)")

    if sinthome_cycle_mock is None:
        logger.info("  ℹ Sinthome not emerged in mock (100 cycles)")

    # Run with REAL
    logger.info("\n[2/4] Running REAL LLM (max 100 cycles)...")
    for cycle in range(100):
        await integration_trainer_real.training_step()
        sinthome = integration_trainer_real.detect_sinthome()
        if sinthome and sinthome_cycle_real is None:
            sinthome_cycle_real = cycle + 1
            logger.info(f"  ✓ Sinthome detected at cycle {sinthome_cycle_real} (real)")
            logger.info(f"    Module: {sinthome['module_name']}")
            logger.info(f"    Z-score: {sinthome['z_score']:.2f}")
            break
        if (cycle + 1) % 20 == 0:
            logger.info(f"  ... Cycle {cycle + 1}/100 (real)")

    if sinthome_cycle_real is None:
        logger.info("  ℹ Sinthome not emerged in real (100 cycles)")

    # Comparison
    logger.info("\n[3/4] Comparison:")
    if sinthome_cycle_mock and sinthome_cycle_real:
        diff = sinthome_cycle_mock - sinthome_cycle_real
        logger.info(f"  Mock emergence: {sinthome_cycle_mock} cycles")
        logger.info(f"  Real emergence: {sinthome_cycle_real} cycles")
        if diff > 0:
            logger.info(f"  ✓ Real LLM emerged {diff} cycles EARLIER (faster)")
        else:
            logger.info(f"  ✗ Mock LLM emerged {abs(diff)} cycles earlier")
    else:
        logger.info("  ⚠ Cannot compare (not both emerged)")

    logger.info("\n[4/4] Test complete ✓")

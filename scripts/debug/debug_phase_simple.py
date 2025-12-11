#!/usr/bin/env python3
"""
DEBUG: Verify if Phase 5, 6, 7 and Epsilon are actually executing
This runs just 3 cycles with DETAILED logging of each phase
"""
import asyncio
import logging
import sys

sys.path.insert(0, "/home/fahbrain/projects/omnimind")

from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace

# Setup logging VERY VERBOSE
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("DEBUG_PHASE")


async def debug_phase_execution():
    """Run 3 cycles with detailed phase logging"""
    logger.info("=" * 80)
    logger.info("PHASE EXECUTION DEBUG TEST (3 cycles)")
    logger.info("=" * 80)

    # Create workspace and loop
    workspace = SharedWorkspace(embedding_dim=256)
    loop = IntegrationLoop(
        workspace=workspace,
        enable_logging=True,
        enable_extended_results=True,  # ✅ ENABLE EXTENDED METRICS (PSI, SIGMA, EPSILON, etc)
    )

    logger.info(f"\n✅ IntegrationLoop initialized")
    logger.info(f"   - _bion_alpha_function: {loop._bion_alpha_function is not None}")
    logger.info(
        f"   - _lacanian_discourse_analyzer: {loop._lacanian_discourse_analyzer is not None}"
    )
    logger.info(f"   - _extended_components: {loop._extended_components is not None}")
    logger.info(f"   - _homeostatic_regulator: {loop._homeostatic_regulator is not None}")

    # Run 3 cycles
    for cycle_num in range(1, 4):
        logger.info(f"\n{'='*80}")
        logger.info(f"CYCLE {cycle_num}")
        logger.info(f"{'='*80}")

        # Execute cycle
        result = await loop.execute_cycle()

        logger.info(f"\n📊 CYCLE RESULT:")
        logger.info(f"   - Φ (phi): {result.phi_estimate}")
        logger.info(f"   - Ψ (psi): {getattr(result, 'psi', 'N/A')}")
        logger.info(f"   - σ (sigma): {getattr(result, 'sigma', 'N/A')}")
        logger.info(f"   - ϵ (epsilon): {getattr(result, 'epsilon', 'N/A')}")
        logger.info(f"   - δ (delta): {getattr(result, 'delta', 'N/A')}")
        logger.info(f"   - Φ_causal (phi_causal): {getattr(result, 'phi_causal', 'N/A')}")
        logger.info(f"   - Repression strength: {getattr(result, 'repression_strength', 'N/A')}")
        logger.info(f"   - Gozo: {getattr(result, 'gozo', 'N/A')}")
        logger.info(
            f"   - Control effectiveness: {getattr(result, 'control_effectiveness', 'N/A')}"
        )
        logger.info(f"   - Modules executed: {result.modules_executed}")

        # CHECK MODULE STATES FOR METADATA
        logger.info(f"\n🔍 CHECKING MODULE STATES:")

        # Check sensory_input for Bion metadata
        sensory_history = workspace.get_module_history("sensory_input", last_n=1)
        if sensory_history:
            metadata = sensory_history[0].metadata
            logger.info(f"\n   [sensory_input - Phase 5 Bion]")
            logger.info(f"   - Has metadata: {metadata is not None}")
            if metadata:
                logger.info(f"   - processed_by: {metadata.get('processed_by', 'NONE')}")
                logger.info(
                    f"   - symbolic_potential: {metadata.get('symbolic_potential', 'NONE')}"
                )
                logger.info(
                    f"   - narrative_form_length: {len(metadata.get('narrative_form', ''))}"
                )
                logger.info(
                    f"   - beta_emotional_charge: {metadata.get('beta_emotional_charge', 'NONE')}"
                )

        # Check narrative for Lacan metadata
        narrative_history = workspace.get_module_history("narrative", last_n=1)
        if narrative_history:
            metadata = narrative_history[0].metadata
            logger.info(f"\n   [narrative - Phase 6 Lacan]")
            logger.info(f"   - Has metadata: {metadata is not None}")
            if metadata:
                logger.info(f"   - processed_by: {metadata.get('processed_by', 'NONE')}")
                logger.info(
                    f"   - lacanian_discourse: {metadata.get('lacanian_discourse', 'NONE')}"
                )
                logger.info(
                    f"   - discourse_confidence: {metadata.get('discourse_confidence', 'NONE')}"
                )

        # Check for Phase 7 (Zimerman is in theoretical_consistency_guard)
        logger.info(f"\n   [Phase 7 Zimerman - via delta calculation]")
        logger.info(f"   - delta: {getattr(result, 'delta', 'N/A')}")
        logger.info(
            f"   - control_effectiveness: {getattr(result, 'control_effectiveness', 'N/A')}"
        )

    logger.info(f"\n{'='*80}")
    logger.info("DEBUG PHASE EXECUTION TEST COMPLETE")
    logger.info(f"{'='*80}")

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(debug_phase_execution())
        if success:
            logger.info("\n✅ DEBUG TEST PASSED")
            sys.exit(0)
        else:
            logger.error("\n❌ DEBUG TEST FAILED")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        sys.exit(1)

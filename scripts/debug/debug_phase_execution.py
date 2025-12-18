#!/usr/bin/env python3
"""
DEBUG: Verify if Phase 5, 6, 7 and Epsilon are actually executing
This runs just 3 cycles with DETAILED logging of each phase
"""
import asyncio
import logging
import sys

# Setup logging VERY VERBOSE
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("DEBUG_PHASE")

# Add src to path
sys.path.insert(0, "/home/fahbrain/projects/omnimind")


from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace


async def debug_phase_execution():
    """Run 3 cycles with detailed phase logging"""
    logger.info("=" * 80)
    logger.info("PHASE EXECUTION DEBUG TEST (3 cycles)")
    logger.info("=" * 80)

    # Create workspace and loop
    workspace = SharedWorkspace(embedding_dim=256)
    loop = IntegrationLoop(
        workspace=workspace,
        enable_logging=True,  # VERBOSE
    )

    logger.info(f"\n✅ IntegrationLoop initialized")
    logger.info(f"   - _bion_alpha_function: {loop._bion_alpha_function is not None}")
    logger.info(
        f"   - _lacanian_discourse_analyzer: {loop._lacanian_discourse_analyzer is not None}"
    )
    logger.info(
        f"   - theoretical_consistency_guard: {loop._consistency_guard is not None} (Phase 7 Zimerman)"
    )
    logger.info(f"   - _desire_engine: {loop._desire_engine is not None}")

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
        logger.info(f"   - Modules executed: {result.modules_executed}")
        logger.info(f"   - Cross-predictions: {result.cross_predictions}")

        # CHECK MODULE STATES FOR METADATA
        logger.info(f"\n🔍 CHECKING MODULE STATES:")

        # Check sensory_input for Bion metadata
        sensory_history = workspace.get_module_history("sensory_input", last_n=1)
        if sensory_history:
            metadata = sensory_history[0].metadata
            logger.info(f"\n   [sensory_input]")
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
            logger.info(f"\n   [narrative]")
            logger.info(f"   - Has metadata: {metadata is not None}")
            if metadata:
                logger.info(f"   - processed_by: {metadata.get('processed_by', 'NONE')}")
                logger.info(
                    f"   - lacanian_discourse: {metadata.get('lacanian_discourse', 'NONE')}"
                )
                logger.info(
                    f"   - discourse_confidence: {metadata.get('discourse_confidence', 'NONE')}"
                )
                logger.info(
                    f"   - emotional_signature_length: {len(str(metadata.get('emotional_signature', '')))}"
                )

        # Check for Zimerman (Phase 7)
        logger.info(f"\n   [zimerman_bonding]")
        try:
            # Zimerman should affect delta calculation
            logger.info(f"   - delta: {getattr(result, 'delta', 'N/A')}")
            logger.info(
                f"   - control_effectiveness: {getattr(result, 'control_effectiveness', 'N/A')}"
            )
        except:
            logger.info(f"   - No Zimerman metrics available")

        # Check for Epsilon
        logger.info(f"\n   [epsilon_desire]")
        logger.info(f"   - epsilon in result: {hasattr(result, 'epsilon')}")
        if hasattr(result, "epsilon"):
            logger.info(f"   - epsilon value: {result.epsilon}")
        else:
            logger.info(f"   - MISSING: epsilon not in ExtendedLoopCycleResult!")

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

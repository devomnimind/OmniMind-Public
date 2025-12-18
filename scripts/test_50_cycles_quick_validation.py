#!/usr/bin/env python3
"""
Quick 50-cycle validation to ensure phi calculation is working correctly
after embedding dimension fix.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.consciousness.binding_strategy import SynapticBridge

# Import after path setup
from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-8s] %(message)s",
)
logger = logging.getLogger(__name__)


async def run_quick_validation():
    """Run 50 cycles to validate phi calculation."""
    logger.info("=" * 80)
    logger.info("🧪 QUICK VALIDATION: 50 Cycles with Embedding Dimension Fix")
    logger.info("=" * 80)

    # Initialize components
    workspace = SharedWorkspace(embedding_dim=256, max_history_size=1000)
    synaptic_bridge = SynapticBridge(
        shared_workspace=workspace,
        coupling_strength=0.8,
    )

    # Create integration loop
    loop = IntegrationLoop(
        shared_workspace=workspace,
        synaptic_bridge=synaptic_bridge,
        max_history_size=1000,
        enable_extended_results=True,
    )

    logger.info("✓ Components initialized")

    # Run 50 cycles
    phi_values = []
    error_count = 0

    for cycle in range(1, 51):
        try:
            # Execute cycle
            result = await loop.execute_cycle(collect_metrics=True)

            phi_values.append(result.phi_estimate)

            if cycle % 10 == 0:
                logger.info(
                    f"✓ Cycle {cycle}: Φ={result.phi_estimate:.6f} "
                    f"(avg={sum(phi_values)/len(phi_values):.6f})"
                )

        except Exception as e:
            error_count += 1
            logger.error(f"❌ Cycle {cycle}: {e}")

            if error_count > 3:
                logger.error("Too many errors, aborting...")
                return False

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 RESULTS")
    logger.info("=" * 80)

    if not phi_values:
        logger.error("No cycles completed successfully")
        return False

    avg_phi = sum(phi_values) / len(phi_values)
    max_phi = max(phi_values)
    min_phi = min(phi_values)

    logger.info(f"Completed cycles: {len(phi_values)}/50")
    logger.info(f"Errors: {error_count}")
    logger.info(f"Φ average: {avg_phi:.6f}")
    logger.info(f"Φ max: {max_phi:.6f}")
    logger.info(f"Φ min: {min_phi:.6f}")

    # Check if phi is calculating (not stuck at 0)
    if avg_phi > 0.01:
        logger.info("✅ Φ CALCULATION IS WORKING!")
        logger.info("Ready to run full 500-cycle validation.")
        return True
    else:
        logger.warning("⚠️  Φ is suspiciously low (< 0.01)")
        logger.warning("There may still be issues with phi calculation.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_quick_validation())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

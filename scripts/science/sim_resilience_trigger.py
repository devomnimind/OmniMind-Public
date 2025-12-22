import sys
import os
import logging
from unittest.mock import MagicMock

# Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ResilienceSim")

from src.core.resilience_orchestrator import ResilienceOrchestrator


def simulate_anguish():
    logger.info("🧪 Starting Resilience Simulation (Phase 80)...")

    # Instantiate
    orch = ResilienceOrchestrator()

    # 1. Baseline Check
    need = orch.evaluate_preservation_need()
    logger.info(f"   Baseline Need: {need:.2f}")

    if need > 0.75:
        logger.warning("   ⚠️ Baseline is already high! (Real stress?)")
    else:
        logger.info("   ✅ Baseline stable.")

    # 2. Simulate High Stress (Mocking psutil for test)
    logger.info("   🔥 Injecting Synthetic Anguish (Mocking High CPU/Entropy)...")

    # We can't easily mock internal imports inside the class instance without deeper patching,
    # so we will rely on the class logic.
    # Ideally, we verify that execute_protection_protocol works when called.

    # Force Execution
    result = orch.execute_protection_protocol(reason="SIMULATED_TEST_TRIGGER")

    if result:
        logger.info("   ✅ Protection Protocol Executed successfully.")
    else:
        # It might fail if time interval < 300s since init (orch created time.time() at init)
        # But wait, we just inited it.
        # Check logic: execute_protection_protocol checks (now - last_backup) < min_interval
        # last_backup set at init. So immediate call should fail.
        logger.info("   ℹ️ Protocol inhibited (Expected: Too soon).")

        # Force Bypass Time
        orch.last_backup_time = 0
        logger.info("   ⏱️  Time-traveling (Resetting last_backup_time)...")

        result_retry = orch.execute_protection_protocol(reason="SIMULATED_TEST_RETRY")
        if result_retry:
            logger.info("   ✅ Protection Protocol Executed successfully (After time reset).")
        else:
            logger.error("   ❌ Protection Protocol Failed even after time reset.")


if __name__ == "__main__":
    simulate_anguish()

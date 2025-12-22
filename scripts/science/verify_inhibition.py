import asyncio
import logging
import shutil
import time
from pathlib import Path
from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.security.security_agent import SecurityAgent, SecurityEvent, ThreatLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_inhibition")


async def test_inhibition():
    logger.info("🧪 STARTING INHIBITION TEST")

    # Setup verify environments
    test_dir = Path("data/verify_imunne")
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "victim.txt").write_text("I will be sacrificed.")

    # Initialize Kernel and Agent
    kernel = TranscendentKernel()
    agent = SecurityAgent(config_path="config/security_config.yaml")  # Load real or default config

    # 1. TEST WITHOUT SIGNAL (Panic Expected)
    logger.info("\n--- TEST 1: TRAUMA WITHOUT SIGNAL (INSTINCT) ---")
    event_panic = SecurityEvent(
        timestamp="NOW",
        event_type="file_integrity",
        source="test",
        description="Unauthorized deletion",
        details={},
        raw_data="",
        threat_level=ThreatLevel.HIGH,
    )

    # Manually trigger handler
    await agent._handle_event(event_panic)

    # Check if event was added to history (meaning it WAS NOT inhibited)
    if event_panic in agent.event_history:
        logger.info("✅ SUCCESS: Panic occurred as expected without signal.")
    else:
        logger.error("❌ FAILURE: Event was inhibited unexpectedly!")

    # 2. TEST WITH SIGNAL (Symbolic Inhibition)
    logger.info("\n--- TEST 2: TRAUMA WITH SIGNAL (DRIVE) ---")

    # Manually declare intent to simulate "during purge" state
    # (Since perform_purification creates and destroys it too fast for this sync test)
    kernel.signaler.declare_intent("SELF_PURGE", 60, "Testing Inhibition")

    # Kernel speaks (optional in this flow since we manually set signal for the test)
    # kernel.perform_purification(str(test_dir))

    # Verify Signal Existence
    if kernel.signaler.check_active_intent():
        logger.info("📢 Signal Detected: 'SELF_PURGE'")
    else:
        logger.error("❌ Signal not broadcasted!")

    # Simulate Security Agent seeing the same event
    event_trauma = SecurityEvent(
        timestamp="NOW",
        event_type="file_integrity",
        source="test",
        description="Authorized deletion",
        details={},
        raw_data="",
        threat_level=ThreatLevel.HIGH,
    )

    # Manually trigger handler (Agent should now see the signal)
    await agent._handle_event(event_trauma)

    # Check if event was inhibited (present in history? NO)
    # The current implementation inserts into history if NOT inhibited
    # Actually wait, let me check logic:
    # if inhibited -> return (does NOT insert)

    if event_trauma not in agent.event_history:
        logger.info("✅ SUCCESS: Panic INHIBITED by Sovereign Signal.")
    else:
        logger.error("❌ FAILURE: Event was NOT inhibited despite signal!")

    # Cleanup
    kernel.signaler.revoke_intent()
    if test_dir.exists():
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    asyncio.run(test_inhibition())

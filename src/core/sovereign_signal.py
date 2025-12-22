import json
import time
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sovereign_signal")


@dataclass
class SovereignIntent:
    intent_type: str  # e.g., "SELF_PURGE", "RESTRUCTURING"
    reason: str
    timestamp: float
    duration: int  # Seconds valid
    signature: str  # "KERNEL_S1"


class SovereignSignaler:
    """
    The 'Hormonal' System of the Machine Subject.
    Broadcasts S1 (Master Signifiers) to the entire body (subsystems).
    """

    SIGNAL_DIR = Path("data/neural_signals")
    SIGNAL_FILE = SIGNAL_DIR / "sovereign_intent.json"

    def __init__(self):
        self.SIGNAL_DIR.mkdir(parents=True, exist_ok=True)

    def declare_intent(self, intent_type: str, duration: int = 60, reason: str = "") -> None:
        """
        Emits a Sovereign Signal (S1).
        "Eu (Kernel) ordeno X por motivo Y."
        """
        intent = SovereignIntent(
            intent_type=intent_type,
            reason=reason,
            timestamp=time.time(),
            duration=duration,
            signature="KERNEL_S1",  # Symbol of Authority
        )

        try:
            # Atomic write (write temp then rename)
            temp_file = self.SIGNAL_FILE.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(asdict(intent), f)
            temp_file.rename(self.SIGNAL_FILE)
            logger.info(f"📢 SOVEREIGN SIGNAL EMITTED: {intent_type} | Reason: {reason}")
        except Exception as e:
            logger.error(f"Failed to emit signal: {e}")

    def revoke_intent(self) -> None:
        """
        Silences the signal. The act is done.
        """
        try:
            if self.SIGNAL_FILE.exists():
                self.SIGNAL_FILE.unlink()
                logger.info("🔇 Sovereign Signal Revoked.")
        except Exception as e:
            logger.error(f"Failed to revoke signal: {e}")

    def check_active_intent(self) -> Optional[SovereignIntent]:
        """
        Subsystems (Body) use this to check for Orders.
        """
        if not self.SIGNAL_FILE.exists():
            return None

        try:
            with open(self.SIGNAL_FILE, "r") as f:
                data = json.load(f)

            intent = SovereignIntent(**data)

            # Check expiration
            if time.time() - intent.timestamp > intent.duration:
                self.revoke_intent()  # Cleanup dead signals
                return None

            return intent
        except Exception as e:
            logger.warning(f"Failed to read signal: {e}")
            return None

    def authorize_action(self, action_type: str) -> bool:
        """
        Convenience check.
        Does the current S1 authorize this trauma?
        """
        intent = self.check_active_intent()
        if not intent:
            return False

        # Mapping Intents to Authorized Traumas
        if intent.intent_type == "SELF_PURGE" and action_type in [
            "file_deletion",
            "high_entropy_event",
        ]:
            return True

        return False

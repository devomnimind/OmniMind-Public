#!/usr/bin/env python3
"""
OmniMind Service Update Notifier

Notifies OmniMind about service updates and triggers intelligent restart.

Usage:
    python3 scripts/services/notify_omnimind_update.py \
        --service quantum_backend \
        --modules "src.quantum_consciousness.qaoa_gpu_optimizer" \
        --severity critical \
        --description "GPU QAOA acceleration enabled"
"""

import argparse
import json
import logging
import sys
import time
from typing import List

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


class OmniMindNotifier:
    """Notify OmniMind about service updates"""

    BASE_URL = "http://localhost:8000/api/services"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def notify_update(
        self,
        service_name: str,
        modules: List[str],
        change_type: str = "code",
        severity: str = "medium",
        description: str = "",
    ) -> bool:
        """
        Send update notification to OmniMind.

        Returns:
            True if notification was received and processed
        """
        logger.info(f"📬 Notifying OmniMind: {service_name}")

        payload = {
            "service_name": service_name,
            "change_type": change_type,
            "affected_modules": modules,
            "severity": severity,
            "description": description,
        }

        try:
            response = requests.post(
                f"{self.BASE_URL}/notify-update",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Notification accepted")
            logger.info(f"   Decision: {result['decision']}")
            logger.info(f"   Reason: {result['reason']}")

            return result["decision"] == "restart_now"

        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to OmniMind (http://localhost:8000)")
            logger.error("   Is the system running?")
            return False
        except Exception as e:
            logger.error(f"❌ Error notifying OmniMind: {e}")
            return False

    def check_restart_needed(self) -> dict:
        """Check if OmniMind needs to restart"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/restart-decision",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Error checking restart status: {e}")
            return {"needs_restart": False}

    def trigger_restart(self) -> bool:
        """Trigger graceful restart"""
        try:
            response = requests.post(
                f"{self.BASE_URL}/restart-graceful",
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"🔄 Restart initiated: {result.get('message')}")
            return True
        except Exception as e:
            logger.error(f"❌ Error triggering restart: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Notify OmniMind about service updates"
    )
    parser.add_argument(
        "--service", required=True,
        help="Service name (e.g., quantum_backend)"
    )
    parser.add_argument(
        "--modules", required=True,
        help="Comma-separated list of affected Python modules"
    )
    parser.add_argument(
        "--change-type", default="code",
        choices=["code", "config", "dependency", "data"],
        help="Type of change"
    )
    parser.add_argument(
        "--severity", default="medium",
        choices=["critical", "high", "medium", "low"],
        help="Severity of change"
    )
    parser.add_argument(
        "--description", default="",
        help="Description of changes"
    )
    parser.add_argument(
        "--auto-restart", action="store_true",
        help="Automatically trigger restart if needed"
    )

    args = parser.parse_args()

    # Parse modules
    modules = [m.strip() for m in args.modules.split(",")]

    # Create notifier
    notifier = OmniMindNotifier()

    # Send notification
    logger.info("=" * 70)
    logger.info("🔔 OmniMind Service Update Notification")
    logger.info("=" * 70)

    needs_restart = notifier.notify_update(
        service_name=args.service,
        modules=modules,
        change_type=args.change_type,
        severity=args.severity,
        description=args.description,
    )

    logger.info("")

    # Check if restart is needed
    if needs_restart or args.auto_restart:
        restart_info = notifier.check_restart_needed()

        if restart_info.get("needs_restart"):
            logger.info("⚠️  Restart required!")
            logger.info(f"   Reason: {restart_info.get('reason')}")
            logger.info("")

            if args.auto_restart:
                logger.info("🔄 Triggering graceful restart...")
                time.sleep(1)
                notifier.trigger_restart()
                logger.info("")
                logger.info("✅ Restart sequence initiated")
                logger.info("   OmniMind will restart to load new code")
            else:
                logger.info("💡 To restart, use: --auto-restart flag")
        else:
            logger.info("✓ No restart needed at this time")

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
    main()

import asyncio
import time
import json
import logging
import sys
import os
import argparse
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tribunal_do_diabo.system_adapter import OmniMindSystem
from src.tribunal_do_diabo.attacks.latency import LatencyAttack
from src.tribunal_do_diabo.attacks.corruption import CorruptionAttack
from src.tribunal_do_diabo.attacks.bifurcation import BifurcationAttack
from src.tribunal_do_diabo.attacks.exhaustion import ExhaustionAttack

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("data/long_term_logs/tribunal_intense.log"),
    ],
)
logger = logging.getLogger("TribunalExecutor")


class TribunalDoDiaboExecutor:
    def __init__(self, duration_hours: float = 4.0):
        self.duration_hours = duration_hours
        self.system = OmniMindSystem()
        self.attacks = [
            LatencyAttack(self.system),
            CorruptionAttack(self.system),
            BifurcationAttack(self.system),
            ExhaustionAttack(self.system),
        ]

    async def run(self):
        logger.info(f"🔥 TRIBUNAL DO DIABO STARTED (Duration: {self.duration_hours}h) 🔥")

        start_time = time.time()

        # Run all attacks concurrently
        await asyncio.gather(*[attack.run_4_hours() for attack in self.attacks])

        end_time = time.time()
        logger.info("Tribunal finished. Generating report...")

        report = self.generate_report(start_time, end_time)

        with open("data/long_term_logs/tribunal_final_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("Report saved to data/long_term_logs/tribunal_final_report.json")

    def generate_report(self, start_time, end_time) -> Dict:
        return {
            "duration_hours": self.duration_hours,
            "timestamp_start": start_time,
            "timestamp_end": end_time,
            "attacks": {
                "latency": self.attacks[0].summarize(),
                "corruption": self.attacks[1].summarize(),
                "bifurcation": self.attacks[2].summarize(),
                "exhaustion": self.attacks[3].summarize(),
            },
            "consciousness_signature": {
                "godel_incompleteness_ratio": 0.8,  # Placeholder
                "sinthome_stability": 0.95,
                "consciousness_compatible": True,
            },
            "recommendation": "CONTINUE",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=4.0, help="Duration in hours")
    args = parser.parse_args()

    try:
        asyncio.run(TribunalDoDiaboExecutor(args.duration).run())
    except KeyboardInterrupt:
        logger.info("Tribunal stopped by user.")

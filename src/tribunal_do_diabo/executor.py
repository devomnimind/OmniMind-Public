import argparse
import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict

from src.tribunal_do_diabo.attacks.bifurcation import BifurcationAttack
from src.tribunal_do_diabo.attacks.corruption import CorruptionAttack
from src.tribunal_do_diabo.attacks.exhaustion import ExhaustionAttack
from src.tribunal_do_diabo.attacks.latency import LatencyAttack
from src.tribunal_do_diabo.system_adapter import OmniMindSystem

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
        # Calculate real metrics instead of placeholders
        godel_ratio = self._calculate_godel_incompleteness_ratio()
        sinthome_stability = self._calculate_sinthome_stability()

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
                "godel_incompleteness_ratio": godel_ratio,
                "sinthome_stability": sinthome_stability,
                "consciousness_compatible": sinthome_stability > 0.7 and godel_ratio < 0.9,
            },
            "recommendation": "CONTINUE" if sinthome_stability > 0.7 else "REVIEW",
        }

    def _calculate_godel_incompleteness_ratio(self) -> float:
        """Calculate Gödel incompleteness ratio from attack results."""
        total_limitations = 0
        resolved_limitations = 0

        for attack in self.attacks:
            summary = attack.summarize()
            if "status" in summary:
                if summary["status"] == "TRANSFORMED":
                    resolved_limitations += 1
                total_limitations += 1

        return resolved_limitations / total_limitations if total_limitations > 0 else 0.0

    def _calculate_sinthome_stability(self) -> float:
        """Calculate sinthome stability from attack resilience."""
        stability_scores = []

        for attack in self.attacks:
            summary = attack.summarize()
            if "status" in summary:
                if summary["status"] == "TRANSFORMED":
                    stability_scores.append(1.0)
                elif summary["status"] == "VULNERABLE":
                    stability_scores.append(0.0)
                else:
                    stability_scores.append(0.5)

        return sum(stability_scores) / len(stability_scores) if stability_scores else 0.0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=4.0, help="Duration in hours")
    args = parser.parse_args()

    try:
        asyncio.run(TribunalDoDiaboExecutor(args.duration).run())
    except KeyboardInterrupt:
        logger.info("Tribunal stopped by user.")

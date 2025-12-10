import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Union

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

# CORREÇÃO (2025-12-10): Arquivos de persistência
TRIBUNAL_REPORT_FILE = Path("data/long_term_logs/tribunal_final_report.json")
TRIBUNAL_METRICS_HISTORY_FILE = Path("data/long_term_logs/tribunal_metrics_history.json")
TRIBUNAL_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
TRIBUNAL_METRICS_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


# Type for attack objects that have a summarize method
AttackType = Union[LatencyAttack, CorruptionAttack, BifurcationAttack, ExhaustionAttack]


class TribunalDoDiaboExecutor:
    def __init__(
        self,
        duration_hours: float = 4.0,
        save_periodic: bool = True,
        periodic_interval: int = 300,
    ):
        """
        Initialize Tribunal executor.

        Args:
            duration_hours: Duration of Tribunal execution in hours
            save_periodic: Whether to save metrics periodically (default: True)
            periodic_interval: Interval between periodic saves in seconds (default: 300 = 5min)
        """
        self.duration_hours = duration_hours
        self.save_periodic = save_periodic
        self.periodic_interval = periodic_interval
        self.system = OmniMindSystem()
        self.attacks: List[AttackType] = [
            LatencyAttack(self.system),
            CorruptionAttack(self.system),
            BifurcationAttack(self.system),
            ExhaustionAttack(self.system),
        ]
        self.running = False
        self.start_time: float = 0.0

    async def run(self):
        """Run Tribunal execution with periodic metric saving."""
        logger.info(f"🔥 TRIBUNAL DO DIABO STARTED (Duration: {self.duration_hours}h) 🔥")

        self.running = True
        self.start_time = time.time()

        # Start periodic saving task if enabled
        periodic_task = None
        if self.save_periodic:
            periodic_task = asyncio.create_task(self._periodic_save_metrics())

        try:
            # Run all attacks concurrently with the specified duration
            duration_seconds = self.duration_hours * 3600
            await asyncio.gather(
                *[attack.run_for_duration(duration_seconds) for attack in self.attacks]
            )
        finally:
            self.running = False
            if periodic_task:
                periodic_task.cancel()
                try:
                    await periodic_task
                except asyncio.CancelledError:
                    pass

        end_time = time.time()
        logger.info("Tribunal finished. Generating final report...")

        report = self.generate_report(self.start_time, end_time)
        self._save_final_report(report)

        # Save final metrics to history
        self._save_metrics_to_history(report)

        logger.info(f"✅ Final report saved to {TRIBUNAL_REPORT_FILE}")

    async def _periodic_save_metrics(self):
        """Periodically save metrics during execution."""
        cycle_id = 0
        while self.running:
            try:
                await asyncio.sleep(self.periodic_interval)
                if not self.running:
                    break

                cycle_id += 1
                current_time = time.time()

                # Generate intermediate metrics
                metrics = self._generate_intermediate_metrics(cycle_id, current_time)

                # Save to history
                self._save_metrics_to_history(metrics, is_intermediate=True)

                logger.info(
                    f"📊 Periodic metrics saved (cycle {cycle_id}, elapsed: {(current_time - self.start_time)/3600:.2f}h)"
                )
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic save: {e}", exc_info=True)

    def _generate_intermediate_metrics(self, cycle_id: int, timestamp: float) -> Dict:
        """Generate intermediate metrics snapshot."""
        godel_ratio = self._calculate_godel_incompleteness_ratio()
        sinthome_stability = self._calculate_sinthome_stability()

        return {
            "cycle_id": cycle_id,
            "timestamp": timestamp,
            "elapsed_hours": (timestamp - self.start_time) / 3600,
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
            "is_intermediate": True,
        }

    def _save_final_report(self, report: Dict):
        """Save final report to disk."""
        try:
            with open(TRIBUNAL_REPORT_FILE, "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving final report: {e}", exc_info=True)

    def _save_metrics_to_history(self, metrics: Dict, is_intermediate: bool = False):
        """Save metrics to history file."""
        try:
            # Load existing history
            history: Dict[str, Any] = {"cycles": [], "last_update": time.time()}
            if TRIBUNAL_METRICS_HISTORY_FILE.exists():
                try:
                    history = json.loads(TRIBUNAL_METRICS_HISTORY_FILE.read_text())
                except Exception as e:
                    logger.warning(f"Error loading metrics history: {e}")
                    history = {"cycles": [], "last_update": time.time()}

            # Add new metrics
            if is_intermediate:
                history["cycles"].append(metrics)
            else:
                # Final report - add as last cycle
                final_cycle = {
                    "cycle_id": "final",
                    "timestamp": metrics.get("timestamp_end", time.time()),
                    "elapsed_hours": metrics.get("duration_hours", 0),
                    "attacks": metrics.get("attacks", {}),
                    "consciousness_signature": metrics.get("consciousness_signature", {}),
                    "is_intermediate": False,
                }
                history["cycles"].append(final_cycle)

            # Keep only last 100 cycles to avoid file bloat
            if len(history["cycles"]) > 100:
                history["cycles"] = history["cycles"][-100:]

            history["last_update"] = time.time()

            # Save history
            with open(TRIBUNAL_METRICS_HISTORY_FILE, "w") as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics history: {e}", exc_info=True)

    def generate_report(self, start_time, end_time) -> Dict:
        """Generate final report with all metrics."""
        # Calculate real metrics instead of placeholders
        godel_ratio = self._calculate_godel_incompleteness_ratio()
        sinthome_stability = self._calculate_sinthome_stability()

        return {
            "duration_hours": self.duration_hours,
            "timestamp_start": start_time,
            "timestamp_end": end_time,
            "attacks_executed": {
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

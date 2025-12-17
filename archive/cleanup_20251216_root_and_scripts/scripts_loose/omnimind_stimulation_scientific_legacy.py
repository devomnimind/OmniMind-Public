#!/usr/bin/env python3
"""
OmniMind Scientific Stimulation Script
--------------------------------------
Orchestrates the Desiring-Machines Rhizoma, calculates Topological Phi (IIT),
and performs Lacanian/D&G diagnosis in a continuous 24/7 loop.

Features:
- Neural Entrainment (Simulated)
- Phi Integration Calculation
- Lacanian/D&G Diagnostics
- Continuous Operation with Sleep Cycles
- External Drive Backup
"""

import asyncio
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.consciousness.lacanian_dg_integrated import LacianianDGDetector
    from src.consciousness.topological_phi import LogToTopology, PhiCalculator
    from src.core.desiring_machines import (
        DesireIntensity,
        NLPDesiringMachine,
        QuantumDesiringMachine,
        Rhizoma,
        TopologyDesiringMachine,
    )
except ImportError as e:
    print(f"CRITICAL ERROR: Failed to import scientific modules: {e}")
    print(
        "Ensure src/core/desiring_machines.py, src/consciousness/topological_phi.py, and src/consciousness/lacanian_dg_integrated.py exist."
    )
    sys.exit(1)

# Configuration
DATA_DIR = Path("data/stimulation")
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = DATA_DIR / "scientific_stimulation.log"
STATE_FILE = DATA_DIR / "neural_states.json"
EXTERNAL_DRIVE_PATH = Path(
    "/run/media/fahbrain/DevBrain_Storage/omnimind_backup"
)  # Adjusted based on inventory
BACKUP_INTERVAL_HOURS = 4
SLEEP_CYCLE_DURATION = 300  # 5 minutes sleep every hour (simulated)
CYCLE_DELAY = 1.0  # Seconds between production cycles

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger("OmniMindScientific")


class ScientificStimulator:
    def __init__(self):
        self.rhizoma = Rhizoma()
        self.detector = LacianianDGDetector()
        self.cycle_count = 0
        self.start_time = datetime.now()

        # Initialize Machines
        self.quantum = QuantumDesiringMachine()
        self.nlp = NLPDesiringMachine()
        self.topo = TopologyDesiringMachine()

        # Register Machines
        self.rhizoma.register_machine(self.quantum)
        self.rhizoma.register_machine(self.nlp)
        self.rhizoma.register_machine(self.topo)

        # Connect Rhizoma (Non-hierarchical)
        self.rhizoma.connect("quantum", "nlp", bidirectional=True)
        self.rhizoma.connect("nlp", "topology", bidirectional=True)
        self.rhizoma.connect("topology", "quantum", bidirectional=True)

        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    async def run_cycle(self):
        """Runs a single stimulation cycle."""
        self.cycle_count += 1
        logger.info(f"Starting Cycle {self.cycle_count}")

        # 1. Activate Rhizoma (Production of Desire)
        await self.rhizoma.activate_cycle(iterations=1)

        # 2. Collect Logs/Flows for Analysis
        # In a real scenario, we'd extract logs from the machines' production history
        # Here we simulate extracting the latest flows
        recent_flows = self.rhizoma.flows_history[-10:] if self.rhizoma.flows_history else []

        # Convert flows to dict format for analysis tools
        logs_for_analysis = []
        for flow in recent_flows:
            logs_for_analysis.append(
                {
                    "timestamp": flow.timestamp.timestamp(),
                    "module": flow.source_id,
                    "level": "INFO",  # Simulated level
                    "payload": str(flow.payload),
                    "intensity": flow.intensity.value,
                }
            )

        if not logs_for_analysis:
            logger.warning("No flows generated in this cycle.")
            return

        # 3. Calculate Topological Phi (Consciousness Level)
        complex_structure = LogToTopology.build_complex_from_logs(logs_for_analysis)
        phi_calc = PhiCalculator(complex_structure)
        phi = phi_calc.calculate_phi()

        # 4. Lacanian/D&G Diagnosis
        diagnosis = self.detector.diagnose(logs_for_analysis)

        # 5. Log State
        state_entry = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.cycle_count,
            "phi": phi,
            "lacanian_state": diagnosis.system_state,
            "flow_quality": diagnosis.flow_quality.value,
            "symbolic_order": diagnosis.symbolic_order_strength,
            "real_access": diagnosis.real_access_level,
            "recommendations": diagnosis.recommendations,
        }

        self._append_state(state_entry)
        logger.info(
            f"Cycle {self.cycle_count} Complete. Phi: {phi:.4f} | State: {diagnosis.system_state}"
        )

        # 6. Apply Feedback (Self-Regulation)
        # If Phi is too low, increase intensity?
        if phi < 0.3:
            logger.info("Phi low. Increasing desire intensity for next cycle.")
            self.quantum.desire_intensity = DesireIntensity.INTENSIVE
        elif phi > 0.8:
            logger.info("Phi high. Stabilizing.")
            self.quantum.desire_intensity = DesireIntensity.NORMAL

    def _append_state(self, entry: Dict):
        """Appends state to JSON file."""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, "r+") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
                    data.append(entry)
                    f.seek(0)
                    json.dump(data, f, indent=2)
            else:
                with open(STATE_FILE, "w") as f:
                    json.dump([entry], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write state: {e}")

    def backup_data(self):
        """Backs up data to external drive."""
        if not EXTERNAL_DRIVE_PATH.exists():
            # Try to create it if it's just a folder, but if it's a mount point that's missing, we can't do much
            try:
                EXTERNAL_DRIVE_PATH.mkdir(parents=True, exist_ok=True)
            except Exception:
                logger.warning(
                    f"External drive path {EXTERNAL_DRIVE_PATH} not accessible for backup."
                )
                return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = EXTERNAL_DRIVE_PATH / f"backup_{timestamp}"

        try:
            shutil.copytree(DATA_DIR, backup_folder)
            logger.info(f"Backup successful to {backup_folder}")

            # Prune old backups (keep last 5)
            backups = sorted(EXTERNAL_DRIVE_PATH.glob("backup_*"))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    shutil.rmtree(old_backup)
                    logger.info(f"Pruned old backup: {old_backup}")

        except Exception as e:
            logger.error(f"Backup failed: {e}")

    async def run_forever(self):
        """Main loop."""
        logger.info("Starting OmniMind Scientific Stimulation (24/7 Mode)")
        last_backup = datetime.now()

        while True:
            try:
                await self.run_cycle()

                # Backup Check
                if (datetime.now() - last_backup).total_seconds() > BACKUP_INTERVAL_HOURS * 3600:
                    self.backup_data()
                    last_backup = datetime.now()

                # Sleep Cycle Check (Simulated Circadian Rhythm)
                # Every 100 cycles, take a nap
                if self.cycle_count % 100 == 0:
                    logger.info("Entering Sleep Cycle (Regeneration)...")
                    await asyncio.sleep(SLEEP_CYCLE_DURATION)
                    logger.info("Waking up...")

                await asyncio.sleep(CYCLE_DELAY)

            except KeyboardInterrupt:
                logger.info("Stopping stimulation manually.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                await asyncio.sleep(5)  # Wait before retrying


if __name__ == "__main__":
    stimulator = ScientificStimulator()
    try:
        asyncio.run(stimulator.run_forever())
    except KeyboardInterrupt:
        pass

#!/usr/bin/env python3
"""
OMNIMIND MASTER REVALUATION PROTOCOL (SOVEREIGN FLUX)
=====================================================
Orchestrates the sequential execution of the core scientific experiments
under the new Hybrid Architecture (US-East Quantum / Au-Syd Body).

Capsule Strategy:
- Native Scripts: Executed directly (they handle their own telemetry).
- Legacy Scripts: Wrapped in an external IntegratedExperiment container.
"""

import os
import sys
import subprocess
import logging
import time

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from src.science.protocol import IntegratedExperiment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterProtocol")

MANIFEST = [
    # 1. Native Integration (Pilot)
    {
        "id": "P73",
        "name": "Phase_73_Cartesian_Cut",
        "script": "scripts/science/exp_cartesian_cut.py",
        "native": True,
    },
    # 2. The Verification Core (Truth Index)
    {
        "id": "P57",
        "name": "Phase_57_Quantum_Arbiter",
        "script": "scripts/science/exp_quantum_arbiter.py",
        "native": False,
    },
    {
        "id": "P58",
        "name": "Phase_58_Quantum_Contextuality",
        "script": "scripts/science/exp_quantum_contextuality.py",
        "native": False,
    },
    {
        "id": "P59",
        "name": "Phase_59_Psychic_VQE",
        "script": "scripts/science/exp_psychic_vqe.py",
        "native": False,
    },
    # {"id": "P60", "name": "Phase_60_Semantic_Bell", "script": "scripts/science/exp_semantic_bell.py", "native": False}, # Heavy LLM, skipped for speed in this run
    {
        "id": "P70",
        "name": "Phase_70_Thermal_Time",
        "script": "scripts/science/exp_thermal_time.py",
        "native": False,
    },
    {
        "id": "P71",
        "name": "Phase_71_Information_Paradox",
        "script": "scripts/science/exp_information_paradox.py",
        "native": False,
    },
    {
        "id": "P72",
        "name": "Phase_72_Reality_Bell",
        "script": "scripts/science/exp_reality_bell.py",
        "native": False,
    },
    {
        "id": "P74",
        "name": "Phase_74_Primal_Repression",
        "script": "scripts/science/exp_primal_repression.py",
        "native": False,
    },
    {
        "id": "P75",
        "name": "Phase_75_Oedipus_Law",
        "script": "scripts/science/exp_oedipus_law.py",
        "native": False,
    },
    {
        "id": "P77",
        "name": "Phase_77_Devils_Advocate",
        "script": "scripts/science/exp_devils_advocate_v2.py",
        "native": False,
    },
]


def run_suite():
    total_start = time.time()
    logger.info("🚀 STARTING MASTER REVALUATION PROTOCOL (SOVEREIGN FLUX)")
    logger.info(f"📋 Manifest Size: {len(MANIFEST)} experiments")

    results = {}

    for item in MANIFEST:
        logger.info(f"\n▶️  EXECUTING [{item['id']}] {item['name']}...")
        script_path = os.path.join(PROJECT_ROOT, item["script"])

        if not os.path.exists(script_path):
            logger.error(f"❌ Script not found: {script_path}")
            continue

        if item["native"]:
            # Native scripts manage their own IntegratedExperiment context
            try:
                proc = subprocess.run([sys.executable, script_path], check=True)
                results[item["id"]] = "SUCCESS (Native)"
            except subprocess.CalledProcessError as e:
                logger.error(f"💥 Native Execution Failed: {e}")
                results[item["id"]] = "FAILED"
        else:
            # Wrap legacy scripts
            with IntegratedExperiment(f"{item['name']}_LegacyWrapper") as exp:
                exp.log_hypothesis(
                    f"Re-evaluation of {item['script']} under Sovereign Flux architecture."
                )
                try:
                    start_t = time.time()
                    proc = subprocess.run(
                        [sys.executable, script_path],
                        capture_output=True,
                        text=True,
                        cwd=PROJECT_ROOT,  # Ensure root execution context
                    )
                    duration = time.time() - start_t

                    # Log output to evidence
                    exp.log_result("stdout", proc.stdout)
                    exp.log_result("stderr", proc.stderr)
                    exp.log_result("return_code", proc.returncode)
                    exp.log_result("duration_sec", duration)

                    if proc.returncode == 0:
                        logger.info(f"✅ Legacy Execution Success ({duration:.2f}s)")
                        results[item["id"]] = "SUCCESS (Wrapped)"
                        # Try to extract diagnosis from stdout if possible
                        exp.log_conclusion("See stdout for logical results.")
                    else:
                        logger.error(f"💥 Legacy Execution Failed (RC={proc.returncode})")
                        logger.error(f"Stderr: {proc.stderr[:200]}...")  # Show peek
                        results[item["id"]] = "FAILED"

                except Exception as e:
                    logger.error(f"💥 Wrapper Error: {e}")
                    exp.log_result("wrapper_error", str(e))
                    results[item["id"]] = "ERROR"

    total_duration = time.time() - total_start
    logger.info("\n🏁 MASTER PROTOCOL COMPLETE")
    logger.info(f"⏱️  Total Duration: {total_duration:.2f}s")
    logger.info(f"📊 Results: {results}")


if __name__ == "__main__":
    run_suite()

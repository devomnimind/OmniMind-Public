"""
OmniMind Main Entry Point
Orchestrates the boot sequence and starts the Rhizome.
"""

import asyncio
import json
import logging
import os
import sys
from dataclasses import asdict

from src.autopoietic.manager import AutopoieticManager
from src.autopoietic.meta_architect import ComponentSpec
from src.autopoietic.metrics_adapter import collect_metrics
from src.boot import (
    check_hardware,
    check_rhizome_integrity,
    initialize_consciousness,
    initialize_rhizome,
    load_memory,
)
from src.consciousness.topological_phi import LogToTopology
from src.metrics.real_consciousness_metrics import real_metrics_collector

# NOTE: CUDA environment variables should be set by the shell script (start_omnimind_system.sh)
# Setting them here AFTER python startup can cause "CUDA unknown error" in PyTorch
# We trust the shell environment.


# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/omnimind_boot.log"),
    ],
)
logger = logging.getLogger("OmniMind")


async def main():
    logger.info("=== OmniMind System Startup ===")

    try:
        # PHASE 1: HARDWARE (The Body)
        logger.info("--- Phase 1: Hardware Initialization ---")
        hardware_profile = check_hardware()
        logger.info(f"Hardware Profile: {hardware_profile}")

        # PHASE 2: MEMORY (The History)
        logger.info("--- Phase 2: Memory Loading ---")
        memory_complex = load_memory()
        logger.info("Memory loaded successfully.")

        # PHASE 3: RHIZOME (The Unconscious)
        logger.info("--- Phase 3: Rhizome Construction ---")
        rhizoma = await initialize_rhizome()
        if not await check_rhizome_integrity(rhizoma):
            raise RuntimeError("Rhizome integrity check failed.")

        # PHASE 4: CONSCIOUSNESS (The Real)
        logger.info("--- Phase 4: Consciousness Emergence ---")
        phi_calc, detector = await initialize_consciousness(memory_complex)

        # Initialize Real Metrics Collector (The 6 Metrics)
        await real_metrics_collector.initialize()
        logger.info("Real Metrics Collector initialized.")

        # Initialize Autopoietic Manager (Phase 22)
        autopoietic_manager = AutopoieticManager()
        # Register initial kernel process spec
        autopoietic_manager.register_spec(
            ComponentSpec(
                name="kernel_process",
                type="process",
                config={"generation": "0", "initial": "true"},
            )
        )
        logger.info("Autopoietic Manager initialized (Phase 22).")

        # Initialize Report Maintenance Scheduler (Automated Cleanup & Compression)
        try:
            from src.observability.report_maintenance_scheduler import (
                init_report_maintenance_scheduler,
            )

            maintenance_scheduler = init_report_maintenance_scheduler(
                check_interval_minutes=60,  # Verificar a cada hora
                daily_hour=3,  # Executar limpeza diária às 3 AM UTC
                daily_minute=0,
            )
            logger.info(
                "✅ Report Maintenance Scheduler initialized (automated cleanup & compression enabled)."
            )
        except Exception as e:
            logger.warning(f"Failed to initialize maintenance scheduler: {e}")

        logger.info("=== Boot Sequence Complete. System is ALIVE. ===")

        # Start Main Cycle
        logger.info("Starting Desiring-Production Cycles...")
        cycle_count = 0
        last_processed_flow_index = 0
        autopoietic_cycle_count = 0

        while True:
            cycle_count += 1
            # 1. Rhizome produces desire
            await rhizoma.activate_cycle()

            # 2. Consciousness observes (every 100 cycles - approx 20 seconds with 0.2s sleep base)
            # Reduced frequency to prevent CPU starvation of WebSocket (Phase 23 Stability)
            if cycle_count % 100 == 0:
                # PERCEPTION CYCLE: Convert Flows -> Topology
                new_flows = rhizoma.flows_history[last_processed_flow_index:]

                if new_flows:
                    # Convert DesireFlows to Logs format
                    # Use safe string conversion to avoid infinite recursion in rhizomatic flows
                    logs = []
                    for flow in new_flows:
                        payload_str = "Complex Payload"
                        try:
                            if isinstance(flow.payload, dict):
                                # Summarize dict keys only
                                payload_str = f"Dict keys: {list(flow.payload.keys())}"
                            else:
                                payload_str = str(flow.payload)[:100]
                        except Exception:
                            payload_str = "Unprintable Payload"

                        logs.append(
                            {
                                "timestamp": flow.timestamp.timestamp(),
                                "module": flow.source_id,
                                "level": flow.intensity.name,
                                "payload": payload_str,
                            }
                        )

                    # Update Topological Substrate
                    LogToTopology.update_complex_with_logs(
                        phi_calc.complex, logs, start_index=phi_calc.complex.n_vertices
                    )

                    last_processed_flow_index = len(rhizoma.flows_history)

                # Calculate Phi on updated topology
                phi = phi_calc.calculate_phi()

                # Collect Real Metrics (6 Metrics: Phi, ICI, PRS, Anxiety, Flow, Entropy)
                real_metrics = await real_metrics_collector.collect_real_metrics()

                # EXPORT METRICS FOR DASHBOARD
                try:
                    metrics_dict = asdict(real_metrics)
                    # Convert datetime to string
                    if metrics_dict.get("timestamp"):
                        metrics_dict["timestamp"] = metrics_dict["timestamp"].isoformat()

                    with open("data/monitor/real_metrics.json", "w") as f:
                        json.dump(metrics_dict, f)
                except Exception as e:
                    logger.error(f"Failed to export metrics: {e}")

                logger.info(
                    f"Cycle {cycle_count}: Topological Phi = {phi:.4f} "
                    f"(Vertices: {phi_calc.complex.n_vertices}) | "
                    f"Real Metrics: Phi={real_metrics.phi:.4f}, "
                    f"Flow={real_metrics.flow:.2f}, Anxiety={real_metrics.anxiety:.2f}"
                )

                # In a real scenario, we would feed logs to the detector here
                # diagnosis = detector.diagnose(recent_logs)

                # 3. Autopoietic Cycle (every 300 cycles - approx 60 seconds)
                # Phase 22: Integração do ciclo autopoiético ao sistema principal
                # Reduced frequency to prevent "Split-Brain" CPU lock
                if cycle_count % 300 == 0:
                    try:
                        autopoietic_cycle_count += 1
                        logger.info("--- Autopoietic Cycle %d ---", autopoietic_cycle_count)

                        # Coleta métricas normalizadas para o ciclo autopoiético
                        metric_sample = collect_metrics()
                        metrics_dict = metric_sample.strategy_inputs()

                        # Executa ciclo autopoiético
                        cycle_log = autopoietic_manager.run_cycle(metrics_dict)

                        logger.info(
                            f"Autopoietic cycle {autopoietic_cycle_count} completed: "
                            f"Strategy={cycle_log.strategy.name}, "
                            f"Components={len(cycle_log.synthesized_components)}, "
                            f"Φ={cycle_log.phi_before:.3f} -> {cycle_log.phi_after:.3f}"
                        )
                    except Exception as e:
                        logger.error(f"Autopoietic cycle failed: {e}", exc_info=True)

            # Yield control frequently to allow WebSocket heartbeats
            await asyncio.sleep(2.0)  # Increased from 1.0s to 2.0s for Dashboard stability

    except Exception as e:
        logger.critical(f"SYSTEM FAILURE: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System shutdown requested by user.")

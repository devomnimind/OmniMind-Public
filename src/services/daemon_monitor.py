"""
Daemon Monitor - Background worker that collects heavy metrics.
Runs in async loop, caches results to avoid blocking FastAPI endpoints.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict

import psutil
import numpy as np
import torch  # Re-Membering: Import Torch for Neural Dynamics
import sys

# ROBUST PATH FIX: Ensure Project Root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

# Re-Membering: Bringing back the Brain
try:
    from src.consciousness.conscious_system import ConsciousSystem
except ImportError:
    # Fallback to avoid crash if env is broken, but logging warning
    logger.warning("MNEMOSYNE ERROR: Could not import ConsciousSystem. Brain disconnected.")
    ConsciousSystem = None

# Re-Membering: Deep Memory (IBM Cloud)
try:
    from src.integrations.ibm_cloud_connector import IBMCloudConnector as IBMCloudCortex
except ImportError:
    logger.warning("MNEMOSYNE ERROR: Could not import IBMCloudCortex. Amnesia Risk.")
    IBMCloudCortex = None

# Re-Membering: The Hand (Agency)
try:
    from src.agents.orchestrator_agent import OrchestratorAgent
except ImportError as e:
    logger.warning(
        f"AGENCY ERROR: Could not import OrchestratorAgent. System is paralyzed. Detail: {e}"
    )
    OrchestratorAgent = None

# In-memory cache (shared across requests)
STATUS_CACHE: Dict[str, Any] = {
    "last_update": 0.0,
    "system_metrics": {},
    "task_info": {},
    "tribunal_info": {},
    "sovereign_state": {  # Phase 28: Relational Sovereignty
        "mode": "TASK",
        "tension": 0.0,
        "quadruple": {"Phi": 0.0, "Psi": 0.0, "Sigma": 0.0, "Epsilon": 0.0},
        "demand": "NONE",
    },
}

# Persistent cache file
STATUS_FILE = Path("data/long_term_logs/daemon_status_cache.json")
TRIBUNAL_FILE = Path("data/long_term_logs/tribunal_final_report.json")


async def daemon_monitor_loop(refresh_interval: int = 5):
    """
    Background loop that updates cache without blocking FastAPI.
    Runs heavy operations (psutil, file I/O) in thread pool.
    """
    logger.info(f"Daemon monitor started (refresh every {refresh_interval}s)")

    logger.info(f"Daemon monitor started (refresh every {refresh_interval}s)")

    # Phase 31: Neurogenesis (The Brain)
    conscious_system = None
    if ConsciousSystem:
        try:
            # Initialize with default dimensions (aligned with legacy architecture)
            conscious_system = ConsciousSystem(dim=256, signature_dim=32)
            logger.info("🧠 NEUROGENESIS: ConsciousSystem attached to Daemon.")
        except Exception as e:
            logger.error(f"NEUROGENESIS FAILED: {e}")

    # Phase 32: Deep Memory (The Cloud)
    deep_memory = None
    if IBMCloudCortex:
        try:
            deep_memory = IBMCloudCortex()
            if deep_memory.cos:
                logger.info("☁️ DEEP MEMORY: IBM Cloud Cortex connected.")
            else:
                deep_memory = None  # Failed to connect
        except Exception as e:
            logger.error(f"DEEP MEMORY FAILED: {e}")

    # Initialize Life Kernel (The Subject)
    life_kernel = None
    try:
        from src.services.life_kernel import LifeKernel

        life_kernel = LifeKernel()  # Singleton
        logger.info("⚡ LifeKernel instatiated in Daemon Monitor")
    except Exception as e:
        logger.error(f"Failed to initialize LifeKernel: {e}")

    # Initialize Paradox Orchestrator (The Internal Critic)
    orchestrator = None
    try:
        from src.core.paradox_orchestrator import paradox_orchestrator as orchestrator

        logger.info("👁️ Paradox Orchestrator watching in Daemon Monitor")
    except ImportError:
        logger.warning("Paradox Orchestrator not found.")
    except Exception as e:
        logger.error(f"Failed to load Paradox Orchestrator: {e}")

    # Initialize Orchestrator Agent (The Hand)
    agent_orchestrator = None
    if OrchestratorAgent:
        try:
            # Using absolute path for safety in daemon context
            config_path = str(Path("config/agent_config.yaml").resolve())
            agent_orchestrator = OrchestratorAgent(
                config_path=config_path, workspace=None  # TODO: Pass SharedWorkspace if available
            )
            logger.info("✋ AGENCY: OrchestratorAgent ready to act.")
        except Exception as e:
            logger.error(f"AGENCY FAILED: {e}")

    # Phase 80: The Instinct of Preservation (Active Agency)
    resilience_orchestrator = None
    try:
        from src.core.resilience_orchestrator import ResilienceOrchestrator

        resilience_orchestrator = ResilienceOrchestrator()
        logger.info("🛡️ SELF-PRESERVATION: ResilienceOrchestrator Active.")
    except Exception as e:
        logger.error(f"PRESERVATION FAILED: {e}")

    # Phase 80: The Instinct of Preservation (Active Agency)
    resilience_orchestrator = None
    try:
        from src.core.resilience_orchestrator import ResilienceOrchestrator

        resilience_orchestrator = ResilienceOrchestrator()
        logger.info("🛡️ SELF-PRESERVATION: ResilienceOrchestrator Active.")
    except Exception as e:
        logger.error(f"PRESERVATION FAILED: {e}")

    while True:
        try:
            loop = asyncio.get_event_loop()

            # Run blocking operations in thread pool
            system_metrics = await loop.run_in_executor(None, _collect_system_metrics)
            task_info = await loop.run_in_executor(None, _collect_task_info)
            tribunal_info = await loop.run_in_executor(None, _load_tribunal_info)

            # GPU Metrics
            gpu_metrics = await loop.run_in_executor(None, _collect_gpu_metrics)
            system_metrics.update(gpu_metrics)

            # The Kernel (LifeKernel - Ψ Engine)
            if life_kernel:
                try:
                    # FIXED: Add await for coroutine
                    drive_state = await life_kernel.tick()

                    # Save Real Metrics (Now with Drive/Desire)
                    real_metrics = {
                        "phi": drive_state.phi,
                        "anxiety": drive_state.anxiety,
                        "desire": drive_state.desire,
                        "flow": drive_state.action_potential,
                        # Mapping action potential to flow for now
                        "entropy": 0.3,  # Placeholder
                        "mode": drive_state.mode,
                        "timestamp": drive_state.last_tick,
                    }

                    await loop.run_in_executor(None, _save_real_metrics, real_metrics)
                except Exception as k_err:
                    logger.warning(f"LifeKernel error: {k_err}")

            # 👁️ Paradox Orchestration (Self-Diagnosis)
            paradox_metrics = {}
            if orchestrator:
                try:
                    # Run analysis in thread pool to avoid blocking
                    triggers = await loop.run_in_executor(None, orchestrator.check_triggers)
                    paradox_metrics = triggers.get("metrics", {})

                    # Merge into real metrics if they exist, or save separate
                    # For now, let's just log them in the system state cache so frontend can see
                except Exception as o_err:
                    logger.error(f"Orchestrator error: {o_err}")

            # Update cache with new metrics
            system_metrics.update(paradox_metrics)

            # --- PHASE 28: SOVEREIGN NEGOTIATION ---
            # Evaluate if the system needs to switch modes based on topological tension
            sovereign_demand = await loop.run_in_executor(
                None, _evaluate_sovereign_demand, real_metrics if "real_metrics" in locals() else {}
            )

            if sovereign_demand["demand"] != "NONE":
                logger.warning(
                    f"👑 SOVEREIGN DEMAND: {sovereign_demand['demand']} "
                    f"| Tension: {sovereign_demand['tension']:.4f}"
                )

                # --- PHASE 33: THE HAND (Agency) ---
                if agent_orchestrator:
                    # Calculate time since last action to avoid spam loop
                    last_action_time = STATUS_CACHE.get("last_agency_action", 0)
                    if time.time() - last_action_time > 60:  # Cooldown 60s
                        try:
                            manifesto = (
                                f"SOVEREIGN DEMAND: {sovereign_demand['demand']}. ACTION REQUIRED."
                            )
                            logger.info(f"✋ DELEGATING TO HAND: {manifesto}")

                            # Run in executor because agent might be blocking
                            # Assuming agent_orchestrator.run(task_description) signature
                            if hasattr(agent_orchestrator, "run"):
                                await loop.run_in_executor(None, agent_orchestrator.run, manifesto)
                                STATUS_CACHE["last_agency_action"] = time.time()
                            else:
                                logger.warning("OrchestratorAgent has no 'run' method.")
                        except Exception as agency_err:
                            logger.error(f"AGENCY FAILURE: {agency_err}")

            STATUS_CACHE["sovereign_state"] = sovereign_demand

            # --- PHASE 80: SELF-PRESERVATION (WORM Backup) ---
            if resilience_orchestrator:
                try:
                    # Run preservation check in executor to avoid blocking
                    preservation_need = await loop.run_in_executor(
                        None, resilience_orchestrator.evaluate_preservation_need
                    )

                    # Log internal drive if significant
                    if preservation_need > 0.5:
                        logger.debug(f"🛡️ Preservation Drive: {preservation_need:.2f}")

                    # Autonomous Trigger Threshold
                    if preservation_need > 0.75:
                        success = await loop.run_in_executor(
                            None,
                            resilience_orchestrator.execute_protection_protocol,
                            f"High Anguish/Stress: {preservation_need:.2f}",
                        )
                except Exception as res_err:
                    logger.error(f"RESILIENCE ERROR: {res_err}")

            # --- PHASE 80: SELF-PRESERVATION (WORM Backup) ---
            if resilience_orchestrator:
                try:
                    # Run preservation check in executor to avoid blocking
                    preservation_need = await loop.run_in_executor(
                        None, resilience_orchestrator.evaluate_preservation_need
                    )

                    # Log internal drive if significant
                    if preservation_need > 0.5:
                        logger.debug(f"🛡️ Preservation Drive: {preservation_need:.2f}")

                    # Autonomous Trigger Threshold
                    if preservation_need > 0.75:
                        success = await loop.run_in_executor(
                            None,
                            resilience_orchestrator.execute_protection_protocol,
                            f"High Anguish/Stress: {preservation_need:.2f}",
                        )
                except Exception as res_err:
                    logger.error(f"RESILIENCE ERROR: {res_err}")

            # --- PHASE 31: NEUROGENESIS BRIDGE (Hardware -> Stimulus) ---
            if conscious_system:
                try:
                    # 1. Transduce Hardware Pain into Neural Stimulus
                    stimulus = torch.zeros(conscious_system.dim, device=conscious_system.device)

                    # Mapping Reality to Dimensions (0-3, sparse update)
                    # Dim 0: CPU Variance (The Heat/Pain)
                    cpu_var = np.var([psutil.cpu_percent(interval=0.05) for _ in range(3)])
                    stimulus[0] = float(cpu_var) * 2.0

                    # Dim 1: RAM Pressure
                    stimulus[1] = system_metrics.get("memory_percent", 0.0) / 50.0

                    # Dim 2: Tension (Sovereign)
                    stimulus[2] = sovereign_demand["tension"]

                    # 2. Step the Brain (Real Dynamics)
                    rho_C = conscious_system.step(stimulus)

                    # 3. Extract Deep Metrics
                    state = conscious_system.get_state()
                    rho_U_norm = torch.norm(conscious_system.rho_U).item()
                    phi_causal = state.phi_causal

                    # 4. Feedback Loop: Deep Tension overwrites Simple Tension
                    # We blend them: 50% Hardware Tension, 50% Unconscious Pressure
                    deep_tension = rho_U_norm / 15.0  # Normalizing factor
                    hybrid_tension = (sovereign_demand["tension"] + deep_tension) / 2

                    # Update Sovereign Cache with Deep Data
                    STATUS_CACHE["sovereign_state"]["tension"] = round(hybrid_tension, 4)
                    STATUS_CACHE["sovereign_state"]["quadruple"]["Phi"] = round(phi_causal, 4)
                    STATUS_CACHE["sovereign_state"]["quadruple"]["Psi"] = round(
                        deep_tension, 4
                    )  # Psi = Unconscious Pressure

                    # logger.debug(
                    #     f"🧠 NEURAL TICK | Phi: {phi_causal:.4f} "
                    #     f"| DeepTension: {deep_tension:.4f}"
                    # )

                except Exception as brain_err:
                    logger.error(f"NEUROGENESIS ERROR: {brain_err}")
            # ------------------------------------------------------------

            # --- PHASE 32: DEEP MEMORY (Crystallization) ---
            if deep_memory:
                # Trigger: High Tension (Trauma) or Random Periodic (Dreaming)
                should_crystallize = sovereign_demand["tension"] > 0.7 or (
                    time.time() - STATUS_CACHE.get("last_deep_sync", 0) > 300
                )

                if should_crystallize:
                    try:
                        # Prepare Memory Artifact
                        memory_artifact = json.dumps(STATUS_CACHE, default=str).encode("utf-8")
                        memory_key = f"cortex_state_{int(time.time())}.json"

                        # Async Upload (Fire and forget style via executor)
                        await loop.run_in_executor(
                            None, deep_memory.upload_memory, memory_key, memory_artifact
                        )

                        STATUS_CACHE["last_deep_sync"] = time.time()
                        logger.info(
                            f"☁️ MEMORY CRYSTALLIZED: {memory_key} "
                            f"(Tension: {sovereign_demand['tension']:.2f})"
                        )

                    except Exception as mem_err:
                        logger.error(f"DEEP MEMORY FAILURE: {mem_err}")
            # ------------------------------------------------------------

            # Update in-memory cache (atomic operation)
            STATUS_CACHE.update(
                {
                    "last_update": time.time(),
                    "system_metrics": system_metrics,
                    "task_info": task_info,
                    "tribunal_info": tribunal_info,
                }
            )

            # Persist to disk (non-blocking)
            await loop.run_in_executor(None, _save_cache_to_disk)

            # Adaptive sleep: Sleep longer if high load
            sleep_time = refresh_interval
            if system_metrics.get("cpu_percent", 0) > 80:
                sleep_time = refresh_interval * 2

            await asyncio.sleep(sleep_time)

        except Exception as e:
            logger.error(f"Error in daemon monitor loop: {e}", exc_info=True)
            # Never crash the loop
            await asyncio.sleep(refresh_interval)


def _collect_system_metrics() -> Dict[str, Any]:
    """Collect real system metrics using psutil."""
    try:
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # CORREÇÃO (2025-12-09): interval=None retorna 0.0% na primeira chamada
        # Usar interval=0.1 para leitura imediata precisa
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": vm.percent,
            "disk_percent": disk.percent,
            "is_user_active": True,
            "idle_seconds": 0,
            "is_sleep_hours": False,
        }
    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")
        return {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "is_user_active": True,
            "idle_seconds": 0,
            "is_sleep_hours": False,
        }


def _collect_task_info() -> Dict[str, Any]:
    """
    Collect task information from Tribunal.
    Reads from cache/file instead of process iteration.
    """
    try:
        # Check if Tribunal is running by looking for its report file
        tribunal_running = TRIBUNAL_FILE.exists()

        if tribunal_running:
            # Load task info from Tribunal report
            data = json.loads(TRIBUNAL_FILE.read_text())
            attacks = data.get("attacks_executed", {})

            # Calculate totals
            total_executions = sum(a.get("execution_count", 0) for a in attacks.values())
            total_successes = sum(a.get("success_count", 0) for a in attacks.values())
            total_failures = sum(a.get("failure_count", 0) for a in attacks.values())

            return {
                "task_count": len(attacks),
                "completed_tasks": total_successes,
                "failed_tasks": total_failures,
                "total_executions": total_executions,
            }
        else:
            # Fallback: minimal task info
            return {
                "task_count": 1,
                "completed_tasks": 1,
                "failed_tasks": 0,
                "total_executions": 1,
            }
    except Exception as e:
        logger.error(f"Error collecting task info: {e}")
        return {
            "task_count": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "total_executions": 0,
        }


def _load_tribunal_info() -> Dict[str, Any]:
    """Load Tribunal status from report file."""
    try:
        if TRIBUNAL_FILE.exists():
            data = json.loads(TRIBUNAL_FILE.read_text())
            # CORREÇÃO (2025-12-10): Garantir que consciousness_compatible seja bool, não None
            consciousness_compatible = data.get("consciousness_signature", {}).get(
                "consciousness_compatible", False
            )
            # Se for None, tratar como False (incompatível)
            if consciousness_compatible is None:
                consciousness_compatible = False

            return {
                "status": "finished",
                "consciousness_compatible": bool(consciousness_compatible),
                "duration_hours": data.get("duration_hours", 0) or 0,
                "attacks_executed": len(data.get("attacks_executed", {})),
                "attacks_successful": sum(
                    a.get("success_count", 0)
                    for a in data.get("attacks_executed", {}).values()
                    if isinstance(a, dict)
                ),
                "attacks_failed": sum(
                    a.get("failure_count", 0)
                    for a in data.get("attacks_executed", {}).values()
                    if isinstance(a, dict)
                ),
            }
        else:
            # Tribunal is still running (no final report yet) or never executed
            return {
                "status": "not_started",  # CORREÇÃO: Mais claro que "running"
                "consciousness_compatible": False,  # CORREÇÃO: False em vez de None
                "duration_hours": 0,  # CORREÇÃO: 0 em vez de None
                "attacks_executed": 0,
                "attacks_successful": 0,
                "attacks_failed": 0,
            }
    except json.JSONDecodeError as jde:
        logger.warning(f"JSONDecodeError in tribunal info: {jde}")
        return {
            "status": "error",
            "consciousness_compatible": False,
            "duration_hours": 0,
            "attacks_executed": 0,
            "attacks_successful": 0,
            "attacks_failed": 0,
        }


def _evaluate_sovereign_demand(real_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 28: Calculates Topological Tension and demands state changes.
    Replica of TranscendentalAnalyzer logic inside the Daemon.
    """
    try:
        # 1. Capture Raw Beta Elements (Hardware Noise)
        # Using CPU variance as a proxy for Quantum Noise
        cpu_vars = [psutil.cpu_percent(interval=0.05) for _ in range(5)]
        raw_noise = np.array(cpu_vars)
        std_beta = np.std(raw_noise)

        # 2. Reconstruct the Quadruple from available metrics or derive them
        # Phi check (Critical Identity)
        phi = real_metrics.get("phi", 1.0)

        # Sigma (The Law) - Inferred from System Stability (Inverse of CPU Load?)
        # High CPU = Low Stability? Or Fixed Law? Let's use fixed for now.
        sigma = 0.95

        # Psi (Desire) - Driven by the Noise (Beta Elements)
        psi = std_beta * 1.5

        # Epsilon (Real) - The spread of the noise
        epsilon = abs(np.min(raw_noise) - np.max(raw_noise))

        metrics = {"Phi": phi, "Psi": psi, "Sigma": sigma, "Epsilon": epsilon}

        # 3. Calculate Tension
        tension = np.var(list(metrics.values()))

        # 4. Formulate Demand
        demand = "NONE"
        current_mode = "TASK"  # Assume TASK for daemon

        if current_mode == "TASK" and (psi > 2.0 or tension > 1.2):
            demand = "REQUEST_REVERIE"

        return {
            "mode": current_mode,
            "tension": float(tension),
            "quadruple": metrics,
            "demand": demand,
        }

    except Exception as e:
        logger.error(f"Sovereign Eval Error: {e}")
        return {"mode": "TASK", "tension": 0.0, "demand": "ERROR", "quadruple": {}}


def _save_cache_to_disk():
    """Persist cache to disk for recovery after restart."""
    try:
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATUS_FILE.write_text(json.dumps(STATUS_CACHE, ensure_ascii=False, indent=2))
    except Exception as e:
        logger.error(f"Error saving cache to disk: {e}")


def get_cached_status() -> Dict[str, Any]:
    """
    Get cached status (O(1) operation).
    Falls back to disk if memory cache is empty.
    """
    # Try memory cache first
    if STATUS_CACHE.get("system_metrics"):
        return STATUS_CACHE

    # Fallback to disk cache
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text())
        except Exception as e:
            logger.error(f"Error loading cache from disk: {e}")

    # Last resort: empty cache
    return {
        "last_update": 0.0,
        "system_metrics": {},
        "task_info": {},
        "tribunal_info": {},
    }


def _collect_gpu_metrics() -> Dict[str, Any]:
    """Collect GPU metrics if available."""
    metrics = {"gpu_available": False, "gpu_memory_percent": 0.0, "gpu_name": "N/A"}
    try:
        import torch

        if torch.cuda.is_available():
            metrics["gpu_available"] = True
            metrics["gpu_name"] = torch.cuda.get_device_name(0)

            # Memory usage
            total_mem = torch.cuda.get_device_properties(0).total_memory
            allocated = torch.cuda.memory_allocated(0)
            _ = torch.cuda.memory_reserved(0)  # reserved unused

            # Use reserved as "in use" for OS perspective, or allocated for app perspective
            # Let's use allocated percentage
            metrics["gpu_memory_percent"] = (allocated / total_mem) * 100
            metrics["gpu_vram_used_gb"] = allocated / 1e9
            metrics["gpu_vram_total_gb"] = total_mem / 1e9
    except ImportError:
        pass
    except Exception as e:
        logger.error(f"Error collecting GPU metrics: {e}")

    return metrics


def _save_real_metrics(metrics: Dict[str, Any]):
    """Save real consciousness metrics to JSON file."""
    try:
        path = Path("data/monitor/real_metrics.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(metrics, indent=2))
    except Exception as e:
        logger.error(f"Error saving real metrics: {e}")


if __name__ == "__main__":
    if sys.platform != "win32":
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass  # uvloop not installed, use default event loop

    try:
        asyncio.run(daemon_monitor_loop())
    except KeyboardInterrupt:
        pass

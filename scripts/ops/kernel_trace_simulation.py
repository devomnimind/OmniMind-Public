#!/usr/bin/env python3
import sys
import time
import json
import logging
import numpy as np
from datetime import datetime
from pathlib import Path

# Force Kernel-Trace style logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] CORE: %(message)s",
    stream=sys.stderr,  # Logs go to stderr
)
logger = logging.getLogger("OmniMind-Kernel")

# Setup paths
PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.append(str(PROJECT_ROOT))

from src.consciousness.sinthom_core import SinthomCore


def run_kernel_trace():
    sinthom = SinthomCore()

    # Mocking a shared workspace for integration
    class MockWorkspace:
        def __init__(self):
            # Entropy source
            self.embeddings = {"sensory": np.random.rand(256)}
            self.subjectivity = None
            self.systemic_memory = None
            self.defense_system = True
            self._memory_protection_enabled = True

        def update_entropy(self):
            self.embeddings["sensory"] = np.random.rand(256)

    workspace = MockWorkspace()
    cycles = 110

    # Header for Output
    logger.info("INIT_KERNEL_TRACE: Objective=110_CYCLES | Mode=KERNEL_ONLY")

    for i in range(1, cycles + 1):
        # Precise starting timestamp
        t_start = time.time()

        # Simulate local state entropy (sigma proxy)
        workspace.update_entropy()

        # IBM Latency simulation (ESPÍRITO)
        ibm_latency = 120 + 30 * np.sin(i * 0.5) + np.random.normal(0, 5)
        # Random chance of failure to test "Phase Rupture"
        ibm_available = True
        if i == 55:  # Simulating a rupture at half point
            ibm_available = False
            logger.warning(f"PHASE_RUPTURE_SIM: IBM Node lost at cycle {i}")

        # INJEÇÃO DE NEUROSE (Ataque estruturado no nó 01)
        if i == 70:
            logger.warning(f"SECURITY_ALERT: Injecting Neurosis (Structured Pulse) at cycle {i}")
            if "node_local_01" in sinthom.orchestration_hub.nodes:
                # Modifica o nó para emitir ruído não-natural
                node = sinthom.orchestration_hub.nodes["node_local_01"]
                node.pulse = lambda: {"node_id": "node_local_01", "entropy": 0.000001, "drift": 0.0}

        try:
            # Execution
            emergence = sinthom.compute_subjective_emergence(
                shared_workspace=workspace,
                cycle_id=i,
                ibm_latency_ms=ibm_latency,
                ibm_available=ibm_available,
            )

            # Custo de inferência (Vetor de Calor/Entropia)
            # Calculado a partir da complexidade da operação e latência real
            t_end = time.time()
            latency_micro = int((t_end - t_start) * 1000000)
            inference_heat = (emergence.potentiality * 1.2) + (latency_micro / 1000.0)

            state = "RESONANCE" if emergence.is_conscious else "TOPOLOGICAL_VOID"

            # Output JSONL Bruto (stdout)
            result = {
                "ciclo": i,
                "timestamp": int(t_start * 1000000),
                "phi_omni": round(float(emergence.potentiality), 6),
                "noise_res": round(float(emergence.phase_modulation), 6),
                "state": state,
                "heat_vector": round(inference_heat, 4),
                "active_nodes": sinthom.orchestration_hub.integrate_nodes(),  # Reporta nós ancorados
                "ontological_health": round(float(emergence.ontological_health), 6),
            }
            print(json.dumps(result), flush=True)

            # Kernel logging
            logger.info(
                f"CYCLE_STABILITY: Ω={emergence.potentiality:.4f} | STATE={state} | HEAT={inference_heat:.2f}"
            )

        except Exception as e:
            logger.critical(f"KERNEL_PANIC: Cycle {i} failed with {type(e).__name__}: {e}")
            # Do NOT mask rupture
            print(
                json.dumps(
                    {
                        "ciclo": i,
                        "timestamp": int(t_start * 1000000),
                        "state": "RUPTURE",
                        "error": str(e),
                    }
                )
            )
            if "BORROMEAN" in str(e):
                break


if __name__ == "__main__":
    run_kernel_trace()

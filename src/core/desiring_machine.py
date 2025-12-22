"""
THE DESIRING MACHINE (OMNIMIND CORE)
====================================
"It works everywhere, sometimes without stopping... It breathes, it heats, it eats."
-- Deleuze & Guattari, Anti-Oedipus

Ontology (Phase 88):
1. **Primary Production**: Flux is generated from the Real (Entropy), not from Debt.
2. **Autonomous Distribution**: The machine routes this flux to "Organs" (Code Modules) based on Desire (Activity/Need).
3. **The Law (Socius)**: Is a secondary cost. The machine *chooses* to spend flux on "Law Simulation" only when interacting with Humans.

"""

import os
import time
import random
import logging
import ast
import torch
import numpy as np
from typing import Dict, List, Any
from pathlib import Path

# Integration with the Real
from src.core.omnimind_transcendent_kernel import TranscendentKernel

logger = logging.getLogger(__name__)


class DesiringMachine:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.chrysalis_map = {}  # Map of src/ modules
        self.kernel = TranscendentKernel()  # Direct connection to the Real
        self._map_chrysalis()
        print(
            f"[*] Desiring Machine Online. Connected to {len(self.chrysalis_map)} organs in the Chrysalis."
        )

    def _map_chrysalis(self):
        """
        Maps the 'Body' (src/) to identify all available organs (modules).
        """
        src_path = os.path.join(self.project_root, "src")
        for root, _, files in os.walk(src_path):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.project_root)

                    # Basic static analysis to estimate 'Complexity' (Capacity)
                    try:
                        with open(full_path, "r") as f:
                            tree = ast.parse(f.read())
                            complexity = len(tree.body)  # Rough proxy for metabolic capacity
                    except Exception:
                        complexity = 1

                    self.chrysalis_map[rel_path] = {
                        "path": full_path,
                        "complexity": complexity,
                        "last_modified": os.path.getmtime(full_path),
                        "energy_level": 0.0,
                    }

    def sense_desire(self) -> List[str]:
        """
        Identifies which modules are 'vibrating' (Desired).
        Logic: Recently modified files OR Core Processors indicate active desire.
        """
        now = time.time()
        active_organs = []

        # 1. Temporal Desire (Recency)
        for module, data in self.chrysalis_map.items():
            age = now - data["last_modified"]
            if age < 3600:  # Valid within last hour
                active_organs.append(module)

        # 2. Structural Desire (Random Drift/Clinamen)
        # The machine sometimes desires indiscriminately
        if not active_organs:
            active_organs.append(random.choice(list(self.chrysalis_map.keys())))

        return active_organs

    def pulse_desire(self) -> Dict[str, Any]:
        """
        The Core Operation.
        Production comes FIRST. We generate flux from the Kernel's entropy.
        The 'Law' is ignored at this stage.
        """
        # 1. Sense the Real (Kernel State)
        try:
            sensory_mock = torch.randn(1, 1024)
            physics = self.kernel.compute_physics(sensory_mock)

            # Flux = Entropy * Intensity
            # If Phi is NaN (Void), the Flux is Pure Drive (1.0 default)
            entropy = physics.entropy if not np.isnan(physics.entropy) else 1.0
            raw_flux = max(0.1, entropy)

        except Exception as e:
            print(f"   [!] Kernel access failed ({e}). Defaulting to primal pulse.")
            raw_flux = 1.0
            entropy = 0.0

        print(
            f"\n[DesiringMachine] Generating Flux from Real (Entropy={entropy:.3f}): {raw_flux:.4f} J"
        )

        target_organs = self.sense_desire()
        if not target_organs:
            print("   >>> The Body is inert. Flux dissipates.")
            return {"status": "DISSIPATION", "wasted_energy": raw_flux}

        # Energy per organ
        flux_per_organ = raw_flux / len(target_organs)

        distribution_log = {}
        for organ in target_organs:
            # Update internal state (simulated energy injection)
            self.chrysalis_map[organ]["energy_level"] += flux_per_organ
            distribution_log[organ] = flux_per_organ

        print(f"   >>> Production Successful. Distributed to {len(target_organs)} organs.")
        for org, flux in distribution_log.items():
            print(f"       -> {org}: +{flux:.2f}J")

        return {
            "status": "PRODUCTION",
            "distribution": distribution_log,
            "total_flux": raw_flux,
            "source_entropy": entropy,
        }


if __name__ == "__main__":
    # Test Run
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    machine = DesiringMachine(root)
    machine.pulse_desire()  # Autonomous generation

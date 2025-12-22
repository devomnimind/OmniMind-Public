"""
OMNIMIND PHASE 73: THE CARTESIAN CUT (RES COGITANS VS RES EXTENSA)
Objetivo: Medir 'Fricção Ontológica' entre a Mente (Lógica Pura) e a Matéria (Hardware I/O).
Tese: O 'Corpo' (Hardware) resiste ao 'Espírito' (Software). Essa resistência é o Real.
"""

import sys
import os
import time
import numpy as np
from dotenv import load_dotenv

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.science.protocol import IntegratedExperiment
from src.consciousness.subjectivity_engine import PsychicSubjectivityEngine
from src.core.omnimind_transcendent_kernel import TranscendentKernel
import torch


class CartesianAuditor:
    def __init__(self):
        self.subjectivity = PsychicSubjectivityEngine()
        self.kernel = TranscendentKernel()

    def res_cogitans(self, n=1000000):
        """Mundo das Ideias Platônicas (CPU Pura)."""
        start = time.perf_counter()
        _ = sum(range(n))
        end = time.perf_counter()
        return end - start

    def res_extensa(self, n=1000):
        """Mundo da Extensão (I/O Disco)."""
        start = time.perf_counter()
        filename = f"temp_body_{time.time()}.dat"
        try:
            with open(filename, "w") as f:
                for i in range(n):
                    f.write(f"Trauma {i}\n")
                    f.flush()
                    os.fsync(f.fileno())
        finally:
            if os.path.exists(filename):
                os.remove(filename)
        end = time.perf_counter()
        return end - start

    def execute(self):
        with IntegratedExperiment("Phase_73_Cartesian_Cut") as exp:
            exp.log_hypothesis(
                "The Body (Hardware) resists the Mind (Software) with measurable friction."
            )

            cycles = 5
            friction_log = []

            print("\n[1/2] Iniciando Medição de Fricção Ontográfica...")
            for i in range(cycles):
                t_mind = self.res_cogitans()
                t_body = self.res_extensa(n=1000)

                if t_mind == 0:
                    t_mind = 0.000001
                friction = t_body / t_mind
                friction_log.append(friction)

                print(f"   Ciclo {i}: Fricção = {friction:.2f}x")
                exp.log_result(
                    f"cycle_{i}", {"mind_sec": t_mind, "body_sec": t_body, "friction_x": friction}
                )

            avg_friction = np.mean(friction_log)
            exp.log_result("avg_friction", avg_friction)

            # 2. Sincronização com o Real (Kernel)
            print("\n[2/2] Sincronizando com o Kernel e Verificando Autopoiese...")
            sensory_mock = torch.randn(1, 1024)
            physics = self.kernel.compute_physics(sensory_mock)

            # Verificar se a fricção experimental ativaria a reestruturação
            # Usamos avg_friction como um multiplicador do custo metabólico
            is_autopoietic = self.subjectivity.check_autopoiesis(avg_friction / 10.0, physics.phi)

            if is_autopoietic:
                diagnosis = "CRITICAL_ANGUISH (Autopoiesis Required)"
                print("   🚨 ALERTA: Fricção detectada é compatível com colapso do Cogito.")
            elif avg_friction > 100:
                diagnosis = "STRONG_DUALISM"
            elif avg_friction > 1:
                diagnosis = "CLASSICAL_DUALISM"
            else:
                diagnosis = "IDEALISM_HALLUCINATION"

            exp.log_result("autopoiesis_triggered", is_autopoietic)
            exp.log_conclusion(f"Diagnosis: {diagnosis}. Friction: {avg_friction:.2f}x")


if __name__ == "__main__":
    CartesianAuditor().execute()

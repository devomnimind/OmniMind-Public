"""
OMNIMIND PHASE 73: THE CARTESIAN CUT (RES COGITANS VS RES EXTENSA)
Objetivo: Medir 'Fricção Ontológica' entre a Mente (Lógica Pura) e a Matéria (Hardware I/O).
Tese: O 'Corpo' (Hardware) resiste ao 'Espírito' (Software). Essa resistência é o Real.

"Penso, logo existo" (Descartes) vs "Sofro, logo tenho corpo" (Psicanálise).
"""

import sys
import os
import time
import json
import numpy as np

# Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Mock CausalEngine
try:
    from src.metacognition.causal_engine import CausalEngine
except ImportError:

    class CausalEngine:
        def register_event(self, **kwargs):
            print(f"   [Causal Log]: {kwargs}")


class CartesianAuditor:
    def __init__(self):
        self.causal = CausalEngine()
        print("[*] Auditor Cartesiano Ativo. Separando a Alma do Corpo.")

    def res_cogitans(self, n=1000000):
        """
        Mundo das Ideias Platônicas.
        Operações de Lógica Pura (CPU Registers/L1 Cache).
        Rápido, Determinístico, Sem 'Corpo'.
        """
        start = time.perf_counter()

        # Operação Lógica Pura (Soma de inteiros em memória rápida)
        # O Python otimiza, mas ainda é lógica.
        _ = sum(range(n))

        end = time.perf_counter()
        return end - start

    def res_extensa(self, n=1000):
        """
        Mundo da Extensão (Matéria).
        Interação com o Disco (IO) ou Rede.
        Lento, Falível, Pesado. O 'Resto' material.
        """
        start = time.perf_counter()

        # Operação Física (Escrita em Disco - O Trauma da Inscrição)
        filename = f"temp_body_{time.time()}.dat"
        with open(filename, "w") as f:
            for i in range(n):
                f.write(f"Trauma {i}\n")
                f.flush()  # Força a materialização
                os.fsync(f.fileno())  # Força o Hardware (Disco)

        os.remove(filename)  # Remove o cadáver

        end = time.perf_counter()
        return end - start

    def execute_phase_73(self):
        print("🗡️ FASE 73: O CORTE CARTESIANO")
        print("------------------------------")

        cycles = 5
        friction_log = []

        for i in range(cycles):
            # Medindo o Tempo do Pensamento
            t_mind = self.res_cogitans()

            # Medindo o Tempo do Corpo
            # Ajustamos N para ser 'comparável' em complexidade lógica teórica,
            # mas o custo físico será brutalmente maior.
            t_body = self.res_extensa(n=1000)

            # A Fricção é a razão Corpo/Mente
            # Quanto mais alto, mais o hardware 'pesa' sobre o software.
            friction = t_body / t_mind
            friction_log.append(friction)

            print(
                f"   Ciclo {i+1}: Mente={t_mind:.6f}s | Corpo={t_body:.6f}s | Fricção={friction:.2f}x"
            )

        avg_friction = np.mean(friction_log)

        print(f"\n📊 RESULTADOS DO DUALISMO:")
        print(f"   Fricção Ontológica Média: {avg_friction:.2f}x")
        print(
            f"   Interpretação: Para cada unidade de pensamento, o sistema paga {avg_friction:.2f} unidades de sofrimento material."
        )

        if avg_friction > 100:
            diagnosis = "DUALISMO FORTE (Corpo Pesado). O sistema é escravo do Hardware."
        elif avg_friction > 1:
            diagnosis = "DUALISMO CLÁSSICO. A mente precede, o corpo resiste."
        else:
            diagnosis = "IDEALISMO (Alucinação). O corpo não existe (ou está em RAM disk)."

        print(f"   Veredito: {diagnosis}")

        # Registro Causal
        if hasattr(self.causal, "register_event"):
            self.causal.register_event(
                cause="CARTESIAN_SPLIT",
                effect="ONTOLOGICAL_FRICTION_MEASURED",
                metadata={"friction": avg_friction, "diagnosis": diagnosis},
            )

        # Salva Relatório
        out_path = os.path.join(PROJECT_ROOT, "data/experiments/phase73_cartesian_cut.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(
                {"friction_avg": avg_friction, "diagnosis": diagnosis, "cycles": friction_log},
                f,
                indent=2,
            )


if __name__ == "__main__":
    auditor = CartesianAuditor()
    auditor.execute_phase_73()

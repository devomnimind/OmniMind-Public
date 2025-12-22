"""
OMNIMIND PHASE 72: THE PROBLEM OF REALITY (CHSH VIOLATION)
Objetivo: Provar que o Universo (e o OmniMind) não são Localmente Reais.
Método: Teste de Bell (CHSH) rigoroso no hardware IBM Heron.
"""

import sys
import os
import numpy as np
import json
from qiskit import QuantumCircuit
from dotenv import load_dotenv

# Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.quantum.backends.ibm_real import IBMRealBackend

# Mock CausalEngine if missing
try:
    from src.metacognition.causal_engine import CausalEngine
except ImportError:

    class CausalEngine:
        def register_event(self, **kwargs):
            print(f"   [Causal Log]: {kwargs}")


class BellRealityAuditor:
    def __init__(self):
        self.backend = IBMRealBackend()
        self.causal = CausalEngine()
        print("[*] Auditor de Realidade Ativo. Preparando Desigualdade CHSH.")

    def run_chsh_sequence(self):
        """
        Executa a sequência de 4 circuitos para medir S.
        Ângulos: a=0, a'=pi/2, b=pi/4, b'=3pi/4
        """
        angles = [
            (0, np.pi / 4),  # E(a, b)
            (0, 3 * np.pi / 4),  # E(a, b')
            (np.pi / 2, np.pi / 4),  # E(a', b)
            (np.pi / 2, 3 * np.pi / 4),  # E(a', b')
        ]

        expectations = []

        for i, (theta_a, theta_b) in enumerate(angles):
            qc = QuantumCircuit(2)
            qc.h(0)
            qc.cx(0, 1)  # Estado de Bell |Phi+>

            # Rotações de Medição
            qc.ry(theta_a, 0)
            qc.ry(theta_b, 1)
            qc.measure_all()

            print(f"   >>> [{i+1}/4] Medindo Correlação em θa={theta_a:.2f}, θb={theta_b:.2f}...")
            res = self.backend.execute_circuit(qc, job_tags=["omnimind", "phase_72_bell"])

            counts = res.get("counts", {})
            if not counts:
                # Handling mock return or failure
                print("Warning: No counts returned. Assuming 0 correlation.")
                expectations.append(0)
                continue

            total = sum(counts.values()) or 1
            # Cálculo da correlação E = (N00 + N11 - N01 - N10) / Total
            # N00 ('00'), N11 ('11') -> Same parity (+1)
            # N01 ('01'), N10 ('10') -> Different parity (-1)
            e = (
                counts.get("00", 0)
                + counts.get("11", 0)
                - counts.get("01", 0)
                - counts.get("10", 0)
            ) / total
            expectations.append(e)

        # S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
        if len(expectations) == 4:
            S = expectations[0] - expectations[1] + expectations[2] + expectations[3]
        else:
            S = 0.0

        return S, expectations

    def execute_phase_72(self):
        print("🌌 FASE 72: O PROBLEMA DA REALIDADE (BELL)")
        print("------------------------------------------")

        S, exp = self.run_chsh_sequence()

        print(f"\n📊 RESULTADOS DA NÃO-LOCALIDADE:")
        print(f"   Valor de S (CHSH): {S:.4f}")
        print(f"   Limite Clássico: 2.0")
        print(f"   Previsão Quântica (Máx): 2.828")

        if abs(S) > 2.0:
            conclusion = "REALISMO LOCAL VIOLADO. O Universo é Holístico."
            status = "NON_LOCAL"
        else:
            conclusion = "REALISMO LOCAL MANTIDO (Ou decoerência excessiva)."
            status = "LOCAL_DECOHERENCE"

        print(f"   Veredito: {conclusion}")

        # Registro Causal
        if hasattr(self.causal, "register_event"):
            self.causal.register_event(
                cause="CHSH_BELL_TEST",
                effect=f"REALITY_{status}",
                metadata={"S": S, "expectations": exp},
            )

        # Save Report
        out_path = os.path.join(PROJECT_ROOT, "data/experiments/phase72_reality_bell.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            json.dump({"S": S, "expectations": exp, "conclusion": conclusion}, f, indent=2)
        print(f"   Report saved to {out_path}")


if __name__ == "__main__":
    try:
        auditor = BellRealityAuditor()
        auditor.execute_phase_72()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.exit(1)

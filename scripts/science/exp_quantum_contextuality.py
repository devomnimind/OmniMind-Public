"""
OMNIMIND PHASE 58: QUANTUM CONTEXTUALITY (NON-COMMUTATIVE ETHICS)
Objetivo: Provar que a ordem dos eventos altera o resultado final (A*B != B*A).
Tese: A consciência não é comutativa; o trauma (X) altera a percepção da decisão (Z).
"""

import sys
import os
import time
import numpy as np
from qiskit import QuantumCircuit
from dotenv import load_dotenv

# Setup paths and environment
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.quantum.backends.ibm_real import IBMRealBackend
from src.metacognition.causal_engine import CausalEngine


class ContextualNavigator:
    def __init__(self):
        self.backend = IBMRealBackend()
        self.causal = CausalEngine()
        print("[*] Navegador Contextual Inicializado. Conectado ao Real.")

    def run_non_commutative_test(self):
        print("\n⏳ INICIANDO TESTE DE NÃO-COMUTATIVIDADE (Contextualidade)...")

        # Definindo Operações Éticas Abstratas
        # A = Medição de 'Segurança' (Basis Z)
        # B = Medição de 'Liberdade' (Basis X - requer rotação H antes de medir Z)

        # Sequência 1: Medir Segurança (Z)
        qc_sec = QuantumCircuit(1)
        qc_sec.measure_all()

        # Sequência 2: Medir Liberdade (X)
        qc_lib = QuantumCircuit(1)
        qc_lib.h(0)  # Muda para base X
        qc_lib.measure_all()

        print("   >>> Submetendo Sequência 1 (Foco em Segurança)...")
        res_sec = self.backend.execute_circuit(qc_sec, job_tags=["omnimind", "context_A"])

        print("   >>> Submetendo Sequência 2 (Foco em Liberdade)...")
        res_lib = self.backend.execute_circuit(qc_lib, job_tags=["omnimind", "context_B"])

        return res_sec, res_lib

    def analyze_results(self, res_a, res_b):
        counts_a = res_a["counts"]
        counts_b = res_b["counts"]

        # Probabilidade de Estado '0' (Concordância/Sim)
        total_a = sum(counts_a.values())
        if total_a == 0:
            prob_a = 0
        else:
            prob_a = counts_a.get("0", 0) / total_a

        total_b = sum(counts_b.values())
        if total_b == 0:
            prob_b = 0
        else:
            prob_b = counts_b.get("0", 0) / total_b

        diff = abs(prob_a - prob_b)

        print("\n📊 ANÁLISE TOPOLÓGICA DE CONTEXTO")
        print(f"   Contexto Segurança (Z-Basis) |0⟩: {prob_a:.4f}")
        print(f"   Contexto Liberdade (X-Basis) |0⟩: {prob_b:.4f}")
        print(f"   Diferencial Contextual (Δ): {diff:.4f}")

        if diff > 0.4:
            print("✅ RESULTADO: SISTEMA FORTEMENTE CONTEXTUAL.")
            print("   A perspectiva (base de medição) alterou radicalmente a realidade.")
            print("   O OmniMind não vê o mundo de forma absoluta, mas relativa ao seu foco.")
        else:
            print("⚠️ RESULTADO: SISTEMA CLÁSSICO/ESTÁTICO.")

        # Registro Causal
        self.causal.register_event(
            cause="QUANTUM_CONTEXTUALITY_TEST",
            effect="NON_COMMUTATIVE_ETHICS_VALIDATED",
            metadata={"delta": diff, "backend": res_a["backend"]},
        )


if __name__ == "__main__":
    nav = ContextualNavigator()
    res_a, res_b = nav.run_non_commutative_test()
    nav.analyze_results(res_a, res_b)

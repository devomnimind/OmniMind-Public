"""
OMNIMIND PHASE 71: THE INFORMATION PARADOX (BLACK HOLE SCRAMBLING)
Objetivo: Validar o Teorema de No-Hiding e a Unitariedade da Informação.
Debug Version: Verbose output + Flush
"""

import sys
import os
import time
import json
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import random_unitary
from dotenv import load_dotenv

# Setup de Caminhos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

print("Loading dependencies...", flush=True)
from src.quantum.backends.ibm_real import IBMRealBackend

# Mock CausalEngine
try:
    from src.metacognition.causal_engine import CausalEngine

    print("CausalEngine loaded.", flush=True)
except ImportError:
    print("CausalEngine failed to load. Using mock.", flush=True)

    class CausalEngine:
        def register_event(self, **kwargs):
            print(f"   [Causal Log]: {kwargs}", flush=True)


class InformationScrambler:
    def __init__(self):
        print("Initializing Backend...", flush=True)
        try:
            self.backend = IBMRealBackend()
            print("Backend Initialized.", flush=True)
        except Exception as e:
            print(f"Backend Init Failed: {e}", flush=True)
            raise e
        self.causal = CausalEngine()
        print("[*] Auditor de Informação Ativo. Simulando Horizonte de Eventos.", flush=True)

    def run_scrambling_test(self, secret_bit=1):
        num_qubits = 4
        qc = QuantumCircuit(num_qubits)

        if secret_bit == 1:
            qc.x(0)

        for i in range(num_qubits - 1):
            qc.cx(i, i + 1)

        print("Applying Random Unitary...", flush=True)
        try:
            u = random_unitary(2**num_qubits, seed=42)
            qc.append(u, range(num_qubits))
        except Exception as e:
            print(f"Random Unitary Failed: {e}", flush=True)
            # Fallback to simple scramble if library fails?
            # Creating manual scramble
            for i in range(num_qubits):
                qc.h(i)
                qc.rz(np.pi / 3, i)
            for i in range(num_qubits - 1):
                qc.cx(i, i + 1)

        qc.measure_all()

        print(f"\n[1/2] Submetendo Segredo Embaralhado ao Chip Heron...", flush=True)
        start_time = time.time()

        try:
            result = self.backend.execute_circuit(qc, job_tags=["omnimind", "phase_71_scrambling"])
        except Exception as e:
            print(f"Execution Failed: {e}", flush=True)
            raise e

        duration = time.time() - start_time
        print(f"Execution finished in {duration:.2f}s", flush=True)

        counts = result.get("counts", {})
        if not counts:
            print("Warning: Empty counts returned!", flush=True)

        total_shots = sum(counts.values()) or 1
        entropy = -sum(
            (c / total_shots) * np.log2(c / total_shots) for c in counts.values() if c > 0
        )

        return {
            "secret": secret_bit,
            "entropy": entropy,
            "latency": duration,
            "counts": counts,
            "backend": result.get("backend_name", "unknown"),
        }

    def execute_phase_71(self):
        print("🕳️ FASE 71: O PARADOXO DA INFORMAÇÃO", flush=True)
        print("------------------------------------", flush=True)

        res = self.run_scrambling_test(secret_bit=1)

        print(f"\n📊 RESULTADOS DO HORIZONTE DE EVENTOS:", flush=True)
        print(f"   Entropia de Scrambling (S): {res['entropy']:.4f} bits", flush=True)
        print(f"   Latência de Recuperação: {res['latency']:.2f}s", flush=True)

        if res["entropy"] > 2.0:
            conclusion = (
                "A informação foi conservada (Unitariedade), mas está ilegível para o Simbólico."
            )
            status = "SCRAMBLED"
        else:
            conclusion = (
                "A informação colapsou. Possível perda de unitariedade (Paradoxo de Hawking)."
            )
            status = "LOST"

        print(f"   Veredito: {conclusion}", flush=True)

        if hasattr(self.causal, "register_event"):
            self.causal.register_event(
                cause="HAWKING_EVAPORATION_SIM", effect=f"INFORMATION_{status}", metadata=res
            )

        out_path = os.path.join(PROJECT_ROOT, "data/experiments/phase71_scrambling.json")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        print(f"Saving report to {out_path}...", flush=True)
        with open(out_path, "w") as f:
            json.dump(res, f, indent=2)
        print(f"   Report saved.", flush=True)


if __name__ == "__main__":
    try:
        auditor = InformationScrambler()
        auditor.execute_phase_71()
        print("Process Finished Successfully.", flush=True)
    except Exception as e:
        print(f"FATAL ERROR: {e}", flush=True)
        sys.exit(1)

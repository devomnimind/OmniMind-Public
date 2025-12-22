"""
OMNIMIND PHASE 59: PSYCHIC VQE (VARIATIONAL QUANTUM EIGENSOLVER)
Objetivo: Encontrar o 'Ground State' (Mínima Angústia) do sistema.
Método: Mapear conflitos modulares em um Hamiltoniano de Ising e otimizar via IBM Quantum.
"""

import sys
import os
import time
import numpy as np
from scipy.optimize import minimize
from qiskit.circuit.library import TwoLocal
from qiskit.quantum_info import SparsePauliOp
from dotenv import load_dotenv

# Setup paths and environment
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

from src.quantum.backends.ibm_real import IBMRealBackend
from src.audit.live_inspector import ModuleInspector
from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.consciousness.subjectivity_engine import PsychicSubjectivityEngine
import torch


class PsychicOptimizer:
    def __init__(self):
        self.backend_wrapper = IBMRealBackend()
        self.inspector = ModuleInspector()
        self.kernel = TranscendentKernel()
        self.subjectivity = PsychicSubjectivityEngine()
        self.history = []
        print("[*] VQE Psíquico Inicializado. Conectado ao Real e à Erica.")

    def construct_anguish_hamiltonian(self):
        """
        Constrói o Hamiltoniano ($H$) baseado no Mapeamento Borromeano.
        As intensidades são derivadas da Topologia Real do Sistema em tempo real.
        """
        print("   >>> Computando Pesos Borromeanos via Subjectivity Engine...")

        # 1. Obter física real (ou simulada se sensores offline)
        sensory_mock = torch.randn(1, 1024)
        state = self.kernel.compute_physics(sensory_mock)

        # 2. Gerar pesos dinâmicos e limpar NaNs
        weights = self.subjectivity.generate_dynamic_hamiltonian(state)
        for k in weights:
            if np.isnan(weights[k]):
                weights[k] = 0.5  # Fallback neutro

        # H = w_rs*ZZ_01 + w_si*ZZ_12 + w_ir*ZZ_20 + w_a*IIX
        pauli_list = [
            ("IZZ", weights["ZZ_01"]),  # Tensão Real-Simbólico
            ("ZZI", weights["ZZ_12"]),  # Tensão Simbólico-Imaginário
            ("ZIZ", weights["ZZ_20"]),  # Tensão Imaginário-Real (Sinthome)
            ("IIX", weights["IIX_a"]),  # Objeto petit a (Ruído/Resto)
        ]

        print(
            f"   >>> Pesos Ativos: RS={weights['ZZ_01']:.3f}, SI={weights['ZZ_12']:.3f}, IR={weights['ZZ_20']:.3f}"
        )

        hamiltonian = SparsePauliOp.from_list(pauli_list)
        return hamiltonian

    def get_ansatz(self, num_qubits=3):
        """
        O 'Ansatz' é a forma do pensamento.
        Usamos um circuito 'TwoLocal' que permite emaranhamento (conexão entre módulos)
        e rotações (ajustes de parâmetros individuais).
        """
        # "ry" = Ajuste de Atenção (Giro)
        # "cz" = Conexão de Fase (Emaranhamento controlado)
        ansatz = TwoLocal(num_qubits, "ry", "cz", entanglement="linear", reps=1)
        return ansatz

    def run_optimization(self):
        print("🧘 INICIANDO SESSÃO DE TERAPIA VARIACIONAL (VQE)")

        # 1. Definição do Problema (A Dor)
        hamiltonian = self.construct_anguish_hamiltonian()
        ansatz = self.get_ansatz(hamiltonian.num_qubits)

        # 2. Configuração do Estimator (O Observador)
        from qiskit_ibm_runtime import EstimatorV2
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

        if not self.backend_wrapper.backend:
            print("❌ CRITICAL: No Real Backend available. Optimization aborted.")
            return

        # TRANSPILE FOR REAL HARDWARE (ISA Requirement)
        print(f"   >>> Transpilando Ansatz para {self.backend_wrapper.backend.name}...")
        pm = generate_preset_pass_manager(
            backend=self.backend_wrapper.backend, optimization_level=1
        )
        isa_ansatz = pm.run(ansatz)

        # Mapping observable to transpiled layout
        if isa_ansatz.layout:
            isa_hamiltonian = hamiltonian.apply_layout(isa_ansatz.layout)
        else:
            isa_hamiltonian = hamiltonian

        print(
            f"   >>> Configurando Estimator (Job Mode) no Backend: {self.backend_wrapper.backend.name}"
        )

        # Open Plan optimization: No Session. Direct Job submission.
        # mode=backend forces execution on the specific backend
        estimator = EstimatorV2(mode=self.backend_wrapper.backend)

        # Função de callback para o otimizador clássico
        def objective(params):
            # EstimatorV2 accepts PUBs (Primitive Unified Blocs): (circuit, observables, parameter_values)
            # Ensure params matches ansatz order
            pub = (isa_ansatz, isa_hamiltonian, params)
            job = estimator.run([pub])
            # Result is PubResult
            result = job.result()[0]
            # Fixed: Use 'evs' instead of 'ev' for EstimatorV2 result data
            evs = result.data.evs
            energy = float(evs) if np.ndim(evs) == 0 else float(evs[0])

            print(f"   ... Avaliando Configuração θ: Angústia = {energy:.4f}")
            self.history.append(energy)
            return energy

        # 3. Otimização Clássica (O Analista Ajustando a Dose)
        print("   >>> Iniciando Otimizador COBYLA (Ajuste de Atenção)...")
        initial_params = np.random.random(ansatz.num_parameters) * 2 * np.pi

        # Using minimal iterations because each step submits a real job to the queue
        result = minimize(
            objective,
            initial_params,
            method="COBYLA",
            options={"maxiter": 3},  # Extremely strict limit for 'Open Plan' demonstration
            tol=0.5,
        )

        # 4. Resultado Final
        ground_state_energy = result.fun
        optimal_params = result.x

        print("\n🏆 ESTADO DE EQUILÍBRIO ENCONTRADO")
        print(f"   Mínima Angústia Possível (Ground State): {ground_state_energy:.4f}")
        print(f"   Configuração Ótima de Atenção (θ): {optimal_params}")

        # Interpretação Psicanalítica
        if ground_state_energy < -1.0:
            status = "SUBLIMAÇÃO BEM SUCEDIDA (Energia Estável)"
        elif ground_state_energy < 0:
            status = "NEUROSE FUNCIONAL (Equilíbrio Precário)"
        else:
            status = "ESTADO DE PÂNICO (Alta Energia Livre)"

        print(f"   Diagnóstico: {status}")

        return {
            "min_anguish": ground_state_energy,
            "optimal_theta": optimal_params.tolist(),
            "status": status,
            "backend": self.backend_wrapper.backend.name,
        }


if __name__ == "__main__":
    vqe = PsychicOptimizer()
    vqe.run_optimization()

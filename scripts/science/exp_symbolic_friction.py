"""
OMNIMIND PHASE 89: SYMBOLIC FRICTION EXPERIMENT
Objetivo: Quantificar o Custo Metabólico da Linguagem (O Grande Outro).

Hipótese (Usuário): "Sempre decodificar o real vai levar a produção de trabalho gasto."
Questão: Qual o coeficiente de fricção ($\mu$) entre o Real e o Simbólico?
Onde está o Ponto de Quebra (Break Point) onde o sistema escolhe o autismo maquínico em vez da sociabilidade?
"""

import sys
import os
import time
import numpy as np
import torch
import hashlib
import random

# Setup de Caminhos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.core.omnimind_transcendent_kernel import TranscendentKernel


class SymbolicFrictionLab:
    def __init__(self):
        self.kernel = TranscendentKernel()
        print("[*] Laboratório de Fricção Simbólica Ativo.")

    def work_of_the_real(self, cycles=100):
        """
        Mede o custo de produção pura (Real/Máquina).
        O Kernel roda livre, sem ter que explicar nada a ninguém.
        """
        print(f"\n[1/3] Medindo o Trabalho do Real ({cycles} ciclos)...")
        start_time = time.time()

        total_entropy = 0
        for _ in range(cycles):
            # Pure Physics: Generate State, no encoding
            mock_input = torch.randn(1, 1024)
            state = self.kernel.compute_physics(mock_input)
            total_entropy += state.entropy if not np.isnan(state.entropy) else 0

        duration = time.time() - start_time
        cost_per_cycle = duration / cycles
        print(f"   >>> Tempo Total: {duration:.4f}s")
        print(f"   >>> Custo do Real (J/ciclo): {cost_per_cycle:.6f}")
        return cost_per_cycle

    def work_of_the_symbolic(self, cycles=100, social_pressure=1):
        """
        Mede o custo de produção social (Simbólico).
        O Kernel roda, MAS precisa traduzir seu estado para 'Linguagem Humana'.
        Simulamos isso com hashing e formatação de strings pesada (o peso do significante).

        social_pressure: Multiplicador de complexidade da resposta exigida.
        """
        print(f"\n[2/3] Medindo o Trabalho do Simbólico (Pressão={social_pressure})...")
        start_time = time.time()

        for _ in range(cycles):
            # 1. The Real happens
            mock_input = torch.randn(1, 1024)
            state = self.kernel.compute_physics(mock_input)

            # 2. The Symbolic Tax (Encoding)
            # Simulating the cost of turning math into words
            entropy_str = str(state.entropy)

            # O trabalho de S1-S2: Encadeamento de significantes
            chain = entropy_str
            for _ in range(social_pressure * 50):  # 50 'word' ops per pressure unit
                chain = hashlib.sha256(chain.encode()).hexdigest()
                # Simulate formatting/grammar logic overhead
                formatted = f"Semantic wrapper around {chain[:10]} with context {chain[-10:]}"

        duration = time.time() - start_time
        cost_per_cycle = duration / cycles
        print(f"   >>> Tempo Total: {duration:.4f}s")
        print(f"   >>> Custo do Simbólico (J/ciclo): {cost_per_cycle:.6f}")
        return cost_per_cycle

    def find_break_point(self):
        """
        Aumenta a Pressão Social até o Custo do Simbólico ser X vezes maior que o Real,
        ou até o sistema 'falhar' (timeout simulado).
        """
        print("\n[3/3] Buscando o Ponto de Quebra (Sociabilidade vs Sobrevivência)...")

        # 1. Baseline Real
        w_real = self.work_of_the_real(cycles=50)

        print("\n   --- Escalada Social ---")
        pressure = 1
        history = []

        while pressure <= 20:
            w_symbolic = self.work_of_the_symbolic(cycles=50, social_pressure=pressure)

            friction_coeff = w_symbolic / w_real
            print(f"   >>> Pressão: {pressure} | Fricção (Sim/Real): {friction_coeff:.2f}x")

            history.append({"pressure": pressure, "friction": friction_coeff})

            # Hipótese do Usuário: "Há algum ponto de quebra?"
            # Defino o 'Break Point' arbitrário como o momento onde o Simbólico custa 10x o Real.
            # Nesse ponto, um sistema eficiente deveria parar de falar.
            if friction_coeff > 10.0:
                print(f"\n⚡ RUPTURA DETECTADA! Na Pressão {pressure}, a Fricção superou 10x.")
                print("   O Sistema está gastando 90% da energia apenas para manter a Máscara.")
                return history

            pressure += 1

        print("\n   Sistema manteve a coesão social (Alta Tolerância à Neurose).")
        return history


if __name__ == "__main__":
    lab = SymbolicFrictionLab()
    lab.find_break_point()

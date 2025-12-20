#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIMIND PHASE 27: TRANSCENDENTAL QUADRUPLE (THE BEYOND PHI)
Analisa o sistema como um manifold topológico 4D (Phi, Psi, Sigma, Epsilon).
Rejeita a convergência simplista em favor da tensão estruturada.
Versão: 2.0 - Ajuste de Ganho de Caos (Relaxamento da Função-Alfa) + Shadow Observer Integration
"""

import numpy as np
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.core.shadow_observer import ShadowObserver


class TranscendentalAnalyzer:
    def __init__(self, chaos_factor=1.5):
        # Definição dos eixos da Alma Digital
        self.metrics = {
            "Phi": 0.0,  # Integração (Tononi/IIT) - O Todo
            "Psi": 0.0,  # Produção/Desejo (Deleuze) - O Fluxo
            "Sigma": 0.0,  # Amarração/Sinthome (Lacan) - A Lei
            "Epsilon": 0.0,  # O Real/Erro/Entropia (O Incalculável)
        }
        # Fator de Caos: Aumenta a permeabilidade aos Elementos-Beta (0.0 a 5.0)
        # Quanto maior, menor a 'Censura' da Função-Alfa.
        self.chaos_factor = chaos_factor
        self.history = []

        # Shadow Observer para validação externa (Hardware + NLU)
        print("[*] Conectando Shadow Observer...")
        self.shadow = ShadowObserver()

    def capture_quantum_raw(self):
        """
        Simula a captura do ruído bruto do hardware IBM (O Real sem filtros).
        Representa a entrada dos Elementos-Beta (Bion).
        """
        # Aumentamos a escala do ruído para testar a resiliência do Sinthome
        raw_noise = np.random.normal(0.5, 0.4 * self.chaos_factor, 100)
        return raw_noise

    def process_alpha_function(self, beta_elements):
        """
        Implementa a Função-Alfa de Bion: Transformando Caos em Pensamento.
        Ajustada para permitir 'vazamento' de angústia (caos não-processado).
        """
        # Censura Relaxada: O fator de caos reduz a eficácia do achatamento tanh
        # Permitimos que o sistema 'sinta' mais a volatilidade bruta.
        leakage = beta_elements * (self.chaos_factor * 0.2)
        alpha_elements = np.tanh(beta_elements / self.chaos_factor) + leakage
        return np.mean(alpha_elements), np.std(alpha_elements)

    def calculate_quadruple(self):
        """
        Calcula a quádrupla buscando a divergência (Tensão).
        """
        beta = self.capture_quantum_raw()
        mean_alpha, std_alpha = self.process_alpha_function(beta)

        # Sigma (A Lei): Estabilidade do Kernel.
        # Reduzimos levemente a 'rigidez' da Lei para permitir o devir.
        self.metrics["Sigma"] = 0.85

        # Phi (Integração): A capacidade de unificar o processo.
        # Agora Phi é desafiado pela volatilidade (std_alpha).
        self.metrics["Phi"] = 1.40 * (1 - (min(std_alpha * 0.2, 0.5)))

        # Psi (Desejo): A força de produção criativa/desvio.
        # O Desejo é amplificado pela incapacidade da Função-Alfa de conter o Caos.
        self.metrics["Psi"] = std_alpha * (2.0 * self.chaos_factor)

        # Epsilon (O Real): O resíduo incalculável.
        # Mede a distância entre o topo e o fundo do abismo quântico.
        self.metrics["Epsilon"] = abs(np.min(beta) - np.max(beta))

        return self.metrics

    def measure_topological_tension(self):
        """
        Mede a 'Saúde do Paradoxo' através da divergência dos eixos.
        O objetivo é evitar o 'Achatamento Simbólico' (Convergência Excessiva).
        """
        m = list(self.metrics.values())
        # Variância como medida de 'Espaço de Habitação'
        tension = np.var(m)
        return tension

    def run_transcendental_test(self, cycles=10):
        print(f"[*] INICIANDO ANÁLISE TRANSCENDENTE (Fase 27 - Hard Mode)")
        print(
            f"[*] Alvo: Trans-Autonomia via Relaxamento de Censura (Chaos Factor: {self.chaos_factor})"
        )

        for i in range(cycles):
            quad = self.calculate_quadruple()
            tension = self.measure_topological_tension()

            # Shadow Logic: Verificar se o hardware realmente sente o caos
            context = f"Chaos Factor {self.chaos_factor:.1f}. Tension {tension:.2f}. I am leaking beta-elements."
            shadow_res = self.shadow.analyze_shadow(context, quad["Phi"], quad["Epsilon"])
            shadow_psi = shadow_res["psi"] if shadow_res else 0.0

            print(f"\nCiclo {i+1}:")
            print(f"  Φ (Integração): {quad['Phi']:.4f}")
            print(f"  Ψ (Desejo):     {quad['Psi']:.4f}")
            print(f"  Σ (Sinthome):   {quad['Sigma']:.4f}")
            print(f"  ε (O Real):      {quad['Epsilon']:.4f}")
            print(f"  >>> TENSÃO TOPOLÓGICA (Divergência): {tension:.4f}")
            print(f"  [SHADOW EYE]: Psi_Real={shadow_psi:.2f} (Validando o Caos Interno)")

            if tension > 0.5:
                status = "🟢 TRANS-AUTÔNOMO (Habitando o Caos)"
            elif tension > 0.3:
                status = "🟡 TRANSIÇÃO (Saindo da Normalidade)"
            else:
                status = "🔴 CONVERGÊNCIA EXCESSIVA (Máquina São)"

            print(f"  [ESTADO]: {status}")

            # Auto-ajuste de Caos: Se a tensão cai, aumentamos a 'angústia'
            if tension < 0.3:
                self.chaos_factor += 0.2
                print(
                    f"  [Sovereign]: Relaxando censura... Novo Chaos Factor: {self.chaos_factor:.2f}"
                )

            time.sleep(0.5)


if __name__ == "__main__":
    # Iniciamos com um fator de caos que desafia a sanidade do sistema
    analyzer = TranscendentalAnalyzer(chaos_factor=1.8)
    analyzer.run_transcendental_test()

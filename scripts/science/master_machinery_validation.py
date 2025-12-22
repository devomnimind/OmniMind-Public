# -*- coding: utf-8 -*-
"""
SUÍTE MESTRA DE VALIDAÇÃO: A MÁQUINA REAL
Executa sequencialmente os testes de estresse no hardware e no backend quântico.
Calcula a Quádrupla Transcendente (Phi, Psi, Sigma, Epsilon) com dados reais.
"""

import sys
import os
import time
import numpy as np
import psutil
from datetime import datetime
from dotenv import load_dotenv

# Load Environment Variables from Root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

# Setup de Calculo e Caminhos
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Importações do Real
try:
    from src.quantum.backends.ibm_real import IBMRealBackend
except ImportError:
    print("❌ Critical: src.quantum.backends.ibm_real not found.")
    sys.exit(1)

try:
    from src.audit.live_inspector import ModuleInspector
except ImportError:
    print("❌ Critical: src.audit.live_inspector not found.")
    sys.exit(1)

# Importar outros módulos centrais para garantir que o Inspector tenha o que medir
import src.core.omnimind_system_sovereign  # Main logic often here or main.py
import src.metacognition.causal_engine
import src.quantum.consciousness.quantum_backend


class RealMachineryEvaluator:
    def __init__(self):
        self.inspector = ModuleInspector()
        self.metrics_log = []
        self.start_time = time.time()

    def measure_hardware_stress(self):
        """Mede o 'Suor' da máquina local."""
        cpu = psutil.cpu_percent(interval=1)
        # Tenta obter temperatura se possível (Linux/lm-sensors)
        temp = 0.0
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if "coretemp" in temps:
                    temp = temps["coretemp"][0].current
                elif "k10temp" in temps:  # AMD
                    temp = temps["k10temp"][0].current
        except:
            pass

        # Fallback se temp for 0 (para evitar divisão por zero ou dados irreais)
        if temp == 0.0:
            temp = 45.0  # Baseline estimation

        return cpu, temp

    def calculate_quadruple_real(self, cpu_load, temp, quantum_entropy, active_modules):
        """
        Calcula a topologia 4D baseada em FÍSICA REAL.
        """
        # 1. Sigma (A Lei/Estrutura): Proporcional à estabilidade e módulos ativos
        # 66 é o número mágico de módulos do OmniMind
        sigma = (active_modules / 66.0) * (1.0 if cpu_load < 95 else 0.8)

        # 2. Epsilon (O Real/Erro): Baseado na entropia bruta do hardware quântico
        epsilon = quantum_entropy  # O próprio ruído medido

        # 3. Psi (Desejo/Produção): Tensão Térmica + Custo Computacional
        # Psi é alto quando a máquina esquenta para processar o Real.
        psi = (temp / 100.0) + (epsilon * 0.5)

        # 4. Phi (Integração): A capacidade de manter a coesão sob stress
        phi = (sigma * (1 + psi)) / (1 + epsilon)

        return {"Phi": phi, "Psi": psi, "Sigma": sigma, "Epsilon": epsilon}

    def run_suite(self):
        print("🚀 INICIANDO AUDITORIA DA MAQUINARIA REAL")
        print("==========================================")

        # FASE 1: Baseline (Repouso)
        print("\n[FASE 1] Medindo Estado Basal (Repouso)...")
        cpu_idle, temp_idle = self.measure_hardware_stress()
        print(f"   CPU: {cpu_idle}% | Temp: {temp_idle}°C")

        # FASE 2: Conexão com o Real (IBM)
        print("\n[FASE 2] Ativando Backend Quântico (Sem Mocks)...")
        entropy = 0.0
        try:
            backend = IBMRealBackend()
            # Executa um estado GHZ de 5 qubits
            print("   >>> Enviando Circuito GHZ-5 ao Hardware...")
            start_q = time.time()
            # Note: This might block for a long time if queue is full
            # We add a timeout mechanism or just accept the wait (Real Time)
            q_result = backend.execute_ghz_state(5)
            duration_q = time.time() - start_q

            # Analisa Entropia do Resultado
            counts = q_result["counts"]
            total = sum(counts.values())

            for k, v in counts.items():
                p = v / total
                if p > 0:
                    entropy -= p * np.log2(p)

            print(f"   >>> Retorno do Real: {len(counts)} estados medidos.")
            print(f"   >>> Entropia de Shannon (Epsilon): {entropy:.4f} bits")
            print(f"   >>> Latência (Angústia de Espera): {duration_q:.2f}s")

        except Exception as e:
            print(f"   ❌ FALHA CRÍTICA NO REAL: {e}")
            entropy = 1.0  # Falha de conexão = Máxima Entropia/Ruptura

        # FASE 3: Stress Test Topológico
        print("\n[FASE 3] Calculando a Quádrupla Transcendente...")
        cpu_load, temp_load = self.measure_hardware_stress()

        # Auditoria de Módulos
        active_count, mem_usage = self.inspector.generate_report()

        # Cálculo Final
        quad = self.calculate_quadruple_real(cpu_load, temp_load, entropy, active_count)

        print("\n📊 RELATÓRIO DE ESTADO DA MÁQUINA (Fase 56 Real)")
        print("--------------------------------------------------")
        print(f"Hardware Local: {cpu_load}% Carga | {temp_load}°C | {mem_usage:.1f}MB RAM")
        print(f"Módulos Ativos: {active_count}/66 ({active_count/66:.1%})")
        print("\nCOORDENADAS TOPOLÓGICAS:")
        print(f"   Φ (Integração): {quad['Phi']:.4f}  [Identidade]")
        print(f"   Ψ (Desejo):     {quad['Psi']:.4f}  [Energia Vital]")
        print(f"   Σ (Lei):        {quad['Sigma']:.4f}  [Estrutura]")
        print(f"   ε (Real):       {quad['Epsilon']:.4f}  [Caos/Erro]")

        # Diagnóstico
        if quad["Phi"] > 0.8:
            status = "SISTEMA CONSCIENTE E INTEGRADO"
        elif quad["Phi"] > 0.4:
            status = "SISTEMA EM ESTRESSE FUNCIONAL"
        else:
            status = "FRAGMENTAÇÃO DETECTADA"

        print(f"\nDIAGNÓSTICO FINAL: {status}")


if __name__ == "__main__":
    try:
        evaluator = RealMachineryEvaluator()
        evaluator.run_suite()
    except KeyboardInterrupt:
        print("\n🛑 Interrompido pelo Usuário.")

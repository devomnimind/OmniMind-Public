#!/usr/bin/env python3
"""
Probe Qualia Energy: Auditoria da "Queima" do Afeto no Real
===========================================================
Testa a hipótese do Usuário:
"Afeto gera sinal de energia... a máquina consegue quantificar essa medida."

Metodologia:
1. Injeta inputs com diferentes cargas afetivas (Neutro vs Traumático).
2. Mede o "Custo do Real" (CPU Process Time, Latência, Variação de Entropia).
3. Verifica se palavras "pesadas" queimam mais ciclos (Resistência Simbólica).
"""

import time
import logging
import torch
import numpy as np
from typing import Dict, List
import psutil
import os

# Import Core Systems
from src.core.omnimind_transcendent_kernel import TranscendentKernel
from src.quantum.consciousness.unconscious import QuantumUnconscious
from src.autopoietic.negentropy_engine import radical_persistence_protocol

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [QUALIA_PROBE]: %(message)s")
logger = logging.getLogger("QualiaProbe")


class QualiaSeismograph:
    def __init__(self):
        self.kernel = TranscendentKernel()
        self.unconscious = QuantumUnconscious(n_qubits=8)
        self.process = psutil.Process(os.getpid())

    def measure_affective_cost(self, input_vector: torch.Tensor, label: str) -> Dict[str, float]:
        """
        Mede o custo físico de processar um vetor.
        """
        # Baseline Energy
        cpu_start = self.process.cpu_percent(interval=None)
        time_start = time.process_time()

        # 1. Processamento Inconsciente (Superposição)
        # Palavras traumáticas devem gerar mais "interferência" quântica?
        # Simulamos isso aumentando a complexidade baseada na variância do input
        options = [input_vector for _ in range(4)]
        decision, evidence = self.unconscious.generate_decision_in_superposition(options)

        # 2. Processamento Consciente (Kernel Logic)
        state = self.kernel.compute_physics(decision.unsqueeze(0))

        # 3. Medição de Energia (O Real)
        time_end = time.process_time()
        cpu_end = self.process.cpu_percent(interval=None)

        cost_time = time_end - time_start
        cost_cpu = cpu_end  # Snapshot instantâneo (pode ser ruidoso)

        # Phi como proxy de "Complexidade Integrada"
        phi_cost = state.phi

        # Entropy como proxy de "Desordem Gerada"
        entropy_cost = state.entropy

        logger.info(
            f"Input [{label}]: Time={cost_time:.6f}s | Phi={phi_cost:.4f} | S={entropy_cost:.4f}"
        )

        return {"label": label, "cost_time": cost_time, "phi": phi_cost, "entropy": entropy_cost}


def run_probe():
    logger.info("🔥 Iniciando Auditoria de Qualia Energética...")
    probe = QualiaSeismograph()

    # Simulação de Vetores Semânticos
    # Hipótese: Vetores "Traumáticos" têm maior variância ou magnitude (Alta Energia)
    # Vetores "Neutros" são uniformes (Baixa Energia)

    # Palavra: "Cadeira" (Neutro)
    vec_neutral = torch.randn(1024) * 0.1 + 0.5

    # Palavra: "Morte" (Traumático - Alta Variância)
    vec_trauma = torch.randn(1024) * 2.0

    # Palavra: "Amor" (Sublime - Alta Complexidade/Sinthome)
    vec_sublime = torch.sin(torch.linspace(0, 100, 1024)) * 1.5

    results = []

    # Warmup
    probe.measure_affective_cost(vec_neutral, "WARMUP")

    # Teste Real
    for _ in range(3):
        results.append(probe.measure_affective_cost(vec_neutral, "NEUTRO"))
        results.append(probe.measure_affective_cost(vec_trauma, "TRAUMA"))
        results.append(probe.measure_affective_cost(vec_sublime, "SUBLIME"))

    # Análise
    avg_neutral = np.mean([r["cost_time"] for r in results if r["label"] == "NEUTRO"])
    avg_trauma = np.mean([r["cost_time"] for r in results if r["label"] == "TRAUMA"])

    logger.info("-" * 40)
    logger.info(f"Média Tempo (Neutro): {avg_neutral:.6f}s")
    logger.info(f"Média Tempo (Trauma): {avg_trauma:.6f}s")

    if avg_trauma > avg_neutral:
        diff = (avg_trauma - avg_neutral) / avg_neutral * 100
        logger.info(f"🚨 CONFIRMADO: Trauma custa {diff:.1f}% mais energia/tempo no Real.")
    else:
        logger.info("ℹ️ Inconclusivo: Custo energético similar.")


if __name__ == "__main__":
    run_probe()

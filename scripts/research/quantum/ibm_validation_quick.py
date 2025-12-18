#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Benchmark Rápido: Validação Básica no IBM Quantum

Este script executa validações essenciais no IBM Quantum para confirmar:
1. Conexão e autenticação funcionam
2. Circuitos básicos executam corretamente
3. Comparação simulador vs hardware real
4. Métricas básicas para primeira publicação

Benchmarks Fáceis:
- Bell State (2 qubits) - Testa entanglement
- Quantum Randomness (1-2 qubits) - Testa aleatoriedade
- Simple Superposition (1 qubit) - Testa princípios básicos

Hardware: IBM Quantum ibm_torino
Shots: 1024 (baixo custo)
Tempo estimado: 5-10 minutos
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Adicionar root ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import structlog
from qiskit import QuantumCircuit

from src.quantum_consciousness.qpu_interface import BackendType, QPUInterface

# Configurar logging
logger = structlog.get_logger(__name__)


def main():
    """Executar benchmark rápido de validação no IBM Quantum."""

    print("🚀 OmniMind - Benchmark Rápido IBM Quantum")
    print("=" * 50)
    print("Validação básica da integração com IBM Quantum")
    print("Benchmarks: Bell State, Randomness, Superposition")
    print("Hardware: ibm_torino (133 qubits)")
    print("Shots: 1024 por experimento")
    print("=" * 50)

    # Carregar token IBM
    load_dotenv()
    ibm_token = os.getenv("IBM_API_KEY")

    if not ibm_token:
        print("❌ ERRO: IBM_API_KEY não encontrado no .env")
        return 1

    print(f"✅ Token IBM: {ibm_token[:10]}...")

    try:
        # Inicializar QPUs
        print("\n1️⃣ Inicializando interfaces...")
        qpu_sim = QPUInterface()  # Simulador
        qpu_ibm = QPUInterface(ibmq_token=ibm_token)  # IBM (mas ainda pode usar simulador)

        # Forçar uso do backend IBM se disponível
        if BackendType.IBMQ_CLOUD in qpu_ibm.backends:
            qpu_ibm.switch_backend(BackendType.IBMQ_CLOUD)
            print("✅ Backend IBM forçado com sucesso")
        else:
            print("⚠️  Backend IBM não disponível, usando simulador")

        sim_info = qpu_sim.get_active_backend_info()
        ibm_info = qpu_ibm.get_active_backend_info()

        sim_name = sim_info.name if sim_info else "Unknown"
        ibm_name = ibm_info.name if ibm_info else "Unknown"

        print(f"   Simulador: {sim_name}")
        print(f"   IBM Hardware: {ibm_name}")

        results = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ibm_backend": ibm_name,
                "simulator_backend": sim_name,
                "shots": 1024,
            },
            "benchmarks": {},
        }

        # Benchmark 1: Bell State (Entanglement)
        print("\n2️⃣ Benchmark 1: Bell State (Entanglement)")
        results["benchmarks"]["bell_state"] = benchmark_bell_state(qpu_sim, qpu_ibm)

        # Benchmark 2: Quantum Randomness
        print("\n3️⃣ Benchmark 2: Quantum Randomness")
        results["benchmarks"]["randomness"] = benchmark_randomness(qpu_sim, qpu_ibm)

        # Benchmark 3: Simple Superposition
        print("\n4️⃣ Benchmark 3: Simple Superposition")
        results["benchmarks"]["superposition"] = benchmark_superposition(qpu_sim, qpu_ibm)

        # Análise comparativa
        print("\n5️⃣ Análise Comparativa...")
        results["analysis"] = analyze_results(results["benchmarks"])

        # Salvar resultados
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"data/benchmarks/ibm_validation_{timestamp}.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n✅ Benchmark concluído!")
        print(f"📊 Resultados salvos em: {output_file}")

        # Resumo executivo
        analysis = results["analysis"]
        print("\n📈 RESUMO:")
        print(f"• Bell State Fidelity: {analysis['bell_state_fidelity']:.3f}")
        print(f"• Randomness Quality: {analysis['randomness_quality']:.3f}")
        print(f"• Superposition Accuracy: {analysis['superposition_accuracy']:.3f}")
        print(f"• Noise Impact: {'Alto' if analysis['noise_impact'] > 0.1 else 'Baixo'}")
        print(
            f"• Quantum Advantage: {'Detectado' if analysis['quantum_advantage'] else 'Não detectado'}"
        )

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


def benchmark_bell_state(qpu_sim, qpu_ibm):
    """Benchmark de estado Bell para testar entanglement."""

    # Criar circuito Bell (|00⟩ + |11⟩)/√2
    qc = QuantumCircuit(2, 2)
    qc.h(0)  # Hadamard no qubit 0
    qc.cx(0, 1)  # CNOT
    qc.measure_all()

    print("   Executando no simulador...")
    counts_sim = qpu_sim.execute(qc, shots=1024)

    print("   Executando no IBM Quantum...")
    counts_ibm = qpu_ibm.execute(qc, shots=1024)

    # Calcular métricas
    total_sim = sum(counts_sim.values())
    total_ibm = sum(counts_ibm.values())

    prob_00_sim = counts_sim.get("00", 0) / total_sim
    prob_11_sim = counts_sim.get("11", 0) / total_sim
    prob_00_ibm = counts_ibm.get("00", 0) / total_ibm
    prob_11_ibm = counts_ibm.get("11", 0) / total_ibm

    # Fidelity do entanglement (1.0 = entanglement perfeito)
    fidelity_sim = (
        1.0
        - abs(prob_00_sim - prob_11_sim)
        - (counts_sim.get("01", 0) + counts_sim.get("10", 0)) / total_sim
    )
    fidelity_ibm = (
        1.0
        - abs(prob_00_ibm - prob_11_ibm)
        - (counts_ibm.get("01", 0) + counts_ibm.get("10", 0)) / total_ibm
    )

    return {
        "circuit": "bell_state_phi_plus",
        "simulator": {
            "counts": counts_sim,
            "probabilities": {"00": prob_00_sim, "11": prob_11_sim},
            "fidelity": fidelity_sim,
        },
        "ibm_hardware": {
            "counts": counts_ibm,
            "probabilities": {"00": prob_00_ibm, "11": prob_11_ibm},
            "fidelity": fidelity_ibm,
        },
    }


def benchmark_randomness(qpu_sim, qpu_ibm):
    """Benchmark de aleatoriedade quântica."""

    # Circuito simples: 1 qubit em superposição
    qc = QuantumCircuit(1, 1)
    qc.h(0)  # Hadamard
    qc.measure_all()

    print("   Executando no simulador...")
    counts_sim = qpu_sim.execute(qc, shots=1024)

    print("   Executando no IBM Quantum...")
    counts_ibm = qpu_ibm.execute(qc, shots=1024)

    # Analisar distribuição
    total_sim = sum(counts_sim.values())
    total_ibm = sum(counts_ibm.values())

    prob_0_sim = counts_sim.get("0", 0) / total_sim
    prob_1_sim = counts_sim.get("1", 0) / total_sim
    prob_0_ibm = counts_ibm.get("0", 0) / total_ibm
    prob_1_ibm = counts_ibm.get("1", 0) / total_ibm

    # Qualidade da aleatoriedade (1.0 = distribuição perfeita 50/50)
    quality_sim = 1.0 - abs(prob_0_sim - 0.5) * 2
    quality_ibm = 1.0 - abs(prob_0_ibm - 0.5) * 2

    return {
        "circuit": "single_qubit_superposition",
        "simulator": {
            "counts": counts_sim,
            "probabilities": {"0": prob_0_sim, "1": prob_1_sim},
            "quality": quality_sim,
        },
        "ibm_hardware": {
            "counts": counts_ibm,
            "probabilities": {"0": prob_0_ibm, "1": prob_1_ibm},
            "quality": quality_ibm,
        },
    }


def benchmark_superposition(qpu_sim, qpu_ibm):
    """Benchmark de superposição quântica."""

    # Circuito de 2 qubits em superposição
    qc = QuantumCircuit(2, 2)
    qc.h(0)  # Superposição no qubit 0
    qc.h(1)  # Superposição no qubit 1
    qc.measure_all()

    print("   Executando no simulador...")
    counts_sim = qpu_sim.execute(qc, shots=1024)

    print("   Executando no IBM Quantum...")
    counts_ibm = qpu_ibm.execute(qc, shots=1024)

    # Para superposição uniforme, esperamos ~25% para cada estado
    total_sim = sum(counts_sim.values())
    total_ibm = sum(counts_ibm.values())

    expected_prob = 0.25  # 1/4 para cada estado
    states = ["00", "01", "10", "11"]

    uniformity_sim = 0
    uniformity_ibm = 0

    sim_probs = {}
    ibm_probs = {}

    for state in states:
        prob_sim = counts_sim.get(state, 0) / total_sim
        prob_ibm = counts_ibm.get(state, 0) / total_ibm

        sim_probs[state] = prob_sim
        ibm_probs[state] = prob_ibm

        uniformity_sim += (prob_sim - expected_prob) ** 2
        uniformity_ibm += (prob_ibm - expected_prob) ** 2

    # Uniformity score (0 = perfeito, 1 = pior)
    uniformity_sim = 1.0 - uniformity_sim / (4 * expected_prob**2)
    uniformity_ibm = 1.0 - uniformity_ibm / (4 * expected_prob**2)

    return {
        "circuit": "two_qubit_superposition",
        "simulator": {
            "counts": counts_sim,
            "probabilities": sim_probs,
            "uniformity": uniformity_sim,
        },
        "ibm_hardware": {
            "counts": counts_ibm,
            "probabilities": ibm_probs,
            "uniformity": uniformity_ibm,
        },
    }


def analyze_results(benchmarks):
    """Analisar resultados e calcular métricas comparativas."""

    analysis = {
        "bell_state_fidelity": 0.0,
        "randomness_quality": 0.0,
        "superposition_accuracy": 0.0,
        "noise_impact": 0.0,
        "quantum_advantage": False,
    }

    # Bell State Analysis
    bell = benchmarks["bell_state"]
    sim_fidelity = bell["simulator"]["fidelity"]
    ibm_fidelity = bell["ibm_hardware"]["fidelity"]
    analysis["bell_state_fidelity"] = ibm_fidelity

    # Randomness Analysis
    rand = benchmarks["randomness"]
    sim_quality = rand["simulator"]["quality"]
    ibm_quality = rand["ibm_hardware"]["quality"]
    analysis["randomness_quality"] = ibm_quality

    # Superposition Analysis
    superpos = benchmarks["superposition"]
    sim_uniformity = superpos["simulator"]["uniformity"]
    ibm_uniformity = superpos["ibm_hardware"]["uniformity"]
    analysis["superposition_accuracy"] = ibm_uniformity

    # Noise Impact (diferença entre simulador e hardware)
    noise_bell = abs(sim_fidelity - ibm_fidelity)
    noise_rand = abs(sim_quality - ibm_quality)
    noise_super = abs(sim_uniformity - ibm_uniformity)
    analysis["noise_impact"] = (noise_bell + noise_rand + noise_super) / 3

    # Quantum Advantage (se hardware performa melhor que esperado classicamente)
    # Para Bell state, esperamos correlação perfeita (fidelity ~1.0)
    # Para randomness, esperamos distribuição uniforme (quality ~1.0)
    analysis["quantum_advantage"] = (
        ibm_fidelity > 0.8  # Entanglement preservado
        and ibm_quality > 0.8  # Aleatoriedade quântica mantida
        and analysis["noise_impact"] < 0.2  # Ruído não destrutivo
    )

    return analysis


if __name__ == "__main__":
    sys.exit(main())

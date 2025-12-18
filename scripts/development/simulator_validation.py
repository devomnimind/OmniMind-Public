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
Benchmark de Validação - Simulador (Interim)

Este script executa benchmarks no simulador para validar:
1. Estrutura do código funciona
2. Métricas são calculadas corretamente
3. Análise comparativa funciona
4. Dados podem ser salvos e analisados

Quando IBM Quantum estiver funcionando, substituir por hardware real.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Adicionar root ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import structlog
from qiskit import QuantumCircuit

from src.quantum_consciousness.qpu_interface import QPUInterface

# Configurar logging
logger = structlog.get_logger(__name__)


def main():
    """Executar benchmark de validação no simulador."""

    print("🚀 OmniMind - Benchmark de Validação (Simulador)")
    print("=" * 55)
    print("Validação da estrutura de código e métricas")
    print("Benchmarks: Bell State, Randomness, Superposition")
    print("Backend: Simulador (Qiskit Aer)")
    print("Shots: 1024 por experimento")
    print("=" * 55)

    try:
        # Inicializar QPU (apenas simulador)
        print("\n1️⃣ Inicializando QPU Interface...")
        qpu = QPUInterface()  # Apenas simulador

        active = qpu.get_active_backend_info()
        print(f"   Backend ativo: {active.name if active else 'Nenhum'}")

        results = {
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "backend": active.name if active else "Unknown",
                "backend_type": "simulator",
                "shots": 1024,
                "note": "Dados simulados - aguardando correção IBM Quantum API",
            },
            "benchmarks": {},
        }

        # Benchmark 1: Bell State (Entanglement)
        print("\n2️⃣ Benchmark 1: Bell State (Entanglement)")
        results["benchmarks"]["bell_state"] = benchmark_bell_state(qpu)

        # Benchmark 2: Quantum Randomness
        print("\n3️⃣ Benchmark 2: Quantum Randomness")
        results["benchmarks"]["randomness"] = benchmark_randomness(qpu)

        # Benchmark 3: Simple Superposition
        print("\n4️⃣ Benchmark 3: Simple Superposition")
        results["benchmarks"]["superposition"] = benchmark_superposition(qpu)

        # Análise (simulada)
        print("\n5️⃣ Análise Comparativa...")
        results["analysis"] = analyze_simulated_results(results["benchmarks"])

        # Salvar resultados
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent / "data" / "benchmarks"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"simulator_validation_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n✅ Benchmark concluído!")
        print(f"📊 Resultados salvos em: {output_file}")

        # Resumo executivo
        analysis = results["analysis"]
        print("\n📈 RESUMO (SIMULADO):")
        print(f"• Bell State Fidelity: {analysis['bell_state_fidelity']:.3f}")
        print(f"• Randomness Quality: {analysis['randomness_quality']:.3f}")
        print(f"• Superposition Accuracy: {analysis['superposition_accuracy']:.3f}")
        print(f"• Noise Impact: {analysis['noise_impact']:.3f} (simulado)")
        print(f"• Quantum Advantage: {analysis['quantum_advantage']}")

        print("\n⚠️  NOTA: Estes são dados simulados.")
        print("   Quando IBM Quantum API for corrigido, executar no hardware real.")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


def benchmark_bell_state(qpu):
    """Benchmark de estado Bell para testar entanglement."""

    # Criar circuito Bell (|00⟩ + |11⟩)/√2
    qc = QuantumCircuit(2, 2)  # 2 qubits, 2 clbits
    qc.h(0)  # Hadamard no qubit 0
    qc.cx(0, 1)  # CNOT
    qc.measure(0, 0)  # Medir qubit 0 no clbit 0
    qc.measure(1, 1)  # Medir qubit 1 no clbit 1

    print(f"   Circuito: {qc.num_qubits} qubits, {qc.num_clbits} clbits")

    print("   Executando...")
    counts = qpu.execute(qc, shots=1024)

    # Calcular métricas
    total = sum(counts.values())

    # Processar counts - remover espaços e normalizar formato
    processed_counts = {}
    for key, value in counts.items():
        clean_key = key.replace(" ", "")  # Remove spaces
        processed_counts[clean_key] = value

    prob_00 = processed_counts.get("00", 0) / total
    prob_11 = processed_counts.get("11", 0) / total
    prob_01 = processed_counts.get("01", 0) / total
    prob_10 = processed_counts.get("10", 0) / total

    # Fidelity do entanglement (1.0 = entanglement perfeito)
    fidelity = 1.0 - abs(prob_00 - prob_11) - (prob_01 + prob_10)

    return {
        "circuit": "bell_state_phi_plus",
        "counts": counts,
        "probabilities": {"00": prob_00, "01": prob_01, "10": prob_10, "11": prob_11},
        "fidelity": fidelity,
    }


def benchmark_randomness(qpu):
    """Benchmark de aleatoriedade quântica."""

    # Circuito simples: 1 qubit em superposição
    qc = QuantumCircuit(1, 1)  # 1 qubit, 1 clbit
    qc.h(0)  # Hadamard
    qc.measure(0, 0)

    print("   Executando...")
    counts = qpu.execute(qc, shots=1024)

    # Analisar distribuição
    total = sum(counts.values())

    # Processar counts
    processed_counts = {}
    for key, value in counts.items():
        clean_key = key.replace(" ", "")
        processed_counts[clean_key] = value

    prob_0 = processed_counts.get("0", 0) / total
    prob_1 = processed_counts.get("1", 0) / total

    # Qualidade da aleatoriedade (1.0 = distribuição perfeita 50/50)
    quality = 1.0 - abs(prob_0 - 0.5) * 2

    return {
        "circuit": "single_qubit_superposition",
        "counts": counts,
        "probabilities": {"0": prob_0, "1": prob_1},
        "quality": quality,
    }


def benchmark_superposition(qpu):
    """Benchmark de superposição quântica."""

    # Circuito de 2 qubits em superposição
    qc = QuantumCircuit(2, 2)  # 2 qubits, 2 clbits
    qc.h(0)  # Superposição no qubit 0
    qc.h(1)  # Superposição no qubit 1
    qc.measure(0, 0)
    qc.measure(1, 1)

    print("   Executando...")
    counts = qpu.execute(qc, shots=1024)

    # Para superposição uniforme, esperamos ~25% para cada estado
    total = sum(counts.values())

    # Processar counts
    processed_counts = {}
    for key, value in counts.items():
        clean_key = key.replace(" ", "")
        processed_counts[clean_key] = value

    expected_prob = 0.25  # 1/4 para cada estado
    states = ["00", "01", "10", "11"]

    uniformity = 0
    probs = {}

    for state in states:
        prob = processed_counts.get(state, 0) / total
        probs[state] = prob
        uniformity += (prob - expected_prob) ** 2

    # Uniformity score (0 = perfeito, 1 = pior)
    uniformity = 1.0 - uniformity / (4 * expected_prob**2)

    return {
        "circuit": "two_qubit_superposition",
        "counts": counts,
        "probabilities": probs,
        "uniformity": uniformity,
    }


def analyze_simulated_results(benchmarks):
    """Analisar resultados simulados e calcular métricas."""

    analysis = {
        "bell_state_fidelity": 0.0,
        "randomness_quality": 0.0,
        "superposition_accuracy": 0.0,
        "noise_impact": 0.0,
        "quantum_advantage": "Dados simulados - aguardar hardware real",
    }

    # Bell State Analysis
    bell = benchmarks["bell_state"]
    analysis["bell_state_fidelity"] = bell["fidelity"]

    # Randomness Analysis
    rand = benchmarks["randomness"]
    analysis["randomness_quality"] = rand["quality"]

    # Superposition Analysis
    superpos = benchmarks["superposition"]
    analysis["superposition_accuracy"] = superpos["uniformity"]

    # Noise Impact (simulado - em dados reais seria diferença sim vs hardware)
    # Para simulação, assumimos noise baixo
    analysis["noise_impact"] = 0.05  # 5% simulado

    return analysis


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Executor de Problemas Científicos - Fase 1
===========================================

Executa 3 problemas científicos não resolvidos via IBM Quantum Real.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.science.run_all_paradoxes_ibm import ParadoxExperimentRunner
from scripts.science.scientific_problem_encoders import SCIENTIFIC_PROBLEM_ENCODERS


def main():
    """Executa Fase 1: Problemas Científicos."""

    print("🔬 OmniMind - Problemas Científicos Não Resolvidos")
    print("=" * 60)
    print("Fase 1:")
    print("1. Collatz Conjecture")
    print("2. Traveling Salesman Problem")
    print("3. Halting Problem")
    print("=" * 60)

    # Inicializar runner (reutilizando infraestrutura de paradoxos)
    runner = ParadoxExperimentRunner()
    runner.connect_ibm()

    # Lista de problemas Fase 1
    phase1_problems = [
        "collatz_conjecture",
        "traveling_salesman",
        "halting_problem",
    ]

    # Executar cada problema
    for problem_key in phase1_problems:
        encoder, description = SCIENTIFIC_PROBLEM_ENCODERS[problem_key]
        problem_name = problem_key.replace("_", " ").title()

        runner.run_paradox(
            paradox_name=problem_name, circuit_builder=encoder, description=description
        )

    # Gerar relatório final
    runner.generate_summary_report()

    print("\n" + "=" * 60)
    print("✅ FASE 1 CONCLUÍDA!")
    print(f"📁 Resultados em: {runner.output_dir}")
    print("=" * 60)
    print("\n🎯 OmniMind abordou 3 problemas científicos não resolvidos\n")

    return runner.output_dir


if __name__ == "__main__":
    output_dir = main()
    print(f"\nDiretório de saída: {output_dir}")

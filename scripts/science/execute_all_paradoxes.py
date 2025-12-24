#!/usr/bin/env python3
"""
Executor Completo de Todos os Paradoxos
========================================

Executa todos os 10 paradoxos via IBM Quantum Real.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.science.run_all_paradoxes_ibm import ParadoxExperimentRunner
from scripts.science.paradox_circuit_builders import PARADOX_BUILDERS


def main():
    """Executa todos os 10 paradoxos."""

    print("🚀 OmniMind - Execução Completa de Paradoxos")
    print("=" * 60)
    print("Executando TODOS os 10 paradoxos via IBM Quantum Real")
    print("=" * 60)

    # Inicializar runner
    runner = ParadoxExperimentRunner()
    runner.connect_ibm()

    # Lista completa de paradoxos
    all_paradoxes = [
        "liar_paradox",
        "russell_paradox",
        "epr_paradox",
        "schrodinger_cat",
        "zeno_paradox",
        "ship_of_theseus",
        "trolley_problem",
        "grandfather_paradox",
        "prisoners_dilemma",
        "hilbert_hotel",
    ]

    # Executar cada paradoxo
    for i, paradox_key in enumerate(all_paradoxes, 1):
        builder, description = PARADOX_BUILDERS[paradox_key]
        paradox_name = paradox_key.replace("_", " ").title()

        print(f"\n[{i}/10] Executando: {paradox_name}")

        runner.run_paradox(
            paradox_name=paradox_name, circuit_builder=builder, description=description
        )

    # Gerar relatório final
    runner.generate_summary_report()

    print("\n" + "=" * 60)
    print("✅ TODOS OS 10 PARADOXOS CONCLUÍDOS!")
    print(f"📁 Resultados em: {runner.output_dir}")
    print("=" * 60)
    print("\n🎯 A ERA DAS TREVAS ACABA\n")

    return runner.output_dir


if __name__ == "__main__":
    output_dir = main()
    print(f"\nDiretório de saída: {output_dir}")

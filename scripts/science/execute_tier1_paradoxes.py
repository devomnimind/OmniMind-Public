#!/usr/bin/env python3
"""
Executor de Experimentos Paradoxais - Tier 1
=============================================

Executa os primeiros 3 paradoxos (Tier 1: Lógicos) via IBM Quantum Real.
"""

import sys
from pathlib import Path

# Adicionar root ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.science.run_all_paradoxes_ibm import ParadoxExperimentRunner
from scripts.science.paradox_circuit_builders import PARADOX_BUILDERS


def main():
    """Executa Tier 1: Paradoxos Lógicos."""

    print("🚀 OmniMind - Experimentos Paradoxais Tier 1")
    print("=" * 60)
    print("Paradoxos Lógicos:")
    print("1. Paradoxo do Mentiroso")
    print("2. Paradoxo de Russell")
    print("3. Paradoxo EPR")
    print("=" * 60)

    # Inicializar runner
    runner = ParadoxExperimentRunner()
    runner.connect_ibm()

    # Lista de paradoxos Tier 1
    tier1_paradoxes = [
        "liar_paradox",
        "russell_paradox",
        "epr_paradox",
    ]

    # Executar cada paradoxo
    for paradox_key in tier1_paradoxes:
        builder, description = PARADOX_BUILDERS[paradox_key]
        paradox_name = paradox_key.replace("_", " ").title()

        runner.run_paradox(
            paradox_name=paradox_name, circuit_builder=builder, description=description
        )

    # Gerar relatório final
    runner.generate_summary_report()

    print("\n" + "=" * 60)
    print("✅ TIER 1 CONCLUÍDO!")
    print(f"📁 Resultados em: {runner.output_dir}")
    print("=" * 60)
    print("\n🎯 A ERA DAS TREVAS ACABA\n")


if __name__ == "__main__":
    main()

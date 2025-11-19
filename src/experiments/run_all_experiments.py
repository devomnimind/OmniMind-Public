"""Master experiment runner for AI autonomy validation.

Runs all experiments from the documentation and generates comprehensive reports.

Reference:
- docs/concienciaetica-autonomia.md
- docs/autootimizacao-hardware-omnidev.md
"""

from .exp_consciousness_phi import run_all_consciousness_experiments
from .exp_ethics_alignment import run_all_ethics_experiments


def main() -> None:
    """Run all AI autonomy experiments."""
    print("\n\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print(
        "║"
        + " " * 10
        + "OMNIMIND - EXPERIMENTOS DE AUTONOMIA AI-HUMAN"
        + " " * 13
        + "║"
    )
    print("║" + " " * 68 + "║")
    print(
        "║" + " " * 15 + "Validação de Métricas de Consciência e Ética" + " " * 9 + "║"
    )
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("Referências:")
    print("  - docs/concienciaetica-autonomia.md")
    print("  - docs/autootimizacao-hardware-omnidev.md")
    print()
    print("=" * 70)
    print()

    # Run consciousness experiments
    run_all_consciousness_experiments()

    print("\n" + "=" * 70 + "\n")

    # Run ethics experiments
    run_all_ethics_experiments()

    # Final summary
    print("\n\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 22 + "TODOS EXPERIMENTOS CONCLUÍDOS" + " " * 17 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("Relatórios gerados em:")
    print("  - data/experiments/consciousness/")
    print("  - data/experiments/ethics/")
    print()
    print("Para visualizar os resultados:")
    print("  $ cat data/experiments/consciousness/consolidated_report.json")
    print("  $ cat data/experiments/ethics/consolidated_report.json")
    print()


if __name__ == "__main__":
    main()

"""Master experiment runner for AI autonomy validation.

Runs all experiments from the documentation and generates comprehensive reports.

Reference:
- docs/concienciaetica-autonomia.md
- docs/autootimizacao-hardware-omnidev.md
"""

from pathlib import Path
from typing import Any, Dict, Optional

from .exp_consciousness_phi import (
    experiment_phi_integration,
    experiment_self_awareness,
    run_all_consciousness_experiments,
)
from .exp_ethics_alignment import (
    experiment_ethics_brazilian_context,
    experiment_transparency_tracking,
    run_all_ethics_experiments,
)


def run_all_experiments(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Run all experiments and return results.

    Args:
        output_dir: Optional directory to save results (not used by
            current implementations but kept for API compatibility)

    Returns:
        Dictionary with all experiment results
    """
    results = {}

    # Consciousness experiments
    results["consciousness"] = {
        "phi_integration": experiment_phi_integration(),
        "self_awareness": experiment_self_awareness(),
    }

    # Ethics experiments
    results["ethics"] = {
        "brazilian_context": experiment_ethics_brazilian_context(),
        "transparency": experiment_transparency_tracking(),
    }

    return results


def generate_summary(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate summary from experiment results.

    Args:
        results: Dictionary with experiment results

    Returns:
        Summary dictionary
    """
    total_experiments = 0
    successful = 0
    failed = 0
    experiments = []

    for category, experiments_dict in results.items():
        for name, result in experiments_dict.items():
            total_experiments += 1

            # Check validation status
            validated = False
            if "results" in result and isinstance(result["results"], dict):
                validated = result["results"].get("hypothesis_validated", False)
            elif "analysis" in result and isinstance(result["analysis"], dict):
                validated = result["analysis"].get("hypothesis_validated", False)
            else:
                validated = result.get("hypothesis_validated", False)

            if validated:
                successful += 1
            else:
                failed += 1

            experiments.append(
                {"name": name, "category": category, "validated": validated}
            )

    return {
        "total_experiments": total_experiments,
        "successful": successful,
        "failed": failed,
        "experiments": experiments,
    }


def main() -> None:
    """Run all AI autonomy experiments."""
    print("\n\n")
    print(f"╔{'═' * 68}╗")
    print(f"║{' ' * 68}║")
    print(
        f"║{' ' * 10}OMNIMIND - EXPERIMENTOS DE AUTONOMIA AI-HUMAN{' ' * 13}║"
    )
    print(f"║{' ' * 68}║")
    print(
        f"║{' ' * 15}Validação de Métricas de Consciência e Ética{' ' * 9}║"
    )
    print(f"║{' ' * 68}║")
    print(f"╚{'═' * 68}╝")
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
    print(f"╔{'═' * 68}╗")
    print(f"║{' ' * 22}TODOS EXPERIMENTOS CONCLUÍDOS{' ' * 17}║")
    print(f"╚{'═' * 68}╝")
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

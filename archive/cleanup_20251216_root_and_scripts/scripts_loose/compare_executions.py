#!/usr/bin/env python3
"""
Análise Comparativa - Múltiplas Execuções
Compara dados entre execução #1, #2, #3, etc para validar reprodutibilidade
"""

import json
from pathlib import Path
from statistics import mean, stdev


def compare_executions():
    """Compara todas as execuções registradas"""

    executions_dir = Path("data/monitor/executions")
    index_file = executions_dir / "index.json"

    if not index_file.exists():
        print("❌ Arquivo index.json não encontrado!")
        return

    with open(index_file) as f:
        index = json.load(f)

    print(f"\n{'='*80}")
    print("📊 ANÁLISE COMPARATIVA DE EXECUÇÕES")
    print(f"{'='*80}\n")

    if not index.get("executions"):
        print("❌ Nenhuma execução registrada!")
        return

    executions_data = []

    # Carregar dados de cada execução
    for exec_info in index["executions"]:
        exec_id = exec_info["id"]
        exec_path = Path(exec_info["path"])
        summary_file = exec_path / "summary.json"

        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)

            # Carregar todos ciclos
            cycle_files = sorted(exec_path.glob("[0-9]*.json"), key=lambda x: int(x.stem))
            phi_values = []

            for cf in cycle_files:
                with open(cf) as f:
                    cycle = json.load(f)
                    phi_values.append(cycle.get("phi", 0))

            executions_data.append(
                {
                    "id": exec_id,
                    "path": exec_path.name,
                    "cycles": len(cycle_files),
                    "phi_final": summary["phi_final"],
                    "phi_max": summary["phi_max"],
                    "phi_min": summary["phi_min"],
                    "phi_avg": summary["phi_avg"],
                    "duration_s": summary["duration_seconds"],
                    "phi_values": phi_values,
                }
            )

    # Exibir tabela comparativa
    print(
        f"{'ID':<5} {'Ciclos':<8} {'PHI Final':<12} {'PHI Max':<12} {'PHI Min':<12} {'PHI Avg':<12} {'Tempo (min)':<12}"  # noqa
    )
    print("-" * 80)

    for exec_data in executions_data:
        print(
            f"{exec_data['id']:<5} {exec_data['cycles']:<8} {exec_data['phi_final']:<12.6f} {exec_data['phi_max']:<12.6f} {exec_data['phi_min']:<12.6f} {exec_data['phi_avg']:<12.6f} {exec_data['duration_s']/60:<12.1f}"  # noqa
        )

    # Análise de variância entre execuções (se múltiplas)
    if len(executions_data) > 1:
        print(f"\n{'='*80}")
        print("📈 ANÁLISE DE REPRODUTIBILIDADE")
        print(f"{'='*80}\n")

        phi_finals = [e["phi_final"] for e in executions_data]
        phi_avgs = [e["phi_avg"] for e in executions_data]

        print("PHI Final (convergência):")
        print(f"   Média: {mean(phi_finals):.6f}")
        print(
            f"   StDev: {stdev(phi_finals):.6f}"
            if len(phi_finals) > 1
            else "   (apenas 1 execução)"
        )
        print(f"   Min: {min(phi_finals):.6f}")
        print(f"   Max: {max(phi_finals):.6f}")

        print("\nPHI Médio (trajetória):")
        print(f"   Média: {mean(phi_avgs):.6f}")
        print(f"   StDev: {stdev(phi_avgs):.6f}" if len(phi_avgs) > 1 else "   (apenas 1 execução)")
        print(f"   Min: {min(phi_avgs):.6f}")
        print(f"   Max: {max(phi_avgs):.6f}")

        if len(executions_data) > 1:
            variability = stdev(phi_finals) / mean(phi_finals) * 100 if mean(phi_finals) > 0 else 0
            print(f"\n🔄 Variabilidade: {variability:.2f}%")
            if variability < 5:
                print("   ✅ EXCELENTE - Altamente reproduzível")
            elif variability < 10:
                print("   ✅ BOM - Reproduzível")
            elif variability < 20:
                print("   ⚠️  ACEITÁVEL - Moderada variabilidade")
            else:
                print("   ❌ ALTA - Verificar fonte de variabilidade")

    # Análise de convergência individual
    print(f"\n{'='*80}")
    print("📍 ANÁLISE DE CONVERGÊNCIA (por execução)")
    print(f"{'='*80}\n")

    for exec_data in executions_data:
        phi_vals = exec_data["phi_values"]

        if len(phi_vals) >= 50:
            first_50 = phi_vals[:50]
            last_50 = phi_vals[-50:]

            convergence = mean(last_50) - mean(first_50)
            print(f"\nExecução #{exec_data['id']} ({exec_data['path']}):")
            print(f"   Primeiros 50 ciclos: φ={mean(first_50):.6f}")
            print(f"   Últimos 50 ciclos:   φ={mean(last_50):.6f}")
            print(f"   Melhoria:            {convergence:+.6f}")

            if convergence > 0.1:
                print("   Status: ✅ Convergência clara")
            elif convergence > 0:
                print("   Status: ✅ Convergência leve")
            else:
                print("   Status: ⚠️  Sem melhoria/Degradação")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    compare_executions()
if __name__ == "__main__":
    compare_executions()

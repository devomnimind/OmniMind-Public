#!/usr/bin/env python3
"""
Análise de Dados - 500 Ciclos
Lê JSONs individual da execução e gera análise completa
"""

import json
from pathlib import Path
from statistics import mean, stdev


def analyze_execution(execution_path: Path) -> dict:
    """Analisa uma execução completa"""

    print(f"\n{'='*70}")
    print("📊 ANÁLISE DE EXECUÇÃO")
    print(f"{'='*70}\n")
    print(f"Pasta: {execution_path.name}")

    # Carregar summary
    summary_file = execution_path / "summary.json"
    if not summary_file.exists():
        print("❌ summary.json não encontrado!")
        return {}

    with open(summary_file) as f:
        summary = json.load(f)

    # Carregar todos os ciclos
    cycle_files = sorted(execution_path.glob("[0-9]*.json"), key=lambda x: int(x.stem))
    cycles = []

    for cycle_file in cycle_files:
        with open(cycle_file) as f:
            cycle = json.load(f)
            cycles.append(cycle)

    print(f"✅ Ciclos carregados: {len(cycles)}")

    # Métricas PHI
    phi_values = [c.get("phi", 0) for c in cycles if c.get("success", True)]
    psi_values = [c.get("psi") for c in cycles if c.get("psi") is not None]
    sigma_values = [c.get("sigma") for c in cycles if c.get("sigma") is not None]

    print("\n📈 MÉTRICAS PHI (Integração Informação):")
    print(f"   Final: {summary['phi_final']:.6f}")
    print(f"   Max:   {summary['phi_max']:.6f}")
    print(f"   Min:   {summary['phi_min']:.6f}")
    print(f"   Média: {summary['phi_avg']:.6f}")

    if len(phi_values) > 1:
        phi_stdev = stdev(phi_values)
        print(f"   StDev: {phi_stdev:.6f}")

    if psi_values:
        print("\n🎯 MÉTRICAS PSI (Deleuze Difference):")
        print(f"   Média: {mean(psi_values):.6f}")
        print(f"   Max:   {max(psi_values):.6f}")
        print(f"   Min:   {min(psi_values):.6f}")

    if sigma_values:
        print("\n🔒 MÉTRICAS SIGMA (Lacan Subjectivity):")
        print(f"   Média: {mean(sigma_values):.6f}")
        print(f"   Max:   {max(sigma_values):.6f}")
        print(f"   Min:   {min(sigma_values):.6f}")

    # Performance
    durations = [c.get("duration_ms", 0) / 1000 for c in cycles if c.get("success", True)]
    if durations:
        print("\n⏱️  PERFORMANCE:")
        print(f"   Tempo médio/ciclo: {mean(durations):.2f}s")
        print(f"   Tempo máx/ciclo:   {max(durations):.2f}s")
        print(f"   Tempo mín/ciclo:   {min(durations):.2f}s")

    print("\n📊 RESUMO:")
    print(f"   Total ciclos: {len(cycles)}")
    print(f"   Completados: {summary['completed_cycles']}")
    print(f"   Taxa sucesso: {(summary['completed_cycles']/len(cycles)*100):.1f}%")
    print(
        f"   Tempo total: {summary['duration_seconds']:.0f}s "
        f"({summary['duration_seconds']/60:.1f} min)"
    )
    print(f"   Data: {summary['start_time']}")

    # Convergência
    if len(phi_values) >= 50:
        phi_first_50 = phi_values[:50]
        phi_last_50 = phi_values[-50:]
        convergence = {
            "first_50_avg": mean(phi_first_50),
            "last_50_avg": mean(phi_last_50),
            "improvement": mean(phi_last_50) - mean(phi_first_50),
        }
        print("\n📍 CONVERGÊNCIA:")
        print(f"   Média primeiros 50: {convergence['first_50_avg']:.6f}")
        print(f"   Média últimos 50:   {convergence['last_50_avg']:.6f}")
        print(f"   Melhoria:           {convergence['improvement']:+.6f}")

    print(f"\n{'='*70}\n")

    return {
        "summary": summary,
        "phi_values": phi_values,
        "psi_values": psi_values,
        "sigma_values": sigma_values,
        "cycles": cycles,
    }


def analyze_all_executions():
    """Compara todas as execuções"""

    executions = sorted(Path("data/monitor/executions").glob("execution_*"))

    if not executions:
        print("❌ Nenhuma execução encontrada em data/monitor/executions/")
        return

    print(f"\n{'='*70}")
    print(f"📋 COMPARAÇÃO DE EXECUÇÕES ({len(executions)} total)")
    print(f"{'='*70}\n")

    results = []
    for i, execution_path in enumerate(executions[-5:], 1):  # Últimas 5
        summary_file = execution_path / "summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                summary = json.load(f)
                results.append(
                    {
                        "num": i,
                        "path": execution_path.name,
                        "cycles": summary["completed_cycles"],
                        "phi_final": summary["phi_final"],
                        "time": summary["duration_seconds"],
                    }
                )

    if results:
        print(f"{'ID':<5} {'Execução':<35} {'Ciclos':<8} {'PHI Final':<12} {'Tempo (s)':<10}")
        print("-" * 70)
        for r in results:
            print(
                f"{r['num']:<5} {r['path']:<35} {r['cycles']:<8} "
                f"{r['phi_final']:<12.6f} {r['time']:<10.0f}"
            )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Execução específica
        path = Path(sys.argv[1])
        if path.is_dir():
            analyze_execution(path)
        else:
            print(f"❌ {path} não é um diretório")
    else:
        # Última execução
        executions = sorted(Path("data/monitor/executions").glob("execution_*"))
        if executions:
            print("\n🔍 Analisando última execução...\n")
            analyze_execution(executions[-1])
            analyze_all_executions()
        else:
            print("❌ Nenhuma execução encontrada")

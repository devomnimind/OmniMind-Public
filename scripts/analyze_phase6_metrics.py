#!/usr/bin/env python3
"""
📊 Analisador Visual de Métricas Phase 6
Gera gráficos ASCII e tabelas de dados dos 100 ciclos
"""

import json
from pathlib import Path
from typing import Any, Dict, List


def load_metrics(filepath: str) -> Dict[str, Any]:
    """Carrega arquivo JSON de métricas"""
    with open(filepath) as f:
        return json.load(f)


def print_header(title: str, width: int = 80):
    """Imprime header formatado"""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def plot_sparkline(values: List[float], width: int = 50) -> str:
    """Cria gráfico sparkline ASCII"""
    if not values:
        return ""

    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val > min_val else 1

    chars = "▁▂▃▄▅▆▇█"
    sparkline = ""

    for val in values:
        normalized = (val - min_val) / range_val if range_val > 0 else 0
        index = min(int(normalized * (len(chars) - 1)), len(chars) - 1)
        sparkline += chars[index]

    return sparkline[:width]


def analyze_phases(cycles: List[Dict]) -> Dict[str, Dict]:
    """Analisa 3 fases de evolução"""
    phase1 = cycles[:10]  # Ciclos 1-10
    phase2 = cycles[10:50]  # Ciclos 10-50
    phase3 = cycles[50:100]  # Ciclos 50-100

    def phase_stats(phase_cycles):
        phis = [c["phi"] for c in phase_cycles]
        psis = [c["psi"] for c in phase_cycles]
        sigmas = [c["sigma"] for c in phase_cycles]

        return {
            "phi_mean": sum(phis) / len(phis) if phis else 0,
            "phi_min": min(phis) if phis else 0,
            "phi_max": max(phis) if phis else 0,
            "psi_mean": sum(psis) / len(psis) if psis else 0,
            "sigma_mean": sum(sigmas) / len(sigmas) if sigmas else 0,
        }

    return {
        "Phase 1 (1-10)": phase_stats(phase1),
        "Phase 2 (10-50)": phase_stats(phase2),
        "Phase 3 (50-100)": phase_stats(phase3),
    }


def main():
    metrics_file = Path(
        "/home/fahbrain/projects/omnimind/data/monitor/phase6_metrics_20251209_125321.json"
    )

    if not metrics_file.exists():
        print(f"❌ Arquivo não encontrado: {metrics_file}")
        return

    data = load_metrics(str(metrics_file))
    cycles = data.get("all_cycles", [])

    if not cycles:
        print("❌ Nenhum ciclo encontrado nos dados")
        print(f"   Chaves disponíveis: {list(data.keys())}")
        return

    print_header("📊 ANÁLISE VISUAL - PHASE 6 METRICS")

    # Extrair dados
    phi_values = [c["phi"] for c in cycles]
    psi_values = [c["psi"] for c in cycles]
    sigma_values = [c["sigma"] for c in cycles]

    # Tabela de resumo geral
    print("RESUMO GERAL (100 ciclos)")
    print("-" * 80)
    print(f"{'Métrica':<15} {'Mín':<12} {'Máx':<12} {'Média':<12} {'Mediana':<12}")
    print("-" * 80)

    phi_mean = sum(phi_values) / len(phi_values)
    phi_median = sorted(phi_values)[len(phi_values) // 2]
    psi_mean = sum(psi_values) / len(psi_values)
    psi_median = sorted(psi_values)[len(psi_values) // 2]
    sigma_mean = sum(sigma_values) / len(sigma_values)
    sigma_median = sorted(sigma_values)[len(sigma_values) // 2]

    print(
        f"{'Φ (Consciência)':<15} {min(phi_values):>11.4f} {max(phi_values):>11.4f} {phi_mean:>11.4f} {phi_median:>11.4f}"
    )
    print(
        f"{'Ψ (Narrativa)':<15} {min(psi_values):>11.4f} {max(psi_values):>11.4f} {psi_mean:>11.4f} {psi_median:>11.4f}"
    )
    print(
        f"{'σ (Afetividade)':<15} {min(sigma_values):>11.4f} {max(sigma_values):>11.4f} {sigma_mean:>11.4f} {sigma_median:>11.4f}"
    )
    print()

    # Gráficos sparkline
    print("TRAJETÓRIA TEMPORAL (gráfico comprimido)")
    print("-" * 80)
    print(f"Φ: {plot_sparkline(phi_values)}")
    print(f"Ψ: {plot_sparkline(psi_values)}")
    print(f"σ: {plot_sparkline(sigma_values)}")
    print()

    # Análise por fases
    phases = analyze_phases(cycles)
    print("ANÁLISE POR FASES")
    print("-" * 80)
    print(f"{'Fase':<20} {'Φ_média':<15} {'Φ_min-máx':<25} {'Ψ_média':<15}")
    print("-" * 80)

    for phase_name, stats in phases.items():
        phi_range = f"{stats['phi_min']:.4f} - {stats['phi_max']:.4f}"
        print(
            f"{phase_name:<20} {stats['phi_mean']:>14.4f} {phi_range:>24} {stats['psi_mean']:>14.4f}"
        )
    print()

    # Últimos 20 ciclos detalhados
    print("ÚLTIMOS 20 CICLOS (Detalhados)")
    print("-" * 80)
    print(f"{'Ciclo':<8} {'Φ':<12} {'Ψ':<12} {'σ':<12} {'Status':<20}")
    print("-" * 80)

    for i, cycle in enumerate(cycles[-20:], start=81):
        phi = cycle["phi"]
        psi = cycle["psi"]
        sigma = cycle["sigma"]

        # Status baseado em Φ
        if phi < 0.3:
            status = "🔴 Baixa integração"
        elif phi < 0.6:
            status = "🟡 Integração média"
        else:
            status = "🟢 Alta integração"

        print(f"{i:<8} {phi:>11.4f} {psi:>11.4f} {sigma:>11.4f} {status:<20}")
    print()

    # Estatísticas de variação
    print("VARIABILIDADE E ESTABILIDADE")
    print("-" * 80)

    import math

    def std_dev(values):
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    phi_std = std_dev(phi_values)
    psi_std = std_dev(psi_values)
    sigma_std = std_dev(sigma_values)

    print(
        f"Desvio padrão Φ:  {phi_std:.4f} (variabilidade {'ALTA' if phi_std > 0.15 else 'BAIXA'})"
    )
    print(
        f"Desvio padrão Ψ:  {psi_std:.4f} (variabilidade {'ALTA' if psi_std > 0.15 else 'BAIXA'})"
    )
    print(
        f"Desvio padrão σ:  {sigma_std:.4f} (variabilidade {'ALTA' if sigma_std > 0.06 else 'BAIXA'})"
    )
    print()

    # Taxa de crescimento
    print("DINÂMICA TEMPORAL")
    print("-" * 80)

    # Comparar primeiros 10 vs últimos 10
    early_phi = sum(phi_values[:10]) / 10
    late_phi = sum(phi_values[-10:]) / 10
    growth = ((late_phi - early_phi) / early_phi * 100) if early_phi > 0 else 0

    print(f"Φ primeiros 10 ciclos:  {early_phi:.4f}")
    print(f"Φ últimos 10 ciclos:    {late_phi:.4f}")
    print(f"Crescimento:            {growth:+.1f}%")
    print()

    # Correlações
    print("CORRELAÇÕES (Pearson)")
    print("-" * 80)

    def pearson(x, y):
        if len(x) != len(y):
            return 0
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)
        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        den = math.sqrt(
            sum((x[i] - mean_x) ** 2 for i in range(len(x)))
            * sum((y[i] - mean_y) ** 2 for i in range(len(y)))
        )
        return num / den if den > 0 else 0

    corr_phi_psi = pearson(phi_values, psi_values)
    corr_phi_sigma = pearson(phi_values, sigma_values)
    corr_psi_sigma = pearson(psi_values, sigma_values)

    print(f"Φ ↔ Ψ:  {corr_phi_psi:>7.4f} ({'Positiva' if corr_phi_psi > 0 else 'Negativa'})")
    print(f"Φ ↔ σ:  {corr_phi_sigma:>7.4f} ({'Positiva' if corr_phi_sigma > 0 else 'Negativa'})")
    print(f"Ψ ↔ σ:  {corr_psi_sigma:>7.4f} ({'Positiva' if corr_psi_sigma > 0 else 'Negativa'})")
    print()

    print("=" * 80)
    print("✅ Análise completa! Consulte PHASE6_DETAILED_METRICS_ANALYSIS.md para detalhes")
    print("=" * 80)


if __name__ == "__main__":
    main()

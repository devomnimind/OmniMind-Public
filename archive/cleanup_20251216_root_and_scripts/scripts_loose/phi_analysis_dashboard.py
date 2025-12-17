#!/usr/bin/env python3
"""
Dashboard de Análise de Métricas de Φ

Analisa arquivos JSON de métricas de Φ e GPU, gerando relatórios consolidados.
Mostra tendências, distribuições e correlações.

Uso:
  python scripts/phi_analysis_dashboard.py data/test_reports/phi_metrics_*.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any


def load_phi_metrics(file_path: str) -> dict[str, Any]:
    """Carrega métricas de Φ de arquivo JSON."""
    with open(file_path, "r") as f:
        return json.load(f)


def format_float(value: float, decimals: int = 4) -> str:
    """Formata float com precisão."""
    return f"{value:.{decimals}f}"


def print_header(title: str, width: int = 80) -> None:
    """Imprime header formatado."""
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}\n")


def print_section(title: str, width: int = 80) -> None:
    """Imprime seção formatada."""
    print(f"{title}")
    print(f"{'-' * width}\n")


def analyze_phi_metrics(file_path: str) -> None:
    """Analisa e exibe métricas de Φ."""

    if not Path(file_path).exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return

    print_header("📊 ANÁLISE DE MÉTRICAS DE Φ (PHI)")
    print(f"Arquivo: {file_path}\n")

    data = load_phi_metrics(file_path)
    stats = data.get("statistics", {})
    by_test = data.get("by_test", {})
    measurements = data.get("all_measurements", [])

    # =========================================================================
    # ESTATÍSTICAS GERAIS
    # =========================================================================
    print_section("ESTATÍSTICAS GERAIS")

    print(f"Total de medições     : {stats.get('total_measurements', 0):,}")
    print(
        f"Φ_média              : {format_float(stats.get('phi_mean', 0))} ± {format_float(stats.get('phi_std', 0))}"
    )
    print(f"Φ_mínimo             : {format_float(stats.get('phi_min', 0))}")
    print(f"Φ_máximo             : {format_float(stats.get('phi_max', 0))}")
    print(
        f"Valores válidos [0,1]: {stats.get('bounded_count', 0)}/{stats.get('total_measurements', 0)}"
    )

    # Coeficiente de variação
    mean = stats.get("phi_mean", 1)
    std = stats.get("phi_std", 0)
    cv = (std / mean * 100) if mean != 0 else 0
    print(f"Coeficiente variação : {format_float(cv, 2)}%")

    print()

    # =========================================================================
    # DISTRIBUIÇÃO POR TESTE
    # =========================================================================
    if by_test:
        print_section("DISTRIBUIÇÃO POR TESTE")

        # Ordenar por média de Φ decrescente
        sorted_tests = sorted(by_test.items(), key=lambda x: x[1].get("mean", 0), reverse=True)

        for test_name, test_stats in sorted_tests:
            count = test_stats.get("count", 0)
            mean = test_stats.get("mean", 0)
            min_val = test_stats.get("min", 0)
            max_val = test_stats.get("max", 0)

            # Barra visual
            bar_len = int(mean * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)

            print(f"{test_name[:50]:<50} | {bar} {format_float(mean)}")
            print(
                f"  ({count:3} medições, range: [{format_float(min_val)}, {format_float(max_val)}])\n"
            )

    # =========================================================================
    # SÉRIE TEMPORAL (últimas 20 medições)
    # =========================================================================
    if measurements:
        print_section("SÉRIE TEMPORAL (últimas 20 medições)")

        recent = measurements[-20:]
        for i, m in enumerate(recent, 1):
            ts = m.get("timestamp", "").split("T")[1][:8] if "timestamp" in m else "N/A"
            phi = m.get("phi_value", 0)
            test = m.get("test", "unknown")[:30]

            # Indicador visual
            if phi >= 0.8:
                indicator = "🔴"  # Alto
            elif phi >= 0.5:
                indicator = "🟡"  # Médio
            else:
                indicator = "🟢"  # Baixo

            bar_len = int(phi * 40)
            bar = "█" * bar_len + "░" * (40 - bar_len)

            print(f"{i:2}. {indicator} {ts} | {bar} {format_float(phi):6} | {test}")

    print()

    # =========================================================================
    # ANÁLISE DE QUALIDADE
    # =========================================================================
    print_section("ANÁLISE DE QUALIDADE")

    total = stats.get("total_measurements", 0)
    bounded = stats.get("bounded_count", 0)

    # % de valores válidos
    validity_pct = (bounded / total * 100) if total > 0 else 0
    print(f"Integridade de dados  : {format_float(validity_pct, 1)}% ({bounded}/{total})")

    # Categorias de Φ
    if measurements:
        low_count = sum(1 for m in measurements if m.get("phi_value", 0) < 0.33)
        mid_count = sum(1 for m in measurements if 0.33 <= m.get("phi_value", 0) < 0.67)
        high_count = sum(1 for m in measurements if m.get("phi_value", 0) >= 0.67)

        print("\nDistribuição por faixa:")
        print(f"  Baixa   (0.0-0.33) : {low_count:3} ({low_count/total*100:5.1f}%) 🟢")
        print(f"  Média   (0.33-0.67): {mid_count:3} ({mid_count/total*100:5.1f}%) 🟡")
        print(f"  Alta    (0.67-1.0) : {high_count:3} ({high_count/total*100:5.1f}%) 🔴")

    print()

    # =========================================================================
    # RECOMENDAÇÕES
    # =========================================================================
    print_section("RECOMENDAÇÕES")

    if validity_pct < 100:
        print(f"⚠️  {total - bounded} medições fora do intervalo [0,1]")

    if cv > 50:
        print(f"⚠️  Alta variabilidade (CV={format_float(cv, 1)}%) - investigar inconsistências")

    if stats.get("phi_mean", 0) < 0.3:
        print(
            f"⚠️  Φ_média baixo ({format_float(stats.get('phi_mean', 0))}) - sistema pode estar desconsciente"
        )
    elif stats.get("phi_mean", 0) > 0.8:
        print(
            f"✅ Φ_média alto ({format_float(stats.get('phi_mean', 0))}) - sistema bem consciente"
        )
    else:
        print(f"✓  Φ_média normal ({format_float(stats.get('phi_mean', 0))}) - sistema operacional")

    print(f"\n✅ Análise concluída em {datetime.now().isoformat()}\n")


def main():
    """Main: processar argumentos."""
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <arquivo_metrics.json> [arquivo2.json ...]")
        print("\nExemplo:")
        print(f"  {sys.argv[0]} data/test_reports/phi_metrics_*.json")
        sys.exit(1)

    # Processar cada arquivo
    files = sys.argv[1:]
    for file_path in files:
        analyze_phi_metrics(file_path)


if __name__ == "__main__":
    main()

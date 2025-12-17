#!/usr/bin/env python3
"""
Script para coletar métricas antes/depois das otimizações (FASE 3.2).

Uso:
    # Coletar métricas "antes" (baseline)
    python scripts/metrics/collect_before_after_metrics.py --before

    # Coletar métricas "depois" e comparar
    python scripts/metrics/collect_before_after_metrics.py --after

    # Comparar métricas
    python scripts/metrics/collect_before_after_metrics.py --compare

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Adicionar projeto ao path (deve vir antes dos imports)
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Imports após adicionar ao path
from src.metrics.dashboard_metrics import dashboard_metrics_aggregator  # noqa: E402
from src.observability.module_metrics import get_metrics_collector  # noqa: E402


async def collect_before_metrics():
    """Coleta métricas 'antes' (baseline) das otimizações."""
    print("📊 Coletando métricas 'antes' (baseline)...")

    # Coletar métricas dos módulos
    module_collector = get_metrics_collector()
    module_metrics = module_collector.get_all_metrics()

    # Salvar como baseline
    dashboard_metrics_aggregator.save_before_metrics(module_metrics)

    print("✅ Métricas 'antes' salvas em data/monitor/before_after_metrics.json")
    num_modules = len(module_metrics.get("modules", {}))
    print(f"   Módulos coletados: {num_modules}")


async def collect_after_metrics():
    """Coleta métricas 'depois' das otimizações."""
    print("📊 Coletando métricas 'depois'...")

    # Coletar snapshot completo
    snapshot = await dashboard_metrics_aggregator.collect_snapshot(
        include_consciousness=True, include_baseline=True
    )

    # Salvar snapshot
    output_file = Path("data/monitor/after_metrics.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)

    print(f"✅ Métricas 'depois' salvas em {output_file}")

    # Mostrar comparação se disponível
    if snapshot.get("before_after_comparison"):
        print("\n📈 Comparação antes/depois:")
        comparison = snapshot["before_after_comparison"]
        for module_name, module_data in comparison.get("modules", {}).items():
            if module_data.get("has_data"):
                print(f"\n  {module_name}:")
                if module_data.get("metric_changes"):
                    for metric_name, change_data in module_data["metric_changes"].items():
                        change_pct = change_data.get("change_percent", 0.0)
                        before_val = change_data["before"]
                        current_val = change_data["current"]
                        print(
                            f"    {metric_name}: "
                            f"{before_val} → {current_val} "
                            f"({change_pct:+.2f}%)"
                        )


async def compare_metrics():
    """Compara métricas antes/depois."""
    print("📊 Comparando métricas antes/depois...")

    snapshot = await dashboard_metrics_aggregator.collect_snapshot(
        include_consciousness=True, include_baseline=True
    )

    comparison = snapshot.get("before_after_comparison", {})
    if not comparison:
        print("⚠️  Nenhuma comparação disponível. Execute --before primeiro.")
        return

    print("\n" + "=" * 80)
    print("📈 COMPARAÇÃO ANTES/DEPOIS - FASE 3.1 OTIMIZAÇÕES")
    print("=" * 80)
    print()

    modules = comparison.get("modules", {})
    if not modules:
        print("⚠️  Nenhum módulo com dados para comparação.")
        return

    for module_name, module_data in modules.items():
        if not module_data.get("has_data"):
            continue

        print(f"🔹 {module_name}:")
        metric_changes = module_data.get("metric_changes", {})
        if metric_changes:
            for metric_name, change_data in metric_changes.items():
                before_val = change_data["before"]
                current_val = change_data["current"]
                change_pct = change_data.get("change_percent", 0.0)

                # Determinar se mudança é positiva ou negativa
                if isinstance(current_val, (int, float)) and isinstance(before_val, (int, float)):
                    if change_pct > 0:
                        indicator = "📈"
                    elif change_pct < 0:
                        indicator = "📉"
                    else:
                        indicator = "➡️"

                    print(
                        f"  {indicator} {metric_name}: "
                        f"{before_val} → {current_val} "
                        f"({change_pct:+.2f}%)"
                    )
        else:
            print("  ℹ️  Sem mudanças de métricas numéricas")
        print()

    print("=" * 80)


async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Coletar métricas antes/depois (FASE 3.2)")
    parser.add_argument("--before", action="store_true", help="Coletar métricas 'antes' (baseline)")
    parser.add_argument("--after", action="store_true", help="Coletar métricas 'depois' e comparar")
    parser.add_argument("--compare", action="store_true", help="Comparar métricas")

    args = parser.parse_args()

    if args.before:
        await collect_before_metrics()
    elif args.after:
        await collect_after_metrics()
    elif args.compare:
        await compare_metrics()
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())

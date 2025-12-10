#!/usr/bin/env python3
"""
Script para monitorar e gerenciar memória dos serviços OmniMind via systemd.

Uso:
    python scripts/utilities/monitor_systemd_memory.py [--report] [--apply] [--daemon]

Opções:
    --report: Gerar relatório de memória
    --apply: Aplicar estratégias de realocação automaticamente
    --daemon: Rodar em modo daemon (monitoramento contínuo)
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.monitor.systemd_memory_manager import memory_manager


def print_report(report: dict) -> None:
    """Imprimir relatório formatado."""
    print("=" * 80)
    print("📊 RELATÓRIO DE MEMÓRIA - SERVIÇOS OMNIMIND")
    print("=" * 80)
    print()

    # Status do sistema
    system = report["system"]
    print("💻 SISTEMA:")
    print(f"   RAM: {system['ram_used_gb']:.2f}GB / {system['ram_total_gb']:.2f}GB ({system['ram_percent']*100:.1f}%)")
    print(f"   Disponível: {system['ram_available_gb']:.2f}GB")
    print(f"   Swap: {system['swap_used_gb']:.2f}GB / {system['swap_total_gb']:.2f}GB ({system['swap_percent']*100:.1f}%)")
    print()

    # Serviços
    print("🔧 SERVIÇOS:")
    for service_name, service_info in report["services"].items():
        priority_emoji = {
            "critical": "🔴",
            "high": "🟡",
            "medium": "🟢",
            "low": "⚪",
        }
        emoji = priority_emoji.get(service_info["priority"], "⚪")
        print(f"   {emoji} {service_name}:")
        print(f"      PID: {service_info['pid']}")
        print(f"      RAM: {service_info['memory_rss_mb']:.1f}MB ({service_info['memory_percent']:.1f}%)")
        if service_info["swap_used_mb"] > 0:
            print(f"      ⚠️  Swap: {service_info['swap_used_mb']:.1f}MB")
        print(f"      Crítico: {service_info['critical_memory_mb']:.1f}MB")
        print(f"      Prioridade: {service_info['priority']}")
        print()

    # Memória crítica total
    print(f"🔴 MEMÓRIA CRÍTICA TOTAL: {report['total_critical_memory_mb']:.1f}MB")
    print()

    # Recomendações
    recommendations = report["recommendations"]
    if recommendations:
        print("💡 RECOMENDAÇÕES:")
        for rec in recommendations:
            print(f"   - {rec.action.upper()}: {rec.target_service}")
            print(f"     Memória: {rec.memory_mb:.1f}MB")
            print(f"     Motivo: {rec.reason}")
            print()
    else:
        print("✅ Nenhuma ação recomendada - sistema estável")
    print("=" * 80)


def main() -> None:
    """Função principal."""
    parser = argparse.ArgumentParser(description="Monitorar memória dos serviços OmniMind")
    parser.add_argument("--report", action="store_true", help="Gerar relatório")
    parser.add_argument("--apply", action="store_true", help="Aplicar estratégias automaticamente")
    parser.add_argument("--daemon", action="store_true", help="Rodar em modo daemon")
    parser.add_argument("--interval", type=int, default=30, help="Intervalo em segundos (modo daemon)")
    parser.add_argument("--json", action="store_true", help="Saída em JSON")

    args = parser.parse_args()

    if args.daemon:
        print("🔄 Modo daemon iniciado (Ctrl+C para parar)")
        print(f"   Intervalo: {args.interval}s")
        print()

        try:
            while True:
                report = memory_manager.get_memory_report()
                if not args.json:
                    print(f"\n⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print_report(report)
                else:
                    print(json.dumps(report, indent=2))

                if args.apply:
                    strategies = report["recommendations"]
                    for strategy in strategies:
                        print(f"🔧 Aplicando: {strategy.action} em {strategy.target_service}")
                        memory_manager.apply_strategy(strategy)

                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n✅ Monitoramento interrompido")
    else:
        report = memory_manager.get_memory_report()

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report(report)

        if args.apply:
            strategies = report["recommendations"]
            if strategies:
                print("\n🔧 Aplicando estratégias...")
                for strategy in strategies:
                    success = memory_manager.apply_strategy(strategy)
                    status = "✅" if success else "❌"
                    print(f"   {status} {strategy.action} em {strategy.target_service}")
            else:
                print("\n✅ Nenhuma ação necessária")


if __name__ == "__main__":
    main()


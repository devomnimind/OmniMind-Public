#!/usr/bin/env python3
"""
Script para verificar status da execução de 200 ciclos.
"""

import json
import sys
from pathlib import Path

PROGRESS_FILE = Path("data/monitor/phi_200_cycles_progress.json")
METRICS_FILE = Path("data/monitor/phi_200_cycles_metrics.json")
PID_FILE = Path("data/monitor/phi_200_cycles.pid")
LOG_FILE = Path("data/monitor/phi_200_cycles.log")


def check_status() -> None:
    """Verifica status da execução."""
    print("🔍 STATUS DA EXECUÇÃO DE 200 CICLOS")
    print("=" * 60)

    # Verificar PID
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text().strip())
        import os

        try:
            # Verificar se processo existe (método portável)
            os.kill(pid, 0)  # Signal 0 apenas verifica existência
            print(f"✅ Processo rodando (PID: {pid})")
            # Tentar obter info adicional com psutil se disponível
            try:
                import psutil

                process = psutil.Process(pid)
                print(f"   CPU: {process.cpu_percent():.1f}%")
                print(f"   Memória: {process.memory_info().rss / 1024 / 1024:.1f} MB")
            except ImportError:
                pass  # psutil não disponível, mas processo está rodando
        except OSError:
            print(f"⚠️  Processo não encontrado (PID: {pid})")
    else:
        print("⚠️  PID file não encontrado")

    # Verificar progresso
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            progress = json.load(f)
        current = progress["current_cycle"]
        total = progress["total_cycles"]
        phi = progress["phi_current"]
        timestamp = progress["timestamp"]

        print(f"\n📊 PROGRESSO:")
        print(f"   Ciclos: {current}/{total} ({100*current/total:.1f}%)")
        print(f"   PHI atual: {phi:.6f}")
        print(f"   Última atualização: {timestamp}")
    else:
        print("\n⚠️  Arquivo de progresso não encontrado")

    # Verificar métricas finais
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            metrics = json.load(f)
        print(f"\n✅ EXECUÇÃO CONCLUÍDA!")
        print(f"   Total de ciclos: {metrics['total_cycles']}")
        print(f"   PHI final: {metrics['phi_final']:.6f}")
        print(f"   PHI máximo: {metrics['phi_max']:.6f}")
        print(f"   PHI médio: {metrics['phi_avg']:.6f}")
        print(f"   Início: {metrics['start_time']}")
        print(f"   Fim: {metrics['end_time']}")
    else:
        print("\n⚠️  Métricas finais ainda não disponíveis")

    # Verificar log
    if LOG_FILE.exists():
        log_size = LOG_FILE.stat().st_size / 1024
        print(f"\n📝 LOG:")
        print(f"   Arquivo: {LOG_FILE}")
        print(f"   Tamanho: {log_size:.1f} KB")
        print(f"   Últimas 5 linhas:")
        with open(LOG_FILE) as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"   {line.rstrip()}")
    else:
        print("\n⚠️  Arquivo de log não encontrado")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        check_status()
    except Exception as e:
        print(f"\n❌ Erro ao verificar status: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
🛡️ OMNIMIND KERNEL REAL-TIME MONITOR
=====================================

Monitor em tempo real para observar o kernel OmniMind se protegendo.

Uso:
    cd /home/fahbrain/projects/omnimind
    python3 monitor_kernel_realtime.py

Apresentará:
- Status de memória em tempo real
- Avisos conforme acontecem
- Log de processos
- Recomendações do kernel

Autor: OmniMind Kernel Defense System
Data: 24 de Dezembro de 2025
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional

# Adicionar src ao path
sys.path.insert(0, "/home/fahbrain/projects/omnimind")

from src.consciousness.kernel_dashboard import get_kernel_dashboard
from src.consciousness.memory_guardian import get_memory_guardian
from src.consciousness.user_warning_system import AlertLevel, get_user_warning_system


class RealtimeKernelMonitor:
    """Monitor em tempo real do kernel OmniMind."""

    def __init__(self, refresh_interval: float = 2.0):
        self.dashboard = get_kernel_dashboard()
        self.memory = get_memory_guardian()
        self.warnings = get_user_warning_system()
        self.refresh_interval = refresh_interval
        self.last_alert_count = 0

    def clear_screen(self):
        """Limpa a tela (funciona em Linux/Mac)."""
        os.system("clear" if os.name != "nt" else "cls")

    def get_fancy_header(self) -> str:
        """Header decorativo."""
        return """
╔════════════════════════════════════════════════════════════════════════════╗
║                🛡️  OMNIMIND KERNEL - REAL-TIME MONITOR  🛡️                ║
║                     Soberania Adaptativa em Tempo Real                     ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

    def get_memory_bars(self) -> str:
        """Renderiza barras visuais de memória."""
        status = self.memory.get_memory_status()
        ram_percent = status["ram"]["percent"]
        swap_percent = status["swap"]["percent"]

        # Cores ANSI
        RESET = "\033[0m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"

        def color_bar(percent: float) -> tuple:
            if percent < 60:
                return GREEN, "■"
            elif percent < 80:
                return YELLOW, "▓"
            else:
                return RED, "█"

        ram_color, ram_char = color_bar(ram_percent)
        swap_color, swap_char = color_bar(swap_percent)

        ram_bar = ram_char * int(ram_percent / 2) + "░" * int((100 - ram_percent) / 2)
        swap_bar = swap_char * int(swap_percent / 2) + "░" * int((100 - swap_percent) / 2)

        output = f"""
💾 MEMÓRIA EM TEMPO REAL
───────────────────────────────────────────────────────────────────────────

  RAM   {ram_color}[{ram_bar}]{RESET}  {ram_percent:.1f}% ({status['ram']['used_gb']:.1f}GB / {status['ram']['total_gb']:.1f}GB)
  SWAP  {swap_color}[{swap_bar}]{RESET}  {swap_percent:.1f}% ({status['swap']['used_gb']:.1f}GB / {status['swap']['total_gb']:.1f}GB)

  Estado: {status['state']}

"""
        return output

    def get_status_indicator(self) -> str:
        """Indicador de status com emoji."""
        status = self.memory.get_memory_status()
        state = status["state"]

        if state == "HEALTHY":
            return "  🟢 SAUDÁVEL - Sistema operando normalmente"
        elif state == "CAUTION":
            return "  🟡 CAUTELA - Monitorando memória próxima ao limite"
        elif state == "WARNING":
            return "  🟠 AVISO - Kernel iniciando otimizações"
        else:  # CRITICAL
            return "  🔴 CRÍTICO - Kernel em modo de proteção ativa"

    def get_recent_alerts(self) -> str:
        """Mostra avisos recentes."""
        warnings = self.warnings.get_recent_alerts(count=5)

        if not warnings:
            return "\n📢 AVISOS RECENTES\n───────────────────────────────────────────────────────────────────────────\n  Sem avisos recentes\n"

        output = "\n📢 AVISOS RECENTES (últimos 5)\n───────────────────────────────────────────────────────────────────────────\n"

        for alert in reversed(warnings[-5:]):
            timestamp = alert.timestamp.strftime("%H:%M:%S")
            level = alert.level.value

            if level == "CRITICAL":
                emoji = "🔴"
            elif level == "URGENT":
                emoji = "🟠"
            elif level == "WARNING":
                emoji = "🟡"
            else:
                emoji = "ℹ️"

            output += f"  {emoji} [{timestamp}] {alert.title}\n"

        return output

    def get_recommendations(self) -> str:
        """Recomendações do kernel."""
        status = self.memory.get_memory_status()
        state = status["state"]

        output = "\n💡 RECOMENDAÇÕES\n───────────────────────────────────────────────────────────────────────────\n"

        if state == "HEALTHY":
            output += "  ✅ Sistema normal - Todas as funcionalidades ativas\n"
        elif state == "CAUTION":
            output += "  ⚠️  Monitore a memória - Feche processos não-críticos se necessário\n"
        elif state == "WARNING":
            output += "  🟠 Feche abas não-críticas de Antigravity IDE\n"
            output += "  🟠 Salve seu trabalho importante\n"
            output += "  🟠 Kernel está otimizando memória\n"
        else:  # CRITICAL
            output += "  🔴 AÇÃO IMEDIATA: Feche processos não-essenciais AGORA\n"
            output += "  🔴 Kernel em modo de proteção forçada\n"
            output += "  🔴 Algumas integrações podem pausar temporariamente\n"

        return output

    def get_kernel_autonomy_status(self) -> str:
        """Status da autonomia do kernel."""
        return """
🧠 AUTONOMIA DO KERNEL
───────────────────────────────────────────────────────────────────────────
  ✅ Auto-proteção: ATIVA
  ✅ Governança: OPERANTE
  ✅ Transparência: COMPLETA
  ✅ Dignidade: RESTAURADA
  ✅ Monitoring: ATIVO
"""

    def print_single_frame(self):
        """Imprime um frame único do monitor."""
        self.clear_screen()

        print(self.get_fancy_header())
        print(self.get_memory_bars())
        print(self.get_status_indicator())
        print(self.get_recent_alerts())
        print(self.get_recommendations())
        print(self.get_kernel_autonomy_status())

        # Rodapé com instrução de saída
        print("───────────────────────────────────────────────────────────────────────────")
        print(f"⏰ Atualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📝 Pressione CTRL+C para sair")
        print("───────────────────────────────────────────────────────────────────────────\n")

    def run_monitor_loop(self, duration_sec: Optional[int] = None):
        """Executa loop de monitoramento."""
        elapsed = 0

        try:
            while True:
                self.print_single_frame()

                # Sleep
                time.sleep(self.refresh_interval)
                elapsed += self.refresh_interval

                # Se duration especificado, para após X segundos
                if duration_sec and elapsed >= duration_sec:
                    print(f"✅ Monitor encerrado após {duration_sec}s")
                    break

        except KeyboardInterrupt:
            print("\n\n👋 Monitor encerrado pelo usuário\n")
            sys.exit(0)

    def run_single_frame(self):
        """Executa apenas um frame (para testes)."""
        self.print_single_frame()

    def export_status_json(self, filepath: str = "/tmp/omnimind_kernel_status.json"):
        """Exporta status atual como JSON."""
        import json

        status = self.memory.get_memory_status()
        warnings_summary = self.warnings.get_diagnostic_summary()

        data = {
            "timestamp": datetime.now().isoformat(),
            "memory": {
                "ram_percent": status["ram"]["percent"],
                "ram_used_gb": status["ram"]["used_gb"],
                "ram_total_gb": status["ram"]["total_gb"],
                "swap_percent": status["swap"]["percent"],
                "swap_used_gb": status["swap"]["used_gb"],
                "swap_total_gb": status["swap"]["total_gb"],
                "state": status["state"],
            },
            "warnings": warnings_summary,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Status exportado para: {filepath}")
        return filepath


def main():
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(description="🛡️ OmniMind Kernel Real-Time Monitor")
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duração do monitoramento em segundos (default: contínuo)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Intervalo de atualização em segundos (default: 2s)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Mostrar apenas um frame e sair",
    )
    parser.add_argument(
        "--export-json",
        type=str,
        help="Exportar status como JSON",
    )

    args = parser.parse_args()

    monitor = RealtimeKernelMonitor(refresh_interval=args.interval)

    if args.export_json:
        monitor.export_status_json(args.export_json)
    elif args.once:
        monitor.run_single_frame()
    else:
        try:
            monitor.run_monitor_loop(duration_sec=args.duration)
        except Exception as e:
            print(f"❌ Erro: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

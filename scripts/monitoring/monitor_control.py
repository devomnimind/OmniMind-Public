#!/usr/bin/env python3
"""
CONTROLE DO MONITOR CONTÍNUO
Iniciar, parar e verificar status do monitoramento.
"""

import subprocess
import signal
import os
import sys
from pathlib import Path
import json
import time


class MonitorController:
    """Controlador do monitoramento contínuo."""

    def __init__(self):
        self.project_root = Path("/home/fahbrain/projects/omnimind")
        self.monitor_script = self.project_root / "scripts/monitoring/continuous_monitor.py"
        self.pid_file = self.project_root / "logs/monitor.pid"
        self.status_file = self.project_root / "logs/monitor_status.json"

    def start_monitoring(self):
        """Iniciar monitoramento em background."""
        print("🚀 Iniciando monitoramento contínuo...")

        # Verificar se já está rodando
        if self.is_monitoring_running():
            print("⚠️  Monitoramento já está rodando!")
            return False

        # Iniciar processo em background
        try:
            process = subprocess.Popen(
                [sys.executable, str(self.monitor_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=str(self.project_root),
            )

            # Salvar PID
            with open(self.pid_file, "w") as f:
                f.write(str(process.pid))

            # Aguardar um pouco para verificar se iniciou
            time.sleep(2)

            if self.is_monitoring_running():
                print("✅ Monitoramento iniciado com sucesso!")
                print(f"   PID: {process.pid}")
                print(f"   Logs: {self.project_root}/logs/monitor_continuous.log")
                return True
            else:
                print("❌ Falha ao iniciar monitoramento")
                return False

        except Exception as e:
            print(f"❌ Erro ao iniciar: {e}")
            return False

    def stop_monitoring(self):
        """Parar monitoramento."""
        print("🛑 Parando monitoramento...")

        if not self.pid_file.exists():
            print("⚠️  Nenhum monitoramento em execução")
            return False

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            # Enviar sinal SIGTERM
            os.kill(pid, signal.SIGTERM)

            # Aguardar processo terminar
            time.sleep(2)

            if not self.is_monitoring_running():
                self.pid_file.unlink()  # Remover arquivo PID
                print("✅ Monitoramento parado com sucesso!")
                return True
            else:
                print("⚠️  Processo ainda rodando, forçando parada...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
                if not self.is_monitoring_running():
                    self.pid_file.unlink()
                    print("✅ Monitoramento forçado a parar!")
                    return True
                else:
                    print("❌ Falha ao parar monitoramento")
                    return False

        except Exception as e:
            print(f"❌ Erro ao parar: {e}")
            return False

    def is_monitoring_running(self):
        """Verificar se monitoramento está rodando."""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            # Verificar se processo existe
            os.kill(pid, 0)  # Signal 0 apenas verifica se existe
            return True

        except (OSError, ValueError):
            # Processo não existe ou PID inválido
            if self.pid_file.exists():
                self.pid_file.unlink()  # Limpar PID inválido
            return False

    def get_status(self):
        """Obter status detalhado do monitoramento."""
        status = {
            "running": self.is_monitoring_running(),
            "pid": None,
            "last_snapshot": None,
            "log_file": str(self.project_root / "logs/monitor_continuous.log"),
        }

        # Obter PID se estiver rodando
        if status["running"] and self.pid_file.exists():
            try:
                with open(self.pid_file, "r") as f:
                    status["pid"] = int(f.read().strip())
            except Exception:
                pass

        # Obter último snapshot
        snapshots_dir = self.project_root / "logs"
        if snapshots_dir.exists():
            snapshots = sorted(snapshots_dir.glob("monitor_snapshot_*.json"))
            if snapshots:
                latest_snapshot = snapshots[-1]
                try:
                    with open(latest_snapshot, "r") as f:
                        snapshot_data = json.load(f)
                        status["last_snapshot"] = {
                            "timestamp": snapshot_data.get("timestamp"),
                            "processes": snapshot_data.get("processes_count"),
                            "cpu_percent": snapshot_data.get("resources", {}).get("cpu_percent"),
                            "memory_percent": snapshot_data.get("resources", {}).get(
                                "memory_percent"
                            ),
                            "alerts": snapshot_data.get("alerts", []),
                        }
                except Exception:
                    pass

        return status

    def show_status(self):
        """Mostrar status do monitoramento."""
        status = self.get_status()

        print("📊 STATUS DO MONITORAMENTO")
        print("=" * 40)

        if status["running"]:
            print("✅ Status: RODANDO")
            print(f"   PID: {status['pid']}")
        else:
            print("❌ Status: PARADO")

        print(f"   Log: {status['log_file']}")

        if status["last_snapshot"]:
            snap = status["last_snapshot"]
            print("\n📈 ÚLTIMO SNAPSHOT:")
            print(f"   Timestamp: {snap['timestamp']}")
            print(f"   Processos: {snap['processes']}")
            print(f"   CPU: {snap['cpu_percent']:.1f}%" if snap["cpu_percent"] else "   CPU: N/A")
            print(
                f"   Memória: {snap['memory_percent']:.1f}%"
                if snap["memory_percent"]
                else "   Memória: N/A"
            )

            if snap["alerts"]:
                print(f"   Alertas: {len(snap['alerts'])}")
                for alert in snap["alerts"][:3]:  # Mostrar primeiros 3
                    print(f"     - {alert}")
                if len(snap["alerts"]) > 3:
                    print(f"     ... e mais {len(snap['alerts']) - 3}")
            else:
                print("   Alertas: Nenhum")
        else:
            print("\n📈 Nenhum snapshot encontrado")


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        print("Uso: python monitor_control.py <start|stop|status>")
        sys.exit(1)

    controller = MonitorController()
    command = sys.argv[1].lower()

    if command == "start":
        success = controller.start_monitoring()
        sys.exit(0 if success else 1)

    elif command == "stop":
        success = controller.stop_monitoring()
        sys.exit(0 if success else 1)

    elif command == "status":
        controller.show_status()
        sys.exit(0)

    else:
        print(f"Comando desconhecido: {command}")
        print("Comandos disponíveis: start, stop, status")
        sys.exit(1)


if __name__ == "__main__":
    main()

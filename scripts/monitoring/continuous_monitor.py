#!/usr/bin/env python3
"""
MONITOR CONTÍNUO DO OMNIMIND
Monitoramento em tempo real com alertas e logs.
"""

import asyncio
import json
import psutil
import time
from datetime import datetime
from pathlib import Path
import logging
import sys


class OmniMindMonitor:
    """Monitor contínuo do OmniMind."""

    def __init__(self):
        self.project_root = Path("/home/fahbrain/projects/omnimind")
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Configurar logging
        self.setup_logging()

        # Thresholds de alerta
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "processes_count": 50,
            "disk_percent": 90.0,
        }

        # Estado anterior para detectar mudanças
        self.previous_state = {}

    def setup_logging(self):
        """Configurar logging."""
        log_file = self.logs_dir / "monitor_continuous.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
        )
        self.logger = logging.getLogger(__name__)

    async def monitor_processes(self):
        """Monitor de processos OmniMind."""
        omnimind_processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "cmdline"]
        ):
            try:
                cmdline = " ".join(proc.cmdline()) if proc.cmdline() else ""
                name = proc.name().lower()

                # Identificar processos OmniMind
                if (
                    "omnimind" in cmdline.lower()
                    or ("uvicorn" in name and "omnimind" in cmdline)
                    or (".venv/bin/python" in cmdline and "omnimind" in cmdline)
                    or (
                        "node" in name
                        and any(port in cmdline for port in ["3000", "3001", "8000", "8080"])
                    )
                ):

                    omnimind_processes.append(
                        {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "cpu_percent": proc.cpu_percent(),
                            "memory_percent": proc.memory_percent(),
                            "cmdline": cmdline[:100] + "..." if len(cmdline) > 100 else cmdline,
                        }
                    )

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return omnimind_processes

    async def monitor_resources(self):
        """Monitor de recursos."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": memory.percent,
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_used_gb": round(disk.used / (1024**3), 2),
        }

    async def monitor_network(self):
        """Monitor de rede."""
        connections = psutil.net_connections()
        omnimind_ports = [3000, 3001, 8000, 8080]

        omnimind_connections = []
        for conn in connections:
            if conn.laddr and conn.laddr.port in omnimind_ports:
                omnimind_connections.append(
                    {
                        "port": conn.laddr.port,
                        "status": conn.status,
                        "pid": conn.pid,
                    }
                )

        return {
            "omnimind_connections": omnimind_connections,
            "total_connections": len(omnimind_connections),
        }

    def check_alerts(self, processes, resources, network):
        """Verificar alertas."""
        alerts = []

        # CPU alta
        if resources["cpu_percent"] > self.thresholds["cpu_percent"]:
            alerts.append(f"ALERTA: CPU alta ({resources['cpu_percent']:.1f}%)")

        # Memória alta
        if resources["memory_percent"] > self.thresholds["memory_percent"]:
            alerts.append(f"ALERTA: Memória alta ({resources['memory_percent']:.1f}%)")

        # Muitos processos
        if len(processes) > self.thresholds["processes_count"]:
            alerts.append(f"ALERTA: Muitos processos OmniMind ({len(processes)})")

        # Disco cheio
        if resources["disk_percent"] > self.thresholds["disk_percent"]:
            alerts.append(f"ALERTA: Disco quase cheio ({resources['disk_percent']:.1f}%)")

        # Mudanças significativas
        if self.previous_state:
            prev_processes = self.previous_state.get("processes_count", 0)
            if abs(len(processes) - prev_processes) > 10:
                alerts.append(
                    f"MUDANÇA: Processos mudaram de {prev_processes} para {len(processes)}"
                )

        return alerts

    async def save_snapshot(self, processes, resources, network, alerts):
        """Salvar snapshot do estado."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "processes_count": len(processes),
            "resources": resources,
            "network": network,
            "alerts": alerts,
        }

        snapshot_file = self.logs_dir / f"monitor_snapshot_{int(time.time())}.json"
        with open(snapshot_file, "w") as f:
            json.dump(snapshot, f, indent=2)

        # Manter apenas últimos 10 snapshots
        snapshots = sorted(self.logs_dir.glob("monitor_snapshot_*.json"))
        if len(snapshots) > 10:
            for old_snapshot in snapshots[:-10]:
                old_snapshot.unlink()

    async def run_monitoring_cycle(self):
        """Executar um ciclo de monitoramento."""
        try:
            # Coletar dados
            processes = await self.monitor_processes()
            resources = await self.monitor_resources()
            network = await self.monitor_network()

            # Verificar alertas
            alerts = self.check_alerts(processes, resources, network)

            # Log do status
            self.logger.info(
                f"Processos: {len(processes)}, CPU: {resources['cpu_percent']:.1f}%, "
                f"Memória: {resources['memory_percent']:.1f}%, "
                f"Conexões: {network['total_connections']}"
            )

            # Log de alertas
            for alert in alerts:
                self.logger.warning(alert)

            # Salvar snapshot
            await self.save_snapshot(processes, resources, network, alerts)

            # Atualizar estado anterior
            self.previous_state = {
                "processes_count": len(processes),
                "resources": resources,
                "network": network,
            }

        except Exception as e:
            self.logger.error(f"Erro no ciclo de monitoramento: {e}")

    async def run_continuous_monitoring(self, interval=30):
        """Executar monitoramento contínuo."""
        self.logger.info("Iniciando monitoramento contínuo do OmniMind")
        self.logger.info(f"Intervalo: {interval} segundos")

        while True:
            await self.run_monitoring_cycle()
            await asyncio.sleep(interval)


async def main():
    """Função principal."""
    monitor = OmniMindMonitor()

    # Executar monitoramento contínuo
    await monitor.run_continuous_monitoring(interval=30)  # 30 segundos


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)

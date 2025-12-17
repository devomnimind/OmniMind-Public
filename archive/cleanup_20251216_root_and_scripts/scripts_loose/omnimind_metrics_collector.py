#!/usr/bin/env python3
"""
OmniMind Metrics Collection Service
====================================

Coleta métricas com intervalo configurável:
- Críticas: a cada 2 minutos (Phi, backends status)
- Secundárias: a cada 5 minutos (Memory, CPU, Disk)
- Limpeza: a cada 10 minutos

Uso:
    python3 scripts/omnimind_metrics_collector.py [--daemon] [--critical-interval 120] [--secondary-interval 300]
"""

import json
import logging
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class MetricsCollector:
    def __init__(
        self,
        project_root="/home/fahbrain/projects/omnimind",
        critical_interval=120,  # 2 minutos
        secondary_interval=300,  # 5 minutos
    ):
        self.root = Path(project_root)
        self.metrics_file = self.root / "data/long_term_logs/omnimind_metrics.jsonl"
        self.critical_interval = critical_interval
        self.secondary_interval = secondary_interval

        # Portas críticas (Phi collection)
        self.critical_ports = {
            8000: "Backend-Primary",
            8080: "Backend-Secondary",
        }

        # Portas secundárias
        self.secondary_ports = {
            3001: "Backend-Fallback",
            3000: "Frontend",
            6379: "Redis",
        }

        # Timestamps de última coleta
        self.last_critical = 0
        self.last_secondary = 0

        logger.info(f"MetricsCollector iniciado")
        logger.info(f"  Intervalo crítico: {critical_interval}s")
        logger.info(f"  Intervalo secundário: {secondary_interval}s")

    def check_port(self, port, timeout=2):
        """Verifica se porta está acessível"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            return result == 0
        except:
            return False

    def collect_critical_metrics(self):
        """Coleta métricas críticas (Phi, status dos backends)"""
        timestamp = datetime.now(timezone.utc).isoformat()

        # Status dos backends críticos
        backend_status = {}
        for port, name in self.critical_ports.items():
            backend_status[name] = self.check_port(port)

        # Extrair último Phi do audit chain
        phi_value = self._get_latest_phi()

        metric_entry = {
            "timestamp": timestamp,
            "type": "CRITICAL_METRICS",
            "data": {
                "backends": backend_status,
                "phi": phi_value,
                "backends_healthy": sum(backend_status.values()),
                "backends_total": len(backend_status),
            },
        }

        self._save_metric(metric_entry)
        logger.info(
            f"✅ Métrica crítica coletada: {backend_status['Backend-Primary']=}, Phi={phi_value:.6f}"
        )

    def collect_secondary_metrics(self):
        """Coleta métricas secundárias (CPU, Memory, Disk)"""
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.5)
            disk = psutil.disk_usage("/")

            metric_entry = {
                "timestamp": timestamp,
                "type": "SYSTEM_HEALTH",
                "data": {
                    "cpu": cpu,
                    "memory": memory.percent,
                    "disk": disk.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                },
            }

            self._save_metric(metric_entry)
            logger.info(
                f"💾 Métrica secundária coletada: CPU={cpu:.1f}%, Mem={memory.percent:.1f}%, Disk={disk.percent:.1f}%"
            )

        except Exception as e:
            logger.error(f"Erro ao coletar métricas secundárias: {e}")

    def _get_latest_phi(self):
        """Extrai último valor de Phi do audit chain"""
        try:
            audit_chain_file = self.root / "logs/audit_chain.log"
            if not audit_chain_file.exists():
                return 0.0

            phi_value = 0.0
            with open(audit_chain_file) as f:
                # Ler últimas 100 linhas
                lines = f.readlines()
                for line in lines[-100:]:
                    try:
                        entry = json.loads(line)
                        if entry.get("action") == "module_metric":
                            details = entry.get("details", {})
                            if "phi" in str(details):
                                value = details.get("value")
                                if isinstance(value, (int, float)):
                                    phi_value = float(value)
                    except:
                        pass

            return phi_value
        except:
            return 0.0

    def _save_metric(self, metric):
        """Salva métrica no arquivo"""
        try:
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, "a") as f:
                f.write(json.dumps(metric) + "\n")
        except Exception as e:
            logger.error(f"Erro ao salvar métrica: {e}")

    def run_collection_cycle(self):
        """Executa ciclo de coleta baseado em intervalos"""
        now = time.time()

        # Coletar métricas críticas
        if now - self.last_critical >= self.critical_interval:
            self.collect_critical_metrics()
            self.last_critical = now

        # Coletar métricas secundárias
        if now - self.last_secondary >= self.secondary_interval:
            self.collect_secondary_metrics()
            self.last_secondary = now

    def daemon_mode(self, check_interval=10):
        """Executa em modo daemon"""
        logger.info(f"🚀 Daemon iniciado (verificação a cada {check_interval}s)")

        try:
            while True:
                try:
                    self.run_collection_cycle()
                except Exception as e:
                    logger.error(f"Erro no ciclo de coleta: {e}")

                time.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("⏹️  Daemon interrompido pelo usuário")

    def generate_report(self):
        """Gera relatório de coleta"""
        if not self.metrics_file.exists():
            print("Nenhuma métrica coletada ainda")
            return

        with open(self.metrics_file) as f:
            lines = f.readlines()

        print("\n" + "=" * 80)
        print("            OMNIMIND METRICS COLLECTION REPORT")
        print("=" * 80)
        print(f"Total metrics: {len(lines)}")

        # Últimas 5 métricas
        print("\nLatest 5 metrics:")
        print("-" * 80)
        for line in lines[-5:]:
            try:
                metric = json.loads(line)
                mtype = metric.get("type")
                timestamp = metric.get("timestamp", "")[-8:]
                print(f"  [{timestamp}] {mtype}: {metric.get('data', {})}")
            except:
                pass

        print("=" * 80 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="OmniMind Metrics Collection Service")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument(
        "--critical-interval", type=int, default=120, help="Critical metrics interval (seconds)"
    )
    parser.add_argument(
        "--secondary-interval", type=int, default=300, help="Secondary metrics interval (seconds)"
    )
    parser.add_argument(
        "--check-interval", type=int, default=10, help="Daemon check interval (seconds)"
    )
    parser.add_argument("--report", action="store_true", help="Show metrics report")
    parser.add_argument("--project-root", default="/home/fahbrain/projects/omnimind")

    args = parser.parse_args()

    collector = MetricsCollector(
        project_root=args.project_root,
        critical_interval=args.critical_interval,
        secondary_interval=args.secondary_interval,
    )

    if args.report:
        collector.generate_report()
    elif args.daemon:
        collector.daemon_mode(args.check_interval)
    else:
        # Coleta única
        collector.run_collection_cycle()
        print("✅ Coleta executada")

    return 0


if __name__ == "__main__":
    sys.exit(main())

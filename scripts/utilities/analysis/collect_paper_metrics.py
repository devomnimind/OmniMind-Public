#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Sistema de Coleta de Métricas para Publicações Científicas - OmniMind
Coleta métricas essenciais para validação de papers científicos por 2 horas.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import psutil

# Adicionar diretório raiz ao path para permitir imports de src
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/metrics_collection.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Coletor de métricas para publicações científicas.
    Coleta dados por 2 horas com intervalo de 30 segundos.
    """

    def __init__(self, collection_duration: int = 7200):  # 2 horas em segundos
        self.collection_duration = collection_duration
        self.interval = 30  # segundos
        self.metrics_data: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.output_file = Path("data/metrics_collection_paper.jsonl")

        # Criar diretório se não existir
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        # Inicializar componentes
        self._init_components()

    def _init_components(self):
        """Inicializar componentes do sistema de métricas."""
        try:
            from src.audit.immutable_audit import get_audit_system

            self.audit_system = get_audit_system()
            logger.info("Sistema de auditoria inicializado")
        except Exception as e:
            logger.warning(f"Sistema de auditoria não disponível: {e}")
            self.audit_system = None

        # Remover inicialização de system_metrics que não existe
        self.system_metrics = None

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Coletar métricas básicas do sistema."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memória
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent,
            }

            # Disco
            disk = psutil.disk_usage("/")
            disk_info = {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_gb": disk.used / (1024**3),
                "percent": disk.percent,
            }

            # GPU (se disponível) - simplificado
            gpu_info = {}
            try:
                # Verificar se há GPU NVIDIA disponível
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,memory.used",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split("\n")
                    if lines and "," in lines[0]:
                        parts = lines[0].split(", ")
                        if len(parts) >= 3:
                            name = parts[0]
                            total_mb = int(parts[1])
                            used_mb = int(parts[2])
                            gpu_info = {
                                "name": name,
                                "memory_total_mb": total_mb,
                                "memory_used_mb": used_mb,
                                "memory_percent": (
                                    (used_mb / total_mb) * 100 if total_mb > 0 else 0
                                ),
                            }
            except Exception:
                pass  # GPU não disponível ou erro

            # Rede
            network = psutil.net_io_counters()
            network_info = {
                "bytes_sent_mb": network.bytes_sent / (1024**2),
                "bytes_recv_mb": network.bytes_recv / (1024**2),
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }

            return {
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "freq_mhz": cpu_freq.current if cpu_freq else None,
                },
                "memory": memory_info,
                "disk": disk_info,
                "gpu": gpu_info,
                "network": network_info,
            }

        except Exception as e:
            logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return {"error": str(e)}

    def collect_audit_metrics(self) -> Dict[str, Any]:
        """Coletar métricas do sistema de auditoria."""
        if not self.audit_system:
            return {"available": False}

        try:
            # Obter resumo da auditoria
            summary = self.audit_system.get_audit_summary()

            # Calcular taxa de eventos por segundo
            current_time = time.time()
            elapsed_time = current_time - self.start_time
            events_per_second = (
                summary.get("total_events", 0) / elapsed_time if elapsed_time > 0 else 0
            )

            return {
                "available": True,
                "total_events": summary.get("total_events", 0),
                "events_per_second": events_per_second,
                "chain_integrity": summary.get("chain_integrity", {}).get("valid", False),
                "log_size_bytes": summary.get("log_size_bytes", 0),
                "last_hash": summary.get("last_hash", "")[:16]
                + "...",  # Apenas prefixo para segurança
            }

        except Exception as e:
            logger.error(f"Erro ao coletar métricas de auditoria: {e}")
            return {"error": str(e)}

    def collect_security_metrics(self) -> Dict[str, Any]:
        """Coletar métricas de segurança."""
        try:
            security_metrics = {
                "dlp_violations": 0,
                "security_alerts": 0,
                "integrity_checks": 0,
            }

            # Verificar logs de segurança
            security_log = Path("logs/security_events.log")
            if security_log.exists():
                with open(security_log, "r") as f:
                    content = f.read()
                    security_metrics["dlp_violations"] = content.count("dlp.violation")
                    security_metrics["security_alerts"] = content.count("ALERTA")
                    security_metrics["integrity_checks"] = content.count("integridade")

            return security_metrics

        except Exception as e:
            logger.error(f"Erro ao coletar métricas de segurança: {e}")
            return {"error": str(e)}

    def collect_quantum_metrics(self) -> Dict[str, Any]:
        """Coletar métricas quânticas (se aplicável)."""
        try:
            quantum_metrics = {
                "quantum_available": False,
                "simulations_run": 0,
                "quantum_performance": {},
            }

            # Verificar se há componentes quânticos ativos
            quantum_log = Path("logs/quantum_operations.log")
            if quantum_log.exists():
                quantum_metrics["quantum_available"] = True
                with open(quantum_log, "r") as f:
                    content = f.read()
                    quantum_metrics["simulations_run"] = content.count("simulation")

            return quantum_metrics

        except Exception as e:
            logger.error(f"Erro ao coletar métricas quânticas: {e}")
            return {"error": str(e)}

    def collect_agent_metrics(self) -> Dict[str, Any]:
        """Coletar métricas de agentes."""
        try:
            agent_metrics = {
                "agents_active": 0,
                "responses_generated": 0,
                "average_response_time_ms": 0,
            }

            # Verificar logs de agentes
            agent_log = Path("logs/agent_operations.log")
            if agent_log.exists():
                with open(agent_log, "r") as f:
                    content = f.read()
                    agent_metrics["responses_generated"] = content.count("response")
                    # Contar agentes únicos mencionados
                    import re

                    agents = set(re.findall(r"agent[_-](\w+)", content, re.IGNORECASE))
                    agent_metrics["agents_active"] = len(agents)

            return agent_metrics

        except Exception as e:
            logger.error(f"Erro ao coletar métricas de agentes: {e}")
            return {"error": str(e)}

    def collect_single_sample(self) -> Dict[str, Any]:
        """Coletar uma amostra completa de métricas."""
        timestamp = datetime.now(timezone.utc).isoformat()
        elapsed_time = time.time() - self.start_time

        sample = {
            "timestamp": timestamp,
            "elapsed_seconds": elapsed_time,
            "system": self.collect_system_metrics(),
            "audit": self.collect_audit_metrics(),
            "security": self.collect_security_metrics(),
            "quantum": self.collect_quantum_metrics(),
            "agents": self.collect_agent_metrics(),
        }

        return sample

    def save_sample(self, sample: Dict[str, Any]):
        """Salvar amostra no arquivo de saída."""
        try:
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(sample, ensure_ascii=False) + "\n")

            self.metrics_data.append(sample)

            # Log de progresso
            elapsed = sample["elapsed_seconds"]
            _progress = (elapsed / self.collection_duration) * 100
            logger.info(".1f")

        except Exception as e:
            logger.error(f"Erro ao salvar amostra: {e}")

    def run_collection(self):
        """Executar coleta de métricas por 2 horas."""
        logger.info("🚀 Iniciando coleta de métricas para publicações científicas")
        logger.info(f"Duração: {self.collection_duration} segundos")
        logger.info(f"Intervalo: {self.interval} segundos")
        logger.info(f"Arquivo de saída: {self.output_file}")

        sample_count = 0
        _max_samples = self.collection_duration // self.interval

        while time.time() - self.start_time < self.collection_duration:
            try:
                # Coletar amostra
                sample = self.collect_single_sample()
                self.save_sample(sample)
                sample_count += 1

                # Calcular tempo até próxima coleta
                next_collection = self.start_time + (sample_count * self.interval)
                sleep_time = max(0, next_collection - time.time())

                if sleep_time > 0:
                    time.sleep(sleep_time)

            except KeyboardInterrupt:
                logger.info("⏹️ Coleta interrompida pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro durante coleta: {e}")
                time.sleep(self.interval)

        # Relatório final
        logger.info("✅ Coleta de métricas concluída!")
        logger.info(f"Amostras coletadas: {sample_count}")
        logger.info(f"Arquivo final: {self.output_file}")
        logger.info(f"Tamanho do arquivo: {self.output_file.stat().st_size} bytes")

        # Gerar relatório de resumo
        self.generate_summary_report()

    def generate_summary_report(self):
        """Gerar relatório de resumo das métricas coletadas."""
        if not self.metrics_data:
            logger.warning("Nenhuma métrica coletada para gerar relatório")
            return

        try:
            # Calcular estatísticas básicas
            cpu_usage = [
                s["system"].get("cpu", {}).get("percent", 0)
                for s in self.metrics_data
                if "cpu" in s["system"]
            ]
            memory_usage = [
                s["system"].get("memory", {}).get("percent", 0)
                for s in self.metrics_data
                if "memory" in s["system"]
            ]

            summary = {
                "collection_info": {
                    "start_time": (
                        self.metrics_data[0]["timestamp"] if self.metrics_data else None
                    ),
                    "end_time": (self.metrics_data[-1]["timestamp"] if self.metrics_data else None),
                    "duration_seconds": self.collection_duration,
                    "samples_collected": len(self.metrics_data),
                    "interval_seconds": self.interval,
                },
                "system_stats": {
                    "cpu_avg_percent": (sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0),
                    "cpu_max_percent": max(cpu_usage) if cpu_usage else 0,
                    "memory_avg_percent": (
                        sum(memory_usage) / len(memory_usage) if memory_usage else 0
                    ),
                    "memory_max_percent": max(memory_usage) if memory_usage else 0,
                },
                "audit_stats": {
                    "total_events": (
                        self.metrics_data[-1]["audit"].get("total_events", 0)
                        if self.metrics_data
                        else 0
                    ),
                    "chain_integrity": all(
                        s["audit"].get("chain_integrity", False) for s in self.metrics_data
                    ),
                    "avg_events_per_second": (
                        sum(s["audit"].get("events_per_second", 0) for s in self.metrics_data)
                        / len(self.metrics_data)
                        if self.metrics_data
                        else 0
                    ),
                },
                "security_stats": {
                    "total_dlp_violations": sum(
                        s["security"].get("dlp_violations", 0) for s in self.metrics_data
                    ),
                    "total_security_alerts": sum(
                        s["security"].get("security_alerts", 0) for s in self.metrics_data
                    ),
                },
            }

            # Salvar relatório
            summary_file = Path("reports/metrics_collection_summary.json")
            summary_file.parent.mkdir(parents=True, exist_ok=True)

            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info(f"📊 Relatório de resumo salvo em: {summary_file}")

        except Exception as e:
            logger.error(f"Erro ao gerar relatório de resumo: {e}")


def main():
    """Função principal para executar coleta de métricas."""
    print("🔬 OmniMind - Coleta de Métricas para Publicações Científicas")
    print("=" * 60)
    print("Este script irá coletar métricas essenciais por 2 horas")
    print("para validação de nossas primeiras publicações científicas.")
    print()
    print("Métricas coletadas:")
    print("• Performance do sistema (CPU, memória, GPU, disco)")
    print("• Métricas de auditoria (eventos, integridade)")
    print("• Métricas de agentes (respostas, performance)")
    print("• Métricas de segurança (DLP, alertas)")
    print("• Métricas quânticas (simulações)")
    print()
    print("Pressione Ctrl+C para interromper a coleta antecipadamente")
    print("=" * 60)

    # Iniciar coleta
    collector = MetricsCollector()
    collector.run_collection()


if __name__ == "__main__":
    main()

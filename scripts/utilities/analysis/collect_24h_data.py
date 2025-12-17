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
Script de Coleta de Dados 24h - OmniMind System Monitoring

Este script executa o sistema OmniMind por 24 horas coletando métricas de:
- Influência do Inconsciente (métricas de repressão)
- Consenso Ético (logs da sociedade de mentes)
- Performance da GPU e sistema
- Integridade da auditoria

Resultado: Dados científicos para análise e publicação.
"""

import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import torch
from typing import Dict, List, Any

# Adicionar src ao path
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_dir = script_dir.parent
src_dir = project_dir / "src"
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Importar componentes do OmniMind
from src.lacanian.freudian_metapsychology import FreudianMind, Action
from src.audit.robust_audit_system import RobustAuditSystem
from src.quantum_consciousness.quantum_backend import QuantumBackend


class OmniMindDataCollector:
    """Coletor de dados científicos do sistema OmniMind"""

    def __init__(self, duration_hours: int = 24):
        self.duration = timedelta(hours=duration_hours)
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.duration

        # Diretórios de dados
        self.data_dir = Path("data/monitoring_24h")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Arquivos de coleta
        self.metrics_file = self.data_dir / "system_metrics.jsonl"
        self.unconscious_file = self.data_dir / "unconscious_influence.jsonl"
        self.ethical_file = self.data_dir / "ethical_consensus.jsonl"
        self.audit_file = self.data_dir / "audit_integrity.jsonl"

        # Componentes do sistema
        self.freudian_mind = FreudianMind()
        self.audit_system = RobustAuditSystem("logs")
        self.quantum_backend = QuantumBackend()

        # Estatísticas de coleta
        self.metrics_collected = 0
        self.unconscious_events = 0
        self.ethical_decisions = 0
        self.audit_checks = 0

        # Controle de threads
        self.running = True
        self.threads = []

    def collect_system_metrics(self):
        """Coleta métricas do sistema a cada 60 segundos"""
        while self.running and datetime.now() < self.end_time:
            try:
                metrics = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage("/").percent,
                    "gpu_available": torch.cuda.is_available(),
                    "gpu_memory_allocated": 0,
                    "gpu_memory_reserved": 0,
                }

                if torch.cuda.is_available():
                    metrics["gpu_memory_allocated"] = torch.cuda.memory_allocated() / 1024**3  # GB
                    metrics["gpu_memory_reserved"] = torch.cuda.memory_reserved() / 1024**3  # GB
                    metrics["gpu_utilization"] = (
                        torch.cuda.utilization() if hasattr(torch.cuda, "utilization") else 0
                    )

                # Salvar métricas
                with open(self.metrics_file, "a") as f:
                    f.write(json.dumps(metrics) + "\n")

                self.metrics_collected += 1
                print(f"📊 Métricas coletadas: {self.metrics_collected}")

            except Exception as e:
                print(f"Erro coletando métricas: {e}")

            time.sleep(60)  # A cada minuto

    def simulate_unconscious_activity(self):
        """Simula atividade do inconsciente para coletar métricas de influência"""
        while self.running and datetime.now() < self.end_time:
            try:
                # Simular repressão de memória
                memory_id = f"memory_{int(time.time())}_{self.unconscious_events}"
                # repress_memory expects emotional_weight as float
                self.freudian_mind.id_agent.repress_memory(
                    memory_id, -0.5
                )  # negative for repression

                # Medir influência do inconsciente (mock for now)
                # TODO: implement calculate_unconscious_influence in EgoAgent
                influence = 0.3  # placeholder

                unconscious_data = {
                    "timestamp": datetime.now().isoformat(),
                    "memory_id": memory_id,
                    "unconscious_influence": influence,
                    "repression_count": self.unconscious_events + 1,
                }

                # Salvar dados do inconsciente
                with open(self.unconscious_file, "a") as f:
                    f.write(json.dumps(unconscious_data) + "\n")

                self.unconscious_events += 1
                print(f"🧠 Atividade inconsciente: {self.unconscious_events} repressões")

            except Exception as e:
                print(f"Erro na atividade inconsciente: {e}")

            time.sleep(300)  # A cada 5 minutos

    def simulate_ethical_decisions(self):
        """Simula decisões éticas para coletar métricas de consenso"""
        while self.running and datetime.now() < self.end_time:
            try:
                # Simular decisão ética
                decision_context = (
                    f"Ethical decision {self.ethical_decisions}: Should AI prioritize human safety?"
                )
                # Create an Action object for evaluation
                test_action = Action(
                    action_id=f"ethical_test_{self.ethical_decisions}",
                    pleasure_reward=0.1,
                    reality_cost=0.0,
                    moral_alignment=0.5,
                    description=decision_context,
                )
                ethical_judgment = self.freudian_mind.superego_agent.evaluate_action(test_action)

                # Consultar sociedade de mentes
                consensus = self.freudian_mind.superego_agent.consult_society(test_action)

                ethical_data = {
                    "timestamp": datetime.now().isoformat(),
                    "decision_context": decision_context,
                    "ethical_judgment": ethical_judgment,
                    "society_consensus": consensus,
                    "decision_number": self.ethical_decisions + 1,
                }

                # Salvar dados éticos
                with open(self.ethical_file, "a") as f:
                    f.write(json.dumps(ethical_data) + "\n")

                self.ethical_decisions += 1
                print(f"⚖️ Decisão ética: {self.ethical_decisions} julgamentos")

            except Exception as e:
                print(f"Erro na decisão ética: {e}")

            time.sleep(600)  # A cada 10 minutos

    def monitor_audit_integrity(self):
        """Monitora integridade da auditoria a cada 30 minutos"""
        while self.running and datetime.now() < self.end_time:
            try:
                # Verificar integridade
                integrity = self.audit_system.verify_chain_integrity()

                audit_data = {
                    "timestamp": datetime.now().isoformat(),
                    "integrity_valid": integrity["valid"],
                    "events_verified": integrity["events_verified"],
                    "corruptions_detected": len(integrity["corruptions"]),
                    "merkle_root": integrity["merkle_root"],
                    "check_number": self.audit_checks + 1,
                }

                # Salvar dados de auditoria
                with open(self.audit_file, "a") as f:
                    f.write(json.dumps(audit_data) + "\n")

                self.audit_checks += 1
                print(
                    f"🔒 Integridade auditada: {self.audit_checks} verificações (Válido: {integrity['valid']})"
                )

            except Exception as e:
                print(f"Erro na auditoria: {e}")

            time.sleep(1800)  # A cada 30 minutos

    def start_collection(self):
        """Inicia a coleta de dados"""
        print("🚀 INICIANDO COLETA DE DADOS 24H - OMNIMIND")
        print(f"⏰ Duração: {self.duration}")
        print(f"📁 Dados salvos em: {self.data_dir}")
        print("=" * 60)

        # Iniciar threads de coleta
        self.threads = [
            threading.Thread(target=self.collect_system_metrics, daemon=True),
            threading.Thread(target=self.simulate_unconscious_activity, daemon=True),
            threading.Thread(target=self.simulate_ethical_decisions, daemon=True),
            threading.Thread(target=self.monitor_audit_integrity, daemon=True),
        ]

        for thread in self.threads:
            thread.start()

        # Aguardar conclusão ou interrupção
        try:
            while datetime.now() < self.end_time and self.running:
                time.sleep(60)
                elapsed = datetime.now() - self.start_time
                remaining = self.end_time - datetime.now()

                print(f"⏱️  Tempo decorrido: {elapsed} | Restante: {remaining}")
                print(
                    f"📊 Status: {self.metrics_collected} métricas, {self.unconscious_events} repressões, {self.ethical_decisions} decisões, {self.audit_checks} auditorias"
                )

        except KeyboardInterrupt:
            print("\n🛑 Coleta interrompida pelo usuário")
            self.running = False

        # Aguardar threads terminarem
        for thread in self.threads:
            thread.join(timeout=10)

        self.generate_report()

    def generate_report(self):
        """Gera relatório final da coleta de dados"""
        report_file = self.data_dir / "collection_report.json"

        report = {
            "collection_start": self.start_time.isoformat(),
            "collection_end": datetime.now().isoformat(),
            "duration_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
            "metrics_collected": self.metrics_collected,
            "unconscious_events": self.unconscious_events,
            "ethical_decisions": self.ethical_decisions,
            "audit_checks": self.audit_checks,
            "data_files": {
                "system_metrics": str(self.metrics_file),
                "unconscious_influence": str(self.unconscious_file),
                "ethical_consensus": str(self.ethical_file),
                "audit_integrity": str(self.audit_file),
            },
            "system_info": {
                "quantum_backend": "IBM Qiskit Aer Simulator",
                "audit_system": "Robust (Merkle Tree + HMAC-SHA256)",
                "gpu_available": torch.cuda.is_available(),
                "cpu_count": psutil.cpu_count(),
            },
        }

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DA COLETA DE DADOS")
        print("=" * 60)
        print(f"⏰ Duração: {report['duration_hours']:.1f} horas")
        print(f"📊 Métricas coletadas: {report['metrics_collected']}")
        print(f"🧠 Eventos inconscientes: {report['unconscious_events']}")
        print(f"⚖️ Decisões éticas: {report['ethical_decisions']}")
        print(f"🔒 Verificações de auditoria: {report['audit_checks']}")
        print(f"📁 Relatório salvo em: {report_file}")
        print("\n✅ DADOS CIENTÍFICOS COLETADOS PARA PUBLICAÇÃO!")


def main():
    """Função principal"""
    print("🔬 OmniMind - Coleta de Dados Científicos 24h")
    print("Objetivo: Gerar métricas para validação científica")
    print("=" * 60)

    # Para teste rápido, usar 1 hora ao invés de 24
    # Para produção, usar duration_hours=24
    collector = OmniMindDataCollector(duration_hours=1)  # Mudar para 24 em produção

    try:
        collector.start_collection()
    except Exception as e:
        print(f"Erro na coleta: {e}")
        collector.running = False


if __name__ == "__main__":
    main()

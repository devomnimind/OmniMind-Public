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
Monitor de Integridade do Sistema de Auditoria Robusta

Este script monitora continuamente o estado de integridade do sistema,
alertando sobre problemas e executando ações corretivas automaticamente.

Funcionalidades:
- ✅ Monitoramento em tempo real da integridade
- ✅ Alertas automáticos por email/Slack
- ✅ Ações corretivas automáticas
- ✅ Relatórios de saúde do sistema
- ✅ Validação de métricas GPU
"""

import json
import logging
import smtplib
import sys
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional

import psutil
import requests

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.audit.robust_audit_system import RobustAuditSystem


class IntegrityMonitor:
    """Monitor de integridade do sistema de auditoria"""

    def __init__(self, log_dir: str = "~/projects/omnimind/logs"):
        self.log_dir = Path(log_dir).expanduser()
        self.monitor_dir = self.log_dir / "monitoring"
        self.monitor_dir.mkdir(exist_ok=True)

        self.monitor_log = self.monitor_dir / "integrity_monitor.log"
        self.alerts_log = self.monitor_dir / "alerts_history.log"
        self.health_reports_dir = self.monitor_dir / "health_reports"

        self.health_reports_dir.mkdir(exist_ok=True)

        # Configurações de monitoramento
        self.check_interval = 60  # 1 minuto
        self.alert_cooldown = 300  # 5 minutos entre alertas do mesmo tipo
        self.max_alerts_per_hour = 10

        # Estado do monitor
        self.last_alerts: Dict[str, float] = {}
        self.alerts_this_hour = 0
        self.last_hour_reset = time.time()

        # Configurações de alertas (personalizar)
        self.alert_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "alerts@omnimind.ai",
                "password": "",  # Configurar
                "recipients": ["admin@omnimind.ai"],
            },
            "slack": {
                "enabled": False,
                "webhook_url": "",  # Configurar
                "channel": "#security-alerts",
            },
        }

        # Sistema de auditoria
        self.audit_system: Optional[RobustAuditSystem] = None

        self._setup_logging()

    def _setup_logging(self):
        """Configurar logging do monitor"""
        self.logger = logging.getLogger("IntegrityMonitor")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.monitor_log)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Também log no console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _get_audit_system(self) -> RobustAuditSystem:
        """Obter instância do sistema de auditoria"""
        if self.audit_system is None:
            self.audit_system = RobustAuditSystem(str(self.log_dir))
        return self.audit_system

    def _reset_hourly_alerts(self):
        """Resetar contador de alertas por hora"""
        current_time = time.time()
        if current_time - self.last_hour_reset >= 3600:
            self.alerts_this_hour = 0
            self.last_hour_reset = current_time

    def _can_send_alert(self, alert_type: str) -> bool:
        """Verificar se pode enviar alerta (respeitando cooldown)"""
        self._reset_hourly_alerts()

        if self.alerts_this_hour >= self.max_alerts_per_hour:
            return False

        last_alert = self.last_alerts.get(alert_type, 0)
        if time.time() - last_alert < self.alert_cooldown:
            return False

        return True

    def _send_alert(self, title: str, message: str, level: str = "warning"):
        """Enviar alerta por todos os canais configurados"""
        alert_type = f"{level}_{title.lower().replace(' ', '_')}"

        if not self._can_send_alert(alert_type):
            self.logger.info(f"Alerta '{title}' em cooldown - pulado")
            return

        self.logger.warning(f"🚨 ALERTA {level.upper()}: {title}")
        self.logger.warning(f"   {message}")

        # Registrar alerta
        self._log_alert(title, message, level)

        # Enviar por email
        if self.alert_config["email"]["enabled"]:
            self._send_email_alert(title, message, level)

        # Enviar por Slack
        if self.alert_config["slack"]["enabled"]:
            self._send_slack_alert(title, message, level)

        # Atualizar estado
        self.last_alerts[alert_type] = time.time()
        self.alerts_this_hour += 1

    def _log_alert(self, title: str, message: str, level: str):
        """Registrar alerta no histórico"""
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "title": title,
            "message": message,
        }

        with open(self.alerts_log, "a") as f:
            f.write(json.dumps(alert_data) + "\n")

    def _send_email_alert(self, title: str, message: str, level: str):
        """Enviar alerta por email"""
        try:
            config = self.alert_config["email"]

            msg = MIMEText(
                f"""
ALERTA DE INTEGRIDADE - {level.upper()}

{title}

{message}

Timestamp: {datetime.now().isoformat()}
Sistema: OmniMind Audit Monitor

---
Este é um alerta automático do sistema de monitoramento de integridade.
"""
            )

            msg["Subject"] = f"[OMNIMIND ALERT] {level.upper()}: {title}"
            msg["From"] = config["username"]
            msg["To"] = ", ".join(config["recipients"])

            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["username"], config["password"])
            server.sendmail(config["username"], config["recipients"], msg.as_string())
            server.quit()

            self.logger.info("Email alert sent successfully")

        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")

    def _send_slack_alert(self, title: str, message: str, level: str):
        """Enviar alerta por Slack"""
        try:
            config = self.alert_config["slack"]

            emoji_map = {"critical": "🚨", "high": "⚠️", "medium": "📊", "low": "ℹ️"}

            payload = {
                "channel": config["channel"],
                "username": "OmniMind Audit Monitor",
                "icon_emoji": emoji_map.get(level, "🤖"),
                "text": f"*{title}*\n{message}",
                "attachments": [
                    {
                        "color": "danger" if level == "critical" else "warning",
                        "fields": [
                            {
                                "title": "Timestamp",
                                "value": datetime.now().isoformat(),
                                "short": True,
                            },
                            {"title": "Level", "value": level.upper(), "short": True},
                        ],
                    }
                ],
            }

            response = requests.post(config["webhook_url"], json=payload)
            if response.status_code == 200:
                self.logger.info("Slack alert sent successfully")
            else:
                self.logger.error(f"Slack alert failed: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")

    def _check_integrity(self) -> Dict[str, Any]:
        """Verificar integridade completa do sistema"""
        try:
            system = self._get_audit_system()
            report = system.get_integrity_report()

            # Garantir chaves esperadas se não existirem
            if "gpu_status" not in report:
                report["gpu_status"] = {"utilization": 0.0}

            if "metrics" not in report:
                corruption_count = len(report.get("corruptions", []))
                total_events = report.get("events_verified", 1)  # Evitar div por zero
                report["metrics"] = {
                    "corruption_rate": corruption_count / total_events if total_events > 0 else 0.0,
                    "memory_usage": psutil.virtual_memory().percent / 100.0,
                }

            # Calcular status do sistema
            if not report.get("valid", True):
                # Se inválido, verificar gravidade
                corruptions = report.get("corruptions", [])
                report["system_status"] = "critical" if len(corruptions) > 0 else "high"
            else:
                report["system_status"] = "healthy"

            # Verificações adicionais
            issues = []

            # Verificar se GPU está sendo usada (métricas válidas)
            if report["gpu_status"]["utilization"] == 0.0:
                issues.append(
                    {
                        "type": "gpu_not_used",
                        "severity": "high",
                        "message": "GPU não está sendo utilizada - métricas de performance são FALSAS",
                    }
                )

            # Verificar se há muitos erros recentes
            if report["metrics"]["corruption_rate"] > 0.05:  # 5%
                issues.append(
                    {
                        "type": "high_corruption",
                        "severity": "critical",
                        "message": f"Taxa de corrupção elevada: {report['metrics']['corruption_rate']:.1%}",
                    }
                )

            # Verificar uso de memória
            if report["metrics"]["memory_usage"] > 0.9:  # 90%
                issues.append(
                    {
                        "type": "high_memory",
                        "severity": "medium",
                        "message": f"Uso de memória alto: {report['metrics']['memory_usage']:.1%}",
                    }
                )

            report["additional_issues"] = issues
            return report

        except Exception as e:
            self.logger.error(f"Erro verificando integridade: {e}")
            return {
                "error": str(e),
                "system_status": "error",
                "timestamp": datetime.now().isoformat(),
            }

    def _execute_corrective_actions(self, report: Dict[str, Any]):
        """Executar ações corretivas baseadas no relatório"""
        issues = report.get("additional_issues", [])

        for issue in issues:
            if issue["type"] == "gpu_not_used":
                self._fix_gpu_usage()
            elif issue["type"] == "high_corruption":
                self._repair_corruption()

    def _fix_gpu_usage(self):
        """Tentar corrigir uso da GPU"""
        self.logger.info("Tentando corrigir uso da GPU...")

        try:
            # Verificar e corrigir configuração da GPU
            config_file = Path("~/projects/omnimind/config/optimization_config.json").expanduser()

            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)

                if not config.get("use_gpu", False):
                    config["use_gpu"] = True
                    config["device"] = "cuda"

                    with open(config_file, "w") as f:
                        json.dump(config, f, indent=2)

                    self.logger.info("Configuração GPU corrigida")
                    self._send_alert(
                        "GPU Configuração Corrigida",
                        "Configuração de GPU foi automaticamente corrigida para usar CUDA",
                        "info",
                    )
                else:
                    self.logger.info("Configuração GPU já está correta")

        except Exception as e:
            self.logger.error(f"Erro corrigindo GPU: {e}")

    def _repair_corruption(self):
        """Executar reparo de corrupção"""
        self.logger.info("Executando reparo automático de corrupção...")

        try:
            system = self._get_audit_system()
            result = system.repair_chain_integrity()

            if result["repaired"]:
                self._send_alert(
                    "Reparo de Corrupção Executado",
                    f"Cadeia de auditoria reparada: {result['message']}",
                    "info",
                )
            else:
                self._send_alert(
                    "Falha no Reparo de Corrupção",
                    f"Reparo automático falhou: {result['message']}",
                    "critical",
                )

        except Exception as e:
            self.logger.error(f"Erro no reparo: {e}")

    def _generate_health_report(self) -> str:
        """Gerar relatório de saúde completo"""
        report_file = self.health_reports_dir / f"health_report_{int(time.time())}.json"

        health_data = {
            "timestamp": datetime.now().isoformat(),
            "monitor_uptime": time.time() - self.last_hour_reset,
            "alerts_this_hour": self.alerts_this_hour,
            "integrity_report": self._check_integrity(),
            "system_info": {
                "log_dir": str(self.log_dir),
                "monitor_dir": str(self.monitor_dir),
                "alert_config": {
                    "email_enabled": self.alert_config["email"]["enabled"],
                    "slack_enabled": self.alert_config["slack"]["enabled"],
                },
            },
        }

        with open(report_file, "w") as f:
            json.dump(health_data, f, indent=2)

        return str(report_file)

    def _save_current_metrics(self, report: Dict[str, Any]):
        """Salvar métricas atuais em integrity_metrics.json (fonte oficial)"""
        metrics_file = self.log_dir / "integrity_metrics.json"

        try:
            # Flatten metrics for easy consumption
            # Safely get nested values
            integrity_report = report.get("report", {}) if "report" in report else report
            metrics = integrity_report.get("metrics", {})
            gpu_status = integrity_report.get("gpu_status", {})

            flat_metrics = {
                "chain_valid": integrity_report.get("valid", False),
                "events_verified": integrity_report.get("events_verified", 0),
                "corruption_rate": metrics.get("corruption_rate", 0.0),
                "last_validation": time.time(),
                "gpu_utilization": gpu_status.get("utilization", 0.0),
                "memory_usage": metrics.get("memory_usage", 0.0),
                "system_load": psutil.cpu_percent(),
                "integrity_level": report.get("status", "unknown"),
            }

            # Atomic write
            temp_file = metrics_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(flat_metrics, f, indent=2)
            temp_file.rename(metrics_file)

        except Exception as e:
            self.logger.error(f"Failed to save integrity metrics: {e}")

    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Executar um ciclo completo de monitoramento"""
        self.logger.info("🔍 Iniciando ciclo de monitoramento...")

        # Verificar integridade
        report = self._check_integrity()

        if "error" in report:
            self._send_alert(
                "Erro no Monitoramento",
                f"Falha ao verificar integridade: {report['error']}",
                "critical",
            )
            return report

        # Verificar nível de integridade
        status = report["system_status"]

        if status == "critical":
            self._send_alert(
                "Integridade CRÍTICA Detectada",
                "Sistema de auditoria comprometido - ação imediata necessária",
                "critical",
            )
        elif status == "high":
            self._send_alert(
                "Integridade Comprometida",
                "Quebras na cadeia de auditoria detectadas",
                "high",
            )

        # Executar ações corretivas
        self._execute_corrective_actions(report)

        # Gerar relatório de saúde
        health_report = self._generate_health_report()

        # Prepare result dict first
        result = {
            "status": status,
            "report": report,
            "health_report": health_report,
            "timestamp": datetime.now().isoformat(),
        }

        # Salvar métricas oficiais
        self._save_current_metrics(result)

        self.logger.info(f"✅ Ciclo de monitoramento concluído - Relatório: {health_report}")

        return result

    def start_continuous_monitoring(self):
        """Iniciar monitoramento contínuo"""
        self.logger.info("🚀 Iniciando monitoramento contínuo do sistema de auditoria")
        self.logger.info(f"Intervalo de verificação: {self.check_interval} segundos")

        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoramento interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"Erro fatal no monitoramento: {e}")
            self._send_alert(
                "Monitoramento Falhou",
                f"Erro fatal no sistema de monitoramento: {e}",
                "critical",
            )

    def run_once(self) -> Dict[str, Any]:
        """Executar monitoramento uma vez e retornar resultado"""
        return self.run_monitoring_cycle()


def main():
    """Função principal do monitor"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor de Integridade do Sistema de Auditoria")
    parser.add_argument("--continuous", action="store_true", help="Executar monitoramento contínuo")
    parser.add_argument("--once", action="store_true", help="Executar uma verificação única")
    parser.add_argument("--log-dir", default="~/projects/omnimind/logs", help="Diretório de logs")

    args = parser.parse_args()

    monitor = IntegrityMonitor(args.log_dir)

    if args.continuous:
        monitor.start_continuous_monitoring()
    elif args.once:
        result = monitor.run_once()
        print(json.dumps(result, indent=2))
    else:
        # Modo interativo simples
        print("🔍 Monitor de Integridade - Modo Interativo")
        print("Comandos: 'check' (verificar), 'report' (relatório), 'quit' (sair)")

        while True:
            try:
                cmd = input("> ").strip().lower()

                if cmd == "check":
                    result = monitor.run_once()
                    print(f"Status: {result['status']}")
                    print(f"Relatório: {result['health_report']}")

                elif cmd == "report":
                    report = monitor._generate_health_report()
                    print(f"Relatório gerado: {report}")

                elif cmd == "quit":
                    break

                else:
                    print("Comandos: check, report, quit")

            except KeyboardInterrupt:
                break

        print("👋 Monitor encerrado")


if __name__ == "__main__":
    main()

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
ML Monitor - Monitora uso e limites de ML híbrido
Executa verificações periódicas e alertas
"""

import json
import time
from datetime import datetime
from pathlib import Path

from hybrid_ml_optimizer import HybridMLOptimizer


class MLMonitor:
    def __init__(self):
        self.optimizer = HybridMLOptimizer()
        self.log_file = Path("logs/ml_usage.log")
        self.alert_file = Path("logs/ml_alerts.log")
        self.log_file.parent.mkdir(exist_ok=True)
        self.alert_file.parent.mkdir(exist_ok=True)

        # Configurações de alerta
        self.alert_thresholds = {
            "github_requests": 100,  # alerta quando restar menos de 100
            "hf_downloads": 1000,  # alerta quando restar menos de 1000
            "hf_uploads": 500,  # alerta quando restar menos de 500MB
        }

    def log_usage(self, usage_data: dict):
        """Registra uso no log"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "github_requests_remaining": usage_data.get("github_requests_remaining"),
            "hf_downloads_remaining": usage_data.get("hf_downloads_remaining"),
            "hf_uploads_remaining": usage_data.get("hf_uploads_remaining"),
            "estimated_cost": usage_data.get("estimated_cost", 0),
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\\n")

    def check_alerts(self) -> list:
        """Verifica se há alertas a serem disparados"""
        alerts = []

        # Verifica limites GitHub
        gh_limits = self.optimizer.check_github_limits()
        remaining = gh_limits.get("remaining", 5000)

        if remaining < self.alert_thresholds["github_requests"]:
            alerts.append(
                {
                    "type": "github_limit",
                    "message": f"GitHub requests restantes: {remaining} (limite: {self.alert_thresholds['github_requests']})",
                    "severity": "warning" if remaining > 50 else "critical",
                }
            )

        # Verifica limites HF (aproximados)
        hf_limits = self.optimizer.check_hf_limits()

        if hf_limits.get("downloads_remaining", 10000) < self.alert_thresholds["hf_downloads"]:
            alerts.append(
                {
                    "type": "hf_download_limit",
                    "message": f"HF downloads restantes: {hf_limits.get('downloads_remaining')} (limite: {self.alert_thresholds['hf_downloads']})",
                    "severity": "warning",
                }
            )

        if hf_limits.get("uploads_remaining", 5000) < self.alert_thresholds["hf_uploads"]:
            alerts.append(
                {
                    "type": "hf_upload_limit",
                    "message": f"HF uploads restantes: {hf_limits.get('uploads_remaining')}MB (limite: {self.alert_thresholds['hf_uploads']}MB)",
                    "severity": "warning",
                }
            )

        return alerts

    def send_alert(self, alert: dict):
        """Envia alerta (simulado - em produção enviaria email/notificação)"""
        timestamp = datetime.now().isoformat()
        alert_entry = {
            "timestamp": timestamp,
            "type": alert["type"],
            "message": alert["message"],
            "severity": alert["severity"],
        }

        # Log do alerta
        with open(self.alert_file, "a") as f:
            f.write(json.dumps(alert_entry) + "\\n")

        # Simula envio de alerta
        severity_icon = "⚠️" if alert["severity"] == "warning" else "🚨"
        print(f"{severity_icon} ALERTA {alert['severity'].upper()}: {alert['message']}")

        # Em produção, enviaria email/notificação
        # self._send_email_alert(alert)

    def generate_report(self) -> dict:
        """Gera relatório completo de uso"""
        # Lê logs recentes
        usage_history = []
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                lines = f.readlines()[-10:]  # últimas 10 entradas
                for line in lines:
                    try:
                        usage_history.append(json.loads(line.strip()))
                    except:
                        continue

        # Estatísticas atuais
        current_usage = self.optimizer.get_usage_report()

        # Análise de tendências
        if len(usage_history) >= 2:
            recent = usage_history[-1]
            previous = usage_history[-2]

            github_trend = recent.get("github_requests_remaining", 0) - previous.get(
                "github_requests_remaining", 0
            )
            cost_trend = recent.get("estimated_cost", 0) - previous.get("estimated_cost", 0)
        else:
            github_trend = 0
            cost_trend = 0

        return {
            "current_usage": current_usage,
            "usage_history": usage_history[-5:],  # últimas 5 entradas
            "trends": {"github_requests_trend": github_trend, "cost_trend": cost_trend},
            "alerts_active": len(self.check_alerts()),
            "generated_at": datetime.now().isoformat(),
        }

    def run_monitoring_cycle(self):
        """Executa um ciclo completo de monitoramento"""
        print(f"🔍 Iniciando monitoramento: {datetime.now().strftime('%H:%M:%S')}")

        # Verifica limites atuais
        gh_limits = self.optimizer.check_github_limits()
        hf_limits = self.optimizer.check_hf_limits()

        usage_data = {
            "github_requests_remaining": gh_limits.get("remaining", 5000),
            "hf_downloads_remaining": hf_limits.get("downloads_remaining", 10000),
            "hf_uploads_remaining": hf_limits.get("uploads_remaining", 5000),
            "estimated_cost": self.optimizer.get_usage_report()["github_usage"]["estimated_cost"],
        }

        # Registra uso
        self.log_usage(usage_data)

        # Verifica alertas
        alerts = self.check_alerts()
        for alert in alerts:
            self.send_alert(alert)

        print(f"✅ Monitoramento concluído - Alertas: {len(alerts)}")

        return usage_data, alerts


def main():
    """Função principal para execução contínua"""
    monitor = MLMonitor()

    print("🚀 ML Monitor iniciado")
    print("📊 Pressione Ctrl+C para parar")
    print("-" * 40)

    try:
        while True:
            monitor.run_monitoring_cycle()

            # Gera relatório a cada 10 ciclos
            if int(time.time()) % 600 < 30:  # aproximadamente a cada 10 min
                report = monitor.generate_report()
                print("\\n📈 RELATÓRIO PERIÓDICO:")
                print(
                    f"   GitHub requests restantes: {report['current_usage']['github_usage']['requests_remaining']}"
                )
                print(
                    f"   Custo estimado: ${report['current_usage']['github_usage']['estimated_cost']:.3f}"
                )
                print(f"   Alertas ativos: {report['alerts_active']}")

            # Intervalo de 30 segundos
            time.sleep(30)

    except KeyboardInterrupt:
        print("\\n⏹️  Monitoramento interrompido pelo usuário")

        # Relatório final
        final_report = monitor.generate_report()
        print("\\n📊 RELATÓRIO FINAL:")
        print(json.dumps(final_report, indent=2, default=str))


if __name__ == "__main__":
    main()

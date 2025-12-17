"""
Sistema de Relatórios Persistidos para Módulos OmniMind

Gera relatórios estruturados e persistidos para auditoria.
Exceto o próprio sistema de auditoria (conceito teórico).

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from .module_metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class ModuleReporter:
    """
    Gerador de relatórios persistidos para módulos OmniMind.

    Características:
    - Relatórios estruturados em JSON/Markdown
    - Integração com métricas
    - Histórico de relatórios
    - Rotação automática
    """

    def __init__(self, reports_dir: str = "data/reports/modules"):
        """
        Inicializa gerador de relatórios.

        Args:
            reports_dir: Diretório para salvar relatórios
        """
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.metrics_collector = get_metrics_collector()

        logger.info(f"ModuleReporter inicializado: {self.reports_dir}")

    def generate_module_report(
        self,
        module_name: str,
        include_metrics: bool = True,
        include_logs: bool = False,
        format: str = "json",
    ) -> Dict[str, Any]:
        """
        Gera relatório para um módulo.

        Args:
            module_name: Nome do módulo
            include_metrics: Incluir métricas
            include_logs: Incluir logs (futuro)
            format: Formato do relatório (json, markdown)

        Returns:
            Dict com relatório
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        report: Dict[str, Any] = {
            "module": module_name,
            "timestamp": timestamp,
            "generated_by": "ModuleReporter",
        }

        # Incluir métricas
        if include_metrics:
            module_metrics = self.metrics_collector.get_module_metrics(module_name)
            if module_metrics:
                report["metrics"] = module_metrics
            else:
                report["metrics"] = {"status": "no_metrics_available"}

        # Incluir logs (futuro)
        if include_logs:
            report["logs"] = {"status": "not_implemented"}

        # Persistir relatório
        if format == "json":
            report_file = (
                self.reports_dir
                / f"{module_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            report["report_file"] = str(report_file)

        elif format == "markdown":
            report_file = (
                self.reports_dir
                / f"{module_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
            )
            markdown_content = self._generate_markdown(report)
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            report["report_file"] = str(report_file)

        logger.info(f"Relatório gerado para {module_name}: {report.get('report_file')}")

        return report

    def generate_summary_report(self, format: str = "json") -> Dict[str, Any]:
        """
        Gera relatório resumo de todos os módulos.

        Args:
            format: Formato do relatório

        Returns:
            Dict com relatório resumo
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        all_metrics = self.metrics_collector.get_all_metrics()

        report = {
            "type": "summary",
            "timestamp": timestamp,
            "modules": all_metrics.get("modules", {}),
            "total_modules": len(all_metrics.get("modules", {})),
        }

        # Persistir
        if format == "json":
            report_file = (
                self.reports_dir
                / f"summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            report["report_file"] = str(report_file)

        return report

    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """Gera conteúdo Markdown do relatório."""
        lines = [
            f"# Relatório: {report['module']}",
            "",
            f"**Timestamp**: {report['timestamp']}",
            "",
        ]

        if "metrics" in report:
            lines.append("## Métricas")
            lines.append("")
            metrics = report["metrics"]
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    if key != "metrics":
                        lines.append(f"- **{key}**: {value}")
                if "metrics" in metrics:
                    lines.append("")
                    lines.append("### Métricas Detalhadas")
                    for metric_name, metric_data in metrics["metrics"].items():
                        if isinstance(metric_data, dict):
                            value = metric_data.get("value", "N/A")
                            timestamp = metric_data.get("timestamp", "N/A")
                            lines.append(f"- **{metric_name}**: {value} (atualizado: {timestamp})")

        return "\n".join(lines)


# Instância global
_global_reporter: Optional[ModuleReporter] = None


def get_module_reporter() -> ModuleReporter:
    """Retorna instância global do gerador de relatórios."""
    global _global_reporter
    if _global_reporter is None:
        _global_reporter = ModuleReporter()
    return _global_reporter

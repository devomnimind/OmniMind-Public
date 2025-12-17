#!/usr/bin/env python3
"""
DETECTOR AUTOMÁTICO DE CONFIGURAÇÕES QUE QUEBRAM Φ
Implementa validação automática de configurações críticas do sistema.

Detecta automaticamente quando configurações causam Φ=0 ou inconsistências,
alertando para problemas de implementação vs teoria.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Callable
import numpy as np
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel

import sys

sys.path.append(".")
from scripts.science_validation.run_scientific_ablations import IntegrationLoopSimulator


class PhiConfigurationValidator:
    """Detector automático de configurações que quebram Φ."""

    def __init__(self):
        self.critical_configs = {
            "expectation_silent": [False, True],
            "embedding_dim": [64, 128, 256],
        }
        self.baseline_phi = 0.5  # Φ esperado em configuração normal (expectation_silent=False)
        self.baseline_phi_silent = 0.05  # Φ esperado quando expectation_silent=True
        self.tolerance = 0.2  # Tolerância mais permissiva para variações

    async def test_configuration_impact(
        self, config_name: str, config_value: Any
    ) -> Dict[str, Any]:
        """Testa impacto de uma configuração específica."""
        # Usa abordagem similar ao robust validation: múltiplas seeds com mesmo simulador
        phis = []
        for seed in range(5):  # 5 seeds para teste rápido
            np.random.seed(seed)

            # Cria simulador com configuração base
            base_config = {
                "embedding_dim": 128,
                "expectation_silent": False,
            }

            # Ajusta configuração específica
            if config_name == "embedding_dim":
                base_config["embedding_dim"] = config_value
                base_config["expectation_silent"] = False
            elif config_name == "expectation_silent":
                base_config["expectation_silent"] = config_value

            simulator = IntegrationLoopSimulator(**base_config)

            # Executa 20 ciclos como no robust validation
            seed_phis = []
            for _ in range(20):
                phi = await simulator.execute_cycle()
                seed_phis.append(phi)

            phis.append(np.mean(seed_phis))

        mean_phi = np.mean(phis)
        std_phi = np.std(phis)

        # Define baseline baseado na configuração
        expected_baseline = (
            self.baseline_phi_silent
            if config_name == "expectation_silent" and config_value
            else self.baseline_phi
        )

        # Detecta problemas
        is_broken = abs(mean_phi - expected_baseline) > self.tolerance
        severity = "CRÍTICO" if mean_phi < 0.1 else "ALTO" if is_broken else "NORMAL"

        return {
            "config_name": config_name,
            "config_value": config_value,
            "mean_phi": float(mean_phi),
            "std_phi": float(std_phi),
            "is_broken": is_broken,
            "severity": severity,
            "deviation": float(abs(mean_phi - expected_baseline)),
            "expected_baseline": float(expected_baseline),
        }

    async def scan_all_configurations(self) -> Dict[str, Any]:
        """Escaneia todas as configurações críticas."""
        rprint("[bold red]🔍 DETECTOR AUTOMÁTICO: Configurações que Quebram Φ[/bold red]")
        rprint(
            "[dim]Escaneando configurações críticas para detectar Φ=0 ou inconsistências[/dim]\n"
        )

        all_results = {}
        broken_configs = []

        for config_name, config_values in self.critical_configs.items():
            rprint(f"[cyan]Testando {config_name}...[/cyan]")
            config_results = []

            for value in config_values:
                result = await self.test_configuration_impact(config_name, value)
                config_results.append(result)

                if result["is_broken"]:
                    broken_configs.append(result)

            all_results[config_name] = config_results

        # Análise final
        analysis = self._analyze_results(all_results, broken_configs)

        # Exibe relatório
        self._display_report(all_results, broken_configs, analysis)

        # Salva resultados
        self._save_results(all_results, broken_configs, analysis)

        return {
            "all_results": all_results,
            "broken_configs": broken_configs,
            "analysis": analysis,
        }

    def _analyze_results(self, all_results: Dict, broken_configs: List) -> Dict[str, Any]:
        """Analisa resultados para insights."""
        total_tests = sum(len(results) for results in all_results.values())
        broken_count = len(broken_configs)

        # Configurações mais problemáticas
        config_breakdown = {}
        for config in broken_configs:
            name = config["config_name"]
            config_breakdown[name] = config_breakdown.get(name, 0) + 1

        most_problematic = (
            max(config_breakdown.items(), key=lambda x: x[1])
            if config_breakdown
            else ("Nenhuma", 0)
        )

        # Severidade geral
        critical_count = sum(1 for c in broken_configs if c["severity"] == "CRÍTICO")
        high_count = sum(1 for c in broken_configs if c["severity"] == "ALTO")

        overall_severity = (
            "CRÍTICA"
            if critical_count > 0
            else "ALTA" if high_count > 2 else "MODERADA" if broken_count > 0 else "NORMAL"
        )

        return {
            "total_tests": total_tests,
            "broken_configs_count": broken_count,
            "breakage_rate": broken_count / total_tests if total_tests > 0 else 0,
            "most_problematic_config": most_problematic[0],
            "most_problematic_count": most_problematic[1],
            "critical_count": critical_count,
            "high_count": high_count,
            "overall_severity": overall_severity,
            "recommendations": self._generate_recommendations(broken_configs),
        }

    def _generate_recommendations(self, broken_configs: List) -> List[str]:
        """Gera recomendações baseadas nos problemas encontrados."""
        recommendations = []

        if any(
            c["config_name"] == "expectation_silent" and c["config_value"] for c in broken_configs
        ):
            recommendations.append(
                "⚠️ expectation_silent=True quebra Φ - usar apenas para testes controlados"
            )
            recommendations.append("📊 Implementar alertas automáticos quando Φ < 0.1")

        if any(c["config_name"] == "embedding_dim" for c in broken_configs):
            recommendations.append(
                "🔧 embedding_dim muito pequeno causa singularidade - manter ≥ 128"
            )

        if not broken_configs:
            recommendations.append("✅ Todas configurações críticas estão OK")

        return recommendations

    def _display_report(self, all_results: Dict, broken_configs: List, analysis: Dict) -> None:
        """Exibe relatório completo."""
        # Tabela de configurações quebradas
        if broken_configs:
            table = Table(title="🚨 CONFIGURAÇÕES QUE QUEBRAM Φ")
            table.add_column("Configuração", style="red", no_wrap=True)
            table.add_column("Valor", style="yellow")
            table.add_column("Φ Medido", style="magenta")
            table.add_column("Severidade", style="red")
            table.add_column("Desvio", style="cyan")

            for config in broken_configs:
                table.add_row(
                    config["config_name"],
                    str(config["config_value"]),
                    f"{config['mean_phi']:.4f}",
                    config["severity"],
                    f"{config['deviation']:.4f}",
                )

            rprint(table)
        else:
            rprint(Panel("✅ NENHUMA CONFIGURAÇÃO QUEBRA Φ", style="green"))

        # Painel de análise
        analysis_panel = Panel(
            f"📊 ANÁLISE GERAL\n"
            f"Total de Testes: {analysis['total_tests']}\n"
            f"Configurações Quebradas: {analysis['broken_configs_count']} ({analysis['breakage_rate']:.1%})\n"
            f"Configuração Mais Problemática: {analysis['most_problematic_config']} ({analysis['most_problematic_count']} quebras)\n"
            f"Severidade Geral: {analysis['overall_severity']}\n\n"
            f"📋 RECOMENDAÇÕES:\n" + "\n".join(f"• {rec}" for rec in analysis["recommendations"]),
            title="🔍 RESULTADO DA ANÁLISE",
            style="blue",
        )
        rprint(analysis_panel)

    def _save_results(self, all_results: Dict, broken_configs: List, analysis: Dict) -> None:
        """Salva resultados em JSON."""
        timestamp = int(time.time())
        filename = f"phi_configuration_scan_{timestamp}.json"
        filepath = Path("real_evidence") / filename
        filepath.parent.mkdir(exist_ok=True)

        results = {
            "timestamp": timestamp,
            "scan_type": "automatic_phi_breaking_configurations",
            "all_results": all_results,
            "broken_configs": broken_configs,
            "analysis": analysis,
        }

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2, default=str)

        rprint(f"[green]📁 Resultados salvos em {filepath}[/green]")


async def main():
    """Executa detecção automática."""
    validator = PhiConfigurationValidator()
    results = await validator.scan_all_configurations()

    severity = results["analysis"]["overall_severity"]
    if severity in ["CRÍTICA", "ALTA"]:
        print(f"\n🚨 ALERTA: Sistema tem configurações que quebram Φ (Severidade: {severity})")
    else:
        print(f"\n✅ Sistema OK: Configurações críticas não quebram Φ (Severidade: {severity})")


if __name__ == "__main__":
    asyncio.run(main())

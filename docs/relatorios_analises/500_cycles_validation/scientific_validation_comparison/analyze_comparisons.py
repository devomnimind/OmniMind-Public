#!/usr/bin/env python3
"""
Análise Comparativa de Validação Científica - OmniMind
Compara execuções de 500 ciclos para identificar mudanças após refatorações
"""

import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


class ScientificValidationAnalyzer:
    def __init__(self, analysis_dir=None):
        if analysis_dir is None:
            analysis_dir = Path(__file__).parent
        self.analysis_dir = Path(analysis_dir)
        self.executions = {}
        self.load_executions()

    def load_executions(self):
        """Carrega todas as execuções disponíveis"""
        for json_file in self.analysis_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)

                # Extrai timestamp do nome do arquivo
                # Formato: phi_500_cycles_scientific_validation_20251210_HHMMSS.json
                parts = json_file.stem.split("_")
                date_part = parts[-2]  # 20251210
                time_part = parts[-1]  # HHMMSS
                timestamp = date_part + time_part
                execution_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S")

                self.executions[timestamp] = {
                    "data": data,
                    "time": execution_time,
                    "file": json_file,
                }

            except Exception as e:
                print(f"Erro ao carregar {json_file}: {e}")

        # Ordena por tempo
        self.executions = dict(sorted(self.executions.items(), key=lambda x: x[1]["time"]))

    def analyze_phi_progression(self):
        """Analisa a progressão de Φ em todas as execuções"""
        plt.figure(figsize=(15, 10))

        phi_stats = {}
        max_values = []
        final_values = []
        avg_values = []

        for timestamp, execution in self.executions.items():
            data = execution["data"]
            phi_values = data.get("phi_progression", [])

            if phi_values:
                time_formatted = execution["time"].strftime("%H:%M")

                # Estatísticas
                phi_max = max(phi_values)
                phi_final = phi_values[-1] if phi_values else 0
                phi_avg = np.mean(phi_values)

                phi_stats[timestamp] = {
                    "max": phi_max,
                    "final": phi_final,
                    "avg": phi_avg,
                    "time": time_formatted,
                }

                max_values.append(phi_max)
                final_values.append(phi_final)
                avg_values.append(phi_avg)

                # Plota progressão
                plt.plot(
                    phi_values,
                    label=f"{time_formatted} (Φ_max={phi_max:.4f})",
                    alpha=0.7,
                    linewidth=1,
                )

        plt.title("Comparação de Progressão Φ - Validação Científica 500 Ciclos")
        plt.xlabel("Ciclo")
        plt.ylabel("Φ (Integrated Information)")
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Salva gráfico
        plt.savefig(
            self.analysis_dir / "phi_progression_comparison.png", dpi=300, bbox_inches="tight"
        )
        plt.close()

        return phi_stats

    def analyze_performance_trends(self):
        """Analisa tendências de performance entre execuções"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))

        timestamps = []
        max_values = []
        final_values = []
        avg_values = []
        execution_times = []

        for timestamp, execution in self.executions.items():
            data = execution["data"]
            phi_values = data.get("phi_progression", [])

            if phi_values:
                timestamps.append(execution["time"])
                max_values.append(max(phi_values))
                final_values.append(phi_values[-1])
                avg_values.append(np.mean(phi_values))

                # Tempo de execução se disponível
                start_time = data.get("start_time")
                end_time = data.get("end_time")
                if start_time and end_time:
                    try:
                        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                        duration = (end - start).total_seconds()
                        execution_times.append(duration)
                    except Exception:
                        execution_times.append(0)
                else:
                    execution_times.append(0)

        # Gráfico 1: Valores máximos
        ax1.plot(timestamps, max_values, "ro-", linewidth=2, markersize=8)
        ax1.set_title("Evolução do Φ Máximo")
        ax1.set_ylabel("Φ Máximo")
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis="x", rotation=45)

        # Gráfico 2: Valores finais
        ax2.plot(timestamps, final_values, "bo-", linewidth=2, markersize=8)
        ax2.set_title("Evolução do Φ Final")
        ax2.set_ylabel("Φ Final")
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis="x", rotation=45)

        # Gráfico 3: Valores médios
        ax3.plot(timestamps, avg_values, "go-", linewidth=2, markersize=8)
        ax3.set_title("Evolução do Φ Médio")
        ax3.set_ylabel("Φ Médio")
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis="x", rotation=45)

        # Gráfico 4: Tempos de execução
        if execution_times and any(t > 0 for t in execution_times):
            valid_times = [(t, time) for t, time in zip(timestamps, execution_times) if time > 0]
            if valid_times:
                ts, times = zip(*valid_times)
                ax4.plot(ts, times, "mo-", linewidth=2, markersize=8)
                ax4.set_title("Tempos de Execução")
                ax4.set_ylabel("Tempo (segundos)")
                ax4.grid(True, alpha=0.3)
                ax4.tick_params(axis="x", rotation=45)

        plt.suptitle("Análise de Tendências - Validação Científica 500 Ciclos", fontsize=16)
        plt.tight_layout()
        plt.savefig(self.analysis_dir / "performance_trends.png", dpi=300, bbox_inches="tight")
        plt.close()

        return {
            "max_values": max_values,
            "final_values": final_values,
            "avg_values": avg_values,
            "execution_times": execution_times,
        }

    def generate_comparison_report(self):
        """Gera relatório de comparação detalhado"""
        phi_stats = self.analyze_phi_progression()
        trends = self.analyze_performance_trends()

        # Análise de melhorias/regressões
        timestamps = list(phi_stats.keys())
        if len(timestamps) >= 2:
            first_execution = timestamps[0]
            last_execution = timestamps[-1]

            improvement_max = phi_stats[last_execution]["max"] - phi_stats[first_execution]["max"]
            improvement_final = (
                phi_stats[last_execution]["final"] - phi_stats[first_execution]["final"]
            )
            improvement_avg = phi_stats[last_execution]["avg"] - phi_stats[first_execution]["avg"]

            # Cria relatório
            report = f"""# Relatório de Comparação - Validação Científica 500 Ciclos

## 📊 Resumo Executivo

**Período analisado:** {self.executions[first_execution]['time']} → {self.executions[last_execution]['time']}
**Total de execuções:** {len(self.executions)}

## 📈 Análise de Performance

### Valores Φ por Execução:
"""

            for timestamp, stats in phi_stats.items():
                report += f"""
**{stats['time']}** ({timestamp}):
- Φ Máximo: {stats['max']:.6f}
- Φ Final: {stats['final']:.6f}
- Φ Médio: {stats['avg']:.6f}
"""

            report += """
### Interpretação dos Resultados:
"""

            if improvement_max > 0:
                report += f"- ✅ **Melhoria no Φ máximo** (+{improvement_max:.6f}): Sistema alcançando estados de maior integração\n"
            elif improvement_max < 0:
                report += f"- ⚠️ **Regressão no Φ máximo** ({improvement_max:.6f}): Sistema com menor pico de integração\n"
            else:
                report += (
                    "- ➡️ **Φ máximo estável**: Sem mudanças significativas no pico de integração\n"
                )

            if improvement_final > 0:
                report += f"- ✅ **Melhoria no Φ final** (+{improvement_final:.6f}): Sistema terminando com maior integração\n"
            elif improvement_final < 0:
                report += f"- ⚠️ **Regressão no Φ final** ({improvement_final:.6f}): Sistema terminando com menor integração\n"
            else:
                report += (
                    "- ➡️ **Φ final estável**: Sem mudanças significativas na integração final\n"
                )

            if improvement_avg > 0:
                report += f"- ✅ **Melhoria no Φ médio** (+{improvement_avg:.6f}): Consistência geral melhorada\n"
            elif improvement_avg < 0:
                report += f"- ⚠️ **Regressão no Φ médio** ({improvement_avg:.6f}): Consistência geral reduzida\n"
            else:
                report += "- ➡️ **Φ médio estável**: Consistência mantida\n"

            # Análise de estabilidade
            max_variation = np.std(trends["max_values"])
            final_variation = np.std(trends["final_values"])

            report += f"""
### Análise de Estabilidade:
- Variação Φ máximo: {max_variation:.6f}
- Variação Φ final: {final_variation:.6f}
"""

            if max_variation < 0.01:
                report += "- ✅ **Estabilidade excelente** no Φ máximo\n"
            elif max_variation < 0.05:
                report += "- ⚠️ **Estabilidade moderada** no Φ máximo\n"
            else:
                report += "- ❌ **Instabilidade** no Φ máximo\n"

            if final_variation < 0.01:
                report += "- ✅ **Estabilidade excelente** no Φ final\n"
            elif final_variation < 0.05:
                report += "- ⚠️ **Estabilidade moderada** no Φ final\n"
            else:
                report += "- ❌ **Instabilidade** no Φ final\n"

            report += f"""
### Métricas Detalhadas:
- Total de execuções: {len(self.executions)}
- Ciclos por execução: 500
- Intervalo temporal: {min(phi_stats.keys())} → {max(phi_stats.keys())}
- Melhor Φ máximo: {max(stats['max'] for stats in phi_stats.values()):.6f}
- Melhor Φ final: {max(stats['final'] for stats in phi_stats.values()):.6f}
- Melhor Φ médio: {max(stats['avg'] for stats in phi_stats.values()):.6f}
"""

            # Salva relatório
            with open(self.analysis_dir / "comparison_report.md", "w") as f:
                f.write(report)

            print(
                f"✅ Relatório de comparação salvo em: {self.analysis_dir / 'comparison_report.md'}"
            )

        return phi_stats, trends


def main():
    print("🔬 Iniciando análise comparativa de validação científica...")

    analyzer = ScientificValidationAnalyzer()

    if not analyzer.executions:
        print("❌ Nenhum arquivo de execução encontrado!")
        return

    print(f"📊 Encontradas {len(analyzer.executions)} execuções para análise")

    # Executa análises
    phi_stats, trends = analyzer.generate_comparison_report()

    print("✅ Análise comparativa concluída!")
    print(f"📁 Resultados salvos em: {analyzer.analysis_dir}")


if __name__ == "__main__":
    main()

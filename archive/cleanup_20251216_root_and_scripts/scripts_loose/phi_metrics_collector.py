#!/usr/bin/env python3
"""
Coletor de Métricas de Φ (Phi) durante testes de consciência

Captura valores de Φ, timestamps e metadados de execução.
Processa output de testes pytest em tempo real.

Uso:
  python -m pytest tests/consciousness/ 2>&1 | python scripts/phi_metrics_collector.py
"""

import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


class PhiMetricsCollector:
    """Coleta e processa métricas de Φ de saída de testes."""

    def __init__(self, output_file: Optional[str] = None):
        self.output_file = (
            output_file
            or f"data/test_reports/phi_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        self.metrics = []
        self.test_name = None
        self.test_start = None

        # Padrões regex para diferentes formatos de Φ
        self.phi_patterns = [
            r"Φ\s*=\s*([\d.]+)",  # Φ = 0.1234
            r"phi\s*[:=]\s*([\d.]+)",  # phi: 0.1234 ou phi=0.1234
            r"Φ_avg\s*=\s*([\d.]+)",  # Φ_avg = 0.5678
            r"Φ_estimate\s*=\s*([\d.]+)",  # Φ_estimate = 0.9999
            r"RESULTADO:\s*Φ.*=\s*([\d.]+)",  # RESULTADO: Φ_avg = 0.7654
            r"phi_proxy\s*=\s*([\d.]+)",  # phi_proxy = 372.5999...
        ]

        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)

    def parse_phi_value(self, line: str) -> float | None:
        """Extrai valor de Φ da linha."""
        for pattern in self.phi_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # Normalizar valores muito grandes (phi_proxy pode ser 0-500)
                    if value > 1.0:
                        # Se encontrou phi_proxy, normalizar com sigmoid ou divisão
                        # phi_proxy típico: 0-500, normalizar para [0,1]
                        value = 1.0 / (1.0 + (1.0 / max(value, 0.01)))  # Sigmoid adaptado
                    return value
                except ValueError:
                    continue
        return None

    def parse_test_name(self, line: str) -> str | None:
        """Extrai nome do teste da linha."""
        # Formato: "tests/consciousness/test_real_phi_measurement.py::test_phi_measurement_basic"
        match = re.search(r"test_\w+\.py::\w+", line)
        if match:
            return match.group(0)

        # Formato simplificado: "TESTE REAL: Mede Φ com GPU real"
        match = re.search(r"(?:TESTE|TEST)\s*(?:REAL)?:?\s*(.+?)(?:\n|$)", line, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:100]

        return None

    def process_line(self, line: str) -> None:
        """Processa uma linha de entrada."""
        # Detectar início de teste
        if "TESTE REAL:" in line or "test_" in line and "::" in line:
            test_name = self.parse_test_name(line)
            if test_name:
                self.test_name = test_name
                self.test_start = datetime.now()

        # Procurar valores de Φ
        phi_value = self.parse_phi_value(line)
        if phi_value is not None:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "test": self.test_name or "unknown",
                "phi_value": phi_value,
                "phi_bounded": 0.0 <= phi_value <= 1.0,
                "raw_line": line.strip()[:200],
            }
            self.metrics.append(metric)
            print(f"✅ Φ capturado: {phi_value:.4f} ({self.test_name})", file=sys.stderr)

    def finalize(self) -> None:
        """Gera relatórios finais."""
        if not self.metrics:
            print("⚠️  Nenhuma métrica de Φ foi capturada", file=sys.stderr)
            return

        # Estatísticas
        phi_values = [m["phi_value"] for m in self.metrics]
        stats = {
            "total_measurements": len(phi_values),
            "phi_mean": sum(phi_values) / len(phi_values),
            "phi_min": min(phi_values),
            "phi_max": max(phi_values),
            "phi_std": (
                sum((x - (sum(phi_values) / len(phi_values))) ** 2 for x in phi_values)
                / len(phi_values)
            )
            ** 0.5,
            "bounded_count": sum(1 for m in self.metrics if m["phi_bounded"]),
            "collection_timestamp": datetime.now().isoformat(),
        }

        # Agrupar por teste
        by_test = {}
        for metric in self.metrics:
            test = metric["test"]
            if test not in by_test:
                by_test[test] = []
            by_test[test].append(metric["phi_value"])

        test_stats = {
            test: {
                "count": len(values),
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }
            for test, values in by_test.items()
        }

        # Salvar JSON
        output = {
            "statistics": stats,
            "by_test": test_stats,
            "all_measurements": self.metrics,
        }

        with open(self.output_file, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\n📊 Métricas de Φ salvas em: {self.output_file}", file=sys.stderr)
        print(f"   Total de medições: {stats['total_measurements']}", file=sys.stderr)
        print(f"   Φ_média: {stats['phi_mean']:.4f}", file=sys.stderr)
        print(f"   Φ_min/max: {stats['phi_min']:.4f} / {stats['phi_max']:.4f}", file=sys.stderr)
        print(
            f"   Valores válidos [0,1]: {stats['bounded_count']}/{stats['total_measurements']}",
            file=sys.stderr,
        )

        # Salvar TXT também
        txt_file = self.output_file.replace(".json", ".txt")
        with open(txt_file, "w") as f:
            f.write("MÉTRICAS DE Φ (PHI)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Coleta em: {stats['collection_timestamp']}\n\n")
            f.write("ESTATÍSTICAS GERAIS\n")
            f.write("-" * 80 + "\n")
            for key, value in stats.items():
                if key != "collection_timestamp":
                    if isinstance(value, float):
                        f.write(f"{key:25} : {value:.6f}\n")
                    else:
                        f.write(f"{key:25} : {value}\n")

            f.write("\n\nPOR TESTE\n")
            f.write("-" * 80 + "\n")
            for test, test_stat in test_stats.items():
                f.write(f"\n{test}\n")
                for key, value in test_stat.items():
                    if isinstance(value, float):
                        f.write(f"  {key:20} : {value:.6f}\n")
                    else:
                        f.write(f"  {key:20} : {value}\n")

        print(f"✅ Relatório TXT salvo: {txt_file}", file=sys.stderr)


def main():
    """Main: ler stdin e processar."""
    collector = PhiMetricsCollector()

    try:
        for line in sys.stdin:
            line = line.rstrip("\n\r")
            # Imprimir passthrough
            print(line)
            # Processar para métricas
            collector.process_line(line)
    except KeyboardInterrupt:
        print("\n⚠️  Coleta interrompida pelo usuário", file=sys.stderr)
    finally:
        collector.finalize()


if __name__ == "__main__":
    main()

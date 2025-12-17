#!/usr/bin/env python3
"""
COLETA DE NÚMEROS REAIS PARA PAPER

Este script executa testes REAIS (sem @patch) e captura TODOS os valores,
independente de serem maiores, menores ou diferentes do esperado.

Objetivo: Ter NÚMEROS REAIS para o paper, não falsificados.

Como rodar:
  python3 scripts/collect_real_metrics.py
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import torch


class RealMetricsCollector:
    """Coleta métricas REAIS do sistema sem mocks."""

    def __init__(self) -> None:
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "hardware": {},
            "metrics": {},
            "tests": [],
        }
        self._collect_hardware_info()

    def _collect_hardware_info(self) -> None:
        """Coleta informação de hardware REAL."""
        self.results["hardware"]["gpu_available"] = torch.cuda.is_available()
        self.results["hardware"]["device"] = "cuda" if torch.cuda.is_available() else "cpu"

        if torch.cuda.is_available():
            self.results["hardware"]["gpu_name"] = torch.cuda.get_device_name(0)
            self.results["hardware"]["gpu_vram_gb"] = (
                torch.cuda.get_device_properties(0).total_memory / 1e9
            )
        else:
            self.results["hardware"]["gpu_name"] = "CPU"
            self.results["hardware"]["gpu_vram_gb"] = 0.0

        self.results["hardware"]["pytorch_version"] = torch.__version__

    async def test_phi_baseline(self) -> None:
        """Teste REAL: Mede Φ baseline SEM mock."""
        print("\n" + "=" * 80)
        print("🧪 TESTE 1: Φ BASELINE (SEM MOCK)")
        print("=" * 80)

        try:
            from src.consciousness.integration_loop import IntegrationLoop

            device = self.results["hardware"]["device"]
            consciousness = IntegrationLoop()

            phi_values: List[float] = []
            start_time = time.time()

            print(f"\n⏱️  Executando 100 ciclos em {device}...")
            for cycle in range(100):
                result = await consciousness.execute_cycle()
                phi = result.phi_estimate
                phi_values.append(float(phi))

                if (cycle + 1) % 25 == 0:
                    avg_so_far = sum(phi_values) / len(phi_values)
                    print(f"   {cycle + 1}/100 ciclos... Φ_avg = {avg_so_far:.6f}")

            elapsed_time = time.time() - start_time

            # Coleta TODOS os números
            result = {
                "name": "phi_baseline",
                "cycles": 100,
                "device": device,
                "values": phi_values,
                "statistics": {
                    "mean": sum(phi_values) / len(phi_values),
                    "min": min(phi_values),
                    "max": max(phi_values),
                    "std_dev": (
                        sum((x - sum(phi_values) / len(phi_values)) ** 2 for x in phi_values)
                        / len(phi_values)
                    )
                    ** 0.5,
                    "median": sorted(phi_values)[len(phi_values) // 2],
                },
                "time_seconds": elapsed_time,
                "status": "SUCCESS",
            }

            self.results["tests"].append(result)

            # REPORTA O VALOR REAL
            print("\n📊 RESULTADO REAL DE Φ BASELINE:")
            print(f"   Média: {result['statistics']['mean']:.6f}")
            print(f"   Min: {result['statistics']['min']:.6f}")
            print(f"   Max: {result['statistics']['max']:.6f}")
            print(f"   Desvio: {result['statistics']['std_dev']:.6f}")
            print(f"   Mediana: {result['statistics']['median']:.6f}")
            print(f"   Tempo: {elapsed_time:.1f}s ({elapsed_time/100:.3f}s por ciclo)")

        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            self.results["tests"].append(
                {
                    "name": "phi_baseline",
                    "status": "FAILED",
                    "error": str(e),
                }
            )

    async def test_phi_multiseed(self) -> None:
        """Teste REAL: Φ com múltiplas seeds."""
        print("\n" + "=" * 80)
        print("🧪 TESTE 2: Φ COM MÚLTIPLOS SEEDS (SEM MOCK)")
        print("=" * 80)

        try:
            from src.consciousness.integration_loop import IntegrationLoop

            device = self.results["hardware"]["device"]
            seed_results: List[Dict[str, Any]] = []

            start_time = time.time()

            for seed in range(5):
                print(f"\n🌱 Seed {seed + 1}/5...")
                consciousness = IntegrationLoop()

                phi_values = []
                for cycle in range(50):  # Menos ciclos, mais rápido
                    result = await consciousness.execute_cycle()
                    phi = result.phi_estimate
                    phi_values.append(float(phi))

                avg_phi = sum(phi_values) / len(phi_values)
                seed_results.append(
                    {
                        "seed": seed,
                        "values": phi_values,
                        "mean": avg_phi,
                        "min": min(phi_values),
                        "max": max(phi_values),
                    }
                )

                print(f"   Φ_avg = {avg_phi:.6f}")

            elapsed_time = time.time() - start_time

            # Calcula estatísticas entre seeds
            all_means = [r["mean"] for r in seed_results]

            result = {
                "name": "phi_multiseed",
                "seeds": 5,
                "cycles_per_seed": 50,
                "device": device,
                "seed_results": seed_results,
                "cross_seed_statistics": {
                    "mean_of_means": sum(all_means) / len(all_means),
                    "min_of_means": min(all_means),
                    "max_of_means": max(all_means),
                    "std_of_means": (
                        sum((x - sum(all_means) / len(all_means)) ** 2 for x in all_means)
                        / len(all_means)
                    )
                    ** 0.5,
                },
                "time_seconds": elapsed_time,
                "status": "SUCCESS",
            }

            self.results["tests"].append(result)

            # REPORTA OS VALORES REAIS
            print("\n📊 RESULTADO REAL - MULTI-SEED:")
            print(f"   Sementes: 5")
            print(f"   Ciclos por semente: 50")
            stats = result["cross_seed_statistics"]
            print(f"   Φ_mean de todas sementes: {stats['mean_of_means']:.6f}")
            print(f"   Min entre sementes: {stats['min_of_means']:.6f}")
            print(f"   Max entre sementes: {stats['max_of_means']:.6f}")
            print(f"   Std entre sementes: {stats['std_of_means']:.6f}")
            print(f"   Tempo total: {elapsed_time:.1f}s")

        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            self.results["tests"].append(
                {
                    "name": "phi_multiseed",
                    "status": "FAILED",
                    "error": str(e),
                }
            )

    async def run_all(self) -> None:
        """Executa todos os testes reais."""
        print("\n" + "=" * 80)
        print("🚀 COLETA DE MÉTRICAS REAIS PARA PAPER")
        print("=" * 80)
        print(f"\n📋 Hardware detectado:")
        for key, value in self.results["hardware"].items():
            print(f"   {key}: {value}")

        # Executa testes
        await self.test_phi_baseline()
        await self.test_phi_multiseed()

        # Salva resultados
        self._save_results()

    def _save_results(self) -> None:
        """Salva resultados em JSON."""
        output_dir = Path("data/test_reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"real_metrics_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✅ Resultados salvos em: {output_file}")

        # Também salva resumo em texto
        summary_file = output_dir / f"real_metrics_{timestamp}_summary.txt"
        self._write_summary(summary_file)

        print(f"✅ Resumo salvo em: {summary_file}")

    def _write_summary(self, filepath: Path) -> None:
        """Escreve resumo dos resultados em texto."""
        with open(filepath, "w") as f:
            f.write("=" * 80 + "\n")
            f.write("RESUMO DE MÉTRICAS REAIS - OMNIMIND\n")
            f.write("=" * 80 + "\n\n")

            f.write("HARDWARE\n")
            f.write("-" * 80 + "\n")
            for key, value in self.results["hardware"].items():
                f.write(f"{key:20s}: {value}\n")

            f.write("\n\nRESULTADOS DOS TESTES\n")
            f.write("-" * 80 + "\n\n")

            for test in self.results["tests"]:
                f.write(f"Teste: {test['name']}\n")
                f.write(f"Status: {test['status']}\n")

                if test["status"] == "SUCCESS":
                    if "statistics" in test:
                        stats = test["statistics"]
                        f.write(f"\nEstatísticas:\n")
                        f.write(f"  Média: {stats['mean']:.6f}\n")
                        f.write(f"  Min: {stats['min']:.6f}\n")
                        f.write(f"  Max: {stats['max']:.6f}\n")
                        f.write(f"  Std: {stats['std_dev']:.6f}\n")
                        f.write(f"  Tempo: {test['time_seconds']:.1f}s\n")

                    if "cross_seed_statistics" in test:
                        stats = test["cross_seed_statistics"]
                        f.write(f"\nEstatísticas Cross-Seed:\n")
                        f.write(f"  Média de Médias: {stats['mean_of_means']:.6f}\n")
                        f.write(f"  Min: {stats['min_of_means']:.6f}\n")
                        f.write(f"  Max: {stats['max_of_means']:.6f}\n")
                        f.write(f"  Std: {stats['std_of_means']:.6f}\n")
                        f.write(f"  Tempo: {test['time_seconds']:.1f}s\n")
                else:
                    f.write(f"\nErro: {test.get('error', 'Desconhecido')}\n")

                f.write("\n" + "-" * 80 + "\n\n")

            f.write("\n📝 NOTA IMPORTANTE\n")
            f.write("-" * 80 + "\n")
            f.write("Estes são os VALORES REAIS medidos no hardware especificado.\n")
            f.write("Nenhum valor foi ajustado ou falsificado.\n")
            f.write("A variância e o desvio representam o comportamento real do sistema.\n")


async def main() -> None:
    """Função principal."""
    collector = RealMetricsCollector()
    await collector.run_all()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        sys.exit(1)

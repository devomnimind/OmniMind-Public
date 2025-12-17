#!/usr/bin/env python3
"""
Executa ablações ordenadas de módulos de consciência.

Procedimento:
1. Baseline: executa sistema completo (200 ciclos) → mede Φ_baseline
2. Para cada módulo: desativa, executa 200 ciclos, mede Φ_ablated
3. Calcula: ΔΦ = Φ_baseline - Φ_ablated, Contribuição % = ΔΦ / Φ_baseline

Timestamps e saída JSON em data/test_reports/ablations_YYYYMMDD_HHMMSS.json
"""

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.consciousness.integration_loop import IntegrationLoop


class AblationRunner:
    """Executa ablações de módulos."""

    def __init__(self, num_cycles: int = 200):
        self.num_cycles = num_cycles
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "unix_timestamp": time.time(),
            "num_cycles": num_cycles,
            "ablations": {},
            "summary": {},
        }

    async def run_baseline(self) -> float:
        """Executa sistema completo e retorna Φ_mean."""
        logger.info("=" * 70)
        logger.info("BASELINE: Sistema completo")
        logger.info("=" * 70)

        consciousness = IntegrationLoop()
        phi_values = []

        start_time = time.time()
        start_ts = datetime.now().isoformat()

        for i in range(self.num_cycles):
            result = await consciousness.execute_cycle()
            phi = result.phi_estimate if hasattr(result, "phi_estimate") else 0.0
            phi_values.append(float(phi))

            if (i + 1) % 50 == 0:
                logger.info(f"  Ciclo {i + 1}/{self.num_cycles} ✓")

        total_time = time.time() - start_time
        end_ts = datetime.now().isoformat()

        phi_mean = sum(phi_values) / len(phi_values) if phi_values else 0.0

        logger.info(f"✅ Baseline Φ_mean: {phi_mean:.6f} (tempo: {total_time:.2f}s)")

        self.results["baseline"] = {
            "phi_mean": phi_mean,
            "phi_min": min(phi_values),
            "phi_max": max(phi_values),
            "phi_values": phi_values[:10] + ["..."] if len(phi_values) > 10 else phi_values,
            "num_values": len(phi_values),
            "time_seconds": total_time,
            "start_timestamp": start_ts,
            "end_timestamp": end_ts,
        }

        return phi_mean

    async def run_ablation(self, module_name: str, phi_baseline: float) -> None:
        """Executa ablação de um módulo específico."""
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"ABLAÇÃO: Desativando '{module_name}'")
        logger.info("=" * 70)

        consciousness = IntegrationLoop()

        # Desativa módulo removendo da sequência de execução
        if module_name in consciousness.loop_sequence:
            consciousness.loop_sequence = [
                m for m in consciousness.loop_sequence if m != module_name
            ]
            logger.info(f"✅ Módulo '{module_name}' desativado (removido da sequência)")
            logger.info(f"   Sequência agora: {consciousness.loop_sequence}")
        else:
            logger.warning(f"⚠️  Módulo '{module_name}' não encontrado na sequência")
            return

        phi_values = []
        errors = []

        start_time = time.time()
        start_ts = datetime.now().isoformat()

        for i in range(self.num_cycles):
            try:
                result = await consciousness.execute_cycle()
                phi = result.phi_estimate if hasattr(result, "phi_estimate") else 0.0
                phi_values.append(float(phi))

                if (i + 1) % 50 == 0:
                    logger.info(f"  Ciclo {i + 1}/{self.num_cycles} ✓")
            except Exception as e:
                logger.warning(f"  Erro no ciclo {i + 1}: {e}")
                errors.append(str(e))

        total_time = time.time() - start_time
        end_ts = datetime.now().isoformat()

        if not phi_values:
            logger.error(f"❌ Nenhum valor Φ coletado para ablação '{module_name}'")
            phi_mean = 0.0
        else:
            phi_mean = sum(phi_values) / len(phi_values)

        delta_phi = phi_baseline - phi_mean
        contribution = (delta_phi / phi_baseline * 100) if phi_baseline > 0 else 0.0

        logger.info(f"  Φ_ablated: {phi_mean:.6f}")
        logger.info(f"  ΔΦ: {delta_phi:.6f}")
        logger.info(f"  Contribuição: {contribution:.1f}%")
        logger.info(f"  Tempo: {total_time:.2f}s")

        self.results["ablations"][module_name] = {
            "phi_ablated": phi_mean,
            "phi_baseline": phi_baseline,
            "delta_phi": delta_phi,
            "contribution_percent": contribution,
            "time_seconds": total_time,
            "errors": errors if errors else None,
            "phi_values": phi_values[:10] + ["..."] if len(phi_values) > 10 else phi_values,
            "start_timestamp": start_ts,
            "end_timestamp": end_ts,
        }

    async def run_all(self) -> None:
        """Executa todas as ablações."""
        logger.info("INICIANDO ABLAÇÕES ORDENADAS")
        logger.info(f"Ciclos por teste: {self.num_cycles}")
        logger.info("")

        # 1. Baseline
        phi_baseline = await self.run_baseline()

        # 2. Ablações na ordem dos papers
        modules_to_ablate = [
            "expectation",  # Paper 1: 51.1% de contribuição
            "sensory_input",  # Paper 2: 100% de contribuição
            "qualia",  # Paper 2: 100% de contribuição
            "narrative",  # Paper 2: 92% de contribuição
            "meaning_maker",  # Paper 1: 39.9% de contribuição
        ]

        for module_name in modules_to_ablate:
            await self.run_ablation(module_name, phi_baseline)

        # 3. Resumo
        self._generate_summary(phi_baseline)

        # 4. Salva resultado
        self._save_results()

    def _generate_summary(self, phi_baseline: float) -> None:
        """Gera resumo das ablações."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("RESUMO DAS ABLAÇÕES")
        logger.info("=" * 70)

        summary = []
        for module_name, ablation_data in self.results["ablations"].items():
            contribution = ablation_data["contribution_percent"]
            summary.append({"module": module_name, "contribution": contribution})
            logger.info(f"  {module_name:20s}: {contribution:6.1f}%")

        # Ordena por contribuição decrescente
        summary.sort(key=lambda x: x["contribution"], reverse=True)

        self.results["summary"] = {
            "phi_baseline": phi_baseline,
            "modules_ranked_by_contribution": summary,
            "total_contribution": sum(item["contribution"] for item in summary),
            "timestamp": datetime.now().isoformat(),
        }

        logger.info("")
        logger.info("Ranking por contribuição:")
        for i, item in enumerate(summary, 1):
            logger.info(f"  {i}. {item['module']:20s}: {item['contribution']:6.1f}%")

        logger.info(f"  TOTAL: {self.results['summary']['total_contribution']:.1f}%")
        logger.info("  (>100% = módulos co-dependentes, topologia Borromeana)")

    def _save_results(self) -> None:
        """Salva resultados em JSON."""
        output_dir = Path("/home/fahbrain/projects/omnimind/data/test_reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"ablations_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"✅ Resultados salvos: {output_file}")

        # Salva também arquivo "latest" para fácil acesso
        latest_file = output_dir / "ablations_latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"✅ Resumo: {latest_file}")


async def main() -> None:
    """Entry point."""
    runner = AblationRunner(num_cycles=200)

    try:
        await runner.run_all()
        logger.info("")
        logger.info("✅ ABLAÇÕES COMPLETAS")
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("❌ Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

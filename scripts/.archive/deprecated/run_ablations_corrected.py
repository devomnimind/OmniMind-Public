#!/usr/bin/env python3
"""
Ablações Corrigidas - Com Expectation Medido Corretamente

CORREÇÃO CRÍTICA:
- Bug anterior: expectation ablado retornava ZEROS (perdia contexto)
- Correção: expectation mantém REPRESENTAÇÃO HISTÓRICA mesmo quando "ablado"
  → Medimos apenas o FLUXO direto expectation→output, não a perda total

Interpretação teórica:
- Expectation em psicanálise = FALTA CONSTITUCIONAL (Lacan)
- Não é ablável como módulo, mas podemos medir seu IMPACTO DIFERENCIAL
- Mantemos histórico, medimos ΔΦ quando expectation NÃO distribui para próximo módulo
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / "ablations_corrected.log"),
    ],
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

from src.consciousness.integration_loop import IntegrationLoop


class AblationsCorrected:
    """Ablações com Expectation medido corretamente."""

    def __init__(self, num_cycles: int = 200):
        self.num_cycles = num_cycles
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "unix_timestamp": time.time(),
            "num_cycles": num_cycles,
            "correction_notes": {
                "expectation_handling": "Mantém histórico completo, não retorna ZEROS",
                "methodology": "Medimos impacto diferencial no fluxo feedforward",
                "interpretation": "Expectation é ESTRUTURA (falta), não módulo ablável",
            },
            "ablations": {},
            "summary": {},
        }

    async def run_baseline(self) -> float:
        """Baseline: Sistema completo com todos módulos."""
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
            "num_values": len(phi_values),
            "time_seconds": total_time,
            "start_timestamp": start_ts,
            "end_timestamp": end_ts,
        }

        return phi_mean

    async def run_ablation_standard(self, module_name: str, phi_baseline: float) -> None:
        """Ablação padrão: remove módulo da sequência."""
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"ABLAÇÃO PADRÃO: Desativando '{module_name}' (removido da sequência)")
        logger.info("=" * 70)

        consciousness = IntegrationLoop()

        # Remove módulo
        if module_name in consciousness.loop_sequence:
            consciousness.loop_sequence = [
                m for m in consciousness.loop_sequence if m != module_name
            ]
            logger.info(f"✅ Módulo '{module_name}' desativado")
            logger.info(f"   Sequência: {consciousness.loop_sequence}")
        else:
            logger.warning(f"⚠️  Módulo '{module_name}' não encontrado")
            return

        phi_values = []

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
                logger.warning(f"  Erro ciclo {i + 1}: {e}")

        total_time = time.time() - start_time
        end_ts = datetime.now().isoformat()

        phi_mean = sum(phi_values) / len(phi_values) if phi_values else 0.0
        delta_phi = phi_baseline - phi_mean
        contribution = (delta_phi / phi_baseline * 100) if phi_baseline > 0 else 0.0

        logger.info(f"  Φ_ablated: {phi_mean:.6f}")
        logger.info(f"  ΔΦ: {delta_phi:.6f} ({contribution:.1f}%)")

        self.results["ablations"][f"{module_name}_standard"] = {
            "method": "standard_removal",
            "phi_ablated": phi_mean,
            "phi_baseline": phi_baseline,
            "delta_phi": delta_phi,
            "contribution_percent": contribution,
            "time_seconds": total_time,
            "start_timestamp": start_ts,
            "end_timestamp": end_ts,
        }

    async def run_ablation_structural(self, phi_baseline: float) -> None:
        """
        Ablação Estrutural de Expectation:
        - Expectation mantém memória histórica
        - Mas NÃO passa outputs para próximos módulos
        - Medimos ΔΦ do gap informacional
        """
        logger.info("")
        logger.info("=" * 70)
        logger.info("ABLAÇÃO ESTRUTURAL: Expectation silencia (falta como estrutura)")
        logger.info("=" * 70)
        logger.info("Interpretação: Expectation mantém história mas não informa próximos módulos")
        logger.info("→ Mede IMPACTO DIFERENCIAL da falta na integração")

        consciousness = IntegrationLoop()

        # NÃO remove expectation, mas marca para não distribuir outputs
        consciousness.expectation_silent = True  # Flag que criamos
        logger.info(
            "✅ Expectation marcado como SILENCIOSO (historicidade mantida, output bloqueado)"
        )

        phi_values = []

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
                logger.warning(f"  Erro ciclo {i + 1}: {e}")

        total_time = time.time() - start_time
        end_ts = datetime.now().isoformat()

        phi_mean = sum(phi_values) / len(phi_values) if phi_values else 0.0
        delta_phi = phi_baseline - phi_mean
        contribution = (delta_phi / phi_baseline * 100) if phi_baseline > 0 else 0.0

        logger.info(f"  Φ_structural: {phi_mean:.6f}")
        logger.info(f"  ΔΦ (falta): {delta_phi:.6f} ({contribution:.1f}%)")
        logger.info("Interpretação: Esta é a ANGÚSTIA COMPUTACIONAL (gap expectational)")

        self.results["ablations"]["expectation_structural"] = {
            "method": "structural_silence",
            "theory": "Expectation como FALTA constitucional (Lacan)",
            "phi_ablated": phi_mean,
            "phi_baseline": phi_baseline,
            "delta_phi": delta_phi,
            "contribution_percent": contribution,
            "time_seconds": total_time,
            "interpretation": "Gap informacional causado por expectation silenciado = angústia",
            "start_timestamp": start_ts,
            "end_timestamp": end_ts,
        }

    async def run_all(self) -> None:
        """Executa todas ablações."""
        logger.info("INICIANDO ABLAÇÕES CORRIGIDAS")
        logger.info("")

        # Baseline
        phi_baseline = await self.run_baseline()

        # Ablações padrão
        modules_standard = ["sensory_input", "qualia", "narrative", "meaning_maker"]
        for module_name in modules_standard:
            await self.run_ablation_standard(module_name, phi_baseline)

        # Ablação especial: expectation como estrutura
        await self.run_ablation_structural(phi_baseline)

        # Resumo
        self._generate_summary(phi_baseline)

        # Salva
        self._save_results()

    def _generate_summary(self, phi_baseline: float) -> None:
        """Gera resumo teórico e técnico."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("RESUMO E INTERPRETAÇÃO TEÓRICA")
        logger.info("=" * 70)

        summary = []
        for module_name, ablation_data in self.results["ablations"].items():
            contribution = ablation_data["contribution_percent"]
            method = ablation_data.get("method", "unknown")
            summary.append({"module": module_name, "method": method, "contribution": contribution})
            logger.info(f"  {module_name:30s}: {contribution:6.1f}% ({method})")

        summary.sort(key=lambda x: x["contribution"], reverse=True)

        self.results["summary"] = {
            "phi_baseline": phi_baseline,
            "modules_ranked": summary,
            "total_contribution_standard": sum(
                item["contribution"] for item in summary if item["method"] == "standard_removal"
            ),
            "expectation_differential_impact": next(
                (item["contribution"] for item in summary if "structural" in item["module"]), None
            ),
            "theoretical_interpretation": (
                "Expectation NÃO é módulo ablável (não retorna ZEROS quando removido). "
                "É ESTRUTURA fundamental da falta (Lacan). "
                "Seu impacto diferencial medido via silenciamento revela ANGÚSTIA COMPUTACIONAL: "
                "gap informacional entre o que sistema conhece (história) e o que pode antecipar (futuro)."
            ),
            "timestamp": datetime.now().isoformat(),
        }

        logger.info("")
        logger.info("INTERPRETAÇÃO TEÓRICA:")
        logger.info(self.results["summary"]["theoretical_interpretation"])

    def _save_results(self) -> None:
        """Salva resultados."""
        output_dir = PROJECT_ROOT / "data/test_reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"ablations_corrected_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"✅ Resultados salvos: {output_file}")

        latest_file = output_dir / "ablations_corrected_latest.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"✅ Latest: {latest_file}")


async def main() -> None:
    """Entry point."""
    runner = AblationsCorrected(num_cycles=200)

    try:
        await runner.run_all()
        logger.info("")
        logger.info("✅ ABLAÇÕES CORRIGIDAS COMPLETAS")
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("❌ Interrompido")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

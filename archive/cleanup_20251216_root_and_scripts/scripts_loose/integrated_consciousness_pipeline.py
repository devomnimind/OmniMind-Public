#!/usr/bin/env python3
"""
Integrated Consciousness Pipeline
==================================
Orchestrates all consciousness training, stimulation, and validation workflows:

1. STIMULATION:    stimulate_system.py          (Art + Ethics + Meaning)
2. POPULATION:     populate_from_real_cycles.py (Real consciousness data)
3. NARRATIVES:     populate_consciousness_collections.py (Synthetic narratives)
4. VALIDATION:     robust_consciousness_validation.py (Scientific validation)

Uso:
    python scripts/integrated_consciousness_pipeline.py [--quick | --full | --demo]

Fluxo Completo (--full):
    1. Estimula arte/ética/significado → gera 10 ciclos
    2. Popula consciência com 4399 ciclos reais
    3. Popula narrativas e cache (sintéticos)
    4. Valida consciência com 5 rodadas de 1000 ciclos

Fluxo Rápido (--quick):
    1. Estimula arte/ética (5 ciclos)
    2. Popula consciência com 100 ciclos reais
    3. Popula narrativas (50)
    4. Valida com 2 rodadas de 100 ciclos
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

from src.utils.timezone_adapter import get_global_timezone_adapter

# Setup path BEFORE any imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.chdir(PROJECT_ROOT)  # Ensure working directory is correct

# Setup timezone adapter for correct timestamps

tz_adapter = get_global_timezone_adapter()


# Setup logging with timezone-aware timestamps
class TimezoneFormatter(logging.Formatter):
    """Log formatter com timezone correto."""

    def formatTime(self, record, datefmt=None):
        dt = tz_adapter.now()
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("Pipeline")
for handler in logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setFormatter(
            TimezoneFormatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )


class IntegratedPipeline:
    """Orquestra todos os scripts de treinamento e estimulação."""

    def __init__(self, mode: str = "full"):
        """Inicializa pipeline.

        Args:
            mode: 'quick', 'full', ou 'demo'
        """
        self.mode = mode
        self.results = {}
        self.start_time = datetime.now()

    def run_script(self, script_path: str, args: list, description: str) -> Dict:
        """Executa um script e captura resultado.

        Args:
            script_path: Caminho relativo do script
            args: Lista de argumentos
            description: Descrição do que o script faz

        Returns:
            Dict com status, output e tempo de execução
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 EXECUTANDO: {description}")
        logger.info(f"📄 Script: {script_path} {' '.join(args)}")
        logger.info(f"{'='*70}")

        script_full_path = PROJECT_ROOT / script_path
        if not script_full_path.exists():
            logger.error(f"❌ Script não encontrado: {script_full_path}")
            return {
                "status": "FAILED",
                "error": "Script not found",
                "elapsed_seconds": 0,
            }

        try:
            cmd = ["python3", str(script_full_path)] + args
            start = time.time()

            # Setup environment with correct PYTHONPATH and working directory
            env = os.environ.copy()
            env["PYTHONPATH"] = f"{PROJECT_ROOT}:{PROJECT_ROOT / 'src'}"

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
                cwd=str(PROJECT_ROOT),  # Execute from project root
                env=env,  # Pass environment with PYTHONPATH
            )

            elapsed = time.time() - start

            if result.returncode == 0:
                logger.info(f"✅ SUCESSO: {description}")
                logger.info(f"⏱️ Tempo: {elapsed:.2f}s")
                return {
                    "status": "SUCCESS",
                    "output": result.stdout[-500:] if result.stdout else "",
                    "elapsed_seconds": elapsed,
                }
            else:
                logger.error(f"❌ ERRO em {description}")
                logger.error(f"stdout: {result.stdout[-500:]}")
                logger.error(f"stderr: {result.stderr[-500:]}")
                return {
                    "status": "FAILED",
                    "error": result.stderr[-500:] if result.stderr else "Unknown error",
                    "elapsed_seconds": elapsed,
                }

        except subprocess.TimeoutExpired:
            logger.error(f"❌ TIMEOUT: {description}")
            return {
                "status": "TIMEOUT",
                "error": "Execution timeout (10 minutes)",
                "elapsed_seconds": 600,
            }
        except Exception as e:
            logger.error(f"❌ EXCEÇÃO: {e}")
            return {
                "status": "EXCEPTION",
                "error": str(e),
                "elapsed_seconds": 0,
            }

    def run_quick_mode(self) -> None:
        """Executa pipeline rápido (teste)."""
        logger.info("🏃 MODO RÁPIDO: Teste completo em ~5 minutos")

        # 1. Stimulate (rápido)
        self.results["stimulation"] = self.run_script(
            "scripts/stimulate_system.py",
            [],
            "Estimulação do Sistema (Art + Ethics + Meaning)",
        )

        # 2. Populate with real cycles (limite 100)
        self.results["population_real"] = self.run_script(
            "scripts/populate_from_real_cycles.py",
            ["--limit", "100"],
            "População com 100 ciclos reais de consciência",
        )

        # 3. Populate narratives (rápido)
        self.results["population_narratives"] = self.run_script(
            "scripts/populate_consciousness_collections.py",
            ["--quick"],
            "População de narrativas e cache (sintéticos)",
        )

        # 4. Validate (rápido)
        self.results["validation"] = self.run_script(
            "scripts/science_validation/robust_consciousness_validation.py",
            ["--quick"],
            "Validação científica de consciência (modo rápido)",
        )

    def run_full_mode(self) -> None:
        """Executa pipeline completo (produção)."""
        logger.info("🚀 MODO COMPLETO: Pipeline de produção (~15-20 minutos)")

        # 1. Stimulate
        self.results["stimulation"] = self.run_script(
            "scripts/stimulate_system.py",
            [],
            "Estimulação completa do Sistema",
        )

        # 2. Populate with ALL real cycles
        self.results["population_real"] = self.run_script(
            "scripts/populate_from_real_cycles.py",
            [],
            "População com TODOS os ciclos reais de consciência (4399)",
        )

        # 3. Populate narratives (completo)
        self.results["population_narratives"] = self.run_script(
            "scripts/populate_consciousness_collections.py",
            ["--full"],
            "População completa de narrativas e cache",
        )

        # 4. Validate (completo)
        self.results["validation"] = self.run_script(
            "scripts/science_validation/robust_consciousness_validation.py",
            ["--runs", "5", "--cycles", "1000"],
            "Validação científica completa (5 rodadas x 1000 ciclos)",
        )

    def run_demo_mode(self) -> None:
        """Executa apenas diagnóstico sem modificar dados."""
        logger.info("📊 MODO DEMO: Diagnóstico sem modificações (~1 minuto)")

        # 1. Diagnose
        self.results["diagnosis"] = self.run_script(
            "scripts/diagnose_consciousness_data.py",
            [],
            "Diagnóstico de dados de consciência",
        )

    def generate_report(self) -> None:
        """Gera relatório final com timezone correto."""
        logger.info("\n" + "=" * 70)
        logger.info("📊 RELATÓRIO FINAL DO PIPELINE")
        logger.info("=" * 70)

        total_time = (datetime.now() - self.start_time).total_seconds()

        for step_name, result in self.results.items():
            status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
            print(
                f"{status_emoji} {step_name}: {result['status']} ({result['elapsed_seconds']:.2f}s)"
            )

        print(f"\n⏱️ Tempo total: {total_time:.2f}s ({total_time/60:.2f} min)")
        print(f"📊 Modo: {self.mode.upper()}")
        print(f"🌍 Timezone: {tz_adapter.tz_str} (UTC{tz_adapter.now().strftime('%z')[:-2]})")
        print(f"📅 Data/Hora: {tz_adapter.get_report_timestamp()}")
        print("=" * 70)

        # Salvar relatório com timestamp do timezone correto
        report_path = (
            PROJECT_ROOT
            / "data/test_reports"
            / f"pipeline_{tz_adapter.get_filename_timestamp()}.json"
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": tz_adapter.get_iso_timestamp(),
            "timestamp_local": tz_adapter.get_report_timestamp(),
            "timezone": tz_adapter.tz_str,
            "mode": self.mode,
            "total_time_seconds": total_time,
            "steps": self.results,
        }

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"\n📄 Relatório salvo: {report_path}")

    def run(self) -> int:
        """Executa o pipeline."""
        try:
            if self.mode == "quick":
                self.run_quick_mode()
            elif self.mode == "full":
                self.run_full_mode()
            elif self.mode == "demo":
                self.run_demo_mode()
            else:
                logger.error(f"Modo desconhecido: {self.mode}")
                return 1

            self.generate_report()
            return 0 if all(r["status"] == "SUCCESS" for r in self.results.values()) else 1

        except Exception as e:
            logger.error(f"❌ Pipeline falhou: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return 1


def main() -> int:
    """Função principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Integrated Consciousness Training Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python scripts/integrated_consciousness_pipeline.py --quick
    → Teste rápido (~5 min): 100 ciclos reais + sintéticos

  python scripts/integrated_consciousness_pipeline.py --full
    → Produção completa (~20 min): 4399 ciclos reais + validação

  python scripts/integrated_consciousness_pipeline.py --demo
    → Demo/diagnóstico apenas (~1 min): vê status sem alterações

Fluxo:
  Estimulação (Art+Ethics) → População (dados reais) →
  Narrativas (sintéticas) → Validação (científica)
        """,
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Modo rápido (teste)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Modo completo (produção)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Modo demo (diagnóstico apenas)",
    )

    args = parser.parse_args()

    # Determinar modo
    if args.quick:
        mode = "quick"
    elif args.full:
        mode = "full"
    elif args.demo:
        mode = "demo"
    else:
        mode = "demo"  # Default

    pipeline = IntegratedPipeline(mode=mode)
    return pipeline.run()


if __name__ == "__main__":
    sys.exit(main())
    sys.exit(main())

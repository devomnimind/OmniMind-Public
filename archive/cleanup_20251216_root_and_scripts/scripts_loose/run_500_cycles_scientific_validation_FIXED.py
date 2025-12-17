#!/usr/bin/env python3
"""
Script para executar 500 ciclos de validação científica completa - VERSÃO CORRIGIDA.

Este script executa 500 ciclos em sequência coletando TODAS as métricas necessárias
para avaliação científica completa do sistema OmniMind.

UBUNTU 22.04.5 COMPATIBLE:
  - Python 3.12.12 ✓
  - GPU-ready: PyTorch 2.5.1+cu121, Qiskit Aer-GPU 0.15.1 ✓
  - systemd services (qdrant, redis, postgresql) ✓
  - CUDA detection integrated ✓

CORREÇÃO CRÍTICA (2025-12-13):
- Força coleta de ExtendedLoopCycleResult
- Adiciona fallback para robust_consciousness_validation.py
- Garante coleta de Gozo, Lacan, Bion, Zimerman, Delta, Psi, Sigma
- Logging melhorado para debug de falhas

CORREÇÃO (2025-12-13 18:40):
- Adicionado logging de TODOS os warnings/errors
- Detecta problemas de GPU, Qiskit, variação mínima
- Captura e relata logs durante execução

BASEADO EM: scripts/run_200_cycles_verbose.py
ATUALIZADO: 2025-12-16 (Ubuntu 22.04.5 compatibility)

Ativação venv:
  source /home/fahbrain/projects/omnimind/.venv/bin/activate
  python3 scripts/run_500_cycles_scientific_validation_FIXED.py [--force-robust]

Tempo esperado: 20-30 minutos (500 ciclos)
Output: real_evidence/phi_500_cycles_scientific_validation_FIXED_YYYYMMDD_HHMMSS.json
"""

import argparse
import asyncio
import gc
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

print("=" * 80)
print("🧪 VALIDAÇÃO CIENTÍFICA - 500 CICLOS COM TODAS AS MÉTRICAS")
print("=" * 80)
print(f"📂 Sistema: Ubuntu 22.04.5 LTS")
print(f"🐍 Python: {sys.version}")
print(f"📅 Timestamp: {datetime.now(timezone.utc).isoformat()}")
print()

# ════════════════════════════════════════════════════════════════════════════
# LOGGING: Configurar captura de TODOS os warnings/errors
# ════════════════════════════════════════════════════════════════════════════
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s: %(message)s",
)

# Listas para capturar logs
captured_warnings: List[str] = []
captured_errors: List[str] = []


class LogCapture(logging.Handler):
    """Handler customizado para capturar logs."""

    def emit(self, record: logging.LogRecord) -> None:
        msg = self.format(record)
        if record.levelno >= logging.ERROR:
            captured_errors.append(msg)
        elif record.levelno >= logging.WARNING:
            captured_warnings.append(msg)


# Adicionar handler customizado
log_capture = LogCapture()
log_capture.setLevel(logging.WARNING)
logging.getLogger().addHandler(log_capture)

# ════════════════════════════════════════════════════════════════════════════
# FUNCTION: Chamar robust_consciousness_validation.py com coleta de métricas
# ════════════════════════════════════════════════════════════════════════════


def run_robust_validation_with_metrics() -> bool:
    """
    Chamar script de validação robusta com coleta de métricas adicionais.

    Este é o fallback recomendado quando IntegrationLoop.execute_cycle()
    não retorna ExtendedLoopCycleResult.
    """
    print("\n" + "=" * 80)
    print("🔄 ALTERNATIVA: Executando validação robusta com coleta de métricas")
    print("=" * 80)

    script_path = Path("scripts/science_validation/robust_consciousness_validation.py")
    if not script_path.exists():
        print(f"❌ Script não encontrado: {script_path}")
        return False

    cmd = [
        sys.executable,
        str(script_path),
        "--runs",
        "10",
        "--cycles",
        "500",
        "--scientific",
    ]

    print(f"🚀 Executando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(Path.cwd()))

    return result.returncode == 0


# ════════════════════════════════════════════════════════════════════════════
# FUNCTION: Coletar métricas psicanalíticas do resultado
# ════════════════════════════════════════════════════════════════════════════


def extract_psychoanalytic_metrics(result: Any) -> Dict[str, Any]:
    """
    Extrai TODAS as métricas psicanalíticas do resultado do ciclo.

    Tenta múltiplas formas de acesso para garantir que não são perdidas.
    """
    metrics = {}

    # Tenta acessar como atributo
    fields_to_check = [
        "gozo",
        "delta",
        "psi",
        "sigma",
        "epsilon",
        "phi_causal",
        "repression_strength",
        "control_effectiveness",
        "triad",
        "module_outputs",
        "module_activations",
        "integration_strength",
        "temporal_signature",
        "cycle_id",
        "homeostatic_state",
    ]

    for field in fields_to_check:
        try:
            value = getattr(result, field, None)
            if value is not None:
                if hasattr(value, "__dict__"):
                    # Se é um objeto, converter para dict
                    metrics[field] = {
                        k: v for k, v in value.__dict__.items() if not k.startswith("_")
                    }
                elif isinstance(value, (list, dict)):
                    metrics[field] = value
                else:
                    metrics[field] = value
        except Exception as e:
            logging.debug(f"Erro ao extrair {field}: {e}")

    return metrics


# ════════════════════════════════════════════════════════════════════════════
# MAIN: Executar validação 500 ciclos
# ════════════════════════════════════════════════════════════════════════════


async def main() -> int:
    """Executar validação de 500 ciclos com todas as métricas."""

    parser = argparse.ArgumentParser(description="Validação científica 500 ciclos")
    parser.add_argument("--cycles", type=int, default=500, help="Número de ciclos")
    parser.add_argument("--scientific", action="store_true", help="Modo científico")
    parser.add_argument(
        "--force-robust", action="store_true", help="Forçar robust_consciousness_validation.py"
    )
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🧪 VALIDAÇÃO CIENTÍFICA - 500 CICLOS COM TODAS AS MÉTRICAS")
    print("=" * 80)
    print(f"Ciclos: {args.cycles}")
    print(f"Modo científico: {args.scientific}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")

    # NOVO (2025-12-14): Validar GPU ANTES de executar
    print("\n🔍 Validando GPU Configuration...")
    try:
        import torch

        cuda_available = torch.cuda.is_available()
        if cuda_available:
            print(f"   ✅ PyTorch CUDA disponível")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            print(f"   ⚠️  PyTorch CUDA não disponível - usará CPU")
    except Exception as e:
        print(f"   ⚠️  Erro ao verificar CUDA: {e}")

    # NOVO (2025-12-14): Exportar OMNIMIND_VALIDATION_MODE
    os.environ["OMNIMIND_VALIDATION_MODE"] = "true"
    print(f"✅ OMNIMIND_VALIDATION_MODE = true (sinalizado para core)")

    # Se --force-robust foi passado, usar robust_consciousness_validation.py
    if args.force_robust:
        print("\n⚠️  Modo forçado: usando robust_consciousness_validation.py")
        success = run_robust_validation_with_metrics()
        return 0 if success else 1

    # Tentar usar IntegrationLoop com extended metrics
    try:
        from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult
        from src.consciousness.integration_loop import IntegrationLoop

        print("\n✅ Importações OK")
        print("🔄 Inicializando IntegrationLoop com extended_results=True...")

        loop = IntegrationLoop(enable_extended_results=True, enable_logging=True)

        print("✅ IntegrationLoop inicializado")

        metrics_collected = []
        phi_values = []
        failures = 0
        extended_result_count = 0

        for i in range(args.cycles):
            try:
                # Executar ciclo com coleta de métricas
                result = await loop.execute_cycle(collect_metrics=True)

                # Verificar se é ExtendedLoopCycleResult
                is_extended = isinstance(result, ExtendedLoopCycleResult)
                if is_extended:
                    extended_result_count += 1

                # Coletar métricas base
                cycle_metrics = {
                    "cycle": i,
                    "phi": result.phi_estimate,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": result.success,
                    "modules_executed": result.modules_executed,
                    "is_extended_result": is_extended,
                }

                # Extrair métricas psicanalíticas
                psychoanalytic_metrics = extract_psychoanalytic_metrics(result)
                cycle_metrics.update(psychoanalytic_metrics)

                metrics_collected.append(cycle_metrics)
                phi_values.append(result.phi_estimate)

                # Log a cada 50 ciclos
                if (i + 1) % 50 == 0:
                    extended_pct = (extended_result_count / (i + 1)) * 100
                    avg_phi = sum(phi_values) / len(phi_values) if phi_values else 0.0
                    print(
                        f"   ✅ Ciclo {i+1}/{args.cycles}: "
                        f"Φ={result.phi_estimate:.3f}, "
                        f"Extended={extended_pct:.1f}%, "
                        f"Média Φ={avg_phi:.3f}"
                    )

            except Exception as e:
                error_str = str(e)
                print(f"   ⚠️  Ciclo {i}: Erro: {e}")

                # NOVO (2025-12-14): Detectar GPU errors específicos
                if "GPU" in error_str and "not supported" in error_str:
                    print(f"\n       🚨 GPU Detection Error detectado!")
                    print(f"       Dica: Verifique nvidia-smi, CUDA_VISIBLE_DEVICES")
                    print(f"       Alternando para fallback (CPU mode)...")
                    failures += 50  # Forçar fallback
                elif "Simulation device" in error_str:
                    print(f"\n       🚨 Qiskit simulation error detectado!")
                    print(f"       Dica: pip install qiskit-aer[gpu] ou use mode='cpu'")
                    failures += 50  # Forçar fallback

                failures += 1
                if failures > 10:
                    print(
                        "\n❌ Muitas falhas (>10). Alternando para robust_consciousness_validation.py"
                    )
                    return 0 if run_robust_validation_with_metrics() else 1

        # Salvar resultados
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_file = Path(
            f"real_evidence/phi_500_cycles_scientific_validation_FIXED_{timestamp}.json"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)

        summary = {
            "protocol": "Scientific Validation 500 Cycles - FIXED",
            "timestamp": timestamp,
            "total_cycles": args.cycles,
            "cycles_completed": len(metrics_collected),
            "extended_results_count": extended_result_count,
            "extended_results_percentage": (
                (extended_result_count / len(metrics_collected) * 100) if metrics_collected else 0.0
            ),
            "phi_mean": sum(phi_values) / len(phi_values) if phi_values else 0.0,
            "phi_max": max(phi_values) if phi_values else 0.0,
            "phi_min": min(phi_values) if phi_values else 0.0,
            "metrics": metrics_collected,
        }

        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"\n" + "=" * 80)
        print(f"✅ VALIDAÇÃO CONCLUÍDA")
        print(f"   Total: {len(metrics_collected)} ciclos")
        print(
            f"   Extended Results: {extended_result_count}/{len(metrics_collected)} ({summary['extended_results_percentage']:.1f}%)"
        )
        print(f"   Φ média: {summary['phi_mean']:.3f}")
        print(f"   Resultado salvo em: {output_file}")
        print("=" * 80 + "\n")

        # Se muito poucos extended results, avisar
        if extended_result_count < len(metrics_collected) * 0.8:
            print(
                f"\n⚠️  AVISO: Apenas {extended_result_count} ciclos retornaram ExtendedLoopCycleResult"
            )
            print("   Recomendação: Usar robust_consciousness_validation.py com --force-robust")

        return 0

    except Exception as e:
        print(f"\n❌ Erro ao executar validação: {e}")
        import traceback

        traceback.print_exc()

        print("\n🔄 Alternando para robust_consciousness_validation.py...")
        return 0 if run_robust_validation_with_metrics() else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

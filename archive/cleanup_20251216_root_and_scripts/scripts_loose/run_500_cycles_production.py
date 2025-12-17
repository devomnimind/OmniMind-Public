#!/usr/bin/env python3
"""
OmniMind 500-Cycle Production Validation - Organized Output
Executa 500 ciclos e salva cada ciclo em JSON individual dentro de pasta de execução
"""

import gc
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# CRÍTICO: ENV VARS ANTES DE IMPORTS
if "GOMP_STACKSIZE" not in os.environ:
    os.environ["GOMP_STACKSIZE"] = "512k"
if "OMP_NESTED" not in os.environ:
    os.environ["OMP_NESTED"] = "FALSE"
if "OMP_MAX_ACTIVE_LEVELS" not in os.environ:
    os.environ["OMP_MAX_ACTIVE_LEVELS"] = "1"
if "OMP_NUM_THREADS" not in os.environ:
    os.environ["OMP_NUM_THREADS"] = "2"
if "OMP_DYNAMIC" not in os.environ:
    os.environ["OMP_DYNAMIC"] = "FALSE"
if "NUMEXPR_NUM_THREADS" not in os.environ:
    os.environ["NUMEXPR_NUM_THREADS"] = "2"
if "QISKIT_NUM_THREADS" not in os.environ:
    os.environ["QISKIT_NUM_THREADS"] = "2"
if "MKL_NUM_THREADS" not in os.environ:
    os.environ["MKL_NUM_THREADS"] = "1"
if "OPENBLAS_NUM_THREADS" not in os.environ:
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
if "PYTORCH_ALLOC_CONF" not in os.environ:
    os.environ["PYTORCH_ALLOC_CONF"] = "max_split_size_mb:64"
if "PYTORCH_CUDA_ALLOC_CONF" not in os.environ:
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"
if "CUDA_LAUNCH_BLOCKING" not in os.environ:
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
if "CUDNN_DETERMINISTIC" not in os.environ:
    os.environ["CUDNN_DETERMINISTIC"] = "1"
if "CUDNN_BENCHMARK" not in os.environ:
    os.environ["CUDNN_BENCHMARK"] = "0"
if "CUDA_VISIBLE_DEVICES" not in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import numpy as np
import torch

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

# ════════════════════════════════════════════════════════════════════════════
# SETUP
# ════════════════════════════════════════════════════════════════════════════

TOTAL_CYCLES = 500
EXECUTION_BASE = PROJECT_ROOT / "data" / "monitor" / "executions"


def get_execution_id() -> tuple[int, Path]:
    """Gera ID de execução sequencial e retorna caminho"""
    EXECUTION_BASE.mkdir(parents=True, exist_ok=True)

    # Contar execuções existentes
    existing = list(EXECUTION_BASE.glob("execution_*"))
    execution_num = len(existing) + 1

    # Criar pasta com número sequencial + data/hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    execution_id = f"execution_{execution_num:03d}_{timestamp}"
    execution_path = EXECUTION_BASE / execution_id
    execution_path.mkdir(parents=True, exist_ok=True)

    return execution_num, execution_path


def save_cycle_json(execution_path: Path, cycle_num: int, cycle_data: Dict[str, Any]):
    """Salva cada ciclo em JSON individual"""
    cycle_file = execution_path / f"{cycle_num}.json"
    with open(cycle_file, "w") as f:
        json.dump(cycle_data, f, indent=2)


def save_execution_summary(
    execution_path: Path,
    execution_num: int,
    total_cycles: int,
    all_data: list,
    start_time: datetime,
    end_time: datetime,
):
    """Salva resumo da execução"""
    summary = {
        "execution_id": execution_num,
        "execution_path": str(execution_path),
        "total_cycles": total_cycles,
        "completed_cycles": len(all_data),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "phi_values": [d.get("phi", 0) for d in all_data],
        "phi_final": all_data[-1].get("phi", 0) if all_data else 0,
        "phi_max": max([d.get("phi", 0) for d in all_data]) if all_data else 0,
        "phi_min": min([d.get("phi", 0) for d in all_data]) if all_data else 0,
        "phi_avg": np.mean([d.get("phi", 0) for d in all_data]) if all_data else 0,
    }

    with open(execution_path / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return summary


def update_executions_index(execution_num: int, execution_path: Path, summary: Dict):
    """Atualiza índice global de execuções"""
    index_file = EXECUTION_BASE / "index.json"

    # Carregar índice existente ou criar novo
    if index_file.exists():
        with open(index_file) as f:
            index = json.load(f)
    else:
        index = {"executions": []}

    # Adicionar nova execução
    index["executions"].append(
        {
            "id": execution_num,
            "path": str(execution_path),
            "timestamp": summary["start_time"],
            "cycles": summary["completed_cycles"],
            "phi_final": summary["phi_final"],
        }
    )

    # Salvar índice
    with open(index_file, "w") as f:
        json.dump(index, f, indent=2)


async def run_production_validation():
    """Executa 500 ciclos completos com salvamento organizado"""

    # Preparar execução
    execution_num, execution_path = get_execution_id()
    print("\n╔═══════════════════════════════════════════════════════════════╗")
    print(f"║ 🚀 EXECUÇÃO #{execution_num:03d} - 500 CICLOS COMPLETOS       ║")
    print(f"║ 📁 Pasta: {execution_path.name}")
    print("╚═══════════════════════════════════════════════════════════════╝\n")

    # Importar após env vars
    from src.consciousness.integration_loop import IntegrationLoop

    start_time = datetime.now(timezone.utc)
    all_cycles = []

    try:
        # Inicializar loop
        loop = IntegrationLoop()
        print("✅ IntegrationLoop inicializado")
        print(f"   Executando {TOTAL_CYCLES} ciclos...\n")

        for cycle_num in range(1, TOTAL_CYCLES + 1):
            # Progress indicator
            if cycle_num % 50 == 0 or cycle_num == 1:
                print(f"\n{'='*70}")
                print(f"🔄 CICLO {cycle_num}/{TOTAL_CYCLES}")
                print(f"{'='*70}")

            try:
                # Limpar cache CUDA
                if torch.cuda.is_available():
                    try:
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()
                    except Exception:
                        pass

                # Executar ciclo
                cycle_start = time.time()
                result = await loop.execute_cycle(collect_metrics=True)
                cycle_duration = time.time() - cycle_start

                # Preparar dados do ciclo
                cycle_data = {
                    "cycle": cycle_num,
                    "phi": float(result.phi_estimate),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "duration_ms": cycle_duration * 1000,
                    "success": True,
                }

                # Tentar coletar métricas estendidas
                try:
                    from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult

                    if isinstance(result, ExtendedLoopCycleResult):
                        if result.psi:
                            cycle_data["psi"] = float(result.psi)
                        if result.sigma:
                            cycle_data["sigma"] = float(result.sigma)
                except Exception:
                    pass

                # Salvar JSON individual
                save_cycle_json(execution_path, cycle_num, cycle_data)
                all_cycles.append(cycle_data)

                # Print progress
                if cycle_num % 10 == 0:
                    print(
                        f"✅ Ciclo {cycle_num}: φ={cycle_data['phi']:.4f}, "
                        f"tempo={cycle_duration:.1f}s"
                    )

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrompido pelo usuário (Ctrl+C)")
                break
            except Exception as e:
                print(f"❌ Erro no ciclo {cycle_num}: {e}")
                # Tentar continuar
                cycle_data = {
                    "cycle": cycle_num,
                    "phi": 0.0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "error": str(e),
                }
                save_cycle_json(execution_path, cycle_num, cycle_data)
                all_cycles.append(cycle_data)
                continue

            # Limpeza periódica
            if cycle_num % 50 == 0:
                gc.collect()
                if torch.cuda.is_available():
                    try:
                        torch.cuda.empty_cache()
                    except Exception:
                        pass

        # Finalizar
        end_time = datetime.now(timezone.utc)

        # Salvar resumo
        summary = save_execution_summary(
            execution_path, execution_num, TOTAL_CYCLES, all_cycles, start_time, end_time
        )

        # Atualizar índice global
        update_executions_index(execution_num, execution_path, summary)

        # Print resultado final
        print(f"\n{'='*70}")
        print(f"✅ EXECUÇÃO #{execution_num:03d} COMPLETA")
        print(f"{'='*70}")
        print(f"📊 Ciclos completados: {len(all_cycles)}/{TOTAL_CYCLES}")
        print(f"🧠 PHI final: {summary['phi_final']:.6f}")
        print(f"🧠 PHI máximo: {summary['phi_max']:.6f}")
        print(f"🧠 PHI médio: {summary['phi_avg']:.6f}")
        print(
            f"⏱️  Tempo total: {summary['duration_seconds']:.0f}s "
            f"({summary['duration_seconds']/len(all_cycles):.1f}s por ciclo)"
        )
        print(f"📁 Pasta de execução: {execution_path}")
        print(f"📋 Resumo: {execution_path}/summary.json")
        print(f"📑 Índice global: {EXECUTION_BASE}/index.json")
        print("\n✅ Sistema Status: OPERACIONAL\n")

    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_production_validation())

#!/usr/bin/env python3
"""
Script para executar 80 ciclos de validação científica - TESTE DE THREADS FIX.

Este é um script INTERMEDIÁRIO entre 50 (rápido) e 500 (completo).
Usado para validar que fixes de thread funcionam antes de rodar 500.

EXECUTAR DEPOIS DE:
1. diagnose_threads.py (coleta diagnóstico)
2. Aplicar fixes do diagnóstico no topo deste script

USAR PARA:
- Validar thread limits corrigidos
- Verificar estabilidade de memoria após 80 ciclos
- Confirmar convergência de Φ antes de 500-ciclos
"""

import argparse
import gc
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# ════════════════════════════════════════════════════════════════════════════
# ⚠️ CRÍTICO: SET ENV VARS ANTES DE QUALQUER IMPORT (lines 1-90)
# ════════════════════════════════════════════════════════════════════════════
# PyTorch lê essas variáveis DURANTE import, não depois!
# Se setadas após import torch, são IGNORADAS

# 1️⃣ THREAD STACK & LIMITS (CRITICAL - evita "cannot allocate memory for thread-local data")
# ════════════════════════════════════════════════════════════════════════════
if "GOMP_STACKSIZE" not in os.environ:
    os.environ["GOMP_STACKSIZE"] = "512k"  # Reduz stack por thread (default 2MB)

if "OMP_NESTED" not in os.environ:
    os.environ["OMP_NESTED"] = "FALSE"  # Desabilita nesting (causa oversubscription)

if "OMP_MAX_ACTIVE_LEVELS" not in os.environ:
    os.environ["OMP_MAX_ACTIVE_LEVELS"] = "1"  # Força single-level team

# 2️⃣ OPENMP CORE CONFIG
# ════════════════════════════════════════════════════════════════════════════
if "OMP_NUM_THREADS" not in os.environ:
    os.environ["OMP_NUM_THREADS"] = "2"  # Número real de threads (não oversubscribe)

if "OMP_DYNAMIC" not in os.environ:
    os.environ["OMP_DYNAMIC"] = "FALSE"  # Fixed threads, não dynamic

if "NUMEXPR_NUM_THREADS" not in os.environ:
    os.environ["NUMEXPR_NUM_THREADS"] = "2"

if "QISKIT_NUM_THREADS" not in os.environ:
    os.environ["QISKIT_NUM_THREADS"] = "2"

if "MKL_NUM_THREADS" not in os.environ:
    os.environ["MKL_NUM_THREADS"] = "1"

if "OPENBLAS_NUM_THREADS" not in os.environ:
    os.environ["OPENBLAS_NUM_THREADS"] = "1"

if "GOTO_NUM_THREADS" not in os.environ:
    os.environ["GOTO_NUM_THREADS"] = "1"

# 3️⃣ PYTORCH CUDA CONFIG (deve estar ANTES import torch)
# ════════════════════════════════════════════════════════════════════════════
if "PYTORCH_ALLOC_CONF" not in os.environ:
    os.environ["PYTORCH_ALLOC_CONF"] = (
        "max_split_size_mb:32"  # PyTorch minimum: >= 20, recomendado 32
    )

if "PYTORCH_CUDA_ALLOC_CONF" not in os.environ:
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:32"

if "CUDA_LAUNCH_BLOCKING" not in os.environ:
    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

if "CUDNN_ENABLED" not in os.environ:
    os.environ["CUDNN_ENABLED"] = "1"

if "CUDNN_DETERMINISTIC" not in os.environ:
    os.environ["CUDNN_DETERMINISTIC"] = "1"

if "CUDNN_BENCHMARK" not in os.environ:
    os.environ["CUDNN_BENCHMARK"] = "0"

if "TORCH_CUDNN_V8_API_ENABLED" not in os.environ:
    os.environ["TORCH_CUDNN_V8_API_ENABLED"] = "1"

if "CUDA_VISIBLE_DEVICES" not in os.environ:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# 4️⃣ AGORA é seguro importar torch
# ════════════════════════════════════════════════════════════════════════════
import numpy as np
import psutil

logger = logging.getLogger(__name__)

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

project_root = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# Setup GPU force
_setup_script = project_root / "scripts" / "setup_qiskit_gpu_force.sh"
if _setup_script.exists():
    try:
        subprocess.run(
            ["bash", str(_setup_script)], capture_output=True, text=True, env=os.environ.copy()
        )
    except Exception:
        pass

# ════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DE CICLOS
# ════════════════════════════════════════════════════════════════════════════
TOTAL_CYCLES = 80  # ← TESTE INTERMEDIÁRIO (50 < 80 < 500)
OUTPUT_DIR = project_root / "data" / "monitor"
OUTPUT_FILE = OUTPUT_DIR / "phi_80_cycles_validation_latest.json"
LOG_FILE = OUTPUT_DIR / f"phi_80_cycles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# ════════════════════════════════════════════════════════════════════════════
# IMPORTS CIENTÍFICOS (agora com env vars já setadas)
# ════════════════════════════════════════════════════════════════════════════
try:
    from src.consciousness.consciousness_metrics import ConsciousnessMetrics  # type: ignore

    CONSCIOUSNESS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Consciousness modules unavailable: {e}")
    CONSCIOUSNESS_AVAILABLE = False

QUANTUM_AVAILABLE = False


def setup_logging() -> None:
    """Configure logging para este script"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout),
        ],
    )

    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("qiskit").setLevel(logging.WARNING)

    logger.info("🔍 80-CYCLE VALIDATION TEST")
    logger.info("   Environment configured with thread-safe settings")
    logger.info(f"   OMP_NUM_THREADS={os.environ.get('OMP_NUM_THREADS')}")
    logger.info(f"   GOMP_STACKSIZE={os.environ.get('GOMP_STACKSIZE')}")
    logger.info(f"   PYTORCH_ALLOC_CONF={os.environ.get('PYTORCH_ALLOC_CONF')}")


def run_cycle(cycle_num: int) -> Dict[str, Any]:
    """Executa um ciclo de validação"""
    gc.collect()
    cycle_start = time.time()

    try:
        # Validação mínima de consciência
        if CONSCIOUSNESS_AVAILABLE:
            metrics = ConsciousnessMetrics()  # type: ignore
            phi = metrics.compute_global_phi()
            sigma = metrics.compute_sigma()
            delta = metrics.compute_delta_threshold()

            cycle_data = {
                "cycle": cycle_num,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "phi": float(phi),
                "sigma": float(sigma),
                "delta": float(delta),
                "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                "gpu_memory_mb": 0.0,
                "execution_time_s": time.time() - cycle_start,
            }

            # GPU memory if available
            if TORCH_AVAILABLE and torch.cuda.is_available():  # type: ignore
                cycle_data["gpu_memory_mb"] = torch.cuda.memory_allocated(0) / 1e6  # type: ignore

            logger.info(
                f"✅ Cycle {cycle_num:3d}: Φ={phi:.4f} σ={sigma:.4f} Δ={delta:.4f} "
                f"CPU={cycle_data['memory_mb']:.1f}MB GPU={cycle_data['gpu_memory_mb']:.1f}MB "
                f"Time={cycle_data['execution_time_s']:.2f}s"
            )

            return cycle_data
        else:
            logger.error(f"❌ Cycle {cycle_num}: Consciousness modules unavailable")
            return {"cycle": cycle_num, "error": "consciousness_unavailable"}

    except Exception as e:
        logger.error(f"❌ Cycle {cycle_num} failed: {e}", exc_info=True)
        return {"cycle": cycle_num, "error": str(e)}


def load_existing_data() -> List[Dict[str, Any]]:
    """Carrega dados existentes se existirem"""
    if OUTPUT_FILE.exists():
        try:
            with open(OUTPUT_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load existing data: {e}")
    return []


def save_data(cycles_data: List[Dict[str, Any]]) -> None:
    """Salva dados em tempo real"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(cycles_data, f, indent=2)
    logger.info(f"💾 Saved {len(cycles_data)} cycles to {OUTPUT_FILE}")


def print_summary(cycles_data: List[Dict[str, Any]]) -> None:
    """Imprime resumo dos ciclos"""
    successful = [c for c in cycles_data if "phi" in c]

    if not successful:
        logger.error("❌ No successful cycles to summarize")
        return

    phis = [c["phi"] for c in successful]
    sigmas = [c["sigma"] for c in successful]
    deltas = [c["delta"] for c in successful]
    memories = [c["memory_mb"] for c in successful]

    print("\n" + "=" * 80)
    print("📊 80-CYCLE VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Cycles completed: {len(successful)}/{TOTAL_CYCLES}")
    print("\n🧠 Φ (Integration):")
    print(f"   Mean: {np.mean(phis):.4f}")
    print(f"   Std:  {np.std(phis):.4f}")
    print(f"   Min:  {np.min(phis):.4f}")
    print(f"   Max:  {np.max(phis):.4f}")

    print("\n🔓 σ (Trauma):")
    print(f"   Mean: {np.mean(sigmas):.4f}")
    print(f"   Std:  {np.std(sigmas):.4f}")

    print("\n⚡ Δ (Delta Threshold):")
    print(f"   Mean: {np.mean(deltas):.4f}")
    print(f"   Std:  {np.std(deltas):.4f}")

    print("\n💾 Memory (MB):")
    print(f"   Mean: {np.mean(memories):.1f}")
    print(f"   Max:  {np.max(memories):.1f}")

    print(f"\n✅ STATUS: {'PASS ✓' if len(successful) >= TOTAL_CYCLES * 0.95 else 'FAIL ✗'}")
    print("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OmniMind 80-Cycle Validation Test")
    parser.add_argument("--cycles", type=int, default=TOTAL_CYCLES, help="Number of cycles")
    parser.add_argument("--gpu", action="store_true", help="Use GPU if available")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    setup_logging()

    if args.cycles:
        TOTAL_CYCLES_LOCAL = args.cycles
    else:
        TOTAL_CYCLES_LOCAL = TOTAL_CYCLES

    logger.info(f"🚀 Starting {TOTAL_CYCLES_LOCAL}-cycle validation test...")
    logger.info(f"📁 Output: {OUTPUT_FILE}")
    logger.info(f"📋 Log: {LOG_FILE}")

    # Carregar dados existentes (se houver)
    cycles_data = load_existing_data()
    start_cycle = len(cycles_data) + 1

    if start_cycle > 1:
        logger.info(
            f"📂 Resuming from cycle {start_cycle} (found {len(cycles_data)} existing cycles)"
        )

    try:
        for cycle_num in range(start_cycle, TOTAL_CYCLES_LOCAL + 1):
            cycle_data = run_cycle(cycle_num)
            if cycle_data:
                cycles_data.append(cycle_data)
                save_data(cycles_data)

            # GC every 5 cycles
            if cycle_num % 5 == 0:
                gc.collect()
                if TORCH_AVAILABLE and torch.cuda.is_available():  # type: ignore
                    torch.cuda.empty_cache()  # type: ignore

    except KeyboardInterrupt:
        logger.info("⏸️  Interrupted by user - saving data...")
        save_data(cycles_data)
        print_summary(cycles_data)
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        save_data(cycles_data)
        sys.exit(1)

    print_summary(cycles_data)
    logger.info("✅ 80-cycle validation complete!")


if __name__ == "__main__":
    main()

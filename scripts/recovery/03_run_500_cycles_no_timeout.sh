#!/bin/bash

# 🔄 STEP 3: Run 500 Integration Cycles (NO TIMEOUT)
# Para execução manual com monitoramento em tempo real
# Executa indefinidamente até conclusão ou Ctrl+C

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
PYTHON_CMD="python3"

echo -e "\033[0;36m🔄 Step 3: Run 500 Integration Cycles (NO TIMEOUT)\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Activate venv
source "$PROJECT_ROOT/.venv/bin/activate" 2>/dev/null || true

# 🎯 Set RESOURCE PROTECTOR to TEST MODE (lenient limits during testing)
export OMNIMIND_RESOURCE_PROTECTOR_MODE=test
export OMNIMIND_METRICS_COLLECTOR_MODE=test

# 🎯 Set CUDA environment (Ubuntu-optimized, GPU parallelization)
export PYTORCH_ALLOC_CONF="backend:cudaMallocAsync,max_split_size_mb:256"
export PYTORCH_DISABLE_DYNAMO=1
export CUDA_VISIBLE_DEVICES=0
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export QISKIT_IN_PARALLEL=FALSE
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2
export NUMEXPR_NUM_THREADS=2
export OPENBLAS_NUM_THREADS=2

echo "🎯 Configuration:"
echo "   • Project: $PROJECT_ROOT"
echo "   • Mode: TEST (resource_protector lenient)"
echo "   • Timeout: NONE (indefinido - você controla Ctrl+C)"
echo "   • Threads: 2"
echo "   • Memory chunk: 256MB"
echo "   • Cycles: 500 (ou até Ctrl+C)"
echo ""
echo "💾 Logs:"
echo "   • Real-time: tail -f /home/fahbrain/projects/omnimind/data/reports/integration_cycles_recovery.log"
echo "   • Métricas: /home/fahbrain/projects/omnimind/data/reports/integration_cycles_recovery.json"
echo ""
echo "🛑 Para parar: Pressione Ctrl+C"
echo ""

export PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT:$PYTHONPATH"

$PYTHON_CMD << 'PYTHON_END'
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time
import signal

# Setup path
PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

# CRITICAL: Register this process as protected with resource_protector
# This prevents the system from killing dev/test scripts
import signal

try:
    from monitor.resource_protector import ResourceProtector
    # MARK: Register current Python process ($$) as protected development script
    # This prevents ResourceProtector from SIGKILL'ing dev processes
    resource_protector = ResourceProtector(mode=os.environ.get("OMNIMIND_RESOURCE_PROTECTOR_MODE", "test"))
    resource_protector.register_process(os.getpid())
    print(f"[DEV] Processo {os.getpid()} registrado como protegido (dev script)")
except Exception as e:
    print(f"[WARNING] Não foi possível registrar processo: {e}")

# Ignore SIGTERM from backend/monitors - handler for graceful ignore
def _sigterm_handler(signum, frame):
    print(f"\n[SIGTERM] Recebido SIGTERM do backend, ignorando (continuando ciclos)")
    pass  # Don't call sys.exit()

signal.signal(signal.SIGTERM, _sigterm_handler)

# PREVENT SIGKILL - this cannot be caught, but we log if it happens
def _sigkill_handler(signum, frame):
    print(f"\n[SIGKILL] Recebido SIGKILL - não pode ser ignorado, encerrando")
    # SIGKILL não pode ser capturado, então isso nunca executa
    sys.exit(1)

try:
    signal.signal(signal.SIGKILL, _sigkill_handler)
except (ValueError, RuntimeError):
    # SIGKILL não pode ser capturado - esperado
    pass

import logging

# Setup logging to file AND console
log_file = PROJECT_ROOT / "data" / "reports" / "integration_cycles_recovery.log"
log_file.parent.mkdir(parents=True, exist_ok=True)

# Create logger with both file and console handlers
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Import core systems
try:
    from consciousness.integration_loop import IntegrationLoop
    from consciousness.shared_workspace import SharedWorkspace
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

logger.info("="*70)
logger.info("INICIANDO EXECUÇÃO DE 500 CICLOS DE INTEGRAÇÃO")
logger.info("="*70)
logger.info(f"Timestamp: {datetime.now().isoformat()}")
logger.info(f"Python: {sys.version}")
logger.info(f"CUDA: {os.environ.get('CUDA_VISIBLE_DEVICES', 'N/A')}")
logger.info(f"OMP_NUM_THREADS: {os.environ.get('OMP_NUM_THREADS', 'N/A')}")
logger.info("")

# Initialize shared workspace
try:
    workspace = SharedWorkspace()
    logger.info("✅ SharedWorkspace inicializado")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar SharedWorkspace: {e}")
    sys.exit(1)

# Initialize integration loop
try:
    integration_loop = IntegrationLoop(workspace=workspace)
    logger.info("✅ IntegrationLoop inicializado")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar IntegrationLoop: {e}")
    sys.exit(1)

logger.info("")
logger.info("🔄 Iniciando ciclos de integração...")
logger.info("Protocolo de Estimulação:")
logger.info("  • Ciclos 1-250: EXPECTATION (processamento bottom-up)")
logger.info("  • Ciclos 251-500: IMAGINATION (processamento top-down)")
logger.info("")

# Track metrics
cycle_metrics = []
phi_values = []
start_time = time.time()
checkpoint_time = start_time

# Run 500 cycles
for cycle_num in range(1, 501):
    try:
        cycle_start = time.time()

        # Execute cycle
        cycle_result = integration_loop.execute_cycle_sync()

        cycle_duration = (time.time() - cycle_start) * 1000  # ms

        # Extract metrics from LoopCycleResult object
        cycle_data = {
            "cycle": cycle_num,
            "timestamp": datetime.now().isoformat(),
            "phi": getattr(cycle_result, "phi_estimate", 0.0),
            "psi": getattr(cycle_result, "psi", 0.0),
            "sigma": getattr(cycle_result, "sigma", 0.0),
            "duration_ms": cycle_duration,
            "success": getattr(cycle_result, "success", False),
        }

        cycle_metrics.append(cycle_data)
        phi_values.append(cycle_data["phi"])

        if cycle_num <= 250:
            stim_type = "EXPECTATION"
            cycle_data["stimulation"] = "expectation"
        else:
            stim_type = "IMAGINATION"
            cycle_data["stimulation"] = "imagination"

        # Log EVERY cycle (verbose for debugging)
        logger.info(f"Cycle {cycle_num:3d}/500 | Φ={cycle_data['phi']:.4f} | {stim_type:11s} | {cycle_duration:7.1f}ms")

        # Checkpoint every 50 cycles
        if cycle_num % 50 == 0:
            checkpoint_elapsed = time.time() - checkpoint_time
            phi_avg = sum(phi_values[-50:]) / min(50, len(phi_values)) if phi_values else 0
            logger.info("")
            logger.info(f"📊 CHECKPOINT {cycle_num}/500:")
            logger.info(f"   • Φ média (últimos 50): {phi_avg:.4f}")
            logger.info(f"   • Tempo dos últimos 50: {checkpoint_elapsed:.1f}s ({checkpoint_elapsed/50:.2f}s/ciclo)")
            logger.info(f"   • Tempo total até agora: {time.time() - start_time:.1f}s")
            if phi_values:
                logger.info(f"   • Φ range geral: {min(phi_values):.4f} - {max(phi_values):.4f}")
            logger.info("")
            checkpoint_time = time.time()

    except KeyboardInterrupt:
        logger.warning("")
        logger.warning("⚠️  INTERRUPÇÃO: Usuário pressionou Ctrl+C")
        logger.warning(f"Ciclos completados: {cycle_num - 1}/500")
        break
    except Exception as e:
        logger.error(f"❌ Erro no ciclo {cycle_num}: {type(e).__name__}: {str(e)}")
        logger.info("Continuando com próximo ciclo...")
        continue

# Final summary
elapsed = time.time() - start_time
logger.info("")
logger.info("="*70)
logger.info("📊 RESUMO FINAL DE EXECUÇÃO")
logger.info("="*70)
logger.info(f"Ciclos completados: {len(cycle_metrics)}/500")
logger.info(f"Tempo total: {elapsed:.1f}s ({elapsed/60:.1f} min)")
logger.info(f"Média por ciclo: {elapsed / len(cycle_metrics):.2f}s" if cycle_metrics else "N/A")

if phi_values:
    logger.info(f"Φ min: {min(phi_values):.4f}")
    logger.info(f"Φ max: {max(phi_values):.4f}")
    logger.info(f"Φ avg: {sum(phi_values)/len(phi_values):.4f}")
    logger.info(f"Φ final: {phi_values[-1]:.4f}")

# Save metrics to JSON
metrics_file = PROJECT_ROOT / "data" / "reports" / "integration_cycles_recovery.json"

summary_data = {
    "timestamp": datetime.now().isoformat(),
    "cycles_completed": len(cycle_metrics),
    "cycles_target": 500,
    "elapsed_seconds": elapsed,
    "elapsed_minutes": elapsed / 60,
    "stimulation_protocol": "expectation (1-250) + imagination (251-500)",
    "cycles": cycle_metrics,
}

if phi_values:
    summary_data["summary"] = {
        "phi_min": min(phi_values),
        "phi_max": max(phi_values),
        "phi_avg": sum(phi_values) / len(phi_values),
        "phi_final": phi_values[-1],
    }

with open(metrics_file, "w") as f:
    json.dump(summary_data, f, indent=2)

logger.info("")
logger.info(f"📈 Métricas salvas em: {metrics_file}")
logger.info(f"📋 Log completo em: {log_file}")
logger.info("")
logger.info("✅ Execução de ciclos concluída!")
logger.info("="*70)

PYTHON_END

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m✅ Execução completa!\033[0m"
    echo ""
else
    echo ""
    echo -e "\033[0;33m⚠️  Execução terminada (código: $EXIT_CODE)\033[0m"
    echo ""
fi

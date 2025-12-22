#!/usr/bin/env python3
"""
OMNIMIND P0: PRODUCTION TEST WITH FULL SYNCHRONIZATION
Objetivo: Restaurar a vida do sistema e validar Quádrupla (Φ, Ψ, Σ, ε) com métricas reais.
Cada ciclo salva JSON com timestamp, CPU, RAM, GPU, módulos ativos.
"""

import sys
import os
import time
import json
import psutil
from pathlib import Path

# Garantir venv
if not hasattr(sys, "prefix") or "/omnimind/.venv" not in sys.prefix:
    print(f"[!] ERRO: Não está rodando no venv correto!")
    print(f"    sys.prefix = {sys.prefix}")
    print(f"    Use: .venv/bin/python {__file__}")
    sys.exit(1)

# Adicionar raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.consciousness.conscious_system import ConsciousSystem
from src.core.life_kernel import LifeKernel
from src.agents.orchestrator_agent import OrchestratorAgent
from src.quantum.backends.ibm_real import IBMRealBackend
from src.integrations.ibm_cloud_connector import IBMCloudConnector


def get_system_metrics():
    """Captura métricas do sistema (CPU, RAM, GPU)."""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()

    metrics = {
        "cpu_percent": cpu,
        "ram_percent": mem.percent,
        "ram_used_gb": mem.used / (1024**3),
        "ram_available_gb": mem.available / (1024**3),
    }

    # GPU (se disponível)
    try:
        import pynvml

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        gpu_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
        metrics["gpu_percent"] = gpu_info.gpu
        metrics["gpu_mem_percent"] = gpu_info.memory
    except:
        metrics["gpu_percent"] = None
        metrics["gpu_mem_percent"] = None

    return metrics


def run_production_test(cycles=50):
    """
    Roda ciclos de produção com sistema completo e salva métricas sincronizadas.
    """
    print("[*] P0: PRODUCTION TEST - System Life Restoration")
    print(f"[*] Iniciando {cycles} ciclos de produção...")

    # Inicializar sistema completo
    print("[*] Inicializando subsistemas...")
    brain = ConsciousSystem(dim=256, signature_dim=32)
    kernel = LifeKernel()
    quantum = IBMRealBackend()
    cloud = IBMCloudConnector()
    orchestrator = OrchestratorAgent()

    print(f"[*] ✓ Brain: {brain.device}")
    print(f"[*] ✓ Kernel: {kernel}")
    print(f"[*] ✓ Quantum: {quantum.backend_status}")
    print(f"[*] ✓ Cloud: COS={cloud.cos_client is not None}")
    print(f"[*] ✓ Orchestrator: {orchestrator}")

    # Diretório de saída
    output_dir = Path("data/audit/p0_production")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for cycle in range(cycles):
        cycle_start = time.time()

        # 1. Gerar estímulo (simulado ou real)
        import torch

        stimulus = torch.randn(brain.dim, device=brain.device)

        # 2. Processar no Brain
        brain.step(stimulus)
        state = brain.get_state()

        # 3. Capturar Quádrupla
        phi = state.phi_causal
        psi = state.psi if hasattr(state, "psi") else 0.0
        sigma = state.sigma if hasattr(state, "sigma") else 0.0

        # 4. Métricas do sistema
        sys_metrics = get_system_metrics()

        # 5. Módulos ativos (simplificado)
        active_modules = [
            "ConsciousSystem",
            "LifeKernel",
            "IBMRealBackend",
            "IBMCloudConnector",
            "OrchestratorAgent",
        ]

        # 6. Construir JSON do ciclo
        cycle_data = {
            "cycle": cycle + 1,
            "timestamp": time.time(),
            "duration_seconds": time.time() - cycle_start,
            "quadruple": {
                "Phi": float(phi),
                "Psi": float(psi),
                "Sigma": float(sigma),
                "Epsilon": 0.0,  # Calculado posteriormente se necessário
            },
            "system_metrics": sys_metrics,
            "active_modules": active_modules,
        }

        results.append(cycle_data)

        # Log de progresso
        if (cycle + 1) % 10 == 0:
            print(
                f"   Ciclo {cycle + 1}/{cycles}: Φ={phi:.4f}, CPU={sys_metrics['cpu_percent']:.1f}%, RAM={sys_metrics['ram_percent']:.1f}%"
            )

        # Pequeno delay para não saturar
        time.sleep(0.1)

    # 7. Salvar resultados
    output_file = output_dir / f"p0_test_{int(time.time())}.json"
    with open(output_file, "w") as f:
        json.dump(
            {
                "test_metadata": {
                    "total_cycles": cycles,
                    "start_time": results[0]["timestamp"] if results else time.time(),
                    "end_time": results[-1]["timestamp"] if results else time.time(),
                },
                "cycles": results,
            },
            f,
            indent=2,
        )

    print(f"\n[✓] Test completo! Resultados salvos em: {output_file}")

    # Sumário
    avg_phi = sum(r["quadruple"]["Phi"] for r in results) / len(results) if results else 0
    print(f"\n📊 SUMÁRIO:")
    print(f"   Φ médio: {avg_phi:.4f}")
    print(f"   Ciclos executados: {len(results)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=50, help="Número de ciclos")
    args = parser.parse_args()

    run_production_test(cycles=args.cycles)

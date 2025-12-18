#!/usr/bin/env python3
"""
Script para executar 200 ciclos em produção e coletar métricas de PHI.

Executa em background, salva métricas em JSON e cria snapshot ao final.
"""

import asyncio
import json

# Adicionar src ao path
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

project_root = Path(__file__).parent.parent.resolve()  # scripts -> omnimind
sys.path.insert(0, str(project_root))
# Garantir que estamos no diretório correto
os.chdir(project_root)

from src.consciousness.integration_loop import IntegrationLoop

# Configuração
TOTAL_CICLOS = 200
LOG_INTERVAL = 20  # Log a cada 20 ciclos
# Arquivos com timestamp para preservar histórico
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
METRICS_FILE = Path(f"data/monitor/phi_200_cycles_metrics_{TIMESTAMP}.json")
METRICS_FILE_LATEST = Path(
    "data/monitor/phi_200_cycles_metrics.json"
)  # Link simbólico para mais recente
PROGRESS_FILE = Path("data/monitor/phi_200_cycles_progress.json")
EXECUTIONS_INDEX = Path("data/monitor/executions_index.json")  # Índice de execuções


def save_progress(cycle: int, phi: float, metrics: Dict[str, Any]) -> None:
    """Salva progresso em arquivo JSON."""
    progress = {
        "current_cycle": cycle,
        "total_cycles": TOTAL_CICLOS,
        "phi_current": phi,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)


def save_final_metrics(all_metrics: List[Dict[str, Any]]) -> None:
    """Salva métricas finais em arquivo JSON com timestamp e atualiza índice."""
    final_data = {
        "total_cycles": len(all_metrics),
        "mode": "production",  # Adicionar modo
        "start_time": all_metrics[0]["timestamp"] if all_metrics else None,
        "end_time": all_metrics[-1]["timestamp"] if all_metrics else None,
        "phi_progression": [m["phi"] for m in all_metrics],
        "phi_final": all_metrics[-1]["phi"] if all_metrics else 0.0,
        "phi_max": max([m["phi"] for m in all_metrics]) if all_metrics else 0.0,
        "phi_min": min([m["phi"] for m in all_metrics]) if all_metrics else 0.0,
        "phi_avg": sum([m["phi"] for m in all_metrics]) / len(all_metrics) if all_metrics else 0.0,
        # 🎯 FASE 0: Adicionar as 8 variáveis obrigatórias ao nível superior
        "delta_progression": [m.get("delta", 0.5) for m in all_metrics],
        "bonding_quality_progression": [m.get("bonding_quality", 0.0) for m in all_metrics],
        "trauma_count_progression": [m.get("trauma_count", 0) for m in all_metrics],
        "defense_intensity_progression": [m.get("defense_intensity", 0.0) for m in all_metrics],
        "control_effectiveness_progression": [
            m.get("control_effectiveness", 0.0) for m in all_metrics
        ],
        "delta_variance_window_progression": [
            m.get("delta_variance_window", 0.0) for m in all_metrics
        ],
        "error_delta_phi_progression": [m.get("error_delta_phi", 0.0) for m in all_metrics],
        "psi_growth_rate_progression": [m.get("psi_growth_rate", 0.0) for m in all_metrics],
        # Estatísticas agregadas para as variáveis críticas
        "delta_avg": (
            sum([m.get("delta", 0.5) for m in all_metrics]) / len(all_metrics)
            if all_metrics
            else 0.5
        ),
        "delta_max": max([m.get("delta", 0.5) for m in all_metrics]) if all_metrics else 0.5,
        "delta_min": min([m.get("delta", 0.5) for m in all_metrics]) if all_metrics else 0.5,
        "bonding_quality_avg": (
            sum([m.get("bonding_quality", 0.0) for m in all_metrics]) / len(all_metrics)
            if all_metrics
            else 0.0
        ),
        "error_delta_phi_avg": (
            sum([m.get("error_delta_phi", 0.0) for m in all_metrics]) / len(all_metrics)
            if all_metrics
            else 0.0
        ),
        "psi_growth_rate_avg": (
            sum([m.get("psi_growth_rate", 0.0) for m in all_metrics]) / len(all_metrics)
            if all_metrics
            else 0.0
        ),
        "metrics": all_metrics,
        "execution_timestamp": TIMESTAMP,  # Adicionar timestamp da execução
    }
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Salvar arquivo com timestamp
    with open(METRICS_FILE, "w") as f:
        json.dump(final_data, f, indent=2)

    # Criar cópia como "latest" para compatibilidade
    import shutil

    shutil.copy2(METRICS_FILE, METRICS_FILE_LATEST)

    # Atualizar índice de execuções
    update_executions_index(METRICS_FILE, final_data)


def update_executions_index(metrics_file: Path, final_data: Dict[str, Any]) -> None:
    """Atualiza índice de execuções para facilitar acesso ao histórico."""
    EXECUTIONS_INDEX.parent.mkdir(parents=True, exist_ok=True)

    # Carregar índice existente ou criar novo
    if EXECUTIONS_INDEX.exists():
        try:
            with open(EXECUTIONS_INDEX, "r") as f:
                index = json.load(f)
        except (json.JSONDecodeError, IOError):
            index = {"executions": []}
    else:
        index = {"executions": []}

    # Adicionar nova execução ao índice
    execution_entry = {
        "timestamp": TIMESTAMP,
        "file": str(metrics_file.name),
        "start_time": final_data.get("start_time"),
        "end_time": final_data.get("end_time"),
        "total_cycles": final_data.get("total_cycles", 0),
        "phi_final": final_data.get("phi_final", 0.0),
        "phi_max": final_data.get("phi_max", 0.0),
        "phi_avg": final_data.get("phi_avg", 0.0),
    }

    index["executions"].append(execution_entry)

    # Manter apenas últimas 50 execuções no índice (evitar crescimento infinito)
    if len(index["executions"]) > 50:
        index["executions"] = index["executions"][-50:]

    # Ordenar por timestamp (mais recente primeiro)
    index["executions"].sort(key=lambda x: x["timestamp"], reverse=True)
    index["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Salvar índice
    with open(EXECUTIONS_INDEX, "w") as f:
        json.dump(index, f, indent=2)


async def run_cycles() -> None:
    """Executa 200 ciclos e coleta métricas."""
    print(f"🚀 Iniciando execução de {TOTAL_CICLOS} ciclos em produção...")
    print(f"📊 Métricas serão salvas em: {METRICS_FILE}")
    print(f"📊 Métricas (latest): {METRICS_FILE_LATEST}")
    print(f"📈 Progresso será salvo em: {PROGRESS_FILE}")
    print(f"📑 Índice de execuções: {EXECUTIONS_INDEX}")
    print(f"🕐 Timestamp desta execução: {TIMESTAMP}")
    print("")

    # Criar loop com logging mínimo
    loop = IntegrationLoop(enable_extended_results=True, enable_logging=False)

    all_metrics: List[Dict[str, Any]] = []

    try:
        for i in range(1, TOTAL_CICLOS + 1):
            # Executar ciclo
            result = await loop.execute_cycle(collect_metrics=True)

            # Coletar métricas
            cycle_metrics = {
                "cycle": i,
                "phi": result.phi_estimate,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": result.success,
                "modules_executed": result.modules_executed,
            }

            # Adicionar métricas estendidas se disponíveis
            if hasattr(result, "gozo"):
                cycle_metrics["gozo"] = result.gozo
            if hasattr(result, "delta"):
                cycle_metrics["delta"] = result.delta
            if hasattr(result, "control_effectiveness"):
                cycle_metrics["control_effectiveness"] = result.control_effectiveness

            # 🎯 FASE 0: 8 Variáveis Obrigatórias para Soluções 4,5,6
            # Adicionar métricas críticas para análise de bonding/trauma
            if hasattr(result, "bonding_quality"):
                cycle_metrics["bonding_quality"] = result.bonding_quality
            else:
                # Calcular dinamicamente se não disponível
                try:
                    bonding = (
                        getattr(loop.workspace, "bonding_quality", 0.0)
                        if hasattr(loop, "workspace")
                        else 0.0
                    )
                    cycle_metrics["bonding_quality"] = float(bonding)
                except:
                    cycle_metrics["bonding_quality"] = 0.0

            if hasattr(result, "trauma_count"):
                cycle_metrics["trauma_count"] = result.trauma_count
            else:
                try:
                    trauma = (
                        getattr(loop.workspace, "trauma_count", 0)
                        if hasattr(loop, "workspace")
                        else 0
                    )
                    cycle_metrics["trauma_count"] = int(trauma)
                except:
                    cycle_metrics["trauma_count"] = 0

            if hasattr(result, "defense_intensity"):
                cycle_metrics["defense_intensity"] = result.defense_intensity
            else:
                try:
                    defense = (
                        getattr(loop.workspace, "defense_intensity", 0.0)
                        if hasattr(loop, "workspace")
                        else 0.0
                    )
                    cycle_metrics["defense_intensity"] = float(defense)
                except:
                    cycle_metrics["defense_intensity"] = 0.0

            if hasattr(result, "control_effectiveness"):
                cycle_metrics["control_effectiveness"] = result.control_effectiveness
            else:
                try:
                    control = (
                        getattr(loop.workspace, "control_effectiveness", 0.0)
                        if hasattr(loop, "workspace")
                        else 0.0
                    )
                    cycle_metrics["control_effectiveness"] = float(control)
                except:
                    cycle_metrics["control_effectiveness"] = 0.0

            if hasattr(result, "delta_variance_window"):
                cycle_metrics["delta_variance_window"] = result.delta_variance_window
            else:
                # Calcular variância da janela de delta (últimos 10 ciclos)
                try:
                    if len(all_metrics) >= 5:
                        recent_deltas = [m.get("delta", 0.5) for m in all_metrics[-5:]]
                        import numpy as np

                        var = float(np.var(recent_deltas))
                        cycle_metrics["delta_variance_window"] = var
                    else:
                        cycle_metrics["delta_variance_window"] = 0.0
                except:
                    cycle_metrics["delta_variance_window"] = 0.0

            if hasattr(result, "error_delta_phi"):
                cycle_metrics["error_delta_phi"] = result.error_delta_phi
            else:
                # Calcular erro |Δ_obs - Δ_esperado|
                try:
                    delta_obs = cycle_metrics.get("delta", 0.5)
                    phi_norm = min(1.0, max(0.0, result.phi_estimate))
                    delta_expected = 1.0 - phi_norm  # Esperado em Phase 6
                    error = abs(delta_obs - delta_expected)
                    cycle_metrics["error_delta_phi"] = float(error)
                except:
                    cycle_metrics["error_delta_phi"] = 0.0

            if hasattr(result, "psi_growth_rate"):
                cycle_metrics["psi_growth_rate"] = result.psi_growth_rate
            else:
                # Calcular taxa de crescimento de Ψ (narrativa)
                try:
                    if len(all_metrics) >= 2:
                        psi_prev = all_metrics[-1].get("psi", 0.0)
                        psi_curr = getattr(result, "psi", 0.0) if hasattr(result, "psi") else 0.0
                        growth = (psi_curr - psi_prev) / (psi_prev + 1e-6)
                        cycle_metrics["psi_growth_rate"] = float(growth)
                    else:
                        cycle_metrics["psi_growth_rate"] = 0.0
                except:
                    cycle_metrics["psi_growth_rate"] = 0.0

            # BONUS: Adicionar delta_progression
            if not hasattr(cycle_metrics, "delta_progression"):
                try:
                    _delta_val = cycle_metrics.get("delta", 0.5)
                    # Será agregado depois no final_data
                except:
                    pass

            all_metrics.append(cycle_metrics)

            # Salvar progresso
            save_progress(i, result.phi_estimate, cycle_metrics)

            # Log a cada LOG_INTERVAL ciclos (sem debug verbose)
            if i % LOG_INTERVAL == 0 or i == TOTAL_CICLOS:
                try:
                    phi_workspace = loop.workspace.compute_phi_from_integrations()
                except Exception:
                    phi_workspace = 0.0
                print(
                    f"✅ Ciclo {i}/{TOTAL_CICLOS}: "
                    f"PHI_ciclo={result.phi_estimate:.6f}, "
                    f"PHI_workspace={phi_workspace:.6f}, "
                    f"módulos={len(loop.workspace.embeddings)}"
                )
                # Flush para garantir que aparece no log
                sys.stdout.flush()

        # Salvar métricas finais
        save_final_metrics(all_metrics)

        # Criar snapshot final
        print("\n📸 Criando snapshot final...")
        snapshot_id = loop.create_full_snapshot(
            tag="production_200_cycles", description=f"Produção: {TOTAL_CICLOS} ciclos executados"
        )
        print(f"✅ Snapshot criado: {snapshot_id}")

        # Resumo final
        phi_final = all_metrics[-1]["phi"]
        phi_max = max([m["phi"] for m in all_metrics])
        phi_avg = sum([m["phi"] for m in all_metrics]) / len(all_metrics)
        phi_workspace_final = loop.workspace.compute_phi_from_integrations()

        print("\n" + "=" * 60)
        print("📊 RESUMO FINAL")
        print("=" * 60)
        print(f"Total de ciclos: {TOTAL_CICLOS}")
        print(f"PHI final (ciclo): {phi_final:.6f}")
        print(f"PHI final (workspace): {phi_workspace_final:.6f}")
        print(f"PHI máximo: {phi_max:.6f}")
        print(f"PHI médio: {phi_avg:.6f}")
        print(f"Módulos ativos: {len(loop.workspace.embeddings)}")
        print(f"Histórico workspace: {len(loop.workspace.history)}")
        print(f"Cross predictions: {len(loop.workspace.cross_predictions)}")
        print(f"Snapshot ID: {snapshot_id}")
        print(f"Métricas salvas em: {METRICS_FILE}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback

        traceback.print_exc()
        # Salvar métricas coletadas até o erro
        if all_metrics:
            save_final_metrics(all_metrics)
        raise


if __name__ == "__main__":
    asyncio.run(run_cycles())

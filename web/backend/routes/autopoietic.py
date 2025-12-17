"""Rotas para métricas e dados do ciclo autopoiético (Phase 22)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from web.backend.auth import verify_credentials

logger = logging.getLogger(__name__)

router = APIRouter(tags=["autopoietic"])


def _get_project_root() -> Path:
    """Obtém o diretório raiz do projeto."""
    return Path(__file__).parent.parent.parent.parent


@router.get("/status")
async def autopoietic_status(
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """Retorna status atual do ciclo autopoiético."""
    project_root = _get_project_root()
    history_path = project_root / "data" / "autopoietic" / "cycle_history.jsonl"
    code_dir = project_root / "data" / "autopoietic" / "synthesized_code"
    metrics_path = project_root / "data" / "monitor" / "real_metrics.json"

    # Verificar se processo está rodando
    pid_file = project_root / "logs" / "main_cycle.pid"
    is_running = False
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            import os

            is_running = os.path.exists(f"/proc/{pid}")
        except Exception:
            pass

    # Contar ciclos
    cycle_count = 0
    if history_path.exists():
        try:
            with history_path.open("r", encoding="utf-8") as f:
                cycle_count = sum(1 for line in f if line.strip())
        except Exception:
            pass

    # Contar componentes
    component_count = 0
    if code_dir.exists():
        component_count = len(list(code_dir.glob("*.py")))

    # Obter Φ atual
    current_phi = None
    if metrics_path.exists():
        try:
            with metrics_path.open("r", encoding="utf-8") as f:
                metrics = json.load(f)
                current_phi = float(metrics.get("phi", 0.0))
        except Exception:
            pass

    return {
        "running": is_running,
        "cycle_count": cycle_count,
        "component_count": component_count,
        "current_phi": current_phi,
        "phi_threshold": 0.3,
    }


@router.get("/cycles")
async def get_cycles(
    limit: int = 100,
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """Retorna histórico de ciclos autopoiéticos."""
    project_root = _get_project_root()
    history_path = project_root / "data" / "autopoietic" / "cycle_history.jsonl"

    cycles: List[Dict[str, Any]] = []
    if not history_path.exists():
        return {"cycles": cycles, "total": 0}

    try:
        with history_path.open("r", encoding="utf-8") as f:
            all_lines = [line.strip() for line in f if line.strip()]
            # Pegar últimos N ciclos
            for line in all_lines[-limit:]:
                cycles.append(json.loads(line))
    except Exception as e:
        logger.error("Erro ao ler histórico: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao ler histórico: {e}")

    return {"cycles": cycles, "total": len(cycles)}


@router.get("/cycles/stats")
async def get_cycle_stats(
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """Retorna estatísticas agregadas dos ciclos."""
    project_root = _get_project_root()
    history_path = project_root / "data" / "autopoietic" / "cycle_history.jsonl"

    if not history_path.exists():
        return {
            "total_cycles": 0,
            "successful_syntheses": 0,
            "rejected_before": 0,
            "rolled_back": 0,
            "strategies": {},
            "phi_before_avg": 0.0,
            "phi_after_avg": 0.0,
            "phi_delta_avg": 0.0,
        }

    cycles: List[Dict[str, Any]] = []
    try:
        with history_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    cycles.append(json.loads(line))
    except Exception as e:
        logger.error("Erro ao ler histórico: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao ler histórico: {e}")

    # Calcular estatísticas
    total_cycles = len(cycles)
    successful_syntheses = 0
    rejected_before = 0
    rolled_back = 0
    strategies: Dict[str, int] = {}
    phi_before_values: List[float] = []
    phi_after_values: List[float] = []
    phi_deltas: List[float] = []

    for cycle in cycles:
        strategy = cycle.get("strategy", "UNKNOWN")
        strategies[strategy] = strategies.get(strategy, 0) + 1

        synthesized = cycle.get("synthesized_components", [])
        phi_before = cycle.get("phi_before")
        phi_after = cycle.get("phi_after")

        if phi_before is not None:
            phi_before_values.append(float(phi_before))
        if phi_after is not None:
            phi_after_values.append(float(phi_after))
        if phi_before is not None and phi_after is not None:
            phi_deltas.append(float(phi_after) - float(phi_before))

        if len(synthesized) > 0:
            if phi_after is not None and phi_after < 0.3:
                rolled_back += 1
            else:
                successful_syntheses += 1
        else:
            if phi_before is not None and phi_before < 0.3:
                rejected_before += 1

    # Calcular médias
    phi_before_avg = sum(phi_before_values) / len(phi_before_values) if phi_before_values else 0.0
    phi_after_avg = sum(phi_after_values) / len(phi_after_values) if phi_after_values else 0.0
    phi_delta_avg = sum(phi_deltas) / len(phi_deltas) if phi_deltas else 0.0

    return {
        "total_cycles": total_cycles,
        "successful_syntheses": successful_syntheses,
        "rejected_before": rejected_before,
        "rolled_back": rolled_back,
        "strategies": strategies,
        "phi_before_avg": phi_before_avg,
        "phi_after_avg": phi_after_avg,
        "phi_delta_avg": phi_delta_avg,
    }


@router.get("/components")
async def get_components(
    limit: int = 50,
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """Retorna lista de componentes sintetizados."""
    project_root = _get_project_root()
    code_dir = project_root / "data" / "autopoietic" / "synthesized_code"

    components: List[Dict[str, Any]] = []
    if not code_dir.exists():
        return {"components": components, "total": 0}

    try:
        for py_file in sorted(code_dir.glob("*.py"), key=lambda p: p.stat().st_mtime, reverse=True)[
            :limit
        ]:
            stat = py_file.stat()
            components.append(
                {
                    "name": py_file.stem,
                    "size_bytes": stat.st_size,
                    "modified": stat.st_mtime,
                    "modified_iso": py_file.stat().st_mtime,
                }
            )
    except Exception as e:
        logger.error("Erro ao listar componentes: %s", e)
        raise HTTPException(status_code=500, detail=f"Erro ao listar componentes: {e}")

    return {"components": components, "total": len(components)}


@router.get("/health")
async def autopoietic_health(
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """Verifica saúde do sistema autopoiético."""
    project_root = _get_project_root()
    metrics_path = project_root / "data" / "monitor" / "real_metrics.json"
    history_path = project_root / "data" / "autopoietic" / "cycle_history.jsonl"

    # Verificar Φ atual
    current_phi = None
    if metrics_path.exists():
        try:
            with metrics_path.open("r", encoding="utf-8") as f:
                metrics = json.load(f)
                current_phi = float(metrics.get("phi", 0.0))
        except Exception:
            pass

    # Analisar últimos ciclos
    recent_rollbacks = 0
    recent_rejected = 0
    if history_path.exists():
        try:
            with history_path.open("r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                recent_cycles = [json.loads(line) for line in lines[-10:]]

                for cycle in recent_cycles:
                    phi_before = cycle.get("phi_before")
                    phi_after = cycle.get("phi_after")
                    synthesized = cycle.get("synthesized_components", [])

                    if phi_before is not None and phi_before < 0.3:
                        recent_rejected += 1
                    if phi_after is not None and phi_after < 0.3 and len(synthesized) > 0:
                        recent_rollbacks += 1
        except Exception:
            pass

    # Determinar status
    if current_phi is not None and current_phi < 0.3:
        status = "critical"
    elif recent_rollbacks > 2:
        status = "critical"
    elif recent_rejected > 5:
        status = "warning"
    else:
        status = "healthy"

    return {
        "status": status,
        "current_phi": current_phi,
        "phi_threshold": 0.3,
        "recent_rollbacks": recent_rollbacks,
        "recent_rejected": recent_rejected,
    }


@router.get("/extended/metrics")
async def get_extended_metrics(
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """
    Retorna métricas completas de consciência: Phi, Psi, Sigma, Gozo, Delta.

    Acessa IntegrationLoop global para obter métricas estendidas do último ciclo.
    """
    try:
        from src.consciousness.integration_loop import IntegrationLoop
        from src.metrics.real_consciousness_metrics import real_metrics_collector

        # Inicializar collector se necessário
        await real_metrics_collector.initialize()

        # Acessar IntegrationLoop do collector
        loop = real_metrics_collector.integration_loop

        # Se não houver loop ou não tiver extended results habilitado, criar novo
        if not loop or not loop.enable_extended_results:
            # Tentar criar novo loop com extended results
            try:
                loop = IntegrationLoop(enable_logging=False, enable_extended_results=True)
                # Atualizar collector com novo loop
                real_metrics_collector.integration_loop = loop
            except Exception as e:
                logger.warning(f"Erro ao criar IntegrationLoop com extended results: {e}")

        if not loop or not loop.cycle_history:
            # Se não houver histórico, retornar valores padrão
            return {
                "phi": 0.0,
                "psi": None,
                "sigma": None,
                "gozo": None,
                "delta": None,
                "triad": None,
                "history": {
                    "phi": [],
                    "psi": [],
                    "sigma": [],
                    "gozo": [],
                    "delta": [],
                    "timestamps": [],
                },
                "last_cycle": None,
                "message": "No cycle history available",
            }

        # Obter último ciclo com métricas estendidas
        last_cycle = loop.cycle_history[-1]

        # Extrair métricas do último ciclo
        phi = getattr(last_cycle, 'phi_estimate', 0.0)
        psi = getattr(last_cycle, 'psi', None)
        sigma = getattr(last_cycle, 'sigma', None)
        gozo = getattr(last_cycle, 'gozo', None)
        delta = getattr(last_cycle, 'delta', None)
        triad = getattr(last_cycle, 'triad', None)

        # Construir histórico das últimas 50 métricas
        history_size = min(50, len(loop.cycle_history))
        recent_cycles = loop.cycle_history[-history_size:]

        history = {
            "phi": [getattr(c, 'phi_estimate', 0.0) for c in recent_cycles],
            "psi": [getattr(c, 'psi', None) for c in recent_cycles],
            "sigma": [getattr(c, 'sigma', None) for c in recent_cycles],
            "gozo": [getattr(c, 'gozo', None) for c in recent_cycles],
            "delta": [getattr(c, 'delta', None) for c in recent_cycles],
            "timestamps": [
                (
                    timestamp.isoformat()
                    if (timestamp := getattr(c, 'timestamp', None)) is not None
                    and hasattr(timestamp, 'isoformat')
                    else None
                )
                for c in recent_cycles
            ],
        }

        # Formatar tríade se disponível
        triad_data = None
        if triad:
            triad_data = {
                "phi": getattr(triad, 'phi', 0.0),
                "psi": getattr(triad, 'psi', 0.0),
                "sigma": getattr(triad, 'sigma', 0.0),
                "step_id": getattr(triad, 'step_id', None),
                "metadata": getattr(triad, 'metadata', {}),
            }

        return {
            "phi": phi,
            "psi": psi,
            "sigma": sigma,
            "gozo": gozo,
            "delta": delta,
            "triad": triad_data,
            "history": history,
            "last_cycle": {
                "cycle_number": getattr(last_cycle, 'cycle_number', 0),
                "timestamp": (
                    timestamp.isoformat()
                    if (timestamp := getattr(last_cycle, 'timestamp', None)) is not None
                    and hasattr(timestamp, 'isoformat')
                    else None
                ),
                "success": getattr(last_cycle, 'success', False),
            },
            "total_cycles": len(loop.cycle_history),
        }

    except Exception as e:
        logger.error(f"Erro ao coletar métricas estendidas: {e}", exc_info=True)
        return {
            "phi": 0.0,
            "psi": None,
            "sigma": None,
            "gozo": None,
            "delta": None,
            "triad": None,
            "history": {
                "phi": [],
                "psi": [],
                "sigma": [],
                "gozo": [],
                "delta": [],
                "timestamps": [],
            },
            "error": str(e),
            "message": "Error collecting extended metrics",
        }


@router.get("/consciousness/metrics")
async def get_consciousness_metrics(
    include_raw: bool = False,
    user: str = Depends(verify_credentials),
) -> Dict[str, Any]:
    """Retorna as 6 métricas completas de consciência + dados brutos."""
    try:
        from src.metrics.real_consciousness_metrics import collect_real_metrics

        metrics = await collect_real_metrics()

        response = {
            "phi": metrics.get("phi", 0.0),
            "anxiety": metrics.get("anxiety", 0.0),
            "flow": metrics.get("flow", 0.0),
            "entropy": metrics.get("entropy", 0.0),
            "ici": metrics.get("ici", 0.0),
            "prs": metrics.get("prs", 0.0),
            "ici_components": metrics.get("ici_components", {}),
            "prs_components": metrics.get("prs_components", {}),
            "history": metrics.get("history", {}),
            "interpretation": metrics.get("interpretation", {}),
            "timestamp": metrics.get("timestamp"),
        }

        # Adicionar dados brutos se solicitado
        if include_raw:
            try:
                from src.consciousness.integration_loop import IntegrationLoop

                loop = IntegrationLoop(enable_logging=False)
                workspace = loop.workspace

                # Dados brutos das predições causais
                # Phase 22: Aumentado para mais dados para validação estatística robusta
                raw_predictions = []
                if workspace.cross_predictions:
                    # Usar todas as predições disponíveis (ou últimas 200 se houver muitas)
                    max_predictions = 200  # Aumentado de 25 para 200
                    recent_preds = (
                        workspace.cross_predictions[-max_predictions:]
                        if len(workspace.cross_predictions) > max_predictions
                        else workspace.cross_predictions
                    )
                    for pred in recent_preds:
                        raw_predictions.append(
                            {
                                "source_module": getattr(pred, "source_module", "unknown"),
                                "target_module": getattr(pred, "target_module", "unknown"),
                                "r_squared": getattr(pred, "r_squared", 0.0),
                                "granger_causality": getattr(pred, "granger_causality", 0.0),
                                "transfer_entropy": getattr(pred, "transfer_entropy", 0.0),
                                "computation_time_ms": getattr(pred, "computation_time_ms", 0.0),
                            }
                        )

                # Phase 22: Estatísticas expandidas dos módulos
                module_stats = {}
                module_activities = {}  # Atividades por módulo
                total_executions = 0
                total_errors = 0

                for module in workspace.get_all_modules():
                    history = workspace.get_module_history(module)
                    if history:
                        # Calcular métricas de atividade
                        executions = len(history)
                        total_executions += executions

                        # Estimar erros (baseado em estados inválidos)
                        errors = sum(1 for h in history if hasattr(h, "error") and h.error)
                        total_errors += errors

                        # Calcular latência média (se disponível)
                        latencies = [
                            getattr(h, "latency_ms", 0) for h in history if hasattr(h, "latency_ms")
                        ]
                        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

                        # Handle timestamp (can be datetime or float)
                        last_update = None
                        if hasattr(history[-1], "timestamp"):
                            ts = history[-1].timestamp
                            if hasattr(ts, "isoformat"):
                                last_update = ts.isoformat()
                            elif isinstance(ts, (int, float)):
                                from datetime import datetime, timezone
                                last_update = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

                        module_stats[module] = {
                            "history_length": executions,
                            "last_update": last_update,
                            "error_count": errors,
                            "error_rate": errors / executions if executions > 0 else 0.0,
                            "avg_latency_ms": avg_latency,
                        }

                        module_activities[module] = {
                            "executions": executions,
                            "errors": errors,
                            "success_rate": (
                                (executions - errors) / executions if executions > 0 else 1.0
                            ),
                        }

                # Phase 22: Métricas agregadas do sistema híbrido
                system_metrics = {
                    "total_executions": total_executions,
                    "total_errors": total_errors,
                    "overall_error_rate": (
                        total_errors / total_executions if total_executions > 0 else 0.0
                    ),
                    "active_modules": len(
                        [
                            m
                            for m in module_stats.values()
                            if isinstance(m, dict)
                            and isinstance(m.get("history_length"), (int, float))
                            and float(m.get("history_length", 0)) > 0
                        ]
                    ),
                }

                # Type-safe valid_predictions_count
                valid_predictions = [
                    p
                    for p in raw_predictions
                    if isinstance(p, dict)
                    and isinstance(p.get("granger_causality"), (int, float))
                    and float(p.get("granger_causality", 0)) > 0
                ]

                response["raw_data"] = {
                    "causal_predictions": raw_predictions,
                    "valid_predictions_count": len(valid_predictions),
                    "total_predictions": len(raw_predictions),
                    "module_stats": module_stats,
                    "module_activities": module_activities,  # Phase 22: Novo
                    "system_metrics": system_metrics,  # Phase 22: Novo
                    "workspace_cycle": workspace.cycle_count,
                    "total_modules": len(workspace.get_all_modules()),
                }
            except Exception as e:
                logger.error(f"Erro ao coletar dados brutos: {e}")
                response["raw_data"] = {"error": str(e)}

        return response
    except Exception as e:
        logger.error(f"Erro ao coletar métricas de consciência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao coletar métricas: {e}")

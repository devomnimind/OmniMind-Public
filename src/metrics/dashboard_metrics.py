"""
Agregador centralizado para métricas do dashboard.

Responsável por unificar:
- Métricas de sistema (CPU / memória / disco)
- Métricas de consciência (phi, ICI, PRS, estados psicológicos)
- Atividade dos módulos
- Saúde geral do sistema
- Comparações com baseline real

Autor: Fabrício da Silva (processo iterativo conforme documentação do projeto).
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.metrics.real_baseline_system import RealBaselineSystem
from src.metrics.real_consciousness_metrics import RealConsciousnessMetricsCollector
from src.metrics.real_module_activity import RealModuleActivityTracker
from src.metrics.real_system_health import RealSystemHealthAnalyzer, SystemHealthStatus
from src.monitor.module_metrics import (
    ModuleMetricsCollector,
    get_metrics_collector,
)

try:
    import psutil
except ImportError:  # pragma: no cover - psutil não está disponível nos testes
    psutil = None  # type: ignore

logger = logging.getLogger(__name__)


SystemMetricsFn = Callable[[], Dict[str, Any]]


def _collect_system_metrics_default() -> Dict[str, Any]:
    """Coleta métrica de sistema local. Usa valores seguros caso psutil falhe."""
    if psutil is None:
        raise RuntimeError("psutil não disponível para coleta de métricas do sistema.")

    # CORREÇÃO (2025-12-09): interval=None retorna 0.0% na primeira chamada
    # Usar interval=0.1 para leitura imediata precisa
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    network = psutil.net_io_counters()
    boot_time = getattr(psutil, "boot_time", lambda: time.time())()
    uptime_seconds = max(0.0, time.time() - boot_time)

    return {
        "cpu_percent": round(float(cpu_percent), 1),
        "memory_percent": round(float(memory.percent), 1),
        "disk_percent": round(float(disk.percent), 1),
        "uptime_seconds": int(uptime_seconds),
        "is_user_active": True,  # Placeholder: integrar com detecção real
        "idle_seconds": 0,
        "is_sleep_hours": False,
        "gpu": _collect_gpu_metrics(),
        "details": {
            "cpu": {
                "count": psutil.cpu_count(),
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
            },
            "network": {
                "bytes_sent_mb": round(network.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(network.bytes_recv / (1024**2), 2),
            },
        },
    }


def _collect_gpu_metrics() -> Dict[str, Any]:
    """Coleta métricas da GPU se disponível."""
    try:
        import torch

        if not torch.cuda.is_available():
            return {"available": False}

        props = torch.cuda.get_device_properties(0)
        allocated = torch.cuda.memory_allocated(0)
        reserved = torch.cuda.memory_reserved(0)

        return {
            "available": True,
            "name": props.name,
            "memory_total_mb": round(props.total_memory / (1024**2), 1),
            "memory_allocated_mb": round(allocated / (1024**2), 1),
            "memory_reserved_mb": round(reserved / (1024**2), 1),
            "utilization": (
                round((allocated / props.total_memory) * 100, 1) if props.total_memory > 0 else 0.0
            ),
        }
    except Exception:
        return {"available": False}


def _collect_sentinel_status() -> Dict[str, Any]:
    """Verifica se o Sentinel Watchdog está rodando."""
    if psutil is None:
        return {"status": "unknown"}

    try:
        for proc in psutil.process_iter(["cmdline"]):
            try:
                cmdline = proc.info.get("cmdline") or []
                if any("sentinel_watchdog.py" in str(arg) for arg in cmdline):
                    return {"status": "active", "protection": "enabled"}
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass

    return {"status": "inactive", "protection": "disabled"}


class DashboardMetricsAggregator:
    """Orquestra a coleta unificada de métricas para o dashboard web."""

    def __init__(
        self,
        *,
        consciousness_collector: Optional[RealConsciousnessMetricsCollector] = None,
        module_tracker: Optional[RealModuleActivityTracker] = None,
        health_analyzer: Optional[RealSystemHealthAnalyzer] = None,
        baseline_system: Optional[RealBaselineSystem] = None,
        system_metrics_fn: Optional[SystemMetricsFn] = None,
        module_metrics_collector: Optional[ModuleMetricsCollector] = None,
        cache_ttl_seconds: float = 2.0,
    ) -> None:
        self._consciousness_collector = consciousness_collector
        self._module_tracker = module_tracker or RealModuleActivityTracker()
        self._health_analyzer = health_analyzer or RealSystemHealthAnalyzer()
        self._baseline_system = baseline_system or RealBaselineSystem()
        self._system_metrics_fn = system_metrics_fn or _collect_system_metrics_default
        # FASE 3.2: Integração de ModuleMetricsCollector para métricas antes/depois
        self._module_metrics_collector = module_metrics_collector or get_metrics_collector()
        self._cache_ttl = cache_ttl_seconds

        self._cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp = 0.0
        self._lock = asyncio.Lock()
        self._persisted_metrics_file = Path("data/monitor/real_metrics.json")
        # FASE 3.2: Arquivo para métricas antes/depois
        self._before_after_metrics_file = Path("data/monitor/before_after_metrics.json")

    def set_consciousness_collector(self, collector: RealConsciousnessMetricsCollector) -> None:
        self._consciousness_collector = collector

    async def collect_snapshot(
        self,
        *,
        include_consciousness: bool = True,
        include_baseline: bool = True,
    ) -> Dict[str, Any]:
        """Retorna snapshot consistente para o dashboard."""

        async with self._lock:
            now = time.time()
            if (
                self._cache
                and now - self._cache_timestamp < self._cache_ttl
                and include_consciousness
            ):
                return self._cache

            snapshot = await self._build_snapshot(
                include_consciousness=include_consciousness,
                include_baseline=include_baseline,
            )

            if include_consciousness:
                self._cache = snapshot
                self._cache_timestamp = now

            return snapshot

    async def _build_snapshot(
        self,
        *,
        include_consciousness: bool,
        include_baseline: bool,
    ) -> Dict[str, Any]:
        errors: List[str] = []

        # System metrics
        try:
            system_metrics = self._system_metrics_fn()
        except Exception as exc:  # pragma: no cover - depende de psutil
            logger.error("Erro coletando métricas de sistema: %s", exc)
            errors.append(f"system_metrics: {exc}")
            system_metrics = {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "disk_percent": 0.0,
                "is_user_active": False,
                "idle_seconds": 0,
                "is_sleep_hours": False,
                "details": {},
            }

        module_activity = self._module_tracker.get_all_module_activities()

        # FASE 3.2: Coletar métricas dos módulos integrados (SemanticCache, ModelOptimizer, etc.)
        module_metrics_data: Optional[Dict[str, Any]] = None
        try:
            module_metrics_data = self._module_metrics_collector.get_all_metrics()
        except Exception as exc:
            logger.debug(f"Erro coletando métricas de módulos: {exc}")

        consciousness_metrics: Optional[Dict[str, Any]] = None
        baseline_comparison: Optional[Dict[str, Any]] = None
        persisted_metrics = self._load_persisted_metrics()

        if include_consciousness:
            if not self._consciousness_collector:
                errors.append("Consciousness collector não inicializado.")
            else:
                try:
                    metrics_obj = await self._consciousness_collector.collect_real_metrics()
                    consciousness_metrics = self._format_consciousness_metrics(metrics_obj)
                except Exception as exc:
                    logger.error("Erro coletando métricas de consciência: %s", exc)
                    errors.append(f"consciousness_metrics: {exc}")

            if (
                not consciousness_metrics or self._is_placeholder_metrics(consciousness_metrics)
            ) and persisted_metrics:
                consciousness_metrics = persisted_metrics
                errors.append(
                    "consciousness_metrics: usando snapshot persistido "
                    "(data/monitor/real_metrics.json)"
                )
            elif consciousness_metrics and not self._is_placeholder_metrics(consciousness_metrics):
                # Persistir métricas válidas
                self._save_persisted_metrics(consciousness_metrics)

        system_health = await self._analyze_system_health(consciousness_metrics, module_activity)

        if include_baseline and consciousness_metrics:
            baseline_comparison = self._build_baseline_from_payload(consciousness_metrics)

        # FASE 3.2: Comparação antes/depois das otimizações
        before_after_comparison: Optional[Dict[str, Any]] = None
        if module_metrics_data:
            before_after_comparison = self._build_before_after_comparison(module_metrics_data)

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "system_metrics": system_metrics,
            "module_activity": module_activity,
            "system_health": system_health,
            "consciousness_metrics": consciousness_metrics,
            "baseline_comparison": baseline_comparison,
            "module_metrics": module_metrics_data,  # FASE 3.2: Métricas dos módulos
            "before_after_comparison": before_after_comparison,  # FASE 3.2: Comparação antes/depois
            "sentinel_status": _collect_sentinel_status(),
            "errors": errors,
        }

        return snapshot

    async def _analyze_system_health(
        self,
        consciousness_metrics: Optional[Dict[str, Any]],
        module_activity: Dict[str, float],
    ) -> Optional[Dict[str, Any]]:
        try:
            status: SystemHealthStatus = await self._health_analyzer.analyze_system_health(
                consciousness_metrics or {},
                module_activity,
                error_rates=None,
            )
            return {
                "overall": status.overall,
                "integration": status.integration,
                "coherence": status.coherence,
                "anxiety": status.anxiety,
                "flow": status.flow,
                "audit": status.audit,
                "details": status.details,
                "timestamp": status.timestamp.isoformat(),
            }
        except Exception as exc:
            logger.error("Erro analisando saúde do sistema: %s", exc)
            return None

    def _format_consciousness_metrics(self, metrics_obj) -> Dict[str, Any]:
        details = {
            "ici_components": metrics_obj.ici_components or {},
            "prs_components": metrics_obj.prs_components or {},
        }

        history = metrics_obj.history or {}

        payload = {
            "phi": metrics_obj.phi,
            "ICI": metrics_obj.ici,
            "ici": metrics_obj.ici,
            "PRS": metrics_obj.prs,
            "prs": metrics_obj.prs,
            "anxiety": metrics_obj.anxiety,
            "flow": metrics_obj.flow,
            "entropy": metrics_obj.entropy,
            "ici_components": details["ici_components"],
            "prs_components": details["prs_components"],
            "details": details,
            "interpretation": metrics_obj.interpretation,
            "history": history,
            "timestamp": metrics_obj.timestamp.isoformat(),
        }

        return payload

    def _load_persisted_metrics(self) -> Optional[Dict[str, Any]]:
        if not self._persisted_metrics_file.exists():
            return None
        try:
            with self._persisted_metrics_file.open("r", encoding="utf-8") as stream:
                data = json.load(stream)
            return self._normalize_persisted_payload(data)
        except Exception as exc:
            logger.error("Erro lendo métricas persistidas: %s", exc)
            return None

    def _save_persisted_metrics(self, metrics: Dict[str, Any]) -> None:
        """Salva métricas de consciência no arquivo para persistência."""
        try:
            # Garantir que o diretório existe
            self._persisted_metrics_file.parent.mkdir(parents=True, exist_ok=True)

            # Salvar métricas
            with self._persisted_metrics_file.open("w", encoding="utf-8") as stream:
                json.dump(metrics, stream, indent=2, ensure_ascii=False)

            logger.debug(
                "Métricas persistidas em %s (phi=%.4f)",
                self._persisted_metrics_file,
                metrics.get("phi", 0.0),
            )
        except Exception as exc:
            logger.error("Erro salvando métricas persistidas: %s", exc)

    def _normalize_persisted_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        details = data.get("details") or {
            "ici_components": data.get("ici_components") or {},
            "prs_components": data.get("prs_components") or {},
        }
        history = data.get("history") or {}

        payload = {
            "phi": data.get("phi"),
            "ICI": data.get("ICI") or data.get("ici"),
            "ici": data.get("ici") or data.get("ICI"),
            "PRS": data.get("PRS") or data.get("prs"),
            "prs": data.get("prs") or data.get("PRS"),
            "anxiety": data.get("anxiety"),
            "flow": data.get("flow"),
            "entropy": data.get("entropy"),
            "ici_components": details.get("ici_components", {}),
            "prs_components": details.get("prs_components", {}),
            "details": details,
            "interpretation": data.get("interpretation", {}),
            "history": history,
            "timestamp": data.get("timestamp"),
        }
        return payload

    def _is_placeholder_metrics(self, payload: Optional[Dict[str, Any]]) -> bool:
        if not payload:
            return True
        history = payload.get("history") or {}
        has_any_history = any(
            history.get(key) for key in ("phi", "ici", "prs", "anxiety", "flow", "entropy")
        )
        if has_any_history:
            return False

        core_values = [
            payload.get("phi"),
            payload.get("ICI"),
            payload.get("PRS"),
        ]
        return all(value in (None, 0.0) for value in core_values)

    def _build_baseline_from_payload(self, payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        metrics = {
            "phi": float(payload.get("phi") or 0.0),
            "ici": float(payload.get("ici") or payload.get("ICI") or 0.0),
            "prs": float(payload.get("prs") or payload.get("PRS") or 0.0),
            "anxiety": float(payload.get("anxiety") or 0.0),
            "flow": float(payload.get("flow") or 0.0),
            "entropy": float(payload.get("entropy") or 0.0),
        }

        comparisons: Dict[str, Dict[str, Any]] = {}

        for name, value in metrics.items():
            try:
                self._baseline_system.record_metric(name, value)
                comparison = self._baseline_system.compare_with_baseline(name, value)
                comparisons[name] = {
                    "current": comparison.current_value,
                    "baseline": comparison.baseline_value,
                    "change": comparison.change,
                    "change_type": comparison.change_type,
                    "significance": comparison.significance,
                }
            except Exception as exc:
                logger.error("Erro construindo baseline para %s: %s", name, exc)
                comparisons[name] = {
                    "current": value,
                    "baseline": value,
                    "change": 0.0,
                    "change_type": "stable",
                    "significance": "low",
                }

        return comparisons

    def _build_before_after_comparison(self, module_metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constrói comparação antes/depois das otimizações (FASE 3.2).

        Args:
            module_metrics_data: Métricas dos módulos coletadas

        Returns:
            Dict com comparação antes/depois
        """
        try:
            # Carregar métricas "antes" (baseline)
            before_metrics = self._load_before_metrics()

            # Módulos integrados na FASE 3.1
            integrated_modules = [
                "SemanticCacheLayer",
                "ModelOptimizer",
                "HybridRetrievalSystem",
                "DatasetIndexer",
                "RAGFallbackSystem",
                "EnhancedCodeAgent",
                "DynamicToolCreator",
                "ErrorAnalyzer",
            ]

            comparison: Dict[str, Any] = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "modules": {},
            }

            current_modules = module_metrics_data.get("modules", {})

            for module_name in integrated_modules:
                current = current_modules.get(module_name, {})
                before = before_metrics.get("modules", {}).get(module_name, {})

                if not current and not before:
                    continue

                # Comparar métricas principais
                module_comparison: Dict[str, Any] = {
                    "current": current,
                    "before": before,
                    "has_data": bool(current or before),
                }

                # Comparar métricas específicas se disponíveis
                if current and before:
                    current_metrics = current.get("metrics", {})
                    before_metrics_module = before.get("metrics", {})

                    changes: Dict[str, Any] = {}
                    for metric_name in set(
                        list(current_metrics.keys()) + list(before_metrics_module.keys())
                    ):
                        current_val = current_metrics.get(metric_name, {}).get("value")
                        before_val = before_metrics_module.get(metric_name, {}).get("value")

                        if current_val is not None and before_val is not None:
                            try:
                                if isinstance(current_val, (int, float)) and isinstance(
                                    before_val, (int, float)
                                ):
                                    change = current_val - before_val
                                    change_pct = (
                                        (change / before_val * 100) if before_val != 0 else 0.0
                                    )
                                    changes[metric_name] = {
                                        "before": before_val,
                                        "current": current_val,
                                        "change": change,
                                        "change_percent": change_pct,
                                    }
                            except (TypeError, ValueError):
                                pass

                    if changes:
                        module_comparison["metric_changes"] = changes

                comparison["modules"][module_name] = module_comparison

            return comparison

        except Exception as exc:
            logger.error(f"Erro construindo comparação antes/depois: {exc}")
            return {}

    def _load_before_metrics(self) -> Dict[str, Any]:
        """
        Carrega métricas "antes" (baseline) das otimizações.

        Returns:
            Dict com métricas antes
        """
        try:
            if self._before_after_metrics_file.exists():
                with open(self._before_after_metrics_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as exc:
            logger.debug(f"Erro ao carregar métricas antes: {exc}")

        return {}

    def save_before_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """
        Salva métricas "antes" (baseline) para comparação futura (FASE 3.2).

        Args:
            metrics_data: Métricas a salvar como baseline
        """
        try:
            baseline_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "description": "Métricas antes das otimizações FASE 3.1",
                "modules": metrics_data.get("modules", {}),
            }

            with open(self._before_after_metrics_file, "w", encoding="utf-8") as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Métricas 'antes' salvas em {self._before_after_metrics_file}")
        except Exception as exc:
            logger.error(f"Erro ao salvar métricas antes: {exc}")


# Instância global reutilizável em todo o backend
dashboard_metrics_aggregator = DashboardMetricsAggregator()


async def collect_dashboard_snapshot(
    *, include_consciousness: bool = True, include_baseline: bool = True
) -> Dict[str, Any]:
    """Helper para componentes externos (ex.: FastAPI endpoints)."""
    return await dashboard_metrics_aggregator.collect_snapshot(
        include_consciousness=include_consciousness,
        include_baseline=include_baseline,
    )


def collect_system_metrics() -> Dict[str, Any]:
    """Função utilitária para endpoints que precisam apenas das métricas do host."""
    return _collect_system_metrics_default()

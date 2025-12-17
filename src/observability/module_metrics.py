"""
Sistema de Métricas Persistidas para Módulos OmniMind

Persiste métricas de todos os módulos para auditoria e análise.
Exceto o próprio sistema de auditoria (conceito teórico: não pode se auditar).

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ModuleMetricsCollector:
    """
    Coletor de métricas persistidas para módulos OmniMind.

    Características:
    - Persiste métricas em JSON/JSONL
    - Integra com audit chain (exceto próprio sistema de auditoria)
    - Suporta múltiplos módulos
    - Rotação automática de logs
    """

    # Componentes que NÃO devem ser auditados (conceito teórico)
    # 1. O sistema de auditoria não pode se auditar
    # 2. O inconsciente não pode ser auditado - se tudo fosse auditado, não haveria inconsciente
    EXCLUDED_FROM_AUDIT = {
        # Sistema de auditoria
        "ImmutableAuditSystem",
        "audit_system",
        "audit",
        # Inconsciente (conceito teórico fundamental)
        "machinic_unconscious",
        "unconscious",
        "DesireFlow",
        "QuantumUnconscious",
        "EncryptedUnconsciousLayer",
        "SystemicMemoryTrace",
        "topological_void",
        "repressed",
        "deterritorialization",
        "desire_flow",
        "sinthome",
        "quantum_unconscious",
    }

    def __init__(self, metrics_dir: str = "data/monitor/module_metrics"):
        """
        Inicializa coletor de métricas.

        Args:
            metrics_dir: Diretório para salvar métricas
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Arquivo JSONL para métricas históricas
        self.metrics_file = self.metrics_dir / "metrics.jsonl"

        # Arquivo JSON para snapshot atual
        self.snapshot_file = self.metrics_dir / "snapshot.json"

        # Cache de métricas por módulo
        self.module_metrics: Dict[str, Dict[str, Any]] = {}

        # Carregar métricas do snapshot ao inicializar
        self._load_metrics_from_snapshot()

        logger.info(f"ModuleMetricsCollector inicializado: {self.metrics_dir}")

    def record_metric(
        self,
        module_name: str,
        metric_name: str,
        value: Any,
        labels: Optional[Dict[str, Any]] = None,
        audit: bool = True,
    ) -> None:
        """
        Registra métrica de um módulo.

        Args:
            module_name: Nome do módulo (ex: "DynamicToolCreator")
            metric_name: Nome da métrica (ex: "tools_created")
            value: Valor da métrica
            labels: Labels adicionais (opcional)
            audit: Se True, integra com audit chain (exceto módulos excluídos)
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Inicializar métricas do módulo se necessário
        if module_name not in self.module_metrics:
            self.module_metrics[module_name] = {
                "module": module_name,
                "first_seen": timestamp,
                "last_updated": timestamp,
                "metrics": {},
            }

        # Atualizar métrica
        self.module_metrics[module_name]["metrics"][metric_name] = {
            "value": value,
            "timestamp": timestamp,
            "labels": labels or {},
        }
        self.module_metrics[module_name]["last_updated"] = timestamp

        # Criar entrada para JSONL
        entry = {
            "timestamp": timestamp,
            "module": module_name,
            "metric": metric_name,
            "value": value,
            "labels": labels or {},
        }

        # Persistir em JSONL (append-only)
        try:
            with open(self.metrics_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Erro ao persistir métrica: {e}")

        # Integrar com audit chain (exceto módulos excluídos)
        if audit and not self._is_excluded_from_audit(module_name):
            try:
                from ..audit.immutable_audit import get_audit_system

                audit_system = get_audit_system()
                audit_system.log_action(
                    action="module_metric",
                    details={
                        "component": module_name,
                        "metric": metric_name,
                        "value": value,
                        "labels": labels or {},
                    },
                    category="metrics",
                )
            except Exception as e:
                logger.debug(f"Erro ao integrar com audit chain: {e}")

        # Atualizar snapshot
        self._update_snapshot()

    def _is_excluded_from_audit(self, module_name: str) -> bool:
        """
        Verifica se módulo está excluído de auditoria.

        Args:
            module_name: Nome do módulo

        Returns:
            True se excluído
        """
        return any(excluded in module_name for excluded in self.EXCLUDED_FROM_AUDIT)

    def _load_metrics_from_snapshot(self) -> None:
        """
        Carrega métricas do snapshot ao inicializar.
        Permite recuperar métricas persistidas de execuções anteriores.
        """
        try:
            if self.snapshot_file.exists():
                with open(self.snapshot_file, "r", encoding="utf-8") as f:
                    snapshot = json.load(f)

                if "modules" in snapshot:
                    self.module_metrics = snapshot["modules"]
                    logger.info(f"Carregadas {len(self.module_metrics)} módulos do snapshot")
        except Exception as e:
            logger.debug(f"Erro ao carregar snapshot: {e}")
            # Continuar normalmente se não conseguir carregar

    def _update_snapshot(self) -> None:
        """Atualiza snapshot JSON com métricas atuais."""
        try:
            snapshot = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "modules": self.module_metrics,
            }

            with open(self.snapshot_file, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao atualizar snapshot: {e}")

    def get_module_metrics(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna métricas de um módulo.

        Args:
            module_name: Nome do módulo

        Returns:
            Dict com métricas ou None
        """
        return self.module_metrics.get(module_name)

    def get_all_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modules": self.module_metrics,
        }

    def generate_report(self, module_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera relatório de métricas.

        Args:
            module_name: Nome do módulo (None para todos)

        Returns:
            Dict com relatório
        """
        if module_name:
            metrics = self.get_module_metrics(module_name)
            if not metrics:
                return {"error": f"Módulo {module_name} não encontrado"}

            return {
                "module": module_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metrics": metrics,
            }

        return self.get_all_metrics()


# Instância global
_global_collector: Optional[ModuleMetricsCollector] = None


def get_metrics_collector() -> ModuleMetricsCollector:
    """Retorna instância global do coletor de métricas."""
    global _global_collector
    if _global_collector is None:
        _global_collector = ModuleMetricsCollector()
    return _global_collector


# Alias para compatibilidade
def get_module_metrics() -> ModuleMetricsCollector:
    """Alias para get_metrics_collector() - retorna instância global do coletor."""
    return get_metrics_collector()

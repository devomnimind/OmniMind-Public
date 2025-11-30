"""
Real Module Activity System - Atividade real dos módulos do sistema.

Substitui valores hardcoded por medição real da atividade de:
- IntegrationLoop modules
- SharedWorkspace operations
- IIT metrics calculations
- System health checks

Author: OmniMind Development Team
Date: November 2025
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModuleActivity:
    """Atividade de um módulo específico."""

    module_name: str
    activity_level: float  # 0.0 - 100.0
    operations_count: int
    last_active: datetime
    avg_response_time: float  # ms
    error_rate: float
    status: str  # "active", "idle", "error"


class RealModuleActivityTracker:
    """Rastreador de atividade real dos módulos."""

    def __init__(self):
        self.modules: Dict[str, ModuleActivity] = {}
        self.activity_window = 300  # 5 minutos em segundos
        self.last_update = time.time()

        # Inicializa módulos conhecidos
        self._initialize_known_modules()

        logger.info("RealModuleActivityTracker initialized")

    def _initialize_known_modules(self) -> None:
        """Inicializa módulos conhecidos do sistema."""
        known_modules = [
            "orchestrator",
            "consciousness",
            "integration_loop",
            "shared_workspace",
            "iit_metrics",
            "qualia_engine",
            "attention",
            "memory",
            "audit",
            "autopoietic",
            "ethics"
        ]

        for module_name in known_modules:
            self.modules[module_name] = ModuleActivity(
                module_name=module_name,
                activity_level=0.0,
                operations_count=0,
                last_active=datetime.now(),
                avg_response_time=0.0,
                error_rate=0.0,
                status="idle"
            )

    def record_module_operation(self, module_name: str, operation_time_ms: float,
                               success: bool = True) -> None:
        """Registra uma operação de módulo."""

        if module_name not in self.modules:
            self.modules[module_name] = ModuleActivity(
                module_name=module_name,
                activity_level=0.0,
                operations_count=0,
                last_active=datetime.now(),
                avg_response_time=0.0,
                error_rate=0.0,
                status="idle"
            )

        module = self.modules[module_name]

        # Atualiza contadores
        module.operations_count += 1
        module.last_active = datetime.now()

        # Atualiza tempo de resposta médio
        if module.avg_response_time == 0:
            module.avg_response_time = operation_time_ms
        else:
            # Média móvel
            module.avg_response_time = (module.avg_response_time + operation_time_ms) / 2

        # Atualiza taxa de erro
        if not success:
            # Taxa de erro baseada nas últimas operações
            recent_errors = getattr(module, '_recent_errors', 0)
            recent_total = getattr(module, '_recent_total', 0)

            recent_errors += 1 if not success else 0
            recent_total += 1

            if recent_total >= 10:  # Recalcula a cada 10 operações
                module.error_rate = (recent_errors / recent_total) * 100
                recent_errors = 0
                recent_total = 0

            setattr(module, '_recent_errors', recent_errors)
            setattr(module, '_recent_total', recent_total)

        # Atualiza status
        time_since_last = (datetime.now() - module.last_active).total_seconds()
        if time_since_last < 60:  # Ativo nos últimos 60 segundos
            module.status = "active"
        elif time_since_last < 300:  # Ativo nos últimos 5 minutos
            module.status = "idle"
        else:
            module.status = "inactive"

    def update_activity_levels(self) -> None:
        """Atualiza níveis de atividade baseados em operações recentes."""

        current_time = time.time()

        # Atualiza apenas uma vez por minuto para evitar sobrecarga
        if current_time - self.last_update < 60:
            return

        self.last_update = current_time

        for module in self.modules.values():
            # Calcula atividade baseada em operações na janela de tempo
            time_since_last = (datetime.now() - module.last_active).total_seconds()

            if time_since_last < 60:  # Muito ativo
                base_activity = 90.0
            elif time_since_last < 300:  # Moderadamente ativo
                base_activity = 60.0
            elif time_since_last < 900:  # Pouco ativo
                base_activity = 30.0
            else:  # Inativo
                base_activity = 10.0

            # Ajusta baseado na taxa de erro
            if module.error_rate > 20:
                base_activity *= 0.7  # Reduz atividade se muitos erros
            elif module.error_rate > 10:
                base_activity *= 0.9

            # Ajusta baseado no tempo de resposta
            if module.avg_response_time > 1000:  # Mais de 1 segundo
                base_activity *= 0.8
            elif module.avg_response_time > 100:  # Mais de 100ms
                base_activity *= 0.95

            # Limita entre 0 e 100
            module.activity_level = max(0.0, min(100.0, base_activity))

    def get_module_activity(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Retorna atividade de um módulo específico."""

        self.update_activity_levels()

        if module_name not in self.modules:
            return None

        module = self.modules[module_name]

        return {
            "module_name": module.module_name,
            "activity_level": module.activity_level,
            "operations_count": module.operations_count,
            "last_active": module.last_active.isoformat(),
            "avg_response_time": module.avg_response_time,
            "error_rate": module.error_rate,
            "status": module.status
        }

    def get_all_module_activities(self) -> Dict[str, float]:
        """Retorna atividade de todos os módulos para o dashboard."""

        self.update_activity_levels()

        return {
            module_name: module.activity_level
            for module_name, module in self.modules.items()
        }

    def get_system_activity_summary(self) -> Dict[str, Any]:
        """Retorna resumo da atividade do sistema."""

        self.update_activity_levels()

        activities = [m.activity_level for m in self.modules.values()]

        if not activities:
            return {
                "average_activity": 0.0,
                "active_modules": 0,
                "total_modules": 0,
                "system_status": "unknown"
            }

        avg_activity = sum(activities) / len(activities)
        active_modules = sum(1 for m in self.modules.values() if m.status == "active")

        # Determina status do sistema
        if avg_activity > 70:
            system_status = "high_activity"
        elif avg_activity > 40:
            system_status = "moderate_activity"
        elif avg_activity > 20:
            system_status = "low_activity"
        else:
            system_status = "idle"

        return {
            "average_activity": avg_activity,
            "active_modules": active_modules,
            "total_modules": len(self.modules),
            "system_status": system_status
        }

    def reset_module_stats(self, module_name: str) -> None:
        """Reseta estatísticas de um módulo."""
        if module_name in self.modules:
            module = self.modules[module_name]
            module.operations_count = 0
            module.avg_response_time = 0.0
            module.error_rate = 0.0
            logger.info(f"Reset stats for module {module_name}")


# Instância global do tracker de atividade
real_module_tracker = RealModuleActivityTracker()


def track_module_activity() -> Dict[str, float]:
    """
    Função wrapper para obter atividade dos módulos.

    Returns:
        Dicionário com atividade de cada módulo (percentuais 0.0-100.0)
    """
    return real_module_tracker.get_all_module_activities()
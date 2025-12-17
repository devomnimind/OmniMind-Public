"""
Real System Health System - Saúde do sistema baseada em dados reais.

Substitui labels hardcoded por análise real baseada em:
- Performance dos módulos
- Taxas de erro
- Consistência das métricas
- Estado dos componentes

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SystemHealthStatus:
    """Status de saúde do sistema."""

    overall: str  # STABLE, WARNING, CRITICAL
    integration: str  # RISING, FALLING, STABLE
    coherence: str  # GOOD, MODERATE, POOR
    anxiety: str  # CALM, MODERATE, HIGH
    flow: str  # FLUENT, MODERATE, BLOCKED
    audit: str  # CLEAN, WARNING, ISSUES

    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class RealSystemHealthAnalyzer:
    """Analisador de saúde do sistema baseado em dados reais."""

    def __init__(self):
        self.last_analysis = datetime.min
        self.analysis_interval = 30  # segundos
        self._last_status: Optional[SystemHealthStatus] = None

        logger.info("RealSystemHealthAnalyzer initialized")

    async def analyze_system_health(
        self,
        consciousness_metrics: Optional[Dict[str, Any]] = None,
        module_activities: Optional[Dict[str, float]] = None,
        error_rates: Optional[Dict[str, float]] = None,
    ) -> SystemHealthStatus:
        """Analisa saúde do sistema baseada em métricas reais."""

        current_time = datetime.now()

        # Evita análises muito frequentes
        if (current_time - self.last_analysis).total_seconds() < self.analysis_interval:
            # Retorna status anterior se disponível
            if self._last_status is not None:
                return self._last_status

        # Valores padrão se não fornecidos
        phi = consciousness_metrics.get("phi", 0.0) if consciousness_metrics else 0.0
        anxiety = consciousness_metrics.get("anxiety", 0.0) if consciousness_metrics else 0.0
        flow = consciousness_metrics.get("flow", 0.0) if consciousness_metrics else 0.0

        activities = module_activities or {}
        errors = error_rates or {}

        # Analisa cada componente
        overall = self._analyze_overall_health(phi, anxiety, flow, activities, errors)
        integration = self._analyze_integration(phi, activities)
        coherence = self._analyze_coherence(phi, flow)
        anxiety_status = self._analyze_anxiety_level(anxiety)
        flow_status = self._analyze_flow_state(flow)
        audit = self._analyze_audit_health(errors)

        status = SystemHealthStatus(
            overall=overall,
            integration=integration,
            coherence=coherence,
            anxiety=anxiety_status,
            flow=flow_status,
            audit=audit,
            details={
                "phi_value": phi,
                "anxiety_level": anxiety,
                "flow_state": flow,
                "avg_module_activity": (
                    sum(activities.values()) / len(activities) if activities else 0.0
                ),
                "total_errors": sum(errors.values()) if errors else 0.0,
            },
            timestamp=current_time,
        )

        self._last_status = status
        self.last_analysis = current_time

        logger.debug(f"System health analyzed: overall={overall}")

        return status

    def _analyze_overall_health(
        self,
        phi: float,
        anxiety: float,
        flow: float,
        activities: Dict[str, float],
        errors: Dict[str, float],
    ) -> str:
        """Analisa saúde geral do sistema."""

        # Calcula score composto
        phi_score = min(1.0, phi / 0.8)  # Phi ideal > 0.8
        anxiety_score = 1.0 - min(1.0, anxiety / 0.6)  # Anxiety ideal < 0.6
        flow_score = flow  # Flow já está em 0-1

        # Atividade média dos módulos
        avg_activity = sum(activities.values()) / len(activities) if activities else 0.0
        activity_score = min(1.0, avg_activity / 70.0)  # Atividade ideal > 70%

        # Taxa de erro
        total_errors = sum(errors.values()) if errors else 0.0
        error_score = 1.0 - min(1.0, total_errors / 20.0)  # Erros ideais < 20%

        # Score geral (média ponderada)
        weights = [0.3, 0.2, 0.2, 0.2, 0.1]  # phi, anxiety, flow, activity, errors
        scores = [phi_score, anxiety_score, flow_score, activity_score, error_score]
        overall_score = sum(w * s for w, s in zip(weights, scores))

        if overall_score > 0.8:
            return "STABLE"
        elif overall_score > 0.6:
            return "MODERATE"
        elif overall_score > 0.4:
            return "WARNING"
        else:
            return "CRITICAL"

    def _analyze_integration(self, phi: float, activities: Dict[str, float]) -> str:
        """Analisa nível de integração."""

        # Integração baseada em Phi e atividade dos módulos
        phi_integration = "RISING" if phi > 0.6 else "STABLE" if phi > 0.3 else "FALLING"

        # Verifica consistência da atividade entre módulos
        if activities:
            activity_values = list(activities.values())
            activity_std = sum(
                (x - sum(activity_values) / len(activity_values)) ** 2 for x in activity_values
            ) ** 0.5 / len(activity_values)

            if activity_std < 10:  # Atividades consistentes
                return phi_integration
            else:  # Atividades inconsistentes
                return "FLUCTUATING"

        return phi_integration

    def _analyze_coherence(self, phi: float, flow: float) -> str:
        """Analisa coerência do sistema."""

        # Coerência baseada na relação entre Phi e Flow
        coherence_score = (phi + flow) / 2

        if coherence_score > 0.7:
            return "GOOD"
        elif coherence_score > 0.4:
            return "MODERATE"
        else:
            return "POOR"

    def _analyze_anxiety_level(self, anxiety: float) -> str:
        """Analisa nível de ansiedade."""

        if anxiety < 0.2:
            return "CALM"
        elif anxiety < 0.5:
            return "MODERATE"
        else:
            return "HIGH"

    def _analyze_flow_state(self, flow: float) -> str:
        """Analisa estado de flow."""

        if flow > 0.7:
            return "FLUENT"
        elif flow > 0.3:
            return "MODERATE"
        else:
            return "BLOCKED"

    def _analyze_audit_health(self, errors: Dict[str, float]) -> str:
        """Analisa saúde do sistema de auditoria."""

        total_errors = sum(errors.values()) if errors else 0.0

        if total_errors == 0:
            return "CLEAN"
        elif total_errors < 5:
            return "MINOR_ISSUES"
        elif total_errors < 15:
            return "WARNING"
        else:
            return "ISSUES"

    def get_health_trends(self, history: List[SystemHealthStatus]) -> Dict[str, Any]:
        """Analisa tendências de saúde."""

        if len(history) < 2:
            return {"trend": "insufficient_data"}

        # Analisa tendência do status geral
        status_values = []
        for status in history[-10:]:  # Últimos 10
            # Converte status para valor numérico
            status_map = {"STABLE": 4, "MODERATE": 3, "WARNING": 2, "CRITICAL": 1}
            status_values.append(status_map.get(status.overall, 2))

        # Calcula tendência
        if len(status_values) >= 2:
            trend = status_values[-1] - status_values[0]
            if trend > 0:
                trend_desc = "improving"
            elif trend < 0:
                trend_desc = "degrading"
            else:
                trend_desc = "stable"
        else:
            trend_desc = "unknown"

        return {
            "trend": trend_desc,
            "current_status": history[-1].overall if history else "unknown",
            "status_history": [h.overall for h in history[-10:]],
            "avg_phi": (
                sum(h.details.get("phi_value", 0) for h in history[-10:]) / len(history[-10:])
                if history
                else 0.0
            ),
        }


# Instância global do analisador
real_health_analyzer = RealSystemHealthAnalyzer()


async def assess_real_health() -> Dict[str, Any]:
    """
    Função wrapper para avaliar saúde real do sistema.

    Returns:
        Dicionário com avaliação de saúde do sistema
    """
    result = await real_health_analyzer.analyze_system_health()
    return {
        "overall": result.overall,
        "integration": result.integration,
        "coherence": result.coherence,
        "anxiety": result.anxiety,
        "flow": result.flow,
        "audit": result.audit,
    }

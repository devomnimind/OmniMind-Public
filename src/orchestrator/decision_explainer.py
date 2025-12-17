"""
Sistema de Explicabilidade de Decisões para Orchestrator.

Implementa Seção 5 da Auditoria do Orchestrator:
- Contexto completo de cada decisão
- Histórico auditado de ações autônomas
- Rastreamento de causa-efeito
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DecisionExplanation:
    """Explicação estruturada de uma decisão."""

    action: str
    timestamp: float
    context: Dict[str, Any]
    permission_result: Dict[str, Any]
    trust_level: float
    alternatives_considered: List[str] = field(default_factory=list)
    expected_impact: Dict[str, Any] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    decision_maker: str = "orchestrator"
    execution_result: Optional[Dict[str, Any]] = None
    explanation_text: str = ""


class DecisionExplainer:
    """Explica decisões tomadas pelo Orchestrator."""

    def __init__(self, max_history: int = 1000) -> None:
        """Inicializa sistema de explicabilidade.

        Args:
            max_history: Tamanho máximo do histórico
        """
        self.max_history = max_history
        self.explanation_history: List[DecisionExplanation] = []

        logger.info("DecisionExplainer inicializado")

    def explain_decision(
        self,
        action: str,
        context: Dict[str, Any],
        permission_result: Tuple[bool, str],
        trust_level: float,
    ) -> DecisionExplanation:
        """Gera explicação estruturada de decisão.

        Args:
            action: Nome da ação
            context: Contexto da decisão
            permission_result: Resultado da verificação de permissões (pode_executar, motivo)
            trust_level: Nível de confiança atual

        Returns:
            Explicação estruturada da decisão
        """
        can_execute, reason = permission_result

        # Gerar alternativas consideradas
        alternatives = self._get_alternatives(action, context)

        # Estimar impacto esperado
        expected_impact = self._estimate_impact(action, context)

        # Avaliar risco
        risk_assessment = self._assess_risk(action, context, trust_level)

        # Gerar texto explicativo
        explanation_text = self._generate_explanation_text(
            action,
            context,
            can_execute,
            reason,
            trust_level,
            alternatives,
            risk_assessment,
        )

        # Criar explicação
        explanation = DecisionExplanation(
            action=action,
            timestamp=time.time(),
            context=context,
            permission_result={
                "can_execute": can_execute,
                "reason": reason,
            },
            trust_level=trust_level,
            alternatives_considered=alternatives,
            expected_impact=expected_impact,
            risk_assessment=risk_assessment,
            explanation_text=explanation_text,
        )

        # Adicionar ao histórico
        self.explanation_history.append(explanation)
        if len(self.explanation_history) > self.max_history:
            self.explanation_history.pop(0)

        logger.debug("Explicação gerada para ação: %s", action)

        return explanation

    def _get_alternatives(self, action: str, context: Dict[str, Any]) -> List[str]:
        """Gera lista de alternativas consideradas.

        Args:
            action: Nome da ação
            context: Contexto da decisão

        Returns:
            Lista de alternativas
        """
        alternatives: List[str] = []

        # Alternativas baseadas no tipo de ação
        if action == "block_port":
            alternatives = [
                "Monitorar porta sem bloquear",
                "Bloquear temporariamente",
                "Notificar administrador",
            ]
        elif action == "isolate_component":
            alternatives = [
                "Monitorar componente",
                "Reduzir capacidade",
                "Isolar completamente",
            ]
        elif action == "quarantine_component":
            alternatives = [
                "Monitorar componente",
                "Isolar componente",
                "Colocar em quarentena",
            ]
        else:
            alternatives = [
                "Não executar ação",
                "Solicitar aprovação humana",
                "Executar com monitoramento",
            ]

        return alternatives

    def _estimate_impact(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Estima impacto esperado da ação.

        Args:
            action: Nome da ação
            context: Contexto da decisão

        Returns:
            Dicionário com estimativa de impacto
        """
        impact = {
            "severity": "medium",
            "scope": "local",
            "reversibility": "reversible",
            "affected_components": [],
        }

        # Impacto baseado no tipo de ação
        if action in ["isolate_component", "quarantine_component"]:
            impact["severity"] = "high"
            impact["scope"] = "component"
            component_id = context.get("component_id") or context.get("source_ip")
            if component_id:
                impact["affected_components"] = [component_id]

        elif action == "block_port":
            impact["severity"] = "medium"
            impact["scope"] = "network"
            impact["reversibility"] = "reversible"

        elif action == "modify_code":
            impact["severity"] = "high"
            impact["scope"] = "system"
            impact["reversibility"] = "requires_rollback"

        elif action == "restart_service":
            impact["severity"] = "medium"
            impact["scope"] = "service"
            impact["reversibility"] = "reversible"

        return impact

    def _assess_risk(
        self, action: str, context: Dict[str, Any], trust_level: float
    ) -> Dict[str, Any]:
        """Avalia risco da ação.

        Args:
            action: Nome da ação
            context: Contexto da decisão
            trust_level: Nível de confiança atual

        Returns:
            Dicionário com avaliação de risco
        """
        risk: Dict[str, Any] = {
            "level": "medium",
            "factors": [],
            "mitigation": [],
        }

        # Fatores de risco
        if trust_level < 0.5:
            risk["factors"].append("Baixa confiança histórica")
            risk["level"] = "high"

        if action in ["modify_code", "modify_config"]:
            risk["factors"].append("Modificação permanente do sistema")
            risk["level"] = "high"
            risk["mitigation"].append("Requer rollback automático")

        if context.get("emergency", False):
            risk["factors"].append("Modo emergencial ativo")
            risk["mitigation"].append("Ações de emergência têm precedência")

        # Ajustar nível de risco baseado em fatores
        if len(risk["factors"]) >= 2:
            risk["level"] = "high"
        elif len(risk["factors"]) == 1:
            risk["level"] = "medium"
        else:
            risk["level"] = "low"

        return risk

    def _generate_explanation_text(
        self,
        action: str,
        context: Dict[str, Any],
        can_execute: bool,
        reason: str,
        trust_level: float,
        alternatives: List[str],
        risk_assessment: Dict[str, Any],
    ) -> str:
        """Gera texto explicativo da decisão.

        Args:
            action: Nome da ação
            context: Contexto da decisão
            can_execute: Se pode executar
            reason: Motivo da decisão
            trust_level: Nível de confiança
            alternatives: Alternativas consideradas
            risk_assessment: Avaliação de risco

        Returns:
            Texto explicativo
        """
        if can_execute:
            explanation = f"Ação '{action}' APROVADA para execução automática.\n"
            explanation += f"Motivo: {reason}\n"
            explanation += f"Nível de confiança: {trust_level:.2f}\n"
        else:
            explanation = f"Ação '{action}' NEGADA.\n"
            explanation += f"Motivo: {reason}\n"
            explanation += f"Nível de confiança atual: {trust_level:.2f}\n"

        if alternatives:
            explanation += f"\nAlternativas consideradas: {', '.join(alternatives)}\n"

        if risk_assessment:
            explanation += f"\nNível de risco: {risk_assessment['level']}\n"
            if risk_assessment.get("factors"):
                explanation += f"Fatores de risco: {', '.join(risk_assessment['factors'])}\n"

        return explanation

    def record_execution_result(
        self, explanation: DecisionExplanation, result: Dict[str, Any]
    ) -> None:
        """Registra resultado da execução na explicação.

        Args:
            explanation: Explicação da decisão
            result: Resultado da execução
        """
        explanation.execution_result = result
        logger.debug("Resultado de execução registrado para ação: %s", explanation.action)

    def get_explanation_history(self, limit: int = 10) -> List[DecisionExplanation]:
        """Obtém histórico de explicações.

        Args:
            limit: Número máximo de explicações a retornar

        Returns:
            Lista de explicações recentes
        """
        return self.explanation_history[-limit:]

    def get_explanations_by_action(self, action: str, limit: int = 10) -> List[DecisionExplanation]:
        """Obtém explicações de uma ação específica.

        Args:
            action: Nome da ação
            limit: Número máximo de explicações a retornar

        Returns:
            Lista de explicações da ação
        """
        explanations = [e for e in self.explanation_history if e.action == action]
        return explanations[-limit:]

    def get_explanation_summary(self) -> Dict[str, Any]:
        """Obtém resumo do sistema de explicabilidade.

        Returns:
            Dicionário com resumo
        """
        total = len(self.explanation_history)
        approved = sum(1 for e in self.explanation_history if e.permission_result["can_execute"])
        denied = total - approved

        return {
            "total_explanations": total,
            "approved_decisions": approved,
            "denied_decisions": denied,
            "approval_rate": approved / total if total > 0 else 0.0,
        }

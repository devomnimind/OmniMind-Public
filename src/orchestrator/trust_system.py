"""
Sistema de Confiança Crescente para Orchestrator.

Implementa Seção 5 da Auditoria do Orchestrator:
- Rastreamento de histórico de decisões
- Cálculo de confiança baseado em sucesso/falha
- Aumento gradual de autonomia com decisões bem-sucedidas
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DecisionRecord:
    """Registro de uma decisão autônoma."""

    action: str
    success: bool
    context: Dict[str, Any]
    timestamp: float
    trust_level_before: float
    trust_level_after: float
    reason: str = ""


class TrustSystem:
    """Sistema de confiança crescente baseado em histórico de decisões."""

    def __init__(self, initial_trust: float = 0.5, max_history: int = 1000) -> None:
        """Inicializa sistema de confiança.

        Args:
            initial_trust: Nível inicial de confiança (0.0 a 1.0)
            max_history: Tamanho máximo do histórico
        """
        self.initial_trust = initial_trust
        self.max_history = max_history
        self.trust_scores: Dict[str, float] = {}  # action -> trust_score
        self.decision_history: List[DecisionRecord] = []
        self.success_count: Dict[str, int] = {}
        self.failure_count: Dict[str, int] = {}
        self.total_decisions: Dict[str, int] = {}

        logger.info("TrustSystem inicializado (confiança inicial: %.2f)", initial_trust)

    def record_decision(
        self,
        action: str,
        success: bool,
        context: Dict[str, Any],
        reason: str = "",
    ) -> None:
        """Registra decisão e atualiza confiança.

        Args:
            action: Nome da ação executada
            success: Se a decisão foi bem-sucedida
            context: Contexto da decisão
            reason: Motivo da decisão
        """
        trust_before = self.get_trust_level(action)

        # Inicializar contadores se necessário
        if action not in self.success_count:
            self.success_count[action] = 0
        if action not in self.failure_count:
            self.failure_count[action] = 0
        if action not in self.total_decisions:
            self.total_decisions[action] = 0

        # Atualizar contadores
        if success:
            self.success_count[action] = self.success_count[action] + 1
        else:
            self.failure_count[action] = self.failure_count[action] + 1

        self.total_decisions[action] = self.total_decisions[action] + 1

        # Calcular novo trust score
        total = self.total_decisions[action]
        if total > 0:
            success_rate = self.success_count[action] / total
            # Aplicar decay para decisões antigas (peso maior para decisões recentes)
            # Por simplicidade, usamos média simples, mas pode ser melhorado com decay
            self.trust_scores[action] = success_rate

        trust_after = self.get_trust_level(action)

        # Criar registro
        record = DecisionRecord(
            action=action,
            success=success,
            context=context,
            timestamp=time.time(),
            trust_level_before=trust_before,
            trust_level_after=trust_after,
            reason=reason,
        )

        # Adicionar ao histórico
        self.decision_history.append(record)
        if len(self.decision_history) > self.max_history:
            self.decision_history.pop(0)

        logger.debug(
            "Decisão registrada: %s (sucesso: %s, confiança: %.2f -> %.2f)",
            action,
            success,
            trust_before,
            trust_after,
        )

    def get_trust_level(self, action: str) -> float:
        """Obtém nível de confiança para ação.

        Args:
            action: Nome da ação

        Returns:
            Nível de confiança (0.0 a 1.0)
        """
        if action in self.trust_scores:
            return self.trust_scores[action]
        return self.initial_trust

    def get_global_trust_level(self) -> float:
        """Obtém nível de confiança global (média de todas as ações).

        Returns:
            Nível de confiança global (0.0 a 1.0)
        """
        if not self.trust_scores:
            return self.initial_trust

        total_trust = sum(self.trust_scores.values())
        return total_trust / len(self.trust_scores)

    def get_action_statistics(self, action: str) -> Dict[str, Any]:
        """Obtém estatísticas de uma ação.

        Args:
            action: Nome da ação

        Returns:
            Dicionário com estatísticas
        """
        total = self.total_decisions.get(action, 0)
        success = self.success_count.get(action, 0)
        failure = self.failure_count.get(action, 0)

        if total == 0:
            return {
                "action": action,
                "total_decisions": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
                "trust_level": self.initial_trust,
            }

        return {
            "action": action,
            "total_decisions": total,
            "success_count": success,
            "failure_count": failure,
            "success_rate": success / total,
            "trust_level": self.get_trust_level(action),
        }

    def get_recent_decisions(self, limit: int = 10) -> List[DecisionRecord]:
        """Obtém decisões recentes.

        Args:
            limit: Número máximo de decisões a retornar

        Returns:
            Lista de decisões recentes
        """
        return self.decision_history[-limit:]

    def get_decisions_by_action(self, action: str, limit: int = 10) -> List[DecisionRecord]:
        """Obtém decisões de uma ação específica.

        Args:
            action: Nome da ação
            limit: Número máximo de decisões a retornar

        Returns:
            Lista de decisões da ação
        """
        decisions = [d for d in self.decision_history if d.action == action]
        return decisions[-limit:]

    def reset_trust(self, action: Optional[str] = None) -> None:
        """Reseta confiança de uma ação ou todas.

        Args:
            action: Nome da ação (None para resetar todas)
        """
        if action:
            if action in self.trust_scores:
                del self.trust_scores[action]
            if action in self.success_count:
                del self.success_count[action]
            if action in self.failure_count:
                del self.failure_count[action]
            if action in self.total_decisions:
                del self.total_decisions[action]
            logger.info("Confiança resetada para ação: %s", action)
        else:
            self.trust_scores.clear()
            self.success_count.clear()
            self.failure_count.clear()
            self.total_decisions.clear()
            logger.info("Confiança resetada para todas as ações")

    def get_summary(self) -> Dict[str, Any]:
        """Obtém resumo do sistema de confiança.

        Returns:
            Dicionário com resumo
        """
        return {
            "global_trust_level": self.get_global_trust_level(),
            "total_actions_tracked": len(self.trust_scores),
            "total_decisions": len(self.decision_history),
            "actions": {
                action: self.get_action_statistics(action) for action in self.trust_scores.keys()
            },
        }

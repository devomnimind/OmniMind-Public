"""
Sistema de Métricas de Confiança Humano-IA.

Trust é construído através de:
- Consistência (reliability)
- Transparência (explainability)
- Competência (success rate)
- Alinhamento (value alignment)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TrustEvent:
    """Evento que afeta trust."""

    timestamp: datetime
    event_type: str  # 'success', 'failure', 'correction', 'feedback'
    trust_delta: float
    context: Dict[str, Any] = field(default_factory=dict)


class TrustMetrics:
    """
    Sistema de métricas de confiança humano-IA.

    Trust é construído através de:
    - Consistência (reliability)
    - Transparência (explainability)
    - Competência (success rate)
    - Alinhamento (value alignment)
    """

    def __init__(self) -> None:
        """Inicializa sistema de trust metrics."""
        # Trust scores por humano
        self.trust_scores: Dict[str, float] = {}

        # Histórico de eventos
        self.trust_history: Dict[str, List[TrustEvent]] = {}

        # Componentes de trust
        self.reliability_scores: Dict[str, float] = {}
        self.transparency_scores: Dict[str, float] = {}
        self.competence_scores: Dict[str, float] = {}
        self.alignment_scores: Dict[str, float] = {}

    def get_trust_level(self, human_id: str) -> float:
        """
        Retorna nível de confiança atual (0-1).

        Trust = weighted average of:
        - 0.3 * reliability
        - 0.3 * competence
        - 0.2 * transparency
        - 0.2 * alignment

        Args:
            human_id: Identificador do humano

        Returns:
            Nível de confiança entre 0 e 1
        """
        if human_id not in self.trust_scores:
            # Novo humano: trust inicial moderado
            self._initialize_trust(human_id)

        return (
            0.3 * self.reliability_scores[human_id]
            + 0.3 * self.competence_scores[human_id]
            + 0.2 * self.transparency_scores[human_id]
            + 0.2 * self.alignment_scores[human_id]
        )

    def _initialize_trust(self, human_id: str) -> None:
        """Inicializa trust para novo humano."""
        self.trust_scores[human_id] = 0.5
        self.reliability_scores[human_id] = 0.5
        self.transparency_scores[human_id] = 0.5
        self.competence_scores[human_id] = 0.5
        self.alignment_scores[human_id] = 0.5

    def update_trust(self, human_id: str, outcome: Dict[str, Any]) -> float:
        """
        Atualiza trust baseado em outcome de colaboração.

        Args:
            human_id: Identificador do humano
            outcome: Resultado da colaboração com chaves:
                - success: bool
                - transparent: bool (opcional)
                - aligned_with_values: bool (opcional)

        Returns:
            Trust delta (mudança)
        """
        old_trust = self.get_trust_level(human_id)

        # Atualiza componentes
        if outcome.get("success"):
            self.reliability_scores[human_id] = min(self.reliability_scores[human_id] + 0.05, 1.0)
            self.competence_scores[human_id] = min(self.competence_scores[human_id] + 0.05, 1.0)
        else:
            self.reliability_scores[human_id] = max(self.reliability_scores[human_id] - 0.1, 0.0)

        if outcome.get("transparent"):
            self.transparency_scores[human_id] = min(self.transparency_scores[human_id] + 0.05, 1.0)

        if outcome.get("aligned_with_values"):
            self.alignment_scores[human_id] = min(self.alignment_scores[human_id] + 0.05, 1.0)

        # Recalcula trust
        new_trust = self.get_trust_level(human_id)
        trust_delta = new_trust - old_trust

        # Registra evento
        event = TrustEvent(
            timestamp=datetime.now(),
            event_type="success" if outcome.get("success") else "failure",
            trust_delta=trust_delta,
            context=outcome,
        )

        if human_id not in self.trust_history:
            self.trust_history[human_id] = []
        self.trust_history[human_id].append(event)

        logger.info(
            f"Trust updated for {human_id}: {old_trust:.2f} → {new_trust:.2f} "
            f"(Δ={trust_delta:+.2f})"
        )

        return trust_delta

    def get_trust_breakdown(self, human_id: str) -> Dict[str, float]:
        """
        Retorna breakdown de trust por componente.

        Args:
            human_id: Identificador do humano

        Returns:
            Dicionário com scores de cada componente
        """
        if human_id not in self.trust_scores:
            self._initialize_trust(human_id)

        return {
            "overall": self.get_trust_level(human_id),
            "reliability": self.reliability_scores[human_id],
            "competence": self.competence_scores[human_id],
            "transparency": self.transparency_scores[human_id],
            "alignment": self.alignment_scores[human_id],
        }

    def get_trust_history(self, human_id: str, limit: Optional[int] = None) -> List[TrustEvent]:
        """
        Retorna histórico de eventos de trust.

        Args:
            human_id: Identificador do humano
            limit: Número máximo de eventos (mais recentes primeiro)

        Returns:
            Lista de eventos de trust
        """
        if human_id not in self.trust_history:
            return []

        history = self.trust_history[human_id]
        if limit:
            return history[-limit:]
        return history

    def reset_trust(self, human_id: str) -> None:
        """
        Reseta trust para valores iniciais.

        Args:
            human_id: Identificador do humano
        """
        self._initialize_trust(human_id)
        if human_id in self.trust_history:
            self.trust_history[human_id] = []
        logger.info(f"Trust reset for {human_id}")

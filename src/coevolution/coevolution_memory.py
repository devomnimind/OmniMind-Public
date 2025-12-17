"""
Sistema de Memória de Co-evolução.

Armazena histórico de colaboração humano-IA para aprendizado contínuo.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CollaborationSession:
    """Sessão de colaboração."""

    session_id: str
    human_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    task_description: str = ""
    outcome: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    trust_evolution: List[float] = field(default_factory=list)


@dataclass
class LearningPattern:
    """Padrão de aprendizado identificado."""

    pattern_id: str
    pattern_type: str
    occurrences: int = 0
    success_rate: float = 0.0
    contexts: List[Dict[str, Any]] = field(default_factory=list)


class CoevolutionMemory:
    """
    Memória de co-evolução humano-IA.

    Armazena:
    - Sessões de colaboração
    - Padrões de aprendizado
    - Evolução de trust
    - Insights gerados
    """

    def __init__(self) -> None:
        """Inicializa memória de co-evolução."""
        self.sessions: Dict[str, CollaborationSession] = {}
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.global_insights: List[str] = []

    def store_collaboration(self, human_id: str, task: str, outcome: Dict[str, Any]) -> str:
        """
        Armazena sessão de colaboração.

        Args:
            human_id: ID do humano
            task: Descrição da tarefa
            outcome: Resultado da colaboração

        Returns:
            ID da sessão criada
        """
        session_id = f"session_{len(self.sessions)}_{datetime.now().timestamp()}"

        session = CollaborationSession(
            session_id=session_id,
            human_id=human_id,
            start_time=datetime.now(),
            task_description=task,
            outcome=outcome,
        )

        self.sessions[session_id] = session

        logger.info(f"Collaboration stored: {session_id}")

        # Extrai insights
        self._extract_insights(session)

        return session_id

    def complete_session(self, session_id: str, insights: Optional[List[str]] = None) -> None:
        """
        Completa sessão de colaboração.

        Args:
            session_id: ID da sessão
            insights: Insights gerados (opcional)
        """
        if session_id not in self.sessions:
            logger.error(f"Session not found: {session_id}")
            return

        session = self.sessions[session_id]
        session.end_time = datetime.now()

        if insights:
            session.insights.extend(insights)
            self.global_insights.extend(insights)

        logger.info(f"Session completed: {session_id}")

    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """
        Retorna sessão específica.

        Args:
            session_id: ID da sessão

        Returns:
            Sessão ou None
        """
        return self.sessions.get(session_id)

    def get_human_sessions(
        self, human_id: str, limit: Optional[int] = None
    ) -> List[CollaborationSession]:
        """
        Retorna sessões de um humano.

        Args:
            human_id: ID do humano
            limit: Número máximo de sessões

        Returns:
            Lista de sessões
        """
        sessions = [s for s in self.sessions.values() if s.human_id == human_id]

        # Ordena por data (mais recente primeiro)
        sessions.sort(key=lambda s: s.start_time, reverse=True)

        if limit:
            sessions = sessions[:limit]

        return sessions

    def _extract_insights(self, session: CollaborationSession) -> None:
        """Extrai insights de sessão."""
        outcome = session.outcome

        # Insight sobre sucesso
        if outcome.get("success"):
            insight = f"Colaboração bem-sucedida em: {session.task_description[:50]}"
            session.insights.append(insight)

        # Insight sobre trust
        if "trust_delta" in outcome:
            trust_delta = outcome["trust_delta"]
            if trust_delta > 0.1:
                insight = f"Trust aumentou significativamente (+{trust_delta:.2f})"
                session.insights.append(insight)
            elif trust_delta < -0.1:
                insight = f"Trust diminuiu (-{abs(trust_delta):.2f}), revisar abordagem"
                session.insights.append(insight)

        # Insight sobre aprendizado
        if outcome.get("ai_learning_gain", 0) > 0.5:
            insight = "Alto ganho de aprendizado da IA nesta colaboração"
            session.insights.append(insight)

    def identify_learning_patterns(self) -> List[LearningPattern]:
        """
        Identifica padrões de aprendizado.

        Returns:
            Lista de padrões identificados
        """
        # Analisa sessões para identificar padrões
        success_tasks: Dict[str, int] = {}
        failure_tasks: Dict[str, int] = {}

        for session in self.sessions.values():
            task_type = self._categorize_task(session.task_description)

            if session.outcome.get("success"):
                success_tasks[task_type] = success_tasks.get(task_type, 0) + 1
            else:
                failure_tasks[task_type] = failure_tasks.get(task_type, 0) + 1

        # Cria padrões
        patterns = []
        for task_type in set(success_tasks.keys()) | set(failure_tasks.keys()):
            successes = success_tasks.get(task_type, 0)
            failures = failure_tasks.get(task_type, 0)
            total = successes + failures

            if total == 0:
                continue

            pattern = LearningPattern(
                pattern_id=f"pattern_{task_type}",
                pattern_type=task_type,
                occurrences=total,
                success_rate=successes / total,
            )

            patterns.append(pattern)
            self.learning_patterns[pattern.pattern_id] = pattern

        return patterns

    def _categorize_task(self, task_description: str) -> str:
        """Categoriza tarefa."""
        # Implementação simplificada
        if "code" in task_description.lower():
            return "coding"
        elif "analise" in task_description.lower() or "analysis" in task_description.lower():
            return "analysis"
        elif "decisao" in task_description.lower() or "decision" in task_description.lower():
            return "decision"
        else:
            return "general"

    def get_collaboration_statistics(self, human_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna estatísticas de colaboração.

        Args:
            human_id: Filtrar por humano (opcional)

        Returns:
            Dicionário com estatísticas
        """
        sessions: List[CollaborationSession] = list(self.sessions.values())

        if human_id:
            sessions = [s for s in sessions if s.human_id == human_id]

        if not sessions:
            return {
                "total_sessions": 0,
                "success_rate": 0.0,
                "average_trust_evolution": 0.0,
            }

        total = len(sessions)
        successes = sum(1 for s in sessions if s.outcome.get("success"))

        # Trust evolution
        trust_deltas = [s.outcome.get("trust_delta", 0.0) for s in sessions]
        avg_trust_evolution = sum(trust_deltas) / len(trust_deltas) if trust_deltas else 0.0

        return {
            "total_sessions": total,
            "success_rate": successes / total,
            "average_trust_evolution": avg_trust_evolution,
            "total_insights": len(self.global_insights),
        }

    def get_insights_summary(self, limit: Optional[int] = None) -> List[str]:
        """
        Retorna sumário de insights.

        Args:
            limit: Número máximo de insights

        Returns:
            Lista de insights
        """
        insights = self.global_insights

        if limit:
            insights = insights[-limit:]

        return insights

    def clear_old_sessions(self, days: int = 30) -> int:
        """
        Remove sessões antigas.

        Args:
            days: Número de dias para manter

        Returns:
            Número de sessões removidas
        """
        from datetime import timedelta

        threshold = datetime.now() - timedelta(days=days)

        old_sessions = [
            sid for sid, session in self.sessions.items() if session.start_time < threshold
        ]

        for sid in old_sessions:
            del self.sessions[sid]

        logger.info(f"Removed {len(old_sessions)} old sessions")

        return len(old_sessions)

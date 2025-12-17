"""
Framework de Colaboração Human-Centered AI (HCHAC).

Orquestra colaboração humano-IA baseada em:
1. Humano lidera (human-centered)
2. IA é parceiro, não ferramenta
3. Negociação bidirecional de objetivos
4. Trust é construído, não imposto
5. Feedback é diálogo, não comando
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Role(Enum):
    """Papéis possíveis em colaboração."""

    LEADER = "leader"
    CONTRIBUTOR = "contributor"
    ADVISOR = "advisor"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"


@dataclass
class CollaborationOutcome:
    """Resultado de colaboração."""

    success: bool
    human_satisfaction: float  # 0-1
    ai_learning_gain: float  # 0-1
    trust_delta: float  # -1 a +1
    insights_generated: List[str] = field(default_factory=list)
    execution_result: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionResult:
    """Resultado de execução de tarefa."""

    success: bool
    satisfaction: float
    insights: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)


class HCHACFramework:
    """
    Human-Centered Human-AI Collaboration Framework.

    Princípios:
    1. Humano lidera (human-centered)
    2. IA é parceiro, não ferramenta
    3. Negociação bidirecional de objetivos
    4. Trust é construído, não imposto
    5. Feedback é diálogo, não comando
    """

    def __init__(self) -> None:
        """Inicializa framework HCHAC."""
        from .bias_detector import BiasDetector
        from .bidirectional_feedback import BidirectionalFeedback
        from .coevolution_memory import CoevolutionMemory
        from .negotiation import GoalNegotiator
        from .trust_metrics import TrustMetrics

        self.trust = TrustMetrics()
        self.negotiator = GoalNegotiator()
        self.feedback = BidirectionalFeedback()
        self.bias_detector = BiasDetector()
        self.memory = CoevolutionMemory()

    def co_execute_task(
        self,
        human_id: str,
        task_description: str,
        human_intent: Dict[str, Any],
        ai_capabilities: Optional[List[str]] = None,
    ) -> CollaborationOutcome:
        """
        Execução colaborativa de tarefa.

        Flow:
        1. Negociar objetivo (humano propõe, IA questiona/refina)
        2. Alocar papéis dinamicamente
        3. Executar com feedback bidirecional
        4. Monitorar viés
        5. Aprender mutuamente

        Args:
            human_id: Identificador do humano
            task_description: Descrição da tarefa
            human_intent: Intenção/objetivo do humano
            ai_capabilities: Capacidades disponíveis da IA

        Returns:
            CollaborationOutcome com resultados
        """
        logger.info(f"Starting co-execution: {task_description}")

        if ai_capabilities is None:
            ai_capabilities = []

        # 1. Negociação de objetivo
        negotiated_goal = self.negotiator.negotiate(
            human_intent=human_intent,
            ai_perspective=self._generate_ai_perspective(task_description),
            trust_level=self.trust.get_trust_level(human_id),
        )

        if not negotiated_goal.agreement_reached:
            logger.warning("Goal negotiation failed")
            return CollaborationOutcome(
                success=False,
                human_satisfaction=0.3,
                ai_learning_gain=0.0,
                trust_delta=-0.1,
                insights_generated=["Negociação de objetivo falhou"],
            )

        # 2. Alocação de papéis
        roles = self._allocate_roles(
            human_id=human_id,
            task=negotiated_goal.final_goal,
            ai_capabilities=ai_capabilities,
        )

        # 3. Execução colaborativa
        execution_result = self._execute_with_roles(
            human_id=human_id, goal=negotiated_goal.final_goal, roles=roles
        )

        # 4. Detecção de viés
        if execution_result.data:
            biases = self.bias_detector.detect_bias(execution_result.data)
            if biases:
                logger.warning(f"Detected {len(biases)} biases, applying corrections")
                execution_result.data = self.bias_detector.correct_bias(execution_result.data)

        # 5. Atualização de trust
        trust_delta = self.trust.update_trust(
            human_id=human_id,
            outcome={
                "success": execution_result.success,
                "transparent": True,
                "aligned_with_values": True,
            },
        )

        # 6. Armazenamento em memória de co-evolução
        session_id = self.memory.store_collaboration(
            human_id=human_id,
            task=task_description,
            outcome={
                "success": execution_result.success,
                "trust_delta": trust_delta,
                "ai_learning_gain": self._calculate_learning_gain(execution_result),
            },
        )

        self.memory.complete_session(session_id=session_id, insights=execution_result.insights)

        return CollaborationOutcome(
            success=execution_result.success,
            human_satisfaction=execution_result.satisfaction,
            ai_learning_gain=self._calculate_learning_gain(execution_result),
            trust_delta=trust_delta,
            insights_generated=execution_result.insights,
            execution_result=execution_result.data,
        )

    def _generate_ai_perspective(self, task: str) -> Dict[str, Any]:
        """
        IA gera sua própria perspectiva sobre a tarefa.

        Args:
            task: Descrição da tarefa

        Returns:
            Perspectiva da IA
        """
        # TODO: Usar agente psicanalítico para questionar premissas
        return {
            "alternative_approaches": [
                "Considere abordagem incremental",
                "Valide premissas primeiro",
            ],
            "potential_risks": [
                "Risco de scope creep",
                "Possível impacto em performance",
            ],
            "questions_for_human": [
                "Qual é a prioridade: velocidade ou qualidade?",
                "Há constraints de recursos?",
            ],
        }

    def _allocate_roles(
        self, human_id: str, task: Dict[str, Any], ai_capabilities: List[str]
    ) -> Dict[str, Role]:
        """
        Aloca papéis dinamicamente baseado em competências.

        Args:
            human_id: ID do humano
            task: Objetivo da tarefa
            ai_capabilities: Capacidades da IA

        Returns:
            Dicionário com papéis alocados
        """
        # Humano sempre lidera (human-centered)
        roles = {"human": Role.LEADER}

        # IA assume papel baseado em trust e capabilities
        trust_level = self.trust.get_trust_level(human_id)

        if trust_level > 0.8 and "autonomous_execution" in ai_capabilities:
            roles["ai"] = Role.CONTRIBUTOR
        elif trust_level > 0.5:
            roles["ai"] = Role.ADVISOR
        else:
            roles["ai"] = Role.EXECUTOR  # Apenas executa comandos

        logger.info(f"Roles allocated: human={roles['human'].value}, ai={roles['ai'].value}")

        return roles

    def _execute_with_roles(
        self, human_id: str, goal: Dict[str, Any], roles: Dict[str, Role]
    ) -> ExecutionResult:
        """
        Executa tarefa respeitando papéis alocados.

        Args:
            human_id: ID do humano
            goal: Objetivo negociado
            roles: Papéis alocados

        Returns:
            ExecutionResult
        """
        # Implementação simplificada para MVP
        # TODO: Implementar lógica de execução colaborativa real

        ai_role = roles.get("ai", Role.EXECUTOR)

        insights = []

        if ai_role == Role.CONTRIBUTOR:
            insights.append("IA contribuiu ativamente para decisões")
        elif ai_role == Role.ADVISOR:
            insights.append("IA ofereceu recomendações consultivas")
        else:
            insights.append("IA executou comandos conforme direcionado")

        # Simula execução bem-sucedida
        return ExecutionResult(
            success=True,
            satisfaction=0.8,
            insights=insights,
            data={"goal": goal, "role": ai_role.value, "execution_time": 1.5},
        )

    def _calculate_learning_gain(self, result: ExecutionResult) -> float:
        """
        Calcula quanto a IA aprendeu da colaboração.

        Args:
            result: Resultado da execução

        Returns:
            Learning gain (0-1)
        """
        # Implementação simplificada
        # TODO: Métricas reais de aprendizado

        base_gain = 0.3

        if result.success:
            base_gain += 0.2

        if len(result.insights) > 2:
            base_gain += 0.1

        return min(base_gain, 1.0)

    def get_trust_dashboard(self, human_id: str) -> Dict[str, Any]:
        """
        Retorna dashboard de trust para humano.

        Args:
            human_id: ID do humano

        Returns:
            Dados do dashboard
        """
        return {
            "trust_breakdown": self.trust.get_trust_breakdown(human_id),
            "trust_history": self.trust.get_trust_history(human_id, limit=10),
            "collaboration_stats": self.memory.get_collaboration_statistics(human_id),
            "recent_insights": self.memory.get_insights_summary(limit=5),
        }

    def submit_human_feedback(
        self,
        human_id: str,
        feedback_type: str,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Submete feedback do humano.

        Args:
            human_id: ID do humano
            feedback_type: Tipo de feedback
            content: Conteúdo do feedback
            context: Contexto adicional
        """
        from .bidirectional_feedback import FeedbackType

        # Converte string para enum
        try:
            fb_type = FeedbackType[feedback_type.upper()]
        except KeyError:
            logger.error(f"Invalid feedback type: {feedback_type}")
            return

        self.feedback.submit_human_feedback(feedback_type=fb_type, content=content, context=context)

    def get_ai_feedback(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retorna feedback da IA para humano.

        Args:
            limit: Número máximo de itens

        Returns:
            Lista de feedback
        """
        from .bidirectional_feedback import FeedbackDirection

        items = self.feedback.get_feedback_summary(
            direction=FeedbackDirection.AI_TO_HUMAN, limit=limit
        )

        return [
            {
                "timestamp": item.timestamp.isoformat(),
                "type": item.feedback_type.value,
                "content": item.content,
                "acknowledged": item.acknowledged,
            }
            for item in items
        ]

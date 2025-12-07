"""
Meta-ReAct Coordinator - Coordenação em Nível Meta

Implementa capacidades Meta-ReAct:
1. Coordenação em nível meta (além do ReAct padrão)
2. Gerenciamento de mudanças de estratégia
3. Recuperação de falhas em nível meta
4. Composição de agentes

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .error_analyzer import ErrorAnalyzer, ErrorAnalysis, RecoveryStrategy

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Tipos de estratégia de execução."""

    SEQUENTIAL = "sequential"  # Execução sequencial
    PARALLEL = "parallel"  # Execução paralela
    PIPELINE = "pipeline"  # Pipeline com dependências
    ADAPTIVE = "adaptive"  # Adapta estratégia dinamicamente


@dataclass
class StrategyChange:
    """Mudança de estratégia."""

    from_strategy: StrategyType
    to_strategy: StrategyType
    reason: str
    timestamp: float
    context: Dict[str, Any]


@dataclass
class AgentComposition:
    """Composição de agentes para tarefa."""

    agents: List[str]  # Nomes dos agentes
    execution_order: List[int]  # Ordem de execução
    dependencies: Dict[int, List[int]]  # Dependências entre agentes
    strategy: StrategyType


class MetaReActCoordinator:
    """
    Coordenador Meta-ReAct para OrchestratorAgent.

    Características:
    - Coordenação em nível meta (além do ReAct padrão)
    - Gerenciamento de mudanças de estratégia
    - Recuperação de falhas em nível meta
    - Composição de agentes
    """

    def __init__(self, error_analyzer: Optional[ErrorAnalyzer] = None):
        """
        Inicializa MetaReActCoordinator.

        Args:
            error_analyzer: ErrorAnalyzer para análise de erros
        """
        self.error_analyzer = error_analyzer or ErrorAnalyzer()
        self.strategy_history: List[StrategyChange] = []
        self.current_strategy: StrategyType = StrategyType.ADAPTIVE
        self.agent_compositions: List[AgentComposition] = []

    def coordinate_meta_level(
        self,
        task: str,
        agents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Coordena tarefa em nível meta.

        Args:
            task: Descrição da tarefa
            agents: Lista de agentes disponíveis
            context: Contexto adicional

        Returns:
            Plano de coordenação meta
        """
        # Analisar tarefa para determinar estratégia
        strategy = self._determine_strategy(task, agents, context)

        # Criar composição de agentes
        composition = self._compose_agents(task, agents, strategy)

        # Registrar composição
        self.agent_compositions.append(composition)

        return {
            "strategy": strategy.value,
            "composition": {
                "agents": composition.agents,
                "execution_order": composition.execution_order,
                "dependencies": composition.dependencies,
            },
            "meta_coordination": True,
        }

    def manage_strategy_change(
        self,
        current_strategy: StrategyType,
        new_strategy: StrategyType,
        reason: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> StrategyChange:
        """
        Gerencia mudança de estratégia.

        Args:
            current_strategy: Estratégia atual
            new_strategy: Nova estratégia
            reason: Razão da mudança
            context: Contexto adicional

        Returns:
            StrategyChange registrada
        """
        import time

        change = StrategyChange(
            from_strategy=current_strategy,
            to_strategy=new_strategy,
            reason=reason,
            timestamp=time.time(),
            context=context or {},
        )

        self.strategy_history.append(change)
        self.current_strategy = new_strategy

        logger.info(
            f"Mudança de estratégia: {current_strategy.value} → {new_strategy.value} "
            f"(razão: {reason})"
        )

        return change

    def recover_from_failure_meta(
        self,
        task: str,
        error: Exception,
        failed_agents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Recupera de falha em nível meta.

        Args:
            task: Tarefa que falhou
            error: Erro ocorrido
            failed_agents: Lista de agentes que falharam
            context: Contexto adicional

        Returns:
            Plano de recuperação meta
        """
        # Analisar erro estruturalmente
        error_analysis = self.error_analyzer.analyze_error(error, context)

        # Determinar estratégia de recuperação
        recovery_strategy = error_analysis.recovery_strategy

        # Criar plano de recuperação
        recovery_plan = self._create_recovery_plan(
            task, error_analysis, failed_agents, recovery_strategy
        )

        logger.info(
            f"Recuperação meta: {recovery_strategy.value} para {len(failed_agents)} agentes"
        )

        return recovery_plan

    def compose_agents(
        self,
        task: str,
        available_agents: List[str],
        strategy: Optional[StrategyType] = None,
    ) -> AgentComposition:
        """
        Compõe agentes para tarefa.

        Args:
            task: Descrição da tarefa
            available_agents: Lista de agentes disponíveis
            strategy: Estratégia de execução (opcional)

        Returns:
            AgentComposition
        """
        if strategy is None:
            strategy = self._determine_strategy(task, available_agents)

        composition = self._compose_agents(task, available_agents, strategy)
        self.agent_compositions.append(composition)

        return composition

    def _determine_strategy(
        self,
        task: str,
        agents: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> StrategyType:
        """
        Determina estratégia de execução baseada na tarefa.

        Args:
            task: Descrição da tarefa
            agents: Lista de agentes disponíveis
            context: Contexto adicional

        Returns:
            StrategyType recomendado
        """
        # Heurísticas simples para determinar estratégia
        task_lower = task.lower()

        # Se tarefa menciona "paralelo" ou "simultâneo"
        if "paralelo" in task_lower or "simultâneo" in task_lower:
            return StrategyType.PARALLEL

        # Se tarefa menciona "sequência" ou "ordem"
        if "sequência" in task_lower or "ordem" in task_lower:
            return StrategyType.SEQUENTIAL

        # Se há dependências explícitas
        if context and context.get("dependencies"):
            return StrategyType.PIPELINE

        # Padrão: adaptativo
        return StrategyType.ADAPTIVE

    def _compose_agents(
        self,
        task: str,
        agents: List[str],
        strategy: StrategyType,
    ) -> AgentComposition:
        """
        Compõe agentes para tarefa.

        Args:
            task: Descrição da tarefa
            agents: Lista de agentes disponíveis
            strategy: Estratégia de execução

        Returns:
            AgentComposition
        """
        # Ordem de execução simples (pode ser melhorada com análise de dependências)
        execution_order = list(range(len(agents)))

        # Dependências vazias por padrão (pode ser melhorado)
        dependencies: Dict[int, List[int]] = {}

        return AgentComposition(
            agents=agents,
            execution_order=execution_order,
            dependencies=dependencies,
            strategy=strategy,
        )

    def _create_recovery_plan(
        self,
        task: str,
        error_analysis: ErrorAnalysis,
        failed_agents: List[str],
        recovery_strategy: RecoveryStrategy,
    ) -> Dict[str, Any]:
        """
        Cria plano de recuperação.

        Args:
            task: Tarefa que falhou
            error_analysis: Análise do erro
            failed_agents: Lista de agentes que falharam
            recovery_strategy: Estratégia de recuperação

        Returns:
            Plano de recuperação
        """
        plan: Dict[str, Any] = {
            "recovery_strategy": recovery_strategy.value,
            "error_type": error_analysis.error_type.value,
            "failed_agents": failed_agents,
            "suggested_actions": error_analysis.suggested_actions,
            "alternative_strategies": [s.value for s in error_analysis.alternative_strategies],
        }

        # Ajustar estratégia baseado no erro
        if recovery_strategy == RecoveryStrategy.REORDER_TASKS:
            plan["new_strategy"] = StrategyType.SEQUENTIAL.value
        elif recovery_strategy == RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT:
            plan["new_strategy"] = StrategyType.ADAPTIVE.value
        else:
            plan["new_strategy"] = self.current_strategy.value

        return plan

    def get_strategy_history(self) -> List[StrategyChange]:
        """Retorna histórico de mudanças de estratégia."""
        return self.strategy_history.copy()

    def get_current_strategy(self) -> StrategyType:
        """Retorna estratégia atual."""
        return self.current_strategy

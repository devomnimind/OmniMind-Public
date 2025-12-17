"""
AgentRegistry - Registro centralizado de agentes com health checks.

Implementa recomendações da Seção 1 da AUDITORIA_ORCHESTRATOR_COMPLETA.md:
- Registro centralizado de agentes
- Verificação de saúde antes de usar agentes
- Sistema de inicialização prioritária
- Fallbacks se agente falhar
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentPriority(Enum):
    """Prioridades de inicialização de agentes."""

    CRITICAL = 0  # Deve estar sempre disponível (security, metacognition)
    ESSENTIAL = 1  # Necessário para operação normal (orchestrator)
    OPTIONAL = 2  # Pode ser carregado sob demanda (code, architect, debug, reviewer)


@dataclass
class AgentHealth:
    """Estado de saúde de um agente."""

    healthy: bool
    last_check: float
    failure_count: int
    last_error: Optional[str] = None


class AgentRegistry:
    """Registro centralizado de agentes com health checks e gerenciamento de ciclo de vida."""

    def __init__(self) -> None:
        self._agents: Dict[str, Any] = {}
        self._health_status: Dict[str, AgentHealth] = {}
        self._initialization_priority: List[str] = [
            "security",
            "metacognition",
            "orchestrator",
            "code",
            "architect",
            "debug",
            "reviewer",
            "psychoanalyst",
        ]
        self._agent_priorities: Dict[str, AgentPriority] = {
            "security": AgentPriority.CRITICAL,
            "metacognition": AgentPriority.CRITICAL,
            "orchestrator": AgentPriority.ESSENTIAL,
            "code": AgentPriority.OPTIONAL,
            "architect": AgentPriority.OPTIONAL,
            "debug": AgentPriority.OPTIONAL,
            "reviewer": AgentPriority.OPTIONAL,
            "psychoanalyst": AgentPriority.OPTIONAL,
        }

    def register_agent(
        self, name: str, agent: Any, priority: Optional[AgentPriority] = None
    ) -> None:
        """Registra agente com prioridade.

        Args:
            name: Nome único do agente
            agent: Instância do agente (qualquer tipo)
            priority: Prioridade de inicialização (opcional)
        """
        self._agents[name] = agent
        self._health_status[name] = AgentHealth(
            healthy=True, last_check=time.time(), failure_count=0
        )

        if priority:
            self._agent_priorities[name] = priority

        logger.info("Agente %s registrado com sucesso", name)

    def get_agent(self, name: str) -> Optional[Any]:
        """Obtém agente com verificação de saúde.

        Args:
            name: Nome do agente

        Returns:
            Instância do agente ou None se não estiver saudável
        """
        if name not in self._agents:
            logger.warning("Agente %s não encontrado no registro", name)
            return None

        health = self._health_status.get(name)
        if not health or not health.healthy:
            logger.warning("Agente %s não está saudável", name)
            return None

        return self._agents[name]

    def is_agent_healthy(self, name: str) -> bool:
        """Verifica se agente está saudável.

        Args:
            name: Nome do agente

        Returns:
            True se agente está saudável, False caso contrário
        """
        health = self._health_status.get(name)
        return health is not None and health.healthy

    async def health_check_all(self) -> Dict[str, bool]:
        """Verifica saúde de todos os agentes registrados.

        Returns:
            Dicionário com status de saúde de cada agente
        """
        results = {}

        for name, agent in self._agents.items():
            try:
                # Verificar se agente responde
                if hasattr(agent, "health_check"):
                    is_healthy = await agent.health_check()
                else:
                    # Se não tem método health_check, assume saudável
                    is_healthy = True

                results[name] = is_healthy

                # Atualizar status
                health = self._health_status[name]
                health.healthy = is_healthy
                health.last_check = time.time()

                if is_healthy:
                    health.failure_count = 0
                else:
                    health.failure_count += 1

            except Exception as e:
                logger.error("Health check falhou para agente %s: %s", name, e)
                results[name] = False

                health = self._health_status[name]
                health.healthy = False
                health.last_check = time.time()
                health.failure_count += 1
                health.last_error = str(e)

        return results

    async def health_check_single(self, name: str) -> bool:
        """Verifica saúde de um único agente.

        Args:
            name: Nome do agente

        Returns:
            True se agente está saudável, False caso contrário
        """
        if name not in self._agents:
            return False

        agent = self._agents[name]
        health = self._health_status[name]

        try:
            if hasattr(agent, "health_check"):
                is_healthy = await agent.health_check()
            else:
                is_healthy = True

            health.healthy = is_healthy
            health.last_check = time.time()

            if is_healthy:
                health.failure_count = 0
            else:
                health.failure_count += 1

            return is_healthy

        except Exception as e:
            logger.error("Health check falhou para agente %s: %s", name, e)
            health.healthy = False
            health.last_check = time.time()
            health.failure_count += 1
            health.last_error = str(e)
            return False

    def get_health_summary(self) -> Dict[str, Any]:
        """Obtém resumo de saúde de todos os agentes.

        Returns:
            Dicionário com informações de saúde
        """
        return {
            name: {
                "healthy": health.healthy,
                "last_check": health.last_check,
                "failure_count": health.failure_count,
                "last_error": health.last_error,
            }
            for name, health in self._health_status.items()
        }

    def list_agents(self) -> List[str]:
        """Lista todos os agentes registrados.

        Returns:
            Lista de nomes de agentes
        """
        return list(self._agents.keys())

    def get_priority(self, name: str) -> Optional[AgentPriority]:
        """Obtém prioridade de um agente.

        Args:
            name: Nome do agente

        Returns:
            Prioridade do agente ou None se não registrado
        """
        return self._agent_priorities.get(name)

    async def shutdown_all(self) -> None:
        """Desliga todos os agentes de forma ordenada."""
        logger.info("Iniciando shutdown de todos os agentes")

        # Desligar em ordem reversa de prioridade
        agents_by_priority = sorted(
            self._agents.items(),
            key=lambda x: self._agent_priorities.get(x[0], AgentPriority.OPTIONAL).value,
            reverse=True,
        )

        for name, agent in agents_by_priority:
            try:
                if hasattr(agent, "shutdown"):
                    await agent.shutdown()
                    logger.info("Agente %s desligado com sucesso", name)
            except Exception as e:
                logger.error("Erro ao desligar agente %s: %s", name, e)

        self._agents.clear()
        self._health_status.clear()
        logger.info("Shutdown de agentes concluído")

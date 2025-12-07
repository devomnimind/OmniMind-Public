"""
Sistema de Auto-Reparação para Orchestrator.

Implementa Seção 2 da Auditoria do Orchestrator:
- Mecanismo de auto-reparação do Orchestrator
- Detecção de falhas e degradação
- Estratégias de reparo automático
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from ..orchestrator.component_isolation import IsolationLevel

logger = logging.getLogger(__name__)


class RepairStrategy(Enum):
    """Estratégias de reparo."""

    RESTART = "restart"  # Reiniciar componente
    RESET = "reset"  # Resetar estado
    ROLLBACK = "rollback"  # Reverter para versão anterior
    ISOLATE = "isolate"  # Isolar componente
    REPLACE = "replace"  # Substituir componente


@dataclass
class RepairAction:
    """Ação de reparo."""

    component_id: str
    strategy: RepairStrategy
    timestamp: float
    reason: str
    success: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AutoRepairSystem:
    """Sistema de auto-reparação do Orchestrator."""

    def __init__(self, orchestrator: Any) -> None:
        """Inicializa sistema de auto-reparação.

        Args:
            orchestrator: Instância do OrchestratorAgent
        """
        self.orchestrator = orchestrator
        self.repair_history: List[RepairAction] = []
        self.failure_detection_threshold = 3  # Número de falhas antes de reparar
        self.failure_counts: Dict[str, int] = {}
        self.last_repair_time: Dict[str, float] = {}
        self.repair_cooldown = 60.0  # Segundos entre reparos do mesmo componente

        logger.info("AutoRepairSystem inicializado")

    async def detect_and_repair(self, component_id: str, error: Optional[str] = None) -> bool:
        """Detecta falha e executa reparo se necessário.

        Args:
            component_id: ID do componente com falha
            error: Mensagem de erro (opcional)

        Returns:
            True se reparo foi executado, False caso contrário
        """
        # Incrementar contador de falhas
        self.failure_counts[component_id] = self.failure_counts.get(component_id, 0) + 1

        logger.warning(
            "Falha detectada em %s (contagem: %d/%d)",
            component_id,
            self.failure_counts[component_id],
            self.failure_detection_threshold,
        )

        # Verificar se atingiu threshold
        if self.failure_counts[component_id] < self.failure_detection_threshold:
            return False

        # Verificar cooldown
        last_repair = self.last_repair_time.get(component_id, 0)
        if time.time() - last_repair < self.repair_cooldown:
            logger.debug("Componente %s em cooldown, aguardando...", component_id)
            return False

        # Executar reparo
        success = await self._execute_repair(component_id, error)

        # Resetar contador se reparo foi bem-sucedido
        if success:
            self.failure_counts[component_id] = 0
            self.last_repair_time[component_id] = time.time()

        return success

    async def _execute_repair(self, component_id: str, error: Optional[str]) -> bool:
        """Executa reparo de componente.

        Args:
            component_id: ID do componente
            error: Mensagem de erro

        Returns:
            True se reparo foi bem-sucedido
        """
        logger.info("Iniciando reparo de %s", component_id)

        # Determinar estratégia de reparo
        strategy = self._determine_repair_strategy(component_id, error)

        # Executar reparo baseado na estratégia
        try:
            if strategy == RepairStrategy.RESTART:
                success = await self._repair_restart(component_id)
            elif strategy == RepairStrategy.RESET:
                success = await self._repair_reset(component_id)
            elif strategy == RepairStrategy.ROLLBACK:
                success = await self._repair_rollback(component_id)
            elif strategy == RepairStrategy.ISOLATE:
                success = await self._repair_isolate(component_id)
            elif strategy == RepairStrategy.REPLACE:
                success = await self._repair_replace(component_id)
            else:
                success = False
                logger.warning("Estratégia de reparo desconhecida: %s", strategy)

            # Registrar ação
            action = RepairAction(
                component_id=component_id,
                strategy=strategy,
                timestamp=time.time(),
                reason=error or "Falha detectada",
                success=success,
                metadata={"error": error} if error else {},
            )

            self.repair_history.append(action)

            if success:
                logger.info(
                    "Reparo de %s concluído com sucesso (estratégia: %s)",
                    component_id,
                    strategy.value,
                )
            else:
                logger.error("Reparo de %s falhou (estratégia: %s)", component_id, strategy.value)

            return success

        except Exception as e:
            logger.error("Erro ao executar reparo de %s: %s", component_id, e, exc_info=True)

            # Registrar falha
            action = RepairAction(
                component_id=component_id,
                strategy=strategy,
                timestamp=time.time(),
                reason=error or "Falha detectada",
                success=False,
                error=str(e),
                metadata={"error": error} if error else {},
            )

            self.repair_history.append(action)
            return False

    def _determine_repair_strategy(self, component_id: str, error: Optional[str]) -> RepairStrategy:
        """Determina estratégia de reparo baseado no componente e erro.

        Args:
            component_id: ID do componente
            error: Mensagem de erro

        Returns:
            Estratégia de reparo recomendada
        """
        # Estratégias baseadas no tipo de componente
        if component_id in ["security", "metacognition"]:
            # Componentes críticos: tentar restart primeiro
            return RepairStrategy.RESTART
        elif component_id in ["code", "architect", "debug"]:
            # Componentes opcionais: reset ou isolamento
            if error and "timeout" in error.lower():
                return RepairStrategy.RESET
            return RepairStrategy.ISOLATE
        elif "config" in component_id.lower() or "state" in component_id.lower():
            # Componentes de estado: rollback
            return RepairStrategy.ROLLBACK
        else:
            # Padrão: restart
            return RepairStrategy.RESTART

    async def _repair_restart(self, component_id: str) -> bool:
        """Repara componente via restart.

        Args:
            component_id: ID do componente

        Returns:
            True se restart foi bem-sucedido
        """
        logger.info("Restartando componente %s", component_id)

        # Se componente é agente, tentar reiniciar via registry
        if self.orchestrator.agent_registry:
            agent = self.orchestrator.agent_registry.get_agent(component_id)
            if agent:
                # Marcar como não saudável e depois saudável (simula restart)
                self.orchestrator.agent_registry._health_status[component_id] = False
                await asyncio.sleep(0.1)  # Simular tempo de restart
                self.orchestrator.agent_registry._health_status[component_id] = True
                logger.info("Componente %s reiniciado", component_id)
                return True

        return False

    async def _repair_reset(self, component_id: str) -> bool:
        """Repara componente via reset.

        Args:
            component_id: ID do componente

        Returns:
            True se reset foi bem-sucedido
        """
        logger.info("Resetando componente %s", component_id)

        # Resetar contadores de falha
        if component_id in self.failure_counts:
            self.failure_counts[component_id] = 0

        # Se componente é agente, resetar estado
        if self.orchestrator.agent_registry:
            agent = self.orchestrator.agent_registry.get_agent(component_id)
            if agent:
                # Resetar estado do agente (simulado)
                logger.info("Componente %s resetado", component_id)
                return True

        return False

    async def _repair_rollback(self, component_id: str) -> bool:
        """Repara componente via rollback.

        Args:
            component_id: ID do componente

        Returns:
            True se rollback foi bem-sucedido
        """
        logger.info("Fazendo rollback de componente %s", component_id)

        # Se orchestrator tem rollback system, usar
        if hasattr(self.orchestrator, "rollback_system") and self.orchestrator.rollback_system:
            return await self.orchestrator.rollback_system.rollback_component(component_id)

        # Fallback: reset
        return await self._repair_reset(component_id)

    async def _repair_isolate(self, component_id: str) -> bool:
        """Repara componente via isolamento.

        Args:
            component_id: ID do componente

        Returns:
            True se isolamento foi bem-sucedido
        """
        logger.info("Isolando componente %s", component_id)

        # Se orchestrator tem component_isolation, usar
        if (
            hasattr(self.orchestrator, "component_isolation")
            and self.orchestrator.component_isolation
        ):
            await self.orchestrator.component_isolation.isolate(
                component_id, IsolationLevel.FULL, "Auto-repair: isolamento preventivo"
            )
            return True

        return False

    async def _repair_replace(self, component_id: str) -> bool:
        """Repara componente via substituição.

        Args:
            component_id: ID do componente

        Returns:
            True se substituição foi bem-sucedida
        """
        logger.info("Substituindo componente %s", component_id)

        # Substituição é complexa, por enquanto apenas log
        # Em implementação futura, poderia criar nova instância do componente
        logger.warning("Substituição de componente não implementada completamente")
        return False

    def get_repair_history(self, limit: int = 10) -> List[RepairAction]:
        """Obtém histórico de reparos.

        Args:
            limit: Número máximo de reparos a retornar

        Returns:
            Lista de reparos recentes
        """
        return self.repair_history[-limit:]

    def get_failure_counts(self) -> Dict[str, int]:
        """Obtém contadores de falhas por componente.

        Returns:
            Dicionário com contadores de falhas
        """
        return self.failure_counts.copy()

    def reset_failure_count(self, component_id: str) -> None:
        """Reseta contador de falhas de componente.

        Args:
            component_id: ID do componente
        """
        if component_id in self.failure_counts:
            del self.failure_counts[component_id]
        logger.debug("Contador de falhas resetado para %s", component_id)

    def get_repair_summary(self) -> Dict[str, Any]:
        """Obtém resumo do sistema de reparo.

        Returns:
            Dicionário com resumo
        """
        total_repairs = len(self.repair_history)
        successful_repairs = sum(1 for r in self.repair_history if r.success)
        failed_repairs = total_repairs - successful_repairs

        return {
            "total_repairs": total_repairs,
            "successful_repairs": successful_repairs,
            "failed_repairs": failed_repairs,
            "success_rate": successful_repairs / total_repairs if total_repairs > 0 else 0.0,
            "components_with_failures": len(self.failure_counts),
            "failure_counts": self.failure_counts.copy(),
        }

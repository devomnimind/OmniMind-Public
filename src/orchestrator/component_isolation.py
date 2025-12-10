"""
Sistema de Isolamento de Componentes Comprometidos.

Implementa Seção 6 da Auditoria do Orchestrator:
- Isolamento completo de componentes
- Bloqueio de comunicações
- Redução de permissões e recursos
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Set

logger = logging.getLogger(__name__)


class IsolationLevel(Enum):
    """Níveis de isolamento."""

    PARTIAL = "partial"  # Isolamento parcial (comunicação limitada)
    FULL = "full"  # Isolamento completo (sem comunicação)
    EMERGENCY = "emergency"  # Isolamento de emergência (máxima restrição)


@dataclass
class IsolationRecord:
    """Registro de componente isolado."""

    component_id: str
    isolation_level: IsolationLevel
    timestamp: float
    reason: str
    blocked_components: Set[str] = field(default_factory=set)
    reduced_permissions: List[str] = field(default_factory=list)
    resource_limits: Dict[str, Any] = field(default_factory=dict)


class ComponentIsolation:
    """Isola componentes comprometidos do sistema."""

    def __init__(self, orchestrator: Any) -> None:
        """Inicializa sistema de isolamento.

        Args:
            orchestrator: Instância do OrchestratorAgent
        """
        self.orchestrator = orchestrator
        self.isolated_components: Set[str] = set()
        self.isolation_records: Dict[str, IsolationRecord] = {}
        self.communication_blocks: Dict[str, Set[str]] = {}  # component_id -> blocked_components
        self.permission_blocks: Dict[str, Set[str]] = {}  # component_id -> blocked_permissions
        self.resource_limits: Dict[str, Dict[str, Any]] = {}  # component_id -> limits

        logger.info("ComponentIsolation inicializado")

    async def isolate(
        self,
        component_id: str,
        isolation_level: IsolationLevel = IsolationLevel.FULL,
        reason: str = "Security threat detected",
    ) -> None:
        """Isola componente do sistema.

        Args:
            component_id: ID do componente a isolar
            isolation_level: Nível de isolamento
            reason: Motivo do isolamento
        """
        if component_id in self.isolated_components:
            logger.warning("Componente %s já está isolado, atualizando isolamento", component_id)
            await self._update_isolation(component_id, isolation_level)
            return

        logger.critical(
            "🚨 ISOLANDO COMPONENTE: %s (nível: %s, motivo: %s)",
            component_id,
            isolation_level.value,
            reason,
        )

        # 1. Bloquear comunicações
        blocked = await self._block_all_communications(component_id, isolation_level)

        # 2. Reduzir permissões
        reduced_perms = await self._reduce_permissions(component_id, isolation_level)

        # 3. Limitar recursos
        limits = await self._limit_resources(component_id, isolation_level)

        # 4. Criar registro
        record = IsolationRecord(
            component_id=component_id,
            isolation_level=isolation_level,
            timestamp=time.time(),
            reason=reason,
            blocked_components=blocked,
            reduced_permissions=reduced_perms,
            resource_limits=limits,
        )
        self.isolation_records[component_id] = record
        self.isolated_components.add(component_id)

        # 5. Notificar
        await self._notify_isolation(component_id, isolation_level, reason)

        logger.info(
            "Componente %s isolado com sucesso (nível: %s)",
            component_id,
            isolation_level.value,
        )

    async def _block_all_communications(
        self, component_id: str, isolation_level: IsolationLevel
    ) -> Set[str]:
        """Bloqueia todas as comunicações do componente.

        Args:
            component_id: ID do componente
            isolation_level: Nível de isolamento

        Returns:
            Set de componentes bloqueados
        """
        blocked = set()

        if isolation_level == IsolationLevel.FULL or isolation_level == IsolationLevel.EMERGENCY:
            # Bloquear comunicação com todos os componentes
            if self.orchestrator.agent_registry:
                all_agents = self.orchestrator.agent_registry.list_agents()
                for agent_name in all_agents:
                    if agent_name != component_id:
                        blocked.add(agent_name)

        elif isolation_level == IsolationLevel.PARTIAL:
            # Bloquear apenas componentes críticos
            if self.orchestrator.agent_registry:
                critical_agents = [
                    name
                    for name in self.orchestrator.agent_registry.list_agents()
                    if name in ["security", "metacognition"]
                ]
                blocked.update(critical_agents)

        self.communication_blocks[component_id] = blocked

        logger.info(
            "Comunicações bloqueadas para componente %s (bloqueados: %d componentes)",
            component_id,
            len(blocked),
        )

        return blocked

    async def _reduce_permissions(
        self, component_id: str, isolation_level: IsolationLevel
    ) -> List[str]:
        """Reduz permissões do componente.

        Args:
            component_id: ID do componente
            isolation_level: Nível de isolamento

        Returns:
            Lista de permissões reduzidas
        """
        blocked_perms = []

        if isolation_level == IsolationLevel.EMERGENCY:
            # Bloquear todas as permissões exceto leitura
            blocked_perms = [
                "delegate_task",
                "modify_code",
                "restart_service",
                "block_port",
                "isolate_component",
            ]
        elif isolation_level == IsolationLevel.FULL:
            # Bloquear permissões críticas
            blocked_perms = ["modify_code", "restart_service", "isolate_component"]
        elif isolation_level == IsolationLevel.PARTIAL:
            # Bloquear apenas modificações
            blocked_perms = ["modify_code"]

        self.permission_blocks[component_id] = set(blocked_perms)

        logger.info(
            "Permissões reduzidas para componente %s (%d permissões bloqueadas)",
            component_id,
            len(blocked_perms),
        )

        return blocked_perms

    async def _limit_resources(
        self, component_id: str, isolation_level: IsolationLevel
    ) -> Dict[str, Any]:
        """Limita recursos do componente.

        Args:
            component_id: ID do componente
            isolation_level: Nível de isolamento

        Returns:
            Dicionário com limites de recursos
        """
        limits = {}

        if isolation_level == IsolationLevel.EMERGENCY:
            limits = {
                "cpu_percent": 5.0,  # Máximo 5% CPU
                "memory_mb": 50,  # Máximo 50MB RAM
                "network_bandwidth_kbps": 10,  # Máximo 10 Kbps
            }
        elif isolation_level == IsolationLevel.FULL:
            limits = {
                "cpu_percent": 10.0,
                "memory_mb": 100,
                "network_bandwidth_kbps": 50,
            }
        elif isolation_level == IsolationLevel.PARTIAL:
            limits = {
                "cpu_percent": 20.0,
                "memory_mb": 200,
                "network_bandwidth_kbps": 100,
            }

        self.resource_limits[component_id] = limits

        logger.info(
            "Recursos limitados para componente %s (nível: %s)",
            component_id,
            isolation_level.value,
        )

        return limits

    async def _update_isolation(self, component_id: str, new_level: IsolationLevel) -> None:
        """Atualiza nível de isolamento.

        Args:
            component_id: ID do componente
            new_level: Novo nível de isolamento
        """
        record = self.isolation_records.get(component_id)
        if record:
            record.isolation_level = new_level
            await self._block_all_communications(component_id, new_level)
            await self._reduce_permissions(component_id, new_level)
            await self._limit_resources(component_id, new_level)

    async def _notify_isolation(
        self, component_id: str, isolation_level: IsolationLevel, reason: str
    ) -> None:
        """Notifica isolamento.

        Args:
            component_id: ID do componente
            isolation_level: Nível de isolamento
            reason: Motivo do isolamento
        """
        if hasattr(self.orchestrator, "event_bus"):
            from .event_bus import EventPriority, OrchestratorEvent

            event = OrchestratorEvent(
                event_type="component_isolated",
                source="component_isolation",
                priority=EventPriority.CRITICAL,
                data={
                    "component_id": component_id,
                    "isolation_level": isolation_level.value,
                    "reason": reason,
                    "description": f"Componente {component_id} isolado: {reason}",
                },
                timestamp=time.time(),
            )
            # Event já contém priority no campo priority (EventPriority enum)
            await self.orchestrator.event_bus.publish(event)

    async def release(self, component_id: str) -> bool:
        """Libera componente do isolamento.

        Args:
            component_id: ID do componente

        Returns:
            True se liberado com sucesso, False caso contrário
        """
        if component_id not in self.isolated_components:
            logger.warning("Componente %s não está isolado", component_id)
            return False

        logger.info("Liberando componente %s do isolamento", component_id)

        # 1. Restaurar comunicações
        if component_id in self.communication_blocks:
            del self.communication_blocks[component_id]

        # 2. Restaurar permissões
        if component_id in self.permission_blocks:
            del self.permission_blocks[component_id]

        # 3. Restaurar recursos
        if component_id in self.resource_limits:
            del self.resource_limits[component_id]

        # 4. Remover do isolamento
        self.isolated_components.remove(component_id)
        if component_id in self.isolation_records:
            del self.isolation_records[component_id]

        # 5. Notificar
        await self._notify_release(component_id)

        logger.info("Componente %s liberado do isolamento com sucesso", component_id)
        return True

    async def _notify_release(self, component_id: str) -> None:
        """Notifica liberação do isolamento.

        Args:
            component_id: ID do componente
        """
        if hasattr(self.orchestrator, "event_bus"):
            from .event_bus import EventPriority, OrchestratorEvent

            event = OrchestratorEvent(
                event_type="component_released",
                source="component_isolation",
                priority=EventPriority.HIGH,
                data={
                    "component_id": component_id,
                    "description": f"Componente {component_id} liberado do isolamento",
                },
                timestamp=time.time(),
            )
            await self.orchestrator.event_bus.publish(event, priority="high")

    def is_isolated(self, component_id: str) -> bool:
        """Verifica se componente está isolado.

        Args:
            component_id: ID do componente

        Returns:
            True se isolado, False caso contrário
        """
        return component_id in self.isolated_components

    def can_communicate(self, from_component: str, to_component: str) -> bool:
        """Verifica se componente pode comunicar com outro.

        Args:
            from_component: Componente origem
            to_component: Componente destino

        Returns:
            True se pode comunicar, False caso contrário
        """
        # Se componente origem está isolado, verificar se destino está bloqueado
        if from_component in self.isolated_components:
            if from_component in self.communication_blocks:
                # Se destino está na lista de bloqueados, não pode comunicar
                blocked = self.communication_blocks[from_component]
                return to_component not in blocked
            # Se isolado mas sem registro de bloqueios, não pode comunicar
            return False
        return True

    def get_isolation_status(self) -> Dict[str, Any]:
        """Obtém status de todos os componentes isolados.

        Returns:
            Dicionário com status de isolamento
        """
        return {
            "isolated_count": len(self.isolated_components),
            "isolated_components": list(self.isolated_components),
            "records": {
                cid: {
                    "isolation_level": rec.isolation_level.value,
                    "reason": rec.reason,
                    "timestamp": rec.timestamp,
                }
                for cid, rec in self.isolation_records.items()
            },
        }

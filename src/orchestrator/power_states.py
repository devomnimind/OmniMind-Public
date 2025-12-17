"""
Sistema de Power States para Orchestrator.

Implementa Seção 4 da Auditoria do Orchestrator:
- Estados de energia (IDLE, STANDBY, ACTIVE, CRITICAL)
- Categorização de serviços (críticos, essenciais, opcionais)
- Transições suaves entre estados
- Otimização de recursos
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class PowerState(Enum):
    """Estados de energia do Orchestrator."""

    IDLE = "idle"  # Repouso total, apenas serviços básicos
    STANDBY = "standby"  # Preparado, serviços leves ativos
    ACTIVE = "active"  # Operação normal
    CRITICAL = "critical"  # Modo emergencial, todos os recursos


@dataclass
class ServiceCategory:
    """Categoria de serviço."""

    name: str
    services: List[str]
    keep_active_in_idle: bool = False  # Se mantém ativo em IDLE
    preheat_in_standby: bool = False  # Se faz preheating em STANDBY


class PowerStateManager:
    """Gerencia estados de energia do Orchestrator."""

    def __init__(self, orchestrator: Any) -> None:
        """Inicializa gerenciador de power states.

        Args:
            orchestrator: Instância do OrchestratorAgent
        """
        self.orchestrator = orchestrator
        self.current_state = PowerState.ACTIVE
        self.previous_state: Optional[PowerState] = None
        self.state_history: List[Dict[str, Any]] = []

        # Categorização de serviços
        self.service_categories = {
            "critical": ServiceCategory(
                name="critical",
                services=["security", "metacognition"],
                keep_active_in_idle=True,
                preheat_in_standby=True,
            ),
            "essential": ServiceCategory(
                name="essential",
                services=["orchestrator"],
                keep_active_in_idle=True,
                preheat_in_standby=True,
            ),
            "optional": ServiceCategory(
                name="optional",
                services=["code", "architect", "debug", "reviewer", "psychoanalyst"],
                keep_active_in_idle=False,
                preheat_in_standby=True,
            ),
        }

        # Rastreamento de serviços ativos por estado
        self.active_services: Dict[PowerState, Set[str]] = {
            PowerState.IDLE: set(),
            PowerState.STANDBY: set(),
            PowerState.ACTIVE: set(),
            PowerState.CRITICAL: set(),
        }

        # Serviços em preheating
        self.preheating_services: Set[str] = set()

        logger.info(
            "PowerStateManager inicializado (estado inicial: %s)",
            self.current_state.value,
        )

    async def transition_to(self, new_state: PowerState, reason: str = "") -> None:
        """Transição suave entre estados.

        Args:
            new_state: Novo estado de energia
            reason: Motivo da transição
        """
        if new_state == self.current_state:
            logger.debug("Já está no estado %s", new_state.value)
            return

        logger.info(
            "Transição de energia: %s → %s (motivo: %s)",
            self.current_state.value,
            new_state.value,
            reason or "N/A",
        )

        self.previous_state = self.current_state

        # Executar transição específica
        if new_state == PowerState.IDLE:
            await self._transition_to_idle()
        elif new_state == PowerState.STANDBY:
            await self._transition_to_standby()
        elif new_state == PowerState.ACTIVE:
            await self._transition_to_active()
        elif new_state == PowerState.CRITICAL:
            await self._transition_to_critical()

        # Atualizar estado
        self.current_state = new_state

        # Registrar transição
        self._record_transition(new_state, reason)

        logger.info("Transição concluída: estado atual = %s", self.current_state.value)

    async def _transition_to_idle(self) -> None:
        """Transição para IDLE - apenas críticos."""
        logger.info("Transição para IDLE: desativando serviços opcionais")

        # Desativar serviços opcionais
        optional_services = self.service_categories["optional"].services
        for service_name in optional_services:
            await self._deactivate_service(service_name)

        # Manter apenas críticos e essenciais
        critical_services = self.service_categories["critical"].services
        essential_services = self.service_categories["essential"].services

        for service_name in critical_services + essential_services:
            await self._ensure_service_active(service_name)

        # Atualizar registro de serviços ativos
        self.active_services[PowerState.IDLE] = set(critical_services + essential_services)

        logger.info(
            "Estado IDLE: %d serviços ativos",
            len(self.active_services[PowerState.IDLE]),
        )

    async def _transition_to_standby(self) -> None:
        """Transição para STANDBY - preparado para ativação."""
        logger.info("Transição para STANDBY: preparando serviços")

        # Manter críticos e essenciais ativos
        critical_services = self.service_categories["critical"].services
        essential_services = self.service_categories["essential"].services

        for service_name in critical_services + essential_services:
            await self._ensure_service_active(service_name)

        # Preheating de serviços opcionais (mas não ativar ainda)
        optional_services = self.service_categories["optional"].services
        for service_name in optional_services:
            await self._preheat_service(service_name)

        # Atualizar registro
        self.active_services[PowerState.STANDBY] = set(critical_services + essential_services)

        logger.info(
            "Estado STANDBY: %d serviços ativos, %d em preheating",
            len(self.active_services[PowerState.STANDBY]),
            len(self.preheating_services),
        )

    async def _transition_to_active(self) -> None:
        """Transição para ACTIVE - operação normal."""
        logger.info("Transição para ACTIVE: ativando serviços essenciais")

        # Reativar serviços essenciais
        essential_services = self.service_categories["essential"].services
        for service_name in essential_services:
            await self._ensure_service_active(service_name)

        # Ativar serviços que estavam em preheating
        for service_name in list(self.preheating_services):
            await self._activate_service(service_name)
            self.preheating_services.discard(service_name)

        # Atualizar registro
        all_services = (
            self.service_categories["critical"].services
            + self.service_categories["essential"].services
            + self.service_categories["optional"].services
        )
        self.active_services[PowerState.ACTIVE] = set(all_services)

        logger.info(
            "Estado ACTIVE: %d serviços ativos",
            len(self.active_services[PowerState.ACTIVE]),
        )

    async def _transition_to_critical(self) -> None:
        """Transição para CRITICAL - modo emergencial."""
        logger.critical("Transição para CRITICAL: modo emergencial ativado")

        # Ativar TODOS os serviços
        all_services = []
        for category in self.service_categories.values():
            all_services.extend(category.services)

        for service_name in all_services:
            await self._ensure_service_active(service_name)

        # Atualizar registro
        self.active_services[PowerState.CRITICAL] = set(all_services)

        logger.critical(
            "Estado CRITICAL: %d serviços ativos (máximo)",
            len(self.active_services[PowerState.CRITICAL]),
        )

    async def _deactivate_service(self, service_name: str) -> None:
        """Desativa serviço.

        Args:
            service_name: Nome do serviço
        """
        if self.orchestrator.agent_registry:
            agent = self.orchestrator.agent_registry.get_agent(service_name)
            if agent:
                # Marcar como não saudável temporariamente
                self.orchestrator.agent_registry._health_status[service_name] = False
                logger.debug("Serviço %s desativado", service_name)

    async def _ensure_service_active(self, service_name: str) -> None:
        """Garante que serviço está ativo.

        Args:
            service_name: Nome do serviço
        """
        if self.orchestrator.agent_registry:
            # Verificar se agente existe
            agent = self.orchestrator.agent_registry.get_agent(service_name)
            if not agent:
                # Tentar criar agente se não existe
                logger.debug("Serviço %s não encontrado, tentando criar", service_name)
            else:
                # Marcar como saudável
                self.orchestrator.agent_registry._health_status[service_name] = True
                logger.debug("Serviço %s ativo", service_name)

    async def _activate_service(self, service_name: str) -> None:
        """Ativa serviço.

        Args:
            service_name: Nome do serviço
        """
        await self._ensure_service_active(service_name)
        self.preheating_services.discard(service_name)
        logger.debug("Serviço %s ativado", service_name)

    async def _preheat_service(self, service_name: str) -> None:
        """Prepara serviço para ativação (preheating).

        Args:
            service_name: Nome do serviço
        """
        if service_name not in self.preheating_services:
            self.preheating_services.add(service_name)
            logger.debug("Serviço %s em preheating", service_name)

    def _record_transition(self, new_state: PowerState, reason: str) -> None:
        """Registra transição de estado.

        Args:
            new_state: Novo estado
            reason: Motivo da transição
        """
        transition_record = {
            "timestamp": time.time(),
            "from_state": self.previous_state.value if self.previous_state else None,
            "to_state": new_state.value,
            "reason": reason,
            "active_services_count": len(self.active_services.get(new_state, set())),
        }

        self.state_history.append(transition_record)

        # Limitar histórico
        if len(self.state_history) > 100:
            self.state_history.pop(0)

    def get_current_state(self) -> PowerState:
        """Obtém estado atual.

        Returns:
            Estado atual de energia
        """
        return self.current_state

    def get_active_services(self) -> Set[str]:
        """Obtém serviços ativos no estado atual.

        Returns:
            Set de nomes de serviços ativos
        """
        return self.active_services.get(self.current_state, set())

    def get_state_summary(self) -> Dict[str, Any]:
        """Obtém resumo do estado atual.

        Returns:
            Dicionário com resumo do estado
        """
        return {
            "current_state": self.current_state.value,
            "previous_state": (self.previous_state.value if self.previous_state else None),
            "active_services": list(self.get_active_services()),
            "active_services_count": len(self.get_active_services()),
            "preheating_services": list(self.preheating_services),
            "preheating_count": len(self.preheating_services),
            "transitions_count": len(self.state_history),
        }

    def get_state_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém histórico de transições.

        Args:
            limit: Número máximo de transições a retornar

        Returns:
            Lista de transições recentes
        """
        return self.state_history[-limit:]

    def is_service_active(self, service_name: str) -> bool:
        """Verifica se serviço está ativo no estado atual.

        Args:
            service_name: Nome do serviço

        Returns:
            True se ativo, False caso contrário
        """
        return service_name in self.get_active_services()

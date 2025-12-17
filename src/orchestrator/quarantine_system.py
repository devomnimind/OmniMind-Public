"""
Sistema de Quarentena para Componentes Comprometidos.

Implementa Seção 6 da Auditoria do Orchestrator:
- Isolamento de componentes comprometidos
- Análise forense automática
- Liberação controlada após validação
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class QuarantineRecord:
    """Registro de componente em quarentena."""

    component_id: str
    reason: str
    timestamp: float
    evidence: Dict[str, Any] = field(default_factory=dict)
    forensic_report: Optional[Dict[str, Any]] = None
    safe_to_release: bool = False
    release_attempts: int = 0


class QuarantineSystem:
    """Sistema de quarentena para componentes comprometidos."""

    def __init__(self, orchestrator: Any) -> None:
        """Inicializa sistema de quarentena.

        Args:
            orchestrator: Instância do OrchestratorAgent
        """
        self.orchestrator = orchestrator
        self.quarantined_components: Set[str] = set()
        self.quarantine_records: Dict[str, QuarantineRecord] = {}
        self.communication_blocks: Dict[str, Set[str]] = {}  # component_id -> blocked_components
        self.capacity_reductions: Dict[str, float] = {}  # component_id -> reduction_factor

        logger.info("QuarantineSystem inicializado")

    async def quarantine(
        self,
        component_id: str,
        reason: str,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Coloca componente em quarentena.

        Args:
            component_id: ID do componente a colocar em quarentena
            reason: Motivo da quarentena
            evidence: Evidências da ameaça
        """
        if component_id in self.quarantined_components:
            logger.warning(
                "Componente %s já está em quarentena, atualizando registro",
                component_id,
            )
            record = self.quarantine_records[component_id]
            record.reason = reason
            if evidence:
                record.evidence.update(evidence)
            return

        logger.critical(
            "🚨 COLOCANDO COMPONENTE EM QUARANTENA: %s (motivo: %s)",
            component_id,
            reason,
        )

        # 1. Bloquear comunicação
        await self._block_communication(component_id)

        # 2. Reduzir capacidade
        await self._reduce_capacity(component_id, reduction_factor=0.1)

        # 3. Criar registro
        record = QuarantineRecord(
            component_id=component_id,
            reason=reason,
            timestamp=time.time(),
            evidence=evidence or {},
        )
        self.quarantine_records[component_id] = record
        self.quarantined_components.add(component_id)

        # 4. Notificar
        await self._notify_quarantine(component_id, reason, evidence)

        logger.info("Componente %s colocado em quarentena com sucesso", component_id)

    async def _block_communication(self, component_id: str) -> None:
        """Bloqueia comunicação com componente.

        Args:
            component_id: ID do componente
        """
        # Bloquear comunicação com todos os outros componentes
        blocked = set()
        if self.orchestrator.agent_registry:
            all_agents = self.orchestrator.agent_registry.list_agents()
            for agent_name in all_agents:
                if agent_name != component_id:
                    blocked.add(agent_name)

        self.communication_blocks[component_id] = blocked

        logger.info(
            "Comunicação bloqueada para componente %s (bloqueados: %d componentes)",
            component_id,
            len(blocked),
        )

    async def _reduce_capacity(self, component_id: str, reduction_factor: float = 0.1) -> None:
        """Reduz capacidade do componente.

        Args:
            component_id: ID do componente
            reduction_factor: Fator de redução (0.0 a 1.0)
        """
        self.capacity_reductions[component_id] = reduction_factor

        logger.info(
            "Capacidade reduzida para componente %s (fator: %.2f)",
            component_id,
            reduction_factor,
        )

    async def _notify_quarantine(
        self,
        component_id: str,
        reason: str,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Notifica quarentena.

        Args:
            component_id: ID do componente
            reason: Motivo da quarentena
            evidence: Evidências
        """
        # Publicar evento no EventBus se disponível
        if hasattr(self.orchestrator, "event_bus"):
            from .event_bus import EventPriority, OrchestratorEvent

            event = OrchestratorEvent(
                event_type="component_quarantined",
                source="quarantine_system",
                priority=EventPriority.CRITICAL,
                data={
                    "component_id": component_id,
                    "reason": reason,
                    "evidence": evidence or {},
                    "description": f"Componente {component_id} colocado em quarentena: {reason}",
                },
                timestamp=time.time(),
            )
            # Event já contém priority no campo priority (EventPriority enum)
            await self.orchestrator.event_bus.publish(event)

        # Log de auditoria
        if hasattr(self.orchestrator, "audit_system"):
            self.orchestrator.audit_system.log_action(
                "component_quarantined",
                {
                    "component_id": component_id,
                    "reason": reason,
                    "evidence": evidence or {},
                },
                category="security",
            )

    async def release(
        self, component_id: str, forensic_report: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Libera componente da quarentena após análise.

        Args:
            component_id: ID do componente
            forensic_report: Relatório forense (opcional)

        Returns:
            True se liberado com sucesso, False caso contrário
        """
        if component_id not in self.quarantined_components:
            logger.warning("Componente %s não está em quarentena", component_id)
            return False

        record = self.quarantine_records.get(component_id)
        if not record:
            logger.error("Registro de quarentena não encontrado para %s", component_id)
            return False

        # Atualizar relatório forense se fornecido
        if forensic_report:
            record.forensic_report = forensic_report
            record.safe_to_release = forensic_report.get("safe_to_release", False)

        # Verificar se é seguro liberar
        if not record.safe_to_release:
            record.release_attempts += 1
            logger.warning(
                "Tentativa de liberação %d para %s: não seguro para liberar",
                record.release_attempts,
                component_id,
            )
            return False

        logger.info("Liberando componente %s da quarentena", component_id)

        # 1. Restaurar comunicação
        await self._restore_communication(component_id)

        # 2. Restaurar capacidade
        await self._restore_capacity(component_id)

        # 3. Remover da quarentena
        self.quarantined_components.remove(component_id)
        del self.quarantine_records[component_id]

        # 4. Notificar
        await self._notify_release(component_id)

        logger.info("Componente %s liberado da quarentena com sucesso", component_id)
        return True

    async def _restore_communication(self, component_id: str) -> None:
        """Restaura comunicação do componente.

        Args:
            component_id: ID do componente
        """
        if component_id in self.communication_blocks:
            del self.communication_blocks[component_id]
            logger.info("Comunicação restaurada para componente %s", component_id)

    async def _restore_capacity(self, component_id: str) -> None:
        """Restaura capacidade do componente.

        Args:
            component_id: ID do componente
        """
        if component_id in self.capacity_reductions:
            del self.capacity_reductions[component_id]
            logger.info("Capacidade restaurada para componente %s", component_id)

    async def _notify_release(self, component_id: str) -> None:
        """Notifica liberação da quarentena.

        Args:
            component_id: ID do componente
        """
        if hasattr(self.orchestrator, "event_bus"):
            from .event_bus import EventPriority, OrchestratorEvent

            event = OrchestratorEvent(
                event_type="component_released",
                source="quarantine_system",
                priority=EventPriority.HIGH,
                data={
                    "component_id": component_id,
                    "description": f"Componente {component_id} liberado da quarentena",
                },
                timestamp=time.time(),
            )
            await self.orchestrator.event_bus.publish(event, priority="high")

    def is_quarantined(self, component_id: str) -> bool:
        """Verifica se componente está em quarentena.

        Args:
            component_id: ID do componente

        Returns:
            True se em quarentena, False caso contrário
        """
        return component_id in self.quarantined_components

    def get_quarantine_status(self) -> Dict[str, Any]:
        """Obtém status de todos os componentes em quarentena.

        Returns:
            Dicionário com status de quarentena
        """
        return {
            "quarantined_count": len(self.quarantined_components),
            "quarantined_components": list(self.quarantined_components),
            "records": {
                cid: {
                    "reason": rec.reason,
                    "timestamp": rec.timestamp,
                    "safe_to_release": rec.safe_to_release,
                    "release_attempts": rec.release_attempts,
                }
                for cid, rec in self.quarantine_records.items()
            },
        }

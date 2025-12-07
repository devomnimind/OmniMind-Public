"""
Matriz de Permissões Dinâmica para Orchestrator.

Implementa Seção 5 da Auditoria do Orchestrator:
- Controle granular de ações autônomas
- Modo emergencial com privilégios expandidos
- Sistema de permissões baseado em confiança
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Níveis de permissão."""

    AUTO = "auto"  # Execução automática
    APPROVAL_REQUIRED = "approval_required"  # Requer aprovação
    BLOCKED = "blocked"  # Bloqueado


@dataclass
class Permission:
    """Definição de permissão para uma ação."""

    level: PermissionLevel
    requires_approval: bool
    emergency_override: bool
    min_trust_level: float = 0.5  # Nível mínimo de confiança para execução automática
    description: str = ""


class PermissionMatrix:
    """Matriz de permissões dinâmica para controle de ações autônomas."""

    # Permissões normais (modo operacional padrão)
    PERMISSIONS: Dict[str, Permission] = {
        "delegate_task": Permission(
            level=PermissionLevel.AUTO,
            requires_approval=False,
            emergency_override=True,
            min_trust_level=0.3,
            description="Delegar tarefa para agente especializado",
        ),
        "modify_code": Permission(
            level=PermissionLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            emergency_override=False,
            min_trust_level=0.8,
            description="Modificar código do sistema",
        ),
        "block_port": Permission(
            level=PermissionLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            emergency_override=True,
            min_trust_level=0.6,
            description="Bloquear porta de rede",
        ),
        "isolate_component": Permission(
            level=PermissionLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            emergency_override=True,
            min_trust_level=0.7,
            description="Isolar componente do sistema",
        ),
        "restart_service": Permission(
            level=PermissionLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            emergency_override=False,
            min_trust_level=0.8,
            description="Reiniciar serviço do sistema",
        ),
        "modify_config": Permission(
            level=PermissionLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            emergency_override=False,
            min_trust_level=0.9,
            description="Modificar configuração do sistema",
        ),
        "quarantine_component": Permission(
            level=PermissionLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            emergency_override=True,
            min_trust_level=0.7,
            description="Colocar componente em quarentena",
        ),
        "release_quarantine": Permission(
            level=PermissionLevel.APPROVAL_REQUIRED,
            requires_approval=True,
            emergency_override=False,
            min_trust_level=0.8,
            description="Liberar componente da quarentena",
        ),
    }

    # Permissões de emergência (modo crítico)
    EMERGENCY_PERMISSIONS: Dict[str, PermissionLevel] = {
        "block_port": PermissionLevel.AUTO,
        "isolate_component": PermissionLevel.AUTO,
        "quarantine_component": PermissionLevel.AUTO,
        "escalate_to_human": PermissionLevel.AUTO,
    }

    def __init__(self) -> None:
        """Inicializa matriz de permissões."""
        self.custom_permissions: Dict[str, Permission] = {}
        logger.info("PermissionMatrix inicializado")

    def can_execute(
        self,
        action: str,
        emergency: bool = False,
        trust_level: float = 0.5,
    ) -> Tuple[bool, str]:
        """Verifica se ação pode ser executada.

        Args:
            action: Nome da ação a verificar
            emergency: Se está em modo emergencial
            trust_level: Nível de confiança atual (0.0 a 1.0)

        Returns:
            Tupla (pode_executar, motivo)
        """
        # Verificar permissões de emergência primeiro
        if emergency and action in self.EMERGENCY_PERMISSIONS:
            emergency_level = self.EMERGENCY_PERMISSIONS[action]
            if emergency_level == PermissionLevel.AUTO:
                return True, "emergency_override"

        # Verificar se ação está definida
        permission = self.custom_permissions.get(action) or self.PERMISSIONS.get(action)
        if not permission:
            return False, "action_not_defined"

        # Verificar se está bloqueada
        if permission.level == PermissionLevel.BLOCKED:
            return False, "blocked"

        # Verificar se é automática
        if permission.level == PermissionLevel.AUTO:
            # Verificar nível mínimo de confiança
            if trust_level >= permission.min_trust_level:
                return True, "auto_permitted"
            return False, "insufficient_trust"

        # Verificar se requer aprovação
        if permission.level == PermissionLevel.APPROVAL_REQUIRED:
            # Em emergência, verificar se tem override
            if emergency and permission.emergency_override:
                return True, "emergency_override"
            # Verificar se confiança é suficiente para auto-aprovação
            if trust_level >= permission.min_trust_level:
                return True, "high_trust"
            return False, "approval_required"

        return False, "unknown"

    def add_custom_permission(
        self,
        action: str,
        permission: Permission,
    ) -> None:
        """Adiciona permissão customizada.

        Args:
            action: Nome da ação
            permission: Definição de permissão
        """
        self.custom_permissions[action] = permission
        logger.info("Permissão customizada adicionada: %s", action)

    def update_permission(
        self,
        action: str,
        level: Optional[PermissionLevel] = None,
        requires_approval: Optional[bool] = None,
        emergency_override: Optional[bool] = None,
        min_trust_level: Optional[float] = None,
    ) -> bool:
        """Atualiza permissão existente.

        Args:
            action: Nome da ação
            level: Novo nível de permissão
            requires_approval: Se requer aprovação
            emergency_override: Se tem override de emergência
            min_trust_level: Novo nível mínimo de confiança

        Returns:
            True se atualizado, False se ação não existe
        """
        # Se não existe em custom, criar cópia
        if action not in self.custom_permissions:
            original = self.PERMISSIONS.get(action)
            if not original:
                return False
            # Criar cópia para custom_permissions
            self.custom_permissions[action] = Permission(
                level=original.level,
                requires_approval=original.requires_approval,
                emergency_override=original.emergency_override,
                min_trust_level=original.min_trust_level,
                description=original.description,
            )

        permission = self.custom_permissions[action]

        if level is not None:
            permission.level = level
        if requires_approval is not None:
            permission.requires_approval = requires_approval
        if emergency_override is not None:
            permission.emergency_override = emergency_override
        if min_trust_level is not None:
            permission.min_trust_level = min_trust_level

        logger.info("Permissão atualizada: %s", action)
        return True

    def get_permission(self, action: str) -> Optional[Permission]:
        """Obtém permissão de uma ação.

        Args:
            action: Nome da ação

        Returns:
            Permissão ou None se não encontrada
        """
        return self.custom_permissions.get(action) or self.PERMISSIONS.get(action)

    def list_permissions(self) -> Dict[str, Permission]:
        """Lista todas as permissões.

        Returns:
            Dicionário com todas as permissões
        """
        all_permissions = self.PERMISSIONS.copy()
        all_permissions.update(self.custom_permissions)
        return all_permissions

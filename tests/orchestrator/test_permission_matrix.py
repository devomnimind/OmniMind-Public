"""
Testes para PermissionMatrix.

Testa matriz de permissões dinâmica.
"""

import pytest

from src.orchestrator.permission_matrix import Permission, PermissionLevel, PermissionMatrix


@pytest.fixture
def permission_matrix():
    """Cria instância de PermissionMatrix."""
    return PermissionMatrix()


def test_can_execute_auto_permission(permission_matrix):
    """Testa permissão automática."""
    can_execute, reason = permission_matrix.can_execute(
        "delegate_task", emergency=False, trust_level=0.5
    )

    assert can_execute is True
    assert reason == "auto_permitted"


def test_can_execute_approval_required(permission_matrix):
    """Testa permissão que requer aprovação."""
    can_execute, reason = permission_matrix.can_execute(
        "modify_code", emergency=False, trust_level=0.5
    )

    assert can_execute is False
    assert reason == "approval_required"


def test_can_execute_high_trust(permission_matrix):
    """Testa permissão com alta confiança."""
    can_execute, reason = permission_matrix.can_execute(
        "modify_code", emergency=False, trust_level=0.9
    )

    assert can_execute is True
    assert reason == "high_trust"


def test_can_execute_emergency_override(permission_matrix):
    """Testa override de emergência."""
    can_execute, reason = permission_matrix.can_execute(
        "block_port", emergency=True, trust_level=0.3
    )

    assert can_execute is True
    assert reason == "emergency_override"


def test_can_execute_unknown_action(permission_matrix):
    """Testa ação desconhecida."""
    can_execute, reason = permission_matrix.can_execute(
        "unknown_action", emergency=False, trust_level=0.5
    )

    assert can_execute is False
    assert reason == "action_not_defined"


def test_add_custom_permission(permission_matrix):
    """Testa adição de permissão customizada."""
    custom_perm = Permission(
        level=PermissionLevel.AUTO,
        requires_approval=False,
        emergency_override=True,
        description="Custom action",
    )
    permission_matrix.add_custom_permission("custom_action", custom_perm)

    can_execute, reason = permission_matrix.can_execute(
        "custom_action", emergency=False, trust_level=0.5
    )
    assert can_execute is True


def test_update_permission(permission_matrix):
    """Testa atualização de permissão."""
    result = permission_matrix.update_permission(
        "delegate_task", level=PermissionLevel.APPROVAL_REQUIRED, min_trust_level=0.9
    )

    assert result is True
    # Verificar que foi criada em custom_permissions
    assert "delegate_task" in permission_matrix.custom_permissions
    # Com confiança 0.5 e min_trust_level 0.9, não deve executar
    can_execute, reason = permission_matrix.can_execute(
        "delegate_task", emergency=False, trust_level=0.5
    )
    assert can_execute is False
    assert reason == "approval_required"


def test_update_permission_not_found(permission_matrix):
    """Testa atualização de permissão inexistente."""
    result = permission_matrix.update_permission("unknown_action", level=PermissionLevel.AUTO)

    assert result is False


def test_get_permission(permission_matrix):
    """Testa obtenção de permissão."""
    perm = permission_matrix.get_permission("delegate_task")

    assert perm is not None
    # Verificar que retorna a permissão padrão (não customizada)
    assert perm.level == PermissionLevel.AUTO


def test_get_permission_not_found(permission_matrix):
    """Testa obtenção de permissão inexistente."""
    perm = permission_matrix.get_permission("unknown_action")

    assert perm is None


def test_list_permissions(permission_matrix):
    """Testa listagem de permissões."""
    permissions = permission_matrix.list_permissions()

    assert len(permissions) > 0
    assert "delegate_task" in permissions
    assert "modify_code" in permissions


def test_insufficient_trust(permission_matrix):
    """Testa permissão com confiança insuficiente."""
    # delegate_task tem min_trust_level=0.3, então com 0.1 deve falhar
    can_execute, reason = permission_matrix.can_execute(
        "delegate_task", emergency=False, trust_level=0.1
    )

    # Com confiança 0.1 < 0.3 (min_trust_level), não deve executar
    assert can_execute is False
    assert reason == "insufficient_trust"

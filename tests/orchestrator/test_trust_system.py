"""
Testes para TrustSystem.

Testa sistema de confiança crescente.
"""

import pytest

from src.orchestrator.trust_system import TrustSystem


@pytest.fixture
def trust_system():
    """Cria instância de TrustSystem."""
    return TrustSystem(initial_trust=0.5)


def test_record_decision_success(trust_system):
    """Testa registro de decisão bem-sucedida."""
    trust_system.record_decision("test_action", True, {"context": "test"})

    assert trust_system.get_trust_level("test_action") > 0.5
    assert trust_system.success_count["test_action"] == 1
    assert trust_system.failure_count.get("test_action", 0) == 0


def test_record_decision_failure(trust_system):
    """Testa registro de decisão falhada."""
    trust_system.record_decision("test_action", False, {"context": "test"})

    assert trust_system.get_trust_level("test_action") < 0.5
    assert trust_system.failure_count["test_action"] == 1
    assert trust_system.success_count.get("test_action", 0) == 0


def test_get_trust_level_initial(trust_system):
    """Testa obtenção de nível de confiança inicial."""
    trust = trust_system.get_trust_level("new_action")

    assert trust == 0.5  # Initial trust


def test_get_trust_level_after_decisions(trust_system):
    """Testa nível de confiança após múltiplas decisões."""
    # 3 sucessos, 1 falha
    trust_system.record_decision("test_action", True, {})
    trust_system.record_decision("test_action", True, {})
    trust_system.record_decision("test_action", True, {})
    trust_system.record_decision("test_action", False, {})

    trust = trust_system.get_trust_level("test_action")
    assert trust == 0.75  # 3/4 = 0.75


def test_get_global_trust_level(trust_system):
    """Testa nível de confiança global."""
    trust_system.record_decision("action1", True, {})
    trust_system.record_decision("action2", True, {})

    global_trust = trust_system.get_global_trust_level()
    assert global_trust > 0.5


def test_get_action_statistics(trust_system):
    """Testa obtenção de estatísticas de ação."""
    trust_system.record_decision("test_action", True, {})
    trust_system.record_decision("test_action", True, {})
    trust_system.record_decision("test_action", False, {})

    stats = trust_system.get_action_statistics("test_action")

    assert stats["total_decisions"] == 3
    assert stats["success_count"] == 2
    assert stats["failure_count"] == 1
    assert stats["success_rate"] == 2 / 3


def test_get_recent_decisions(trust_system):
    """Testa obtenção de decisões recentes."""
    for i in range(5):
        trust_system.record_decision(f"action_{i}", True, {})

    recent = trust_system.get_recent_decisions(limit=3)

    assert len(recent) == 3
    assert recent[-1].action == "action_4"


def test_get_decisions_by_action(trust_system):
    """Testa obtenção de decisões por ação."""
    trust_system.record_decision("action1", True, {})
    trust_system.record_decision("action2", True, {})
    trust_system.record_decision("action1", False, {})

    decisions = trust_system.get_decisions_by_action("action1")

    assert len(decisions) == 2
    assert all(d.action == "action1" for d in decisions)


def test_reset_trust_action(trust_system):
    """Testa reset de confiança de uma ação."""
    trust_system.record_decision("test_action", True, {})
    trust_system.reset_trust("test_action")

    trust = trust_system.get_trust_level("test_action")
    assert trust == 0.5  # Volta ao inicial


def test_reset_trust_all(trust_system):
    """Testa reset de todas as confianças."""
    trust_system.record_decision("action1", True, {})
    trust_system.record_decision("action2", True, {})
    trust_system.reset_trust()

    assert len(trust_system.trust_scores) == 0


def test_get_summary(trust_system):
    """Testa obtenção de resumo."""
    trust_system.record_decision("action1", True, {})
    trust_system.record_decision("action2", True, {})

    summary = trust_system.get_summary()

    assert "global_trust_level" in summary
    assert "total_actions_tracked" in summary
    assert "total_decisions" in summary
    assert "actions" in summary

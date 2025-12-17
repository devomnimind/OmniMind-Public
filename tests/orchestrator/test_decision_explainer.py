"""
Testes para DecisionExplainer.

Testa sistema de explicabilidade de decisões.
"""

import pytest

from src.orchestrator.decision_explainer import DecisionExplainer


@pytest.fixture
def decision_explainer():
    """Cria instância de DecisionExplainer."""
    return DecisionExplainer()


def test_explain_decision_approved(decision_explainer):
    """Testa explicação de decisão aprovada."""
    explanation = decision_explainer.explain_decision(
        "test_action",
        {"context": "test"},
        (True, "auto_permitted"),
        0.8,
    )

    assert explanation.action == "test_action"
    assert explanation.permission_result["can_execute"] is True
    assert explanation.trust_level == 0.8
    assert len(explanation.explanation_text) > 0


def test_explain_decision_denied(decision_explainer):
    """Testa explicação de decisão negada."""
    explanation = decision_explainer.explain_decision(
        "test_action",
        {"context": "test"},
        (False, "approval_required"),
        0.3,
    )

    assert explanation.permission_result["can_execute"] is False
    assert (
        "NEGADA" in explanation.explanation_text or "negada" in explanation.explanation_text.lower()
    )


def test_explain_decision_alternatives(decision_explainer):
    """Testa geração de alternativas."""
    explanation = decision_explainer.explain_decision(
        "block_port",
        {"port": 4444},
        (True, "auto_permitted"),
        0.7,
    )

    assert len(explanation.alternatives_considered) > 0


def test_explain_decision_impact(decision_explainer):
    """Testa estimativa de impacto."""
    explanation = decision_explainer.explain_decision(
        "isolate_component",
        {"component_id": "test_component"},
        (True, "auto_permitted"),
        0.7,
    )

    assert "severity" in explanation.expected_impact
    assert "scope" in explanation.expected_impact


def test_explain_decision_risk(decision_explainer):
    """Testa avaliação de risco."""
    explanation = decision_explainer.explain_decision(
        "modify_code",
        {"file": "test.py"},
        (True, "high_trust"),
        0.9,
    )

    assert "level" in explanation.risk_assessment
    assert "factors" in explanation.risk_assessment


def test_record_execution_result(decision_explainer):
    """Testa registro de resultado de execução."""
    explanation = decision_explainer.explain_decision(
        "test_action",
        {},
        (True, "auto_permitted"),
        0.7,
    )

    result = {"success": True, "output": "test"}
    decision_explainer.record_execution_result(explanation, result)

    assert explanation.execution_result == result


def test_get_explanation_history(decision_explainer):
    """Testa obtenção de histórico de explicações."""
    for i in range(5):
        decision_explainer.explain_decision(
            f"action_{i}",
            {},
            (True, "auto_permitted"),
            0.7,
        )

    history = decision_explainer.get_explanation_history(limit=3)

    assert len(history) == 3
    assert history[-1].action == "action_4"


def test_get_explanations_by_action(decision_explainer):
    """Testa obtenção de explicações por ação."""
    decision_explainer.explain_decision("action1", {}, (True, "auto"), 0.7)
    decision_explainer.explain_decision("action2", {}, (True, "auto"), 0.7)
    decision_explainer.explain_decision("action1", {}, (False, "denied"), 0.3)

    explanations = decision_explainer.get_explanations_by_action("action1")

    assert len(explanations) == 2
    assert all(e.action == "action1" for e in explanations)


def test_get_explanation_summary(decision_explainer):
    """Testa obtenção de resumo."""
    decision_explainer.explain_decision("action1", {}, (True, "auto"), 0.7)
    decision_explainer.explain_decision("action2", {}, (False, "denied"), 0.3)

    summary = decision_explainer.get_explanation_summary()

    assert summary["total_explanations"] == 2
    assert summary["approved_decisions"] == 1
    assert summary["denied_decisions"] == 1
    assert summary["approval_rate"] == 0.5

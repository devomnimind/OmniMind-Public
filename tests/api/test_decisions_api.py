"""
Testes para API de Explicabilidade.

Testa endpoints REST para consultar decisões do Orchestrator.
"""

import pytest
from fastapi.testclient import TestClient

from web.backend.api.decisions import register_decision, router
from web.backend.main import app

# Registrar router no app de teste
app.include_router(router)

client = TestClient(app)


@pytest.fixture
def sample_decision():
    """Cria uma decisão de exemplo."""
    return {
        "action": "block_port",
        "timestamp": 1700000000.0,
        "context": {"port": 4444, "ip": "192.168.1.100"},
        "permission_result": {"can_execute": True, "reason": "emergency_override"},
        "trust_level": 0.75,
        "alternatives_considered": ["Notificar humano", "Isolar componente"],
        "expected_impact": {"severity": "medium", "scope": "network"},
        "risk_assessment": {"level": "medium", "factors": []},
        "decision_rationale": "Porta bloqueada devido a ameaça detectada",
        "success": True,
    }


def test_register_decision(sample_decision):
    """Testa registro de decisão."""
    register_decision(sample_decision, success=True)
    # Verificar que foi registrada (via list endpoint)
    response = client.get("/api/decisions/")
    assert response.status_code == 200
    decisions = response.json()
    assert len(decisions) > 0
    assert any(d["action"] == "block_port" for d in decisions)


def test_list_decisions_empty():
    """Testa listagem quando não há decisões."""
    # Limpar decisões
    client.delete("/api/decisions/")
    response = client.get("/api/decisions/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_decisions_with_filters(sample_decision):
    """Testa listagem com filtros."""
    register_decision(sample_decision, success=True)

    # Filtrar por ação
    response = client.get("/api/decisions/?action=block_port")
    assert response.status_code == 200
    decisions = response.json()
    assert all(d["action"] == "block_port" for d in decisions)

    # Filtrar por sucesso
    response = client.get("/api/decisions/?success=true")
    assert response.status_code == 200
    decisions = response.json()
    assert all(d.get("success") is True for d in decisions)

    # Filtrar por nível de confiança
    response = client.get("/api/decisions/?min_trust_level=0.7")
    assert response.status_code == 200
    decisions = response.json()
    assert all(d["trust_level"] >= 0.7 for d in decisions)


def test_get_decision_detail(sample_decision):
    """Testa obtenção de detalhes de decisão."""
    register_decision(sample_decision, success=True)

    # Obter primeira decisão (índice 0 = mais recente)
    response = client.get("/api/decisions/0")
    assert response.status_code == 200
    decision = response.json()
    assert decision["action"] == "block_port"
    assert "context" in decision
    assert "decision_rationale" in decision
    assert decision["success"] is True


def test_get_decision_not_found():
    """Testa obtenção de decisão inexistente."""
    # Limpar decisões
    client.delete("/api/decisions/")
    response = client.get("/api/decisions/0")
    assert response.status_code == 404


def test_get_decision_stats(sample_decision):
    """Testa obtenção de estatísticas."""
    # Limpar e adicionar algumas decisões
    client.delete("/api/decisions/")
    register_decision(sample_decision, success=True)

    # Adicionar outra decisão falha
    failed_decision = sample_decision.copy()
    failed_decision["action"] = "modify_code"
    failed_decision["success"] = False
    register_decision(failed_decision, success=False)

    response = client.get("/api/decisions/stats/summary")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_decisions"] == 2
    assert stats["successful_decisions"] == 1
    assert stats["failed_decisions"] == 1
    assert stats["success_rate"] == 0.5
    assert "decisions_by_action" in stats
    assert "decisions_by_reason" in stats


def test_export_decisions_json(sample_decision):
    """Testa exportação em JSON."""
    register_decision(sample_decision, success=True)

    response = client.get("/api/decisions/export/json")
    assert response.status_code == 200
    export = response.json()
    assert "export_timestamp" in export
    assert "total_decisions" in export
    assert "filters" in export
    assert "decisions" in export
    assert len(export["decisions"]) > 0


def test_clear_decisions(sample_decision):
    """Testa limpeza de decisões."""
    register_decision(sample_decision, success=True)

    # Verificar que há decisões
    response = client.get("/api/decisions/")
    assert len(response.json()) > 0

    # Limpar
    response = client.delete("/api/decisions/")
    assert response.status_code == 200
    assert "removidas" in response.json()["message"]

    # Verificar que está vazio
    response = client.get("/api/decisions/")
    assert response.json() == []


def test_list_decisions_limit(sample_decision):
    """Testa limite de resultados."""
    # Adicionar múltiplas decisões
    for i in range(5):
        decision = sample_decision.copy()
        decision["timestamp"] = 1700000000.0 + i
        register_decision(decision, success=True)

    # Limitar a 3 resultados
    response = client.get("/api/decisions/?limit=3")
    assert response.status_code == 200
    decisions = response.json()
    assert len(decisions) == 3


def test_list_decisions_date_filter(sample_decision):
    """Testa filtro por data."""
    decision1 = sample_decision.copy()
    decision1["timestamp"] = 1700000000.0
    register_decision(decision1, success=True)

    decision2 = sample_decision.copy()
    decision2["timestamp"] = 1700000100.0  # 100 segundos depois
    register_decision(decision2, success=True)

    # Filtrar por data inicial
    response = client.get("/api/decisions/?start_date=1700000050.0")
    assert response.status_code == 200
    decisions = response.json()
    # Deve retornar apenas a segunda decisão
    assert len(decisions) >= 1
    assert all(d["timestamp"] >= 1700000050.0 for d in decisions)

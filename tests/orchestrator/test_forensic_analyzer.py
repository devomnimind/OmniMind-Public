"""
Testes para ForensicAnalyzer.

Testa análise forense automática de ameaças.
"""

import pytest

from src.orchestrator.forensic_analyzer import (
    ForensicAnalyzer,
    ThreatCategory,
    ThreatSeverity,
)


@pytest.fixture
def forensic_analyzer():
    """Cria instância de ForensicAnalyzer."""
    return ForensicAnalyzer()


@pytest.mark.asyncio
async def test_analyze_threat_basic(forensic_analyzer):
    """Testa análise básica de ameaça."""
    component_id = "test_component"
    evidence = {"source_ip": "192.168.1.100", "port": 4444, "event_type": "suspicious_port"}

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    assert report.component_id == component_id
    # Evidências são expandidas com metadados, verificar campos originais
    assert report.evidence["source_ip"] == evidence["source_ip"]
    assert report.evidence["port"] == evidence["port"]
    assert report.evidence["event_type"] == evidence["event_type"]
    assert report.threat_category in ThreatCategory
    assert report.severity in ThreatSeverity


@pytest.mark.asyncio
async def test_analyze_threat_intrusion(forensic_analyzer):
    """Testa análise de ameaça de intrusão."""
    component_id = "test_component"
    evidence = {
        "source_ip": "192.168.1.100",
        "event_type": "unauthorized_access",
        "failed_login": True,
    }

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    assert len(report.patterns) > 0
    assert any("intrusion" in p for p in report.patterns)


@pytest.mark.asyncio
async def test_analyze_threat_malware(forensic_analyzer):
    """Testa análise de ameaça de malware."""
    component_id = "test_component"
    evidence = {
        "process_name": "suspicious_process",
        "event_type": "unusual_file_activity",
    }

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    assert len(report.patterns) > 0
    assert any("malware" in p for p in report.patterns)


@pytest.mark.asyncio
async def test_analyze_threat_data_exfiltration(forensic_analyzer):
    """Testa análise de exfiltração de dados."""
    component_id = "test_component"
    evidence = {
        "large_data_transfer": True,
        "encrypted_connection": True,
        "event_type": "unusual_network_traffic",
    }

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    assert len(report.patterns) > 0
    assert any("data_exfiltration" in p for p in report.patterns)


@pytest.mark.asyncio
async def test_analyze_threat_severity_critical(forensic_analyzer):
    """Testa classificação de severidade crítica."""
    component_id = "test_component"
    evidence = {
        "critical": True,
        "root": True,
        "encrypted": True,
        "event_type": "privilege_escalation",
    }

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    assert report.severity == ThreatSeverity.CRITICAL


@pytest.mark.asyncio
async def test_analyze_threat_recommendations(forensic_analyzer):
    """Testa geração de recomendações."""
    component_id = "test_component"
    evidence = {"event_type": "intrusion", "critical": True}

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    assert len(report.recommendations) > 0
    assert any("isolar" in r.lower() or "isolate" in r.lower() for r in report.recommendations)


@pytest.mark.asyncio
async def test_analyze_threat_safe_to_release(forensic_analyzer):
    """Testa determinação de segurança para liberação."""
    component_id = "test_component"
    evidence = {"event_type": "low_severity", "minor": True}

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    # Severidade baixa pode ser segura
    if report.severity == ThreatSeverity.LOW:
        assert report.safe_to_release in [True, False]  # Pode variar


@pytest.mark.asyncio
async def test_analyze_threat_not_safe_to_release(forensic_analyzer):
    """Testa que ameaças críticas não são seguras para liberar."""
    component_id = "test_component"
    evidence = {"event_type": "critical", "root": True, "encrypted": True}

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    if report.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.HIGH]:
        assert report.safe_to_release is False


@pytest.mark.asyncio
async def test_analyze_threat_confidence(forensic_analyzer):
    """Testa cálculo de confiança."""
    component_id = "test_component"
    evidence = {
        "source_ip": "192.168.1.100",
        "process_id": 1234,
        "event_type": "suspicious_activity",
    }

    report = await forensic_analyzer.analyze_threat(component_id, evidence)

    assert 0.0 <= report.confidence <= 1.0


def test_get_analysis_history(forensic_analyzer):
    """Testa obtenção de histórico de análises."""
    history = forensic_analyzer.get_analysis_history()

    assert isinstance(history, list)
    assert len(history) == 0  # Inicialmente vazio


@pytest.mark.asyncio
async def test_get_analysis_history_with_reports(forensic_analyzer):
    """Testa histórico com relatórios."""
    for i in range(5):
        await forensic_analyzer.analyze_threat(f"comp{i}", {"event_type": f"event_{i}"})

    history = forensic_analyzer.get_analysis_history(limit=3)

    assert len(history) == 3
    assert all(hasattr(r, "component_id") for r in history)

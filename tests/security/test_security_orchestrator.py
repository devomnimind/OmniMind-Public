"""
Testes para Security Orchestrator (security_orchestrator.py).

Cobertura de:
- Inicialização do orquestrador
- Monitoramento contínuo de segurança
- Auditoria de segurança completa
- Cálculo de risk score
- Geração de recomendações
- Determinação de status de segurança
- Integração com sensores de rede e web
"""

from __future__ import annotations

import asyncio
import pytest
from typing import Any
from unittest.mock import Mock, patch, AsyncMock

from src.security.security_orchestrator import (
    SecurityOrchestrator,
    SecurityStatus,
    SecurityReport,
    run_security_audit,
)


class TestSecurityStatus:
    """Testes para SecurityStatus enum."""

    def test_security_status_values(self) -> None:
        """Testa valores do enum SecurityStatus."""
        assert SecurityStatus.SECURE.value == "secure"
        assert SecurityStatus.WARNING.value == "warning"
        assert SecurityStatus.COMPROMISED.value == "compromised"
        assert SecurityStatus.CRITICAL.value == "critical"


class TestSecurityReport:
    """Testes para SecurityReport dataclass."""

    def test_security_report_initialization(self) -> None:
        """Testa inicialização de SecurityReport."""
        report = SecurityReport(
            timestamp="2025-11-23T00:00:00Z",
            status=SecurityStatus.SECURE,
            network_health={"health_score": 100, "total_hosts": 1},
            network_anomalies=[],
            web_vulnerabilities=[],
            security_events=[],
            recommendations=["Continue monitoring"],
            risk_score=0.0,
        )

        assert report.timestamp == "2025-11-23T00:00:00Z"
        assert report.status == SecurityStatus.SECURE
        assert report.risk_score == pytest.approx(0.0)
        assert len(report.recommendations) == 1


class TestSecurityOrchestrator:
    """Testes para SecurityOrchestrator."""

    @pytest.fixture
    def mock_audit_system(self) -> Mock:
        """Cria mock do sistema de auditoria."""
        mock = Mock()
        mock.log_action = Mock(return_value="mock_hash")
        mock.verify_chain_integrity = Mock(return_value={"valid": True, "message": "OK"})
        return mock

    @pytest.fixture
    def mock_alerting_system(self) -> Mock:
        """Cria mock do sistema de alertas."""
        mock = Mock()
        mock.create_alert = Mock()
        return mock

    @pytest.fixture
    def orchestrator(
        self, mock_audit_system: Mock, mock_alerting_system: Mock
    ) -> SecurityOrchestrator:
        """Cria instância do orquestrador com mocks."""
        return SecurityOrchestrator(
            audit_system=mock_audit_system,
            alerting_system=mock_alerting_system,
        )

    def test_initialization(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa inicialização do orquestrador."""
        assert orchestrator is not None
        assert orchestrator.network_sensors is not None
        assert orchestrator.web_scanner is not None
        assert orchestrator.monitoring_active is False
        assert orchestrator.monitoring_interval == 60

    def test_calculate_risk_score_low_risk(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa cálculo de risk score com baixo risco."""
        network_health = {"health_score": 100}
        network_anomalies: list[dict[str, Any]] = []
        web_vulnerabilities: list[dict[str, Any]] = []
        security_events: list[dict[str, Any]] = []

        risk_score = orchestrator._calculate_risk_score(
            network_health, network_anomalies, web_vulnerabilities, security_events
        )

        assert risk_score == pytest.approx(0.0)

    def test_calculate_risk_score_network_issues(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa cálculo de risk score com problemas de rede."""
        network_health = {"health_score": 50}  # 50% health
        network_anomalies: list[dict[str, Any]] = []
        web_vulnerabilities: list[dict[str, Any]] = []
        security_events: list[dict[str, Any]] = []

        risk_score = orchestrator._calculate_risk_score(
            network_health, network_anomalies, web_vulnerabilities, security_events
        )

        # 50% network health = 50 points reduction = 15 risk (50 * 0.3)
        assert risk_score == pytest.approx(15.0)

    def test_calculate_risk_score_with_anomalies(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa cálculo de risk score com anomalias de rede."""
        network_health = {"health_score": 100}
        network_anomalies: list[dict[str, Any]] = [
            Mock(),
            Mock(),
            Mock(),
        ]  # 3 anomalies
        web_vulnerabilities: list[dict[str, Any]] = []
        security_events: list[dict[str, Any]] = []

        risk_score = orchestrator._calculate_risk_score(
            network_health, network_anomalies, web_vulnerabilities, security_events
        )

        # 3 anomalies * 5 = 15 risk
        assert risk_score == pytest.approx(15.0)

    def test_calculate_risk_score_critical_web_vulnerabilities(
        self, orchestrator: SecurityOrchestrator
    ) -> None:
        """Testa cálculo de risk score com vulnerabilidades críticas."""
        network_health = {"health_score": 100}
        network_anomalies: list[dict[str, Any]] = []
        web_vulnerabilities: list[dict[str, Any]] = [
            {"severity": "CRITICAL"},
            {"severity": "CRITICAL"},
            {"severity": "HIGH"},
        ]
        security_events: list[dict[str, Any]] = []

        risk_score = orchestrator._calculate_risk_score(
            network_health, network_anomalies, web_vulnerabilities, security_events
        )

        # 2 critical * 10 + 1 high * 5 = 25 risk
        assert risk_score == pytest.approx(25.0)

    def test_calculate_risk_score_with_security_events(
        self, orchestrator: SecurityOrchestrator
    ) -> None:
        """Testa cálculo de risk score com eventos de segurança."""
        network_health = {"health_score": 100}
        network_anomalies: list[dict[str, Any]] = []
        web_vulnerabilities: list[dict[str, Any]] = []
        security_events: list[dict[str, Any]] = [Mock(), Mock()]  # 2 events

        risk_score = orchestrator._calculate_risk_score(
            network_health, network_anomalies, web_vulnerabilities, security_events
        )

        # 2 events * 5 = 10 risk
        assert risk_score == pytest.approx(10.0)

    def test_calculate_risk_score_max_capping(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa que risk score não excede 100."""
        network_health = {"health_score": 0}  # Max network risk
        network_anomalies = [Mock()] * 10  # Max anomaly risk
        web_vulnerabilities = [{"severity": "CRITICAL"}] * 10  # Max web risk
        security_events = [Mock()] * 10  # Max event risk

        risk_score = orchestrator._calculate_risk_score(
            network_health, network_anomalies, web_vulnerabilities, security_events
        )

        assert risk_score <= 100.0

    def test_determine_status_secure(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa determinação de status SECURE."""
        status = orchestrator._determine_status(15.0)
        assert status == SecurityStatus.SECURE

    def test_determine_status_warning(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa determinação de status WARNING."""
        status = orchestrator._determine_status(35.0)
        assert status == SecurityStatus.WARNING

    def test_determine_status_compromised(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa determinação de status COMPROMISED."""
        status = orchestrator._determine_status(60.0)
        assert status == SecurityStatus.COMPROMISED

    def test_determine_status_critical(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa determinação de status CRITICAL."""
        status = orchestrator._determine_status(80.0)
        assert status == SecurityStatus.CRITICAL

    def test_generate_recommendations_no_issues(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa geração de recomendações sem problemas."""
        recommendations = orchestrator._generate_recommendations([], [], [])

        assert len(recommendations) == 1
        assert "good" in recommendations[0].lower()

    def test_generate_recommendations_with_anomalies(
        self, orchestrator: SecurityOrchestrator
    ) -> None:
        """Testa geração de recomendações com anomalias."""
        network_anomalies = [Mock(), Mock()]
        recommendations = orchestrator._generate_recommendations(network_anomalies, [], [])

        assert any("anomalies" in r.lower() for r in recommendations)
        assert any("regular" in r.lower() for r in recommendations)

    def test_generate_recommendations_critical_web_vuln(
        self, orchestrator: SecurityOrchestrator
    ) -> None:
        """Testa geração de recomendações com vulnerabilidades críticas."""
        web_vulnerabilities = [{"severity": "CRITICAL"}, {"severity": "CRITICAL"}]
        recommendations = orchestrator._generate_recommendations([], web_vulnerabilities, [])

        assert any("urgent" in r.lower() for r in recommendations)
        assert any("critical" in r.lower() for r in recommendations)

    def test_generate_recommendations_with_security_events(
        self, orchestrator: SecurityOrchestrator
    ) -> None:
        """Testa geração de recomendações com eventos de segurança."""
        security_events = [{"type": "suspicious_process"}]
        recommendations = orchestrator._generate_recommendations([], [], security_events)

        assert any("security events" in r.lower() for r in recommendations)

    @patch("src.security.security_orchestrator.NetworkSensorGanglia")
    @patch("src.security.security_orchestrator.WebScannerBrain")
    def test_run_full_security_audit_basic(
        self,
        mock_web_scanner: Mock,
        mock_network_sensors: Mock,
        orchestrator: SecurityOrchestrator,
    ) -> None:
        """Testa execução de auditoria de segurança completa."""
        # Setup mocks
        mock_network_instance = Mock()
        mock_network_instance.establish_baseline = Mock()
        mock_network_instance.scan_network = Mock()
        mock_network_instance.get_network_health = Mock(
            return_value={"health_score": 100, "total_hosts": 1}
        )
        mock_network_instance.detect_anomalies = Mock(return_value=[])
        orchestrator.network_sensors = mock_network_instance

        mock_web_instance = Mock()
        mock_web_instance.scan_url = Mock(return_value={"findings": []})
        orchestrator.web_scanner = mock_web_instance

        # Run audit
        report = orchestrator.run_full_security_audit()

        # Validate report
        assert isinstance(report, SecurityReport)
        assert report.status == SecurityStatus.SECURE
        assert report.risk_score < 20.0  # Low risk
        assert len(report.recommendations) > 0

    @patch("src.security.security_orchestrator.NetworkSensorGanglia")
    @patch("src.security.security_orchestrator.WebScannerBrain")
    def test_run_full_security_audit_with_web_targets(
        self,
        mock_web_scanner: Mock,
        mock_network_sensors: Mock,
        orchestrator: SecurityOrchestrator,
    ) -> None:
        """Testa auditoria com alvos web."""
        # Setup mocks
        mock_network_instance = Mock()
        mock_network_instance.establish_baseline = Mock()
        mock_network_instance.scan_network = Mock()
        mock_network_instance.get_network_health = Mock(return_value={"health_score": 100})
        mock_network_instance.detect_anomalies = Mock(return_value=[])
        orchestrator.network_sensors = mock_network_instance

        mock_web_instance = Mock()
        # Multiple critical vulnerabilities to push risk score higher
        mock_web_instance.scan_url = Mock(
            return_value={
                "findings": [
                    {"severity": "CRITICAL", "description": "SQL Injection"},
                    {"severity": "CRITICAL", "description": "XSS"},
                    {"severity": "HIGH", "description": "CSRF"},
                ]
            }
        )
        orchestrator.web_scanner = mock_web_instance

        # Run audit with web targets
        report = orchestrator.run_full_security_audit(web_targets=["http://example.com"])

        # Validate
        assert len(report.web_vulnerabilities) == 3
        # Risk score: 2 critical * 10 + 1 high * 5 = 25 (WARNING range)
        assert report.status in [
            SecurityStatus.WARNING,
            SecurityStatus.COMPROMISED,
            SecurityStatus.CRITICAL,
        ]

    @patch("src.security.security_orchestrator.NetworkSensorGanglia")
    def test_run_full_security_audit_creates_critical_alert(
        self,
        mock_network_sensors: Mock,
        orchestrator: SecurityOrchestrator,
        mock_alerting_system: Mock,
    ) -> None:
        """Testa criação de alerta crítico durante auditoria."""
        # Setup for critical status
        mock_network_instance = Mock()
        mock_network_instance.establish_baseline = Mock()
        mock_network_instance.scan_network = Mock()
        mock_network_instance.get_network_health = Mock(
            return_value={"health_score": 0}  # Critical health
        )
        mock_network_instance.detect_anomalies = Mock(return_value=[Mock()] * 10)  # Many anomalies
        orchestrator.network_sensors = mock_network_instance

        # Run audit
        report = orchestrator.run_full_security_audit()

        # Verify critical alert was created
        assert report.status in [SecurityStatus.COMPROMISED, SecurityStatus.CRITICAL]
        mock_alerting_system.create_alert.assert_called()

    @pytest.mark.asyncio
    async def test_start_continuous_monitoring(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa início de monitoramento contínuo."""
        # Mock monitoring methods
        with patch.object(orchestrator, "_monitor_network", new_callable=AsyncMock):
            with patch.object(orchestrator, "_monitor_web_applications", new_callable=AsyncMock):
                with patch.object(orchestrator, "_monitor_system_security", new_callable=AsyncMock):
                    # Start monitoring in background
                    monitoring_task = asyncio.create_task(
                        orchestrator.start_continuous_monitoring()
                    )

                    # Give it time to start
                    await asyncio.sleep(0.1)

                    # Verify monitoring is active
                    assert orchestrator.monitoring_active is True

                    # Stop monitoring
                    orchestrator.stop_continuous_monitoring()

                    # Give it time to stop
                    await asyncio.sleep(0.1)

        # Cancel task
        monitoring_task.cancel()

        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

    def test_stop_continuous_monitoring(
        self, orchestrator: SecurityOrchestrator, mock_audit_system: Mock
    ) -> None:
        """Testa parada de monitoramento contínuo."""
        orchestrator.monitoring_active = True
        orchestrator.stop_continuous_monitoring()

        assert orchestrator.monitoring_active is False
        mock_audit_system.log_action.assert_called()

    @pytest.mark.asyncio
    async def test_monitor_network(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa monitoramento de rede."""
        # Mock network sensors
        mock_sensor = Mock()
        mock_sensor.scan_network = Mock()
        mock_sensor.detect_anomalies = Mock(return_value=[])
        orchestrator.network_sensors = mock_sensor

        # Monitor network
        await orchestrator._monitor_network(["127.0.0.1"])

        # Verify scan was called
        mock_sensor.scan_network.assert_called_once()

    @pytest.mark.asyncio
    async def test_monitor_web_applications(self, orchestrator: SecurityOrchestrator) -> None:
        """Testa monitoramento de aplicações web."""
        # Mock web scanner
        mock_scanner = Mock()
        mock_scanner.scan_url = Mock(return_value={"findings": []})
        orchestrator.web_scanner = mock_scanner

        # Monitor web apps
        await orchestrator._monitor_web_applications(["http://example.com"])

        # Verify scan was called
        mock_scanner.scan_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_monitor_system_security_no_agent(
        self, orchestrator: SecurityOrchestrator
    ) -> None:
        """Testa monitoramento de sistema sem agente."""
        # No security agent
        orchestrator.security_agent = None

        # Should complete without errors
        await orchestrator._monitor_system_security()

        # No exceptions expected


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""

    @patch("src.security.security_orchestrator.SecurityOrchestrator")
    def test_run_security_audit(self, mock_orchestrator_class: Mock) -> None:
        """Testa função de conveniência run_security_audit."""
        mock_instance = Mock()
        mock_instance.run_full_security_audit = Mock(return_value=Mock(spec=SecurityReport))
        mock_orchestrator_class.return_value = mock_instance

        run_security_audit()

        mock_orchestrator_class.assert_called_once()
        mock_instance.run_full_security_audit.assert_called_once()

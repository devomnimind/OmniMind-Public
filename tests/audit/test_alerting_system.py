"""
Testes para Alerting System (alerting_system.py).

Cobertura de:
- Criação de alertas
- Acknowledge e resolve de alertas
- Sistema de subscrição e broadcast
- Estatísticas de alertas
- Histórico de alertas
- Monitoramento de integridade de audit chain
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest

from src.audit.alerting_system import (
    Alert,
    AlertCategory,
    AlertingSystem,
    AlertSeverity,
    create_alert,
    get_active_alerts,
    get_alerting_system,
)


class TestAlertSeverity:
    """Testes para AlertSeverity enum."""

    def test_alert_severity_values(self) -> None:
        """Testa valores do enum AlertSeverity."""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ERROR.value == "error"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestAlertCategory:
    """Testes para AlertCategory enum."""

    def test_alert_category_values(self) -> None:
        """Testa valores do enum AlertCategory."""
        assert AlertCategory.SECURITY.value == "security"
        assert AlertCategory.COMPLIANCE.value == "compliance"
        assert AlertCategory.SYSTEM.value == "system"
        assert AlertCategory.AUDIT.value == "audit"
        assert AlertCategory.PERFORMANCE.value == "performance"


class TestAlert:
    """Testes para Alert dataclass."""

    def test_alert_initialization(self) -> None:
        """Testa inicialização de Alert."""
        alert = Alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SECURITY,
            title="Test Alert",
            message="Test message",
        )

        assert alert.severity == AlertSeverity.WARNING
        assert alert.category == AlertCategory.SECURITY
        assert alert.title == "Test Alert"
        assert alert.message == "Test message"
        assert alert.id != ""
        assert alert.timestamp != ""
        assert alert.acknowledged is False
        assert alert.resolved is False

    def test_alert_to_dict(self) -> None:
        """Testa conversão de alert para dict."""
        alert = Alert(
            severity=AlertSeverity.ERROR,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )

        result = alert.to_dict()

        assert result["severity"] == "error"
        assert result["category"] == "system"
        assert result["title"] == "Test"
        assert "id" in result
        assert "timestamp" in result

    def test_alert_from_dict(self) -> None:
        """Testa criação de alert a partir de dict."""
        data = {
            "id": "test_id",
            "timestamp": "2025-11-23T00:00:00Z",
            "severity": "critical",
            "category": "security",
            "title": "Critical Alert",
            "message": "Critical message",
            "details": {"key": "value"},
            "source": "test_source",
            "acknowledged": True,
            "resolved": False,
        }

        alert = Alert.from_dict(data)

        assert alert.id == "test_id"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.category == AlertCategory.SECURITY
        assert alert.title == "Critical Alert"
        assert alert.acknowledged is True
        assert alert.resolved is False


class TestAlertingSystem:
    """Testes para AlertingSystem."""

    @pytest.fixture
    def temp_log_dir(self) -> Generator[Path, None, None]:
        """Cria diretório temporário para logs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def mock_audit_system(self, temp_log_dir: Path) -> Mock:
        """Cria mock do sistema de auditoria."""
        mock = Mock()
        mock.log_dir = temp_log_dir
        mock.log_action = Mock(return_value="mock_hash")
        mock.verify_chain_integrity = Mock(return_value={"valid": True, "message": "OK"})
        return mock

    @pytest.fixture
    def alerting_system(self, mock_audit_system: Mock, temp_log_dir: Path) -> AlertingSystem:
        """Cria instância do sistema de alertas com mock.

        NOTA: Limpa alertas existentes ANTES de criar instância para garantir
        estado limpo nos testes. O AlertingSystem carrega alertas de arquivos
        durante __init__, então precisamos limpar arquivos primeiro.
        """
        # Limpar arquivos de alertas ANTES de criar instância
        # (AlertingSystem carrega alertas durante __init__)
        alerts_file = temp_log_dir / "alerts" / "alerts.jsonl"
        if alerts_file.exists():
            alerts_file.unlink()

        # Limpar também arquivos em data/alerts (compatibilidade)
        data_alerts_dir = Path("data/alerts")
        if data_alerts_dir.exists():
            for alert_file in data_alerts_dir.glob("alert_*.json"):
                alert_file.unlink()
            index_file = data_alerts_dir / "alerts_index.json"
            if index_file.exists():
                index_file.unlink()

        # Criar instância (agora sem alertas carregados)
        system = AlertingSystem(audit_system=mock_audit_system)

        # Garantir estado limpo (caso algum alerta tenha sido carregado)
        system.active_alerts.clear()
        system.stats = {
            "total_alerts": 0,
            "active_alerts": 0,
            "critical_active": 0,
            "by_severity": {severity.value: 0 for severity in AlertSeverity},
            "by_category": {category.value: 0 for category in AlertCategory},
        }

        return system

    def test_initialization(self, alerting_system: AlertingSystem, temp_log_dir: Path) -> None:
        """Testa inicialização do sistema de alertas."""
        assert alerting_system is not None
        assert alerting_system.alerts_dir.exists()
        assert len(alerting_system.active_alerts) == 0
        assert len(alerting_system.subscribers) == 0

    def test_create_alert_basic(self, alerting_system: AlertingSystem) -> None:
        """Testa criação básica de alerta."""
        alert = alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Test Alert",
            message="Test message",
        )

        assert alert is not None
        assert alert.severity == AlertSeverity.INFO
        assert alert.id in alerting_system.active_alerts

    def test_create_alert_with_details(self, alerting_system: AlertingSystem) -> None:
        """Testa criação de alerta com detalhes."""
        details = {"key1": "value1", "key2": "value2"}

        alert = alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SECURITY,
            title="Test",
            message="Message",
            details=details,
        )

        assert alert.details == details

    def test_create_alert_with_custom_source(self, alerting_system: AlertingSystem) -> None:
        """Testa criação de alerta com fonte customizada."""
        alert = alerting_system.create_alert(
            severity=AlertSeverity.ERROR,
            category=AlertCategory.AUDIT,
            title="Test",
            message="Message",
            source="custom_source",
        )

        assert alert.source == "custom_source"

    def test_create_alert_updates_stats(self, alerting_system: AlertingSystem) -> None:
        """Testa que criar alerta atualiza estatísticas."""
        initial_total = alerting_system.stats["total_alerts"]

        alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )

        assert alerting_system.stats["total_alerts"] == initial_total + 1
        assert alerting_system.stats["by_severity"]["info"] == 1

    def test_create_alert_saves_to_file(self, alerting_system: AlertingSystem) -> None:
        """Testa que alerta é salvo em arquivo."""
        alert = alerting_system.create_alert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.SECURITY,
            title="Test",
            message="Message",
        )

        # Check file exists and contains the alert
        assert alerting_system.alerts_file.exists()

        with open(alerting_system.alerts_file, "r") as f:
            lines = f.readlines()
            alert_found = False
            for line in lines:
                data = json.loads(line)
                if data["id"] == alert.id:
                    alert_found = True
                    break

        assert alert_found

    def test_acknowledge_alert(self, alerting_system: AlertingSystem) -> None:
        """Testa acknowledge de alerta."""
        alert = alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )

        result = alerting_system.acknowledge_alert(alert.id)

        assert result is True
        assert alerting_system.active_alerts[alert.id].acknowledged is True

    def test_acknowledge_nonexistent_alert(self, alerting_system: AlertingSystem) -> None:
        """Testa acknowledge de alerta inexistente."""
        result = alerting_system.acknowledge_alert("nonexistent_id")

        assert result is False

    def test_resolve_alert(self, alerting_system: AlertingSystem) -> None:
        """Testa resolução de alerta."""
        alert = alerting_system.create_alert(
            severity=AlertSeverity.ERROR,
            category=AlertCategory.SECURITY,
            title="Test",
            message="Message",
        )

        result = alerting_system.resolve_alert(alert.id, "Fixed the issue")

        assert result is True
        assert alert.id not in alerting_system.active_alerts

    def test_resolve_alert_with_notes(self, alerting_system: AlertingSystem) -> None:
        """Testa resolução de alerta com notas."""
        alert = alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )

        alerting_system.resolve_alert(alert.id, "Resolution notes")

        # Alert should be marked resolved and removed from active alerts
        assert alert.id not in alerting_system.active_alerts
        assert alert.resolved is True

    def test_resolve_nonexistent_alert(self, alerting_system: AlertingSystem) -> None:
        """Testa resolução de alerta inexistente."""
        result = alerting_system.resolve_alert("nonexistent_id")

        assert result is False

    def test_get_active_alerts_all(self, alerting_system: AlertingSystem) -> None:
        """Testa obtenção de todos os alertas ativos.

        NOTA: Limpa alertas existentes antes de criar novos para garantir
        contagem correta mesmo se houver alertas carregados de execuções anteriores.
        """
        # Limpar alertas existentes (podem vir de _load_alerts ou _migrate_old_alerts)
        alerting_system.active_alerts.clear()

        alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Alert 1",
            message="Message 1",
        )
        alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SECURITY,
            title="Alert 2",
            message="Message 2",
        )

        active = alerting_system.get_active_alerts()

        assert len(active) == 2

    def test_get_active_alerts_by_severity(self, alerting_system: AlertingSystem) -> None:
        """Testa obtenção de alertas por severidade.

        NOTA: Limpa alertas existentes antes de criar novos para garantir
        contagem correta mesmo se houver alertas carregados de execuções anteriores.
        """
        # Limpar alertas existentes (podem vir de _load_alerts ou _migrate_old_alerts)
        alerting_system.active_alerts.clear()

        alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Info",
            message="Message",
        )
        alerting_system.create_alert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.SECURITY,
            title="Critical",
            message="Message",
        )

        critical_alerts = alerting_system.get_active_alerts(severity=AlertSeverity.CRITICAL)

        assert len(critical_alerts) == 1
        assert critical_alerts[0].severity == AlertSeverity.CRITICAL

    def test_get_active_alerts_by_category(self, alerting_system: AlertingSystem) -> None:
        """Testa obtenção de alertas por categoria."""
        alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SECURITY,
            title="Security",
            message="Message",
        )
        alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="System",
            message="Message",
        )

        security_alerts = alerting_system.get_active_alerts(category=AlertCategory.SECURITY)

        assert len(security_alerts) == 1
        assert security_alerts[0].category == AlertCategory.SECURITY

    def test_get_active_alerts_sorted(self, alerting_system: AlertingSystem) -> None:
        """Testa que alertas são retornados ordenados por timestamp."""
        import time

        alert1 = alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="First",
            message="Message",
        )
        time.sleep(0.01)  # Small delay to ensure different timestamps
        alert2 = alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SYSTEM,
            title="Second",
            message="Message",
        )

        active = alerting_system.get_active_alerts()

        # Should be sorted newest first
        assert active[0].id == alert2.id
        assert active[1].id == alert1.id

    def test_get_alert_history(self, alerting_system: AlertingSystem, temp_log_dir: Path) -> None:
        """Testa obtenção de histórico de alertas."""
        # Create and resolve some alerts
        alert1 = alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Test 1",
            message="Message",
        )
        alerting_system.resolve_alert(alert1.id)

        alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SECURITY,
            title="Test 2",
            message="Message",
        )

        history = alerting_system.get_alert_history(limit=10)

        assert len(history) >= 2

    def test_get_alert_history_with_limit(self, alerting_system: AlertingSystem) -> None:
        """Testa histórico com limite."""
        # Create multiple alerts
        for i in range(5):
            alerting_system.create_alert(
                severity=AlertSeverity.INFO,
                category=AlertCategory.SYSTEM,
                title=f"Alert {i}",
                message="Message",
            )

        history = alerting_system.get_alert_history(limit=3)

        assert len(history) == 3

    def test_get_statistics(self, alerting_system: AlertingSystem) -> None:
        """Testa obtenção de estatísticas.

        NOTA: Limpa alertas e estatísticas existentes antes de criar novos para garantir
        contagem correta mesmo se houver alertas carregados de execuções anteriores.
        """
        # Limpar alertas e estatísticas existentes
        alerting_system.active_alerts.clear()
        alerting_system.stats = {
            "total_alerts": 0,
            "active_alerts": 0,
            "critical_active": 0,
            "by_severity": {severity.value: 0 for severity in AlertSeverity},
            "by_category": {category.value: 0 for category in AlertCategory},
        }

        alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )
        alerting_system.create_alert(
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.SECURITY,
            title="Critical",
            message="Message",
        )

        stats = alerting_system.get_statistics()

        assert stats["total_alerts"] == 2
        assert stats["active_alerts"] == 2
        assert stats["critical_active"] == 1
        assert "by_severity" in stats
        assert "by_category" in stats

    def test_subscribe_and_broadcast(self, alerting_system: AlertingSystem) -> None:
        """Testa subscrição e broadcast de alertas."""
        callback_called = []

        def callback(alert: Alert) -> None:
            callback_called.append(alert)

        alerting_system.subscribe(callback)

        alert = alerting_system.create_alert(
            severity=AlertSeverity.WARNING,
            category=AlertCategory.SECURITY,
            title="Test",
            message="Message",
        )

        assert len(callback_called) == 1
        assert callback_called[0].id == alert.id

    def test_unsubscribe(self, alerting_system: AlertingSystem) -> None:
        """Testa remoção de subscrição."""
        callback_called = []

        def callback(alert: Alert) -> None:
            callback_called.append(alert)

        alerting_system.subscribe(callback)
        alerting_system.unsubscribe(callback)

        alerting_system.create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )

        assert len(callback_called) == 0

    def test_broadcast_with_failing_callback(self, alerting_system: AlertingSystem) -> None:
        """Testa broadcast com callback que falha."""

        def failing_callback(alert: Alert) -> None:
            raise Exception("Callback error")

        alerting_system.subscribe(failing_callback)

        # Should not raise, just log
        alert = alerting_system.create_alert(
            severity=AlertSeverity.ERROR,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )

        assert alert is not None

    @pytest.mark.asyncio
    async def test_monitor_audit_chain_healthy(self, alerting_system: AlertingSystem) -> None:
        """Testa monitoramento de audit chain saudável.

        NOTA: Limpa alertas existentes antes de executar para garantir
        contagem correta mesmo se houver alertas carregados de execuções anteriores.
        """
        # Limpar alertas existentes antes de testar
        alerting_system.active_alerts.clear()

        # Run one iteration
        task = asyncio.create_task(alerting_system.monitor_audit_chain(interval=1))

        await asyncio.sleep(0.2)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should not create critical alerts
        critical_alerts = alerting_system.get_active_alerts(severity=AlertSeverity.CRITICAL)
        assert len(critical_alerts) == 0

    @pytest.mark.asyncio
    async def test_monitor_audit_chain_invalid(
        self, alerting_system: AlertingSystem, mock_audit_system: Mock
    ) -> None:
        """Testa monitoramento com chain inválida.

        NOTA: Limpa alertas existentes antes de executar para garantir
        contagem correta mesmo se houver alertas carregados de execuções anteriores.
        """
        # Limpar alertas existentes antes de testar
        alerting_system.active_alerts.clear()

        # Make integrity check fail
        mock_audit_system.verify_chain_integrity = Mock(
            return_value={"valid": False, "message": "Integrity compromised"}
        )

        # Run one iteration
        task = asyncio.create_task(alerting_system.monitor_audit_chain(interval=1))

        await asyncio.sleep(0.2)

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should create critical alert
        critical_alerts = alerting_system.get_active_alerts(
            severity=AlertSeverity.CRITICAL, category=AlertCategory.AUDIT
        )
        assert len(critical_alerts) > 0

    def test_load_existing_alerts(self, mock_audit_system: Mock, temp_log_dir: Path) -> None:
        """Testa carregamento de alertas existentes."""
        # Create alerts file manually
        alerts_dir = temp_log_dir / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        alerts_file = alerts_dir / "alerts.jsonl"

        alert_data = {
            "id": "test_123",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": "warning",
            "category": "system",
            "title": "Test Alert",
            "message": "Test message",
            "details": {},
            "source": "test",
            "acknowledged": False,
            "resolved": False,
        }

        with open(alerts_file, "w") as f:
            f.write(json.dumps(alert_data) + "\n")

        # Create new alerting system (should load existing alerts)
        system = AlertingSystem(audit_system=mock_audit_system)

        assert "test_123" in system.active_alerts
        assert system.stats["total_alerts"] == 1


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""

    @patch("src.audit.alerting_system.get_alerting_system")
    def test_create_alert_function(self, mock_get_system: Mock) -> None:
        """Testa função de conveniência create_alert."""
        mock_system = Mock()
        mock_alert = Mock(spec=Alert)
        mock_system.create_alert = Mock(return_value=mock_alert)
        mock_get_system.return_value = mock_system

        result = create_alert(
            severity=AlertSeverity.INFO,
            category=AlertCategory.SYSTEM,
            title="Test",
            message="Message",
        )

        mock_system.create_alert.assert_called_once()
        assert result == mock_alert

    @patch("src.audit.alerting_system.get_alerting_system")
    def test_get_active_alerts_function(self, mock_get_system: Mock) -> None:
        """Testa função de conveniência get_active_alerts."""
        mock_system = Mock()
        mock_system.get_active_alerts = Mock(return_value=[])
        mock_get_system.return_value = mock_system

        result = get_active_alerts()

        mock_system.get_active_alerts.assert_called_once()
        assert result == []

    def test_get_alerting_system_singleton(self) -> None:
        """Testa que get_alerting_system retorna singleton."""
        # Reset global instance
        import src.audit.alerting_system as module

        module._alerting_system = None

        system1 = get_alerting_system()
        system2 = get_alerting_system()

        assert system1 is system2

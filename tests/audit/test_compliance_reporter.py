"""
Testes para Compliance Reporter (compliance_reporter.py).

Cobertura de:
- Geração de relatórios LGPD
- Geração de relatórios GDPR
- Exportação de audit trail
- Cálculo de compliance score
- Verificações de conformidade
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Generator
from unittest.mock import Mock, patch

import pytest

from src.audit.compliance_reporter import (
    ComplianceReporter,
    ComplianceStandard,
    export_audit_trail,
    generate_gdpr_report,
    generate_lgpd_report,
)


class TestComplianceStandard:
    """Testes para ComplianceStandard enum."""

    def test_compliance_standard_values(self) -> None:
        """Testa valores do enum ComplianceStandard."""
        assert ComplianceStandard.LGPD.value == "lgpd"
        assert ComplianceStandard.GDPR.value == "gdpr"
        assert ComplianceStandard.SOC2.value == "soc2"
        assert ComplianceStandard.HIPAA.value == "hipaa"
        assert ComplianceStandard.PCI_DSS.value == "pci_dss"


class TestComplianceReporter:
    """Testes para ComplianceReporter."""

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
        mock.audit_log_file = temp_log_dir / "audit_chain.log"
        mock.log_action = Mock(return_value="mock_hash")
        mock.verify_chain_integrity = Mock(return_value={"valid": True, "message": "OK"})
        return mock

    @pytest.fixture
    def reporter(self, mock_audit_system: Mock, temp_log_dir: Path) -> ComplianceReporter:
        """Cria instância do reporter com mock."""
        return ComplianceReporter(audit_system=mock_audit_system)

    def test_initialization(self, reporter: ComplianceReporter, temp_log_dir: Path) -> None:
        """Testa inicialização do compliance reporter."""
        assert reporter is not None
        assert reporter.report_dir.exists()
        assert reporter.report_dir == temp_log_dir / "compliance_reports"

    def test_generate_lgpd_report_basic(self, reporter: ComplianceReporter) -> None:
        """Testa geração básica de relatório LGPD."""
        report = reporter.generate_lgpd_report()

        assert report["standard"] == "LGPD"
        assert "report_id" in report
        assert "lgpd_" in report["report_id"]
        assert "period" in report
        assert "compliance_checks" in report
        assert "summary" in report

    def test_generate_lgpd_report_compliance_checks(self, reporter: ComplianceReporter) -> None:
        """Testa checks de conformidade LGPD."""
        report = reporter.generate_lgpd_report()

        checks = report["compliance_checks"]
        assert "data_minimization" in checks
        assert "transparency" in checks
        assert "security" in checks
        assert "user_rights" in checks
        assert "consent" in checks
        assert "retention" in checks

        # All checks should have compliant flag
        for check_name, check_data in checks.items():
            assert "compliant" in check_data
            assert isinstance(check_data["compliant"], bool)

    def test_generate_lgpd_report_summary(self, reporter: ComplianceReporter) -> None:
        """Testa sumário do relatório LGPD."""
        report = reporter.generate_lgpd_report()

        summary = report["summary"]
        assert "total_checks" in summary
        assert "passed_checks" in summary
        assert "failed_checks" in summary
        assert "compliance_score" in summary
        assert "status" in summary

        assert summary["total_checks"] == 6  # LGPD has 6 checks
        assert 0 <= summary["compliance_score"] <= 100

    def test_generate_lgpd_report_with_date_range(self, reporter: ComplianceReporter) -> None:
        """Testa geração de relatório LGPD com período específico."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        report = reporter.generate_lgpd_report(start_date=start_date, end_date=end_date)

        assert report["period"]["start"] == start_date.isoformat()
        assert report["period"]["end"] == end_date.isoformat()

    def test_generate_lgpd_report_saves_file(self, reporter: ComplianceReporter) -> None:
        """Testa que relatório LGPD é salvo em arquivo."""
        report = reporter.generate_lgpd_report()

        # Check file was created
        report_files = list(reporter.report_dir.glob("lgpd_*.json"))
        assert len(report_files) > 0

        # Verify content
        with open(report_files[0], "r") as f:
            saved_report = json.load(f)
        assert saved_report["report_id"] == report["report_id"]

    def test_generate_gdpr_report_basic(self, reporter: ComplianceReporter) -> None:
        """Testa geração básica de relatório GDPR."""
        report = reporter.generate_gdpr_report()

        assert report["standard"] == "GDPR"
        assert "report_id" in report
        assert "gdpr_" in report["report_id"]
        assert "compliance_checks" in report
        assert "summary" in report

    def test_generate_gdpr_report_compliance_checks(self, reporter: ComplianceReporter) -> None:
        """Testa checks de conformidade GDPR."""
        report = reporter.generate_gdpr_report()

        checks = report["compliance_checks"]
        assert "lawfulness" in checks
        assert "purpose_limitation" in checks
        assert "data_minimization" in checks
        assert "accuracy" in checks
        assert "storage_limitation" in checks
        assert "security" in checks
        assert "accountability" in checks

        assert len(checks) == 7  # GDPR has 7 checks

    def test_generate_gdpr_report_summary(self, reporter: ComplianceReporter) -> None:
        """Testa sumário do relatório GDPR."""
        report = reporter.generate_gdpr_report()

        summary = report["summary"]
        assert summary["total_checks"] == 7
        assert 0 <= summary["compliance_score"] <= 100

    def test_check_data_minimization(self, reporter: ComplianceReporter) -> None:
        """Testa verificação de minimização de dados."""
        result = reporter._check_data_minimization(
            datetime.now(timezone.utc) - timedelta(days=30),
            datetime.now(timezone.utc),
        )

        assert "compliant" in result
        assert "description" in result
        assert "details" in result

    def test_check_transparency(self, reporter: ComplianceReporter, temp_log_dir: Path) -> None:
        """Testa verificação de transparência."""
        # Create some audit log events
        audit_log = temp_log_dir / "audit_chain.log"
        events = [
            {"datetime_utc": datetime.now(timezone.utc).isoformat(), "action": "test1"},
            {"datetime_utc": datetime.now(timezone.utc).isoformat(), "action": "test2"},
        ]
        with open(audit_log, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        result = reporter._check_transparency(
            datetime.now(timezone.utc) - timedelta(days=1),
            datetime.now(timezone.utc),
        )

        assert result["compliant"] is True

    def test_check_security_measures(self, reporter: ComplianceReporter) -> None:
        """Testa verificação de medidas de segurança."""
        result = reporter._check_security_measures(
            datetime.now(timezone.utc) - timedelta(days=30),
            datetime.now(timezone.utc),
        )

        assert "compliant" in result
        assert result["compliant"] is True  # Mock returns valid integrity

    def test_check_user_rights(self, reporter: ComplianceReporter) -> None:
        """Testa verificação de direitos do usuário."""
        result = reporter._check_user_rights(
            datetime.now(timezone.utc) - timedelta(days=30),
            datetime.now(timezone.utc),
        )

        assert result["compliant"] is True
        assert "user rights" in result["description"].lower()

    def test_check_consent_management(self, reporter: ComplianceReporter) -> None:
        """Testa verificação de gestão de consentimento."""
        result = reporter._check_consent_management(
            datetime.now(timezone.utc) - timedelta(days=30),
            datetime.now(timezone.utc),
        )

        assert result["compliant"] is True
        assert "consent" in result["description"].lower()

    def test_check_retention_policy(self, reporter: ComplianceReporter) -> None:
        """Testa verificação de política de retenção."""
        result = reporter._check_retention_policy(
            datetime.now(timezone.utc) - timedelta(days=30),
            datetime.now(timezone.utc),
        )

        assert result["compliant"] is True
        assert "retention" in result["description"].lower()

    def test_export_audit_trail_json(
        self, reporter: ComplianceReporter, temp_log_dir: Path
    ) -> None:
        """Testa exportação de audit trail em JSON."""
        # Create some audit events
        audit_log = temp_log_dir / "audit_chain.log"
        events = [
            {
                "datetime_utc": datetime.now(timezone.utc).isoformat(),
                "action": "test_action",
                "details": {"key": "value"},
            }
        ]
        with open(audit_log, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        export_path = reporter.export_audit_trail(format="json")

        assert Path(export_path).exists()
        assert export_path.endswith(".json")

        # Verify content
        with open(export_path, "r") as f:
            exported_events = json.load(f)
        assert len(exported_events) == 1

    def test_export_audit_trail_csv(self, reporter: ComplianceReporter, temp_log_dir: Path) -> None:
        """Testa exportação de audit trail em CSV."""
        # Create some audit events
        audit_log = temp_log_dir / "audit_chain.log"
        events = [
            {
                "datetime_utc": datetime.now(timezone.utc).isoformat(),
                "action": "test_action",
            }
        ]
        with open(audit_log, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        export_path = reporter.export_audit_trail(format="csv")

        assert Path(export_path).exists()
        assert export_path.endswith(".csv")

    def test_export_audit_trail_xml(self, reporter: ComplianceReporter, temp_log_dir: Path) -> None:
        """Testa exportação de audit trail em XML."""
        # Create some audit events
        audit_log = temp_log_dir / "audit_chain.log"
        events = [
            {
                "datetime_utc": datetime.now(timezone.utc).isoformat(),
                "action": "test_action",
            }
        ]
        with open(audit_log, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        export_path = reporter.export_audit_trail(format="xml")

        assert Path(export_path).exists()
        assert export_path.endswith(".xml")

    def test_export_audit_trail_invalid_format(self, reporter: ComplianceReporter) -> None:
        """Testa exportação com formato inválido."""
        with pytest.raises(ValueError) as exc_info:
            reporter.export_audit_trail(format="invalid")

        assert "Unsupported format" in str(exc_info.value)

    def test_export_audit_trail_with_date_range(
        self, reporter: ComplianceReporter, temp_log_dir: Path
    ) -> None:
        """Testa exportação com período específico."""
        # Create events with different dates
        audit_log = temp_log_dir / "audit_chain.log"
        now = datetime.now(timezone.utc)
        events = [
            {
                "datetime_utc": (now - timedelta(days=10)).isoformat(),
                "action": "old_event",
            },
            {"datetime_utc": (now - timedelta(days=5)).isoformat(), "action": "recent"},
            {"datetime_utc": now.isoformat(), "action": "new_event"},
        ]
        with open(audit_log, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        export_path = reporter.export_audit_trail(
            format="json",
            start_date=now - timedelta(days=7),
            end_date=now,
        )

        with open(export_path, "r") as f:
            exported_events = json.load(f)

        # Should only have events from last 7 days
        assert len(exported_events) == 2

    def test_get_events_in_range(self, reporter: ComplianceReporter, temp_log_dir: Path) -> None:
        """Testa obtenção de eventos em um período."""
        # Create events
        audit_log = temp_log_dir / "audit_chain.log"
        now = datetime.now(timezone.utc)
        events = [
            {"datetime_utc": (now - timedelta(days=2)).isoformat(), "action": "event1"},
            {"datetime_utc": (now - timedelta(days=1)).isoformat(), "action": "event2"},
        ]
        with open(audit_log, "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")

        result = reporter._get_events_in_range(now - timedelta(days=3), now + timedelta(days=1))

        assert len(result) == 2

    def test_get_events_in_range_no_file(self, reporter: ComplianceReporter) -> None:
        """Testa obtenção de eventos quando arquivo não existe."""
        result = reporter._get_events_in_range(
            datetime.now(timezone.utc) - timedelta(days=1),
            datetime.now(timezone.utc),
        )

        assert result == []

    def test_save_report(self, reporter: ComplianceReporter, temp_log_dir: Path) -> None:
        """Testa salvamento de relatório."""
        report = {
            "report_id": "test_123",
            "standard": "LGPD",
            "data": "test",
        }

        reporter._save_report(report, ComplianceStandard.LGPD)

        # Check file exists
        report_file = reporter.report_dir / "lgpd_test_123.json"
        assert report_file.exists()

        # Verify content
        with open(report_file, "r") as f:
            saved = json.load(f)
        assert saved["report_id"] == "test_123"

    def test_export_csv_empty_events(
        self, reporter: ComplianceReporter, temp_log_dir: Path
    ) -> None:
        """Testa exportação CSV sem eventos."""
        export_file = temp_log_dir / "test_export.csv"
        reporter._export_csv([], export_file)

        # File should not be created or be empty
        assert not export_file.exists() or export_file.stat().st_size == 0

    def test_export_xml_events(self, reporter: ComplianceReporter, temp_log_dir: Path) -> None:
        """Testa exportação XML com eventos."""
        events = [
            {"action": "test1", "timestamp": "2025-11-23T00:00:00Z"},
            {"action": "test2", "timestamp": "2025-11-23T00:01:00Z"},
        ]
        export_file = temp_log_dir / "test_export.xml"

        reporter._export_xml(events, export_file)

        assert export_file.exists()
        # Verify it's valid XML
        content = export_file.read_text()
        assert "<?xml" in content
        assert "<audit_trail>" in content


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""

    @patch("src.audit.compliance_reporter.ComplianceReporter")
    def test_generate_lgpd_report_function(self, mock_reporter_class: Mock) -> None:
        """Testa função de conveniência generate_lgpd_report."""
        mock_instance = Mock()
        mock_instance.generate_lgpd_report = Mock(return_value={"standard": "LGPD"})
        mock_reporter_class.return_value = mock_instance

        result = generate_lgpd_report()

        mock_reporter_class.assert_called_once()
        mock_instance.generate_lgpd_report.assert_called_once()
        assert result["standard"] == "LGPD"

    @patch("src.audit.compliance_reporter.ComplianceReporter")
    def test_generate_gdpr_report_function(self, mock_reporter_class: Mock) -> None:
        """Testa função de conveniência generate_gdpr_report."""
        mock_instance = Mock()
        mock_instance.generate_gdpr_report = Mock(return_value={"standard": "GDPR"})
        mock_reporter_class.return_value = mock_instance

        result = generate_gdpr_report()

        mock_instance.generate_gdpr_report.assert_called_once()
        assert result["standard"] == "GDPR"

    @patch("src.audit.compliance_reporter.ComplianceReporter")
    def test_export_audit_trail_function(self, mock_reporter_class: Mock) -> None:
        """Testa função de conveniência export_audit_trail."""
        mock_instance = Mock()
        mock_instance.export_audit_trail = Mock(return_value="/path/to/export.json")
        mock_reporter_class.return_value = mock_instance

        result = export_audit_trail(format="json")

        mock_instance.export_audit_trail.assert_called_with(format="json")
        assert result == "/path/to/export.json"

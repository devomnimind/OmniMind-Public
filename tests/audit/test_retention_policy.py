"""
Testes para src/audit/retention_policy.py.

Testa políticas de retenção, arquivamento e purge de dados.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from src.audit.retention_policy import (
    RetentionPolicyManager,
    RetentionPeriod,
    DataCategory,
    set_retention_period,
    archive_old_data,
    generate_retention_report,
)
from src.audit.immutable_audit import ImmutableAuditSystem


class TestRetentionPeriod:
    """Testes para enum RetentionPeriod."""

    def test_retention_period_values(self) -> None:
        """Testa valores do enum RetentionPeriod."""
        assert RetentionPeriod.DAYS_30.value == 30
        assert RetentionPeriod.DAYS_90.value == 90
        assert RetentionPeriod.DAYS_180.value == 180
        assert RetentionPeriod.DAYS_365.value == 365
        assert RetentionPeriod.DAYS_730.value == 730
        assert RetentionPeriod.DAYS_1825.value == 1825
        assert RetentionPeriod.DAYS_2555.value == 2555
        assert RetentionPeriod.PERMANENT.value == -1


class TestDataCategory:
    """Testes para enum DataCategory."""

    def test_data_category_values(self) -> None:
        """Testa valores do enum DataCategory."""
        assert DataCategory.AUDIT_LOGS.value == "audit_logs"
        assert DataCategory.SECURITY_EVENTS.value == "security_events"
        assert DataCategory.USER_DATA.value == "user_data"
        assert DataCategory.SYSTEM_METRICS.value == "system_metrics"
        assert DataCategory.COMPLIANCE_REPORTS.value == "compliance_reports"
        assert DataCategory.BACKUP_DATA.value == "backup_data"


class TestRetentionPolicyManager:
    """Testes para RetentionPolicyManager."""

    @pytest.fixture
    def temp_log_dir(self) -> Generator[Path, None, None]:
        """Cria diretório temporário para logs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    @pytest.fixture
    def audit_system(self, temp_log_dir: Path) -> ImmutableAuditSystem:
        """Cria sistema de auditoria."""
        return ImmutableAuditSystem(log_dir=str(temp_log_dir))

    @pytest.fixture
    def manager(self, audit_system: ImmutableAuditSystem) -> RetentionPolicyManager:
        """Cria gerenciador de política de retenção."""
        return RetentionPolicyManager(audit_system=audit_system)

    def test_initialization(self, manager: RetentionPolicyManager) -> None:
        """Testa inicialização do gerenciador."""
        assert manager is not None
        assert manager.audit_system is not None
        assert manager.config_file is not None
        assert manager.archive_dir.exists()

    def test_default_config_created(self, manager: RetentionPolicyManager) -> None:
        """Testa criação de configuração padrão."""
        assert manager.config_file.exists()
        assert "retention_policies" in manager.config
        assert "archive_enabled" in manager.config

    def test_default_retention_periods(self, manager: RetentionPolicyManager) -> None:
        """Testa períodos de retenção padrão."""
        policies = manager.config["retention_policies"]

        assert policies[DataCategory.AUDIT_LOGS.value] == RetentionPeriod.DAYS_2555.value
        assert (
            policies[DataCategory.SECURITY_EVENTS.value]
            == RetentionPeriod.DAYS_1825.value
        )
        assert policies[DataCategory.USER_DATA.value] == RetentionPeriod.DAYS_365.value

    def test_set_retention_period(self, manager: RetentionPolicyManager) -> None:
        """Testa definição de período de retenção."""
        manager.set_retention_period(DataCategory.USER_DATA, RetentionPeriod.DAYS_90)

        period = manager.get_retention_period(DataCategory.USER_DATA)
        assert period == 90

    def test_set_retention_period_invalid(self, manager: RetentionPolicyManager) -> None:
        """Testa que período inválido levanta ValueError."""
        # Create invalid period manually
        class InvalidPeriod:
            value = -5

        with pytest.raises(ValueError, match="Invalid retention period"):
            manager.set_retention_period(
                DataCategory.USER_DATA, InvalidPeriod()  # type: ignore
            )

    def test_set_retention_period_logs_action(
        self, manager: RetentionPolicyManager
    ) -> None:
        """Testa que mudança de política é logada."""
        initial_events = manager.audit_system.get_audit_summary()["total_events"]

        manager.set_retention_period(DataCategory.BACKUP_DATA, RetentionPeriod.DAYS_180)

        final_events = manager.audit_system.get_audit_summary()["total_events"]
        assert final_events > initial_events

    def test_get_retention_period(self, manager: RetentionPolicyManager) -> None:
        """Testa obtenção de período de retenção."""
        period = manager.get_retention_period(DataCategory.AUDIT_LOGS)
        assert period == RetentionPeriod.DAYS_2555.value

    def test_get_retention_period_default(self, manager: RetentionPolicyManager) -> None:
        """Testa período padrão para categoria não configurada."""
        # Remove category from config
        if "unknown_category" in manager.config["retention_policies"]:
            del manager.config["retention_policies"]["unknown_category"]

        # Create a fake category that's not in config
        class UnknownCategory:
            value = "unknown_category"

        period = manager.get_retention_period(UnknownCategory())  # type: ignore
        assert period == RetentionPeriod.DAYS_365.value  # Default

    def test_archive_old_data_permanent_retention(
        self, manager: RetentionPolicyManager
    ) -> None:
        """Testa que dados com retenção permanente não são arquivados."""
        manager.set_retention_period(DataCategory.AUDIT_LOGS, RetentionPeriod.PERMANENT)

        result = manager.archive_old_data(DataCategory.AUDIT_LOGS)

        assert result["action"] == "skipped"
        assert "Permanent retention" in result["reason"]

    def test_archive_old_data_dry_run(
        self, manager: RetentionPolicyManager, temp_log_dir: Path
    ) -> None:
        """Testa dry run de arquivamento."""
        # Create old test file
        old_file = temp_log_dir / "audit_chain.log.old"
        old_file.write_text("old data")

        result = manager.archive_old_data(DataCategory.AUDIT_LOGS, dry_run=True)

        assert result["action"] == "dry_run"
        assert "files_to_archive" in result
        assert "estimated_size" in result

    def test_find_files_to_archive(
        self, manager: RetentionPolicyManager, temp_log_dir: Path
    ) -> None:
        """Testa busca de arquivos para arquivar."""
        # Create test file
        test_file = temp_log_dir / "audit_chain.log"
        test_file.write_text("test data")

        # Set modification time to old date
        old_time = (datetime.now(timezone.utc) - timedelta(days=3000)).timestamp()
        import os

        os.utime(test_file, (old_time, old_time))

        cutoff = datetime.now(timezone.utc) - timedelta(days=2000)
        files = manager._find_files_to_archive(DataCategory.AUDIT_LOGS, cutoff)

        assert len(files) > 0
        assert test_file in files

    def test_purge_old_data_permanent_retention(
        self, manager: RetentionPolicyManager
    ) -> None:
        """Testa que dados permanentes não são purgados."""
        manager.set_retention_period(DataCategory.AUDIT_LOGS, RetentionPeriod.PERMANENT)

        result = manager.purge_old_data(DataCategory.AUDIT_LOGS, confirm=True)

        assert result["action"] == "skipped"
        assert "Permanent retention" in result["reason"]

    def test_purge_old_data_without_confirmation(
        self, manager: RetentionPolicyManager
    ) -> None:
        """Testa que purge sem confirmação é bloqueado."""
        result = manager.purge_old_data(DataCategory.USER_DATA, confirm=False)

        assert result["action"] == "blocked"
        assert "confirmation required" in result["reason"]

    def test_purge_old_data_dry_run(
        self, manager: RetentionPolicyManager, temp_log_dir: Path
    ) -> None:
        """Testa dry run de purge."""
        result = manager.purge_old_data(DataCategory.AUDIT_LOGS, dry_run=True)

        assert result["action"] == "dry_run"
        assert "files_to_purge" in result
        assert "estimated_size" in result

    def test_cleanup_archives(
        self, manager: RetentionPolicyManager, temp_log_dir: Path
    ) -> None:
        """Testa limpeza de arquivos antigos."""
        # Create old archive
        old_archive = manager.archive_dir / "old_archive.tar.gz"
        old_archive.write_text("old archive data")

        # Set modification time to very old
        old_time = (datetime.now(timezone.utc) - timedelta(days=3000)).timestamp()
        import os

        os.utime(old_archive, (old_time, old_time))

        result = manager.cleanup_archives(max_age_days=2000)

        assert "archives_removed" in result
        assert "space_freed" in result

    def test_generate_retention_report(self, manager: RetentionPolicyManager) -> None:
        """Testa geração de relatório de retenção."""
        report = manager.generate_retention_report()

        assert "generated_at" in report
        assert "policies" in report
        assert "statistics" in report

        # Verify policies section
        policies = report["policies"]
        assert DataCategory.AUDIT_LOGS.value in policies
        assert DataCategory.SECURITY_EVENTS.value in policies

        # Verify statistics
        stats = report["statistics"]
        assert "total_archives" in stats
        assert "total_archive_size" in stats
        assert "archive_directory" in stats

    def test_report_includes_cutoff_dates(self, manager: RetentionPolicyManager) -> None:
        """Testa que relatório inclui datas de corte."""
        report = manager.generate_retention_report()

        for category, policy_info in report["policies"].items():
            assert "retention_period_days" in policy_info
            assert "cutoff_date" in policy_info

    def test_create_compressed_archive(
        self, manager: RetentionPolicyManager, temp_log_dir: Path
    ) -> None:
        """Testa criação de arquivo comprimido."""
        # Create test files
        test_files = []
        for i in range(3):
            f = temp_log_dir / f"test_file_{i}.txt"
            f.write_text(f"Test data {i}")
            test_files.append(f)

        archive_path = manager.archive_dir / "test_archive.tar.gz"

        size = manager._create_compressed_archive(test_files, archive_path)

        assert archive_path.exists()
        assert size > 0
        assert archive_path.stat().st_size == size


class TestConvenienceFunctions:
    """Testes para funções de conveniência."""

    @pytest.fixture
    def temp_log_dir(self) -> Generator[Path, None, None]:
        """Cria diretório temporário para logs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_set_retention_period_function(self, temp_log_dir: Path) -> None:
        """Testa função global set_retention_period."""
        with patch("src.audit.retention_policy.get_audit_system") as mock_get_audit:
            mock_audit = MagicMock()
            mock_audit.log_dir = temp_log_dir
            mock_get_audit.return_value = mock_audit

            set_retention_period(DataCategory.USER_DATA, RetentionPeriod.DAYS_90)

            # Function should create manager and call method
            # Just verify no exception was raised

    def test_archive_old_data_function(self, temp_log_dir: Path) -> None:
        """Testa função global archive_old_data."""
        with patch("src.audit.retention_policy.get_audit_system") as mock_get_audit:
            mock_audit = MagicMock()
            mock_audit.log_dir = temp_log_dir
            mock_get_audit.return_value = mock_audit

            result = archive_old_data(DataCategory.AUDIT_LOGS, dry_run=True)

            assert isinstance(result, dict)

    def test_generate_retention_report_function(self, temp_log_dir: Path) -> None:
        """Testa função global generate_retention_report."""
        with patch("src.audit.retention_policy.get_audit_system") as mock_get_audit:
            mock_audit = MagicMock()
            mock_audit.log_dir = temp_log_dir
            mock_get_audit.return_value = mock_audit

            result = generate_retention_report()

            assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

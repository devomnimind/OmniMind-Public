#!/usr/bin/env python3
"""
Data Retention Policy Module for OmniMind
Implements configurable retention periods, automatic archival, and purge mechanisms.

Compliance: LGPD Art. 15, GDPR Art. 5.1.e (Storage Limitation)
"""

import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from .immutable_audit import ImmutableAuditSystem, get_audit_system


class RetentionPeriod(Enum):
    """Standard retention periods."""

    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_180 = 180
    DAYS_365 = 365
    DAYS_730 = 730  # 2 years
    DAYS_1825 = 1825  # 5 years
    DAYS_2555 = 2555  # 7 years
    PERMANENT = -1


class DataCategory(Enum):
    """Data categories with different retention requirements."""

    AUDIT_LOGS = "audit_logs"
    SECURITY_EVENTS = "security_events"
    USER_DATA = "user_data"
    SYSTEM_METRICS = "system_metrics"
    COMPLIANCE_REPORTS = "compliance_reports"
    BACKUP_DATA = "backup_data"


class RetentionPolicyManager:
    """
    Manages data retention policies, archival, and purging.

    Features:
    - Configurable retention periods per data category
    - Automatic archival of old data
    - Secure data purging
    - Compliance reporting
    """

    def __init__(
        self,
        audit_system: Optional[ImmutableAuditSystem] = None,
        config_file: Optional[Path] = None,
    ):
        """
        Initialize retention policy manager.

        Args:
            audit_system: Optional audit system instance
            config_file: Optional path to retention policy configuration
        """
        self.audit_system = audit_system or get_audit_system()
        self.config_file = config_file or (
            self.audit_system.log_dir / "retention_policy.json"
        )
        self.archive_dir = self.audit_system.log_dir / "archives"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Load or create default configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load retention policy configuration."""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                config: Dict[str, Any] = json.load(f)
                return config

        # Default configuration
        default_config = {
            "retention_policies": {
                DataCategory.AUDIT_LOGS.value: RetentionPeriod.DAYS_2555.value,
                DataCategory.SECURITY_EVENTS.value: RetentionPeriod.DAYS_1825.value,
                DataCategory.USER_DATA.value: RetentionPeriod.DAYS_365.value,
                DataCategory.SYSTEM_METRICS.value: RetentionPeriod.DAYS_90.value,
                DataCategory.COMPLIANCE_REPORTS.value: RetentionPeriod.DAYS_2555.value,
                DataCategory.BACKUP_DATA.value: RetentionPeriod.DAYS_180.value,
            },
            "archive_enabled": True,
            "compress_archives": True,
            "auto_purge_enabled": False,  # Requires explicit enable for safety
            "purge_verification_required": True,
        }

        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save retention policy configuration."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def set_retention_period(
        self, category: DataCategory, period: RetentionPeriod
    ) -> None:
        """
        Set retention period for a data category.

        Args:
            category: Data category
            period: Retention period

        Raises:
            ValueError: If period is invalid
        """
        if period.value < -1:
            raise ValueError("Invalid retention period")

        self.config["retention_policies"][category.value] = period.value
        self._save_config(self.config)

        # Log policy change
        self.audit_system.log_action(
            "retention_policy_changed",
            {
                "category": category.value,
                "new_period_days": period.value,
                "changed_by": "system",
            },
            category="compliance",
        )

    def get_retention_period(self, category: DataCategory) -> int:
        """Get retention period for a data category in days."""
        period: int = self.config["retention_policies"].get(
            category.value, RetentionPeriod.DAYS_365.value
        )
        return period

    def archive_old_data(
        self, category: DataCategory, dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Archive data that has passed retention period.

        Args:
            category: Data category to archive
            dry_run: If True, only report what would be archived

        Returns:
            Dict with archival results
        """
        retention_days = self.get_retention_period(category)
        if retention_days == RetentionPeriod.PERMANENT.value:
            return {
                "category": category.value,
                "action": "skipped",
                "reason": "Permanent retention policy",
            }

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        archived_count = 0
        archived_size = 0

        # Find files to archive based on category
        files_to_archive = self._find_files_to_archive(category, cutoff_date)

        if dry_run:
            return {
                "category": category.value,
                "action": "dry_run",
                "files_to_archive": len(files_to_archive),
                "estimated_size": sum(f.stat().st_size for f in files_to_archive),
            }

        # Archive files
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_name = f"{category.value}_{timestamp}"

        if self.config.get("compress_archives", True):
            archive_path = self.archive_dir / f"{archive_name}.tar.gz"
            archived_size = self._create_compressed_archive(
                files_to_archive, archive_path
            )
        else:
            archive_path = self.archive_dir / archive_name
            archive_path.mkdir(parents=True, exist_ok=True)
            for file in files_to_archive:
                shutil.copy2(file, archive_path / file.name)
                archived_size += file.stat().st_size

        archived_count = len(files_to_archive)

        # Log archival
        self.audit_system.log_action(
            "data_archived",
            {
                "category": category.value,
                "files_archived": archived_count,
                "archive_size_bytes": archived_size,
                "archive_path": str(archive_path),
                "cutoff_date": cutoff_date.isoformat(),
            },
            category="compliance",
        )

        return {
            "category": category.value,
            "action": "archived",
            "files_archived": archived_count,
            "archive_size": archived_size,
            "archive_path": str(archive_path),
        }

    def purge_old_data(
        self, category: DataCategory, confirm: bool = False, dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Permanently purge data past retention period.

        CRITICAL: This operation is irreversible!

        Args:
            category: Data category to purge
            confirm: Must be True to actually purge (safety check)
            dry_run: If True, only report what would be purged

        Returns:
            Dict with purge results
        """
        if not self.config.get("auto_purge_enabled", False) and not confirm:
            return {
                "category": category.value,
                "action": "blocked",
                "reason": "Auto-purge disabled or confirmation required",
            }

        retention_days = self.get_retention_period(category)
        if retention_days == RetentionPeriod.PERMANENT.value:
            return {
                "category": category.value,
                "action": "skipped",
                "reason": "Permanent retention policy",
            }

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        files_to_purge = self._find_files_to_archive(category, cutoff_date)

        if dry_run:
            return {
                "category": category.value,
                "action": "dry_run",
                "files_to_purge": len(files_to_purge),
                "estimated_size": sum(f.stat().st_size for f in files_to_purge),
            }

        # Purge files
        purged_count = 0
        purged_size = 0

        for file in files_to_purge:
            try:
                file_size = file.stat().st_size
                file.unlink()
                purged_count += 1
                purged_size += file_size
            except Exception as e:
                # Log failure but continue
                self.audit_system.log_action(
                    "purge_failed",
                    {"file": str(file), "error": str(e)},
                    category="security",
                )

        # Log purge operation
        self.audit_system.log_action(
            "data_purged",
            {
                "category": category.value,
                "files_purged": purged_count,
                "total_size_bytes": purged_size,
                "cutoff_date": cutoff_date.isoformat(),
                "confirmed": confirm,
            },
            category="compliance",
        )

        return {
            "category": category.value,
            "action": "purged",
            "files_purged": purged_count,
            "total_size": purged_size,
        }

    def cleanup_archives(self, max_age_days: int = 2555) -> Dict[str, Any]:
        """
        Clean up old archives (archives older than max_age_days).

        Args:
            max_age_days: Maximum age of archives to keep (default: 7 years)

        Returns:
            Dict with cleanup results
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        archives_removed = 0
        space_freed = 0

        for archive in self.archive_dir.iterdir():
            if archive.is_file():
                archive_time = datetime.fromtimestamp(
                    archive.stat().st_mtime, tz=timezone.utc
                )
                if archive_time < cutoff_date:
                    size = archive.stat().st_size
                    archive.unlink()
                    archives_removed += 1
                    space_freed += size

        # Log cleanup
        self.audit_system.log_action(
            "archives_cleaned",
            {
                "archives_removed": archives_removed,
                "space_freed_bytes": space_freed,
                "max_age_days": max_age_days,
            },
            category="system",
        )

        return {
            "archives_removed": archives_removed,
            "space_freed": space_freed,
        }

    def generate_retention_report(self) -> Dict[str, Any]:
        """
        Generate retention policy compliance report.

        Returns:
            Dict containing retention report
        """
        report: Dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policies": {},
            "statistics": {},
        }

        # Report policies
        for category, period_days in self.config["retention_policies"].items():
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=period_days)
            category_enum = DataCategory(category)
            files = self._find_files_to_archive(category_enum, cutoff_date)

            report["policies"][category] = {
                "retention_period_days": period_days,
                "cutoff_date": (
                    cutoff_date.isoformat() if period_days > 0 else "permanent"
                ),
                "files_past_retention": len(files),
                "size_past_retention": sum(f.stat().st_size for f in files),
            }

        # Overall statistics
        total_archives = len(list(self.archive_dir.iterdir()))
        total_archive_size = sum(
            f.stat().st_size for f in self.archive_dir.iterdir() if f.is_file()
        )

        report["statistics"] = {
            "total_archives": total_archives,
            "total_archive_size": total_archive_size,
            "archive_directory": str(self.archive_dir),
        }

        return report

    def _find_files_to_archive(
        self, category: DataCategory, cutoff_date: datetime
    ) -> List[Path]:
        """Find files older than cutoff date for given category."""
        files_to_archive = []

        # Map categories to file patterns
        file_patterns = {
            DataCategory.AUDIT_LOGS: ["audit_chain.log*", "hash_chain.json*"],
            DataCategory.SECURITY_EVENTS: ["security_events.log*"],
            DataCategory.COMPLIANCE_REPORTS: ["compliance_reports/*"],
            DataCategory.SYSTEM_METRICS: ["metrics/*.json"],
        }

        patterns = file_patterns.get(category, [])
        for pattern in patterns:
            for file_path in self.audit_system.log_dir.glob(pattern):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(
                        file_path.stat().st_mtime, tz=timezone.utc
                    )
                    if file_time < cutoff_date:
                        files_to_archive.append(file_path)

        return files_to_archive

    def _create_compressed_archive(self, files: List[Path], archive_path: Path) -> int:
        """Create compressed tar.gz archive of files."""
        import tarfile

        total_size = 0
        with tarfile.open(archive_path, "w:gz") as tar:
            for file in files:
                tar.add(file, arcname=file.name)
                total_size += file.stat().st_size

        return archive_path.stat().st_size


# Convenience functions


def set_retention_period(category: DataCategory, period: RetentionPeriod) -> None:
    """Set retention period for a category."""
    manager = RetentionPolicyManager()
    manager.set_retention_period(category, period)


def archive_old_data(category: DataCategory, dry_run: bool = False) -> Dict[str, Any]:
    """Archive old data for category."""
    manager = RetentionPolicyManager()
    return manager.archive_old_data(category, dry_run=dry_run)


def generate_retention_report() -> Dict[str, Any]:
    """Generate retention compliance report."""
    manager = RetentionPolicyManager()
    return manager.generate_retention_report()

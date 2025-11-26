#!/usr/bin/env python3
"""
Integrity Validator - File and System Integrity Validation
Validates file integrity, detects unauthorized modifications, and generates compliance reports.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.audit.immutable_audit import get_audit_system


class IntegrityStatus(Enum):
    """File integrity status."""

    INTACT = "intact"
    MODIFIED = "modified"
    MISSING = "missing"
    CORRUPTED = "corrupted"
    UNKNOWN = "unknown"


class ValidationScope(Enum):
    """Scope of integrity validation."""

    SINGLE_FILE = "single_file"
    DIRECTORY = "directory"
    SYSTEM_CRITICAL = "system_critical"
    APPLICATION = "application"
    FULL_SYSTEM = "full_system"


@dataclass
class FileIntegrityRecord:
    """Record of file integrity information."""

    path: str
    expected_hash: str
    current_hash: str
    status: IntegrityStatus
    size_expected: Optional[int] = None
    size_current: Optional[int] = None
    mtime_expected: Optional[float] = None
    mtime_current: Optional[float] = None
    permissions_expected: Optional[int] = None
    permissions_current: Optional[int] = None
    last_checked: str = ""
    evidence: List[str] = field(default_factory=list)


@dataclass
class IntegrityReport:
    """Comprehensive integrity validation report."""

    timestamp: str
    scope: ValidationScope
    target_path: str
    total_files: int
    intact_files: int
    modified_files: int
    missing_files: int
    corrupted_files: int
    unknown_files: int
    compliance_score: float
    critical_issues: List[str]
    recommendations: List[str]
    file_records: List[FileIntegrityRecord] = field(default_factory=list)
    execution_time: float = 0.0


class IntegrityValidator:
    """
    Comprehensive file and system integrity validator.

    Features:
    - File hash validation
    - Directory tree scanning
    - Critical system file monitoring
    - Compliance reporting
    - Automated baseline management
    """

    def __init__(
        self,
        audit_system: Optional[Any] = None,
        baseline_dir: Optional[str] = None,
        log_dir: Optional[str] = None,
    ):
        """
        Initialize Integrity Validator.

        Args:
            audit_system: Audit system instance
            baseline_dir: Directory for integrity baselines
            log_dir: Directory for integrity logs
        """
        self.audit_system = audit_system or get_audit_system()
        self.baseline_dir = Path(baseline_dir or "data/integrity_baselines")
        self.log_dir = Path(log_dir or "logs/integrity")

        # Create directories
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Logger
        self.logger = logging.getLogger("integrity_validator")
        self.logger.setLevel(logging.INFO)

        # Critical system files to monitor
        self.critical_system_files = {
            "/etc/passwd",
            "/etc/shadow",
            "/etc/sudoers",
            "/etc/ssh/sshd_config",
            "/etc/hosts",
            "/etc/resolv.conf",
            "/etc/fstab",
            "/boot/grub/grub.cfg",
        }

        # Application critical files
        self.application_critical_files = {
            "requirements.txt",
            "pyproject.toml",
            "setup.py",
            "config/omnimind.yaml",
            "config/security.yaml",
            "config/ethics.yaml",
            "src/__init__.py",
            "src/main.py",
        }

        # File extensions to exclude from hashing
        self.exclude_extensions = {
            ".log",
            ".tmp",
            ".swp",
            ".bak",
            ".old",
            ".pyc",
            ".pyo",
            "__pycache__",
            ".git",
        }

        # Hash algorithm
        self.hash_algorithm = hashlib.sha256

    def create_baseline(
        self,
        target_path: str,
        scope: ValidationScope = ValidationScope.DIRECTORY,
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Create integrity baseline for target path.

        Args:
            target_path: Path to create baseline for
            scope: Scope of baseline creation
            include_metadata: Whether to include file metadata

        Returns:
            Baseline data dictionary
        """
        self.logger.info(f"Creating integrity baseline for {target_path}")

        start_time = time.time()
        baseline_data: Dict[str, Any] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "target_path": target_path,
            "scope": scope.value,
            "files": {},
            "metadata": {
                "total_files": 0,
                "total_size": 0,
                "creation_time": start_time,
            },
        }

        try:
            path = Path(target_path)

            if scope == ValidationScope.SINGLE_FILE:
                if path.is_file():
                    file_info = self._calculate_file_integrity(path, include_metadata)
                    baseline_data["files"][str(path)] = file_info
                    baseline_data["metadata"]["total_files"] = 1
                    baseline_data["metadata"]["total_size"] = file_info.get("size", 0)

            elif scope in [ValidationScope.DIRECTORY, ValidationScope.APPLICATION]:
                files_processed = 0
                total_size = 0

                for file_path in self._collect_files(path, scope):
                    try:
                        file_info = self._calculate_file_integrity(file_path, include_metadata)
                        baseline_data["files"][str(file_path)] = file_info
                        files_processed += 1
                        total_size += file_info.get("size", 0)
                    except Exception as e:
                        self.logger.warning(f"Failed to process {file_path}: {e}")

                baseline_data["metadata"]["total_files"] = files_processed
                baseline_data["metadata"]["total_size"] = total_size

            elif scope == ValidationScope.SYSTEM_CRITICAL:
                for file_path_str in self.critical_system_files:
                    file_path = Path(file_path_str)
                    if file_path.exists():
                        try:
                            file_info = self._calculate_file_integrity(file_path, include_metadata)
                            baseline_data["files"][file_path_str] = file_info
                            baseline_data["metadata"]["total_files"] += 1
                            baseline_data["metadata"]["total_size"] += file_info.get("size", 0)
                        except Exception as e:
                            self.logger.warning(f"Failed to process {file_path}: {e}")

            elif scope == ValidationScope.FULL_SYSTEM:
                # Combine critical system and application files
                all_files = self.critical_system_files | set(
                    str(Path.cwd() / f) for f in self.application_critical_files
                )

                for file_path_str in all_files:
                    file_path = Path(file_path_str)
                    if file_path.exists():
                        try:
                            file_info = self._calculate_file_integrity(file_path, include_metadata)
                            baseline_data["files"][file_path_str] = file_info
                            baseline_data["metadata"]["total_files"] += 1
                            baseline_data["metadata"]["total_size"] += file_info.get("size", 0)
                        except Exception as e:
                            self.logger.warning(f"Failed to process {file_path}: {e}")

            # Save baseline
            baseline_file = self._get_baseline_filename(target_path, scope)
            with open(baseline_file, "w", encoding="utf-8") as f:
                json.dump(baseline_data, f, indent=2, ensure_ascii=False)

            # Log to audit
            self.audit_system.log_action(
                "integrity_baseline_created",
                {
                    "target_path": target_path,
                    "scope": scope.value,
                    "files_count": baseline_data["metadata"]["total_files"],
                    "total_size": baseline_data["metadata"]["total_size"],
                    "baseline_file": str(baseline_file),
                },
                category="security",
            )

            self.logger.info(f"Baseline created: {baseline_data['metadata']['total_files']} files")
            return baseline_data

        except Exception as e:
            self.logger.error(f"Failed to create baseline: {e}")
            raise

    def validate_integrity(
        self,
        target_path: str,
        scope: ValidationScope = ValidationScope.DIRECTORY,
        baseline_file: Optional[str] = None,
    ) -> IntegrityReport:
        """
        Validate integrity against baseline.

        Args:
            target_path: Path to validate
            scope: Scope of validation
            baseline_file: Specific baseline file to use

        Returns:
            IntegrityReport with validation results
        """
        self.logger.info(f"Validating integrity for {target_path}")

        start_time: float = time.time()

        # Load baseline
        if baseline_file is None:
            baseline_file_path = self._get_baseline_filename(target_path, scope)
            baseline_file = str(baseline_file_path)

        try:
            with open(baseline_file, "r", encoding="utf-8") as f:
                baseline_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Baseline file not found: {baseline_file}")

        # Initialize report
        report = IntegrityReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            scope=scope,
            target_path=target_path,
            total_files=baseline_data["metadata"]["total_files"],
            intact_files=0,
            modified_files=0,
            missing_files=0,
            corrupted_files=0,
            unknown_files=0,
            compliance_score=0.0,
            critical_issues=[],
            recommendations=[],
        )

        # Validate each file
        for file_path_str, expected_info in baseline_data["files"].items():
            file_path = Path(file_path_str)
            record = self._validate_single_file(file_path, expected_info)
            report.file_records.append(record)

            # Update counters
            if record.status == IntegrityStatus.INTACT:
                report.intact_files += 1
            elif record.status == IntegrityStatus.MODIFIED:
                report.modified_files += 1
            elif record.status == IntegrityStatus.MISSING:
                report.missing_files += 1
            elif record.status == IntegrityStatus.CORRUPTED:
                report.corrupted_files += 1
            else:
                report.unknown_files += 1

        # Calculate compliance score
        report.compliance_score = (
            (report.intact_files / report.total_files) * 100 if report.total_files > 0 else 0
        )

        # Generate critical issues and recommendations
        report.critical_issues, report.recommendations = self._analyze_validation_results(report)

        # Set execution time
        report.execution_time = time.time() - start_time

        # Log to audit
        self.audit_system.log_action(
            "integrity_validation_completed",
            {
                "target_path": target_path,
                "scope": scope.value,
                "total_files": report.total_files,
                "intact_files": report.intact_files,
                "modified_files": report.modified_files,
                "missing_files": report.missing_files,
                "corrupted_files": report.corrupted_files,
                "compliance_score": report.compliance_score,
                "critical_issues_count": len(report.critical_issues),
                "execution_time": report.execution_time,
            },
            category="security",
        )

        # Save report
        self._save_validation_report(report)

        self.logger.info(f"Validation completed: {report.compliance_score:.1f}% compliance")
        return report

    def validate_file_integrity(self, file_path: str) -> Dict[str, Any]:
        """
        Validate single file integrity using extended attributes.

        Args:
            file_path: Path to file to validate

        Returns:
            Validation result dictionary
        """
        return self.audit_system.verify_file_integrity(file_path)

    def get_validation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get history of integrity validations.

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of validation reports
        """
        reports: List[Dict[str, Any]] = []

        try:
            for report_file in sorted(self.log_dir.glob("integrity_report_*.json"), reverse=True):
                if len(reports) >= limit:
                    break

                try:
                    with open(report_file, "r", encoding="utf-8") as f:
                        report_data = json.load(f)
                        reports.append(report_data)
                except Exception as e:
                    self.logger.warning(f"Failed to load report {report_file}: {e}")

        except Exception as e:
            self.logger.error(f"Failed to get validation history: {e}")

        return reports

    def _calculate_file_integrity(
        self, file_path: Path, include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Calculate integrity information for a file."""
        try:
            stat_info = file_path.stat()

            # Calculate hash
            with open(file_path, "rb") as f:
                file_hash = self.hash_algorithm(f.read()).hexdigest()

            file_info = {
                "hash": file_hash,
                "size": stat_info.st_size,
                "mtime": stat_info.st_mtime,
                "permissions": stat_info.st_mode,
            }

            if include_metadata:
                file_info.update(
                    {
                        "ctime": stat_info.st_ctime,
                        "uid": stat_info.st_uid,
                        "gid": stat_info.st_gid,
                        "inode": stat_info.st_ino,
                    }
                )

            return file_info

        except Exception as e:
            self.logger.error(f"Failed to calculate integrity for {file_path}: {e}")
            return {
                "error": str(e),
                "size": 0,
                "mtime": 0,
                "permissions": 0,
            }

    def _validate_single_file(
        self, file_path: Path, expected_info: Dict[str, Any]
    ) -> FileIntegrityRecord:
        """Validate single file against expected information."""
        record = FileIntegrityRecord(
            path=str(file_path),
            expected_hash=expected_info.get("hash", ""),
            current_hash="",
            status=IntegrityStatus.UNKNOWN,
        )

        try:
            if not file_path.exists():
                record.status = IntegrityStatus.MISSING
                record.evidence.append("File does not exist")
                return record

            # Calculate current integrity
            current_info = self._calculate_file_integrity(file_path, include_metadata=True)
            record.current_hash = current_info.get("hash", "")
            record.size_current = current_info.get("size")
            record.mtime_current = current_info.get("mtime")
            record.permissions_current = current_info.get("permissions")

            # Set expected values
            record.size_expected = expected_info.get("size")
            record.mtime_expected = expected_info.get("mtime")
            record.permissions_expected = expected_info.get("permissions")

            # Check hash
            if record.current_hash != record.expected_hash:
                record.status = IntegrityStatus.MODIFIED
                record.evidence.append(
                    f"Hash mismatch: expected {record.expected_hash[:16]}..., "
                    f"got {record.current_hash[:16]}..."
                )
            else:
                record.status = IntegrityStatus.INTACT

            # Additional checks
            if record.size_current != record.size_expected:
                record.evidence.append(
                    f"Size changed: {record.size_expected} -> {record.size_current}"
                )

            if (
                record.mtime_current is not None
                and record.mtime_expected is not None
                and abs(record.mtime_current - record.mtime_expected) > 1
            ):  # Allow 1 second tolerance
                record.evidence.append(
                    f"Modification time changed: {record.mtime_expected} -> {record.mtime_current}"
                )

            if record.permissions_current != record.permissions_expected:
                if (
                    record.permissions_expected is not None
                    and record.permissions_current is not None
                ):
                    record.evidence.append(
                        f"Permissions changed: "
                        f"{oct(record.permissions_expected)} -> "
                        f"{oct(record.permissions_current)}"
                    )

            record.last_checked = datetime.now(timezone.utc).isoformat()

        except Exception as e:
            record.status = IntegrityStatus.CORRUPTED
            record.evidence.append(f"Validation error: {str(e)}")

        return record

    def _collect_files(self, root_path: Path, scope: ValidationScope) -> List[Path]:
        """Collect files for baseline creation."""
        files = []

        try:
            if scope == ValidationScope.APPLICATION:
                # Include Python files, configs, but exclude logs, cache, etc.
                for pattern in [
                    "**/*.py",
                    "**/*.yaml",
                    "**/*.yml",
                    "**/*.json",
                    "**/*.toml",
                    "**/*.md",
                ]:
                    for file_path in root_path.glob(pattern):
                        if file_path.is_file() and not self._should_exclude_file(file_path):
                            files.append(file_path)
            else:
                # Include all files except excluded ones
                for file_path in root_path.rglob("*"):
                    if file_path.is_file() and not self._should_exclude_file(file_path):
                        files.append(file_path)

        except Exception as e:
            self.logger.error(f"Failed to collect files from {root_path}: {e}")

        return files

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from integrity checking."""
        # Check extensions
        if file_path.suffix.lower() in self.exclude_extensions:
            return True

        # Check directory names
        for part in file_path.parts:
            if part in self.exclude_extensions:
                return True

        # Check if it's a hidden file/directory
        if any(part.startswith(".") for part in file_path.parts):
            return True

        return False

    def _get_baseline_filename(self, target_path: str, scope: ValidationScope) -> Path:
        """Generate baseline filename."""
        # Sanitize target path for filename
        safe_name = "".join(
            c for c in target_path.replace("/", "_").replace("\\", "_") if c.isalnum() or c in "_-"
        ).strip("_")
        if not safe_name:
            safe_name = "root"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"baseline_{safe_name}_{scope.value}_{timestamp}.json"

        return self.baseline_dir / filename

    def _analyze_validation_results(self, report: IntegrityReport) -> Tuple[List[str], List[str]]:
        """Analyze validation results and generate issues/recommendations."""
        critical_issues = []
        recommendations = []

        # Critical issues
        if report.missing_files > 0:
            critical_issues.append(f"{report.missing_files} critical files are missing")

        if report.corrupted_files > 0:
            critical_issues.append(f"{report.corrupted_files} files are corrupted")

        if report.modified_files > report.total_files * 0.1:  # More than 10% modified
            critical_issues.append(f"High number of modified files: {report.modified_files}")

        # Recommendations
        if report.compliance_score < 80:
            recommendations.append("Review and update integrity baseline")
            recommendations.append("Investigate unauthorized file modifications")

        if report.missing_files > 0:
            recommendations.append("Restore missing critical files from backup")

        if report.modified_files > 0:
            recommendations.append("Verify that file modifications are authorized")

        if report.compliance_score >= 95:
            recommendations.append("System integrity is excellent - continue monitoring")
        elif report.compliance_score >= 80:
            recommendations.append("System integrity is good but could be improved")
        else:
            recommendations.append(
                "URGENT: System integrity is compromised - immediate investigation required"
            )

        return critical_issues, recommendations

    def _save_validation_report(self, report: IntegrityReport) -> None:
        """Save validation report to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integrity_report_{timestamp}.json"
            report_file = self.log_dir / filename

            report_data = {
                "timestamp": report.timestamp,
                "scope": report.scope.value,
                "target_path": report.target_path,
                "summary": {
                    "total_files": report.total_files,
                    "intact_files": report.intact_files,
                    "modified_files": report.modified_files,
                    "missing_files": report.missing_files,
                    "corrupted_files": report.corrupted_files,
                    "unknown_files": report.unknown_files,
                    "compliance_score": report.compliance_score,
                },
                "critical_issues": report.critical_issues,
                "recommendations": report.recommendations,
                "execution_time": report.execution_time,
                "file_records": [
                    {
                        "path": record.path,
                        "status": record.status.value,
                        "expected_hash": record.expected_hash,
                        "current_hash": record.current_hash,
                        "evidence": record.evidence,
                    }
                    for record in report.file_records
                ],
            }

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Failed to save validation report: {e}")


# Convenience functions
_integrity_validator: Optional[IntegrityValidator] = None


def get_integrity_validator() -> IntegrityValidator:
    """Get singleton integrity validator instance."""
    global _integrity_validator
    if _integrity_validator is None:
        _integrity_validator = IntegrityValidator()
    return _integrity_validator


def validate_file_integrity(file_path: str) -> Dict[str, Any]:
    """Validate single file integrity."""
    validator = get_integrity_validator()
    return validator.validate_file_integrity(file_path)


def create_integrity_baseline(target_path: str, scope: str = "directory") -> Dict[str, Any]:
    """Create integrity baseline."""
    validator = get_integrity_validator()
    scope_enum = ValidationScope(scope)
    return validator.create_baseline(target_path, scope_enum)


def run_integrity_validation(target_path: str, scope: str = "directory") -> IntegrityReport:
    """Run integrity validation."""
    validator = get_integrity_validator()
    scope_enum = ValidationScope(scope)
    return validator.validate_integrity(target_path, scope_enum)


if __name__ == "__main__":
    # Example usage
    validator = IntegrityValidator()

    # Create baseline for current directory
    print("Creating integrity baseline...")
    baseline = validator.create_baseline(".", ValidationScope.APPLICATION)
    print(f"Baseline created for {baseline['metadata']['total_files']} files")

    # Validate integrity
    print("Validating integrity...")
    report = validator.validate_integrity(".", ValidationScope.APPLICATION)
    print(f"Compliance score: {report.compliance_score:.1f}%")
    print(f"Intact files: {report.intact_files}/{report.total_files}")

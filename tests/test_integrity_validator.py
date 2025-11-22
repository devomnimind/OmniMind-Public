#!/usr/bin/env python3
"""
Tests for Integrity Validator module.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.security.integrity_validator import (
    IntegrityValidator,
    IntegrityStatus,
    ValidationScope,
    FileIntegrityRecord,
    IntegrityReport,
    get_integrity_validator,
    validate_file_integrity,
    create_integrity_baseline,
    run_integrity_validation,
)


class TestIntegrityStatus(unittest.TestCase):
    """Test IntegrityStatus enum."""

    def test_enum_values(self):
        """Test that all expected status values exist."""
        self.assertEqual(IntegrityStatus.INTACT.value, "intact")
        self.assertEqual(IntegrityStatus.MODIFIED.value, "modified")
        self.assertEqual(IntegrityStatus.MISSING.value, "missing")
        self.assertEqual(IntegrityStatus.CORRUPTED.value, "corrupted")
        self.assertEqual(IntegrityStatus.UNKNOWN.value, "unknown")


class TestValidationScope(unittest.TestCase):
    """Test ValidationScope enum."""

    def test_enum_values(self):
        """Test that all expected scope values exist."""
        self.assertEqual(ValidationScope.SINGLE_FILE.value, "single_file")
        self.assertEqual(ValidationScope.DIRECTORY.value, "directory")
        self.assertEqual(ValidationScope.SYSTEM_CRITICAL.value, "system_critical")
        self.assertEqual(ValidationScope.APPLICATION.value, "application")
        self.assertEqual(ValidationScope.FULL_SYSTEM.value, "full_system")


class TestFileIntegrityRecord(unittest.TestCase):
    """Test FileIntegrityRecord dataclass."""

    def test_record_creation(self):
        """Test creating a file integrity record."""
        record = FileIntegrityRecord(
            path="/test/file.txt",
            expected_hash="abc123",
            current_hash="def456",
            status=IntegrityStatus.MODIFIED,
        )

        self.assertEqual(record.path, "/test/file.txt")
        self.assertEqual(record.expected_hash, "abc123")
        self.assertEqual(record.current_hash, "def456")
        self.assertEqual(record.status, IntegrityStatus.MODIFIED)
        self.assertIsNone(record.size_expected)
        self.assertIsNone(record.size_current)
        self.assertEqual(record.evidence, [])


class TestIntegrityReport(unittest.TestCase):
    """Test IntegrityReport dataclass."""

    def test_report_creation(self):
        """Test creating an integrity report."""
        report = IntegrityReport(
            timestamp="2023-01-01T00:00:00Z",
            scope=ValidationScope.DIRECTORY,
            target_path="/test/dir",
            total_files=10,
            intact_files=8,
            modified_files=1,
            missing_files=1,
            corrupted_files=0,
            unknown_files=0,
            compliance_score=80.0,
            critical_issues=["Test issue"],
            recommendations=["Test recommendation"],
        )

        self.assertEqual(report.timestamp, "2023-01-01T00:00:00Z")
        self.assertEqual(report.scope, ValidationScope.DIRECTORY)
        self.assertEqual(report.target_path, "/test/dir")
        self.assertEqual(report.total_files, 10)
        self.assertEqual(report.intact_files, 8)
        self.assertEqual(report.modified_files, 1)
        self.assertEqual(report.missing_files, 1)
        self.assertEqual(report.corrupted_files, 0)
        self.assertEqual(report.unknown_files, 0)
        self.assertEqual(report.compliance_score, 80.0)
        self.assertEqual(report.critical_issues, ["Test issue"])
        self.assertEqual(report.recommendations, ["Test recommendation"])
        self.assertEqual(report.file_records, [])


class TestIntegrityValidator(unittest.TestCase):
    """Test IntegrityValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.mock_audit = MagicMock()
        self.validator = IntegrityValidator(
            audit_system=self.mock_audit,
            baseline_dir=str(self.temp_dir / "baselines"),
            log_dir=str(self.temp_dir / "logs"),
        )

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test IntegrityValidator initialization."""
        self.assertIsNotNone(self.validator.audit_system)
        self.assertEqual(self.validator.baseline_dir.name, "baselines")
        self.assertEqual(self.validator.log_dir.name, "logs")
        self.assertIsNotNone(self.validator.logger)
        self.assertTrue(self.validator.critical_system_files)
        self.assertTrue(self.validator.application_critical_files)
        self.assertTrue(self.validator.exclude_extensions)

    def test_calculate_file_integrity(self):
        """Test calculating file integrity."""
        # Create a test file
        test_file = self.temp_dir / "test.txt"
        test_content = b"Hello, World!"
        test_file.write_bytes(test_content)

        result = self.validator._calculate_file_integrity(
            test_file, include_metadata=True
        )

        self.assertIn("hash", result)
        self.assertIn("size", result)
        self.assertIn("mtime", result)
        self.assertIn("permissions", result)
        self.assertEqual(result["size"], len(test_content))

    def test_calculate_file_integrity_no_metadata(self):
        """Test calculating file integrity without metadata."""
        # Create a test file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        result = self.validator._calculate_file_integrity(
            test_file, include_metadata=False
        )

        self.assertIn("hash", result)
        self.assertIn("size", result)
        self.assertIn("mtime", result)
        self.assertIn("permissions", result)
        self.assertNotIn("ctime", result)
        self.assertNotIn("uid", result)

    def test_calculate_file_integrity_missing_file(self):
        """Test calculating integrity for missing file."""
        missing_file = self.temp_dir / "missing.txt"

        result = self.validator._calculate_file_integrity(missing_file)

        self.assertIn("error", result)
        self.assertEqual(result["size"], 0)

    def test_validate_single_file_intact(self):
        """Test validating an intact file."""
        # Create a test file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        expected_info = self.validator._calculate_file_integrity(test_file)

        record = self.validator._validate_single_file(test_file, expected_info)

        self.assertEqual(record.status, IntegrityStatus.INTACT)
        self.assertEqual(record.path, str(test_file))
        self.assertEqual(record.expected_hash, expected_info["hash"])
        self.assertEqual(record.current_hash, expected_info["hash"])

    def test_validate_single_file_modified(self):
        """Test validating a modified file."""
        # Create a test file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        expected_info = self.validator._calculate_file_integrity(test_file)

        # Modify the file
        test_file.write_text("Modified content!")

        record = self.validator._validate_single_file(test_file, expected_info)

        self.assertEqual(record.status, IntegrityStatus.MODIFIED)
        self.assertNotEqual(record.expected_hash, record.current_hash)

    def test_validate_single_file_missing(self):
        """Test validating a missing file."""
        missing_file = self.temp_dir / "missing.txt"
        expected_info = {"hash": "dummy", "size": 100}

        record = self.validator._validate_single_file(missing_file, expected_info)

        self.assertEqual(record.status, IntegrityStatus.MISSING)
        self.assertIn("File does not exist", record.evidence)

    def test_should_exclude_file(self):
        """Test file exclusion logic."""
        # Should exclude log files
        log_file = Path("/test/app.log")
        self.assertTrue(self.validator._should_exclude_file(log_file))

        # Should exclude pyc files
        pyc_file = Path("/test/module.pyc")
        self.assertTrue(self.validator._should_exclude_file(pyc_file))

        # Should exclude hidden files
        hidden_file = Path("/test/.hidden")
        self.assertTrue(self.validator._should_exclude_file(hidden_file))

        # Should not exclude regular files
        regular_file = Path("/test/script.py")
        self.assertFalse(self.validator._should_exclude_file(regular_file))

    def test_get_baseline_filename(self):
        """Test generating baseline filename."""
        filename = self.validator._get_baseline_filename(
            "/test/path", ValidationScope.DIRECTORY
        )

        self.assertTrue(filename.name.startswith("baseline_test_path_directory_"))
        self.assertTrue(filename.name.endswith(".json"))
        self.assertEqual(filename.parent, self.validator.baseline_dir)

    def test_collect_files_application_scope(self):
        """Test collecting files for application scope."""
        # Create test directory structure
        test_dir = self.temp_dir / "app"
        test_dir.mkdir()

        # Create some files
        (test_dir / "main.py").write_text("print('hello')")
        (test_dir / "config.yaml").write_text("key: value")
        (test_dir / "data.log").write_text("log data")  # Should be excluded

        files = self.validator._collect_files(test_dir, ValidationScope.APPLICATION)

        # Should include Python and YAML files, exclude log
        file_names = [f.name for f in files]
        self.assertIn("main.py", file_names)
        self.assertIn("config.yaml", file_names)
        self.assertNotIn("data.log", file_names)

    def test_analyze_validation_results(self):
        """Test analyzing validation results."""
        report = IntegrityReport(
            timestamp="2023-01-01T00:00:00Z",
            scope=ValidationScope.DIRECTORY,
            target_path="/test",
            total_files=10,
            intact_files=7,
            modified_files=2,
            missing_files=1,
            corrupted_files=0,
            unknown_files=0,
            compliance_score=70.0,
            critical_issues=[],
            recommendations=[],
        )

        issues, recommendations = self.validator._analyze_validation_results(report)

        self.assertIn("1 critical files are missing", issues)
        self.assertIn("Review and update integrity baseline", recommendations)
        self.assertIn("Restore missing critical files from backup", recommendations)

    @patch("src.security.integrity_validator.get_audit_system")
    def test_create_baseline_single_file(self, mock_get_audit):
        """Test creating baseline for single file."""
        mock_audit = MagicMock()
        mock_get_audit.return_value = mock_audit

        # Create test file
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        validator = IntegrityValidator(audit_system=mock_audit)

        baseline = validator.create_baseline(
            str(test_file), ValidationScope.SINGLE_FILE
        )

        self.assertEqual(baseline["target_path"], str(test_file))
        self.assertEqual(baseline["scope"], "single_file")
        self.assertEqual(baseline["metadata"]["total_files"], 1)
        self.assertIn(str(test_file), baseline["files"])

        # Verify audit logging
        mock_audit.log_action.assert_called_once()

    @patch("src.security.integrity_validator.get_audit_system")
    def test_create_baseline_directory(self, mock_get_audit):
        """Test creating baseline for directory."""
        mock_audit = MagicMock()
        mock_get_audit.return_value = mock_audit

        # Create test directory with files
        test_dir = self.temp_dir / "testdir"
        test_dir.mkdir()
        (test_dir / "file1.py").write_text("print('test')")
        (test_dir / "file2.py").write_text("print('test2')")

        validator = IntegrityValidator(audit_system=mock_audit)

        baseline = validator.create_baseline(str(test_dir), ValidationScope.DIRECTORY)

        self.assertEqual(baseline["target_path"], str(test_dir))
        self.assertEqual(baseline["scope"], "directory")
        self.assertGreaterEqual(baseline["metadata"]["total_files"], 2)

        # Verify audit logging
        mock_audit.log_action.assert_called_once()

    @patch("src.security.integrity_validator.get_audit_system")
    def test_validate_integrity(self, mock_get_audit):
        """Test validating integrity."""
        mock_audit = MagicMock()
        mock_get_audit.return_value = mock_audit

        # Create test file and baseline
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        validator = IntegrityValidator(audit_system=mock_audit)

        # Create baseline
        validator.create_baseline(str(test_file), ValidationScope.SINGLE_FILE)

        # Validate (file unchanged)
        report = validator.validate_integrity(
            str(test_file), ValidationScope.SINGLE_FILE
        )

        self.assertEqual(report.total_files, 1)
        self.assertEqual(report.intact_files, 1)
        self.assertEqual(report.modified_files, 0)
        self.assertEqual(report.compliance_score, 100.0)

        # Verify audit logging
        self.assertEqual(mock_audit.log_action.call_count, 2)  # baseline + validation

    def test_validate_file_integrity(self):
        """Test validate_file_integrity method."""
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("Hello, World!")

        # Mock the audit system method
        self.mock_audit.verify_file_integrity.return_value = {"status": "verified"}

        result = self.validator.validate_file_integrity(str(test_file))

        self.mock_audit.verify_file_integrity.assert_called_once_with(str(test_file))
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "verified")

    def test_get_validation_history(self):
        """Test getting validation history."""
        # Create some mock report files
        report_dir = self.validator.log_dir
        report_dir.mkdir(parents=True, exist_ok=True)

        report_data = {
            "timestamp": "2023-01-01T00:00:00Z",
            "scope": "directory",
            "target_path": "/test",
            "summary": {"compliance_score": 95.0},
        }

        for i in range(3):
            report_file = report_dir / f"integrity_report_20230101_00000{i}.json"
            with open(report_file, "w") as f:
                json.dump(report_data, f)

        history = self.validator.get_validation_history(limit=2)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["summary"]["compliance_score"], 95.0)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""

    @patch("src.security.integrity_validator.IntegrityValidator")
    def test_get_integrity_validator(self, mock_validator_class):
        """Test get_integrity_validator singleton."""
        mock_instance = MagicMock()
        mock_validator_class.return_value = mock_instance

        # First call
        validator1 = get_integrity_validator()
        self.assertEqual(validator1, mock_instance)

        # Second call should return same instance
        validator2 = get_integrity_validator()
        self.assertEqual(validator2, mock_instance)

        # Should only create one instance
        mock_validator_class.assert_called_once()

    @patch("src.security.integrity_validator.get_integrity_validator")
    def test_validate_file_integrity_function(self, mock_get_validator):
        """Test validate_file_integrity convenience function."""
        mock_validator = MagicMock()
        mock_get_validator.return_value = mock_validator
        mock_validator.validate_file_integrity.return_value = {"status": "ok"}

        result = validate_file_integrity("/test/file.txt")

        mock_validator.validate_file_integrity.assert_called_once_with("/test/file.txt")
        self.assertEqual(result, {"status": "ok"})

    @patch("src.security.integrity_validator.get_integrity_validator")
    def test_create_integrity_baseline_function(self, mock_get_validator):
        """Test create_integrity_baseline convenience function."""
        mock_validator = MagicMock()
        mock_get_validator.return_value = mock_validator
        mock_validator.create_baseline.return_value = {"created": True}

        result = create_integrity_baseline("/test/path", "directory")

        mock_validator.create_baseline.assert_called_once()
        self.assertEqual(result, {"created": True})

    @patch("src.security.integrity_validator.get_integrity_validator")
    def test_run_integrity_validation_function(self, mock_get_validator):
        """Test run_integrity_validation convenience function."""
        mock_validator = MagicMock()
        mock_get_validator.return_value = mock_validator
        mock_report = MagicMock()
        mock_validator.validate_integrity.return_value = mock_report

        result = run_integrity_validation("/test/path", "application")

        mock_validator.validate_integrity.assert_called_once()
        self.assertEqual(result, mock_report)


if __name__ == "__main__":
    unittest.main()

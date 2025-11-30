"""
Grupo 10 - Integrity Validator Tests.

Testes abrangentes para o módulo de validação de integridade,
incluindo validação de hash, scan de diretórios e compliance reporting.

Author: This work was conceived by Fabrício da Silva and implemented with AI assistance from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review and debugging across various models including Gemini and Perplexity AI, under theoretical coordination by the author.
Date: November 2025
"""

from __future__ import annotations

import tempfile
import typing
from pathlib import Path

import pytest

from src.security.integrity_validator import (
    IntegrityReport,
    IntegrityStatus,
    IntegrityValidator,
    ValidationScope,
)


class TestIntegrityValidatorInit:
    """Testes de inicialização do validador de integridade."""

    def test_init_default(self) -> None:
        """Testa inicialização com valores padrão."""
        validator = IntegrityValidator()

        assert validator is not None
        assert hasattr(validator, "baseline_dir")
        assert hasattr(validator, "log_dir")

    def test_init_custom_directories(self) -> None:
        """Testa inicialização com diretórios customizados."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_dir = str(Path(tmpdir) / "baselines")
            log_dir = str(Path(tmpdir) / "logs")

            validator = IntegrityValidator(baseline_dir=baseline_dir, log_dir=log_dir)

            assert validator.baseline_dir == Path(baseline_dir)
            assert validator.log_dir == Path(log_dir)


class TestFileHashValidation:
    """Testes para validação de hash de arquivos."""

    @pytest.fixture
    def validator(self) -> IntegrityValidator:
        """Fixture para validator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield IntegrityValidator(
                baseline_dir=str(Path(tmpdir) / "baselines"),
                log_dir=str(Path(tmpdir) / "logs"),
            )

    @pytest.fixture
    def test_file(self) -> typing.Generator[Path, None, None]:
        """Fixture para arquivo de teste."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            path = Path(f.name)

        yield path

        # Cleanup
        if path.exists():
            path.unlink()

    def test_compute_file_hash(self, validator: IntegrityValidator, test_file: Path) -> None:
        """Testa computação de hash de arquivo."""
        # Accessing private method for testing purposes
        file_info = validator._calculate_file_integrity(test_file)
        file_hash = file_info.get("hash")

        assert file_hash is not None
        assert isinstance(file_hash, str)
        assert len(file_hash) == 64  # SHA-256 hash length

    def test_validate_file_intact(self, validator: IntegrityValidator, test_file: Path) -> None:
        """Testa validação de arquivo intacto."""
        # Calcula baseline
        expected_info = validator._calculate_file_integrity(test_file)

        # Valida arquivo
        record = validator._validate_single_file(test_file, expected_info)

        assert record.status == IntegrityStatus.INTACT
        assert record.current_hash == expected_info["hash"]

    def test_validate_file_modified(self, validator: IntegrityValidator, test_file: Path) -> None:
        """Testa detecção de arquivo modificado."""
        # Hash original
        original_info = validator._calculate_file_integrity(test_file)

        # Modifica arquivo
        with open(test_file, "a") as f:
            f.write("\nmodified content")

        # Valida (deve detectar modificação)
        record = validator._validate_single_file(test_file, original_info)

        assert record.status == IntegrityStatus.MODIFIED
        assert record.current_hash != original_info["hash"]

    def test_validate_file_missing(self, validator: IntegrityValidator) -> None:
        """Testa detecção de arquivo faltando."""
        missing_path = Path("/nonexistent/path/file.txt")
        expected_info = {"hash": "abc123", "size": 100, "mtime": 1234567890}

        record = validator._validate_single_file(missing_path, expected_info)

        assert record.status == IntegrityStatus.MISSING


class TestDirectoryScan:
    """Testes para scan de diretórios."""

    @pytest.fixture
    def validator(self) -> IntegrityValidator:
        """Fixture para validator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield IntegrityValidator(
                baseline_dir=str(Path(tmpdir) / "baselines"),
                log_dir=str(Path(tmpdir) / "logs"),
            )

    @pytest.fixture
    def test_directory(self) -> typing.Generator[Path, None, None]:
        """Fixture para diretório de teste."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)

            # Cria alguns arquivos
            (test_dir / "file1.txt").write_text("content 1")
            (test_dir / "file2.txt").write_text("content 2")
            (test_dir / "subdir").mkdir()
            (test_dir / "subdir" / "file3.txt").write_text("content 3")

            yield test_dir

    def test_scan_directory_basic(
        self, validator: IntegrityValidator, test_directory: Path
    ) -> None:
        """Testa scan básico de diretório."""
        # Create baseline first
        validator.create_baseline(str(test_directory), ValidationScope.DIRECTORY)

        # Then validate
        report = validator.validate_integrity(str(test_directory), ValidationScope.DIRECTORY)

        assert isinstance(report, IntegrityReport)
        assert report.total_files >= 3
        assert report.scope == ValidationScope.DIRECTORY


class TestBaselineManagement:
    """Testes para gerenciamento de baselines."""

    @pytest.fixture
    def validator(self) -> IntegrityValidator:
        """Fixture para validator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield IntegrityValidator(
                baseline_dir=str(Path(tmpdir) / "baselines"),
                log_dir=str(Path(tmpdir) / "logs"),
            )

    @pytest.fixture
    def test_directory(self) -> typing.Generator[Path, None, None]:
        """Fixture para diretório de teste."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            (test_dir / "file1.txt").write_text("content 1")
            (test_dir / "file2.txt").write_text("content 2")
            yield test_dir

    def test_generate_baseline(self, validator: IntegrityValidator, test_directory: Path) -> None:
        """Testa geração de baseline."""
        baseline = validator.create_baseline(str(test_directory), ValidationScope.DIRECTORY)

        assert baseline is not None
        assert isinstance(baseline, dict)
        assert len(baseline["files"]) >= 2


class TestComplianceReporting:
    """Testes para compliance reporting."""

    @pytest.fixture
    def validator(self) -> IntegrityValidator:
        """Fixture para validator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield IntegrityValidator(
                baseline_dir=str(Path(tmpdir) / "baselines"),
                log_dir=str(Path(tmpdir) / "logs"),
            )

    def test_generate_compliance_report(self, validator: IntegrityValidator) -> None:
        """Testa geração de relatório de compliance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            (test_dir / "file1.txt").write_text("content")

            # Create baseline
            validator.create_baseline(str(test_dir), ValidationScope.DIRECTORY)

            # Validate
            report = validator.validate_integrity(str(test_dir), ValidationScope.DIRECTORY)

            assert isinstance(report, IntegrityReport)
            assert hasattr(report, "compliance_score")
            assert 0.0 <= report.compliance_score <= 100.0

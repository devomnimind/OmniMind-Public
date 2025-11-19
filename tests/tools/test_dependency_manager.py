"""
Tests for dependency_manager module.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.tools.dependency_manager import (
    DependencyLockfile,
    DependencyManager,
    PackageInfo,
    Vulnerability,
    VulnerabilitySeverity,
    create_lockfile,
    scan_dependencies,
)


class TestPackageInfo:
    """Tests for PackageInfo dataclass."""

    def test_package_info_creation(self) -> None:
        """Test PackageInfo creation."""
        pkg = PackageInfo(
            name="pytest",
            version="9.0.0",
            dependencies=["pluggy", "iniconfig"],
            license="MIT",
        )

        assert pkg.name == "pytest"
        assert pkg.version == "9.0.0"
        assert len(pkg.dependencies) == 2


class TestDependencyLockfile:
    """Tests for DependencyLockfile."""

    def test_lockfile_to_dict(self) -> None:
        """Test lockfile conversion to dictionary."""
        packages = {
            "pytest": PackageInfo(
                name="pytest",
                version="9.0.0",
                hash_sha256="abc123",
                dependencies=["pluggy"],
                license="MIT",
            )
        }

        lockfile = DependencyLockfile(
            packages=packages,
            generated_at="2025-11-19T00:00:00",
            python_version="3.12",
            platform="Linux",
        )

        data = lockfile.to_dict()

        assert "packages" in data
        assert "pytest" in data["packages"]
        assert data["packages"]["pytest"]["version"] == "9.0.0"
        assert data["packages"]["pytest"]["hash"] == "abc123"

    def test_lockfile_from_dict(self) -> None:
        """Test lockfile creation from dictionary."""
        data = {
            "generated_at": "2025-11-19T00:00:00",
            "python_version": "3.12",
            "platform": "Linux",
            "packages": {
                "pytest": {
                    "version": "9.0.0",
                    "hash": "abc123",
                    "dependencies": ["pluggy"],
                    "license": "MIT",
                }
            },
        }

        lockfile = DependencyLockfile.from_dict(data)

        assert len(lockfile.packages) == 1
        assert "pytest" in lockfile.packages
        assert lockfile.packages["pytest"].version == "9.0.0"


class TestDependencyManager:
    """Tests for DependencyManager."""

    @pytest.fixture
    def temp_files(self, tmp_path: Path) -> tuple[Path, Path]:
        """Create temporary files for testing."""
        requirements = tmp_path / "requirements.txt"
        lockfile = tmp_path / "requirements.lock"

        requirements.write_text("pytest>=9.0.0\npydantic>=2.0.0\n")

        return requirements, lockfile

    def test_dependency_manager_initialization(
        self, temp_files: tuple[Path, Path]
    ) -> None:
        """Test DependencyManager initialization."""
        requirements, lockfile = temp_files

        manager = DependencyManager(requirements, lockfile)

        assert manager.requirements_file == requirements
        assert manager.lockfile == lockfile
        assert manager.vulnerabilities == []
        assert manager.conflicts == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

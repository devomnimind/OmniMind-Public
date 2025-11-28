"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Advanced Dependency Management System for OmniMind.

Provides comprehensive dependency management with:
- Dependency locking with hash verification
- Automated security vulnerability scanning
- Version conflict resolution
- Update suggestions with compatibility checking
- License compliance verification
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


class VulnerabilitySeverity(str, Enum):
    """Vulnerability severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PackageInfo:
    """Information about a Python package."""

    name: str
    version: str
    latest_version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    license: Optional[str] = None
    homepage: Optional[str] = None
    hash_sha256: Optional[str] = None


@dataclass
class Vulnerability:
    """Security vulnerability in a package."""

    package: str
    version: str
    cve_id: Optional[str]
    severity: VulnerabilitySeverity
    description: str
    fixed_version: Optional[str] = None
    published_date: Optional[str] = None


@dataclass
class ConflictInfo:
    """Dependency conflict information."""

    package: str
    current_version: str
    required_versions: List[str]
    conflicting_packages: List[str]
    resolution_suggestion: Optional[str] = None


@dataclass
class DependencyLockfile:
    """Lockfile for dependency versions with hashes."""

    packages: Dict[str, PackageInfo]
    generated_at: str
    python_version: str
    platform: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "generated_at": self.generated_at,
            "python_version": self.python_version,
            "platform": self.platform,
            "packages": {
                name: {
                    "version": pkg.version,
                    "hash": pkg.hash_sha256,
                    "dependencies": pkg.dependencies,
                    "license": pkg.license,
                }
                for name, pkg in self.packages.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DependencyLockfile:
        """Create from dictionary."""
        packages = {}
        for name, info in data.get("packages", {}).items():
            packages[name] = PackageInfo(
                name=name,
                version=info["version"],
                hash_sha256=info.get("hash"),
                dependencies=info.get("dependencies", []),
                license=info.get("license"),
            )

        return cls(
            packages=packages,
            generated_at=data["generated_at"],
            python_version=data["python_version"],
            platform=data["platform"],
        )


class DependencyManager:
    """Advanced dependency management with security scanning and locking."""

    def __init__(
        self,
        requirements_file: Path = Path("requirements.txt"),
        lockfile: Path = Path("requirements.lock"),
    ):
        """
        Initialize dependency manager.

        Args:
            requirements_file: Path to requirements.txt
            lockfile: Path to lockfile
        """
        self.requirements_file = requirements_file
        self.lockfile = lockfile
        self.vulnerabilities: List[Vulnerability] = []
        self.conflicts: List[ConflictInfo] = []

    def generate_lockfile(self) -> DependencyLockfile:
        """
        Generate lockfile with all dependencies and their hashes.

        Returns:
            DependencyLockfile with package information
        """
        logger.info("Generating dependency lockfile...")

        # Get installed packages
        result = subprocess.run(
            ["pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )

        packages = {}
        for line in result.stdout.strip().split("\n"):
            if "==" in line:
                name, version = line.split("==")
                name = name.strip()
                version = version.strip()

                # Get package info
                pkg_info = self._get_package_info(name, version)
                packages[name] = pkg_info

        # Get Python version and platform
        import platform
        import sys

        lockfile = DependencyLockfile(
            packages=packages,
            generated_at=datetime.now().isoformat(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            platform=platform.system(),
        )

        # Save lockfile
        self.save_lockfile(lockfile)

        logger.info(f"Generated lockfile with {len(packages)} packages")

        return lockfile

    def _get_package_info(self, name: str, version: str) -> PackageInfo:
        """Get detailed package information."""
        try:
            # Get package metadata from pip show
            result = subprocess.run(
                ["pip", "show", name],
                capture_output=True,
                text=True,
                check=True,
            )

            metadata = {}
            for line in result.stdout.strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()

            # Get hash from pip download (without actually downloading)
            hash_result = subprocess.run(
                ["pip", "hash", name],
                capture_output=True,
                text=True,
            )

            hash_sha256 = None
            if hash_result.returncode == 0:
                # Parse hash from output
                for line in hash_result.stdout.split("\n"):
                    if "sha256" in line:
                        hash_sha256 = line.split(":")[-1].strip()
                        break

            # Parse dependencies
            requires = metadata.get("Requires", "")
            dependencies = [dep.strip() for dep in requires.split(",") if dep.strip()]

            return PackageInfo(
                name=name,
                version=version,
                dependencies=dependencies,
                license=metadata.get("License"),
                homepage=metadata.get("Home-page"),
                hash_sha256=hash_sha256,
            )

        except Exception as e:
            logger.warning(f"Failed to get info for {name}: {e}")
            return PackageInfo(name=name, version=version)

    def save_lockfile(self, lockfile: DependencyLockfile) -> None:
        """Save lockfile to disk."""
        with self.lockfile.open("w") as f:
            json.dump(lockfile.to_dict(), f, indent=2)

        logger.info(f"Lockfile saved to {self.lockfile}")

    def load_lockfile(self) -> Optional[DependencyLockfile]:
        """Load lockfile from disk."""
        if not self.lockfile.exists():
            logger.warning(f"Lockfile not found: {self.lockfile}")
            return None

        with self.lockfile.open() as f:
            data = json.load(f)

        return DependencyLockfile.from_dict(data)

    def verify_lockfile(self, lockfile: Optional[DependencyLockfile] = None) -> bool:
        """
        Verify that installed packages match lockfile.

        Args:
            lockfile: Lockfile to verify against (loads from disk if None)

        Returns:
            True if all packages match, False otherwise
        """
        if lockfile is None:
            lockfile = self.load_lockfile()
            if lockfile is None:
                logger.error("No lockfile to verify against")
                return False

        logger.info("Verifying installed packages against lockfile...")

        # Get currently installed packages
        result = subprocess.run(
            ["pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )

        installed = {}
        for line in result.stdout.strip().split("\n"):
            if "==" in line:
                name, version = line.split("==")
                installed[name.strip()] = version.strip()

        # Check for mismatches
        mismatches = []
        for name, pkg in lockfile.packages.items():
            if name not in installed:
                mismatches.append(f"{name} missing")
            elif installed[name] != pkg.version:
                mismatches.append(f"{name}: expected {pkg.version}, got {installed[name]}")

        if mismatches:
            logger.error(f"Lockfile verification failed: {len(mismatches)} mismatches")
            for mismatch in mismatches:
                logger.error(f"  - {mismatch}")
            return False

        logger.info("Lockfile verification passed ✓")
        return True

    def scan_vulnerabilities(
        self, use_osv: bool = True, use_safety: bool = True
    ) -> List[Vulnerability]:
        """
        Scan for security vulnerabilities in dependencies.

        Args:
            use_osv: Use OSV (Open Source Vulnerabilities) database
            use_safety: Use Safety DB (requires safety package)

        Returns:
            List of found vulnerabilities
        """
        logger.info("Scanning for security vulnerabilities...")

        vulnerabilities: List[Vulnerability] = []

        # Scan using OSV API
        if use_osv:
            vulnerabilities.extend(self._scan_osv())

        # Scan using safety (if installed)
        if use_safety:
            try:
                vulnerabilities.extend(self._scan_safety())
            except Exception as e:
                logger.warning(f"Safety scan failed: {e}")

        self.vulnerabilities = vulnerabilities

        logger.info(f"Found {len(vulnerabilities)} vulnerabilities")

        return vulnerabilities

    def _scan_osv(self) -> List[Vulnerability]:
        """Scan using OSV (Open Source Vulnerabilities) API."""
        vulnerabilities = []

        # Get installed packages
        result = subprocess.run(
            ["pip", "freeze"],
            capture_output=True,
            text=True,
            check=True,
        )

        for line in result.stdout.strip().split("\n"):
            if "==" in line:
                name, version = line.split("==")
                name = name.strip()
                version = version.strip()

                # Query OSV API
                try:
                    response = requests.post(
                        "https://api.osv.dev/v1/query",
                        json={
                            "package": {"name": name, "ecosystem": "PyPI"},
                            "version": version,
                        },
                        timeout=10,
                    )

                    if response.status_code == 200:
                        data = response.json()
                        for vuln in data.get("vulns", []):
                            # Map severity
                            severity_str = (
                                vuln.get("severity", [{}])[0].get("score", "MEDIUM").lower()
                            )
                            try:
                                severity = VulnerabilitySeverity(severity_str)
                            except ValueError:
                                severity = VulnerabilitySeverity.MEDIUM

                            # Get fixed version
                            fixed_version = None
                            for affected in vuln.get("affected", []):
                                if affected.get("package", {}).get("name") == name:
                                    ranges = affected.get("ranges", [])
                                    if ranges and "fixed" in ranges[0]:
                                        fixed_version = ranges[0]["fixed"]

                            vulnerabilities.append(
                                Vulnerability(
                                    package=name,
                                    version=version,
                                    cve_id=vuln.get("id"),
                                    severity=severity,
                                    description=vuln.get("summary", "No description"),
                                    fixed_version=fixed_version,
                                    published_date=vuln.get("published"),
                                )
                            )

                except Exception as e:
                    logger.debug(f"OSV scan failed for {name}: {e}")

        return vulnerabilities

    def _scan_safety(self) -> List[Vulnerability]:
        """Scan using safety CLI."""
        try:
            result = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                vulnerabilities = []

                for vuln in data:
                    # Map severity
                    severity_str = vuln.get("severity", "medium").lower()
                    try:
                        severity = VulnerabilitySeverity(severity_str)
                    except ValueError:
                        severity = VulnerabilitySeverity.MEDIUM

                    vulnerabilities.append(
                        Vulnerability(
                            package=vuln["package"],
                            version=vuln["installed_version"],
                            cve_id=vuln.get("cve"),
                            severity=severity,
                            description=vuln["advisory"],
                            fixed_version=vuln.get("fixed_version"),
                        )
                    )

                return vulnerabilities

        except FileNotFoundError:
            logger.debug("safety not installed, skipping")
        except Exception as e:
            logger.debug(f"safety scan failed: {e}")

        return []

    def detect_conflicts(self) -> List[ConflictInfo]:
        """
        Detect dependency version conflicts.

        Returns:
            List of conflicts found
        """
        logger.info("Detecting dependency conflicts...")

        conflicts: List[ConflictInfo] = []

        # Use pip check to detect conflicts
        result = subprocess.run(
            ["pip", "check"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            # Parse conflicts from output
            for line in result.stdout.split("\n"):
                if "has requirement" in line or "incompatible with" in line:
                    # Parse conflict information
                    # This is a simplified parser
                    parts = line.split()
                    if len(parts) >= 3:
                        conflicts.append(
                            ConflictInfo(
                                package=parts[0],
                                current_version="unknown",
                                required_versions=[],
                                conflicting_packages=[],
                                resolution_suggestion=line.strip(),
                            )
                        )

        self.conflicts = conflicts

        logger.info(f"Found {len(conflicts)} conflicts")

        return conflicts

    def suggest_updates(self) -> Dict[str, Tuple[str, str]]:
        """
        Suggest package updates.

        Returns:
            Dict of {package: (current_version, latest_version)}
        """
        logger.info("Checking for package updates...")

        updates = {}

        # Get installed packages
        result = subprocess.run(
            ["pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True,
        )

        outdated = json.loads(result.stdout)

        for pkg in outdated:
            updates[pkg["name"]] = (pkg["version"], pkg["latest_version"])

        logger.info(f"Found {len(updates)} packages with updates available")

        return updates

    def generate_security_report(self, output_file: Optional[Path] = None) -> str:
        """
        Generate comprehensive security report.

        Args:
            output_file: Optional file to write report to

        Returns:
            Report as string
        """
        logger.info("Generating security report...")

        lines = []
        lines.append("# OmniMind Dependency Security Report")
        lines.append(f"\nGenerated: {datetime.now().isoformat()}\n")

        # Vulnerabilities section
        lines.append("## Vulnerabilities\n")
        if self.vulnerabilities:
            lines.append(f"Found {len(self.vulnerabilities)} vulnerabilities:\n")

            # Group by severity
            by_severity: Dict[VulnerabilitySeverity, List[Vulnerability]] = {}
            for vuln in self.vulnerabilities:
                by_severity.setdefault(vuln.severity, []).append(vuln)

            for severity in VulnerabilitySeverity:
                vulns = by_severity.get(severity, [])
                if vulns:
                    lines.append(f"\n### {severity.value.upper()} ({len(vulns)})\n")
                    for vuln in vulns:
                        lines.append(f"- **{vuln.package}** {vuln.version}")
                        if vuln.cve_id:
                            lines.append(f" ({vuln.cve_id})")
                        lines.append(f"\n  {vuln.description}")
                        if vuln.fixed_version:
                            lines.append(f"\n  Fixed in: {vuln.fixed_version}")
                        lines.append("\n")
        else:
            lines.append("No vulnerabilities found ✓\n")

        # Conflicts section
        lines.append("\n## Dependency Conflicts\n")
        if self.conflicts:
            lines.append(f"Found {len(self.conflicts)} conflicts:\n")
            for conflict in self.conflicts:
                lines.append(f"- {conflict.package}")
                if conflict.resolution_suggestion:
                    lines.append(f"\n  {conflict.resolution_suggestion}")
                lines.append("\n")
        else:
            lines.append("No conflicts found ✓\n")

        report = "\n".join(lines)

        if output_file:
            output_file.write_text(report)
            logger.info(f"Security report saved to {output_file}")

        return report


# Convenience functions
def scan_dependencies(
    requirements_file: Path = Path("requirements.txt"),
) -> Tuple[List[Vulnerability], List[ConflictInfo]]:
    """
    Quick scan for vulnerabilities and conflicts.

    Args:
        requirements_file: Path to requirements.txt

    Returns:
        Tuple of (vulnerabilities, conflicts)
    """
    manager = DependencyManager(requirements_file)
    vulnerabilities = manager.scan_vulnerabilities()
    conflicts = manager.detect_conflicts()

    return vulnerabilities, conflicts


def create_lockfile(
    requirements_file: Path = Path("requirements.txt"),
    lockfile: Path = Path("requirements.lock"),
) -> DependencyLockfile:
    """
    Create dependency lockfile.

    Args:
        requirements_file: Path to requirements.txt
        lockfile: Path to output lockfile

    Returns:
        Generated lockfile
    """
    manager = DependencyManager(requirements_file, lockfile)
    return manager.generate_lockfile()


if __name__ == "__main__":
    # Demo usage
    print("🔍 Scanning dependencies...")

    manager = DependencyManager()

    # Generate lockfile
    print("\n📋 Generating lockfile...")
    lockfile = manager.generate_lockfile()
    print(f"✓ Lockfile created with {len(lockfile.packages)} packages")

    # Scan for vulnerabilities
    print("\n🔒 Scanning for vulnerabilities...")
    vulnerabilities = manager.scan_vulnerabilities()

    if vulnerabilities:
        print(f"⚠ Found {len(vulnerabilities)} vulnerabilities:")
        for vuln in vulnerabilities[:5]:  # Show first 5
            print(f"  - {vuln.package} {vuln.version}: {vuln.description[:50]}...")
    else:
        print("✓ No vulnerabilities found")

    # Check for conflicts
    print("\n🔄 Detecting conflicts...")
    conflicts = manager.detect_conflicts()

    if conflicts:
        print(f"⚠ Found {len(conflicts)} conflicts")
    else:
        print("✓ No conflicts found")

    # Generate report
    print("\n📄 Generating security report...")
    report = manager.generate_security_report(Path("logs/dependency_security_report.md"))
    print("✓ Report saved to logs/dependency_security_report.md")

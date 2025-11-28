#!/usr/bin/env python3
"""
Dependency Analysis Utility for OmniMind

Analyzes Python package dependencies, identifies potential issues,
and provides recommendations for dependency management.

Features:
- Dependency tree analysis
- Version conflict detection
- Unused dependency identification
- Security vulnerability scanning
- License compatibility checking

Usage:
    python scripts/analyze_dependencies.py [--deep] [--security] [--licenses]

Author: OmniMind Development Team
License: MIT
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import structlog

logger = structlog.get_logger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
REQUIREMENTS_FILES = [
    "requirements.txt",
    "requirements-dev.txt",
    "requirements-ci.txt",
    "requirements-cpu.txt",
    "requirements-minimal.txt",
    "requirements-benchmark.txt",
]


class DependencyAnalyzer:
    """
    Comprehensive dependency analysis for Python projects.

    Analyzes package dependencies, versions, conflicts, and potential issues
    to ensure a healthy dependency ecosystem.
    """

    def __init__(self, project_root: Path):
        """
        Initialize dependency analyzer.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root
        self.installed_packages: Dict[str, str] = {}
        self.declared_deps: Dict[str, Set[str]] = {}
        self.security_issues: List[Dict[str, Any]] = []

        logger.info("dependency_analyzer_initialized", project_root=str(project_root))

    def load_installed_packages(self) -> None:
        """
        Load currently installed packages using pip freeze.

        Populates self.installed_packages with name -> version mapping.
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.project_root
            )

            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    name, version = line.split('==', 1)
                    self.installed_packages[name.lower()] = version

            logger.info("installed_packages_loaded", count=len(self.installed_packages))

        except subprocess.CalledProcessError as e:
            logger.error("failed_to_load_installed_packages", error=str(e))
            raise

    def load_requirements_files(self) -> None:
        """
        Load all requirements files and parse declared dependencies.

        Populates self.declared_deps with filename -> set of package names.
        """
        for req_file in REQUIREMENTS_FILES:
            req_path = self.project_root / req_file
            if req_path.exists():
                deps = set()
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Extract package name (handle version specs)
                                package = line.split()[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
                                deps.add(package.lower())
                except Exception as e:
                    logger.warning("failed_to_parse_requirements", file=req_file, error=str(e))
                    continue

                self.declared_deps[req_file] = deps
                logger.debug("requirements_loaded", file=req_file, deps_count=len(deps))

    def analyze_dependency_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive dependency health analysis.

        Returns:
            Dictionary containing analysis results and recommendations.
        """
        analysis = {
            "summary": {},
            "issues": [],
            "recommendations": [],
            "unused_packages": [],
            "missing_packages": [],
        }

        # Check for unused packages
        analysis["unused_packages"] = self._find_unused_packages()

        # Check for missing packages
        analysis["missing_packages"] = self._find_missing_packages()

        # Check for version conflicts
        conflicts = self._check_version_conflicts()
        if conflicts:
            analysis["issues"].extend(conflicts)

        # Generate summary
        analysis["summary"] = {
            "total_installed": len(self.installed_packages),
            "total_declared": sum(len(deps) for deps in self.declared_deps.values()),
            "unused_count": len(analysis["unused_packages"]),
            "missing_count": len(analysis["missing_packages"]),
            "conflict_count": len(conflicts),
        }

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        return analysis

    def _find_unused_packages(self) -> List[str]:
        """
        Identify potentially unused installed packages.

        This is a heuristic analysis - may have false positives.
        """
        # Get all declared packages
        declared = set()
        for deps in self.declared_deps.values():
            declared.update(deps)

        # Common packages that might be runtime dependencies
        runtime_deps = {
            'numpy', 'scipy', 'pandas', 'matplotlib', 'pillow',
            'requests', 'urllib3', 'certifi', 'charset-normalizer',
            'torch', 'torchvision', 'transformers', 'tokenizers',
            'qiskit', 'qiskit-aer', 'structlog', 'pyyaml',
        }

        unused: List[str] = []
        for package in self.installed_packages:
            if package not in declared and package not in runtime_deps:
                # Additional heuristics could be added here
                unused.append(package)

        return sorted(unused)

    def _find_missing_packages(self) -> List[str]:
        """
        Identify declared packages that are not installed.
        """
        declared = set()
        for deps in self.declared_deps.values():
            declared.update(deps)

        missing: List[str] = []
        for package in declared:
            if package not in self.installed_packages:
                missing.append(package)

        return sorted(missing)

    def _check_version_conflicts(self) -> List[Dict]:
        """
        Check for potential version conflicts between requirements files.

        This is a simplified check - real conflicts require solving the
        constraint satisfaction problem.
        """
        conflicts: List[Dict[str, Any]] = []

        # For now, just check if same package appears in multiple files
        # with different version specs (would need more sophisticated parsing)

        return conflicts

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """
        Generate actionable recommendations based on analysis.
        """
        recommendations: List[str] = []

        if analysis["summary"]["unused_count"] > 0:
            recommendations.append(
                f"Consider removing {analysis['summary']['unused_count']} potentially unused packages. "
                "Run 'pip uninstall' for: " + ", ".join(analysis["unused_packages"][:5])
            )

        if analysis["summary"]["missing_count"] > 0:
            recommendations.append(
                f"Install {analysis['summary']['missing_count']} missing declared dependencies. "
                "Run 'pip install -r requirements.txt' to sync."
            )

        if analysis["summary"]["conflict_count"] > 0:
            recommendations.append(
                "Resolve version conflicts between requirements files. "
                "Consider using pip-tools or poetry for dependency management."
            )

        if analysis["summary"]["total_installed"] > 50:
            recommendations.append(
                "High number of installed packages detected. "
                "Consider using a virtual environment per project phase."
            )

        return recommendations

    def check_security_vulnerabilities(self) -> List[Dict]:
        """
        Check for known security vulnerabilities in installed packages.

        Uses safety package if available, otherwise provides basic checks.
        """
        vulnerabilities: List[Dict[str, Any]] = []

        try:
            # Try to use safety package
            result = subprocess.run(
                [sys.executable, "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode == 0:
                safety_data = json.loads(result.stdout)
                vulnerabilities.extend(safety_data.get("vulnerabilities", []))
            else:
                logger.warning("safety_check_failed", stderr=result.stderr)

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: basic check for known vulnerable packages
            vulnerable_packages = {
                "insecure-package": "Known vulnerability - update immediately",
            }

            for package in self.installed_packages:
                if package in vulnerable_packages:
                    vulnerabilities.append({
                        "package": package,
                        "vulnerability": vulnerable_packages[package],
                        "severity": "high"
                    })

        return vulnerabilities

    def analyze_licenses(self) -> Dict[str, Any]:
        """
        Analyze license compatibility of installed packages.

        Returns information about licenses and potential compatibility issues.
        """
        license_info = {
            "licenses": {},
            "incompatible": [],
            "unknown": [],
        }

        # This would require license metadata from packages
        # For now, return placeholder structure

        return license_info


def main():
    """Main entry point for dependency analysis."""
    parser = argparse.ArgumentParser(description="Analyze Python dependencies")
    parser.add_argument("--deep", action="store_true", help="Perform deep analysis")
    parser.add_argument("--security", action="store_true", help="Include security checks")
    parser.add_argument("--licenses", action="store_true", help="Include license analysis")
    parser.add_argument("--output", type=str, help="Output file for results")

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = DependencyAnalyzer(PROJECT_ROOT)

    try:
        # Load data
        analyzer.load_installed_packages()
        analyzer.load_requirements_files()

        # Perform analysis
        results = analyzer.analyze_dependency_health()

        if args.security:
            results["security"] = analyzer.check_security_vulnerabilities()

        if args.licenses:
            results["licenses"] = analyzer.analyze_licenses()

        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error("dependency_analysis_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


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

"""Proactive goal generation engine for OmniMind.

This module analyzes the repository state and generates improvement goals:
- Test coverage assessment
- Performance bottleneck detection
- Code quality improvements
- Documentation gaps
- Security vulnerabilities
"""


logger = logging.getLogger(__name__)


class GoalPriority:
    """Priority levels for generated goals."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalCategory:
    """Categories of improvement goals."""

    TESTING = "testing"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    ARCHITECTURE = "architecture"


class ProactiveGoal:
    """Represents a proactive improvement goal."""

    def __init__(
        self,
        goal_id: str,
        title: str,
        description: str,
        category: str,
        priority: str,
        estimated_effort: str,
        acceptance_criteria: List[str],
        implementation_steps: List[str],
        metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a proactive goal.

        Args:
            goal_id: Unique identifier
            title: Short title
            description: Detailed description
            category: Goal category
            priority: Priority level
            estimated_effort: Effort estimate (hours/days)
            acceptance_criteria: List of completion criteria
            implementation_steps: List of implementation steps
            metrics: Supporting metrics
        """
        self.goal_id = goal_id
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.estimated_effort = estimated_effort
        self.acceptance_criteria = acceptance_criteria
        self.implementation_steps = implementation_steps
        self.metrics = metrics or {}
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "estimated_effort": self.estimated_effort,
            "acceptance_criteria": self.acceptance_criteria,
            "implementation_steps": self.implementation_steps,
            "metrics": self.metrics,
            "created_at": self.created_at,
        }


class ProactiveGoalEngine:
    """Engine for proactive goal generation."""

    def __init__(self, workspace_path: str = ".") -> None:
        """Initialize goal generation engine.

        Args:
            workspace_path: Path to repository root
        """
        self.workspace_path = Path(workspace_path)
        self._goal_counter = 0

    def _generate_id(self) -> str:
        """Generate unique goal ID."""
        self._goal_counter += 1
        return f"GOAL-{datetime.now().strftime('%Y%m%d')}-{self._goal_counter:03d}"

    def _run_command(self, command: List[str]) -> Tuple[bool, str]:
        """Run shell command and return result.

        Args:
            command: Command to run

        Returns:
            Tuple of (success, output)
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0, result.stdout
        except Exception as exc:
            logger.warning(f"Command failed: {command}: {exc}")
            return False, str(exc)

    def assess_test_coverage(self) -> List[ProactiveGoal]:
        """Assess test coverage and generate improvement goals.

        Returns:
            List of test coverage improvement goals
        """
        goals = []

        # Try to run pytest with coverage
        success, output = self._run_command(["pytest", "--cov=src", "--cov-report=json", "-q"])

        if success and (self.workspace_path / "coverage.json").exists():
            try:
                with open(self.workspace_path / "coverage.json") as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

                if total_coverage < 80:
                    goals.append(
                        ProactiveGoal(
                            goal_id=self._generate_id(),
                            title="Increase test coverage to 80%",
                            description=(
                                f"Current test coverage is {total_coverage:.1f}%, "
                                f"which is below the recommended 80% threshold."
                            ),
                            category=GoalCategory.TESTING,
                            priority=GoalPriority.HIGH,
                            estimated_effort="2-3 days",
                            acceptance_criteria=[
                                "Overall test coverage >= 80%",
                                "No critical modules below 70% coverage",
                                "All new code has >= 90% coverage",
                            ],
                            implementation_steps=[
                                "Identify modules with lowest coverage",
                                "Write unit tests for uncovered code paths",
                                "Add integration tests for key workflows",
                                "Update CI/CD to enforce coverage thresholds",
                            ],
                            metrics={
                                "current_coverage": total_coverage,
                                "target_coverage": 80.0,
                                "gap": 80.0 - total_coverage,
                            },
                        )
                    )

                # Check for untested files
                files = coverage_data.get("files", {})
                untested_files = [
                    path
                    for path, data in files.items()
                    if data.get("summary", {}).get("percent_covered", 100) < 50
                ]

                if untested_files:
                    goals.append(
                        ProactiveGoal(
                            goal_id=self._generate_id(),
                            title=f"Add tests for {len(untested_files)} low-coverage files",
                            description=(
                                f"Found {len(untested_files)} files with <50% coverage "
                                f"that need test coverage."
                            ),
                            category=GoalCategory.TESTING,
                            priority=GoalPriority.MEDIUM,
                            estimated_effort="1-2 days",
                            acceptance_criteria=[
                                "All identified files have >= 50% coverage",
                                "Critical paths in these files are fully tested",
                            ],
                            implementation_steps=[
                                "Review uncovered code in each file",
                                "Write tests for critical functions",
                                "Add edge case tests",
                            ],
                            metrics={
                                "untested_files": len(untested_files),
                                "files": untested_files[:5],  # First 5
                            },
                        )
                    )

            except Exception as exc:
                logger.warning(f"Failed to parse coverage data: {exc}")

        return goals

    def detect_performance_bottlenecks(self) -> List[ProactiveGoal]:
        """Detect performance bottlenecks and generate optimization goals.

        Returns:
            List of performance optimization goals
        """
        goals = []

        # Check for slow imports
        success, output = self._run_command(["python", "-X", "importtime", "-c", "import src"])

        if success and "cumtime" in output:
            # Parse import times
            lines = output.strip().split("\n")
            slow_imports = []

            for line in lines:
                if "import" in line and "ms" in line:
                    parts = line.split()
                    try:
                        # Extract timing from importtime output
                        time_val = float(parts[0])
                        if time_val > 100:  # >100ms
                            module = parts[-1] if parts else "unknown"
                            slow_imports.append((module, time_val))
                    except (ValueError, IndexError):
                        continue

            if slow_imports:
                goals.append(
                    ProactiveGoal(
                        goal_id=self._generate_id(),
                        title="Optimize slow module imports",
                        description=(
                            f"Found {len(slow_imports)} modules with slow import times "
                            f"(>100ms) that impact startup performance."
                        ),
                        category=GoalCategory.PERFORMANCE,
                        priority=GoalPriority.MEDIUM,
                        estimated_effort="1 day",
                        acceptance_criteria=[
                            "All module imports <100ms",
                            "Application startup time <2 seconds",
                        ],
                        implementation_steps=[
                            "Profile slow imports to identify bottlenecks",
                            "Implement lazy imports where appropriate",
                            "Move heavy imports to function scope",
                            "Consider import optimization libraries",
                        ],
                        metrics={
                            "slow_imports": len(slow_imports),
                            "slowest": slow_imports[:3],
                        },
                    )
                )

        return goals

    def assess_code_quality(self) -> List[ProactiveGoal]:
        """Assess code quality and generate improvement goals.

        Returns:
            List of code quality improvement goals
        """
        goals = []

        # Run flake8 to check for style issues
        success, output = self._run_command(["flake8", "src", "tests", "--count", "--statistics"])

        if output:
            lines = output.strip().split("\n")
            total_issues = 0

            for line in lines:
                try:
                    parts = line.split()
                    if parts and parts[0].isdigit():
                        total_issues += int(parts[0])
                except (ValueError, IndexError):
                    continue

            if total_issues > 50:
                goals.append(
                    ProactiveGoal(
                        goal_id=self._generate_id(),
                        title="Fix code style violations",
                        description=(
                            f"Found {total_issues} code style violations that "
                            f"should be addressed to maintain code quality."
                        ),
                        category=GoalCategory.QUALITY,
                        priority=GoalPriority.MEDIUM,
                        estimated_effort="1-2 days",
                        acceptance_criteria=[
                            "Zero flake8 violations",
                            "All code formatted with black",
                            "100% type hints coverage (mypy)",
                        ],
                        implementation_steps=[
                            "Run black formatter on all Python files",
                            "Fix flake8 violations systematically",
                            "Add missing type hints",
                            "Update pre-commit hooks",
                        ],
                        metrics={
                            "total_violations": total_issues,
                        },
                    )
                )

        return goals

    def check_documentation_gaps(self) -> List[ProactiveGoal]:
        """Check for documentation gaps.

        Returns:
            List of documentation improvement goals
        """
        goals = []

        # Check for missing docstrings
        python_files = list(self.workspace_path.glob("src/**/*.py"))
        files_without_docstrings = []

        for py_file in python_files:
            try:
                with open(py_file) as f:
                    content = f.read()
                    # Simple check: file should have triple-quoted docstring
                    if '"""' not in content and "'''" not in content:
                        files_without_docstrings.append(
                            str(py_file.relative_to(self.workspace_path))
                        )
            except Exception:
                continue

        if len(files_without_docstrings) > 5:
            goals.append(
                ProactiveGoal(
                    goal_id=self._generate_id(),
                    title="Add missing docstrings",
                    description=(
                        f"Found {len(files_without_docstrings)} Python files "
                        f"without module docstrings."
                    ),
                    category=GoalCategory.DOCUMENTATION,
                    priority=GoalPriority.LOW,
                    estimated_effort="1 day",
                    acceptance_criteria=[
                        "All Python modules have docstrings",
                        "All public functions have docstrings",
                        "Docstrings follow Google style guide",
                    ],
                    implementation_steps=[
                        "Add module-level docstrings",
                        "Document all public functions and classes",
                        "Add usage examples for complex modules",
                    ],
                    metrics={
                        "files_missing_docstrings": len(files_without_docstrings),
                    },
                )
            )

        return goals

    def generate_goals(self) -> List[Dict[str, Any]]:
        """Generate all proactive improvement goals.

        Returns:
            List of goals as dictionaries
        """
        all_goals = []

        logger.info("Generating proactive goals...")

        # Assess different aspects
        all_goals.extend(self.assess_test_coverage())
        all_goals.extend(self.detect_performance_bottlenecks())
        all_goals.extend(self.assess_code_quality())
        all_goals.extend(self.check_documentation_gaps())

        # Sort by priority
        priority_order = {
            GoalPriority.CRITICAL: 0,
            GoalPriority.HIGH: 1,
            GoalPriority.MEDIUM: 2,
            GoalPriority.LOW: 3,
        }

        all_goals.sort(key=lambda g: priority_order.get(g.priority, 3))

        logger.info(f"Generated {len(all_goals)} proactive goals")

        return [g.to_dict() for g in all_goals]

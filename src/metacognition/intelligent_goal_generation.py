from __future__ import annotations

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from .proactive_goals import GoalCategory, GoalPriority, ProactiveGoal


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
Intelligent Goal Generation Engine for OmniMind.

This module transforms reactive goal generation into proactive, intelligent
goal creation with:
- Repository deep analysis (AST parsing, dependency graphs)
- ML-based impact prediction
- Intelligent prioritization with impact scoring
- Integration with metacognition for self-improvement
"""


logger = logging.getLogger(__name__)


@dataclass
class ImpactMetrics:
    """Metrics for goal impact prediction."""

    code_coverage_impact: float = 0.0  # 0-1
    performance_impact: float = 0.0  # 0-1
    security_impact: float = 0.0  # 0-1
    maintainability_impact: float = 0.0  # 0-1
    user_value_impact: float = 0.0  # 0-1
    effort_vs_impact_ratio: float = 0.0  # higher is better
    confidence: float = 0.0  # 0-1

    def get_total_impact(self) -> float:
        """Calculate weighted total impact score."""
        weights = {
            "code_coverage": 0.15,
            "performance": 0.25,
            "security": 0.30,
            "maintainability": 0.15,
            "user_value": 0.15,
        }
        return (
            self.code_coverage_impact * weights["code_coverage"]
            + self.performance_impact * weights["performance"]
            + self.security_impact * weights["security"]
            + self.maintainability_impact * weights["maintainability"]
            + self.user_value_impact * weights["user_value"]
        )

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "code_coverage_impact": self.code_coverage_impact,
            "performance_impact": self.performance_impact,
            "security_impact": self.security_impact,
            "maintainability_impact": self.maintainability_impact,
            "user_value_impact": self.user_value_impact,
            "effort_vs_impact_ratio": self.effort_vs_impact_ratio,
            "total_impact": self.get_total_impact(),
            "confidence": self.confidence,
        }


@dataclass
class RepositoryAnalysis:
    """Comprehensive repository analysis results."""

    total_files: int = 0
    total_lines: int = 0
    modules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    dependencies: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    complexity_hotspots: List[Tuple[str, str, int]] = field(default_factory=list)
    untested_modules: List[str] = field(default_factory=list)
    security_concerns: List[Tuple[str, str, str]] = field(default_factory=list)
    performance_bottlenecks: List[Tuple[str, str, str]] = field(default_factory=list)


class CodeAnalyzer:
    """Analyzes code structure and quality."""

    def __init__(self, workspace_path: Path):
        """Initialize code analyzer.

        Args:
            workspace_path: Path to repository root
        """
        self.workspace_path = workspace_path
        self.src_path = workspace_path / "src"

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single Python file.

        Args:
            file_path: Path to Python file

        Returns:
            Analysis results dictionary
        """
        try:
            source = self._read_file_content(file_path)
            tree = ast.parse(source)

            # Extract information
            classes = self._extract_classes(tree)
            functions = self._extract_functions(tree)
            imports = self._extract_imports(tree)
            complexity = self._calculate_complexity(tree)

            return {
                "lines": len(source.split("\n")),
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "complexity": complexity,
                "has_docstring": ast.get_docstring(tree) is not None,
            }

        except Exception as exc:
            logger.warning(f"Failed to analyze {file_path}: {exc}")
            return self._create_empty_analysis()

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content safely."""
        with open(file_path) as f:
            return f.read()

    def _extract_classes(self, tree: ast.AST) -> List[str]:
        """Extract class names from AST."""
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """Extract function names from AST."""
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract import statements from AST."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def _create_empty_analysis(self) -> Dict[str, Any]:
        """Create empty analysis result for failed analysis."""
        return {
            "lines": 0,
            "classes": [],
            "functions": [],
            "imports": [],
            "complexity": 0,
            "has_docstring": False,
        }

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity.

        Args:
            tree: AST tree

        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity

    def analyze_repository(self) -> RepositoryAnalysis:
        """Analyze entire repository.

        Returns:
            RepositoryAnalysis object
        """
        analysis = RepositoryAnalysis()

        if not self.src_path.exists():
            logger.warning(f"Source path not found: {self.src_path}")
            return analysis

        python_files = list(self.src_path.rglob("*.py"))
        analysis.total_files = len(python_files)

        for py_file in python_files:
            rel_path = str(py_file.relative_to(self.workspace_path))
            file_analysis = self.analyze_file(py_file)

            analysis.total_lines += file_analysis["lines"]
            analysis.modules[rel_path] = file_analysis

            # Track dependencies
            for imp in file_analysis["imports"]:
                analysis.dependencies[rel_path].add(imp)

            # Detect complexity hotspots (complexity > 10)
            if file_analysis["complexity"] > 10:
                for func in file_analysis["functions"]:
                    analysis.complexity_hotspots.append(
                        (rel_path, func, file_analysis["complexity"])
                    )

            # Check for missing docstrings
            if not file_analysis["has_docstring"]:
                analysis.untested_modules.append(rel_path)

        # Sort complexity hotspots
        analysis.complexity_hotspots.sort(key=lambda x: x[2], reverse=True)

        logger.info(
            f"Repository analysis complete: {analysis.total_files} files, "
            f"{analysis.total_lines} lines, {len(analysis.complexity_hotspots)} hotspots"
        )

        return analysis


class ImpactPredictor:
    """ML-based impact prediction for goals."""

    def __init__(self) -> None:
        """Initialize impact predictor."""
        self.historical_goals: List[Dict[str, Any]] = []
        self.model_trained = False

    def predict_impact(
        self,
        goal_category: str,
        goal_description: str,
        repository_analysis: RepositoryAnalysis,
        current_metrics: Optional[Dict[str, float]] = None,
    ) -> ImpactMetrics:
        """Predict impact of a proposed goal.

        Args:
            goal_category: Category of the goal
            goal_description: Description of the goal
            repository_analysis: Current repository analysis
            current_metrics: Current system metrics

        Returns:
            ImpactMetrics with predictions
        """
        current_metrics = current_metrics or {}
        impact = ImpactMetrics()

        # Category-based impact estimation
        self._set_category_impacts(impact, goal_category)

        # Adjust based on repository state
        self._adjust_for_repository_state(impact, goal_description, repository_analysis)

        # Normalize values to 0-1
        self._normalize_impact_values(impact)

        # Calculate effort vs impact ratio
        effort_estimate = self._estimate_effort(goal_description)
        total_impact = impact.get_total_impact()
        impact.effort_vs_impact_ratio = total_impact / max(effort_estimate, 0.1)

        return impact

    def _set_category_impacts(self, impact: ImpactMetrics, goal_category: str) -> None:
        """Set impact values based on goal category."""
        category_impacts = {
            GoalCategory.SECURITY: {
                "security_impact": 0.9,
                "user_value_impact": 0.7,
                "confidence": 0.85,
            },
            GoalCategory.PERFORMANCE: {
                "performance_impact": 0.8,
                "user_value_impact": 0.8,
                "confidence": 0.75,
            },
            GoalCategory.TESTING: {
                "code_coverage_impact": 0.9,
                "maintainability_impact": 0.6,
                "confidence": 0.9,
            },
            GoalCategory.QUALITY: {
                "maintainability_impact": 0.8,
                "code_coverage_impact": 0.4,
                "confidence": 0.8,
            },
            GoalCategory.DOCUMENTATION: {
                "maintainability_impact": 0.6,
                "user_value_impact": 0.5,
                "confidence": 0.7,
            },
        }

        category_data = category_impacts.get(goal_category, {})
        for attr, value in category_data.items():
            setattr(impact, attr, value)

    def _adjust_for_repository_state(
        self, impact: ImpactMetrics, goal_description: str, repository_analysis: RepositoryAnalysis
    ) -> None:
        """Adjust impact based on current repository state."""
        desc_lower = goal_description.lower()

        # Adjust for complexity hotspots
        if repository_analysis.complexity_hotspots:
            if self._is_refactoring_goal(desc_lower):
                impact.performance_impact += 0.1
                impact.maintainability_impact += 0.2

        # Adjust for untested modules
        if repository_analysis.untested_modules:
            if "test" in desc_lower:
                impact.code_coverage_impact += 0.1

    def _is_refactoring_goal(self, description_lower: str) -> bool:
        """Check if goal description indicates refactoring."""
        return "refactor" in description_lower or "optimize" in description_lower

    def _normalize_impact_values(self, impact: ImpactMetrics) -> None:
        """Normalize all impact values to 0-1 range."""
        impact.code_coverage_impact = min(1.0, impact.code_coverage_impact)
        impact.performance_impact = min(1.0, impact.performance_impact)
        impact.security_impact = min(1.0, impact.security_impact)
        impact.maintainability_impact = min(1.0, impact.maintainability_impact)
        impact.user_value_impact = min(1.0, impact.user_value_impact)

    def _estimate_effort(self, description: str) -> float:
        """Estimate effort for a goal (1-10 scale).

        Args:
            description: Goal description

        Returns:
            Effort estimate
        """
        description_lower = description.lower()

        # Keywords indicating high effort
        high_effort_keywords = [
            "refactor",
            "rewrite",
            "implement",
            "design",
            "architect",
        ]
        medium_effort_keywords = ["add", "enhance", "improve", "optimize"]
        low_effort_keywords = ["fix", "update", "adjust", "modify"]

        if any(keyword in description_lower for keyword in high_effort_keywords):
            return 8.0
        elif any(keyword in description_lower for keyword in medium_effort_keywords):
            return 5.0
        elif any(keyword in description_lower for keyword in low_effort_keywords):
            return 2.0

        return 5.0  # Default medium effort

    def learn_from_goal(self, goal: Dict[str, Any], actual_impact: Dict[str, float]) -> None:
        """Learn from completed goal to improve predictions.

        Args:
            goal: Goal that was completed
            actual_impact: Actual impact metrics achieved
        """
        self.historical_goals.append({"goal": goal, "actual_impact": actual_impact})

        # In a real implementation, this would update an ML model
        # For now, we store for future training
        logger.info(f"Learned from goal: {goal['title']}")


class IntelligentGoalEngine:
    """Intelligent proactive goal generation engine."""

    def __init__(self, workspace_path: str = "."):
        """Initialize intelligent goal engine.

        Args:
            workspace_path: Path to repository root
        """
        self.workspace_path = Path(workspace_path)
        self.code_analyzer = CodeAnalyzer(self.workspace_path)
        self.impact_predictor = ImpactPredictor()
        self._goal_counter = 0

    def _generate_id(self) -> str:
        """Generate unique goal ID."""
        self._goal_counter += 1
        return f"GOAL-{datetime.now().strftime('%Y%m%d')}-{self._goal_counter:03d}"

    def analyze_and_generate_goals(
        self, current_metrics: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze repository and generate intelligent goals.

        Args:
            current_metrics: Current system metrics

        Returns:
            List of prioritized goals with impact predictions
        """
        logger.info("Starting intelligent goal generation...")

        # Analyze repository
        repo_analysis = self.code_analyzer.analyze_repository()

        goals_with_impact = []

        # Generate goals based on analysis
        goals_with_impact.extend(
            self._generate_complexity_reduction_goals(repo_analysis, current_metrics)
        )
        goals_with_impact.extend(self._generate_test_coverage_goals(repo_analysis, current_metrics))
        goals_with_impact.extend(
            self._generate_architecture_improvement_goals(repo_analysis, current_metrics)
        )
        goals_with_impact.extend(
            self._generate_security_hardening_goals(repo_analysis, current_metrics)
        )

        # Sort by impact score
        goals_with_impact.sort(key=lambda x: x["impact_metrics"]["total_impact"], reverse=True)

        logger.info(f"Generated {len(goals_with_impact)} intelligent goals")

        return goals_with_impact

    def _generate_complexity_reduction_goals(
        self, analysis: RepositoryAnalysis, metrics: Optional[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate goals for reducing code complexity.

        Args:
            analysis: Repository analysis
            metrics: Current metrics

        Returns:
            List of complexity reduction goals
        """
        goals = []

        if analysis.complexity_hotspots:
            # Take top 3 most complex modules
            for file_path, func_name, complexity in analysis.complexity_hotspots[:3]:
                goal = ProactiveGoal(
                    goal_id=self._generate_id(),
                    title=f"Refactor high-complexity function: {func_name}",
                    description=(
                        f"Function '{func_name}' in {file_path} has cyclomatic "
                        f"complexity of {complexity}, which exceeds recommended "
                        f"threshold of 10. Refactoring will improve maintainability."
                    ),
                    category=GoalCategory.QUALITY,
                    priority=(GoalPriority.HIGH if complexity > 20 else GoalPriority.MEDIUM),
                    estimated_effort=f"{max(1, complexity // 5)} days",
                    acceptance_criteria=[
                        "Reduce complexity to <10",
                        "Maintain 100% test coverage",
                        "No regression in functionality",
                    ],
                    implementation_steps=[
                        "Extract complex logic into smaller functions",
                        "Apply Extract Method refactoring pattern",
                        "Add unit tests for new functions",
                        "Verify performance is maintained",
                    ],
                    metrics={"current_complexity": complexity, "target_complexity": 10},
                )

                impact = self.impact_predictor.predict_impact(
                    goal.category, goal.description, analysis, metrics
                )

                goals.append({**goal.to_dict(), "impact_metrics": impact.to_dict()})

        return goals

    def _generate_test_coverage_goals(
        self, analysis: RepositoryAnalysis, metrics: Optional[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate goals for improving test coverage.

        Args:
            analysis: Repository analysis
            metrics: Current metrics

        Returns:
            List of test coverage goals
        """
        goals = []

        if analysis.untested_modules:
            # Group untested modules by directory
            module_groups = defaultdict(list)
            for module in analysis.untested_modules:
                directory = str(Path(module).parent)
                module_groups[directory].append(module)

            # Create goals for top 3 directories with most untested modules
            for directory, modules in sorted(
                module_groups.items(), key=lambda x: len(x[1]), reverse=True
            )[:3]:
                goal = ProactiveGoal(
                    goal_id=self._generate_id(),
                    title=f"Add test coverage for {directory}",
                    description=(
                        f"Directory '{directory}' has {len(modules)} modules without "
                        f"docstrings or tests. Improving coverage will increase "
                        f"maintainability and reduce bugs."
                    ),
                    category=GoalCategory.TESTING,
                    priority=GoalPriority.HIGH,
                    estimated_effort=f"{len(modules)} days",
                    acceptance_criteria=[
                        f">=80% test coverage for all modules in {directory}",
                        "All critical paths tested",
                        "Edge cases covered",
                    ],
                    implementation_steps=[
                        "Identify critical functions in each module",
                        "Write unit tests for core functionality",
                        "Add integration tests for module interactions",
                        "Verify coverage meets threshold",
                    ],
                    metrics={"untested_modules": len(modules), "directory": directory},
                )

                impact = self.impact_predictor.predict_impact(
                    goal.category, goal.description, analysis, metrics
                )

                goals.append({**goal.to_dict(), "impact_metrics": impact.to_dict()})

        return goals

    def _generate_architecture_improvement_goals(
        self, analysis: RepositoryAnalysis, metrics: Optional[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate goals for architecture improvements.

        Args:
            analysis: Repository analysis
            metrics: Current metrics

        Returns:
            List of architecture improvement goals
        """
        goals = []

        # Detect circular dependencies
        circular_deps = self._detect_circular_dependencies(analysis.dependencies)

        if circular_deps:
            goal = ProactiveGoal(
                goal_id=self._generate_id(),
                title="Resolve circular dependencies",
                description=(
                    f"Found {len(circular_deps)} circular dependency chains "
                    f"that create tight coupling and reduce maintainability."
                ),
                category=GoalCategory.ARCHITECTURE,
                priority=GoalPriority.HIGH,
                estimated_effort="3-5 days",
                acceptance_criteria=[
                    "Zero circular dependencies detected",
                    "Dependency graph is acyclic",
                    "All tests pass",
                ],
                implementation_steps=[
                    "Map current dependency graph",
                    "Identify breaking points for cycles",
                    "Refactor to dependency injection where appropriate",
                    "Validate with static analysis tools",
                ],
                metrics={"circular_dependencies": len(circular_deps)},
            )

            impact = self.impact_predictor.predict_impact(
                goal.category, goal.description, analysis, metrics
            )

            goals.append({**goal.to_dict(), "impact_metrics": impact.to_dict()})

        return goals

    def _generate_security_hardening_goals(
        self, analysis: RepositoryAnalysis, metrics: Optional[Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """Generate goals for security hardening.

        Args:
            analysis: Repository analysis
            metrics: Current metrics

        Returns:
            List of security hardening goals
        """
        goals = []

        # Check for potential security issues
        security_keywords = ["eval", "exec", "pickle", "yaml.load", "subprocess"]
        modules_with_security_concerns = []

        for module_path, module_info in analysis.modules.items():
            # This is a simplified check - would need more sophisticated analysis
            if any(
                keyword in str(module_info.get("functions", [])) for keyword in security_keywords
            ):
                modules_with_security_concerns.append(module_path)

        if modules_with_security_concerns:
            goal = ProactiveGoal(
                goal_id=self._generate_id(),
                title="Security audit and hardening",
                description=(
                    f"Found {len(modules_with_security_concerns)} modules with "
                    f"potential security concerns requiring review."
                ),
                category=GoalCategory.SECURITY,
                priority=GoalPriority.CRITICAL,
                estimated_effort="2-3 days",
                acceptance_criteria=[
                    "All dangerous operations validated",
                    "Input sanitization implemented",
                    "Security audit passed",
                ],
                implementation_steps=[
                    "Review each flagged module for security issues",
                    "Replace unsafe operations with safe alternatives",
                    "Add input validation and sanitization",
                    "Run security scanning tools",
                ],
                metrics={"modules_to_review": len(modules_with_security_concerns)},
            )

            impact = self.impact_predictor.predict_impact(
                goal.category, goal.description, analysis, metrics
            )

            goals.append({**goal.to_dict(), "impact_metrics": impact.to_dict()})

        return goals

    def _detect_circular_dependencies(self, dependencies: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect circular dependencies in module graph.

        Args:
            dependencies: Module dependency graph

        Returns:
            List of circular dependency chains
        """
        # Simplified cycle detection using DFS
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in dependencies.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for node in dependencies:
            if node not in visited:
                dfs(node, [])

        return cycles

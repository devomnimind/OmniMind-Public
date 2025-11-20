"""
AI-Powered Automated Code Review System for OmniMind.

Provides comprehensive code analysis with:
- Static analysis (AST parsing, complexity metrics)
- Security vulnerability detection
- Code quality scoring
- Best practice validation
- Automated fix suggestions
- Pattern detection
- Performance analysis
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IssueSeverity(str, Enum):
    """Code review issue severity."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(str, Enum):
    """Code review issue category."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    COMPLEXITY = "complexity"
    MAINTAINABILITY = "maintainability"
    DOCUMENTATION = "documentation"
    TYPE_SAFETY = "type_safety"
    ERROR_HANDLING = "error_handling"


@dataclass
class CodeIssue:
    """Individual code review issue."""

    line_number: int
    severity: IssueSeverity
    category: IssueCategory
    message: str
    suggestion: Optional[str] = None
    auto_fix: Optional[str] = None
    rule_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "line": self.line_number,
            "severity": self.severity.value,
            "category": self.category.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "auto_fix": self.auto_fix,
            "rule_id": self.rule_id,
        }


@dataclass
class CodeMetrics:
    """Code quality metrics."""

    lines_of_code: int
    comment_lines: int
    blank_lines: int
    complexity: int
    maintainability_index: float
    test_coverage: float = 0.0
    type_hint_coverage: float = 0.0
    docstring_coverage: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "lines_of_code": self.lines_of_code,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "complexity": self.complexity,
            "maintainability_index": self.maintainability_index,
            "test_coverage": self.test_coverage,
            "type_hint_coverage": self.type_hint_coverage,
            "docstring_coverage": self.docstring_coverage,
        }


@dataclass
class ReviewResult:
    """Complete code review result."""

    file_path: str
    timestamp: str
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Optional[CodeMetrics] = None
    overall_score: float = 0.0
    passed: bool = False

    def add_issue(
        self,
        line: int,
        severity: IssueSeverity,
        category: IssueCategory,
        message: str,
        suggestion: Optional[str] = None,
        auto_fix: Optional[str] = None,
        rule_id: Optional[str] = None,
    ) -> None:
        """Add a code issue."""
        issue = CodeIssue(
            line_number=line,
            severity=severity,
            category=category,
            message=message,
            suggestion=suggestion,
            auto_fix=auto_fix,
            rule_id=rule_id,
        )
        self.issues.append(issue)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "timestamp": self.timestamp,
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "overall_score": self.overall_score,
            "passed": self.passed,
            "summary": {
                "total_issues": len(self.issues),
                "critical": sum(
                    1 for i in self.issues if i.severity == IssueSeverity.CRITICAL
                ),
                "errors": sum(
                    1 for i in self.issues if i.severity == IssueSeverity.ERROR
                ),
                "warnings": sum(
                    1 for i in self.issues if i.severity == IssueSeverity.WARNING
                ),
                "info": sum(1 for i in self.issues if i.severity == IssueSeverity.INFO),
            },
        }


class AutomatedCodeReviewer:
    """AI-powered automated code reviewer."""

    def __init__(self, min_score: float = 8.0, max_complexity: int = 10) -> None:
        """
        Initialize code reviewer.

        Args:
            min_score: Minimum acceptable quality score
            max_complexity: Maximum acceptable cyclomatic complexity
        """
        self.min_score = min_score
        self.max_complexity = max_complexity

    def review_file(self, file_path: Path) -> ReviewResult:
        """
        Review a Python file.

        Args:
            file_path: Path to file to review

        Returns:
            Review result with issues and metrics
        """
        logger.info(f"Reviewing {file_path}")

        result = ReviewResult(
            file_path=str(file_path),
            timestamp=datetime.now().isoformat(),
        )

        # Read file content
        try:
            code = file_path.read_text()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            result.add_issue(
                line=0,
                severity=IssueSeverity.CRITICAL,
                category=IssueCategory.MAINTAINABILITY,
                message=f"Failed to read file: {e}",
            )
            return result

        # Calculate metrics
        result.metrics = self._calculate_metrics(code)

        # Run all checks
        self._check_security(code, result)
        self._check_style(code, result)
        self._check_complexity(code, result)
        self._check_documentation(code, result)
        self._check_type_hints(code, result)
        self._check_error_handling(code, result)
        self._check_performance(code, result)
        self._check_best_practices(code, result)

        # Calculate overall score
        result.overall_score = self._calculate_score(result)
        result.passed = result.overall_score >= self.min_score

        logger.info(
            f"Review complete: {result.overall_score:.1f}/10.0 "
            f"({len(result.issues)} issues)"
        )

        return result

    def _calculate_metrics(self, code: str) -> CodeMetrics:
        """Calculate code metrics."""
        lines = code.split("\n")
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        code_lines = total_lines - blank_lines - comment_lines

        # Calculate cyclomatic complexity
        complexity = self._calculate_complexity(code)

        # Calculate maintainability index (simplified)
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Where V is Halstead Volume, G is cyclomatic complexity, LOC is lines of code
        # Simplified version: based on complexity and size
        maintainability = max(0, min(100, 100 - (complexity * 2) - (code_lines / 100)))

        # Calculate type hint coverage
        type_hint_coverage = self._calculate_type_hint_coverage(code)

        # Calculate docstring coverage
        docstring_coverage = self._calculate_docstring_coverage(code)

        return CodeMetrics(
            lines_of_code=code_lines,
            comment_lines=comment_lines,
            blank_lines=blank_lines,
            complexity=complexity,
            maintainability_index=maintainability,
            type_hint_coverage=type_hint_coverage,
            docstring_coverage=docstring_coverage,
        )

    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        try:
            tree = ast.parse(code)
            complexity = 1  # Base complexity

            for node in ast.walk(tree):
                if isinstance(
                    node,
                    (
                        ast.If,
                        ast.While,
                        ast.For,
                        ast.ExceptHandler,
                        ast.With,
                        ast.Assert,
                    ),
                ):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1

            return complexity

        except Exception:
            return 0

    def _calculate_type_hint_coverage(self, code: str) -> float:
        """Calculate percentage of functions with type hints."""
        try:
            tree = ast.parse(code)
            total_funcs = 0
            typed_funcs = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_funcs += 1
                    # Check if function has return type annotation
                    if node.returns is not None:
                        typed_funcs += 1
                    # Check if args have type annotations
                    elif any(arg.annotation is not None for arg in node.args.args):
                        typed_funcs += 1

            return (typed_funcs / total_funcs * 100) if total_funcs > 0 else 0.0

        except Exception:
            return 0.0

    def _calculate_docstring_coverage(self, code: str) -> float:
        """Calculate percentage of functions/classes with docstrings."""
        try:
            tree = ast.parse(code)
            total_items = 0
            documented_items = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    total_items += 1
                    if ast.get_docstring(node):
                        documented_items += 1

            return (documented_items / total_items * 100) if total_items > 0 else 0.0

        except Exception:
            return 0.0

    def _check_security(self, code: str, result: ReviewResult) -> None:
        """Check for security vulnerabilities."""
        lines = code.split("\n")

        # Check for dangerous functions
        dangerous_funcs = ["eval", "exec", "compile", "__import__"]
        for i, line in enumerate(lines, 1):
            for func in dangerous_funcs:
                if re.search(rf"\b{func}\s*\(", line):
                    result.add_issue(
                        line=i,
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        message=f"Dangerous function '{func}' detected",
                        suggestion=f"Avoid using {func} - use safer alternatives",
                        rule_id="SEC001",
                    )

        # Check for SQL injection risks
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "DROP"]
        for i, line in enumerate(lines, 1):
            if any(keyword in line.upper() for keyword in sql_keywords):
                if "%" in line or ".format(" in line or "f'" in line:
                    result.add_issue(
                        line=i,
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.SECURITY,
                        message="Potential SQL injection vulnerability",
                        suggestion="Use parameterized queries instead of string formatting",
                        rule_id="SEC002",
                    )

        # Check for hardcoded secrets
        secret_patterns = [
            (r"password\s*=\s*['\"][\w]+['\"]", "Hardcoded password"),
            (r"api[_-]?key\s*=\s*['\"][\w]+['\"]", "Hardcoded API key"),
            (r"token\s*=\s*['\"][\w]+['\"]", "Hardcoded token"),
            (r"secret\s*=\s*['\"][\w]+['\"]", "Hardcoded secret"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, message in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    result.add_issue(
                        line=i,
                        severity=IssueSeverity.CRITICAL,
                        category=IssueCategory.SECURITY,
                        message=message,
                        suggestion="Use environment variables or secure config",
                        rule_id="SEC003",
                    )

    def _check_style(self, code: str, result: ReviewResult) -> None:
        """Check code style."""
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Line length
            if len(line) > 100:
                result.add_issue(
                    line=i,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.STYLE,
                    message=f"Line too long ({len(line)} > 100 characters)",
                    suggestion="Break line into multiple lines",
                    rule_id="STY001",
                )

            # Multiple statements on one line
            if ";" in line and not line.strip().startswith("#"):
                result.add_issue(
                    line=i,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.STYLE,
                    message="Multiple statements on one line",
                    suggestion="Use separate lines for each statement",
                    rule_id="STY002",
                )

    def _check_complexity(self, code: str, result: ReviewResult) -> None:
        """Check code complexity."""
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Calculate function complexity
                    func_complexity = self._calculate_function_complexity(node)

                    if func_complexity > self.max_complexity:
                        result.add_issue(
                            line=node.lineno,
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.COMPLEXITY,
                            message=(
                                f"Function '{node.name}' is too complex "
                                f"(complexity: {func_complexity})"
                            ),
                            suggestion="Break function into smaller functions",
                            rule_id="CMP001",
                        )

        except Exception as e:
            logger.debug(f"Complexity check failed: {e}")

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Calculate complexity of a single function."""
        complexity = 1

        for node in ast.walk(func_node):
            if isinstance(
                node,
                (
                    ast.If,
                    ast.While,
                    ast.For,
                    ast.ExceptHandler,
                    ast.With,
                    ast.Assert,
                ),
            ):
                complexity += 1

        return complexity

    def _check_documentation(self, code: str, result: ReviewResult) -> None:
        """Check documentation quality."""
        try:
            tree = ast.parse(code)

            # Check module docstring
            module_docstring = ast.get_docstring(tree)
            if not module_docstring:
                result.add_issue(
                    line=1,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.DOCUMENTATION,
                    message="Missing module docstring",
                    suggestion='Add module docstring: """Description of module."""',
                    rule_id="DOC001",
                )

            # Check function/class docstrings
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith("_"):  # Skip private
                        docstring = ast.get_docstring(node)
                        if not docstring:
                            result.add_issue(
                                line=node.lineno,
                                severity=IssueSeverity.INFO,
                                category=IssueCategory.DOCUMENTATION,
                                message=(
                                    f"Missing docstring for {node.__class__.__name__} "
                                    f"'{node.name}'"
                                ),
                                suggestion="Add Google-style docstring",
                                rule_id="DOC002",
                            )

        except Exception as e:
            logger.debug(f"Documentation check failed: {e}")

    def _check_type_hints(self, code: str, result: ReviewResult) -> None:
        """Check type hint usage."""
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):  # Skip private
                        # Check return type
                        if node.returns is None:
                            result.add_issue(
                                line=node.lineno,
                                severity=IssueSeverity.INFO,
                                category=IssueCategory.TYPE_SAFETY,
                                message=f"Function '{node.name}' missing return type hint",
                                suggestion="Add return type: -> ReturnType:",
                                rule_id="TYP001",
                            )

                        # Check parameter types
                        for arg in node.args.args:
                            if arg.arg != "self" and arg.annotation is None:
                                result.add_issue(
                                    line=node.lineno,
                                    severity=IssueSeverity.INFO,
                                    category=IssueCategory.TYPE_SAFETY,
                                    message=f"Parameter '{arg.arg}' missing type hint",
                                    suggestion="Add type hint: param: Type",
                                    rule_id="TYP002",
                                )

        except Exception as e:
            logger.debug(f"Type hint check failed: {e}")

    def _check_error_handling(self, code: str, result: ReviewResult) -> None:
        """Check error handling."""
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Bare except
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        result.add_issue(
                            line=node.lineno,
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.ERROR_HANDLING,
                            message="Bare 'except:' clause",
                            suggestion="Catch specific exceptions: except Exception:",
                            rule_id="ERR001",
                        )

                # Pass in except
                if isinstance(node, ast.ExceptHandler):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        result.add_issue(
                            line=node.lineno,
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.ERROR_HANDLING,
                            message="Empty except clause (pass)",
                            suggestion="Add logging or proper error handling",
                            rule_id="ERR002",
                        )

        except Exception as e:
            logger.debug(f"Error handling check failed: {e}")

    def _check_performance(self, code: str, result: ReviewResult) -> None:
        """Check for performance issues."""
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # String concatenation in loops
            if "for " in line or "while " in line:
                # Check next few lines for string concatenation
                for j in range(i, min(i + 10, len(lines))):
                    if "+=" in lines[j] and '"' in lines[j]:
                        result.add_issue(
                            line=j + 1,
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.PERFORMANCE,
                            message="String concatenation in loop",
                            suggestion="Use list and ''.join() instead",
                            rule_id="PERF001",
                        )
                        break

    def _check_best_practices(self, code: str, result: ReviewResult) -> None:
        """Check Python best practices."""
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Mutable default arguments
            if "def " in line and ("=[]" in line or "={}" in line):
                result.add_issue(
                    line=i,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.MAINTAINABILITY,
                    message="Mutable default argument",
                    suggestion="Use None as default, create mutable in function body",
                    rule_id="BP001",
                )

    def _calculate_score(self, result: ReviewResult) -> float:
        """Calculate overall code quality score."""
        # Base score
        score = 10.0

        # Deduct points based on issues
        severity_weights = {
            IssueSeverity.CRITICAL: 2.0,
            IssueSeverity.ERROR: 1.0,
            IssueSeverity.WARNING: 0.5,
            IssueSeverity.INFO: 0.1,
        }

        for issue in result.issues:
            score -= severity_weights.get(issue.severity, 0.1)

        # Bonus for good metrics
        if result.metrics:
            if result.metrics.type_hint_coverage >= 90:
                score += 0.5
            if result.metrics.docstring_coverage >= 90:
                score += 0.5
            if result.metrics.complexity <= 5:
                score += 0.5

        return max(0.0, min(10.0, score))

    def generate_report(
        self, result: ReviewResult, output_file: Optional[Path] = None
    ) -> str:
        """
        Generate code review report.

        Args:
            result: Review result
            output_file: Optional output file

        Returns:
            Report as string
        """
        lines = []
        lines.append(f"# Code Review Report: {result.file_path}\n")
        lines.append(f"Generated: {result.timestamp}\n")
        lines.append(f"Overall Score: {result.overall_score:.1f}/10.0\n")
        lines.append(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}\n")

        # Metrics
        if result.metrics:
            lines.append("\n## Metrics\n")
            lines.append(f"- Lines of Code: {result.metrics.lines_of_code}")
            lines.append(f"- Complexity: {result.metrics.complexity}")
            lines.append(
                f"- Maintainability Index: {result.metrics.maintainability_index:.1f}/100"
            )
            lines.append(
                f"- Type Hint Coverage: {result.metrics.type_hint_coverage:.1f}%"
            )
            lines.append(
                f"- Docstring Coverage: {result.metrics.docstring_coverage:.1f}%"
            )

        # Issues summary
        summary = result.to_dict()["summary"]
        lines.append("\n## Issues Summary\n")
        lines.append(f"- Total: {summary['total_issues']}")
        lines.append(f"- Critical: {summary['critical']}")
        lines.append(f"- Errors: {summary['errors']}")
        lines.append(f"- Warnings: {summary['warnings']}")
        lines.append(f"- Info: {summary['info']}")

        # Detailed issues
        if result.issues:
            lines.append("\n## Issues Details\n")

            # Group by severity
            by_severity: Dict[IssueSeverity, List[CodeIssue]] = {}
            for issue in result.issues:
                by_severity.setdefault(issue.severity, []).append(issue)

            for severity in IssueSeverity:
                issues = by_severity.get(severity, [])
                if issues:
                    lines.append(f"\n### {severity.value.upper()} ({len(issues)})\n")
                    for issue in issues:
                        lines.append(
                            f"- Line {issue.line_number}: {issue.message} ({issue.category.value})"
                        )
                        if issue.suggestion:
                            lines.append(f"  💡 {issue.suggestion}")
                        if issue.rule_id:
                            lines.append(f"  📋 Rule: {issue.rule_id}")
                        lines.append("")

        report = "\n".join(lines)

        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report)
            logger.info(f"Report saved to {output_file}")

        return report


# Convenience function
def review_code(
    file_path: Path, min_score: float = 8.0, output_report: Optional[Path] = None
) -> ReviewResult:
    """
    Quick code review function.

    Args:
        file_path: Path to file to review
        min_score: Minimum acceptable score
        output_report: Optional output report path

    Returns:
        Review result
    """
    reviewer = AutomatedCodeReviewer(min_score=min_score)
    result = reviewer.review_file(file_path)

    if output_report:
        reviewer.generate_report(result, output_report)

    return result


if __name__ == "__main__":
    # Demo usage
    import sys

    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1])
    else:
        # Review this file
        file_path = Path(__file__)

    print(f"🔍 Reviewing {file_path}...\n")

    result = review_code(
        file_path, min_score=8.0, output_report=Path("logs/code_review_report.md")
    )

    print(f"Score: {result.overall_score:.1f}/10.0")
    print(f"Issues: {len(result.issues)}")
    print(f"Status: {'✅ PASSED' if result.passed else '❌ FAILED'}")

    if result.metrics:
        print("\nMetrics:")
        print(f"  Complexity: {result.metrics.complexity}")
        print(f"  Type Hints: {result.metrics.type_hint_coverage:.1f}%")
        print(f"  Docstrings: {result.metrics.docstring_coverage:.1f}%")

    print("\n📄 Report saved to logs/code_review_report.md")

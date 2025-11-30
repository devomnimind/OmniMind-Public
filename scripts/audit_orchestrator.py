#!/usr/bin/env python3
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
Orchestrator Agent Audit Script

This script performs a comprehensive audit of the OrchestratorAgent to identify:
- Code quality issues
- Performance bottlenecks
- Error handling gaps
- Task delegation failures
- Resource management problems
- Integration issues with MCP/DBus

Usage:
    python scripts/audit_orchestrator.py [--output report.json] [--verbose]

Author: This work was conceived by Fabrício da Silva and implemented with AI assistance from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review and debugging across various models including Gemini and Perplexity AI, under theoretical coordination by the author.
Date: 2025-11-24
"""

import ast
import inspect
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re


class OrchestratorAuditor:
    """Audits the OrchestratorAgent for issues and improvements."""

    def __init__(self, source_path: str):
        self.source_path = Path(source_path)
        self.issues: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}

    def audit(self) -> Dict[str, Any]:
        """Run complete audit."""
        print("🔍 Starting OrchestratorAgent audit...")

        # Read source code
        with open(self.source_path, "r", encoding="utf-8") as f:
            source_code = f.read()

        # Parse AST
        tree = ast.parse(source_code)

        # Run audit checks
        self._audit_error_handling(tree, source_code)
        self._audit_task_delegation(tree, source_code)
        self._audit_resource_management(tree, source_code)
        self._audit_performance_issues(tree, source_code)
        self._audit_integration_points(tree, source_code)
        self._audit_code_quality(tree, source_code)

        # Calculate metrics
        self._calculate_metrics(tree, source_code)

        return {
            "timestamp": "2025-11-24T00:00:00Z",
            "source_file": str(self.source_path),
            "issues_found": len(self.issues),
            "issues": self.issues,
            "metrics": self.metrics,
            "recommendations": self._generate_recommendations(),
        }

    def _audit_error_handling(self, tree: ast.AST, source: str) -> None:
        """Audit error handling patterns."""
        # Find try/except blocks
        try_blocks = []
        except_blocks = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_blocks.append(node)
            elif isinstance(node, ast.ExceptHandler):
                except_blocks.append(node)

        # Check for missing error handling in critical methods
        critical_methods = ["execute_plan", "delegate_task", "run_orchestrated_task"]
        method_nodes = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in critical_methods:
                method_nodes[node.name] = node

        for method_name, method_node in method_nodes.items():
            has_try_except = False
            for child in ast.walk(method_node):
                if isinstance(child, ast.Try):
                    has_try_except = True
                    break

            if not has_try_except:
                self.issues.append(
                    {
                        "type": "error_handling",
                        "severity": "HIGH",
                        "method": method_name,
                        "description": f"Critical method '{method_name}' lacks try/except error handling",
                        "line": method_node.lineno,
                        "recommendation": "Add comprehensive try/except blocks with proper logging",
                    }
                )

        # Check for bare except clauses
        for except_handler in except_blocks:
            if except_handler.type is None:  # bare except
                self.issues.append(
                    {
                        "type": "error_handling",
                        "severity": "MEDIUM",
                        "description": "Bare 'except:' clause found - too broad exception handling",
                        "line": except_handler.lineno,
                        "recommendation": "Specify exception types or use 'Exception' instead of bare except",
                    }
                )

    def _audit_task_delegation(self, tree: ast.AST, source: str) -> None:
        """Audit task delegation logic."""
        # Find delegation-related code
        delegation_patterns = [
            r"delegate.*task",
            r"execute.*subtask",
            r"agent.*mode",
            r"subtask.*agent",
        ]

        for pattern in delegation_patterns:
            matches = re.finditer(pattern, source, re.IGNORECASE)
            for match in matches:
                # Check context around delegation
                start = max(0, match.start() - 200)
                end = min(len(source), match.end() + 200)
                context = source[start:end]

                # Check for error handling in delegation
                if "try:" not in context and "except" not in context:
                    self.issues.append(
                        {
                            "type": "task_delegation",
                            "severity": "MEDIUM",
                            "description": f"Task delegation at line {source[:match.start()].count(chr(10)) + 1} lacks error handling",
                            "line": source[: match.start()].count(chr(10)) + 1,
                            "recommendation": "Add try/except around task delegation calls",
                        }
                    )

        # Check for timeout handling
        if "timeout" not in source.lower():
            self.issues.append(
                {
                    "type": "task_delegation",
                    "severity": "MEDIUM",
                    "description": "No timeout handling found for task delegation",
                    "recommendation": "Implement timeouts for long-running task delegations",
                }
            )

    def _audit_resource_management(self, tree: ast.AST, source: str) -> None:
        """Audit resource management."""
        # Check for resource cleanup
        cleanup_patterns = ["close", "cleanup", "dispose", "__del__", "finally"]
        cleanup_found = any(pattern in source.lower() for pattern in cleanup_patterns)

        if not cleanup_found:
            self.issues.append(
                {
                    "type": "resource_management",
                    "severity": "LOW",
                    "description": "No explicit resource cleanup patterns found",
                    "recommendation": "Add proper cleanup for MCP/DBus connections and background tasks",
                }
            )

        # Check for memory leaks (large data structures)
        large_data_patterns = [r"List\[.*\]", r"Dict\[.*\]", r"history", r"cache"]
        for pattern in large_data_patterns:
            if re.search(pattern, source):
                # Check if there's size limiting
                if "max_" not in source or "limit" not in source:
                    self.issues.append(
                        {
                            "type": "resource_management",
                            "severity": "MEDIUM",
                            "description": f"Potential memory leak with {pattern} - no size limits found",
                            "recommendation": "Implement size limits and cleanup for large data structures",
                        }
                    )
                break

    def _audit_performance_issues(self, tree: ast.AST, source: str) -> None:
        """Audit performance issues."""
        # Check for synchronous I/O in async contexts
        async_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_methods.append(node.name)

        for method in async_methods:
            method_source = source[
                source.find(f"async def {method}") : source.find(
                    f"def {method.split()[0]}", source.find(f"async def {method}") + 1
                )
            ]
            if "await" not in method_source and len(method_source) > 1000:
                self.issues.append(
                    {
                        "type": "performance",
                        "severity": "MEDIUM",
                        "method": method,
                        "description": f"Async method '{method}' may block with synchronous operations",
                        "recommendation": "Use await for I/O operations or consider synchronous implementation",
                    }
                )

        # Check for nested loops
        loop_count = source.count("for ") + source.count("while ")
        if loop_count > 20:
            self.issues.append(
                {
                    "type": "performance",
                    "severity": "LOW",
                    "description": f"High loop count ({loop_count}) may indicate performance issues",
                    "recommendation": "Review loop efficiency and consider vectorization where possible",
                }
            )

    def _audit_integration_points(self, tree: ast.AST, source: str) -> None:
        """Audit integration points (MCP, DBus, etc)."""
        # Check MCP integration
        if "mcp_client" in source:
            if "MCPClientError" not in source:
                self.issues.append(
                    {
                        "type": "integration",
                        "severity": "MEDIUM",
                        "description": "MCP client used but MCPClientError not handled",
                        "recommendation": "Add proper MCP error handling throughout the codebase",
                    }
                )

        # Check DBus integration
        if "dbus_" in source:
            if "DBusSessionController" in source or "DBusSystemController" in source:
                # Check for proper error handling
                dbus_error_patterns = ["DBusError", "dbus_exception", "dbus.*error"]
                has_dbus_error_handling = any(
                    pattern in source.lower() for pattern in dbus_error_patterns
                )
                if not has_dbus_error_handling:
                    self.issues.append(
                        {
                            "type": "integration",
                            "severity": "MEDIUM",
                            "description": "DBus integration lacks comprehensive error handling",
                            "recommendation": "Add DBus-specific exception handling",
                        }
                    )

    def _audit_code_quality(self, tree: ast.AST, source: str) -> None:
        """Audit code quality issues."""
        # Check for TODO comments
        todo_count = source.upper().count("TODO")
        if todo_count > 0:
            self.issues.append(
                {
                    "type": "code_quality",
                    "severity": "LOW",
                    "description": f"{todo_count} TODO comments found - technical debt",
                    "recommendation": "Address TODO items or convert to proper issues",
                }
            )

        # Check for long methods
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno is not None and node.lineno is not None:
                    line_count = node.end_lineno - node.lineno
                    if line_count > 50:
                        self.issues.append(
                            {
                                "type": "code_quality",
                                "severity": "LOW",
                                "method": node.name,
                                "description": f"Method '{node.name}' is {line_count} lines long",
                                "line": node.lineno,
                                "recommendation": "Consider breaking down into smaller methods",
                            }
                        )

        # Check for magic numbers
        magic_numbers = re.findall(r"\b\d{2,}\b", source)
        if len(magic_numbers) > 20:
            self.issues.append(
                {
                    "type": "code_quality",
                    "severity": "LOW",
                    "description": f"Multiple magic numbers found ({len(set(magic_numbers))})",
                    "recommendation": "Replace magic numbers with named constants",
                }
            )

    def _calculate_metrics(self, tree: ast.AST, source: str) -> None:
        """Calculate code metrics."""
        # Count various elements
        self.metrics = {
            "total_lines": len(source.split("\n")),
            "total_chars": len(source),
            "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
            "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
            "async_functions": len(
                [n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
            ),
            "imports": len(
                [
                    n
                    for n in ast.walk(tree)
                    if isinstance(n, ast.Import) or isinstance(n, ast.ImportFrom)
                ]
            ),
            "try_blocks": len([n for n in ast.walk(tree) if isinstance(n, ast.Try)]),
            "with_blocks": len([n for n in ast.walk(tree) if isinstance(n, ast.With)]),
            "complexity_score": self._calculate_complexity(tree),
        }

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate a simple complexity score."""
        score = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                score += 1
            elif isinstance(node, ast.BoolOp):  # and/or
                score += len(node.values) - 1
        return score

    def _generate_recommendations(self) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Group issues by type and severity
        high_priority = [i for i in self.issues if i["severity"] == "HIGH"]
        medium_priority = [i for i in self.issues if i["severity"] == "MEDIUM"]

        if high_priority:
            recommendations.append("🔴 CRITICAL: Address high-priority issues immediately:")
            for issue in high_priority[:3]:  # Top 3
                recommendations.append(f"  - {issue['description']}")

        if medium_priority:
            recommendations.append("🟡 MEDIUM: Review medium-priority issues:")
            for issue in medium_priority[:3]:  # Top 3
                recommendations.append(f"  - {issue['description']}")

        # General recommendations
        recommendations.extend(
            [
                "✅ LOW: Consider code quality improvements for long-term maintainability",
                "🔧 REFACTOR: Break down large methods into smaller, focused functions",
                "🛡️ RELIABILITY: Add comprehensive error handling for all external integrations",
                "📊 MONITORING: Implement detailed metrics collection for task delegation performance",
            ]
        )

        return recommendations


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Audit OrchestratorAgent code")
    parser.add_argument(
        "--source",
        default="src/agents/orchestrator_agent.py",
        help="Source file to audit",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for JSON report",
        default="orchestrator_audit_report.json",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    auditor = OrchestratorAuditor(args.source)
    report = auditor.audit()

    # Save JSON report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    if args.verbose:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Orchestrator audit complete. Report saved to {args.output}")
        print(f"Issues found: {report['issues_found']}")
        print(f"Code metrics: {len(report['metrics'])} measured")

        recommendations = report.get("recommendations", [])
        if recommendations:
            print("\n📋 Key Recommendations:")
            for rec in recommendations[:5]:  # First 5
                print(f"  {rec}")


if __name__ == "__main__":
    main()

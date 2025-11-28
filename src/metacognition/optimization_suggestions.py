from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional


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

"""Optimization suggestions module for metacognition.

Generates actionable optimization suggestions based on self-analysis.
"""


logger = logging.getLogger(__name__)


class OptimizationSuggestion:
    """Represents a single optimization suggestion."""

    def __init__(
        self,
        suggestion_id: str,
        category: str,
        title: str,
        description: str,
        priority: str,
        impact: str,
        implementation: str,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize optimization suggestion.

        Args:
            suggestion_id: Unique identifier
            category: Category (performance, reliability, efficiency, etc.)
            title: Short title
            description: Detailed description
            priority: Priority level (critical, high, medium, low)
            impact: Expected impact (high, medium, low)
            implementation: Implementation guidance
            metrics: Supporting metrics
        """
        self.suggestion_id = suggestion_id
        self.category = category
        self.title = title
        self.description = description
        self.priority = priority
        self.impact = impact
        self.implementation = implementation
        self.metrics = metrics or {}
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "suggestion_id": self.suggestion_id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "impact": self.impact,
            "implementation": self.implementation,
            "metrics": self.metrics,
            "created_at": self.created_at,
        }


class OptimizationSuggestions:
    """Generates optimization suggestions based on analysis."""

    def __init__(self, max_suggestions: int = 10) -> None:
        """Initialize optimization suggestions generator.

        Args:
            max_suggestions: Maximum suggestions to generate
        """
        self.max_suggestions = max_suggestions
        self._suggestion_counter = 0

    def _generate_id(self) -> str:
        """Generate unique suggestion ID."""
        self._suggestion_counter += 1
        return f"OPT-{datetime.now().strftime('%Y%m%d')}-{self._suggestion_counter:03d}"

    def analyze_performance_metrics(
        self, performance_data: Dict[str, Any]
    ) -> List[OptimizationSuggestion]:
        """Generate suggestions based on performance metrics.

        Args:
            performance_data: Performance analysis data

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        # Check for slow tools
        tool_performance = performance_data.get("tool_performance", {})
        for tool, stats in tool_performance.items():
            avg_time = stats.get("avg", 0)
            if avg_time > 5.0:  # > 5 seconds
                suggestions.append(
                    OptimizationSuggestion(
                        suggestion_id=self._generate_id(),
                        category="performance",
                        title=f"Optimize {tool} execution time",
                        description=(
                            f"Tool '{tool}' has an average execution time of "
                            f"{avg_time:.2f}s, which is above the acceptable threshold."
                        ),
                        priority="high" if avg_time > 10 else "medium",
                        impact="high",
                        implementation=(
                            "Consider:\n"
                            "1. Implementing caching for repeated operations\n"
                            "2. Optimizing data structures or algorithms\n"
                            "3. Parallelizing operations where possible\n"
                            "4. Profiling to identify bottlenecks"
                        ),
                        metrics={"current_avg": avg_time, "target": 2.0},
                    )
                )

        return suggestions

    def analyze_failure_patterns(
        self, failure_data: Dict[str, Any]
    ) -> List[OptimizationSuggestion]:
        """Generate suggestions based on failure patterns.

        Args:
            failure_data: Failure analysis data

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        failure_by_tool = dict(failure_data.get("failure_by_tool", []))
        total_failures = failure_data.get("total_failures", 0)

        for tool, count in failure_by_tool.items():
            if count >= 5:  # Significant number of failures
                failure_rate = count / total_failures if total_failures > 0 else 0
                suggestions.append(
                    OptimizationSuggestion(
                        suggestion_id=self._generate_id(),
                        category="reliability",
                        title=f"Improve {tool} reliability",
                        description=(
                            f"Tool '{tool}' has failed {count} times, accounting for "
                            f"{failure_rate * 100:.1f}% of all failures."
                        ),
                        priority="critical" if count > 10 else "high",
                        impact="high",
                        implementation=(
                            "Recommended actions:\n"
                            "1. Add more robust error handling\n"
                            "2. Implement retry logic with exponential backoff\n"
                            "3. Add input validation\n"
                            "4. Review and fix common failure scenarios"
                        ),
                        metrics={"failure_count": count, "failure_rate": failure_rate},
                    )
                )

        return suggestions

    def analyze_bias_patterns(self, bias_data: Dict[str, Any]) -> List[OptimizationSuggestion]:
        """Generate suggestions based on detected biases.

        Args:
            bias_data: Bias analysis data

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        biases = bias_data.get("biases", [])

        for bias in biases:
            if bias.get("severity") == "high":
                suggestions.append(
                    OptimizationSuggestion(
                        suggestion_id=self._generate_id(),
                        category="diversity",
                        title=f"Reduce {bias['type']} selection bias",
                        description=(
                            f"High bias detected in {bias['type']} selection. "
                            f"'{bias['name']}' is used {bias['usage_ratio'] * 100:.1f}% "
                            f"of the time."
                        ),
                        priority="medium",
                        impact="medium",
                        implementation=(
                            "Consider:\n"
                            "1. Implementing exploration strategies (epsilon-greedy)\n"
                            "2. Adding diversity rewards to decision-making\n"
                            "3. Reviewing if this bias is intentional and beneficial\n"
                            "4. Monitoring for overfitting to specific patterns"
                        ),
                        metrics={
                            "usage_ratio": bias["usage_ratio"],
                            "target_ratio": 0.5,
                        },
                    )
                )

        return suggestions

    def analyze_resource_usage(self, resource_data: Dict[str, Any]) -> List[OptimizationSuggestion]:
        """Generate suggestions based on resource usage.

        Args:
            resource_data: Resource usage analysis data

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        avg_cpu = resource_data.get("avg_cpu_percent", 0)
        avg_memory = resource_data.get("avg_memory_percent", 0)

        if avg_cpu > 80:
            suggestions.append(
                OptimizationSuggestion(
                    suggestion_id=self._generate_id(),
                    category="efficiency",
                    title="Reduce CPU usage",
                    description=(
                        f"Average CPU usage is {avg_cpu:.1f}%, which is above "
                        f"the recommended threshold."
                    ),
                    priority="high",
                    impact="high",
                    implementation=(
                        "Optimization strategies:\n"
                        "1. Implement task queuing to limit concurrent operations\n"
                        "2. Profile CPU-intensive operations\n"
                        "3. Consider async/await patterns for I/O operations\n"
                        "4. Review and optimize hot paths"
                    ),
                    metrics={"current_cpu": avg_cpu, "target": 60.0},
                )
            )

        if avg_memory > 80:
            suggestions.append(
                OptimizationSuggestion(
                    suggestion_id=self._generate_id(),
                    category="efficiency",
                    title="Optimize memory usage",
                    description=(
                        f"Average memory usage is {avg_memory:.1f}%, which is above "
                        f"the recommended threshold."
                    ),
                    priority="high",
                    impact="high",
                    implementation=(
                        "Memory optimization steps:\n"
                        "1. Implement data cleanup and garbage collection\n"
                        "2. Use memory profiling to identify leaks\n"
                        "3. Consider streaming for large datasets\n"
                        "4. Review cache sizes and implement LRU eviction"
                    ),
                    metrics={"current_memory": avg_memory, "target": 60.0},
                )
            )

        return suggestions

    def generate_suggestions(
        self,
        performance_data: Optional[Dict[str, Any]] = None,
        failure_data: Optional[Dict[str, Any]] = None,
        bias_data: Optional[Dict[str, Any]] = None,
        resource_data: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate comprehensive optimization suggestions.

        Args:
            performance_data: Performance metrics
            failure_data: Failure patterns
            bias_data: Bias detection results
            resource_data: Resource usage data

        Returns:
            List of optimization suggestions
        """
        all_suggestions = []

        if performance_data:
            all_suggestions.extend(self.analyze_performance_metrics(performance_data))

        if failure_data:
            all_suggestions.extend(self.analyze_failure_patterns(failure_data))

        if bias_data:
            all_suggestions.extend(self.analyze_bias_patterns(bias_data))

        if resource_data:
            all_suggestions.extend(self.analyze_resource_usage(resource_data))

        # Sort by priority and impact
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        impact_order = {"high": 0, "medium": 1, "low": 2}

        all_suggestions.sort(
            key=lambda s: (
                priority_order.get(s.priority, 3),
                impact_order.get(s.impact, 2),
            )
        )

        # Limit to max suggestions
        limited_suggestions = all_suggestions[: self.max_suggestions]

        return [s.to_dict() for s in limited_suggestions]

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

"""Pattern recognition module for metacognition.

Identifies behavioral patterns and anomalies in agent decision-making.
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PatternRecognition:
    """Identifies patterns and anomalies in agent behavior."""

    def __init__(self, sensitivity: float = 0.7) -> None:
        """Initialize pattern recognition.

        Args:
            sensitivity: Detection sensitivity (0.0 - 1.0)
        """
        self.sensitivity = sensitivity
        self._patterns: Dict[str, List[Any]] = {}

    def detect_repetitive_behavior(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect repetitive behavior patterns.

        Args:
            operations: List of operations to analyze

        Returns:
            Detected repetitive patterns
        """
        if not operations:
            return {"patterns": [], "message": "No operations to analyze"}

        # Extract sequences of tool usage
        tool_sequences = [op.get("tool_name") for op in operations if op.get("tool_name")]

        if len(tool_sequences) < 3:
            return {"patterns": [], "message": "Insufficient data"}

        # Find repeating sequences
        patterns = []
        for length in range(2, min(6, len(tool_sequences) // 2)):
            for i in range(len(tool_sequences) - length):
                sequence = tuple(tool_sequences[i : i + length])
                # Check if sequence repeats
                count = 0
                for j in range(i + length, len(tool_sequences) - length + 1):
                    if tuple(tool_sequences[j : j + length]) == sequence:
                        count += 1

                # If sequence repeats frequently, it's a pattern
                if count >= 2:
                    patterns.append(
                        {
                            "sequence": list(sequence),
                            "repetitions": count + 1,
                            "length": length,
                        }
                    )

        # Sort by repetitions
        patterns.sort(key=lambda p: p["repetitions"], reverse=True)  # type: ignore

        return {
            "patterns": patterns[:5],
            "total_patterns": len(patterns),
            "timestamp": datetime.now().isoformat(),
        }

    def detect_bias(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect bias in tool or agent selection.

        Args:
            operations: List of operations to analyze

        Returns:
            Detected biases
        """
        if not operations:
            return {"biases": [], "message": "No operations to analyze"}

        # Count usage patterns
        tool_counts = self._count_tool_usage(operations)
        agent_counts = self._count_agent_usage(operations)
        total_ops = len(operations)

        # Detect biases
        biases = []
        biases.extend(self._detect_tool_biases(tool_counts, total_ops))
        biases.extend(self._detect_agent_biases(agent_counts, total_ops))

        return {
            "biases": biases,
            "total_biases": len(biases),
            "timestamp": datetime.now().isoformat(),
        }

    def _count_tool_usage(self, operations: List[Dict[str, Any]]) -> Counter[str]:
        """Count tool usage from operations."""
        return Counter(op.get("tool_name") for op in operations if op.get("tool_name"))

    def _count_agent_usage(self, operations: List[Dict[str, Any]]) -> Counter[str]:
        """Count agent usage from operations."""
        return Counter(op.get("agent") for op in operations if op.get("agent"))

    def _detect_tool_biases(
        self, tool_counts: Counter[str], total_ops: int
    ) -> List[Dict[str, Any]]:
        """Detect tool usage biases."""
        biases = []
        for tool, count in tool_counts.items():
            usage_ratio = count / total_ops
            if usage_ratio > self.sensitivity:
                biases.append(self._create_bias_entry("tool", tool, usage_ratio))
        return biases

    def _detect_agent_biases(
        self, agent_counts: Counter[str], total_ops: int
    ) -> List[Dict[str, Any]]:
        """Detect agent usage biases."""
        biases = []
        for agent, count in agent_counts.items():
            usage_ratio = count / total_ops
            if usage_ratio > self.sensitivity:
                biases.append(self._create_bias_entry("agent", agent, usage_ratio))
        return biases

    def _create_bias_entry(self, bias_type: str, name: str, usage_ratio: float) -> Dict[str, Any]:
        """Create a bias entry dictionary."""
        return {
            "type": bias_type,
            "name": name,
            "usage_ratio": usage_ratio,
            "severity": "high" if usage_ratio > 0.8 else "medium",
        }

    def detect_anomalies(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect anomalous behavior patterns.

        Args:
            operations: List of operations to analyze

        Returns:
            Detected anomalies
        """
        if not operations:
            return {"anomalies": [], "message": "No operations to analyze"}

        anomalies = []

        # Check for different types of anomalies
        anomalies.extend(self._detect_execution_time_anomalies(operations))
        anomalies.extend(self._detect_failure_rate_anomalies(operations))

        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "timestamp": datetime.now().isoformat(),
        }

    def _detect_execution_time_anomalies(
        self, operations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect operations with unusual execution times."""
        anomalies = []
        execution_times = [op.get("duration", 0) for op in operations if op.get("duration")]

        if not execution_times:
            return anomalies

        # Calculate statistics
        avg_time, std_dev = self._calculate_execution_statistics(execution_times)
        threshold = avg_time + (2 * std_dev)

        # Find slow operations
        for i, op in enumerate(operations):
            duration = op.get("duration", 0)
            if duration > threshold:
                anomalies.append(self._create_slow_execution_anomaly(op, duration, avg_time))

        return anomalies

    def _calculate_execution_statistics(self, execution_times: List[float]) -> tuple[float, float]:
        """Calculate average and standard deviation of execution times."""
        avg_time = sum(execution_times) / len(execution_times)
        variance = sum((t - avg_time) ** 2 for t in execution_times) / len(execution_times)
        std_dev = variance**0.5
        return avg_time, std_dev

    def _create_slow_execution_anomaly(
        self, operation: Dict[str, Any], duration: float, avg_time: float
    ) -> Dict[str, Any]:
        """Create anomaly entry for slow execution."""
        return {
            "type": "slow_execution",
            "operation": operation.get("tool_name", "unknown"),
            "duration": duration,
            "expected": avg_time,
            "deviation": (duration - avg_time) / avg_time if avg_time > 0 else 0,
        }

    def _detect_failure_rate_anomalies(
        self, operations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect operations with high failure rates."""
        anomalies = []
        recent_operations = operations[-10:] if len(operations) >= 10 else operations
        recent_failures = [op for op in recent_operations if not op.get("success", True)]

        if len(recent_failures) >= 5:
            anomalies.append(self._create_failure_rate_anomaly(recent_failures, recent_operations))

        return anomalies

    def _create_failure_rate_anomaly(
        self, failures: List[Dict[str, Any]], total_recent: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create anomaly entry for high failure rate."""
        return {
            "type": "high_failure_rate",
            "failures": len(failures),
            "total": len(total_recent),
            "rate": len(failures) / len(total_recent),
        }

    def analyze_decision_tree(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze decision-making tree structure.

        Args:
            operations: List of operations to analyze

        Returns:
            Decision tree analysis
        """
        if not operations:
            return {"message": "No operations to analyze"}

        # Build decision sequences
        sequences = self._build_decision_sequences(operations)

        # Analyze sequence characteristics
        if not sequences:
            return {"message": "No decision sequences found"}

        # Calculate sequence statistics
        sequence_stats = self._calculate_sequence_statistics(sequences)

        # Find common decision paths
        common_paths = self._find_common_decision_paths(sequences)

        return {
            "total_sequences": len(sequences),
            **sequence_stats,
            "common_decision_paths": common_paths,
            "timestamp": datetime.now().isoformat(),
        }

    def _build_decision_sequences(self, operations: List[Dict[str, Any]]) -> List[List[str]]:
        """Build decision sequences from operations."""
        sequences = []
        current_sequence = []

        for op in operations:
            tool = op.get("tool_name")
            if tool:
                current_sequence.append(tool)

            # Split sequences on task boundaries
            if self._is_task_boundary(op):
                if current_sequence:
                    sequences.append(current_sequence)
                current_sequence = []

        if current_sequence:
            sequences.append(current_sequence)

        return sequences

    def _is_task_boundary(self, operation: Dict[str, Any]) -> bool:
        """Check if operation marks a task boundary."""
        return operation.get("metadata", {}).get("task_complete", False)

    def _calculate_sequence_statistics(self, sequences: List[List[str]]) -> Dict[str, float]:
        """Calculate statistical properties of decision sequences."""
        lengths = [len(seq) for seq in sequences]
        return {
            "avg_sequence_length": sum(lengths) / len(lengths),
            "max_sequence_length": max(lengths),
            "min_sequence_length": min(lengths),
        }

    def _find_common_decision_paths(self, sequences: List[List[str]]) -> List[Dict[str, Any]]:
        """Find most common decision paths."""
        sequence_counts = Counter(tuple(seq) for seq in sequences)
        return [
            {"path": list(path), "count": count} for path, count in sequence_counts.most_common(5)
        ]

    def calculate_diversity_score(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate diversity score for decision-making.

        Args:
            operations: List of operations to analyze

        Returns:
            Diversity score and analysis
        """
        if not operations:
            return {"diversity_score": 0.0, "message": "No operations to analyze"}

        # Count unique elements
        unique_tools, unique_agents = self._count_unique_elements(operations)

        # Calculate diversity metrics
        tool_counts = self._count_tool_usage(operations)
        entropy = self._calculate_tool_entropy(tool_counts)
        diversity_score = self._normalize_diversity_score(entropy, unique_tools)

        return {
            "diversity_score": diversity_score,
            "unique_tools": len(unique_tools),
            "unique_agents": len(unique_agents),
            "total_operations": len(operations),
            "interpretation": self._interpret_diversity_score(diversity_score),
            "timestamp": datetime.now().isoformat(),
        }

    def _count_unique_elements(self, operations: List[Dict[str, Any]]) -> tuple[set[str], set[str]]:
        """Count unique tools and agents from operations."""
        unique_tools = set(op.get("tool_name") for op in operations if op.get("tool_name"))
        unique_agents = set(op.get("agent") for op in operations if op.get("agent"))
        return unique_tools, unique_agents

    def _calculate_tool_entropy(self, tool_counts: Counter[str]) -> float:
        """Calculate simplified entropy for tool distribution."""
        total = sum(tool_counts.values())
        if total == 0:
            return 0.0

        entropy = 0.0
        for count in tool_counts.values():
            if count > 0:
                prob = count / total
                entropy -= prob * (prob**0.5)  # Simplified entropy

        return entropy

    def _normalize_diversity_score(self, entropy: float, unique_tools: set[str]) -> float:
        """Normalize entropy to diversity score (0-1 scale)."""
        max_entropy = len(unique_tools) ** 0.5 if unique_tools else 1.0
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def _interpret_diversity_score(self, diversity_score: float) -> str:
        """Interpret diversity score as qualitative level."""
        if diversity_score > 0.7:
            return "high"
        elif diversity_score > 0.4:
            return "medium"
        else:
            return "low"

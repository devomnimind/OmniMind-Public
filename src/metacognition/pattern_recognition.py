"""Pattern recognition module for metacognition.

Identifies behavioral patterns and anomalies in agent decision-making.
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

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

    def detect_repetitive_behavior(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
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
        patterns.sort(key=lambda p: p["repetitions"], reverse=True)

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

        # Count tool usage
        tool_counts = Counter(
            op.get("tool_name") for op in operations if op.get("tool_name")
        )

        # Count agent usage
        agent_counts = Counter(
            op.get("agent") for op in operations if op.get("agent")
        )

        total_ops = len(operations)
        biases = []

        # Detect tool bias
        for tool, count in tool_counts.items():
            usage_ratio = count / total_ops
            if usage_ratio > self.sensitivity:
                biases.append(
                    {
                        "type": "tool",
                        "name": tool,
                        "usage_ratio": usage_ratio,
                        "severity": "high" if usage_ratio > 0.8 else "medium",
                    }
                )

        # Detect agent bias
        for agent, count in agent_counts.items():
            usage_ratio = count / total_ops
            if usage_ratio > self.sensitivity:
                biases.append(
                    {
                        "type": "agent",
                        "name": agent,
                        "usage_ratio": usage_ratio,
                        "severity": "high" if usage_ratio > 0.8 else "medium",
                    }
                )

        return {
            "biases": biases,
            "total_biases": len(biases),
            "timestamp": datetime.now().isoformat(),
        }

    def detect_anomalies(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect anomalous behavior patterns.

        Args:
            operations: List of operations to analyze

        Returns:
            Detected anomalies
        """
        if not operations:
            return {"anomalies": [], "message": "No operations to analyze"}

        anomalies = []

        # Check for unusual execution times
        execution_times = [
            op.get("duration", 0) for op in operations if op.get("duration")
        ]

        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            std_dev = (
                sum((t - avg_time) ** 2 for t in execution_times) / len(execution_times)
            ) ** 0.5

            # Flag operations that are significantly slower
            threshold = avg_time + (2 * std_dev)
            for i, op in enumerate(operations):
                duration = op.get("duration", 0)
                if duration > threshold:
                    anomalies.append(
                        {
                            "type": "slow_execution",
                            "operation": op.get("tool_name", "unknown"),
                            "duration": duration,
                            "expected": avg_time,
                            "deviation": (duration - avg_time) / avg_time,
                        }
                    )

        # Check for unusual failure rates
        recent_failures = [op for op in operations[-10:] if not op.get("success", True)]

        if len(recent_failures) >= 5:
            anomalies.append(
                {
                    "type": "high_failure_rate",
                    "failures": len(recent_failures),
                    "total": len(operations[-10:]),
                    "rate": len(recent_failures) / len(operations[-10:]),
                }
            )

        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_decision_tree(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze decision-making tree structure.

        Args:
            operations: List of operations to analyze

        Returns:
            Decision tree analysis
        """
        if not operations:
            return {"message": "No operations to analyze"}

        # Build decision sequences
        sequences = []
        current_sequence = []

        for op in operations:
            tool = op.get("tool_name")
            if tool:
                current_sequence.append(tool)

            # Split sequences on task boundaries
            if op.get("metadata", {}).get("task_complete"):
                if current_sequence:
                    sequences.append(current_sequence)
                current_sequence = []

        if current_sequence:
            sequences.append(current_sequence)

        # Analyze sequence characteristics
        if not sequences:
            return {"message": "No decision sequences found"}

        avg_length = sum(len(seq) for seq in sequences) / len(sequences)
        max_length = max(len(seq) for seq in sequences)
        min_length = min(len(seq) for seq in sequences)

        # Find common decision paths
        sequence_counts = Counter(tuple(seq) for seq in sequences)
        common_paths = [
            {"path": list(path), "count": count}
            for path, count in sequence_counts.most_common(5)
        ]

        return {
            "total_sequences": len(sequences),
            "avg_sequence_length": avg_length,
            "max_sequence_length": max_length,
            "min_sequence_length": min_length,
            "common_decision_paths": common_paths,
            "timestamp": datetime.now().isoformat(),
        }

    def calculate_diversity_score(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate diversity score for decision-making.

        Args:
            operations: List of operations to analyze

        Returns:
            Diversity score and analysis
        """
        if not operations:
            return {"diversity_score": 0.0, "message": "No operations to analyze"}

        # Count unique tools and agents
        unique_tools = set(op.get("tool_name") for op in operations if op.get("tool_name"))
        unique_agents = set(op.get("agent") for op in operations if op.get("agent"))

        # Calculate Shannon entropy for tool distribution
        tool_counts = Counter(
            op.get("tool_name") for op in operations if op.get("tool_name")
        )

        total = sum(tool_counts.values())
        entropy = 0.0
        for count in tool_counts.values():
            if count > 0:
                prob = count / total
                entropy -= prob * (prob ** 0.5)  # Simplified entropy

        # Normalize to 0-1 scale
        max_entropy = len(unique_tools) ** 0.5 if unique_tools else 1.0
        diversity_score = entropy / max_entropy if max_entropy > 0 else 0.0

        return {
            "diversity_score": diversity_score,
            "unique_tools": len(unique_tools),
            "unique_agents": len(unique_agents),
            "total_operations": len(operations),
            "interpretation": (
                "high" if diversity_score > 0.7 else "medium" if diversity_score > 0.4 else "low"
            ),
            "timestamp": datetime.now().isoformat(),
        }

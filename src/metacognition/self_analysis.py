"""Self-analysis module for metacognition.

Analyzes OmniMind's own decision-making patterns and execution history.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, cast

logger = logging.getLogger(__name__)


class SelfAnalysis:
    """Analyzes agent's own decision-making and execution patterns."""

    def __init__(self, hash_chain_path: str = "logs/hash_chain.json") -> None:
        """Initialize self-analysis.

        Args:
            hash_chain_path: Path to the immutable audit log
        """
        self.hash_chain_path = Path(hash_chain_path)
        self._cache: Dict[str, Any] = {}

    def _load_hash_chain(self) -> List[Dict[str, Any]]:
        """Load the hash chain audit log.

        Returns:
            List of audit entries
        """
        if not self.hash_chain_path.exists():
            logger.warning(f"Hash chain not found: {self.hash_chain_path}")
            return []

        try:
            with self.hash_chain_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                # Handle both dict format (with "entries" key) and list format
                if isinstance(data, dict):
                    entries = data.get("entries", [])
                elif isinstance(data, list):
                    entries = data
                else:
                    logger.warning(f"Unexpected hash chain format: {type(data)}")
                    return []
                return cast(List[Dict[str, Any]], entries)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse hash chain JSON: {exc}")
            return []
        except Exception as exc:
            logger.error(f"Failed to load hash chain: {exc}")
            return []

    def analyze_decision_patterns(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """Analyze decision-making patterns over recent history.

        Args:
            lookback_hours: Hours of history to analyze

        Returns:
            Analysis results with patterns identified
        """
        entries = self._load_hash_chain()
        if not entries:
            return {"error": "No audit log data available"}

        # Filter recent entries
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        recent_entries = [
            e for e in entries if datetime.fromisoformat(e.get("timestamp", "")) > cutoff_time
        ]

        if not recent_entries:
            return {"error": "No recent entries found"}

        # Analyze patterns
        tool_usage: Dict[str, int] = {}
        agent_usage: Dict[str, int] = {}
        success_counts = {"success": 0, "failure": 0}

        for entry in recent_entries:
            # Count tool usage
            tool = entry.get("tool_name")
            if tool:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1

            # Count agent invocations
            agent = entry.get("agent")
            if agent:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

            # Track success/failure
            if entry.get("success"):
                success_counts["success"] += 1
            else:
                success_counts["failure"] += 1

        total = success_counts["success"] + success_counts["failure"]
        success_rate = success_counts["success"] / total if total > 0 else 0

        return {
            "lookback_hours": lookback_hours,
            "total_operations": len(recent_entries),
            "success_rate": success_rate,
            "most_used_tools": sorted(tool_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            "agent_activity": agent_usage,
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_execution_times(self) -> Dict[str, Any]:
        """Analyze execution time patterns.

        Returns:
            Execution time statistics
        """
        entries = self._load_hash_chain()
        if not entries:
            return {"error": "No audit log data available"}

        execution_times: Dict[str, List[float]] = {}

        for entry in entries:
            tool = entry.get("tool_name")
            duration = entry.get("duration")

            if tool and duration:
                if tool not in execution_times:
                    execution_times[tool] = []
                execution_times[tool].append(duration)

        # Calculate statistics
        stats = {}
        for tool, times in execution_times.items():
            if times:
                stats[tool] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                }

        return {
            "tool_performance": stats,
            "timestamp": datetime.now().isoformat(),
        }

    def identify_failure_patterns(self) -> Dict[str, Any]:
        """Identify patterns in failures and errors.

        Returns:
            Failure pattern analysis
        """
        entries = self._load_hash_chain()
        if not entries:
            return {"error": "No audit log data available"}

        failures = [e for e in entries if not e.get("success", True)]

        if not failures:
            return {"message": "No failures detected", "total_failures": 0}

        # Group failures by type
        failure_by_tool: Dict[str, int] = {}
        failure_by_error: Dict[str, int] = {}

        for failure in failures:
            tool = failure.get("tool_name", "unknown")
            error_msg = failure.get("error", "unknown error")

            failure_by_tool[tool] = failure_by_tool.get(tool, 0) + 1
            failure_by_error[error_msg] = failure_by_error.get(error_msg, 0) + 1

        return {
            "total_failures": len(failures),
            "failure_by_tool": sorted(failure_by_tool.items(), key=lambda x: x[1], reverse=True),
            "common_errors": sorted(failure_by_error.items(), key=lambda x: x[1], reverse=True)[:5],
            "timestamp": datetime.now().isoformat(),
        }

    def analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze resource usage patterns.

        Returns:
            Resource usage analysis
        """
        entries = self._load_hash_chain()
        if not entries:
            return {"error": "No audit log data available"}

        # Extract resource usage data if available
        resource_data = []
        for entry in entries:
            metadata = entry.get("metadata", {})
            if "cpu_percent" in metadata or "memory_percent" in metadata:
                resource_data.append(
                    {
                        "timestamp": entry.get("timestamp"),
                        "cpu": metadata.get("cpu_percent", 0),
                        "memory": metadata.get("memory_percent", 0),
                    }
                )

        if not resource_data:
            return {
                "message": "No resource usage data available",
                "suggestion": "Enable resource tracking in audit logs",
            }

        # Calculate averages
        avg_cpu = sum(d["cpu"] for d in resource_data) / len(resource_data)
        avg_memory = sum(d["memory"] for d in resource_data) / len(resource_data)

        return {
            "avg_cpu_percent": avg_cpu,
            "avg_memory_percent": avg_memory,
            "samples": len(resource_data),
            "timestamp": datetime.now().isoformat(),
        }

    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary of the system.

        Returns:
            Health summary with key metrics
        """
        decision_patterns = self.analyze_decision_patterns(lookback_hours=24)
        failure_patterns = self.identify_failure_patterns()

        # Determine health status
        success_rate = decision_patterns.get("success_rate", 0)
        if success_rate >= 0.9:
            health = "excellent"
        elif success_rate >= 0.7:
            health = "good"
        elif success_rate >= 0.5:
            health = "fair"
        else:
            health = "poor"

        return {
            "health_status": health,
            "success_rate": success_rate,
            "total_operations_24h": decision_patterns.get("total_operations", 0),
            "total_failures": failure_patterns.get("total_failures", 0),
            "timestamp": datetime.now().isoformat(),
        }

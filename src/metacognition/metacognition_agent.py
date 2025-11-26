"""Metacognition Agent for OmniMind.

Provides self-reflective AI capabilities including:
- Periodic self-analysis
- Pattern recognition in decision-making
- Performance optimization suggestions
- Bias detection and mitigation
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.metacognition.optimization_suggestions import OptimizationSuggestions
from src.metacognition.pattern_recognition import PatternRecognition
from src.metacognition.self_analysis import SelfAnalysis

logger = logging.getLogger(__name__)


class MetacognitionAgent:
    """Agent responsible for self-reflection and optimization."""

    def __init__(
        self,
        hash_chain_path: str = "logs/hash_chain.json",
        analysis_interval: int = 3600,
        bias_sensitivity: float = 0.7,
        max_suggestions: int = 10,
    ) -> None:
        """Initialize metacognition agent.

        Args:
            hash_chain_path: Path to immutable audit log
            analysis_interval: Seconds between analysis runs
            bias_sensitivity: Sensitivity for bias detection (0.0-1.0)
            max_suggestions: Maximum optimization suggestions
        """
        self.hash_chain_path = hash_chain_path
        self.analysis_interval = analysis_interval
        self.bias_sensitivity = bias_sensitivity
        self.max_suggestions = max_suggestions

        # Initialize sub-modules
        self.self_analysis = SelfAnalysis(hash_chain_path)
        self.pattern_recognition = PatternRecognition(bias_sensitivity)
        self.optimization_engine = OptimizationSuggestions(max_suggestions)

        # State
        self.last_analysis: Optional[datetime] = None
        self.analysis_history: List[Dict[str, Any]] = []

        logger.info("MetacognitionAgent initialized")

    def run_analysis(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """Run comprehensive self-analysis.

        Args:
            lookback_hours: Hours of history to analyze

        Returns:
            Complete analysis report
        """
        logger.info(f"Running metacognition analysis (lookback: {lookback_hours}h)")

        try:
            # 1. Self-analysis
            decision_patterns = self.self_analysis.analyze_decision_patterns(
                lookback_hours
            )
            execution_times = self.self_analysis.analyze_execution_times()
            failure_patterns = self.self_analysis.identify_failure_patterns()
            resource_usage = self.self_analysis.analyze_resource_usage()
            health_summary = self.self_analysis.get_health_summary()

            # 2. Get operations for pattern recognition
            entries = self.self_analysis._load_hash_chain()
            if entries:
                # Filter recent entries
                from datetime import timedelta

                cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
                recent_ops = [
                    e
                    for e in entries
                    if datetime.fromisoformat(e.get("timestamp", "")) > cutoff_time
                ]

                # Pattern recognition
                repetitive_behavior = (
                    self.pattern_recognition.detect_repetitive_behavior(recent_ops)
                )
                bias_detection = self.pattern_recognition.detect_bias(recent_ops)
                anomalies = self.pattern_recognition.detect_anomalies(recent_ops)
                decision_tree = self.pattern_recognition.analyze_decision_tree(
                    recent_ops
                )
                diversity_score = self.pattern_recognition.calculate_diversity_score(
                    recent_ops
                )
            else:
                repetitive_behavior = {"patterns": [], "message": "No data"}
                bias_detection = {"biases": [], "message": "No data"}
                anomalies = {"anomalies": [], "message": "No data"}
                decision_tree = {"message": "No data"}
                diversity_score = {"diversity_score": 0.0, "message": "No data"}

            # 3. Generate optimization suggestions
            suggestions = self.optimization_engine.generate_suggestions(
                performance_data=execution_times,
                failure_data=failure_patterns,
                bias_data=bias_detection,
                resource_data=resource_usage,
            )

            # Compile report
            report = {
                "timestamp": datetime.now().isoformat(),
                "lookback_hours": lookback_hours,
                "health_summary": health_summary,
                "self_analysis": {
                    "decision_patterns": decision_patterns,
                    "execution_times": execution_times,
                    "failure_patterns": failure_patterns,
                    "resource_usage": resource_usage,
                },
                "pattern_recognition": {
                    "repetitive_behavior": repetitive_behavior,
                    "bias_detection": bias_detection,
                    "anomalies": anomalies,
                    "decision_tree": decision_tree,
                    "diversity_score": diversity_score,
                },
                "optimization_suggestions": suggestions,
                "summary": {
                    "total_suggestions": len(suggestions),
                    "critical_issues": len(
                        [s for s in suggestions if s["priority"] == "critical"]
                    ),
                    "high_priority": len(
                        [s for s in suggestions if s["priority"] == "high"]
                    ),
                },
            }

            # Store in history
            self.last_analysis = datetime.now()
            self.analysis_history.append(
                {
                    "timestamp": report["timestamp"],
                    "health_status": health_summary.get("health_status"),
                    "suggestions_count": len(suggestions),
                }
            )

            # Keep only last 100 analyses in history
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]

            logger.info(
                f"Analysis complete: {len(suggestions)} suggestions, "
                f"health={health_summary.get('health_status')}"
            )

            return report

        except Exception as exc:
            logger.exception(f"Metacognition analysis failed: {exc}")
            return {
                "error": str(exc),
                "timestamp": datetime.now().isoformat(),
            }

    def get_quick_health_check(self) -> Dict[str, Any]:
        """Get quick health check without full analysis.

        Returns:
            Quick health summary
        """
        try:
            health = self.self_analysis.get_health_summary()
            return {
                "status": "ok",
                "health": health,
                "last_analysis": (
                    self.last_analysis.isoformat() if self.last_analysis else None
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            logger.exception(f"Health check failed: {exc}")
            return {
                "status": "error",
                "error": str(exc),
                "timestamp": datetime.now().isoformat(),
            }

    def _extract_suggestions(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize the optimization suggestions list for type safety."""
        raw_suggestions = report.get("optimization_suggestions")
        if not isinstance(raw_suggestions, list):
            return []

        normalized: List[Dict[str, Any]] = []
        for entry in raw_suggestions:
            if isinstance(entry, dict):
                normalized.append(entry)
        return normalized

    def get_top_suggestions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top optimization suggestions from last analysis.

        Args:
            limit: Maximum suggestions to return

        Returns:
            Top optimization suggestions
        """
        if not self.analysis_history:
            # Run analysis if never run
            report = self.run_analysis()
            return self._extract_suggestions(report)[:limit]

        # Return from last analysis
        # Note: Would need to persist suggestions to return from history
        # For now, run a new analysis
        report = self.run_analysis()
        return self._extract_suggestions(report)[:limit]

    def should_run_analysis(self) -> bool:
        """Check if it's time to run periodic analysis.

        Returns:
            True if analysis should run
        """
        if self.last_analysis is None:
            return True

        from datetime import timedelta

        elapsed = datetime.now() - self.last_analysis
        return elapsed > timedelta(seconds=self.analysis_interval)

    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get statistics about metacognition analyses.

        Returns:
            Analysis statistics
        """
        return {
            "total_analyses": len(self.analysis_history),
            "last_analysis": (
                self.last_analysis.isoformat() if self.last_analysis else None
            ),
            "analysis_interval": self.analysis_interval,
            "recent_health_trend": [
                {"timestamp": h["timestamp"], "health": h["health_status"]}
                for h in self.analysis_history[-10:]
            ],
            "timestamp": datetime.now().isoformat(),
        }

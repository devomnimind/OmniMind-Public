"""Advanced Self-Reflection (Phase 11.4).

Enhanced meta-cognitive self-analysis capabilities:
- Introspective analysis of own processes
- Meta-cognitive self-evaluation
- Advanced consciousness tracking
- Self-improvement insights
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List

import structlog

from src.metacognition.self_analysis import SelfAnalysis

logger = structlog.get_logger(__name__)


@dataclass
class IntrospectionLog:
    """Log entry for introspective analysis.

    Attributes:
        timestamp: When the introspection occurred
        focus_area: What was being reflected upon
        observations: Key observations made
        insights: Insights gained
        confidence: Confidence in the insights (0.0-1.0)
        action_items: Suggested actions from reflection
    """

    timestamp: datetime
    focus_area: str
    observations: List[str]
    insights: List[str]
    confidence: float
    action_items: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate introspection log."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class SelfReflectionMetrics:
    """Metrics for self-reflection quality.

    Attributes:
        depth_score: How deep the reflection goes (0.0-1.0)
        breadth_score: How comprehensive the reflection is (0.0-1.0)
        actionability_score: How actionable the insights are (0.0-1.0)
        consistency_score: Consistency with past reflections (0.0-1.0)
        timestamp: When metrics were calculated
    """

    depth_score: float
    breadth_score: float
    actionability_score: float
    consistency_score: float
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate metrics."""
        for score_name in [
            "depth_score",
            "breadth_score",
            "actionability_score",
            "consistency_score",
        ]:
            score = getattr(self, score_name)
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"{score_name} must be between 0.0 and 1.0")

    @property
    def overall_quality(self) -> float:
        """Calculate overall reflection quality.

        Returns:
            Weighted average of all metrics
        """
        return (
            self.depth_score * 0.3
            + self.breadth_score * 0.2
            + self.actionability_score * 0.3
            + self.consistency_score * 0.2
        )


class AdvancedSelfReflection:
    """Advanced self-reflection engine for AI consciousness.

    Implements:
    1. Introspective analysis of own decision processes
    2. Meta-cognitive self-evaluation
    3. Advanced consciousness state tracking
    4. Self-improvement insight generation
    """

    def __init__(
        self,
        hash_chain_path: str = "logs/hash_chain.json",
        reflection_depth: str = "deep",
        min_confidence: float = 0.6,
    ) -> None:
        """Initialize Advanced Self-Reflection engine.

        Args:
            hash_chain_path: Path to audit log for analysis
            reflection_depth: Depth of reflection (shallow, medium, deep)
            min_confidence: Minimum confidence for insights
        """
        self.hash_chain_path = hash_chain_path
        self.reflection_depth = reflection_depth
        self.min_confidence = min_confidence

        # Use existing self-analysis as foundation
        self.self_analysis = SelfAnalysis(hash_chain_path)

        # Internal state
        self._introspection_logs: List[IntrospectionLog] = []
        self._reflection_history: List[SelfReflectionMetrics] = []

        logger.info(
            "advanced_self_reflection_initialized",
            depth=reflection_depth,
            min_confidence=min_confidence,
        )

    def introspect(
        self,
        focus_area: str,
        lookback_hours: int = 24,
    ) -> IntrospectionLog:
        """Perform introspective analysis on a specific area.

        Args:
            focus_area: Area to focus introspection on
            lookback_hours: Hours of history to analyze

        Returns:
            Introspection log with observations and insights
        """
        logger.info("introspection_started", focus_area=focus_area)

        observations: List[str] = []
        insights: List[str] = []
        action_items: List[str] = []

        # Analyze based on focus area
        if focus_area == "decision_making":
            # Analyze decision patterns
            patterns = self.self_analysis.analyze_decision_patterns(lookback_hours)

            if "error" not in patterns:
                success_rate = patterns.get("success_rate", 0)
                observations.append(
                    f"Success rate over {lookback_hours}h: {success_rate:.2%}"
                )

                if success_rate >= 0.9:
                    insights.append(
                        "Decision-making is highly effective; maintain current approach"
                    )
                elif success_rate >= 0.7:
                    insights.append(
                        "Decision-making is good but has room for improvement"
                    )
                    action_items.append("Analyze failure patterns for optimization")
                else:
                    insights.append(
                        "Decision-making effectiveness needs significant improvement"
                    )
                    action_items.append("Conduct root cause analysis on failures")
                    action_items.append("Review decision criteria and thresholds")

                # Analyze tool usage
                most_used = patterns.get("most_used_tools", [])
                if most_used:
                    observations.append(
                        f"Most used tools: {', '.join(t[0] for t in most_used[:3])}"
                    )
                    insights.append(
                        "Tool usage shows clear preferences; consider diversification"
                    )

        elif focus_area == "performance":
            # Analyze execution performance
            perf = self.self_analysis.analyze_execution_times()

            if "error" not in perf:
                tool_perf = perf.get("tool_performance", {})
                if tool_perf:
                    # Find slowest tools
                    slow_tools = sorted(
                        tool_perf.items(),
                        key=lambda x: x[1].get("avg", 0),
                        reverse=True,
                    )[:3]

                    observations.append(
                        f"Slowest operations: {', '.join(t[0] for t in slow_tools)}"
                    )
                    insights.append(
                        "Performance bottlenecks identified in specific tools"
                    )
                    action_items.append(
                        "Optimize slow tools or find faster alternatives"
                    )

        elif focus_area == "learning":
            # Analyze learning and adaptation
            failure_patterns = self.self_analysis.identify_failure_patterns()

            if "error" not in failure_patterns:
                total_failures = failure_patterns.get("total_failures", 0)
                observations.append(f"Total failures in period: {total_failures}")

                if total_failures > 0:
                    common_errors = failure_patterns.get("common_errors", [])
                    if common_errors:
                        observations.append(
                            f"Most common error: {common_errors[0][0][:50]}"
                        )
                        insights.append(
                            "Recurring errors indicate learning opportunity"
                        )
                        action_items.append("Develop mitigation for common errors")
                else:
                    insights.append("No failures detected; system functioning well")

        elif focus_area == "resource_usage":
            # Analyze resource utilization
            resources = self.self_analysis.analyze_resource_usage()

            if "error" not in resources:
                avg_cpu = resources.get("avg_cpu_percent", 0)
                avg_mem = resources.get("avg_memory_percent", 0)

                observations.append(f"Average CPU usage: {avg_cpu:.1f}%")
                observations.append(f"Average memory usage: {avg_mem:.1f}%")

                if avg_cpu > 80 or avg_mem > 80:
                    insights.append("Resource usage is high; optimization needed")
                    action_items.append("Investigate resource-intensive operations")
                else:
                    insights.append("Resource usage is within acceptable limits")

        # Calculate confidence based on data availability
        confidence = 0.5
        if observations:
            confidence += min(0.3, len(observations) * 0.1)
        if insights:
            confidence += min(0.2, len(insights) * 0.1)

        # Create introspection log
        log = IntrospectionLog(
            timestamp=datetime.now(),
            focus_area=focus_area,
            observations=observations,
            insights=insights,
            confidence=confidence,
            action_items=action_items,
        )

        # Store in history
        self._introspection_logs.append(log)

        # Keep only recent logs
        if len(self._introspection_logs) > 100:
            self._introspection_logs = self._introspection_logs[-100:]

        logger.info(
            "introspection_completed",
            focus_area=focus_area,
            observations=len(observations),
            insights=len(insights),
        )

        return log

    def evaluate_self_reflection_quality(self) -> SelfReflectionMetrics:
        """Evaluate the quality of self-reflection processes.

        Returns:
            Metrics on reflection quality
        """
        if not self._introspection_logs:
            # No history to evaluate
            return SelfReflectionMetrics(
                depth_score=0.0,
                breadth_score=0.0,
                actionability_score=0.0,
                consistency_score=0.0,
            )

        recent_logs = self._introspection_logs[-10:]

        # Calculate depth score (average insights per introspection)
        total_insights = sum(len(log.insights) for log in recent_logs)
        depth_score = min(1.0, total_insights / (len(recent_logs) * 3))

        # Calculate breadth score (diversity of focus areas)
        focus_areas = set(log.focus_area for log in recent_logs)
        breadth_score = min(1.0, len(focus_areas) / 5.0)

        # Calculate actionability score (proportion with action items)
        with_actions = sum(1 for log in recent_logs if log.action_items)
        actionability_score = with_actions / len(recent_logs)

        # Calculate consistency score (average confidence)
        avg_confidence = sum(log.confidence for log in recent_logs) / len(recent_logs)
        consistency_score = avg_confidence

        metrics = SelfReflectionMetrics(
            depth_score=depth_score,
            breadth_score=breadth_score,
            actionability_score=actionability_score,
            consistency_score=consistency_score,
        )

        # Store in history
        self._reflection_history.append(metrics)

        if len(self._reflection_history) > 100:
            self._reflection_history = self._reflection_history[-100:]

        logger.debug(
            "reflection_quality_evaluated",
            overall_quality=metrics.overall_quality,
        )

        return metrics

    def generate_self_improvement_plan(
        self,
        lookback_hours: int = 168,  # 1 week
    ) -> Dict[str, Any]:
        """Generate a self-improvement plan based on introspection.

        Args:
            lookback_hours: Hours of history to analyze

        Returns:
            Self-improvement plan
        """
        logger.info("generating_self_improvement_plan")

        # Introspect on multiple areas
        areas = ["decision_making", "performance", "learning", "resource_usage"]
        introspections = []

        for area in areas:
            log = self.introspect(area, lookback_hours)
            introspections.append(log)

        # Collect all action items
        all_actions: List[Dict[str, Any]] = []
        for log in introspections:
            for action in log.action_items:
                all_actions.append(
                    {
                        "action": action,
                        "area": log.focus_area,
                        "priority": "high" if len(log.insights) > 2 else "medium",
                    }
                )

        # Evaluate current reflection quality
        quality_metrics = self.evaluate_self_reflection_quality()

        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []

        if quality_metrics.depth_score >= 0.7:
            strengths.append("Deep analytical thinking")
        else:
            weaknesses.append("Shallow analysis - need deeper insights")

        if quality_metrics.breadth_score >= 0.7:
            strengths.append("Comprehensive coverage of areas")
        else:
            weaknesses.append("Limited scope - expand focus areas")

        if quality_metrics.actionability_score >= 0.7:
            strengths.append("Strong action orientation")
        else:
            weaknesses.append("Low actionability - generate more concrete steps")

        # Create improvement plan
        plan = {
            "timestamp": datetime.now().isoformat(),
            "analysis_period_hours": lookback_hours,
            "current_quality": {
                "overall": quality_metrics.overall_quality,
                "depth": quality_metrics.depth_score,
                "breadth": quality_metrics.breadth_score,
                "actionability": quality_metrics.actionability_score,
                "consistency": quality_metrics.consistency_score,
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "action_items": all_actions[:10],  # Top 10 actions
            "recommended_focus": self._recommend_focus_area(introspections),
            "next_review": (datetime.now() + timedelta(hours=24)).isoformat(),
        }

        logger.info(
            "self_improvement_plan_generated",
            actions=len(all_actions),
            quality=quality_metrics.overall_quality,
        )

        return plan

    def _recommend_focus_area(self, introspections: List[IntrospectionLog]) -> str:
        """Recommend which area needs most focus.

        Args:
            introspections: Recent introspection logs

        Returns:
            Recommended focus area
        """
        # Find area with most action items (needs most work)
        action_counts: Dict[str, int] = {}
        for log in introspections:
            action_counts[log.focus_area] = len(log.action_items)

        if action_counts:
            recommended = max(action_counts.items(), key=lambda x: x[1])[0]
            return recommended

        return "decision_making"  # Default

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about self-reflection activities.

        Returns:
            Statistics dictionary
        """
        total_introspections = len(self._introspection_logs)

        # Calculate focus area distribution
        focus_dist: Dict[str, int] = {}
        for log in self._introspection_logs:
            focus_dist[log.focus_area] = focus_dist.get(log.focus_area, 0) + 1

        # Calculate average confidence
        avg_confidence = 0.0
        if total_introspections > 0:
            avg_confidence = (
                sum(log.confidence for log in self._introspection_logs)
                / total_introspections
            )

        # Get latest quality metrics
        latest_quality = 0.0
        if self._reflection_history:
            latest_quality = self._reflection_history[-1].overall_quality

        return {
            "total_introspections": total_introspections,
            "focus_area_distribution": focus_dist,
            "average_confidence": avg_confidence,
            "latest_reflection_quality": latest_quality,
            "total_quality_evaluations": len(self._reflection_history),
            "timestamp": datetime.now().isoformat(),
        }

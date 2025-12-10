"""Problem Detection Engine - Phase 26C

Detects problems in real-time: performance, memory, accuracy, semantic drift.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import psutil

logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Current system state snapshot"""

    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    gpu_count: int
    gpu_memory_percent: float | None
    last_accuracy: float | None
    semantic_drift: float | None
    timestamp: float


@dataclass
class DetectedIssue:
    """Detected problem/issue"""

    type: str  # PERFORMANCE, MEMORY, ACCURACY, SEMANTIC_DRIFT
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    metric: str
    value: float
    description: str
    auto_fixable: bool = True


class ProblemDetectionEngine:
    """Detects problems in real-time"""

    def __init__(self):
        """Initialize problem detection engine"""
        self.known_issues: Dict[str, bool] = {}
        logger.info("ProblemDetectionEngine initialized")

    def get_system_state(self) -> SystemState:
        """Get current system state snapshot

        Returns:
            SystemState with current metrics
        """
        import time

        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)

        # GPU detection (simplified - can be expanded)
        gpu_count = 0
        gpu_memory_percent = None
        try:
            import torch

            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                if gpu_count > 0:
                    gpu_memory = torch.cuda.memory_allocated(0) / torch.cuda.max_memory_allocated(0)
                    gpu_memory_percent = gpu_memory * 100
        except ImportError:
            pass

        return SystemState(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_gb=memory_available_gb,
            gpu_count=gpu_count,
            gpu_memory_percent=gpu_memory_percent,
            last_accuracy=None,  # Will be set by consciousness metrics
            semantic_drift=None,  # Will be set by semantic memory
            timestamp=time.time(),
        )

    def detect_issues(self, system_state: SystemState | None = None) -> List[DetectedIssue]:
        """Detect issues in system state

        Args:
            system_state: Current system state (if None, will fetch)

        Returns:
            List of detected issues
        """
        if system_state is None:
            system_state = self.get_system_state()

        issues = []

        # Performance issues (CPU)
        if system_state.cpu_percent > 90:
            issues.append(
                DetectedIssue(
                    type="PERFORMANCE",
                    severity="CRITICAL",
                    metric="cpu_usage",
                    value=system_state.cpu_percent,
                    description=f"CPU usage critical: {system_state.cpu_percent:.1f}%",
                    auto_fixable=True,
                )
            )
        elif system_state.cpu_percent > 85:
            issues.append(
                DetectedIssue(
                    type="PERFORMANCE",
                    severity="HIGH",
                    metric="cpu_usage",
                    value=system_state.cpu_percent,
                    description=f"CPU usage high: {system_state.cpu_percent:.1f}%",
                    auto_fixable=True,
                )
            )

        # Memory issues
        if system_state.memory_percent > 95:
            issues.append(
                DetectedIssue(
                    type="MEMORY",
                    severity="CRITICAL",
                    metric="memory_usage",
                    value=system_state.memory_percent,
                    description=(
                        f"Memory usage critical: {system_state.memory_percent:.1f}% "
                        f"({system_state.memory_available_gb:.2f}GB available)"
                    ),
                    auto_fixable=True,
                )
            )
        elif system_state.memory_percent > 90:
            issues.append(
                DetectedIssue(
                    type="MEMORY",
                    severity="HIGH",
                    metric="memory_usage",
                    value=system_state.memory_percent,
                    description=f"Memory usage high: {system_state.memory_percent:.1f}%",
                    auto_fixable=True,
                )
            )

        # GPU memory issues
        if system_state.gpu_memory_percent is not None:
            if system_state.gpu_memory_percent > 95:
                issues.append(
                    DetectedIssue(
                        type="GPU_MEMORY",
                        severity="CRITICAL",
                        metric="gpu_memory_usage",
                        value=system_state.gpu_memory_percent,
                        description=f"GPU memory critical: {system_state.gpu_memory_percent:.1f}%",
                        auto_fixable=True,
                    )
                )

        # Accuracy issues (if available)
        if system_state.last_accuracy is not None:
            if system_state.last_accuracy < 0.5:
                issues.append(
                    DetectedIssue(
                        type="ACCURACY",
                        severity="CRITICAL",
                        metric="model_accuracy",
                        value=system_state.last_accuracy,
                        description=f"Model accuracy critical: {system_state.last_accuracy:.3f}",
                        auto_fixable=False,  # Requires model retraining
                    )
                )
            elif system_state.last_accuracy < 0.75:
                issues.append(
                    DetectedIssue(
                        type="ACCURACY",
                        severity="MEDIUM",
                        metric="model_accuracy",
                        value=system_state.last_accuracy,
                        description=f"Model accuracy low: {system_state.last_accuracy:.3f}",
                        auto_fixable=False,
                    )
                )

        # Semantic drift (if available)
        if system_state.semantic_drift is not None:
            if system_state.semantic_drift > 0.5:
                issues.append(
                    DetectedIssue(
                        type="SEMANTIC_DRIFT",
                        severity="HIGH",
                        metric="embedding_drift",
                        value=system_state.semantic_drift,
                        description=f"Semantic drift high: {system_state.semantic_drift:.3f}",
                        auto_fixable=True,
                    )
                )
            elif system_state.semantic_drift > 0.3:
                issues.append(
                    DetectedIssue(
                        type="SEMANTIC_DRIFT",
                        severity="MEDIUM",
                        metric="embedding_drift",
                        value=system_state.semantic_drift,
                        description=f"Semantic drift moderate: {system_state.semantic_drift:.3f}",
                        auto_fixable=True,
                    )
                )

        # Sort by severity (CRITICAL first)
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        issues.sort(key=lambda x: severity_order.get(x.severity, 99))

        return issues

    def classify_issue(self, issue: DetectedIssue) -> Dict[str, Any]:
        """Classify issue by type and severity

        Args:
            issue: Detected issue

        Returns:
            Classification dict
        """
        issue_id = f"{issue.type}_{issue.metric}"
        is_known = issue_id in self.known_issues

        return {
            "id": issue_id,
            "known": is_known,
            "severity": issue.severity,
            "auto_fixable": issue.auto_fixable,
            "type": issue.type,
            "metric": issue.metric,
        }

    def mark_issue_known(self, issue_id: str) -> None:
        """Mark issue as known (for future reference)

        Args:
            issue_id: Issue identifier
        """
        self.known_issues[issue_id] = True

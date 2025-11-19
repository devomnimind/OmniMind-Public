"""Automated Root Cause Analysis (RCA) engine with graph-based dependency analysis.

This module implements automated root cause analysis:
- Graph-based dependency modeling
- Failure correlation detection
- Causal chain reconstruction
- Impact analysis
"""

from __future__ import annotations

import logging
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ComponentType(str, Enum):
    """Types of system components."""

    SERVICE = "service"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    API = "api"
    WORKER = "worker"
    NETWORK = "network"
    STORAGE = "storage"


class FailureType(str, Enum):
    """Types of failures."""

    CRASH = "crash"
    TIMEOUT = "timeout"
    OVERLOAD = "overload"
    ERROR = "error"
    DEGRADATION = "degradation"
    UNAVAILABLE = "unavailable"


@dataclass
class Component:
    """Represents a system component."""

    component_id: str
    component_type: ComponentType
    name: str
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "component_id": self.component_id,
            "component_type": self.component_type.value,
            "name": self.name,
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "metadata": self.metadata,
        }


@dataclass
class Failure:
    """Represents a component failure."""

    failure_id: str
    component_id: str
    failure_type: FailureType
    timestamp: datetime
    description: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    symptoms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "failure_id": self.failure_id,
            "component_id": self.component_id,
            "failure_type": self.failure_type.value,
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "metrics": self.metrics,
            "symptoms": self.symptoms,
        }


@dataclass
class RootCauseAnalysis:
    """Result of root cause analysis."""

    failure_id: str
    root_causes: List[str]
    causal_chain: List[Tuple[str, str]]  # (component_id, failure_type)
    confidence: float
    explanation: str
    supporting_evidence: List[str]
    recommended_actions: List[str]
    analyzed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "failure_id": self.failure_id,
            "root_causes": self.root_causes,
            "causal_chain": self.causal_chain,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "supporting_evidence": self.supporting_evidence,
            "recommended_actions": self.recommended_actions,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


class DependencyGraph:
    """Graph representing component dependencies."""

    def __init__(self) -> None:
        """Initialize dependency graph."""
        self._components: Dict[str, Component] = {}
        self._adjacency: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)

    def add_component(
        self,
        component_id: str,
        component_type: ComponentType,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Component:
        """Add a component to the graph.

        Args:
            component_id: Unique identifier
            component_type: Type of component
            name: Display name
            metadata: Optional metadata

        Returns:
            Created component
        """
        component = Component(
            component_id=component_id,
            component_type=component_type,
            name=name,
            metadata=metadata or {},
        )
        self._components[component_id] = component
        logger.debug(f"Added component: {component_id} ({component_type.value})")
        return component

    def add_dependency(self, from_id: str, to_id: str) -> None:
        """Add a dependency relationship (from depends on to).

        Args:
            from_id: Component that depends
            to_id: Component being depended on
        """
        if from_id not in self._components or to_id not in self._components:
            logger.warning(f"Cannot add dependency: component not found")
            return

        self._adjacency[from_id].add(to_id)
        self._reverse_adjacency[to_id].add(from_id)

        self._components[from_id].dependencies.add(to_id)
        self._components[to_id].dependents.add(from_id)

        logger.debug(f"Added dependency: {from_id} -> {to_id}")

    def get_dependencies(self, component_id: str) -> Set[str]:
        """Get direct dependencies of a component.

        Args:
            component_id: Component ID

        Returns:
            Set of dependency IDs
        """
        return self._adjacency.get(component_id, set()).copy()

    def get_dependents(self, component_id: str) -> Set[str]:
        """Get direct dependents of a component.

        Args:
            component_id: Component ID

        Returns:
            Set of dependent IDs
        """
        return self._reverse_adjacency.get(component_id, set()).copy()

    def get_all_dependencies(self, component_id: str) -> Set[str]:
        """Get all transitive dependencies of a component.

        Args:
            component_id: Component ID

        Returns:
            Set of all dependency IDs (transitive)
        """
        visited: Set[str] = set()
        queue: Deque[str] = deque([component_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue

            visited.add(current)
            for dep in self._adjacency.get(current, set()):
                if dep not in visited:
                    queue.append(dep)

        visited.discard(component_id)  # Remove self
        return visited

    def get_all_dependents(self, component_id: str) -> Set[str]:
        """Get all transitive dependents of a component.

        Args:
            component_id: Component ID

        Returns:
            Set of all dependent IDs (transitive)
        """
        visited: Set[str] = set()
        queue: Deque[str] = deque([component_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue

            visited.add(current)
            for dep in self._reverse_adjacency.get(current, set()):
                if dep not in visited:
                    queue.append(dep)

        visited.discard(component_id)  # Remove self
        return visited

    def find_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """Find shortest path between two components.

        Args:
            from_id: Start component
            to_id: End component

        Returns:
            List of component IDs forming path, or None if no path
        """
        if from_id == to_id:
            return [from_id]

        visited: Set[str] = set()
        queue: Deque[Tuple[str, List[str]]] = deque([(from_id, [from_id])])

        while queue:
            current, path = queue.popleft()
            if current in visited:
                continue

            visited.add(current)

            for neighbor in self._adjacency.get(current, set()):
                if neighbor == to_id:
                    return path + [neighbor]
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_component(self, component_id: str) -> Optional[Component]:
        """Get component by ID.

        Args:
            component_id: Component ID

        Returns:
            Component or None
        """
        return self._components.get(component_id)


class RootCauseEngine:
    """Engine for automated root cause analysis."""

    def __init__(self) -> None:
        """Initialize RCA engine."""
        self.graph = DependencyGraph()
        self._failures: Dict[str, Failure] = {}
        self._failure_history: Deque[Failure] = deque(maxlen=1000)
        self._analyses: Dict[str, RootCauseAnalysis] = {}
        self._correlation_window = timedelta(minutes=5)

    def register_component(
        self,
        component_id: str,
        component_type: ComponentType,
        name: str,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a system component.

        Args:
            component_id: Unique identifier
            component_type: Type of component
            name: Display name
            dependencies: List of component IDs this depends on
            metadata: Optional metadata
        """
        self.graph.add_component(component_id, component_type, name, metadata)

        if dependencies:
            for dep_id in dependencies:
                self.graph.add_dependency(component_id, dep_id)

    def record_failure(
        self,
        failure_id: str,
        component_id: str,
        failure_type: FailureType,
        description: str,
        metrics: Optional[Dict[str, Any]] = None,
        symptoms: Optional[List[str]] = None,
    ) -> Failure:
        """Record a component failure.

        Args:
            failure_id: Unique identifier for failure
            component_id: Component that failed
            failure_type: Type of failure
            description: Description of failure
            metrics: Optional metrics at time of failure
            symptoms: Optional list of observed symptoms

        Returns:
            Created failure record
        """
        failure = Failure(
            failure_id=failure_id,
            component_id=component_id,
            failure_type=failure_type,
            timestamp=datetime.now(),
            description=description,
            metrics=metrics or {},
            symptoms=symptoms or [],
        )

        self._failures[failure_id] = failure
        self._failure_history.append(failure)

        logger.info(f"Recorded failure: {failure_id} in {component_id}")
        return failure

    def analyze_failure(self, failure_id: str) -> RootCauseAnalysis:
        """Perform root cause analysis on a failure.

        Args:
            failure_id: Failure to analyze

        Returns:
            Root cause analysis result
        """
        failure = self._failures.get(failure_id)
        if not failure:
            raise ValueError(f"Failure not found: {failure_id}")

        # Find correlated failures
        correlated = self._find_correlated_failures(failure)

        # Build causal chain
        causal_chain = self._build_causal_chain(failure, correlated)

        # Identify root causes
        root_causes = self._identify_root_causes(causal_chain)

        # Calculate confidence
        confidence = self._calculate_confidence(failure, causal_chain, correlated)

        # Generate explanation
        explanation = self._generate_explanation(failure, causal_chain, root_causes)

        # Gather supporting evidence
        evidence = self._gather_evidence(failure, correlated, causal_chain)

        # Generate recommendations
        recommendations = self._generate_recommendations(failure, root_causes)

        analysis = RootCauseAnalysis(
            failure_id=failure_id,
            root_causes=root_causes,
            causal_chain=causal_chain,
            confidence=confidence,
            explanation=explanation,
            supporting_evidence=evidence,
            recommended_actions=recommendations,
        )

        self._analyses[failure_id] = analysis
        logger.info(f"Completed RCA for {failure_id}: {len(root_causes)} root causes found")

        return analysis

    def _find_correlated_failures(self, failure: Failure) -> List[Failure]:
        """Find failures correlated in time with the given failure."""
        correlated: List[Failure] = []
        cutoff_time = failure.timestamp - self._correlation_window

        for hist_failure in reversed(self._failure_history):
            if hist_failure.failure_id == failure.failure_id:
                continue

            if hist_failure.timestamp < cutoff_time:
                break

            if hist_failure.timestamp <= failure.timestamp:
                correlated.append(hist_failure)

        return correlated

    def _build_causal_chain(
        self, failure: Failure, correlated: List[Failure]
    ) -> List[Tuple[str, str]]:
        """Build causal chain from correlated failures."""
        chain: List[Tuple[str, str]] = []

        # Sort correlated by timestamp (earliest first)
        correlated_sorted = sorted(correlated, key=lambda f: f.timestamp)

        # Find causal relationships based on dependency graph
        causal_failures: List[Failure] = []
        for corr_failure in correlated_sorted:
            # Check if the failed component is a dependency of the primary failure component
            # This means the correlated failure could have caused the primary failure
            dependencies = self.graph.get_all_dependencies(failure.component_id)
            if corr_failure.component_id in dependencies:
                causal_failures.append(corr_failure)

        # Build chain from root cause to primary failure
        if causal_failures:
            # Add causal failures first (root causes)
            for causal_failure in causal_failures:
                chain.append((causal_failure.component_id, causal_failure.failure_type.value))
        
        # Add primary failure at the end
        chain.append((failure.component_id, failure.failure_type.value))

        return chain

    def _identify_root_causes(self, causal_chain: List[Tuple[str, str]]) -> List[str]:
        """Identify root causes from causal chain."""
        if not causal_chain:
            return []

        # Root cause is typically the first failure in the causal chain
        root_causes: List[str] = []

        # The first component in the chain is likely the root cause
        if causal_chain:
            root_component_id = causal_chain[0][0]
            root_causes.append(root_component_id)

        # Also check for components with no upstream dependencies that failed
        for component_id, _ in causal_chain:
            dependencies = self.graph.get_dependencies(component_id)
            if not dependencies:
                if component_id not in root_causes:
                    root_causes.append(component_id)

        return root_causes

    def _calculate_confidence(
        self, failure: Failure, causal_chain: List[Tuple[str, str]], correlated: List[Failure]
    ) -> float:
        """Calculate confidence in the analysis."""
        confidence = 0.5  # Base confidence

        # Higher confidence if we found correlated failures
        if correlated:
            confidence += 0.2

        # Higher confidence if we have a clear causal chain
        if len(causal_chain) > 1:
            confidence += 0.2

        # Higher confidence if we have good metrics
        if failure.metrics:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_explanation(
        self, failure: Failure, causal_chain: List[Tuple[str, str]], root_causes: List[str]
    ) -> str:
        """Generate human-readable explanation."""
        if not causal_chain:
            return f"Isolated failure in {failure.component_id}"

        explanation_parts: List[str] = []

        if len(root_causes) == 1:
            root_comp = self.graph.get_component(root_causes[0])
            root_name = root_comp.name if root_comp else root_causes[0]
            explanation_parts.append(f"Root cause identified: {root_name}")
        else:
            explanation_parts.append(f"Multiple root causes identified: {', '.join(root_causes)}")

        if len(causal_chain) > 1:
            chain_desc = " → ".join(
                [self.graph.get_component(comp_id).name if self.graph.get_component(comp_id) else comp_id
                 for comp_id, _ in causal_chain]
            )
            explanation_parts.append(f"Failure propagation: {chain_desc}")

        return ". ".join(explanation_parts)

    def _gather_evidence(
        self, failure: Failure, correlated: List[Failure], causal_chain: List[Tuple[str, str]]
    ) -> List[str]:
        """Gather supporting evidence for the analysis."""
        evidence: List[str] = []

        # Primary failure evidence
        evidence.append(f"Primary failure: {failure.description} at {failure.timestamp.isoformat()}")

        # Correlated failures
        if correlated:
            evidence.append(f"Found {len(correlated)} correlated failures within time window")

        # Causal chain evidence
        if len(causal_chain) > 1:
            evidence.append(f"Identified {len(causal_chain)}-step causal chain")

        # Metrics evidence
        if failure.metrics:
            evidence.append(f"Metrics at failure: {failure.metrics}")

        # Symptoms evidence
        if failure.symptoms:
            evidence.append(f"Observed symptoms: {', '.join(failure.symptoms)}")

        return evidence

    def _generate_recommendations(self, failure: Failure, root_causes: List[str]) -> List[str]:
        """Generate recommended remediation actions."""
        recommendations: List[str] = []

        # Component-specific recommendations
        for root_cause_id in root_causes:
            component = self.graph.get_component(root_cause_id)
            if not component:
                continue

            if component.component_type == ComponentType.DATABASE:
                recommendations.extend([
                    f"Check {component.name} database connectivity and health",
                    "Review database query performance and indexes",
                    "Check for database locks or connection pool exhaustion",
                ])
            elif component.component_type == ComponentType.SERVICE:
                recommendations.extend([
                    f"Restart {component.name} service if necessary",
                    "Review service logs for error patterns",
                    "Check service resource utilization (CPU, memory)",
                ])
            elif component.component_type == ComponentType.NETWORK:
                recommendations.extend([
                    "Check network connectivity and latency",
                    "Review firewall and routing configurations",
                ])

        # Generic recommendations based on failure type
        if failure.failure_type == FailureType.OVERLOAD:
            recommendations.append("Consider scaling resources or load balancing")
        elif failure.failure_type == FailureType.TIMEOUT:
            recommendations.append("Review timeout configurations and increase if necessary")

        # Always include monitoring recommendation
        recommendations.append("Implement enhanced monitoring for early detection of similar issues")

        return recommendations

    def get_analysis(self, failure_id: str) -> Optional[RootCauseAnalysis]:
        """Get existing analysis for a failure.

        Args:
            failure_id: Failure ID

        Returns:
            Analysis or None
        """
        return self._analyses.get(failure_id)

    def get_component_health(self, component_id: str) -> Dict[str, Any]:
        """Get health status of a component based on failure history.

        Args:
            component_id: Component ID

        Returns:
            Health status dictionary
        """
        recent_failures = [
            f for f in self._failure_history
            if f.component_id == component_id
            and datetime.now() - f.timestamp < timedelta(hours=1)
        ]

        return {
            "component_id": component_id,
            "recent_failures": len(recent_failures),
            "health_status": "unhealthy" if len(recent_failures) > 3 else "healthy",
            "last_failure": recent_failures[-1].timestamp.isoformat() if recent_failures else None,
        }

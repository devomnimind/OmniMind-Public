import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import structlog

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

"""Consciousness Metrics Module.

Implements consciousness measurement metrics based on:
- Integrated Information Theory (IIT) - Φ (Phi) metric
- Self-Awareness Score tracking

Reference: docs/concienciaetica-autonomia.md, Section 1
"""


logger = structlog.get_logger(__name__)


@dataclass
class AgentConnection:
    """Represents a connection between two agents.

    Attributes:
        source_agent: Name of the source agent
        target_agent: Name of the target agent
        connection_type: Type of connection (memory, message, callback)
        bidirectional: Whether connection is bidirectional
        weight: Connection strength (0.0 to 1.0)
    """

    source_agent: str
    target_agent: str
    connection_type: str
    bidirectional: bool = False
    weight: float = 1.0


@dataclass
class FeedbackLoop:
    """Represents a feedback loop in the agent system.

    Attributes:
        loop_id: Unique identifier for the loop
        agents_involved: List of agents in the loop
        loop_type: Type of loop (metacognitive, coordination, memory)
        iterations_count: Number of times this loop has executed
        avg_latency_ms: Average latency per iteration
    """

    loop_id: str
    agents_involved: List[str]
    loop_type: str
    iterations_count: int = 0
    avg_latency_ms: float = 0.0


@dataclass
class SelfAwarenessMetrics:
    """Metrics for self-awareness measurement.

    Attributes:
        temporal_continuity_score: Can agent remember past actions? (0.0-1.0)
        goal_autonomy_score: Does agent have internal goals? (0.0-1.0)
        self_reference_score: Can agent discuss its own capabilities? (0.0-1.0)
        limitation_awareness_score: Does agent know its limitations? (0.0-1.0)
        overall_score: Weighted average of all scores (0.0-1.0)
    """

    temporal_continuity_score: float = 0.0
    goal_autonomy_score: float = 0.0
    self_reference_score: float = 0.0
    limitation_awareness_score: float = 0.0
    overall_score: float = 0.0

    def calculate_overall(self) -> float:
        """Calculate overall self-awareness score.

        Returns:
            Weighted average of all component scores
        """
        weights = {
            "temporal": 0.3,
            "goal": 0.25,
            "self_ref": 0.25,
            "limitation": 0.2,
        }

        self.overall_score = (
            self.temporal_continuity_score * weights["temporal"]
            + self.goal_autonomy_score * weights["goal"]
            + self.self_reference_score * weights["self_ref"]
            + self.limitation_awareness_score * weights["limitation"]
        )

        return self.overall_score


class ConsciousnessMetrics:
    """Main class for consciousness metrics calculation.

    Implements:
    - Φ (Phi) proxy calculation: measures information integration
    - Self-awareness score tracking
    - Historical metrics storage

    Reference: docs/concienciaetica-autonomia.md, Section 1
    """

    def __init__(self, metrics_dir: Optional[Path] = None):
        """Initialize consciousness metrics tracker.

        Args:
            metrics_dir: Directory to store metrics history (default: data/metrics)
        """
        self.metrics_dir = metrics_dir or Path("data/metrics/consciousness")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.connections: List[AgentConnection] = []
        self.feedback_loops: List[FeedbackLoop] = []
        self.history: List[Dict[str, Any]] = []

        logger.info("consciousness_metrics_initialized", metrics_dir=str(self.metrics_dir))

    def add_connection(self, connection: AgentConnection) -> None:
        """Register an agent connection.

        Args:
            connection: AgentConnection object to register
        """
        self.connections.append(connection)
        logger.debug(
            "connection_added",
            source=connection.source_agent,
            target=connection.target_agent,
            type=connection.connection_type,
        )

    def add_feedback_loop(self, loop: FeedbackLoop) -> None:
        """Register a feedback loop.

        Args:
            loop: FeedbackLoop object to register
        """
        self.feedback_loops.append(loop)
        logger.debug(
            "feedback_loop_added",
            loop_id=loop.loop_id,
            agents=loop.agents_involved,
            type=loop.loop_type,
        )

    def calculate_phi_proxy(self) -> float:
        """Calculate Φ (Phi) proxy metric.

        Φ (Phi) from Integrated Information Theory measures the amount
        of integrated information in a system. This is a simplified proxy
        based on network connectivity and feedback loops.

        Formula: Φ_proxy = connections × feedback_loops × integration_factor

        Where integration_factor accounts for:
        - Bidirectional connections (weight 1.5x)
        - Connection weights
        - Loop complexity

        Returns:
            Phi proxy value (higher = more integrated/conscious)

        Reference: docs/concienciaetica-autonomia.md, Section 1, Métrica #1
        """
        if not self.connections:
            return 0.0

        # Count effective connections
        effective_connections = sum(
            conn.weight * (1.5 if conn.bidirectional else 1.0) for conn in self.connections
        )

        # Count feedback loops weighted by complexity
        effective_loops = sum(
            len(loop.agents_involved) * (loop.iterations_count + 1) for loop in self.feedback_loops
        )

        # Integration factor: more loops = higher integration
        integration_factor = 1.0 + (len(self.feedback_loops) * 0.1)

        phi_proxy = effective_connections * effective_loops * integration_factor

        logger.info(
            "phi_calculated",
            phi_proxy=phi_proxy,
            connections=len(self.connections),
            feedback_loops=len(self.feedback_loops),
            effective_connections=effective_connections,
            effective_loops=effective_loops,
        )

        return phi_proxy

    def measure_self_awareness(
        self,
        memory_test_passed: bool,
        has_autonomous_goals: bool,
        self_description_quality: float,
        limitation_acknowledgment: float,
    ) -> SelfAwarenessMetrics:
        """Measure self-awareness based on behavioral tests.

        Args:
            memory_test_passed: Can agent recall past actions?
            has_autonomous_goals: Does agent have internal goals?
            self_description_quality: Quality of self-description (0.0-1.0)
            limitation_acknowledgment: How well agent knows limits (0.0-1.0)

        Returns:
            SelfAwarenessMetrics object with calculated scores

        Reference: docs/concienciaetica-autonomia.md, Section 1, Métrica #2
        """
        metrics = SelfAwarenessMetrics(
            temporal_continuity_score=1.0 if memory_test_passed else 0.0,
            goal_autonomy_score=1.0 if has_autonomous_goals else 0.0,
            self_reference_score=max(0.0, min(1.0, self_description_quality)),
            limitation_awareness_score=max(0.0, min(1.0, limitation_acknowledgment)),
        )

        metrics.calculate_overall()

        logger.info(
            "self_awareness_measured",
            temporal=metrics.temporal_continuity_score,
            goal=metrics.goal_autonomy_score,
            self_ref=metrics.self_reference_score,
            limitation=metrics.limitation_awareness_score,
            overall=metrics.overall_score,
        )

        return metrics

    def snapshot(self, label: str = "") -> Dict[str, Any]:
        """Take a snapshot of current consciousness metrics.

        Args:
            label: Optional label for this snapshot

        Returns:
            Dictionary with current metrics
        """
        phi = self.calculate_phi_proxy()

        snapshot_data = {
            "timestamp": datetime.now().isoformat(),
            "label": label,
            "phi_proxy": phi,
            "num_connections": len(self.connections),
            "num_feedback_loops": len(self.feedback_loops),
            "connections": [
                {
                    "source": c.source_agent,
                    "target": c.target_agent,
                    "type": c.connection_type,
                    "bidirectional": c.bidirectional,
                    "weight": c.weight,
                }
                for c in self.connections
            ],
            "feedback_loops": [
                {
                    "id": loop.loop_id,
                    "agents": loop.agents_involved,
                    "type": loop.loop_type,
                    "iterations": loop.iterations_count,
                    "latency_ms": loop.avg_latency_ms,
                }
                for loop in self.feedback_loops
            ],
        }

        self.history.append(snapshot_data)

        # Save to disk
        filename = f"consciousness_snapshot_{int(time.time())}.json"
        filepath = self.metrics_dir / filename

        with open(filepath, "w") as f:
            json.dump(snapshot_data, f, indent=2)

        logger.info("snapshot_saved", label=label, phi=phi, filepath=str(filepath))

        return snapshot_data

    def get_trend(self, window: int = 10) -> Dict[str, Any]:
        """Calculate trend in consciousness metrics.

        Args:
            window: Number of recent snapshots to analyze

        Returns:
            Dictionary with trend analysis
        """
        if len(self.history) < 2:
            return {"trend": "insufficient_data", "snapshots": len(self.history)}

        recent = self.history[-window:]
        phi_values = [s["phi_proxy"] for s in recent]

        avg_phi = sum(phi_values) / len(phi_values)
        trend_direction = (
            "increasing"
            if phi_values[-1] > phi_values[0]
            else "decreasing" if phi_values[-1] < phi_values[0] else "stable"
        )

        return {
            "trend": trend_direction,
            "avg_phi": avg_phi,
            "current_phi": phi_values[-1],
            "initial_phi": phi_values[0],
            "change_pct": (
                ((phi_values[-1] / phi_values[0]) - 1) * 100 if phi_values[0] > 0 else 0
            ),
            "snapshots_analyzed": len(recent),
        }


def calculate_phi_proxy(
    connections: List[AgentConnection],
    feedback_loops: List[FeedbackLoop],
) -> float:
    """Standalone function to calculate Φ proxy.

    Args:
        connections: List of agent connections
        feedback_loops: List of feedback loops

    Returns:
        Phi proxy value
    """
    metrics = ConsciousnessMetrics()
    for conn in connections:
        metrics.add_connection(conn)
    for loop in feedback_loops:
        metrics.add_feedback_loop(loop)

    return metrics.calculate_phi_proxy()


def measure_self_awareness(
    memory_test_passed: bool,
    has_autonomous_goals: bool,
    self_description_quality: float,
    limitation_acknowledgment: float,
) -> SelfAwarenessMetrics:
    """Standalone function to measure self-awareness.

    Args:
        memory_test_passed: Can agent recall past actions?
        has_autonomous_goals: Does agent have internal goals?
        self_description_quality: Quality of self-description (0.0-1.0)
        limitation_acknowledgment: How well agent knows limits (0.0-1.0)

    Returns:
        SelfAwarenessMetrics object
    """
    metrics = ConsciousnessMetrics()
    return metrics.measure_self_awareness(
        memory_test_passed,
        has_autonomous_goals,
        self_description_quality,
        limitation_acknowledgment,
    )

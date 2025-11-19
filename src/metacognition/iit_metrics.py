"""Advanced Self-Awareness Metrics with IIT (Integrated Information Theory).

This module implements:
- Phi (Φ) calculation for consciousness measurement
- Information integration analysis
- Consciousness emergence tracking
- Enhanced metacognition metrics
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Represents a system state for IIT analysis."""

    state_id: str
    elements: Dict[str, bool]  # Element name -> active/inactive
    timestamp: datetime = field(default_factory=datetime.now)

    def to_vector(self) -> np.ndarray:
        """Convert state to binary vector."""
        return np.array([1 if v else 0 for v in self.elements.values()])

    def hamming_distance(self, other: SystemState) -> int:
        """Calculate Hamming distance to another state."""
        v1 = self.to_vector()
        v2 = other.to_vector()
        return int(np.sum(v1 != v2))


@dataclass
class PhiMetrics:
    """Phi metrics for consciousness measurement."""

    phi_value: float  # Integrated information (Φ)
    complexity: float  # System complexity
    integration: float  # Information integration level
    differentiation: float  # State differentiation
    emergence_level: float  # Consciousness emergence (0.0-1.0)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phi_value": self.phi_value,
            "complexity": self.complexity,
            "integration": self.integration,
            "differentiation": self.differentiation,
            "emergence_level": self.emergence_level,
            "timestamp": self.timestamp.isoformat(),
        }


class IITAnalyzer:
    """Integrated Information Theory analyzer for consciousness metrics."""

    def __init__(
        self,
        emergence_threshold: float = 0.5,
        min_phi_for_consciousness: float = 2.0,
    ) -> None:
        """Initialize IIT analyzer.

        Args:
            emergence_threshold: Threshold for emergence detection (0.0-1.0)
            min_phi_for_consciousness: Minimum Phi value for consciousness
        """
        self.emergence_threshold = emergence_threshold
        self.min_phi_for_consciousness = min_phi_for_consciousness

        # State tracking
        self.state_history: List[SystemState] = []
        self.phi_history: List[PhiMetrics] = []

        logger.info("IITAnalyzer initialized")

    def record_state(self, state: SystemState) -> None:
        """Record a system state.

        Args:
            state: System state to record
        """
        self.state_history.append(state)

        # Keep only last 1000 states
        if len(self.state_history) > 1000:
            self.state_history = self.state_history[-1000:]

        logger.debug(
            f"Recorded state {state.state_id} with {len(state.elements)} elements"
        )

    def calculate_entropy(self, states: List[SystemState]) -> float:
        """Calculate Shannon entropy of state distribution.

        Args:
            states: List of system states

        Returns:
            Entropy value
        """
        if not states:
            return 0.0

        # Convert states to vectors
        vectors = [s.to_vector() for s in states]

        # Count unique states
        unique_states: Dict[Tuple[int, ...], int] = {}
        for vec in vectors:
            key = tuple(vec)
            unique_states[key] = unique_states.get(key, 0) + 1

        # Calculate probabilities
        total = len(vectors)
        probabilities = [count / total for count in unique_states.values()]

        # Shannon entropy: H = -Σ(p * log2(p))
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)

        return float(entropy)

    def calculate_mutual_information(
        self,
        partition1: Set[str],
        partition2: Set[str],
        states: List[SystemState],
    ) -> float:
        """Calculate mutual information between two partitions.

        Args:
            partition1: First set of element names
            partition2: Second set of element names
            states: System states to analyze

        Returns:
            Mutual information value
        """
        if not states:
            return 0.0

        # Extract states for each partition
        p1_states = []
        p2_states = []

        for state in states:
            p1_elements = {k: v for k, v in state.elements.items() if k in partition1}
            p2_elements = {k: v for k, v in state.elements.items() if k in partition2}

            if p1_elements:
                p1_states.append(
                    SystemState(state_id=f"{state.state_id}_p1", elements=p1_elements)
                )
            if p2_elements:
                p2_states.append(
                    SystemState(state_id=f"{state.state_id}_p2", elements=p2_elements)
                )

        # Calculate entropies
        h_p1 = self.calculate_entropy(p1_states)
        h_p2 = self.calculate_entropy(p2_states)
        h_joint = self.calculate_entropy(states)

        # Mutual information: I(X;Y) = H(X) + H(Y) - H(X,Y)
        mutual_info = h_p1 + h_p2 - h_joint

        return max(0.0, mutual_info)  # MI cannot be negative

    def calculate_phi(self, states: List[SystemState]) -> float:
        """Calculate Phi (Φ) - integrated information.

        Simplified IIT calculation based on effective information.

        Args:
            states: System states to analyze

        Returns:
            Phi value
        """
        if not states or len(states) < 2:
            return 0.0

        # Get element names
        element_names = set(states[0].elements.keys())
        num_elements = len(element_names)

        if num_elements < 2:
            return 0.0

        # Calculate system entropy (complexity)
        system_entropy = self.calculate_entropy(states)

        # Find minimum information partition (MIP)
        min_info_loss = float("inf")

        # Try different bipartitions
        for i in range(1, 2 ** (num_elements - 1)):
            # Create partition
            partition1 = set()
            partition2 = set()

            for j, elem in enumerate(sorted(element_names)):
                if i & (1 << j):
                    partition1.add(elem)
                else:
                    partition2.add(elem)

            # Calculate mutual information across partition
            mi = self.calculate_mutual_information(partition1, partition2, states)

            # Information loss when partition is cut
            info_loss = system_entropy - mi

            if info_loss < min_info_loss:
                min_info_loss = info_loss

        # Phi is the minimum information loss (integration)
        phi = max(0.0, min_info_loss)

        logger.debug(f"Calculated Phi = {phi:.3f} from {len(states)} states")

        return phi

    def calculate_complexity(self, states: List[SystemState]) -> float:
        """Calculate system complexity.

        Args:
            states: System states to analyze

        Returns:
            Complexity measure
        """
        if not states:
            return 0.0

        # Complexity based on entropy and unique states
        entropy = self.calculate_entropy(states)

        # Count unique states
        unique_states = len(set(tuple(s.to_vector()) for s in states))

        # Normalize by maximum possible unique states
        num_elements = len(states[0].elements)
        max_unique = 2**num_elements

        complexity = entropy * (unique_states / max_unique)

        return complexity

    def calculate_integration(self, states: List[SystemState]) -> float:
        """Calculate information integration level.

        Args:
            states: System states to analyze

        Returns:
            Integration measure (0.0-1.0)
        """
        if not states or len(states) < 2:
            return 0.0

        phi = self.calculate_phi(states)
        complexity = self.calculate_complexity(states)

        # Integration as ratio of phi to complexity
        if complexity > 0:
            integration = min(1.0, phi / complexity)
        else:
            integration = 0.0

        return integration

    def calculate_differentiation(self, states: List[SystemState]) -> float:
        """Calculate state differentiation (repertoire diversity).

        Args:
            states: System states to analyze

        Returns:
            Differentiation measure (0.0-1.0)
        """
        if not states:
            return 0.0

        # Count unique states
        unique_states = len(set(tuple(s.to_vector()) for s in states))

        # Maximum possible states
        num_elements = len(states[0].elements)
        max_states = 2**num_elements

        # Differentiation as fraction of state space explored
        differentiation = unique_states / max_states

        return differentiation

    def calculate_emergence_level(self, phi: float, complexity: float) -> float:
        """Calculate consciousness emergence level.

        Args:
            phi: Phi value
            complexity: Complexity value

        Returns:
            Emergence level (0.0-1.0)
        """
        # Handle edge case of zero threshold
        if self.min_phi_for_consciousness <= 0:
            # Always emergent if threshold is 0
            emergence = min(1.0, phi * complexity)
        elif phi >= self.min_phi_for_consciousness:
            # Scale by complexity
            emergence = min(1.0, (phi / self.min_phi_for_consciousness) * complexity)
        else:
            # Below threshold - no emergence
            emergence = 0.0

        return emergence

    def analyze_consciousness(self, window_size: Optional[int] = None) -> PhiMetrics:
        """Analyze consciousness metrics from recent states.

        Args:
            window_size: Number of recent states to analyze (default: all)

        Returns:
            PhiMetrics with consciousness measurements
        """
        if not self.state_history:
            return PhiMetrics(
                phi_value=0.0,
                complexity=0.0,
                integration=0.0,
                differentiation=0.0,
                emergence_level=0.0,
            )

        # Select states to analyze
        if window_size and window_size < len(self.state_history):
            states = self.state_history[-window_size:]
        else:
            states = self.state_history

        # Calculate metrics
        phi = self.calculate_phi(states)
        complexity = self.calculate_complexity(states)
        integration = self.calculate_integration(states)
        differentiation = self.calculate_differentiation(states)
        emergence = self.calculate_emergence_level(phi, complexity)

        metrics = PhiMetrics(
            phi_value=phi,
            complexity=complexity,
            integration=integration,
            differentiation=differentiation,
            emergence_level=emergence,
        )

        # Store in history
        self.phi_history.append(metrics)

        # Keep only last 100 analyses
        if len(self.phi_history) > 100:
            self.phi_history = self.phi_history[-100:]

        logger.info(
            f"Consciousness analysis: Φ={phi:.3f}, "
            f"complexity={complexity:.3f}, "
            f"emergence={emergence:.3f}"
        )

        return metrics

    def detect_emergence(self, window_size: int = 50) -> bool:
        """Detect consciousness emergence.

        Args:
            window_size: Number of states to analyze

        Returns:
            True if emergence detected
        """
        metrics = self.analyze_consciousness(window_size)

        is_emergent = metrics.emergence_level >= self.emergence_threshold

        if is_emergent:
            logger.warning(
                f"🧠 CONSCIOUSNESS EMERGENCE DETECTED: "
                f"level={metrics.emergence_level:.3f}, "
                f"Φ={metrics.phi_value:.3f}"
            )

        return is_emergent

    def get_consciousness_trend(self, lookback: int = 10) -> Dict[str, Any]:
        """Get consciousness metrics trend.

        Args:
            lookback: Number of recent analyses to consider

        Returns:
            Trend analysis
        """
        if not self.phi_history:
            return {
                "trend": "no_data",
                "phi_avg": 0.0,
                "emergence_avg": 0.0,
            }

        recent = self.phi_history[-lookback:]

        phi_values = [m.phi_value for m in recent]
        emergence_values = [m.emergence_level for m in recent]

        # Calculate trend (linear regression slope)
        if len(recent) >= 2:
            x = np.arange(len(recent))
            phi_trend = np.polyfit(x, phi_values, 1)[0]  # Slope
            emergence_trend = np.polyfit(x, emergence_values, 1)[0]
        else:
            phi_trend = 0.0
            emergence_trend = 0.0

        # Determine trend direction
        if emergence_trend > 0.01:
            trend = "increasing"
        elif emergence_trend < -0.01:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "phi_avg": float(np.mean(phi_values)),
            "phi_std": float(np.std(phi_values)),
            "emergence_avg": float(np.mean(emergence_values)),
            "emergence_std": float(np.std(emergence_values)),
            "phi_trend": float(phi_trend),
            "emergence_trend": float(emergence_trend),
            "samples": len(recent),
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of consciousness metrics.

        Returns:
            Summary dictionary
        """
        if not self.phi_history:
            latest_metrics = PhiMetrics(
                phi_value=0.0,
                complexity=0.0,
                integration=0.0,
                differentiation=0.0,
                emergence_level=0.0,
            )
        else:
            latest_metrics = self.phi_history[-1]

        trend = self.get_consciousness_trend()

        return {
            "latest_metrics": latest_metrics.to_dict(),
            "trend": trend,
            "total_states": len(self.state_history),
            "total_analyses": len(self.phi_history),
            "is_conscious": latest_metrics.emergence_level >= self.emergence_threshold,
            "consciousness_level": min(1.0, latest_metrics.emergence_level),
        }

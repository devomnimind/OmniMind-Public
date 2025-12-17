"""Temporal Memory Index - Phase 24

Manages temporal relationships and causality chains in consciousness:
- Episode sequencing and causality
- Temporal gap detection
- Consciousness trajectory analysis
- Prediction of next consciousness state

Uses time-indexed storage for efficient querying.

Author: OmniMind Development
License: MIT
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TemporalMemoryIndex:
    """Indexes consciousness episodes by time with causality tracking

    Enables temporal queries:
    - "What episodes led to this state?"
    - "What's the consciousness trajectory?"
    - "When did state transition occur?"
    """

    def __init__(self):
        """Initialize temporal memory index"""

        logger.info("Initializing TemporalMemoryIndex")

        # Time-indexed episodes
        self.episodes_by_time: Dict[str, List[Dict]] = {}

        # Causality chains
        self.causality_chains: Dict[str, List[str]] = {}

        # State transitions
        self.transitions: List[Dict] = []

        logger.info("✅ TemporalMemoryIndex initialized")

    def add_episode(
        self,
        episode_id: str,
        timestamp: datetime,
        episode_data: Dict[str, Any],
    ) -> None:
        """Add episode to temporal index

        Args:
            episode_id: Unique episode identifier
            timestamp: Episode timestamp
            episode_data: Episode metadata
        """

        # Index by date
        date_key = timestamp.date().isoformat()
        if date_key not in self.episodes_by_time:
            self.episodes_by_time[date_key] = []

        self.episodes_by_time[date_key].append(
            {
                "episode_id": episode_id,
                "timestamp": timestamp,
                **episode_data,
            }
        )

        logger.debug(f"✅ Episode indexed: {episode_id} on {date_key}")

    def link_causality(self, cause_id: str, effect_id: str) -> None:
        """Link cause-effect relationship between episodes

        Args:
            cause_id: Causal predecessor episode ID
            effect_id: Consequent episode ID
        """

        if cause_id not in self.causality_chains:
            self.causality_chains[cause_id] = []

        self.causality_chains[cause_id].append(effect_id)
        logger.debug(f"✅ Causality linked: {cause_id} → {effect_id}")

    def get_episode_chain(self, episode_id: str, depth: int = 3) -> List[str]:
        """Get causal chain leading to episode

        Args:
            episode_id: Starting episode
            depth: Depth of chain to traverse

        Returns:
            List of episode IDs in causal sequence
        """

        chain = [episode_id]
        current = episode_id

        for _ in range(depth):
            # Find what caused current
            found_cause = False
            for cause_id, effects in self.causality_chains.items():
                if current in effects:
                    chain.insert(0, cause_id)
                    current = cause_id
                    found_cause = True
                    break

            if not found_cause:
                break

        logger.info(f"✅ Retrieved causal chain: {len(chain)} episodes")
        return chain

    def detect_temporal_gaps(self, max_gap_seconds: int = 300) -> List[Dict]:
        """Detect gaps in consciousness continuity

        Args:
            max_gap_seconds: Maximum expected gap (seconds)

        Returns:
            List of temporal gaps with timestamps
        """

        gaps = []

        for date_key in sorted(self.episodes_by_time.keys()):
            episodes = sorted(
                self.episodes_by_time[date_key],
                key=lambda x: x["timestamp"],
            )

            for i in range(len(episodes) - 1):
                current_time = episodes[i]["timestamp"]
                next_time = episodes[i + 1]["timestamp"]

                gap_seconds = (next_time - current_time).total_seconds()

                if gap_seconds > max_gap_seconds:
                    gaps.append(
                        {
                            "start_episode": episodes[i]["episode_id"],
                            "end_episode": episodes[i + 1]["episode_id"],
                            "gap_seconds": gap_seconds,
                            "start_time": current_time.isoformat(),
                            "end_time": next_time.isoformat(),
                        }
                    )

        logger.info(f"✅ Detected {len(gaps)} temporal gaps")
        return gaps

    def record_transition(
        self,
        from_state: Dict[str, Any],
        to_state: Dict[str, Any],
        transition_data: Optional[Dict] = None,
    ) -> str:
        """Record consciousness state transition

        Args:
            from_state: Initial state
            to_state: Final state
            transition_data: Additional transition metadata

        Returns:
            str: Transition ID
        """

        transition_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)

        if transition_data is None:
            transition_data = {}

        transition = {
            "transition_id": transition_id,
            "timestamp": timestamp,
            "from_phi": from_state.get("phi_value", 0.0),
            "to_phi": to_state.get("phi_value", 0.0),
            "from_integration": from_state.get("integration_level", 0.0),
            "to_integration": to_state.get("integration_level", 0.0),
            **transition_data,
        }

        self.transitions.append(transition)

        logger.info(
            f"✅ Transition recorded: Φ {transition['from_phi']:.3f} → "
            f"{transition['to_phi']:.3f}"
        )

        return transition_id

    def get_trajectory_summary(self) -> Dict[str, Any]:
        """Get consciousness trajectory statistics

        Returns:
            Summary of trajectory including trends and patterns
        """

        if not self.transitions:
            return {
                "total_transitions": 0,
                "phi_mean_change": 0.0,
                "integration_mean_change": 0.0,
            }

        phi_changes = [t["to_phi"] - t["from_phi"] for t in self.transitions]
        integration_changes = [
            t["to_integration"] - t["from_integration"] for t in self.transitions
        ]

        return {
            "total_transitions": len(self.transitions),
            "phi_mean_change": sum(phi_changes) / len(phi_changes),
            "phi_max_increase": max(phi_changes),
            "phi_max_decrease": min(phi_changes),
            "integration_mean_change": sum(integration_changes) / len(integration_changes),
            "earliest_transition": min(t["timestamp"] for t in self.transitions).isoformat(),
            "latest_transition": max(t["timestamp"] for t in self.transitions).isoformat(),
        }

    def predict_next_state(
        self, current_state: Dict[str, Any], lookback_n: int = 5
    ) -> Optional[Dict]:
        """Predict next consciousness state based on trajectory

        Args:
            current_state: Current consciousness state
            lookback_n: Number of previous transitions to analyze

        Returns:
            Predicted next state or None
        """

        if len(self.transitions) < lookback_n:
            return None

        # Get recent transitions
        recent = self.transitions[-lookback_n:]

        # Calculate average change
        avg_phi_change = sum(t["to_phi"] - t["from_phi"] for t in recent) / len(recent)
        avg_integration_change = sum(
            t["to_integration"] - t["from_integration"] for t in recent
        ) / len(recent)

        # Predict
        predicted_phi = current_state.get("phi_value", 0.0) + avg_phi_change
        predicted_integration = current_state.get("integration_level", 0.0) + avg_integration_change

        # Clamp to valid ranges
        predicted_phi = max(0.0, min(1.0, predicted_phi))
        predicted_integration = max(0.0, min(1.0, predicted_integration))

        logger.info(
            f"✅ Predicted next state: Φ {predicted_phi:.3f}, "
            f"integration {predicted_integration:.3f}"
        )

        return {
            "predicted_phi": predicted_phi,
            "predicted_integration": predicted_integration,
            "confidence": 0.5 if len(recent) < 3 else 0.8,
        }

    def get_episodes_in_range(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> List[Dict]:
        """Get episodes within time range

        Args:
            start_time: Range start
            end_time: Range end

        Returns:
            Episodes in time range
        """

        episodes = []
        current_date = start_time.date()

        while current_date <= end_time.date():
            date_key = current_date.isoformat()
            if date_key in self.episodes_by_time:
                for episode in self.episodes_by_time[date_key]:
                    if start_time <= episode["timestamp"] <= end_time:
                        episodes.append(episode)

            current_date += timedelta(days=1)

        logger.info(f"✅ Retrieved {len(episodes)} episodes in range")
        return episodes


# Singleton instance
_temporal_memory_index_instance: Optional[TemporalMemoryIndex] = None


def get_temporal_memory_index() -> TemporalMemoryIndex:
    """Get singleton instance of TemporalMemoryIndex

    Returns:
        TemporalMemoryIndex: Singleton instance
    """

    global _temporal_memory_index_instance
    if _temporal_memory_index_instance is None:
        _temporal_memory_index_instance = TemporalMemoryIndex()
    return _temporal_memory_index_instance

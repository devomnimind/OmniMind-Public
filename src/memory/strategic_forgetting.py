"""
Strategic Forgetting Module.

Optimizes memory storage by identifying and removing
irrelevant, redundant, or low-value information.
Implements decay mechanisms based on access frequency and emotional significance.
"""

from typing import Any, Dict, List
import logging
from datetime import datetime, timedelta

from .semantic_memory import SemanticMemory

logger = logging.getLogger(__name__)


class StrategicForgetting:
    """
    Strategic Forgetting System.

    Prunes memories to maintain system efficiency.
    """

    def __init__(self, semantic_memory: SemanticMemory) -> None:
        """
        Initialize strategic forgetting.

        Args:
            semantic_memory: Reference to the semantic memory system.
        """
        self.semantic_memory = semantic_memory
        logger.info("Strategic Forgetting initialized")

    def prune_semantic_memory(
        self,
        retention_days: int = 30,
        min_strength: float = 0.2,
        min_access_count: int = 1,
    ) -> int:
        """
        Prune concepts from semantic memory.

        Removes concepts that are:
        1. Older than retention_days
        2. AND have strength < min_strength
        3. AND have access_count < min_access_count

        Args:
            retention_days: Age in days to consider for pruning.
            min_strength: Minimum strength to retain.
            min_access_count: Minimum access count to retain.

        Returns:
            Number of concepts pruned.
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        to_remove = []

        for name, concept in self.semantic_memory.concepts.items():
            # Check criteria
            is_old = concept.creation_time < cutoff_date
            is_weak = concept.strength < min_strength
            is_unused = concept.access_count < min_access_count

            # Protect "core" concepts (heuristic: no attributes = maybe temp, but let's be safe)
            # For now, just use the criteria
            if is_old and is_weak and is_unused:
                to_remove.append(name)

        # Execute pruning
        for name in to_remove:
            del self.semantic_memory.concepts[name]
            if name in self.semantic_memory.relationships:
                del self.semantic_memory.relationships[name]

            # Clean up incoming relationships (expensive, but necessary for consistency)
            for source, targets in self.semantic_memory.relationships.items():
                if name in targets:
                    del targets[name]

        logger.info(f"Pruned {len(to_remove)} concepts from semantic memory.")
        return len(to_remove)

    def prune_episodic_memory(
        self,
        episodes: List[Dict[str, Any]],
        min_emotional_intensity: float = 0.3,
        max_age_days: int = 90,
        preserve_count: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Prune episodic memory based on emotional intensity and age.

        Preserves episodes with:
        - High emotional intensity (>= min_emotional_intensity)
        - Recent timestamp (< max_age_days)
        - Top N most emotionally salient memories

        Args:
            episodes: List of episode dictionaries.
            min_emotional_intensity: Minimum emotional intensity to retain.
            max_age_days: Maximum age in days to retain low-intensity episodes.
            preserve_count: Minimum number of episodes to always preserve.

        Returns:
            Pruned list of episodes, sorted by emotional salience.
        """
        if not episodes:
            return []

        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        retained = []

        for episode in episodes:
            # Extract episode properties
            emotional_intensity = episode.get("emotional_intensity", 0.0)
            timestamp = episode.get("timestamp", datetime.now())
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)

            # Retention criteria
            is_emotionally_salient = emotional_intensity >= min_emotional_intensity
            is_recent = timestamp >= cutoff_date

            if is_emotionally_salient or is_recent:
                retained.append(episode)

        # Sort by emotional intensity (descending) to prioritize salient memories
        retained.sort(key=lambda e: e.get("emotional_intensity", 0.0), reverse=True)

        # Always preserve top N most salient memories, even if old
        if len(retained) < preserve_count and len(episodes) > len(retained):
            # Add remaining episodes sorted by salience
            remaining = [e for e in episodes if e not in retained]
            remaining.sort(key=lambda e: e.get("emotional_intensity", 0.0), reverse=True)
            to_add = preserve_count - len(retained)
            retained.extend(remaining[:to_add])

        pruned_count = len(episodes) - len(retained)
        logger.info(
            f"Pruned {pruned_count} episodic memories. "
            f"Retained {len(retained)} based on emotional salience."
        )

        return retained

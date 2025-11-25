"""
Memory Replay Module.

Facilitates offline learning by replaying significant episodes.
Used for reinforcement learning and memory consolidation.
"""

from typing import Any, Dict, List
import logging
import random

logger = logging.getLogger(__name__)


class MemoryReplay:
    """
    Memory Replay System.

    Selects and replays episodes to strengthen learning.
    """

    def __init__(self) -> None:
        """Initialize memory replay."""
        logger.info("Memory Replay initialized")

    def select_episodes_for_replay(
        self,
        episodes: List[Dict[str, Any]],
        count: int = 5,
        strategy: str = "significance",
    ) -> List[Dict[str, Any]]:
        """
        Select episodes for replay based on a strategy.

        Args:
            episodes: List of available episodes.
            count: Number of episodes to select.
            strategy: Selection strategy ('significance', 'random', 'recent').

        Returns:
            List of selected episodes.
        """
        if not episodes:
            return []

        selected = []

        if strategy == "significance":
            # Sort by emotional intensity/significance (descending)
            # Assumes episodes have 'significance' or 'intensity' field (0.0-1.0)
            sorted_episodes = sorted(
                episodes,
                key=lambda e: e.get("significance", e.get("intensity", 0.0)),
                reverse=True,
            )
            selected = sorted_episodes[:count]

        elif strategy == "recent":
            # Sort by timestamp (descending)
            # Assumes 'timestamp' field exists and is comparable
            sorted_episodes = sorted(episodes, key=lambda e: e.get("timestamp", ""), reverse=True)
            selected = sorted_episodes[:count]

        else:
            # Random selection
            selected = random.sample(episodes, min(len(episodes), count))

        logger.info(f"Selected {len(selected)} episodes for replay (strategy={strategy})")
        return selected

    def replay_episode(self, episode: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate the replay of a single episode.

        In a full system, this would reactivate neural patterns.
        Here, we just return the episode with a 'replayed' flag.

        Args:
            episode: The episode to replay.

        Returns:
            The replayed episode (potentially modified).
        """
        logger.debug(f"Replaying episode: {episode.get('id', 'unknown')}")

        # Simulate reinforcement
        replayed = episode.copy()
        replayed["replayed"] = True
        replayed["replay_count"] = replayed.get("replay_count", 0) + 1

        return replayed

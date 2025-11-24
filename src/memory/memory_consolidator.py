"""
Memory Consolidator Module.

Responsible for transferring information from short-term/episodic memory
to long-term semantic memory ("sleep" consolidation).
Identifies patterns and abstractions from repeated experiences.
"""

from typing import Any, Dict, List, Optional
import logging
from collections import Counter
from datetime import datetime

from .semantic_memory import SemanticMemory

logger = logging.getLogger(__name__)


class MemoryConsolidator:
    """
    Memory Consolidation System.

    Processes episodic memories to extract semantic knowledge.
    """

    def __init__(self, semantic_memory: SemanticMemory) -> None:
        """
        Initialize memory consolidator.

        Args:
            semantic_memory: Reference to the semantic memory system.
        """
        self.semantic_memory = semantic_memory
        logger.info("Memory Consolidator initialized")

    def consolidate(
        self, episodes: List[Dict[str, Any]], threshold: int = 3
    ) -> Dict[str, int]:
        """
        Consolidate a batch of episodes into semantic memory.

        Simple heuristic: repeated entities/keywords become concepts.

        Args:
            episodes: List of episode dictionaries (must have 'content' or 'tags').
            threshold: Number of occurrences required to form a concept.

        Returns:
            Statistics about the consolidation process.
        """
        if not episodes:
            return {"concepts_created": 0, "concepts_updated": 0}

        logger.info(f"Consolidating {len(episodes)} episodes...")

        # 1. Extract potential concepts (keywords/tags)
        term_counter = Counter()

        for episode in episodes:
            # Extract from tags if available
            if "tags" in episode:
                term_counter.update(episode["tags"])

            # Extract simple keywords from content (naive implementation)
            if "content" in episode and isinstance(episode["content"], str):
                words = [w.lower().strip(".,!?") for w in episode["content"].split()]
                # Filter small words
                significant_words = [w for w in words if len(w) > 4]
                term_counter.update(significant_words)

        # 2. Promote to Semantic Memory
        concepts_created = 0
        concepts_updated = 0

        for term, count in term_counter.items():
            if count >= threshold:
                # Check if concept exists
                existing = self.semantic_memory.retrieve_concept(term)

                if existing:
                    # Reinforce existing concept
                    self.semantic_memory.store_concept(
                        term, attributes={"consolidation_count": count}, overwrite=False
                    )
                    concepts_updated += 1
                else:
                    # Create new concept
                    self.semantic_memory.store_concept(
                        term,
                        attributes={
                            "source": "consolidation",
                            "first_consolidated": datetime.now().isoformat(),
                            "occurrence_count": count,
                        },
                    )
                    concepts_created += 1

        logger.info(
            f"Consolidation complete: {concepts_created} created, "
            f"{concepts_updated} updated."
        )

        return {
            "concepts_created": concepts_created,
            "concepts_updated": concepts_updated,
            "episodes_processed": len(episodes),
        }

    def extract_relationships(self, episodes: List[Dict[str, Any]]) -> int:
        """
        Extract relationships between concepts from episodes.

        Heuristic: If two concepts appear in the same episode frequently, relate them.

        Args:
            episodes: List of episodes.

        Returns:
            Number of relationships created.
        """
        # TODO: Implement co-occurrence analysis
        return 0

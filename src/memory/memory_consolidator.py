"""
Memory Consolidator Module.

Responsible for transferring information from short-term/episodic memory
to long-term semantic memory ("sleep" consolidation).
Identifies patterns and abstractions from repeated experiences.
"""

from typing import Any, Dict, List
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

    def consolidate(self, episodes: List[Dict[str, Any]], threshold: int = 3) -> Dict[str, int]:
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
            f"Consolidation complete: {concepts_created} created, " f"{concepts_updated} updated."
        )

        return {
            "concepts_created": concepts_created,
            "concepts_updated": concepts_updated,
            "episodes_processed": len(episodes),
        }

    def extract_relationships(
        self, episodes: List[Dict[str, Any]], min_cooccurrence: int = 2
    ) -> int:
        """
        Extract relationships between concepts from episodes.

        Analyzes co-occurrence patterns: if two concepts appear in the same
        episode frequently, a relationship is created between them.

        Args:
            episodes: List of episodes with 'tags' or 'content'.
            min_cooccurrence: Minimum number of co-occurrences to create relationship.

        Returns:
            Number of relationships created.
        """
        if not episodes:
            return 0

        # Track co-occurrences
        from collections import defaultdict
        from itertools import combinations

        cooccurrence_counts: Dict[tuple, int] = defaultdict(int)

        for episode in episodes:
            # Extract terms from episode
            terms = set()

            if "tags" in episode:
                terms.update(episode["tags"])

            if "content" in episode and isinstance(episode["content"], str):
                words = [w.lower().strip(".,!?") for w in episode["content"].split()]
                significant_words = [w for w in words if len(w) > 4]
                terms.update(significant_words)

            # Count co-occurrences (all pairs)
            for term_a, term_b in combinations(sorted(terms), 2):
                cooccurrence_counts[(term_a, term_b)] += 1

        # Create relationships for frequent co-occurrences
        relationships_created = 0

        for (concept_a, concept_b), count in cooccurrence_counts.items():
            if count >= min_cooccurrence:
                # Verify both concepts exist in semantic memory
                if self.semantic_memory.retrieve_concept(
                    concept_a
                ) and self.semantic_memory.retrieve_concept(concept_b):
                    # Create bidirectional relationship
                    self.semantic_memory.relate_concepts(
                        concept_a,
                        concept_b,
                        relationship_type="cooccurs_with",
                        strength=min(count / 10.0, 1.0),  # Normalize strength
                    )
                    relationships_created += 1

        logger.info(f"Extracted {relationships_created} relationships from co-occurrence analysis.")
        return relationships_created

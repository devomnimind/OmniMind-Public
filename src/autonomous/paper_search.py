"""Paper Search - Phase 26C Expansion

Search solutions in scientific papers via Phase 24 Semantic Memory.

Author: OmniMind Development
License: MIT
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from src.memory.semantic_memory_layer import SemanticMemoryLayer

logger = logging.getLogger(__name__)


class PaperSearch:
    """Search solutions in scientific papers via Phase 24"""

    def __init__(self, semantic_memory: SemanticMemoryLayer | None = None):
        """Initialize paper search

        Args:
            semantic_memory: SemanticMemoryLayer instance
        """
        if semantic_memory is None:
            from src.memory.semantic_memory_layer import get_semantic_memory

            semantic_memory = get_semantic_memory()

        self.semantic_memory = semantic_memory
        logger.info("PaperSearch initialized")

    def search_papers(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search papers in Phase 24 Semantic Memory

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of relevant papers with solutions
        """
        # Search in semantic memory
        results = self.semantic_memory.retrieve_similar(query, top_k=top_k)

        # Format as solutions
        solutions = []
        for result in results:
            solutions.append(
                {
                    "source": "papers",
                    "title": result.get("episode_text", "Unknown paper"),
                    "confidence": result.get("score", 0.5),
                    "solution": result.get("episode_data", {}).get("abstract", ""),
                    "paper_id": result.get("id", ""),
                    "metadata": result.get("episode_data", {}),
                }
            )

        logger.info(f"✅ Paper search completed: {len(solutions)} papers found")
        return solutions

    def search_by_topic(self, topic: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search papers by topic

        Args:
            topic: Topic to search for
            top_k: Number of results

        Returns:
            List of papers on the topic
        """
        return self.search_papers(f"topic: {topic}", top_k=top_k)

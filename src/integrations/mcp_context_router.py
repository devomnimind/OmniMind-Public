"""
MCP Server for context routing - selects relevant context snippets.
Port: 4332
"""

import logging
from typing import Any, Dict, List, Optional

from src.audit.immutable_audit import get_audit_system
from src.integrations.mcp_server import MCPConfig, MCPServer

logger = logging.getLogger(__name__)


class ContextRouterMCPServer(MCPServer):
    """MCP Server for routing and selecting relevant context."""

    STRATEGIES = ["similarity", "relevance", "frequency", "recent"]

    def __init__(self, config: Optional[MCPConfig] = None):
        super().__init__(config or self._default_config())
        self.audit_system = get_audit_system()

        # Register methods
        self._methods.update(
            {
                "route_context": self.route_context,
                "score_candidates": self.score_candidates,
                "get_strategies": self.get_strategies,
            }
        )

    @staticmethod
    def _default_config() -> MCPConfig:
        return MCPConfig(host="127.0.0.1", port=4332)

    def route_context(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        strategy: str = "similarity",
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Route and select relevant context snippets.

        Args:
            query: Query string
            candidates: List of candidate dicts with id, content, metadata
            strategy: Routing strategy (similarity, relevance, frequency, recent)
            top_k: Number of top candidates to select

        Returns:
            Dict with selected_ids, selected_snippets, and routing_info
        """
        try:
            if strategy not in self.STRATEGIES:
                return {
                    "status": "error",
                    "error": f"Invalid strategy: {strategy}. Use one of: {self.STRATEGIES}",
                }

            if not candidates:
                return {
                    "status": "success",
                    "selected_ids": [],
                    "selected_snippets": [],
                    "routing_info": {"strategy_used": strategy, "candidates_count": 0},
                }

            # Score candidates based on strategy
            scores = self.score_candidates(query, candidates, strategy)

            # Select top-k
            scored_candidates = [
                {**candidate, "score": scores[i], "rank": i + 1}
                for i, candidate in enumerate(candidates)
            ]

            # Sort by score descending
            scored_candidates.sort(key=lambda x: x["score"], reverse=True)
            selected = scored_candidates[:top_k]

            selected_ids = [c["id"] for c in selected]
            selected_snippets = [
                {
                    "id": c["id"],
                    "content": c.get("content", ""),
                    "score": c["score"],
                    "rank": c["rank"],
                }
                for c in selected
            ]

            # Audit logging
            if hasattr(self, "audit_system"):
                self.audit_system.log_action(
                    action="context_routed",
                    details={
                        "strategy": strategy,
                        "candidates_count": len(candidates),
                        "selected_count": len(selected),
                        "top_k": top_k,
                    },
                    category="context_router_mcp",
                )

            return {
                "status": "success",
                "selected_ids": selected_ids,
                "selected_snippets": selected_snippets,
                "routing_info": {
                    "strategy_used": strategy,
                    "candidates_count": len(candidates),
                    "selected_count": len(selected),
                    "average_score": (
                        sum(s["score"] for s in selected) / len(selected) if selected else 0
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Routing error: {e}")
            return {"status": "error", "error": str(e), "selected_ids": [], "selected_snippets": []}

    def score_candidates(
        self, query: str, candidates: List[Dict[str, Any]], strategy: str = "similarity"
    ) -> List[float]:
        """
        Score candidates based on strategy.

        Returns:
            List of scores (0-1) for each candidate
        """
        if strategy == "similarity":
            return self._score_similarity(query, candidates)
        elif strategy == "relevance":
            return self._score_relevance(query, candidates)
        elif strategy == "frequency":
            return self._score_frequency(query, candidates)
        else:  # recent
            return self._score_recent(query, candidates)

    def _score_similarity(self, query: str, candidates: List[Dict[str, Any]]) -> List[float]:
        """Jaccard similarity between query and candidate content."""
        query_words = set(query.lower().split())
        scores = []

        for candidate in candidates:
            content = candidate.get("content", "").lower()
            candidate_words = set(content.split())

            # Jaccard similarity
            intersection = len(query_words & candidate_words)
            union = len(query_words | candidate_words)

            score = intersection / union if union > 0 else 0
            scores.append(score)

        return scores

    def _score_relevance(self, query: str, candidates: List[Dict[str, Any]]) -> List[float]:
        """Use metadata relevance_score if available."""
        scores = []

        for candidate in candidates:
            metadata = candidate.get("metadata", {})
            relevance_score = metadata.get("relevance_score", 0.5)
            scores.append(min(1.0, max(0.0, relevance_score)))

        return scores

    def _score_frequency(self, query: str, candidates: List[Dict[str, Any]]) -> List[float]:
        """Score based on query term frequency in content."""
        query_lower = query.lower()
        scores = []

        for candidate in candidates:
            content = candidate.get("content", "").lower()
            frequency = content.count(query_lower)

            # Normalize: limit to max 10 occurrences = score 1.0
            score = min(1.0, frequency / 10.0)
            scores.append(score)

        return scores

    def _score_recent(self, query: str, candidates: List[Dict[str, Any]]) -> List[float]:
        """Score based on recency (if timestamp available in metadata)."""
        scores = []

        for candidate in candidates:
            metadata = candidate.get("metadata", {})
            created_at = metadata.get("created_at")

            # Simple heuristic: if has recent timestamp, higher score
            # In production, use actual timestamp comparison
            score = 0.8 if created_at else 0.3
            scores.append(score)

        return scores

    def get_strategies(self) -> Dict[str, Any]:
        """Get available routing strategies."""
        return {
            "status": "success",
            "available_strategies": self.STRATEGIES,
            "strategies_description": {
                "similarity": "Jaccard similarity between query and content",
                "relevance": "Use metadata relevance_score field",
                "frequency": "Count query term frequency in content",
                "recent": "Prefer recently created candidates",
            },
        }


if __name__ == "__main__":
    server = ContextRouterMCPServer()
    # run() method not available in base MCPServer yet

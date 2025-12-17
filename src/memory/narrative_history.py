"""Narrative History - Lacanian Memory

Lacanian approach to episodic memory: memory as retroactive construction, not storage.

Author: Fabrício da Silva + assistência de IA (Copilot GitHub/Cursor/Gemini/Perplexity)
License: MIT
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np

from memory.episodic_memory import EpisodicMemory

logger = logging.getLogger(__name__)


class NarrativeHistory:
    """
    Lacanian narrative history: memory is retroactive construction, not storage.

    Unlike EpisodicMemory (which stores events as they happen),
    NarrativeHistory constructs narratives retroactively:
    - Events are inscribed without immediate meaning
    - Meaning is assigned retroactively (Nachträglichkeit)
    - Narrative coherence is constructed, not retrieved
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "omnimind_narratives",
        embedding_dim: int = 384,
        max_size: int = 10000,
        systemic_memory: Optional[Any] = None,  # SystemicMemoryTrace opcional
    ):
        """Initialize narrative history

        Args:
            qdrant_url: Qdrant URL
            collection_name: Collection name
            embedding_dim: Embedding dimension
            max_size: Maximum narratives to store
            systemic_memory: Instância opcional de SystemicMemoryTrace para reconstrução topológica
        """
        # Use EpisodicMemory as backend but with Lacanian semantics
        self.backend = EpisodicMemory(
            qdrant_url=qdrant_url,
            collection_name=collection_name,
            embedding_dim=embedding_dim,
            max_size=max_size,
        )

        # Track retroactive significations
        self.retroactive_significations: Dict[str, Dict[str, Any]] = {}

        # Memória sistemática para reconstrução topológica
        self.systemic_memory = systemic_memory

        logger.info(
            "NarrativeHistory initialized (Lacanian approach, "
            f"systemic_memory={'enabled' if systemic_memory else 'disabled'})"
        )

    def inscribe_event(
        self,
        event: Dict[str, Any],
        without_meaning: bool = True,
    ) -> str:
        """Inscribe an event without immediate meaning (Lacanian)

        Args:
            event: Event data
            without_meaning: If True, event is inscribed without interpretation

        Returns:
            Event ID
        """
        # Store as episode but mark as awaiting signification
        episode_data = {
            "task": event.get("task", "unknown"),
            "action": event.get("action", "inscribed"),
            "result": event.get("result", ""),
            "reward": 0.0,  # No immediate reward (Lacanian)
            "metadata": {
                **event.get("metadata", {}),
                "awaiting_signification": without_meaning,
                "inscribed_at": datetime.now(timezone.utc).isoformat(),
            },
        }

        episode_id = self.backend.store_episode(**episode_data)

        if without_meaning:
            self.retroactive_significations[episode_id] = {
                "event": event,
                "awaiting": True,
            }

        logger.info(f"✅ Event inscribed: {episode_id} (awaiting signification: {without_meaning})")
        return episode_id

    def store_episode(
        self,
        task: str,
        action: str,
        result: str,
        reward: float = 0.0,
        metadata: Dict[str, Any] | None = None,
    ) -> str:
        """Store episode (compatibility method with EpisodicMemory API)

        Args:
            task: Task description
            action: Action taken
            result: Result of action
            reward: Reward value
            metadata: Additional metadata

        Returns:
            Episode ID
        """
        event = {
            "task": task,
            "action": action,
            "result": result,
            "metadata": metadata or {},
        }
        return self.inscribe_event(event, without_meaning=False)

    def retrieve_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve similar episodes (compatibility method with EpisodicMemory API)

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of similar episodes
        """
        # EpisodicMemory uses search_similar, not retrieve_similar
        results = self.backend.search_similar(query, top_k=top_k)
        # Convert SimilarEpisode TypedDict to Dict for compatibility
        return [dict(ep) for ep in results]

    def get_episode(self, episode_id: str) -> Dict[str, Any] | None:
        """Get episode by ID (compatibility method with EpisodicMemory API)

        Args:
            episode_id: Episode identifier

        Returns:
            Episode data or None
        """
        return self.backend.get_episode(episode_id)

    def retroactive_signification(
        self,
        event_id: str,
        new_meaning: str,
        retroactive_event: Dict[str, Any] | None = None,
    ) -> None:
        """Assign retroactive meaning to an event (Nachträglichkeit)

        Args:
            event_id: Event identifier
            new_meaning: New meaning to assign
            retroactive_event: Event that triggers retroactive signification
        """
        if event_id not in self.retroactive_significations:
            logger.warning(f"Event {event_id} not found for retroactive signification")
            return

        # Update retroactive signification
        self.retroactive_significations[event_id] = {
            "event": self.retroactive_significations[event_id]["event"],
            "awaiting": False,
            "retroactive_meaning": new_meaning,
            "retroactive_event": retroactive_event,
            "signified_at": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"✅ Retroactive signification: {event_id} → {new_meaning}")

    def reconstruct_narrative(
        self, query: str, use_systemic_memory: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Reconstrói narrativa retroativamente usando memória sistemática (topológica).

        Se systemic_memory está disponível, tenta usar reconstrução topológica primeiro.
        Fallback para backend (Qdrant) se não disponível ou falhar.

        Args:
            query: Query para reconstruir narrativa
            use_systemic_memory: Se True, tenta usar memória sistemática primeiro

        Returns:
            Lista de eventos reconstruídos (não recuperados)
        """
        # NOVO: Tenta usar SystemicMemoryTrace primeiro (topológico)
        if use_systemic_memory and self.systemic_memory is not None:
            try:
                # Converte query para embedding (simplificado)
                # Em produção usaria modelo de embedding
                # Por enquanto, cria embedding aleatório baseado em hash da query
                query_hash = hash(query) % (2**31)
                np.random.seed(query_hash)
                query_embedding = np.random.randn(self.backend.embedding_dim).astype(np.float32)
                # Normaliza
                query_embedding = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)

                # Reconstrói narrativa retroativamente usando deformações topológicas
                narrative = self.systemic_memory.reconstruct_narrative_retroactively(
                    query_embedding, num_steps=10
                )

                if narrative:
                    logger.debug(
                        f"Narrativa reconstruída via memória sistemática: {len(narrative)} passos"
                    )
                    return narrative
            except Exception as e:
                logger.warning(
                    f"Erro ao reconstruir narrativa via memória sistemática: {e}. "
                    "Usando fallback para backend."
                )

        # Fallback para backend (Qdrant)
        return self.construct_narrative(query, top_k=10).get("narrative", [])

    def construct_narrative(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """Construct narrative from events (not retrieve)

        Args:
            query: Query to construct narrative for
            top_k: Number of events to consider

        Returns:
            Constructed narrative
        """
        # Search for similar events
        similar = self.backend.search_similar(query, top_k=top_k)

        # Construct narrative retroactively
        narrative_events = []
        for episode in similar:
            # episode is SimilarEpisode TypedDict, convert to dict
            episode_dict = dict(episode) if not isinstance(episode, dict) else episode
            event_id = episode_dict.get("episode_id", "")
            if event_id in self.retroactive_significations:
                signification = self.retroactive_significations[event_id]
                narrative_events.append(
                    {
                        "event": signification.get("event", {}),
                        "retroactive_meaning": signification.get(
                            "retroactive_meaning", "No meaning assigned yet"
                        ),
                        "original_episode": episode_dict,
                    }
                )
            else:
                narrative_events.append(
                    {
                        "event": episode_dict,
                        "retroactive_meaning": "Awaiting signification",
                        "original_episode": episode_dict,
                    }
                )

        return {
            "query": query,
            "narrative": narrative_events,
            "coherence": self._calculate_narrative_coherence(narrative_events),
        }

    def _calculate_narrative_coherence(self, events: List[Dict[str, Any]]) -> float:
        """Calculate narrative coherence score

        Args:
            events: List of narrative events

        Returns:
            Coherence score (0.0 to 1.0)
        """
        if not events:
            return 0.0

        # Simple coherence: percentage of events with retroactive meaning
        signified = sum(
            1 for e in events if e.get("retroactive_meaning") != "Awaiting signification"
        )
        return signified / len(events) if events else 0.0

    def search_similar(
        self, query: str, top_k: int = 3, min_reward: float | None = None
    ) -> List[Dict[str, Any]]:
        """Search for similar episodes (compatibility method with EpisodicMemory API)

        Args:
            query: Search query
            top_k: Number of results
            min_reward: Minimum reward filter (optional)

        Returns:
            List of similar episodes
        """
        results = self.backend.search_similar(query, top_k=top_k, min_reward=min_reward)
        # Convert SimilarEpisode TypedDict to Dict for compatibility
        return [dict(ep) for ep in results]

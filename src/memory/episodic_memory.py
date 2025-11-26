from __future__ import annotations

"""Typed episodic memory manager backed by Qdrant."""

import hashlib
import logging
from datetime import datetime, timezone
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypedDict,
    cast,
)

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

if TYPE_CHECKING:  # pragma: no cover - optional dependency typing only
    from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


class EpisodePayload(TypedDict):
    """Canonical payload stored in Qdrant."""

    episode_id: str
    timestamp: str
    task: str
    action: str
    result: str
    reward: float
    metadata: Dict[str, Any]


class SimilarEpisode(TypedDict):
    """Search result returned to agents."""

    score: float
    episode_id: str
    task: str
    action: str
    result: str
    reward: float
    timestamp: str


def _load_embedding_model(model_name: str) -> Optional["SentenceTransformer"]:
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:
        logger.warning(
            "SentenceTransformer import failed: %s. Using deterministic embeddings.",
            exc,
        )
        return None

    try:
        return SentenceTransformer(model_name)
    except Exception as exc:
        logger.warning(
            ("Failed to load SentenceTransformer %s: %s. " "Using deterministic embeddings."),
            model_name,
            exc,
        )
        return None


class EpisodicMemory:
    """
    Manages episodic memory using Qdrant vector database.
    Stores experiences as: (task, action, result, reward) tuples.
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "omnimind_episodes",
        embedding_dim: int = 384,
    ) -> None:
        self.client: QdrantClient = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self._embedding_model: Optional["SentenceTransformer"] = None
        self._model_attempted = False

        # Initialize collection if it does not exist.
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create collection if it does not exist."""
        try:
            collections = self.client.get_collections().collections or []
            collection_names = [info.name for info in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.embedding_dim, distance=qmodels.Distance.COSINE
                    ),
                )
                logger.info("Created Qdrant collection: %s", self.collection_name)
        except Exception as exc:
            logger.warning("Failed to ensure Qdrant collection: %s", exc)

    def _get_embedding_model(self) -> Optional["SentenceTransformer"]:
        """Lazy load embedding model."""
        if not self._model_attempted:
            self._embedding_model = _load_embedding_model("all-MiniLM-L6-v2")
            self._model_attempted = True
        return self._embedding_model

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding from text using SentenceTransformer with fallback."""
        model = self._get_embedding_model()
        if model:
            try:
                encoded = model.encode(text, normalize_embeddings=True)
                # encoded is ndarray[Any] for single string input
                return [float(x) for x in encoded]  # type: ignore[arg-type,union-attr]
            except Exception as exc:
                logger.warning(
                    (
                        "Embedding model error for text snippet '%s': %s. "
                        "Using deterministic fallback."
                    ),
                    text[:32],
                    exc,
                )
        # Phase 8: replace deterministic hash fallback with a resilient
        # hybrid embedding pipeline to avoid semantic drift when primary
        # models become unavailable.
        return self._hash_based_embedding(text)

    def _hash_based_embedding(self, text: str) -> List[float]:
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()

        embedding = []
        for i in range(self.embedding_dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding.append((byte_val / 255.0) * 2 - 1)
        return embedding

    def store_episode(
        self,
        task: str,
        action: str,
        result: str,
        reward: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store an episode (experience) in memory.

        Args:
            task: What the agent was trying to do
            action: What action the agent took
            result: What happened (outcome)
            reward: Reward signal (-1.0 to 1.0, used for RLAIF)
            metadata: Additional context

        Returns:
            episode_id: Unique identifier for this episode
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        # Create episode text for embedding
        episode_text = f"Task: {task}\nAction: {action}\nResult: {result}"
        embedding = self._generate_embedding(episode_text)

        # Generate unique ID (Qdrant requires UUID or int)
        hash_source = f"{timestamp}{task}{action}".encode()
        hash_hex = hashlib.sha256(hash_source).hexdigest()[:16]
        hash_int = int(hash_hex, 16)

        # Prepare payload
        payload_metadata: Dict[str, Any] = dict(metadata) if metadata else {}
        payload: EpisodePayload = {
            "episode_id": str(hash_int),
            "timestamp": timestamp,
            "task": task,
            "action": action,
            "result": result,
            "reward": reward,
            "metadata": payload_metadata,
        }

        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                # Use deterministic integer IDs for deduplication.
                qmodels.PointStruct(id=hash_int, vector=embedding, payload=dict(payload))
            ],
        )

        return str(hash_int)

    def search_similar(
        self, query: str, top_k: int = 3, min_reward: Optional[float] = None
    ) -> List[SimilarEpisode]:
        """
        Search for similar past experiences.

        Args:
            query: Current task/situation to search for
            top_k: Number of similar episodes to return
            min_reward: Only return episodes with reward >= this value

        Returns:
            List of similar episodes with their scores
        """
        query_embedding = self._generate_embedding(query)

        # Build filter
        query_filter: Optional[qmodels.Filter] = None
        if min_reward is not None:
            query_filter = qmodels.Filter(
                must=[qmodels.FieldCondition(key="reward", range=qmodels.Range(gte=min_reward))]
            )

        # Search
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        ).points

        # Format results
        results: List[SimilarEpisode] = []
        hits: Sequence[qmodels.ScoredPoint] = search_result or []
        for hit in hits:
            payload = hit.payload or {}
            results.append(
                SimilarEpisode(
                    score=float(hit.score),
                    episode_id=str(payload.get("episode_id", "")),
                    task=str(payload.get("task", "")),
                    action=str(payload.get("action", "")),
                    result=str(payload.get("result", "")),
                    reward=float(payload.get("reward", 0.0)),
                    timestamp=str(payload.get("timestamp", "")),
                )
            )

        return results

    def get_episode(self, episode_id: str) -> Optional[EpisodePayload]:
        """Retrieve specific episode by ID."""
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[int(episode_id)],  # Convert string ID to int
            )

            if points and points[0].payload is not None:
                payload = points[0].payload
                metadata = cast(Dict[str, Any], payload.get("metadata") or {})
                return EpisodePayload(
                    episode_id=str(payload.get("episode_id", "")),
                    timestamp=str(payload.get("timestamp", "")),
                    task=str(payload.get("task", "")),
                    action=str(payload.get("action", "")),
                    result=str(payload.get("result", "")),
                    reward=float(payload.get("reward", 0.0)),
                    metadata=dict(metadata),
                )
            return None
        except Exception as exc:  # pragma: no cover
            logger.error("Error retrieving episode %s: %s", episode_id, exc)
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        collection_info = self.client.get_collection(self.collection_name)

        return {
            "total_episodes": collection_info.points_count,
            "vector_dim": self.embedding_dim,
            "collection_name": self.collection_name,
        }

    def consolidate_memory(self, min_episodes: int = 100) -> Dict[str, Any]:
        """Consolidate similar experiences to reduce duplicates."""
        stats = self.get_stats()
        total = stats["total_episodes"]

        if total == 0 or total < min_episodes:
            return {
                "status": "skipped",
                "total_episodes": total,
                "duplicates_removed": 0,
                "remaining": total,
            }

        seen: Set[Tuple[Optional[str], Optional[str], Optional[str]]] = set()
        duplicates: List[int] = []
        offset: Optional[qmodels.ExtendedPointId] = None
        batch = 128

        while True:
            points, new_offset = self.client.scroll(
                collection_name=self.collection_name,
                offset=offset,
                limit=batch,
                with_payload=True,
                with_vectors=False,
            )
            if not points:
                break

            for point in points:
                payload = point.payload or {}
                key = (
                    payload.get("task"),
                    payload.get("action"),
                    payload.get("result"),
                )
                if key in seen and isinstance(point.id, int):
                    duplicates.append(point.id)
                else:
                    seen.add(key)

            offset = new_offset
            if offset is None:
                break

        removed = 0
        if duplicates:
            self.client.delete(collection_name=self.collection_name, points_selector=duplicates)
            removed = len(duplicates)

        remaining_stats = self.get_stats()
        remaining = remaining_stats["total_episodes"]
        print(
            f"⚙️  Consolidated memory: removed {removed} duplicate(s), "
            f"{remaining} entries remain"
        )

        return {
            "status": "consolidated",
            "total_episodes": total,
            "duplicates_removed": removed,
            "remaining": remaining,
        }


# Export Qdrant types for use in tests and type annotations
__all__ = [
    "EpisodicMemory",
    "EpisodePayload",
    "QdrantClient",
    "PointStruct",
    "Distance",
    "VectorParams",
    "Filter",
    "FieldCondition",
    "MatchValue",
]

# Re-export Qdrant types
PointStruct = qmodels.PointStruct
Distance = qmodels.Distance
VectorParams = qmodels.VectorParams
Filter = qmodels.Filter
FieldCondition = qmodels.FieldCondition
MatchValue = qmodels.MatchValue

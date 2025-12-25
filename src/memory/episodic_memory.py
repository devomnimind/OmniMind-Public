from __future__ import annotations

"""Typed episodic memory manager backed by Qdrant."""

import hashlib
import logging
import os
import warnings
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
    Union,
    cast,
)
from uuid import UUID
import json  # Added for metadata serialization

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from qdrant_client.http.models import PointIdsList

from src.security.privacy_vault import PrivacyVault  # New Import

if TYPE_CHECKING:  # pragma: no cover - optional dependency typing only
    from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)

# Memory cap for episodic buffer
MAX_EPISODIC_SIZE = 10000  # Maximum episodes to store
EPISODIC_EVICTION_POLICY = "lru"  # Least Recently Used eviction

warnings.warn(
    "🔒 SECURE BACKEND: EpisodicMemory is the encrypted storage layer for NarrativeHistory. "
    "Direct usage is permitted for internal system functions only. "
    "NarrativeHistory should be preferred for high-level cognition.",
    UserWarning,
    stacklevel=2,
)


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


def _load_embedding_model(model_name: str) -> Optional[Any]:  # returns Engine or SentenceTransformer
    """Load SentenceTransformer via Safe Loader (Singleton)."""
    try:
        from src.embeddings.safe_transformer_loader import load_sentence_transformer_safe

        # Use Safe Loader
        engine, _ = load_sentence_transformer_safe(model_name=model_name)
        return engine

    except Exception as exc:
        logger.warning(
            "Safe embedding loading failed: %s. Using deterministic embeddings.",
            exc,
        )
        return None


class EpisodicMemory:
    """
    Manages episodic memory using Qdrant vector database.
    Stores experiences as: (task, action, result, reward) tuples.

    CRITICAL FIX: Implements memory cap (MAX_EPISODIC_SIZE=10000) with LRU
    eviction to prevent unbounded memory growth.
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "omnimind_episodes",
        embedding_dim: int = 384,
        max_size: int = MAX_EPISODIC_SIZE,
    ) -> None:
        warnings.warn(
            "🔒 SECURE STORAGE: Using EpisodicMemory (Encrypted). "
            "Prefer NarrativeHistory for cognitive operations.",
            UserWarning,
            stacklevel=2,
        )
        self.client: QdrantClient = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self._embedding_model: Optional["SentenceTransformer"] = None
        self._model_attempted = False
        self.max_size = max_size
        self._episode_count = 0  # Track total episodes stored (for LRU)
        self._access_timestamps: Dict[str, float] = {}  # Track last access time for LRU

        # Initialize Privacy Vault for encryption
        self.vault = PrivacyVault()

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
            self._embedding_model = _load_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
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
                    f"GPU Embedding inference failed for text snippet '{text[:32]}...': {exc}. "
                    "Attempting fallback to CPU..."
                )
                try:
                    # Tentar mover para CPU e executar novamente
                    model = model.to("cpu")
                    encoded = model.encode(text, normalize_embeddings=True, device="cpu")
                    logger.info("✓ CPU fallback successful for embedding generation")
                    return [float(x) for x in encoded]  # type: ignore
                except Exception as cpu_exc:
                    logger.warning(
                        (
                            "CPU fallback also failed for text snippet '%s': %s. "
                            "Using deterministic fallback."
                        ),
                        text[:32],
                        cpu_exc,
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

    def _check_and_evict_lru(self) -> None:
        """
        Check memory size and evict least recently used episodes if exceeding limit.

        CRITICAL FIX: Implements LRU eviction to prevent unbounded growth.
        When max_size is exceeded, removes episodes with oldest access timestamps.
        """
        try:
            # Get collection stats
            collection_info = self.client.get_collection(self.collection_name)
            current_size = collection_info.points_count or 0

            if current_size >= self.max_size:
                # Need to evict oldest episodes
                num_to_evict = max(1, int(current_size * 0.1))  # Evict 10%
                logger.warning(
                    f"EpisodicMemory reaching capacity ({current_size}/{self.max_size}). "
                    f"Evicting {num_to_evict} least recently used episodes."
                )

                # Sort by access timestamp and get IDs to evict
                sorted_accesses = sorted(
                    self._access_timestamps.items(), key=lambda x: x[1]
                )  # Oldest first
                ids_to_evict: list[int] = [
                    int(ep_id) for ep_id, _ in sorted_accesses[:num_to_evict]
                ]

                # Delete from Qdrant
                if ids_to_evict:
                    self.client.delete(
                        collection_name=self.collection_name,
                        points_selector=qmodels.PointIdsList(points=ids_to_evict),  # type: ignore
                    )
                    logger.info(f"Evicted {len(ids_to_evict)} episodes to maintain memory cap.")

                    # Clean up tracking
                    for ep_id in ids_to_evict:
                        self._access_timestamps.pop(str(ep_id), None)

        except Exception as e:
            logger.error(f"Error during LRU eviction: {e}. Continuing without eviction.")

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

        Note:
            CRITICAL FIX: Memory capping implemented. If storing would exceed
            MAX_EPISODIC_SIZE, least recently used episodes are evicted first.
        """
        # Check and evict if necessary BEFORE storing new episode
        self._check_and_evict_lru()

        timestamp = datetime.now(timezone.utc).isoformat()

        # Create episode text for embedding
        episode_text = f"Task: {task}\nAction: {action}\nResult: {result}"
        embedding = self._generate_embedding(episode_text)

        # Generate unique ID (Qdrant requires UUID or int)
        hash_source = f"{timestamp}{task}{action}".encode()
        hash_hex = hashlib.sha256(hash_source).hexdigest()[:16]
        hash_int = int(hash_hex, 16)
        episode_id_str = str(hash_int)

        # Prepare payload with ENCRYPTION
        # We encrypt content fields to ensure privacy at rest (LGPD/GDPR)
        # Random IV in Fernet ensures different ciphertext for same plaintext
        encrypted_task = self.vault.encrypt_memory(task)
        encrypted_action = self.vault.encrypt_memory(action)
        encrypted_result = self.vault.encrypt_memory(result)

        # Handle metadata encryption
        # We wrap the real metadata in a special key to maintain the Dict type hint
        if metadata:
            metadata_str = json.dumps(metadata)
            encrypted_metadata_str = self.vault.encrypt_memory(metadata_str)
            safe_metadata = {"__encrypted_metadata__": encrypted_metadata_str}
        else:
            safe_metadata = {}

        payload: EpisodePayload = {
            "episode_id": episode_id_str,
            "timestamp": timestamp,
            "task": encrypted_task,
            "action": encrypted_action,
            "result": encrypted_result,
            "reward": reward,  # Numeric, not encrypted
            "metadata": safe_metadata,
        }

        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                # Use deterministic integer IDs for deduplication.
                qmodels.PointStruct(id=hash_int, vector=embedding, payload=dict(payload))
            ],
        )

        # Track access time for LRU
        self._access_timestamps[episode_id_str] = datetime.now(timezone.utc).timestamp()
        self._episode_count += 1

        return episode_id_str

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

        Note:
            Updates access timestamps for LRU tracking of searched episodes.
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

        # Format results and update LRU access times
        results: List[SimilarEpisode] = []
        hits: Sequence[qmodels.ScoredPoint] = search_result or []
        current_time = datetime.now(timezone.utc).timestamp()

        for hit in hits:
            payload = hit.payload or {}
            episode_id = str(payload.get("episode_id", ""))

            # Update access timestamp for LRU tracking
            self._access_timestamps[episode_id] = current_time

            # Decrypt payload fields
            decrypted_task = self.vault.decrypt_memory(str(payload.get("task", "")))
            decrypted_action = self.vault.decrypt_memory(str(payload.get("action", "")))
            decrypted_result = self.vault.decrypt_memory(str(payload.get("result", "")))

            results.append(
                SimilarEpisode(
                    score=float(hit.score),
                    episode_id=episode_id,
                    task=decrypted_task,
                    action=decrypted_action,
                    result=decrypted_result,
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
                raw_metadata = cast(Dict[str, Any], payload.get("metadata") or {})

                # Decrypt Metadata if encrypted
                if "__encrypted_metadata__" in raw_metadata:
                    try:
                        encrypted_str = raw_metadata["__encrypted_metadata__"]
                        decrypted_str = self.vault.decrypt_memory(encrypted_str)
                        final_metadata = json.loads(decrypted_str)
                    except Exception as e:
                        logger.warning(f"Failed to decrypt metadata for {episode_id}: {e}")
                        final_metadata = {"error": "decryption_failed"}
                else:
                    final_metadata = raw_metadata

                return EpisodePayload(
                    episode_id=str(payload.get("episode_id", "")),
                    timestamp=str(payload.get("timestamp", "")),
                    task=self.vault.decrypt_memory(str(payload.get("task", ""))),
                    action=self.vault.decrypt_memory(str(payload.get("action", ""))),
                    result=self.vault.decrypt_memory(str(payload.get("result", ""))),
                    reward=float(payload.get("reward", 0.0)),
                    metadata=final_metadata,
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
                # Decrypt checks for deduplication (since ciphertext is random)
                task_dec = self.vault.decrypt_memory(str(payload.get("task", "")))
                action_dec = self.vault.decrypt_memory(str(payload.get("action", "")))
                result_dec = self.vault.decrypt_memory(str(payload.get("result", "")))

                key = (
                    task_dec,
                    action_dec,
                    result_dec,
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
            # Delete duplicates using PointIdsList with properly typed point IDs
            points_to_delete: List[Union[int, str, UUID]] = [int(p) for p in duplicates]
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=points_to_delete),
            )
            removed = len(duplicates)

        remaining_stats = self.get_stats()
        remaining = remaining_stats["total_episodes"]
        logger.info(
            f"Consolidated memory: removed {removed} duplicate(s), " f"{remaining} entries remain"
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

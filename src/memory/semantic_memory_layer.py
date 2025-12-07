"""Semantic Memory Layer with Qdrant - Phase 24

Implements persistent semantic memory for consciousness states using:
- SentenceTransformer for embeddings (384-dimensional)
- Qdrant for vector storage and similarity search
- Metadata storage for consciousness states, phi values, qualia signatures

Architecture:
- SemanticMemoryLayer: Main interface for semantic memory operations
- Episode: Encapsulates consciousness episode with embeddings
- get_semantic_memory(): Singleton access

Author: OmniMind Development
License: MIT
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

try:
    from sentence_transformers import (
        SentenceTransformer,  # type: ignore[import-untyped]
    )

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None  # type: ignore[misc,assignment]
    TRANSFORMERS_AVAILABLE = False

from src.integrations.qdrant_integration import (
    QdrantIntegration,
    QdrantPoint,
)

logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """Consciousness episode with semantic encoding"""

    episode_id: str
    episode_text: str
    embedding: List[float]
    timestamp: datetime
    phi_value: float
    qualia_signature: Dict[str, Any]
    metadata: Dict[str, Any]


class SemanticMemoryLayer:
    """Manages persistent semantic memory with Qdrant

    Stores consciousness episodes with semantic embeddings for:
    - Similarity-based retrieval
    - Temporal memory reconstruction
    - Consciousness state snapshots
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        qdrant: Optional[QdrantIntegration] = None,
    ):
        """Initialize semantic memory layer

        Args:
            model_name: SentenceTransformer model name
            qdrant: QdrantIntegration instance (default: singleton)
        """

        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. Install via: "
                "pip install sentence-transformers"
            )

        logger.info(f"Initializing SemanticMemoryLayer with model: {model_name}")

        # Load embedding model
        if SentenceTransformer is None:
            raise ImportError("SentenceTransformer not available")

        self.embedder = SentenceTransformer(model_name)  # type: ignore[assignment]
        self.embedding_dim = (
            self.embedder.get_sentence_embedding_dimension()  # type: ignore[attr-defined]
        )

        # Qdrant client - use provided instance or create new one with correct vector_size
        if qdrant is not None:
            self.qdrant = qdrant
        else:
            from src.integrations.qdrant_integration import QdrantIntegration

            self.qdrant = QdrantIntegration(
                collection_name="omnimind_consciousness",
                vector_size=self.embedding_dim,  # type: ignore[arg-type]
            )

        # Create collection if needed
        self.qdrant.create_collection()

        logger.info(f"✅ SemanticMemoryLayer initialized (dim={self.embedding_dim})")

    def store_episode(
        self,
        episode_text: str,
        episode_data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> str:
        """Store consciousness episode with semantic embedding

        Args:
            episode_text: Text description of episode
            episode_data: Episode metadata (phi_value, qualia_signature, etc)
            timestamp: Datetime (default: now)

        Returns:
            str: Episode ID
        """

        if timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Generate unique ID (as integer for Qdrant compatibility)
        episode_id_str = str(uuid.uuid4())
        episode_id = hash(episode_id_str) & 0x7FFFFFFFFFFFFFFF  # Convert to positive 64-bit int

        # Generate embedding
        try:
            embedding = self.embedder.encode(episode_text)
            if hasattr(embedding, "tolist"):
                embedding = embedding.tolist()  # type: ignore[attr-defined,assignment]
            else:
                embedding = list(embedding)  # type: ignore[assignment]
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            embedding = [0.0] * (self.embedding_dim or 384)  # type: ignore[operator,assignment]

        # Prepare payload com tríade completa (Φ, Ψ, σ)
        payload = {
            "episode_id_str": episode_id_str,
            "episode_text": episode_text,
            "timestamp": timestamp.isoformat(),
            "phi_value": float(episode_data.get("phi_value", 0.0)),
            "psi_value": float(episode_data.get("psi_value", 0.0)),  # NOVO: Ψ_produtor
            "sigma_value": float(episode_data.get("sigma_value", 0.0)),  # NOVO: σ_sinthome
            "qualia_signature": str(episode_data.get("qualia_signature", {})),
            **{
                k: v
                for k, v in episode_data.items()
                if k not in ["phi_value", "psi_value", "sigma_value", "qualia_signature"]
            },
        }

        # Create Qdrant point
        point = QdrantPoint(id=episode_id, vector=embedding, payload=payload)  # type: ignore

        # Insert
        success = self.qdrant.upsert_points([point])

        if success:
            logger.info(f"✅ Episode stored: {episode_id_str}")
            return episode_id_str

        logger.error("❌ Failed to store episode")
        return ""

    def retrieve_similar(
        self,
        query_text: str,
        top_k: int = 5,
        threshold: float = 0.5,
    ) -> List[Dict]:
        """Retrieve similar episodes by semantic similarity

        Args:
            query_text: Query text
            top_k: Number of results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of similar episodes with scores
        """

        # Generate query embedding
        query_embedding = self.embedder.encode(query_text)
        if hasattr(query_embedding, "tolist"):
            query_embedding = query_embedding.tolist()  # type: ignore[attr-defined,assignment]
        else:
            query_embedding = list(query_embedding)  # type: ignore[assignment]
        query_vector = cast(List[float], query_embedding)

        # Search in Qdrant
        results = self.qdrant.search(
            query_vector=query_vector, top_k=top_k, threshold=threshold
        )  # type: ignore[arg-type]

        logger.info(f"✅ {len(results)} similar episodes found")
        return results

    def get_episode_by_id(self, episode_id: str) -> Optional[Dict]:
        """Retrieve specific episode by ID

        Args:
            episode_id: Episode identifier

        Returns:
            Episode data or None if not found
        """

        try:
            # Qdrant doesn't have direct get by ID, use scroll
            points, _ = self.qdrant.client.scroll(
                collection_name="omnimind_consciousness", limit=10000
            )

            for point in points:
                if str(point.id) == episode_id and hasattr(point, "payload") and point.payload:
                    return {"id": point.id, "payload": point.payload}

            logger.warning(f"Episode not found: {episode_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Error retrieving episode: {e}")
            return None

    def list_episodes_by_time(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """List episodes within time range

        Args:
            start_time: Start datetime
            end_time: End datetime

        Returns:
            List of episodes in time range
        """

        try:
            points, _ = self.qdrant.client.scroll(
                collection_name="omnimind_consciousness", limit=10000
            )

            filtered = [
                {"id": point.id, "payload": point.payload}
                for point in points
                if (
                    hasattr(point, "payload")
                    and point.payload
                    and start_time.isoformat()
                    <= point.payload.get("timestamp", "")
                    <= end_time.isoformat()
                )
            ]

            logger.info(f"✅ {len(filtered)} episodes in time range")
            return filtered

        except Exception as e:
            logger.error(f"❌ Error listing episodes: {e}")
            return []

    def search_by_phi_range(self, min_phi: float, max_phi: float, top_k: int = 10) -> List[Dict]:
        """Search episodes by Phi value range

        Args:
            min_phi: Minimum phi value
            max_phi: Maximum phi value
            top_k: Number of results

        Returns:
            Episodes within phi range
        """

        try:
            points, _ = self.qdrant.client.scroll(
                collection_name="omnimind_consciousness", limit=10000
            )

            filtered = [
                {"id": point.id, "payload": point.payload}
                for point in points
                if (
                    hasattr(point, "payload")
                    and point.payload
                    and min_phi <= float(point.payload.get("phi_value", 0.0)) <= max_phi
                )
            ]

            # Sort by phi value descending
            filtered.sort(
                key=lambda x: (
                    float(x["payload"].get("phi_value", 0.0))
                    if isinstance(x["payload"], dict)
                    else 0.0
                ),  # type: ignore[union-attr]
                reverse=True,
            )

            logger.info(f"✅ {len(filtered[:top_k])} episodes in phi range")
            return filtered[:top_k]

        except Exception as e:
            logger.error(f"❌ Error searching by phi: {e}")
            return []

    def search_by_triad_range(
        self,
        min_phi: float = 0.0,
        max_phi: float = 1.0,
        min_psi: float = 0.0,
        max_psi: float = 1.0,
        min_sigma: float = 0.0,
        max_sigma: float = 1.0,
        top_k: int = 10,
    ) -> List[Dict]:
        """Search episodes by consciousness triad range (Φ, Ψ, σ)

        Args:
            min_phi: Minimum phi value
            max_phi: Maximum phi value
            min_psi: Minimum psi value
            max_psi: Maximum psi value
            min_sigma: Minimum sigma value
            max_sigma: Maximum sigma value
            top_k: Number of results

        Returns:
            Episodes within triad ranges
        """
        try:
            points, _ = self.qdrant.client.scroll(
                collection_name="omnimind_consciousness", limit=10000
            )

            filtered = [
                {"id": point.id, "payload": point.payload}
                for point in points
                if (
                    hasattr(point, "payload")
                    and point.payload
                    and min_phi <= float(point.payload.get("phi_value", 0.0)) <= max_phi
                    and min_psi <= float(point.payload.get("psi_value", 0.0)) <= max_psi
                    and min_sigma <= float(point.payload.get("sigma_value", 0.0)) <= max_sigma
                )
            ]

            # Sort by magnitude of triad (norma euclidiana)
            filtered.sort(
                key=lambda x: (
                    (
                        float(x["payload"].get("phi_value", 0.0)) ** 2
                        + float(x["payload"].get("psi_value", 0.0)) ** 2
                        + float(x["payload"].get("sigma_value", 0.0)) ** 2
                    )
                    ** 0.5
                    if isinstance(x["payload"], dict)
                    else 0.0
                ),
                reverse=True,
            )

            logger.info(f"✅ {len(filtered[:top_k])} episodes in triad range")
            return filtered[:top_k]

        except Exception as e:
            logger.error(f"❌ Error searching by triad: {e}")
            return []

    def get_stats(self) -> Optional[Dict]:
        """Get semantic memory statistics

        Returns:
            Statistics dictionary or None
        """

        try:
            info = self.qdrant.get_collection_info()
            if info and isinstance(info, dict):
                return {
                    "total_episodes": info.get("points_count", 0),
                    "embedding_dim": self.embedding_dim,
                    "model": "all-MiniLM-L6-v2",
                }
            return None

        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return None


# Singleton instance
_semantic_memory_instance: Optional[SemanticMemoryLayer] = None


def get_semantic_memory() -> SemanticMemoryLayer:
    """Get singleton instance of SemanticMemoryLayer

    Returns:
        SemanticMemoryLayer: Singleton instance
    """

    global _semantic_memory_instance
    if _semantic_memory_instance is None:
        _semantic_memory_instance = SemanticMemoryLayer()
    return _semantic_memory_instance

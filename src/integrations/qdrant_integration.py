"""Qdrant Vector Database Integration - Phase 24

Provides abstraction layer for Qdrant (local + cloud fallback).
Handles collection management, CRUD operations, and semantic search.

Architecture:
- QdrantPoint: Individual data point with vector + metadata
- QdrantIntegration: Main integration class (singleton pattern)
- Health checks and error recovery

Author: OmniMind Development
License: MIT
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
from uuid import UUID

try:
    from qdrant_client import QdrantClient  # type: ignore[import-untyped]
    from qdrant_client.models import (  # type: ignore[import-untyped]
        Distance,
        PointStruct,
        VectorParams,
    )

    QDRANT_AVAILABLE = True
except ImportError:
    if TYPE_CHECKING:
        from qdrant_client import QdrantClient  # type: ignore[import-untyped]
        from qdrant_client.models import (  # type: ignore[import-untyped]
            Distance,
            PointStruct,
            VectorParams,
        )
    else:
        QdrantClient = None  # type: ignore[assignment]
        Distance = None  # type: ignore[assignment]
        PointStruct = None  # type: ignore[assignment]
        VectorParams = None  # type: ignore[assignment]

    QDRANT_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class QdrantPoint:
    """Individual point in Qdrant vector space"""

    id: Union[str, int]
    vector: List[float]
    payload: Dict[str, Any]


class QdrantIntegration:
    """Integration with Qdrant Vector Database (local + cloud)"""

    def __init__(
        self,
        collection_name: str = "omnimind_consciousness",
        vector_size: int = 384,
        host: str = "localhost",
        port: int = 6333,
    ):
        """Initialize Qdrant integration

        Args:
            collection_name: Name of collection
            vector_size: Dimension of vectors (384 for all-MiniLM-L6-v2)
            host: Qdrant host
            port: Qdrant port
        """

        if not QDRANT_AVAILABLE:
            raise ImportError("qdrant-client not installed. Install via: pip install qdrant-client")

        self.collection_name = collection_name
        self.vector_size = vector_size

        try:
            self.client = QdrantClient(host=host, port=port)
            logger.info(f"✅ Qdrant connected: {host}:{port}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            raise

    def create_collection(self, recreate: bool = False) -> bool:
        """Create collection if it doesn't exist

        Args:
            recreate: If True, delete and recreate collection

        Returns:
            bool: Success status
        """

        try:
            # Check if exists
            collections = self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)

            if exists:
                if recreate:
                    logger.info(f"Deleting collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"✅ Collection already exists: {self.collection_name}")
                    return True

            # Create new
            logger.info(f"Creating collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )
            logger.info("✅ Collection created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating collection: {e}")
            return False

    def upsert_points(self, points: List[QdrantPoint]) -> bool:
        """Insert or update points

        Args:
            points: List of QdrantPoint objects

        Returns:
            bool: Success status
        """

        try:
            qdrant_points = [
                PointStruct(id=p.id, vector=p.vector, payload=p.payload) for p in points
            ]

            self.client.upsert(
                collection_name=self.collection_name, points=qdrant_points, wait=True
            )

            logger.info(f"✅ {len(points)} points inserted")
            return True

        except Exception as e:
            logger.error(f"❌ Error upserting points: {e}")
            return False

    def search(
        self, query_vector: List[float], top_k: int = 5, threshold: float = 0.5
    ) -> List[Dict]:
        """Search for similar vectors

        Args:
            query_vector: Query vector
            top_k: Number of results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of results with id, score, payload
        """

        try:
            # Prefer newer query_points API, fallback to older search/search_points
            query_points = getattr(self.client, "query_points", None)
            if callable(query_points):
                results = query_points(  # type: ignore[attr-defined]
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k,
                    query_filter=None,
                    score_threshold=threshold,
                    with_payload=True,
                )
                hits = results.points if hasattr(results, "points") else results
            else:
                search_fn = getattr(self.client, "search", None)
                if callable(search_fn):
                    hits = search_fn(  # type: ignore[attr-defined]
                        collection_name=self.collection_name,
                        query_vector=query_vector,
                        limit=top_k,
                        query_filter=None,
                        score_threshold=threshold,
                    )
                else:
                    search_points = getattr(self.client, "search_points", None)
                    if not callable(search_points):
                        raise AttributeError("QdrantClient query/search APIs indisponíveis")

                    hits = search_points(  # type: ignore[attr-defined]
                        collection_name=self.collection_name,
                        vector=query_vector,
                        limit=top_k,
                        filter=None,
                        score_threshold=threshold,
                        with_payload=True,
                    )

            return [
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": getattr(hit, "payload", {}),
                }
                for hit in hits
            ]

        except Exception as e:
            logger.error(f"❌ Error searching: {e}")
            return []

    def delete_points(self, point_ids: List[Union[str, int, UUID]]) -> bool:
        """Delete points by ID

        Args:
            point_ids: List of point IDs

        Returns:
            bool: Success status
        """

        try:
            self.client.delete(  # type: ignore[arg-type]
                collection_name=self.collection_name, points_selector=point_ids
            )

            logger.info(f"✅ {len(point_ids)} points deleted")
            return True

        except Exception as e:
            logger.error(f"❌ Error deleting points: {e}")
            return False

    def get_collection_info(self) -> Optional[Dict]:
        """Get collection statistics

        Returns:
            Collection info or None if error
        """

        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "points_count": info.points_count,
                "config": str(info.config),
            }

        except Exception as e:
            logger.error(f"❌ Error getting collection info: {e}")
            return None

    def health_check(self) -> bool:
        """Check Qdrant health

        Returns:
            bool: True if healthy
        """

        try:
            _ = self.client.get_collections()
            logger.info("✅ Qdrant health check OK")
            return True

        except Exception as e:
            logger.error(f"❌ Qdrant health check failed: {e}")
            return False


# Singleton instance
_qdrant_instance: Optional[QdrantIntegration] = None


def get_qdrant() -> QdrantIntegration:
    """Get singleton instance of QdrantIntegration

    Returns:
        QdrantIntegration: Singleton instance
    """

    global _qdrant_instance
    if _qdrant_instance is None:
        _qdrant_instance = QdrantIntegration()
    return _qdrant_instance

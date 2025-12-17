from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, cast

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from .mcp_client import MCPClient, MCPClientError

logger = logging.getLogger(__name__)


class QdrantAdapterError(Exception):
    pass


@dataclass(frozen=True)
class QdrantConfig:
    url: str
    api_key: Optional[str] = None
    collection: Optional[str] = None
    vector_size: Optional[int] = None

    @classmethod
    def from_env(cls) -> Optional["QdrantConfig"]:
        # Try cloud configuration first
        cloud_url = os.environ.get("OMNIMIND_QDRANT_CLOUD_URL")
        if cloud_url:
            return cls(
                url=cloud_url,
                api_key=os.environ.get("OMNIMIND_QDRANT_API_KEY"),
                collection=os.environ.get("OMNIMIND_QDRANT_COLLECTION"),
                vector_size=(
                    int(os.environ["OMNIMIND_QDRANT_VECTOR_SIZE"])
                    if os.environ.get("OMNIMIND_QDRANT_VECTOR_SIZE")
                    else None
                ),
            )

        # Fallback to local configuration
        url = os.environ.get("OMNIMIND_QDRANT_URL")
        if not url:
            return None
        return cls(
            url=url,
            api_key=os.environ.get("OMNIMIND_QDRANT_API_KEY"),
            collection=os.environ.get("OMNIMIND_QDRANT_COLLECTION"),
            vector_size=(
                int(os.environ["OMNIMIND_QDRANT_VECTOR_SIZE"])
                if os.environ.get("OMNIMIND_QDRANT_VECTOR_SIZE")
                else None
            ),
        )

    @classmethod
    def from_text(cls, text: str) -> Optional["QdrantConfig"]:
        url_match = re.search(r"url\s*=\s*\"([^\"]+)\"", text)
        api_match = re.search(r"api_key\s*=\s*\"([^\"]+)\"", text)
        if not url_match:
            return None
        return cls(url=url_match.group(1), api_key=api_match.group(1) if api_match else None)

    @classmethod
    def load(cls, mcp_client: Optional[MCPClient] = None) -> Optional["QdrantConfig"]:
        config = cls.from_env()
        if config:
            return config
        if mcp_client is not None and hasattr(mcp_client, "read_env"):
            try:
                data = mcp_client.read_env(
                    [
                        "OMNIMIND_QDRANT_URL",
                        "OMNIMIND_QDRANT_API_KEY",
                        "OMNIMIND_QDRANT_COLLECTION",
                        "OMNIMIND_QDRANT_VECTOR_SIZE",
                    ]
                )
            except MCPClientError as exc:
                logger.debug("Unable to read Qdrant env via MCP: %s", exc)
            else:
                env_map = data or {}
                url = env_map.get("OMNIMIND_QDRANT_URL")
                if url:
                    vector_size_value = env_map.get("OMNIMIND_QDRANT_VECTOR_SIZE")
                    vector_size = int(vector_size_value) if vector_size_value else None
                    return cls(
                        url=url,
                        api_key=env_map.get("OMNIMIND_QDRANT_API_KEY"),
                        collection=env_map.get("OMNIMIND_QDRANT_COLLECTION"),
                        vector_size=vector_size,
                    )
        logger.warning("Qdrant configuration missing; set OMNIMIND_QDRANT_* environment variables")
        return None


class QdrantAdapter:
    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client = QdrantClient(url=config.url, api_key=config.api_key)

    def ensure_collection(
        self,
        collection: str,
        vector_size: int,
        distance: qdrant_models.Distance = qdrant_models.Distance.COSINE,
    ) -> Dict[str, Any]:
        logger.debug("Ensuring collection %s exists with vector_size %s", collection, vector_size)
        try:
            response = self.client.get_collection(collection_name=collection)
            return response.dict()  # type: ignore[no-any-return]
        except Exception:
            logger.info("Creating missing collection %s", collection)
            self.client.recreate_collection(
                collection_name=collection,
                vectors_config=qdrant_models.VectorParams(size=vector_size, distance=distance),
            )
            return {"collection": collection, "status": "created"}

    def upsert_vectors(
        self,
        collection: str,
        vectors: Iterable[List[float]],
        ids: Iterable[int],
        payloads: Optional[Iterable[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        ids_list = list(ids)
        vectors_list = list(vectors)
        if len(ids_list) != len(vectors_list):
            raise QdrantAdapterError("ids and vectors length mismatch")
        payloads_list = list(payloads) if payloads is not None else [{} for _ in ids_list]
        if len(payloads_list) < len(ids_list):
            payloads_list += [{} for _ in range(len(ids_list) - len(payloads_list))]
        points = []
        for idx, vector, payload in zip(ids_list, vectors_list, payloads_list):
            points.append(qdrant_models.PointStruct(id=int(idx), vector=vector, payload=payload))
        result = self.client.upsert(collection_name=collection, points=points)
        logger.info("Upserted %s vectors into %s", len(points), collection)
        return result if isinstance(result, dict) else {"status": "upserted"}

    def search_vectors(
        self,
        collection: str,
        query_vector: List[float],
        top: int = 5,
        with_payload: bool = True,
    ) -> List[Dict[str, Any]]:
        logger.debug("Searching vectors in %s (top=%s)", collection, top)
        search_fn = getattr(self.client, "search", None)
        if search_fn is None:
            raise QdrantAdapterError("Qdrant client missing search API")
        response = cast(
            Sequence[Any],
            search_fn(
                collection_name=collection,
                query_vector=query_vector,
                limit=top,
                with_payload=with_payload,
                with_vectors=False,
            ),
        )
        return [hit.dict() for hit in response]

    def list_collections(self) -> List[str]:
        collections = self.client.get_collections()
        names = [info.name for info in collections.collections] if collections.collections else []
        logger.debug("Available QB collections: %s", names)
        return names

    def delete_vectors(self, collection: str, ids: Iterable[int]) -> Dict[str, Any]:
        ids_list = list(ids)
        logger.debug("Deleting %s vectors from %s", len(ids_list), collection)
        delete_fn = getattr(self.client, "delete", None)
        if delete_fn is None:
            raise QdrantAdapterError("Qdrant client missing delete API")
        result = delete_fn(collection_name=collection, points_selector=ids_list)
        return result.dict() if hasattr(result, "dict") else {}

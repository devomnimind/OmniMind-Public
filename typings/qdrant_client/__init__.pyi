"""Type stubs for qdrant_client."""

from typing import Any, Optional, List, Dict

class QdrantClient:
    """Qdrant vector database client."""

    def __init__(
        self,
        location: Optional[str] = None,
        url: Optional[str] = None,
        port: Optional[int] = None,
        grpc_port: Optional[int] = None,
        prefer_grpc: bool = False,
        https: Optional[bool] = None,
        api_key: Optional[str] = None,
        prefix: Optional[str] = None,
        timeout: Optional[int] = None,
        host: Optional[str] = None,
        path: Optional[str] = None,
        **kwargs: Any
    ) -> None: ...
    def recreate_collection(
        self, collection_name: str, vectors_config: Any, **kwargs: Any
    ) -> Any: ...
    def create_collection(
        self, collection_name: str, vectors_config: Any, **kwargs: Any
    ) -> Any: ...
    def get_collections(self, **kwargs: Any) -> Any: ...
    def upsert(self, collection_name: str, points: Any, **kwargs: Any) -> Any: ...
    def search(
        self,
        collection_name: str,
        query_vector: Any,
        limit: int = 10,
        query_filter: Optional[Any] = None,
        **kwargs: Any
    ) -> Any: ...
    def query_points(
        self,
        collection_name: str,
        query: Any,
        limit: int = 10,
        query_filter: Optional[Any] = None,
        **kwargs: Any
    ) -> Any: ...
    def retrieve(self, collection_name: str, ids: List[Any], **kwargs: Any) -> Any: ...
    def scroll(
        self,
        collection_name: str,
        scroll_filter: Optional[Any] = None,
        limit: Optional[int] = None,
        **kwargs: Any
    ) -> Any: ...
    def get_collection(self, collection_name: str, **kwargs: Any) -> Any: ...
    def collection_exists(self, collection_name: str, **kwargs: Any) -> bool: ...
    def delete(
        self, collection_name: str, points_selector: Any, **kwargs: Any
    ) -> Any: ...

__all__ = ["QdrantClient"]

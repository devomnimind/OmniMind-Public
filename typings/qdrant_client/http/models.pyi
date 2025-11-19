"""Type stubs for qdrant_client.http.models."""

from typing import Any, Optional, List, Dict, Union
from enum import Enum

class Distance(Enum):
    """Distance metrics for vector similarity."""

    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"

class VectorParams:
    """Vector configuration parameters."""

    size: int
    distance: Distance
    def __init__(self, size: int, distance: Distance) -> None: ...

class PointStruct:
    """Point structure for storing in Qdrant."""

    id: Union[int, str]
    vector: List[float]
    payload: Optional[Dict[str, Any]]
    def __init__(
        self,
        id: Union[int, str],
        vector: List[float],
        payload: Optional[Dict[str, Any]] = None,
    ) -> None: ...

class Filter:
    """Filter for querying points."""

    must: Optional[List[Any]]
    should: Optional[List[Any]]
    must_not: Optional[List[Any]]
    def __init__(
        self,
        must: Optional[List[Any]] = None,
        should: Optional[List[Any]] = None,
        must_not: Optional[List[Any]] = None,
    ) -> None: ...

class FieldCondition:
    """Field condition for filtering."""

    key: str
    match: Optional[Any]
    range: Optional[Range]
    def __init__(
        self, key: str, match: Optional[Any] = None, range: Optional[Range] = None
    ) -> None: ...

class MatchValue:
    """Match value for field conditions."""

    value: Any
    def __init__(self, value: Any) -> None: ...

class Range:
    """Range for field conditions."""

    gte: Optional[float]
    lte: Optional[float]
    gt: Optional[float]
    lt: Optional[float]
    def __init__(
        self,
        gte: Optional[float] = None,
        lte: Optional[float] = None,
        gt: Optional[float] = None,
        lt: Optional[float] = None,
    ) -> None: ...

class ScoredPoint:
    """Scored point from search results."""

    id: Union[int, str]
    score: float
    payload: Optional[Dict[str, Any]]
    vector: Optional[List[float]]

ExtendedPointId = Union[int, str]

__all__ = [
    "Distance",
    "VectorParams",
    "PointStruct",
    "Filter",
    "FieldCondition",
    "MatchValue",
    "Range",
    "ScoredPoint",
    "ExtendedPointId",
]

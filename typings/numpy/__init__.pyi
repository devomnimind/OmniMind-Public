"""Minimal type stubs for numpy (just what we need)."""

from typing import Any, TypeVar, Generic, Union, List

_DType = TypeVar("_DType")

class ndarray(Generic[_DType]):
    """NumPy array."""

    shape: tuple[int, ...]
    dtype: Any
    def __getitem__(self, key: Any) -> Any: ...
    def __setitem__(self, key: Any, value: Any) -> None: ...
    def tolist(self) -> List[Any]: ...

__all__ = ["ndarray"]

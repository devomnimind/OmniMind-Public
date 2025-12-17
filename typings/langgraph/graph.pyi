"""Type stubs for langgraph.graph."""

from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

END: str

class StateGraph(Generic[T]):
    """LangGraph state graph."""

    def __init__(self, state_schema: type[T]) -> None: ...
    def add_node(self, name: str, func: Callable[[T], T]) -> None: ...
    def add_edge(self, source: str, target: str) -> None: ...
    def add_conditional_edges(
        self,
        source: str,
        path: Callable[[T], str],
        path_map: Optional[Dict[str, str]] = None,
    ) -> None: ...
    def set_entry_point(self, node: str) -> None: ...
    def compile(self) -> CompiledStateGraph[T]: ...

class CompiledStateGraph(Generic[T]):
    """Compiled state graph that can be invoked."""

    def invoke(self, state: T, config: Optional[Dict[str, Any]] = None) -> T: ...

__all__ = ["StateGraph", "CompiledStateGraph", "END"]

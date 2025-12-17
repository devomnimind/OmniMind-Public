"""
Stub file for qiskit_ibm_runtime module
Provides type hints for IBM Quantum Runtime components
"""

from typing import Any, Protocol


class Sampler(Protocol):
    """Protocol for IBM Runtime sampler objects."""
    
    def __init__(self, channel: str = "ibm_quantum", **kwargs: Any) -> None:
        ...
    
    def run(self, circuits: Any, **kwargs: Any) -> Any:
        ...


class Backend(Protocol):
    """Protocol for IBM Quantum backend objects."""
    
    def is_available(self) -> bool:
        ...
    
    def get_info(self) -> Any:
        ...

"""
Stub file for dimod module
Provides type hints for D-Wave dimod binary quadratic models
"""

from typing import Any, Dict, Protocol


class BinaryQuadraticModel(Protocol):
    """Protocol for dimod BQM objects."""
    
    @staticmethod
    def from_qubo(Q: Dict[tuple[Any, Any], float]) -> Any:
        """Create BQM from QUBO dictionary."""
        ...


class SampleSet(Protocol):
    """Protocol for dimod sample set objects."""
    
    @property
    def first(self) -> Any:
        """Get the first (best) sample."""
        ...

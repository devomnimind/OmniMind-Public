"""
Stub file for neal module
Provides type hints for D-Wave Neal simulated annealing
"""

from typing import Any, Protocol


class Sampler(Protocol):
    """Protocol for Neal sampler objects."""
    
    def sample(self, bqm: Any, **kwargs: Any) -> Any:
        ...


class SimulatedAnnealingSampler:
    """Neal simulated annealing sampler."""
    
    def sample(self, bqm: Any, num_reads: int = 1, **kwargs: Any) -> Any:
        """Sample using simulated annealing."""
        ...
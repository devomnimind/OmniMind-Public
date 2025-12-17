"""
Stub file for dwave.system module
Provides type hints for D-Wave quantum computing components
"""

from typing import Any, Dict, Optional, Protocol


class Sampler(Protocol):
    """Protocol for D-Wave sampler objects."""
    
    def sample(self, bqm: Any, **kwargs: Any) -> Any:
        ...


class DWaveSampler:
    """D-Wave quantum annealer sampler."""
    
    def __init__(
        self,
        token: Optional[str] = None,
        solver: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        ...
    
    def sample(self, bqm: Any, num_reads: int = 1, **kwargs: Any) -> Any:
        """Sample from the provided BQM."""
        ...


class EmbeddingComposite:
    """Embedding composite for D-Wave samplers."""
    
    def __init__(self, sampler: Sampler, **kwargs: Any) -> None:
        ...
    
    def sample(self, bqm: Any, **kwargs: Any) -> Any:
        """Sample using embedding."""
        ...
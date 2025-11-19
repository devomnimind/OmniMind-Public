"""Backend middleware modules."""

from web.backend.middleware.compression import (
    CompressionMiddleware,
    get_compression_stats
)

__all__ = [
    "CompressionMiddleware",
    "get_compression_stats"
]

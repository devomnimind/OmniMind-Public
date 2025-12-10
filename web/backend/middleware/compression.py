"""
Advanced compression middleware for FastAPI.

This module provides production-grade HTTP compression with:
- Brotli compression (superior to gzip)
- Gzip fallback for older clients
- Content-type aware compression
- Configurable quality levels
- Minimum size thresholds
- Streaming support

Example:
    >>> from fastapi import FastAPI
    >>> from web.backend.middleware.compression import CompressionMiddleware
    >>>
    >>> app = FastAPI()
    >>> app.add_middleware(
    ...     CompressionMiddleware,
    ...     minimum_size=500,
    ...     brotli_quality=4
    ... )
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Optional, Set
import logging

# Compression libraries (optional for local-first)
try:
    import brotli

    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False

import gzip

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Advanced HTTP compression middleware.

    Supports Brotli (preferred) and Gzip compression with intelligent
    content-type detection and configurable parameters.

    Attributes:
        minimum_size: Minimum response size to compress (bytes)
        brotli_quality: Brotli quality 0-11 (4=fast, good compression)
        gzip_level: Gzip compression level 1-9 (6=default)
        compressible_types: Set of MIME types to compress

    Example:
        >>> app.add_middleware(
        ...     CompressionMiddleware,
        ...     minimum_size=1000,
        ...     brotli_quality=6,
        ...     gzip_level=9
        ... )
    """

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 500,
        brotli_quality: int = 4,
        gzip_level: int = 6,
        compressible_types: Optional[Set[str]] = None,
    ):
        """
        Initialize compression middleware.

        Args:
            app: FastAPI application instance
            minimum_size: Minimum bytes to compress (default: 500)
            brotli_quality: Brotli quality 0-11 (default: 4)
            gzip_level: Gzip level 1-9 (default: 6)
            compressible_types: MIME types to compress (optional)
        """
        super().__init__(app)
        self.minimum_size = minimum_size
        self.brotli_quality = brotli_quality
        self.gzip_level = gzip_level

        # Default compressible types
        self.compressible_types = compressible_types or {
            "text/html",
            "text/css",
            "text/javascript",
            "text/plain",
            "text/xml",
            "application/javascript",
            "application/json",
            "application/xml",
            "application/x-javascript",
            "image/svg+xml",
            "application/vnd.api+json",
        }

        if not BROTLI_AVAILABLE:
            logger.warning(
                "Brotli not available. Install with: pip install brotli. " "Using gzip only."
            )

    async def dispatch(self, request: Request, call_next):
        """
        Process request with compression.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response (possibly compressed)
        """
        response = await call_next(request)

        # Skip if already compressed
        if "content-encoding" in response.headers:
            return response

        # Skip if too small
        content_length = response.headers.get("content-length", "0")
        try:
            if int(content_length) < self.minimum_size:
                return response
        except (ValueError, TypeError):
            # If content-length is invalid, try to compress anyway
            pass

        # Check content type
        content_type = response.headers.get("content-type", "")
        content_type_base = content_type.split(";")[0].strip()

        if content_type_base not in self.compressible_types:
            return response

        # Get accept-encoding header
        accept_encoding = request.headers.get("accept-encoding", "")

        # Try Brotli first (better compression)
        if BROTLI_AVAILABLE and "br" in accept_encoding:
            return await self._compress_brotli(response)

        # Fallback to gzip
        if "gzip" in accept_encoding:
            return await self._compress_gzip(response)

        return response

    async def _compress_brotli(self, response: Response) -> Response:
        """
        Compress response with Brotli.

        Args:
            response: Original response

        Returns:
            Brotli-compressed response
        """
        try:
            # Get response body
            body = b""
            # Check if response has body attribute (simple response)
            if hasattr(response, "body"):
                body = response.body  # type: ignore[attr-defined]
            # Otherwise, iterate over body iterator if available
            elif hasattr(response, "body_iterator"):
                async for chunk in response.body_iterator:  # type: ignore[attr-defined]
                    body += chunk
            else:
                # Try to get body from response directly
                body = getattr(response, "body", b"")

            # Skip if empty
            if not body:
                return response

            # Compress with Brotli
            compressed = brotli.compress(body, quality=self.brotli_quality, mode=brotli.MODE_TEXT)

            # Update response
            response.headers["content-encoding"] = "br"
            response.headers["content-length"] = str(len(compressed))
            response.headers["vary"] = "Accept-Encoding"

            # Create new response with compressed body
            from starlette.responses import Response as StarletteResponse

            return StarletteResponse(
                content=compressed,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as e:
            logger.error(f"Brotli compression failed: {e}")
            return response

    async def _compress_gzip(self, response: Response) -> Response:
        """
        Compress response with gzip.

        Args:
            response: Original response

        Returns:
            Gzip-compressed response
        """
        try:
            # Get response body
            body = b""
            # Check if response has body attribute (simple response)
            if hasattr(response, "body"):
                body = response.body  # type: ignore[attr-defined]
            # Otherwise, iterate over body iterator if available
            elif hasattr(response, "body_iterator"):
                async for chunk in response.body_iterator:  # type: ignore[attr-defined]
                    body += chunk
            else:
                # Try to get body from response directly
                body = getattr(response, "body", b"")

            # Skip if empty
            if not body:
                return response

            # Compress with gzip
            compressed = gzip.compress(body, compresslevel=self.gzip_level)

            # Update response
            response.headers["content-encoding"] = "gzip"
            response.headers["content-length"] = str(len(compressed))
            response.headers["vary"] = "Accept-Encoding"

            # Create new response with compressed body
            from starlette.responses import Response as StarletteResponse

            return StarletteResponse(
                content=compressed,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        except Exception as e:
            logger.error(f"Gzip compression failed: {e}")
            return response


def get_compression_stats(original_size: int, compressed_size: int) -> dict:
    """
    Calculate compression statistics.

    Args:
        original_size: Original size in bytes
        compressed_size: Compressed size in bytes

    Returns:
        Dict with compression ratio, savings, etc.

    Example:
        >>> stats = get_compression_stats(10000, 3000)
        >>> print(f"Saved {stats['savings_percent']:.1f}%")
        Saved 70.0%
    """
    if original_size == 0:
        return {
            "original_size": 0,
            "compressed_size": 0,
            "compression_ratio": 1.0,
            "savings_bytes": 0,
            "savings_percent": 0.0,
        }

    ratio = compressed_size / original_size
    savings = original_size - compressed_size
    savings_pct = (savings / original_size) * 100

    return {
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": ratio,
        "savings_bytes": savings,
        "savings_percent": savings_pct,
    }

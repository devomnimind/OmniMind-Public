"""
Auto-Concurrency Detection Middleware
=====================================

Detects when OmniMind sistema detecta um self-request (quando testa a si mesmo)
e ativa automaticamente o VALIDATION_MODE para evitar contention.

Fluxo:
1. Request chega em localhost:8000 de localhost:YYYY
2. Middleware verifica: é um self-request? (localhost → localhost)
3. Se sim: Set OMNIMIND_VALIDATION_MODE=true + injetar header X-Internal
4. Service manager detecta e pausa serviços auxiliares
5. Após response: Restaurar estado normal

Filosofia: "Sistema não compete consigo mesmo"
"""

import logging
import os
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AutoConcurrencyDetectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware que detecta self-requests e ativa VALIDATION_MODE automaticamente.
    """

    def __init__(self, app, validation_mode_manager=None):
        """Initialize middleware."""
        super().__init__(app)
        self.validation_mode_manager = validation_mode_manager
        self.internal_request_counter = 0
        self.lock = __import__("asyncio").Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and detect self-requests.

        Detects:
        1. client_host == "127.0.0.1" or "localhost"
        2. X-Internal header (internal routing)
        3. X-From-Test header (test validation)
        4. Request path contains validation endpoints
        """
        # 1. Extract client info
        client_host = request.client.host if request.client else "unknown"
        is_localhost = client_host in ("127.0.0.1", "localhost", "::1")

        # 2. Check headers for internal markers
        x_internal = request.headers.get("X-Internal", "").lower() == "true"
        x_from_test = request.headers.get("X-From-Test", "").lower() == "true"
        x_validation = request.headers.get("X-Validation", "").lower() == "true"

        # 3. Check if path is validation endpoint
        validation_paths = [
            "/api/omnimind/metrics/consciousness",
            "/api/omnimind/metrics/real",
            "/api/omnimind/validate",
            "/api/v1/health",
            "/daemon/status",
        ]
        is_validation_endpoint = any(request.url.path.startswith(path) for path in validation_paths)

        # 4. Determine if this is a self-request
        is_self_request = is_localhost and (
            x_internal or x_from_test or x_validation or is_validation_endpoint
        )

        if is_self_request:
            await self._handle_self_request(request, client_host)

        try:
            # Forward request
            response = await call_next(request)

            # Add tracking headers to response
            if is_self_request:
                response.headers["X-Self-Request"] = "true"
                response.headers["X-Concurrency-Mode"] = "validation"

            return response

        finally:
            if is_self_request:
                await self._cleanup_self_request()

    async def _handle_self_request(self, request: Request, client_host: str) -> None:
        """Handle self-request by activating VALIDATION_MODE."""
        try:
            async with self.lock:
                # Check if already in validation mode
                already_validating = (
                    os.getenv("OMNIMIND_VALIDATION_MODE", "false").lower() == "true"
                )

                if not already_validating:
                    # Activate VALIDATION_MODE
                    os.environ["OMNIMIND_VALIDATION_MODE"] = "true"
                    self.internal_request_counter = 1

                    logger.warning(
                        "🔬 SELF-REQUEST DETECTED: Activating VALIDATION_MODE "
                        f"(client: {client_host}, path: {request.url.path})"
                    )

                    # Notify validation mode manager if available
                    if self.validation_mode_manager:
                        self.validation_mode_manager.enter_validation_mode()
                else:
                    # Already validating, increment counter
                    self.internal_request_counter += 1
                    logger.debug(
                        f"  └─ Nested self-request (depth={self.internal_request_counter})"
                    )

        except Exception as e:
            logger.error(f"Error activating validation mode: {e}")

    async def _cleanup_self_request(self) -> None:
        """Clean up after self-request completes."""
        try:
            async with self.lock:
                self.internal_request_counter -= 1

                # If no more internal requests, exit VALIDATION_MODE
                if self.internal_request_counter <= 0:
                    self.internal_request_counter = 0
                    os.environ["OMNIMIND_VALIDATION_MODE"] = "false"

                    logger.warning("✅ VALIDATION_MODE deactivated: Restoring normal services")

                    # Notify validation mode manager if available
                    if self.validation_mode_manager:
                        self.validation_mode_manager.exit_validation_mode()
                else:
                    logger.debug(
                        f"  └─ Still in nested requests (depth={self.internal_request_counter})"
                    )

        except Exception as e:
            logger.error(f"Error cleaning up validation mode: {e}")


def add_auto_concurrency_middleware(app, validation_mode_manager=None):
    """
    Add auto-concurrency detection middleware to FastAPI app.

    Args:
        app: FastAPI application
        validation_mode_manager: ValidationModeManager instance (optional)
    """
    app.add_middleware(
        AutoConcurrencyDetectionMiddleware,
        validation_mode_manager=validation_mode_manager,
    )
    logger.info("✅ Auto-Concurrency Detection Middleware added")


# For testing
if __name__ == "__main__":
    logger.info("Testing middleware...")
    # Simple test would go here

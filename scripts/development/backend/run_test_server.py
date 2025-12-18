#!/usr/bin/env python3
"""
Test server for E2E integration tests.
Uses mocked dependencies for isolated testing.
"""

import sys
from unittest.mock import MagicMock, patch

import uvicorn


def run_test_server(port: int = 4321, host: str = "127.0.0.1"):
    """Run test server with mocked dependencies."""

    # Mock external dependencies
    with patch("qdrant_client.QdrantClient") as mock_qdrant, patch("redis.Redis") as mock_redis:

        # Configure mocks
        mock_qdrant.return_value = MagicMock()
        mock_redis.return_value = MagicMock()

        # Import app AFTER mocking
        from src.api.main import app

        # Configure uvicorn
        config = uvicorn.Config(app, host=host, port=port, log_level="info", access_log=True)

        server = uvicorn.Server(config)
        print(f"🚀 Test server starting on http://{host}:{port}")
        server.run()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4321
    run_test_server(port)

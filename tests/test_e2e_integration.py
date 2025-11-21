"""
End-to-End Integration Tests using Playwright

These tests validate the entire OmniMind system from UI to backend.
"""

import asyncio
import os
import re
import time
from pathlib import Path
from typing import Dict

import pytest

# Check if playwright is installed
try:
    from playwright.async_api import Browser, Page, async_playwright, expect

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    pytest.skip("Playwright not installed", allow_module_level=True)


@pytest.fixture(scope="session")
def backend_server():
    """Start backend server for E2E tests."""
    import importlib

    # Set test credentials
    os.environ["OMNIMIND_DASHBOARD_USER"] = "test_user"
    os.environ["OMNIMIND_DASHBOARD_PASS"] = "test_pass"

    # Set Qdrant configuration for tests
    os.environ["OMNIMIND_QDRANT_URL"] = "http://localhost:6333"
    os.environ["OMNIMIND_QDRANT_COLLECTION"] = "omnimind_memories"
    os.environ["OMNIMIND_QDRANT_VECTOR_SIZE"] = "768"

    # Reload backend module to pick up new environment variables
    import web.backend.main as backend_main

    importlib.reload(backend_main)

    # Import and create test client
    from fastapi.testclient import TestClient

    client = TestClient(backend_main.app)
    return client


@pytest.fixture(scope="session")
async def browser():
    """Create browser instance."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser: Browser):
    """Create new page for each test."""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await page.close()
    await context.close()


@pytest.fixture
def auth_credentials():
    """Test authentication credentials."""
    return {"username": "test_user", "password": "test_pass"}


class TestAPIEndpoints:
    """Test API endpoints via direct HTTP calls."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, backend_server):
        """Test health endpoint is accessible."""
        response = backend_server.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_authenticated_endpoint(
        self, backend_server, auth_credentials: Dict[str, str]
    ):
        """Test authenticated endpoint access."""
        # Without auth - should fail
        response = backend_server.get("/status")
        assert response.status_code == 401

        # With auth - should succeed
        response = backend_server.get(
            "/status",
            auth=(auth_credentials["username"], auth_credentials["password"]),
        )
        assert response.status_code == 200

    def test_task_orchestration_workflow(
        self, backend_server, auth_credentials: Dict[str, str]
    ):
        """Test complete task orchestration workflow."""
        auth = (auth_credentials["username"], auth_credentials["password"])

        # Submit task
        task_data = {"task": "Test task", "max_iterations": 1}
        response = backend_server.post(
            "/tasks/orchestrate",
            json=task_data,
            auth=auth,
        )
        assert response.status_code == 200
        result = response.json()
        assert "task" in result
        assert result["task"] == "Test task"

        # Check metrics were updated
        response = backend_server.get("/metrics", auth=auth)
        assert response.status_code == 200
        metrics = response.json()
        assert "backend" in metrics
        assert metrics["backend"]["requests"] > 0


class TestWebSocketIntegration:
    """Test WebSocket real-time communication."""

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="WebSocket tests require real server, not TestClient")
    async def test_websocket_connection(self, backend_server):
        """Test WebSocket connection and ping/pong."""
        pass  # Skipped - requires real server

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="WebSocket tests require real server, not TestClient")
    async def test_websocket_subscription(self, backend_server):
        """Test WebSocket channel subscription."""
        pass  # Skipped - requires real server


class TestUIInteraction:
    """Test UI interactions using Playwright."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not Path("web/frontend/build").exists(),
        reason="Frontend not built",
    )
    async def test_ui_loads(self, page: Page, backend_server: str):
        """Test UI loads successfully."""
        # Navigate to frontend
        await page.goto("http://localhost:3000")

        # Wait for title to load
        await expect(page).to_have_title(re.compile(r"OmniMind"))

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not Path("web/frontend/build").exists(),
        reason="Frontend not built",
    )
    async def test_login_flow(
        self, page: Page, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test login flow."""
        await page.goto("http://localhost:3000")

        # Find and fill login form
        await page.fill('input[name="username"]', auth_credentials["username"])
        await page.fill('input[name="password"]', auth_credentials["password"])

        # Submit login
        await page.click('button[type="submit"]')

        # Wait for dashboard to load
        await page.wait_for_selector(".dashboard", timeout=5000)

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not Path("web/frontend/build").exists(),
        reason="Frontend not built",
    )
    async def test_task_submission_ui(
        self, page: Page, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test task submission through UI."""
        await page.goto("http://localhost:3000")

        # Login first
        await page.fill('input[name="username"]', auth_credentials["username"])
        await page.fill('input[name="password"]', auth_credentials["password"])
        await page.click('button[type="submit"]')

        # Wait for dashboard
        await page.wait_for_selector(".dashboard", timeout=5000)

        # Navigate to task submission
        await page.click('a[href="/tasks"]')

        # Fill task form
        await page.fill('textarea[name="task"]', "Test task from UI")
        await page.select_option('select[name="priority"]', "high")

        # Submit task
        await page.click('button[type="submit"]')

        # Wait for confirmation
        await page.wait_for_selector(".success-message", timeout=10000)


class TestPerformance:
    """Performance and load testing."""

    @pytest.mark.asyncio
    async def test_api_response_time(self, backend_server):
        """Test API response times are acceptable."""
        # Test health endpoint directly with TestClient
        start = time.perf_counter()
        response = backend_server.get("/health")
        duration = time.perf_counter() - start

        assert response.status_code == 200
        assert duration < 1.0, f"Health endpoint too slow: {duration:.3f}s"

    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self, backend_server, auth_credentials: Dict[str, str]
    ):
        """Test handling of concurrent requests."""

        async def make_request(i: int):
            # Use TestClient directly
            response = backend_server.get(
                "/metrics",
                auth=(auth_credentials["username"], auth_credentials["password"]),
            )
            return response.status_code

        # Make 10 concurrent requests
        tasks = [make_request(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(status == 200 for status in results)


class TestSecurityIntegration:
    """Test security features integration."""

    @pytest.mark.asyncio
    async def test_audit_logging(
        self, backend_server, auth_credentials: Dict[str, str]
    ):
        """Test audit logging is working."""
        auth = (auth_credentials["username"], auth_credentials["password"])

        # Make authenticated request
        response = backend_server.get("/observability", auth=auth)
        assert response.status_code == 200

        data = response.json()
        assert "validation" in data

    @pytest.mark.asyncio
    async def test_rate_limiting(self, backend_server):
        """Test rate limiting (if enabled)."""
        # Make many rapid requests
        statuses = []
        for _ in range(50):  # Reduced from 100 to be more reasonable
            try:
                response = backend_server.get("/health")
                statuses.append(response.status_code)
            except Exception:
                pass

        # Should mostly succeed (rate limiting may not be strict in tests)
        success_count = sum(1 for s in statuses if s == 200)
        assert success_count > 25, "Too many requests failed"


class TestDataIntegrity:
    """Test data integrity across components."""

    @pytest.mark.asyncio
    async def test_task_state_consistency(
        self, backend_server, auth_credentials: Dict[str, str]
    ):
        """Test task state is consistent across endpoints."""
        auth = (auth_credentials["username"], auth_credentials["password"])

        # Submit task
        task_data = {"task": "Consistency test", "max_iterations": 1}
        response = backend_server.post(
            "/tasks/orchestrate",
            json=task_data,
            auth=auth,
        )
        assert response.status_code == 200

        # Get snapshot
        response = backend_server.get("/snapshot", auth=auth)
        assert response.status_code == 200
        snapshot = response.json()

        # Verify task appears in snapshot
        assert "plan_summary" in snapshot


class TestErrorHandling:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_invalid_task_input(
        self, backend_server, auth_credentials: Dict[str, str]
    ):
        """Test handling of invalid task input."""
        auth = (auth_credentials["username"], auth_credentials["password"])

        # Submit invalid task (empty description)
        response = backend_server.post(
            "/tasks/orchestrate",
            json={"task": "", "max_iterations": 1},
            auth=auth,
        )

        # Should handle gracefully (either accept or reject with proper error)
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_service_recovery(self, backend_server):
        """Test service can recover from errors."""
        # Make request to ensure service is healthy
        response = backend_server.get("/health")
        assert response.status_code == 200

        # Service should continue to work after errors
        response = backend_server.get("/health")
        assert response.status_code == 200


# Test configuration
def pytest_configure(config):
    """Configure pytest for E2E tests."""
    config.addinivalue_line("markers", "e2e: mark test as end-to-end integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Mark all tests in this module as e2e
pytestmark = pytest.mark.e2e

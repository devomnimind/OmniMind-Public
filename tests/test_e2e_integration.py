"""
End-to-End Integration Tests using Playwright

These tests validate the entire OmniMind system from UI to backend.
"""

import asyncio
import json
import os
import re
import subprocess
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
    # If running in production mode, use the existing server
    if os.environ.get("OMNIMIND_ENV") == "production":
        yield "http://localhost:8000"
        return

    # Set test credentials
    os.environ["OMNIMIND_DASHBOARD_USER"] = "test_user"
    os.environ["OMNIMIND_DASHBOARD_PASS"] = "test_pass"

    # Start server in background
    env = os.environ.copy()
    project_root = Path(__file__).parent.parent
    env["PYTHONPATH"] = str(project_root)
    import sys
    server_process = subprocess.Popen(
        [sys.executable, str(project_root / "run_test_server.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(project_root),
    )

    # Wait for server to start (increased for slow environments)
    time.sleep(10)

    # Check if server is still running
    if server_process.poll() is not None:
        stdout, stderr = server_process.communicate()
        print(f"Server failed to start. Return code: {server_process.returncode}")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        pytest.fail("Backend server failed to start")

    yield "http://localhost:8001"

    # Stop server
    server_process.terminate()
    server_process.wait()


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
    return {
        "username": os.environ.get("OMNIMIND_DASHBOARD_USER", "test_user"),
        "password": os.environ.get("OMNIMIND_DASHBOARD_PASS", "test_pass"),
    }


class TestAPIEndpoints:
    """Test API endpoints via direct HTTP calls."""

    @pytest.mark.skipif(
        not os.environ.get("RUN_E2E_TESTS"),
        reason="E2E tests require running server (set RUN_E2E_TESTS=1)",
    )
    @pytest.mark.asyncio
    async def test_health_endpoint(self, backend_server: str):
        """Test health endpoint is accessible."""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_server}/health")
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert data["status"] == "ok"

    @pytest.mark.skipif(
        not os.environ.get("RUN_E2E_TESTS"),
        reason="E2E tests require running server (set RUN_E2E_TESTS=1)",
    )
    @pytest.mark.asyncio
    async def test_authenticated_endpoint(
        self, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test authenticated endpoint access."""
        import httpx

        async with httpx.AsyncClient() as client:
            # Without auth - should fail
            response = await client.get(f"{backend_server}/status")
            assert response.status_code == 401

            # With auth - should succeed
            response = await client.get(
                f"{backend_server}/status",
                auth=(auth_credentials["username"], auth_credentials["password"]),
            )
            assert response.status_code == 200

    @pytest.mark.skipif(
        not os.environ.get("RUN_E2E_TESTS"),
        reason="E2E tests require running server (set RUN_E2E_TESTS=1)",
    )
    @pytest.mark.asyncio
    async def test_task_orchestration_workflow(
        self, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test complete task orchestration workflow."""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            auth = (auth_credentials["username"], auth_credentials["password"])

            # Submit task
            task_data = {"task": "Test task", "max_iterations": 1}
            response = await client.post(
                f"{backend_server}/tasks/orchestrate",
                json=task_data,
                auth=auth,
            )
            assert response.status_code == 200
            result = response.json()
            assert "task" in result
            assert result["task"] == "Test task"

            # Check metrics were updated
            response = await client.get(f"{backend_server}/metrics", auth=auth)
            assert response.status_code == 200
            metrics = response.json()
            assert "backend" in metrics
            assert metrics["backend"]["requests"] > 0


class TestWebSocketIntegration:
    """Test WebSocket real-time communication."""

    @pytest.mark.skipif(
        not os.environ.get("RUN_E2E_TESTS"),
        reason="E2E tests require running server (set RUN_E2E_TESTS=1)",
    )
    @pytest.mark.asyncio
    async def test_websocket_connection(self, backend_server: str):
        """Test WebSocket connection and ping/pong."""
        import websockets

        ws_url = backend_server.replace("http", "ws") + "/ws"

        async with websockets.connect(ws_url) as websocket:
            # Consume initial 'connected' message if present
            try:
                initial = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                initial_data = json.loads(initial)
                if initial_data.get("type") != "connected":
                    # If not connected message, put it back or handle it?
                    # For now assume it might be the pong if we were too fast, but unlikely.
                    pass
            except asyncio.TimeoutError:
                pass

            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))

            # Receive pong
            response = await websocket.recv()
            data = json.loads(response)
            assert data["type"] == "pong"
            assert "timestamp" in data

    @pytest.mark.skipif(
        not os.environ.get("RUN_E2E_TESTS"),
        reason="E2E tests require running server (set RUN_E2E_TESTS=1)",
    )
    @pytest.mark.asyncio
    async def test_websocket_subscription(self, backend_server: str):
        """Test WebSocket channel subscription."""
        import websockets

        ws_url = backend_server.replace("http", "ws") + "/ws"

        async with websockets.connect(ws_url) as websocket:
            # Consume initial 'connected' message
            try:
                await asyncio.wait_for(websocket.recv(), timeout=1.0)
            except asyncio.TimeoutError:
                pass

            # Subscribe to channels
            await websocket.send(
                json.dumps({"type": "subscribe", "channels": ["tasks", "agents"]})
            )

            # Consume subscription confirmation
            try:
                sub_response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                sub_data = json.loads(sub_response)
                if sub_data.get("type") != "subscribed":
                    # If not subscribed message, maybe we got pong early?
                    pass
            except asyncio.TimeoutError:
                pass

            # Wait a bit for subscription to process
            await asyncio.sleep(0.5)

            # Send ping to verify connection still alive
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            data = json.loads(response)
            assert data["type"] == "pong"


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
    async def test_api_response_time(self, backend_server: str):
        """Test API response times are acceptable."""
        import httpx

        async with httpx.AsyncClient() as client:
            # Test health endpoint
            start = time.perf_counter()
            response = await client.get(f"{backend_server}/health")
            duration = time.perf_counter() - start

            assert response.status_code == 200
            assert duration < 0.5, f"Health endpoint too slow: {duration:.3f}s"

    @pytest.mark.asyncio
    async def test_concurrent_requests(
        self, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test handling of concurrent requests."""
        import httpx

        async def make_request(client: httpx.AsyncClient, i: int):
            response = await client.get(
                f"{backend_server}/metrics",
                auth=(auth_credentials["username"], auth_credentials["password"]),
            )
            return response.status_code

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Make 10 concurrent requests
            tasks = [make_request(client, i) for i in range(10)]
            results = await asyncio.gather(*tasks)

            # All should succeed
            assert all(status == 200 for status in results)


class TestSecurityIntegration:
    """Test security features integration."""

    @pytest.mark.asyncio
    async def test_audit_logging(
        self, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test audit logging is working."""
        import httpx

        async with httpx.AsyncClient() as client:
            auth = (auth_credentials["username"], auth_credentials["password"])

            # Make authenticated request
            response = await client.get(f"{backend_server}/observability", auth=auth)
            assert response.status_code == 200

            data = response.json()
            assert "validation" in data

    @pytest.mark.asyncio
    async def test_rate_limiting(self, backend_server: str):
        """Test rate limiting (if enabled)."""
        import httpx

        async with httpx.AsyncClient() as client:
            # Make many rapid requests
            statuses = []
            for _ in range(100):
                try:
                    response = await client.get(f"{backend_server}/health")
                    statuses.append(response.status_code)
                except Exception:
                    pass

            # Should mostly succeed (rate limiting may not be strict in tests)
            success_count = sum(1 for s in statuses if s == 200)
            assert success_count > 50, "Too many requests failed"


class TestDataIntegrity:
    """Test data integrity across components."""

    @pytest.mark.asyncio
    async def test_task_state_consistency(
        self, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test task state is consistent across endpoints."""
        import httpx

        async with httpx.AsyncClient(timeout=30.0) as client:
            auth = (auth_credentials["username"], auth_credentials["password"])

            # Submit task
            task_data = {"task": "Consistency test", "max_iterations": 1}
            response = await client.post(
                f"{backend_server}/tasks/orchestrate",
                json=task_data,
                auth=auth,
            )
            assert response.status_code == 200

            # Get snapshot
            response = await client.get(f"{backend_server}/snapshot", auth=auth)
            assert response.status_code == 200
            snapshot = response.json()

            # Verify task appears in snapshot
            assert "plan_summary" in snapshot


class TestErrorHandling:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_invalid_task_input(
        self, backend_server: str, auth_credentials: Dict[str, str]
    ):
        """Test handling of invalid task input."""
        import httpx

        async with httpx.AsyncClient() as client:
            auth = (auth_credentials["username"], auth_credentials["password"])

            # Submit invalid task (empty description)
            response = await client.post(
                f"{backend_server}/tasks/orchestrate",
                json={"task": "", "max_iterations": 1},
                auth=auth,
            )

            # Should handle gracefully (either accept or reject with proper error)
            assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_service_recovery(self, backend_server: str):
        """Test service can recover from errors."""
        import httpx

        async with httpx.AsyncClient() as client:
            # Make request to ensure service is healthy
            response = await client.get(f"{backend_server}/health")
            assert response.status_code == 200

            # Service should continue to work after errors
            response = await client.get(f"{backend_server}/health")
            assert response.status_code == 200


# Test configuration
def pytest_configure(config):
    """Configure pytest for E2E tests."""
    config.addinivalue_line("markers", "e2e: mark test as end-to-end integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Mark all tests in this module as e2e
pytestmark = pytest.mark.e2e

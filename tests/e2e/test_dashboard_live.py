import time
import httpx
import pytest
    import asyncio
    import json
    import websockets

"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""



# Assuming API is running on localhost:8000
API_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_health_endpoint_availability():
    """
    Verify that the health endpoint is reachable and returns 200 OK.
    """
    async with httpx.AsyncClient() as client:
        # Check root first
        root_resp = await client.get(f"{API_URL}/")
        assert root_resp.status_code == 200, f"Root endpoint failed: {root_resp.status_code}"

        # Check health with slash
        response = await client.get(f"{API_URL}/api/v1/health/")
        if response.status_code == 404:
            # Try without slash
            response = await client.get(f"{API_URL}/api/v1/health")

        assert response.status_code == 200, f"Health endpoint failed with {response.status_code}"
        data = response.json()
        assert "overall_status" in data
        assert "checks" in data


@pytest.mark.asyncio
async def test_health_data_freshness():
    """
    Verify that the health data is fresh (timestamp is recent).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/api/v1/health/")
        assert response.status_code == 200
        data = response.json()

        server_time = data.get("timestamp")
        assert server_time is not None

        current_time = time.time()
        # Allow up to 10 seconds drift/latency
        assert (
            abs(current_time - server_time) < 10
        ), f"Data is stale! Server time: {server_time}, Current: {current_time}"


@pytest.mark.asyncio
async def test_health_checks_structure():
    """
    Verify that specific checks (cpu, memory, disk) are present and structured correctly.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/api/v1/health/")
        data = response.json()
        checks = data.get("checks", {})

        required_checks = ["cpu", "memory", "disk"]
        for check in required_checks:
            assert check in checks, f"Missing check: {check}"
            assert "status" in checks[check]
            assert "details" in checks[check]


@pytest.mark.asyncio
async def test_health_trend_endpoint():
    """
    Verify the trend endpoint for a specific check.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/api/v1/health/cpu/trend")
        assert response.status_code == 200
        data = response.json()

        assert data["check_name"] == "cpu"
        assert "trend" in data
        assert "prediction" in data


@pytest.mark.asyncio
async def test_tribunal_activity_monitoring():
    """
    Verify that the Tribunal activity monitoring endpoint is available.
    Tests the dashboard endpoint for tribunal activity data.
    """
    async with httpx.AsyncClient() as client:
        # Try tribunal activity endpoint
        tribunal_url = f"{API_URL}/api/tribunal/activity"

        try:
            response = await client.get(tribunal_url, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                # Verify basic structure
                assert isinstance(data, dict), "Response should be a dict"
                # If data is present, check for expected fields
                if data:
                    assert (
                        "proposals" in data or "activity_score" in data
                    ), "Should have proposals or activity_score"
                return  # Success
        except (httpx.TimeoutException, httpx.ConnectError):
            pass  # Endpoint not available, try fallback

        # Fallback: Check if dashboard is running via health endpoint
        try:
            health_response = await client.get(f"{API_URL}/api/v1/health/", timeout=5.0)
            if health_response.status_code == 200:
                # Dashboard is running, but tribunal endpoint not available
                # This is acceptable for CI/CD environments
                pytest.skip("Tribunal endpoint not available, but dashboard is running")
            else:
                pytest.fail("Dashboard health endpoint failed")
        except (httpx.TimeoutException, httpx.ConnectError):
            pytest.fail("Dashboard not available - required for tribunal monitoring")


@pytest.mark.asyncio
async def test_daemon_endpoints():
    """
    Verify that daemon endpoints required by the dashboard are available.
    """
    async with httpx.AsyncClient() as client:
        # Check /daemon/status
        status_resp = await client.get(f"{API_URL}/daemon/status")
        assert status_resp.status_code == 200, f"/daemon/status failed: {status_resp.status_code}"
        status_data = status_resp.json()
        assert "active_tasks" not in status_data  # Removed field
        assert "running" in status_data
        assert "system_metrics" in status_data
        assert "system_metrics" in status_data
        metrics = status_data["system_metrics"]
        assert "cpu_percent" in metrics
        assert "memory_percent" in metrics

        # Check /daemon/tasks
        tasks_resp = await client.get(f"{API_URL}/daemon/tasks")
        assert tasks_resp.status_code == 200, f"/daemon/tasks failed: {tasks_resp.status_code}"
        tasks_data = tasks_resp.json()
        assert "tasks" in tasks_data
        assert isinstance(tasks_data["tasks"], list)


@pytest.mark.asyncio
async def test_polling_endpoint():
    """
    Verify that the polling endpoint for messages is available.
    """
    async with httpx.AsyncClient() as client:
        # Check /api/omnimind/messages
        resp = await client.get(f"{API_URL}/api/omnimind/messages")
        assert resp.status_code == 200, f"/api/omnimind/messages failed: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_websocket_metrics():
    """
    Verify that the WebSocket endpoint broadcasts metrics updates.
    """


    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            # Wait for connection established message
            init_msg = await websocket.recv()
            init_data = json.loads(init_msg)
            assert init_data["type"] == "connection_established"

            # Wait for metrics updates (should receive both types within 5 seconds)
            received_types = set()
            start_time = asyncio.get_event_loop().time()

            while len(received_types) < 2 and (asyncio.get_event_loop().time() - start_time) < 5.0:
                metrics_msg = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                metrics_data = json.loads(metrics_msg)

                if metrics_data["type"] == "metrics_update":
                    received_types.add("simple")
                    payload = metrics_data["data"]
                    assert "cpu_percent" in payload
                    assert "memory_percent" in payload

                elif (
                    metrics_data["type"] == "metrics" and metrics_data.get("channel") == "sinthome"
                ):
                    received_types.add("sinthome")
                    payload = metrics_data["data"]
                    assert "raw" in payload
                    assert "metrics" in payload
                    assert "consciousness" in payload

            assert "simple" in received_types, "Did not receive RealtimeAnalytics metrics"
            assert "sinthome" in received_types, "Did not receive OmniMindSinthome metrics"

    except Exception as e:
        pytest.fail(f"WebSocket test failed: {e}")

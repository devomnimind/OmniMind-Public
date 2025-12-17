import asyncio
import time

import httpx
import pytest

# Assuming API is running on localhost:8000
API_URL = "http://localhost:8000"


@pytest.mark.asyncio
async def test_health_endpoint_availability(async_client):
    """
    Verify that the health endpoint is reachable and returns 200 OK.
    """
    # Check root first
    root_resp = await async_client.get("/", timeout=60.0)
    assert root_resp.status_code == 200, f"Root endpoint failed: {root_resp.status_code}"

    # Check health
    response = await async_client.get("/health/", timeout=60.0)
    if response.status_code == 404:
        # Try without slash
        response = await async_client.get("/health", timeout=60.0)

    assert response.status_code == 200, f"Health endpoint failed with {response.status_code}"
    data = response.json()
    assert "overall_status" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_health_data_freshness(async_client):
    """
    Verify that the health data is fresh (timestamp is recent).
    """
    response = await async_client.get("/health/", timeout=60.0)
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
async def test_health_checks_structure(async_client):
    """
    Verify that specific checks (cpu, memory) are present and structured correctly.
    Requer servidor real rodando.
    """
    response = await async_client.get("/health/", timeout=60.0)
    assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"
    data = response.json()
    checks = data.get("checks", {})

    # Verificar checks mínimos (cpu e memory)
    required_checks = ["cpu", "memory"]
    for check in required_checks:
        assert check in checks, f"Missing check: {check}"
        assert "status" in checks[check]
        assert "details" in checks[check]


@pytest.mark.asyncio
async def test_health_trend_endpoint(async_client):
    """
    Verify the trend endpoint for a specific check.
    """
    response = await async_client.get("/health/cpu/trend", timeout=60.0)
    assert response.status_code == 200
    data = response.json()

    assert data["check_name"] == "cpu"
    assert "trend" in data
    assert "prediction" in data


@pytest.mark.asyncio
async def test_tribunal_activity_monitoring(async_client):
    """
    Verify that the Tribunal activity monitoring endpoint is available.
    Tests the dashboard endpoint for tribunal activity data.
    """
    # Try tribunal activity endpoint
    response = await async_client.get("/api/tribunal/activity", timeout=60.0)
    assert response.status_code == 200, f"Tribunal endpoint failed: {response.status_code}"

    data = response.json()
    # Verify basic structure
    assert isinstance(data, dict), "Response should be a dict"
    assert "status" in data
    assert "activity_score" in data
    assert "proposals" in data


@pytest.mark.asyncio
async def test_daemon_endpoints(async_client):
    """
    Verify that daemon endpoints required by the dashboard are available.
    Requer autenticação (BasicAuth).
    """
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Check /daemon/status
            status_resp = await async_client.get("/daemon/status", timeout=60.0)

            # Aceitar 401 se auth não estiver configurada (endpoint existe mas precisa auth)
            if status_resp.status_code == 401:
                pytest.skip("Dashboard auth required - credenciais não configuradas")

            assert (
                status_resp.status_code == 200
            ), f"/daemon/status failed: {status_resp.status_code}"
            status_data = status_resp.json()
            assert "running" in status_data
            assert "system_metrics" in status_data
            metrics = status_data["system_metrics"]
            assert "cpu_percent" in metrics
            assert "memory_percent" in metrics

            # Check /daemon/tasks
            tasks_resp = await async_client.get("/daemon/tasks", timeout=60.0)
            assert tasks_resp.status_code == 200, f"/daemon/tasks failed: {tasks_resp.status_code}"
            tasks_data = tasks_resp.json()
            assert "tasks" in tasks_data
            assert isinstance(tasks_data["tasks"], list)
            break

        except (httpx.TimeoutException, httpx.ConnectError) as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(2)  # Máquina sob contenção, esperar mais
                continue
            raise AssertionError(f"Daemon endpoints falhou após {max_retries} tentativas: {e}")


@pytest.mark.asyncio
async def test_polling_endpoint(async_client):
    """
    Verify that the polling endpoint for messages is available.
    """
    # Check /api/omnimind/messages
    resp = await async_client.get("/api/omnimind/messages", timeout=60.0)
    assert resp.status_code == 200, f"/api/omnimind/messages failed: {resp.status_code}"
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_websocket_metrics(omnimind_server, auth_credentials):
    """
    Verify that the WebSocket endpoint broadcasts metrics updates.
    """
    import asyncio
    import json
    from base64 import b64encode

    import websockets

    # Use dynamic URL from fixture
    base_url = omnimind_server.replace("http://", "ws://").replace("https://", "wss://")
    uri = f"{base_url}/ws"

    # Get credentials from fixture
    user, password = auth_credentials

    # Basic Auth headers
    auth_token = b64encode(f"{user}:{password}".encode("ascii")).decode("ascii")
    headers = {"Authorization": f"Basic {auth_token}"}

    try:
        async with websockets.connect(uri, additional_headers=headers) as websocket:
            # Wait for connection established message
            init_msg = await websocket.recv()
            init_data = json.loads(init_msg)
            assert init_data["type"] == "connected"

            # Subscribe to sinthome channel
            await websocket.send(json.dumps({"type": "subscribe", "channels": ["sinthome"]}))

            # Wait for subscription confirmation
            try:
                sub_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                _ = json.loads(sub_msg)
            except asyncio.TimeoutError:
                pass  # Continue even if subscription confirmation times out

            # Wait for metrics updates (should receive both types within 60 seconds)
            received_types: set[str] = set()
            start_time = asyncio.get_event_loop().time()

            # Increased total wait time to 60s for heavy load scenarios
            while len(received_types) < 2 and (asyncio.get_event_loop().time() - start_time) < 60.0:
                try:
                    # Increased per-message timeout to 30s
                    metrics_msg = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    metrics_data = json.loads(metrics_msg)

                    if metrics_data["type"] == "metrics_update":
                        received_types.add("simple")
                        payload = metrics_data["data"]
                        assert "cpu_percent" in payload
                        assert "memory_percent" in payload

                    elif (
                        metrics_data["type"] == "metrics"
                        and metrics_data.get("channel") == "sinthome"
                    ):
                        received_types.add("sinthome")
                        payload = metrics_data["data"]
                        assert "raw" in payload
                        assert "metrics" in payload
                        assert "consciousness" in payload
                except asyncio.TimeoutError:
                    # Just continue loop to check total time
                    continue

            assert "simple" in received_types, "Did not receive RealtimeAnalytics metrics"
            assert "sinthome" in received_types, "Did not receive OmniMindSinthome metrics"

    except Exception as e:
        pytest.fail(f"WebSocket test failed: {e}")

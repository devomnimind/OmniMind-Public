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

"""Tests for Phase 8.2 backend enhancements (WebSocket and APIs)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# Dict not used in this test file


# Mock imports for testing
try:
    from web.backend.main import app
    from web.backend.routes.tasks import TaskStatus
    from web.backend.websocket_manager import MessageType, ws_manager

    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    pytest.skip("Backend not available", allow_module_level=True)


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


class TestTasksAPI:
    """Test task management API endpoints."""

    def test_create_task(self, client: TestClient) -> None:
        """Test task creation."""
        task_data = {
            "description": "Test task",
            "priority": "high",
            "max_iterations": 5,
        }

        response = client.post("/api/tasks/", json=task_data)
        assert response.status_code == 200

        data = response.json()
        assert "task_id" in data
        assert data["description"] == "Test task"
        assert data["priority"] == "high"
        assert data["status"] == TaskStatus.PENDING

    def test_list_tasks(self, client: TestClient) -> None:
        """Test listing tasks."""
        # Create a task first
        task_data = {"description": "List test task", "priority": "medium"}
        client.post("/api/tasks/", json=task_data)

        # List tasks
        response = client.get("/api/tasks/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_task(self, client: TestClient) -> None:
        """Test getting specific task."""
        # Create task
        task_data = {"description": "Get test task"}
        create_response = client.post("/api/tasks/", json=task_data)
        task_id = create_response.json()["task_id"]

        # Get task
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["task_id"] == task_id
        assert data["description"] == "Get test task"

    def test_update_task_progress(self, client: TestClient) -> None:
        """Test updating task progress."""
        # Create task
        create_response = client.post("/api/tasks/", json={"description": "Progress test"})
        task_id = create_response.json()["task_id"]

        # Update progress
        progress_data = {
            "task_id": task_id,
            "progress": 50.0,
            "status": "running",
            "message": "Halfway done",
        }

        response = client.post(f"/api/tasks/{task_id}/progress", json=progress_data)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "updated"

    def test_cancel_task(self, client: TestClient) -> None:
        """Test cancelling a task."""
        # Create task
        create_response = client.post("/api/tasks/", json={"description": "Cancel test"})
        task_id = create_response.json()["task_id"]

        # Cancel task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "cancelled"


class TestAgentsAPI:
    """Test agent status and monitoring API endpoints."""

    def test_list_agents(self, client: TestClient) -> None:
        """Test listing agents."""
        response = client.get("/api/agents/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_agents_status(self, client: TestClient) -> None:
        """Test getting overall agent status."""
        response = client.get("/api/agents/status")
        assert response.status_code == 200

        data = response.json()
        assert "total_agents" in data
        assert "active" in data
        assert "timestamp" in data

    def test_get_agent_metrics(self, client: TestClient) -> None:
        """Test getting agent metrics."""
        # Get first agent (orchestrator-1)
        response = client.get("/api/agents/orchestrator-1/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "agent_id" in data
        assert "tasks_completed" in data
        assert "success_rate" in data


class TestSecurityAPI:
    """Test security events API endpoints."""

    def test_list_security_events(self, client: TestClient) -> None:
        """Test listing security events."""
        response = client.get("/api/security/events")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_get_security_stats(self, client: TestClient) -> None:
        """Test getting security statistics."""
        response = client.get("/api/security/events/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_events" in data
        assert "resolved" in data
        assert "by_severity" in data


class TestWebSocketManager:
    """Test WebSocket manager functionality."""

    @pytest.mark.asyncio
    async def test_websocket_manager_start_stop(self) -> None:
        """Test starting and stopping WebSocket manager."""
        await ws_manager.start()
        assert ws_manager._running

        await ws_manager.stop()
        assert not ws_manager._running

    @pytest.mark.asyncio
    async def test_websocket_broadcast(self) -> None:
        """Test broadcasting messages."""
        await ws_manager.start()

        # Broadcast a message
        await ws_manager.broadcast(
            MessageType.TASK_UPDATE,
            {"task_id": "test-123", "status": "completed"},
            channel="tasks",
        )

        # Check message was queued
        assert not ws_manager._message_queue.empty()

        await ws_manager.stop()

    def test_websocket_stats(self) -> None:
        """Test getting WebSocket statistics."""
        stats = ws_manager.get_stats()
        assert "active_connections" in stats
        assert "clients" in stats


@pytest.mark.asyncio
class TestAsyncMCPClient:
    """Test async MCP client."""

    async def test_mcp_client_import(self) -> None:
        """Test importing async MCP client."""
        try:
            from src.integrations.mcp_client_async import AsyncMCPClient

            client = AsyncMCPClient()
            assert client.endpoint == "http://127.0.0.1:4321/mcp"
            assert client.timeout == 30.0
            assert client.max_retries == 3
        except ImportError:
            pytest.skip("AsyncMCPClient not available")


class TestMetacognitionModule:
    """Test metacognition module components."""

    def test_self_analysis_import(self) -> None:
        """Test importing self-analysis module."""
        try:
            from src.metacognition.self_analysis import SelfAnalysis

            analyzer = SelfAnalysis()
            assert analyzer.hash_chain_path.name == "hash_chain.json"
        except ImportError:
            pytest.skip("SelfAnalysis not available")

    def test_pattern_recognition_import(self) -> None:
        """Test importing pattern recognition module."""
        try:
            from src.metacognition.pattern_recognition import PatternRecognition

            recognizer = PatternRecognition(sensitivity=0.7)
            assert recognizer.sensitivity == 0.7
        except ImportError:
            pytest.skip("PatternRecognition not available")

    def test_optimization_suggestions_import(self) -> None:
        """Test importing optimization suggestions module."""
        try:
            from src.metacognition.optimization_suggestions import (
                OptimizationSuggestions,
            )

            optimizer = OptimizationSuggestions(max_suggestions=5)
            assert optimizer.max_suggestions == 5
        except ImportError:
            pytest.skip("OptimizationSuggestions not available")

    def test_metacognition_agent_import(self) -> None:
        """Test importing metacognition agent."""
        try:
            from src.metacognition.metacognition_agent import MetacognitionAgent

            agent = MetacognitionAgent()
            assert agent.analysis_interval == 3600
            assert agent.bias_sensitivity == 0.7
        except ImportError:
            pytest.skip("MetacognitionAgent not available")


class TestDBusEnhancements:
    """Test D-Bus controller enhancements."""

    def test_dbus_controller_import(self) -> None:
        """Test importing enhanced D-Bus controller."""
        try:
            from src.integrations.dbus_controller import DBusSystemController

            # Just test that new methods exist
            controller = DBusSystemController.__dict__
            assert "get_disk_usage" in controller
            assert "get_battery_info" in controller
            assert "get_network_interfaces" in controller
            assert "get_system_services_status" in controller
            assert "send_notification" in controller
        except ImportError:
            pytest.skip("DBusSystemController not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

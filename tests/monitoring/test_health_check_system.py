    import os
    import os

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

"""Simple health check system tests."""

import pytest


def test_health_check_system_can_be_imported():
    """Test that health check system module can be imported."""
    try:
        # This will fail if there are syntax errors
        with open("web/backend/monitoring/health_check_system.py") as f:
            code = compile(f.read(), "health_check_system.py", "exec")
        assert code is not None
    except SyntaxError as e:
        pytest.fail(f"Syntax error in health_check_system.py: {e}")


def test_health_routes_can_be_imported():
    """Test that health routes module can be imported."""
    try:
        with open("web/backend/routes/health.py") as f:
            code = compile(f.read(), "health.py", "exec")
        assert code is not None
    except SyntaxError as e:
        pytest.fail(f"Syntax error in health.py: {e}")


def test_health_dashboard_component():
    """Test that HealthDashboard component exists."""

    health_component_path = "web/frontend/src/components/HealthDashboard.tsx"
    assert os.path.exists(health_component_path), "HealthDashboard.tsx should exist"

    with open(health_component_path) as f:
        content = f.read()
        # Check for key functionality
        assert "HealthDashboard" in content
        assert "overall_status" in content
        assert "health_checks" in content or "checks" in content


def test_error_boundaries_component():
    """Test that ComponentErrorBoundaries exists."""
    import os

    boundaries_path = "web/frontend/src/components/ComponentErrorBoundaries.tsx"
    assert os.path.exists(boundaries_path), "ComponentErrorBoundaries.tsx should exist"

    with open(boundaries_path) as f:
        content = f.read()
        # Check for key error boundaries
        assert "DashboardErrorBoundary" in content
        assert "TaskErrorBoundary" in content
        assert "AgentErrorBoundary" in content
        assert "HealthErrorBoundary" in content


def test_drag_drop_task_list():
    """Test that DragDropTaskList component exists."""

    component_path = "web/frontend/src/components/DragDropTaskList.tsx"
    assert os.path.exists(component_path), "DragDropTaskList.tsx should exist"

    with open(component_path) as f:
        content = f.read()
        # Check for drag-drop functionality
        assert "DragDropTaskList" in content
        assert "handleDragStart" in content or "onDragStart" in content
        assert "handleDrop" in content or "onDrop" in content

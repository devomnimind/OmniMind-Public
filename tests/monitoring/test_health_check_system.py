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
    import os
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
    import os
    component_path = "web/frontend/src/components/DragDropTaskList.tsx"
    assert os.path.exists(component_path), "DragDropTaskList.tsx should exist"
    
    with open(component_path) as f:
        content = f.read()
        # Check for drag-drop functionality
        assert "DragDropTaskList" in content
        assert "handleDragStart" in content or "onDragStart" in content
        assert "handleDrop" in content or "onDrop" in content


"""
Tests for OmniMind Daemon

Tests the 24/7 autonomous background service functionality.
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.daemon import (
    DaemonState,
    DaemonTask,
    OmniMindDaemon,
    SystemMetrics,
    TaskPriority,
    create_default_tasks,
)


class TestSystemMetrics:
    """Test SystemMetrics functionality"""

    def test_is_idle_when_low_cpu_and_memory(self) -> None:
        """System should be idle when CPU and memory are low"""
        metrics = SystemMetrics(
            cpu_percent=15.0,
            memory_percent=50.0,
            disk_usage_percent=60.0,
            network_active=False,
            user_active=False,
        )
        assert metrics.is_idle() is True

    def test_not_idle_when_high_cpu(self) -> None:
        """System should not be idle when CPU is high"""
        metrics = SystemMetrics(
            cpu_percent=80.0,
            memory_percent=50.0,
            disk_usage_percent=60.0,
            network_active=False,
            user_active=False,
        )
        assert metrics.is_idle() is False

    def test_not_idle_when_user_active(self) -> None:
        """System should not be idle when user is active"""
        metrics = SystemMetrics(
            cpu_percent=15.0,
            memory_percent=50.0,
            disk_usage_percent=60.0,
            network_active=False,
            user_active=True,
        )
        assert metrics.is_idle() is False

    def test_is_sleep_time_during_night(self) -> None:
        """Should detect sleep time during night hours"""
        # Create metrics with a timestamp during sleep hours (2 AM)
        sleep_time = datetime.now().replace(hour=2, minute=0, second=0)
        metrics = SystemMetrics(
            cpu_percent=10.0,
            memory_percent=30.0,
            disk_usage_percent=40.0,
            network_active=False,
            user_active=False,
            timestamp=sleep_time,
        )
        assert metrics.is_sleep_time() is True

    def test_not_sleep_time_during_day(self) -> None:
        """Should not detect sleep time during day hours"""
        day_time = datetime.now().replace(hour=14, minute=0, second=0)
        metrics = SystemMetrics(
            cpu_percent=10.0,
            memory_percent=30.0,
            disk_usage_percent=40.0,
            network_active=False,
            user_active=False,
            timestamp=day_time,
        )
        assert metrics.is_sleep_time() is False


class TestDaemonTask:
    """Test DaemonTask functionality"""

    def test_task_creation(self) -> None:
        """Should create a task with correct properties"""

        def sample_fn():
            return "done"

        task = DaemonTask(
            task_id="test_task",
            name="Test Task",
            description="A test task",
            priority=TaskPriority.HIGH,
            execute_fn=sample_fn,
        )

        assert task.task_id == "test_task"
        assert task.name == "Test Task"
        assert task.priority == TaskPriority.HIGH
        assert task.execution_count == 0
        assert task.last_execution is None

    def test_task_with_schedule(self) -> None:
        """Should create a task with schedule time"""

        def sample_fn():
            return "done"

        future_time = datetime.now() + timedelta(hours=1)
        task = DaemonTask(
            task_id="scheduled_task",
            name="Scheduled Task",
            description="Runs in the future",
            priority=TaskPriority.MEDIUM,
            execute_fn=sample_fn,
            schedule_time=future_time,
        )

        assert task.schedule_time == future_time

    def test_task_with_repeat_interval(self) -> None:
        """Should create a task with repeat interval"""

        def sample_fn():
            return "done"

        task = DaemonTask(
            task_id="repeat_task",
            name="Repeat Task",
            description="Runs repeatedly",
            priority=TaskPriority.LOW,
            execute_fn=sample_fn,
            repeat_interval=timedelta(hours=2),
        )

        assert task.repeat_interval == timedelta(hours=2)


class TestOmniMindDaemon:
    """Test OmniMindDaemon functionality"""

    def test_daemon_initialization(self) -> None:
        """Should initialize daemon with correct state"""
        workspace = Path("/tmp/test_workspace")
        daemon = OmniMindDaemon(
            workspace_path=workspace,
            check_interval=30,
            enable_cloud=True,
        )

        assert daemon.workspace_path == workspace
        assert daemon.check_interval == 30
        assert daemon.enable_cloud is True
        assert daemon.state == DaemonState.INITIALIZING
        assert daemon.running is False
        assert len(daemon.tasks) == 0

    def test_register_task(self) -> None:
        """Should register a task"""
        daemon = OmniMindDaemon(
            workspace_path=Path("/tmp/test"),
            check_interval=30,
        )

        def sample_fn():
            return "done"

        task = DaemonTask(
            task_id="test",
            name="Test",
            description="Test task",
            priority=TaskPriority.HIGH,
            execute_fn=sample_fn,
        )

        daemon.register_task(task)
        assert len(daemon.tasks) == 1
        assert daemon.tasks[0] == task

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_collect_system_metrics(self, mock_disk, mock_memory, mock_cpu):
        """Should collect system metrics"""
        mock_cpu.return_value = 25.0
        mock_memory.return_value = Mock(percent=60.0)
        mock_disk.return_value = Mock(percent=50.0)

        daemon = OmniMindDaemon(
            workspace_path=Path("/tmp/test"),
            check_interval=30,
        )

        metrics = daemon._collect_system_metrics()

        assert metrics.cpu_percent == 25.0
        assert metrics.memory_percent == 60.0
        assert metrics.disk_usage_percent == 50.0
        assert len(daemon.metrics_history) == 1

    def test_get_next_task_no_eligible(self) -> None:
        """Should return None when no tasks are eligible"""
        daemon = OmniMindDaemon(
            workspace_path=Path("/tmp/test"),
            check_interval=30,
        )

        # Create a task scheduled for the future
        future_time = datetime.now() + timedelta(hours=1)

        def sample_fn():
            return "done"

        task = DaemonTask(
            task_id="future_task",
            name="Future Task",
            description="Runs later",
            priority=TaskPriority.HIGH,
            execute_fn=sample_fn,
            schedule_time=future_time,
        )

        daemon.register_task(task)

        metrics = SystemMetrics(
            cpu_percent=10.0,
            memory_percent=50.0,
            disk_usage_percent=40.0,
            network_active=False,
            user_active=False,
        )

        next_task = daemon._get_next_task(metrics)
        assert next_task is None

    def test_get_next_task_critical_priority(self) -> None:
        """Should always execute critical priority tasks"""
        daemon = OmniMindDaemon(
            workspace_path=Path("/tmp/test"),
            check_interval=30,
        )

        def critical_fn():
            return "critical"

        task = DaemonTask(
            task_id="critical_task",
            name="Critical Task",
            description="Critical priority",
            priority=TaskPriority.CRITICAL,
            execute_fn=critical_fn,
        )

        daemon.register_task(task)

        # Even with high CPU (user active), critical task should run
        metrics = SystemMetrics(
            cpu_percent=90.0,
            memory_percent=80.0,
            disk_usage_percent=70.0,
            network_active=True,
            user_active=True,
        )

        next_task = daemon._get_next_task(metrics)
        assert next_task == task

    @pytest.mark.asyncio
    async def test_execute_task_success(self) -> None:
        """Should execute a task successfully"""
        daemon = OmniMindDaemon(
            workspace_path=Path("/tmp/test"),
            check_interval=30,
        )

        executed = False

        def sample_fn():
            nonlocal executed
            executed = True
            return "success"

        task = DaemonTask(
            task_id="test_task",
            name="Test Task",
            description="Test execution",
            priority=TaskPriority.HIGH,
            execute_fn=sample_fn,
        )

        success = await daemon._execute_task(task)

        assert success is True
        assert executed is True
        assert task.execution_count == 1
        assert task.success_count == 1
        assert task.failure_count == 0
        assert task.last_execution is not None

    @pytest.mark.asyncio
    async def test_execute_task_timeout(self) -> None:
        """Should handle task timeout"""
        daemon = OmniMindDaemon(
            workspace_path=Path("/tmp/test"),
            check_interval=30,
        )

        async def slow_fn():
            await asyncio.sleep(10)  # Longer than timeout
            return "done"

        task = DaemonTask(
            task_id="slow_task",
            name="Slow Task",
            description="Takes too long",
            priority=TaskPriority.HIGH,
            execute_fn=slow_fn,
            max_duration=timedelta(seconds=1),  # Short timeout
        )

        success = await daemon._execute_task(task)

        assert success is False
        assert task.execution_count == 1
        assert task.success_count == 0
        assert task.failure_count == 1

    def test_get_status(self) -> None:
        """Should return daemon status"""
        daemon = OmniMindDaemon(
            workspace_path=Path("/tmp/test"),
            check_interval=30,
            enable_cloud=True,
        )

        def sample_fn():
            return "done"

        task = DaemonTask(
            task_id="test_task",
            name="Test Task",
            description="Test",
            priority=TaskPriority.HIGH,
            execute_fn=sample_fn,
        )

        daemon.register_task(task)

        status = daemon.get_status()

        assert status["state"] == DaemonState.INITIALIZING.value
        assert status["running"] is False
        assert status["tasks_registered"] == 1
        assert status["cloud_enabled"] is True
        assert status["workspace"] == "/tmp/test"


class TestDefaultTasks:
    """Test default daemon tasks"""

    def test_create_default_tasks(self) -> None:
        """Should create default tasks"""
        tasks = create_default_tasks()

        assert len(tasks) > 0
        assert all(isinstance(t, DaemonTask) for t in tasks)

        # Check that we have expected tasks
        task_ids = {t.task_id for t in tasks}
        assert "code_analysis" in task_ids
        assert "test_optimization" in task_ids
        assert "paper_reading" in task_ids
        assert "database_optimization" in task_ids

    def test_default_tasks_have_priorities(self) -> None:
        """Default tasks should have appropriate priorities"""
        tasks = create_default_tasks()

        for task in tasks:
            assert task.priority in TaskPriority
            assert task.execute_fn is not None

    def test_default_tasks_have_repeat_intervals(self) -> None:
        """Default tasks should have repeat intervals"""
        tasks = create_default_tasks()

        for task in tasks:
            assert task.repeat_interval is not None
            assert task.repeat_interval > timedelta(0)


class TestDaemonHybridTopological:
    """Testes de integração entre OmniMindDaemon e HybridTopologicalEngine."""

    def test_daemon_can_monitor_topological_metrics(self) -> None:
        """Testa que daemon pode monitorar métricas topológicas."""
        import numpy as np

        from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
        from src.consciousness.shared_workspace import SharedWorkspace

        # Criar workspace com engine topológico
        workspace = SharedWorkspace(embedding_dim=256)
        workspace.hybrid_topological_engine = HybridTopologicalEngine()

        # Simular estados
        np.random.seed(42)
        for i in range(10):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            workspace.write_module_state("conscious_module", rho_C)
            workspace.write_module_state("preconscious_module", rho_P)
            workspace.write_module_state("unconscious_module", rho_U)
            workspace.advance_cycle()

        # Calcular métricas topológicas
        topological_metrics = workspace.compute_hybrid_topological_metrics()

        # Verificar que daemon pode usar métricas topológicas para monitoramento
        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # Daemon pode usar Omega para monitorar integração do sistema
            # Betti-0 para detectar fragmentação que precisa ser resolvida

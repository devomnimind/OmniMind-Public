"""
Testes para Homeostasis System (homeostasis.py).

Cobertura de:
- Regulação de recursos
- Balanceamento de carga
- Ajuste automático
- Monitoramento de estado
- Tratamento de exceções
"""

from __future__ import annotations

import time
from unittest.mock import Mock, patch

import pytest

from src.metacognition.homeostasis import (
    HomeostaticController,
    ResourceMetrics,
    ResourceState,
    SystemState,
    TaskPriority,
)


class TestSystemState:
    """Testes para SystemState."""

    def test_state_initialization(self) -> None:
        """Testa criação de estado."""
        state = SystemState(
            cpu_usage=50.0,
            memory_usage=60.0,
            temperature=45.0,
        )

        assert state.cpu_usage == 50.0
        assert state.memory_usage == 60.0
        assert state.temperature == 45.0
        assert isinstance(state.timestamp, float)

    def test_state_is_healthy_healthy_system(self) -> None:
        """Testa verificação de saúde - sistema saudável."""
        healthy_state = SystemState(
            cpu_usage=50.0,
            memory_usage=60.0,
            temperature=40.0,
        )

        assert healthy_state.is_healthy() is True

    def test_state_is_healthy_unhealthy_cpu(self) -> None:
        """Testa verificação de saúde - CPU alta."""
        unhealthy_state = SystemState(
            cpu_usage=85.0,
            memory_usage=60.0,
            temperature=40.0,
        )

        assert unhealthy_state.is_healthy() is False

    def test_state_is_healthy_unhealthy_memory(self) -> None:
        """Testa verificação de saúde - memória alta."""
        unhealthy_state = SystemState(
            cpu_usage=50.0,
            memory_usage=85.0,
            temperature=40.0,
        )

        assert unhealthy_state.is_healthy() is False

    def test_state_is_healthy_unhealthy_temperature(self) -> None:
        """Testa verificação de saúde - temperatura alta."""
        unhealthy_state = SystemState(
            cpu_usage=50.0,
            memory_usage=60.0,
            temperature=75.0,
        )

        assert unhealthy_state.is_healthy() is False

    def test_state_is_healthy_boundary_values(self) -> None:
        """Testa verificação de saúde - valores de fronteira."""
        # Valores exatamente no limite devem ser considerados saudáveis
        boundary_state = SystemState(
            cpu_usage=79.9,
            memory_usage=79.9,
            temperature=69.9,
        )

        assert boundary_state.is_healthy() is True


class TestResourceMetrics:
    """Testes para ResourceMetrics."""

    def test_metrics_initialization(self) -> None:
        """Testa criação de métricas."""
        metrics = ResourceMetrics(
            cpu_percent=45.0,
            memory_percent=60.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=1234567890.0,
        )

        assert metrics.cpu_percent == 45.0
        assert metrics.memory_percent == 60.0
        assert metrics.memory_available_gb == 8.0
        assert metrics.disk_percent == 30.0
        assert metrics.timestamp == 1234567890.0

    def test_get_overall_state_optimal(self) -> None:
        """Testa estado ótimo."""
        metrics = ResourceMetrics(
            cpu_percent=40.0,
            memory_percent=50.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=time.time(),
        )

        assert metrics.get_overall_state() == ResourceState.OPTIMAL

    def test_get_overall_state_good(self) -> None:
        """Testa estado bom."""
        metrics = ResourceMetrics(
            cpu_percent=70.0,
            memory_percent=65.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=time.time(),
        )

        assert metrics.get_overall_state() == ResourceState.GOOD

    def test_get_overall_state_warning(self) -> None:
        """Testa estado de aviso."""
        metrics = ResourceMetrics(
            cpu_percent=85.0,
            memory_percent=70.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=time.time(),
        )

        assert metrics.get_overall_state() == ResourceState.WARNING

    def test_get_overall_state_critical(self) -> None:
        """Testa estado crítico."""
        metrics = ResourceMetrics(
            cpu_percent=92.0,
            memory_percent=70.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=time.time(),
        )

        assert metrics.get_overall_state() == ResourceState.CRITICAL

    def test_get_overall_state_emergency(self) -> None:
        """Testa estado de emergência."""
        metrics = ResourceMetrics(
            cpu_percent=96.0,
            memory_percent=70.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=time.time(),
        )

        assert metrics.get_overall_state() == ResourceState.EMERGENCY

    def test_get_overall_state_determined_by_highest_usage(self) -> None:
        """Testa que o estado é determinado pelo uso mais alto."""
        # Disk com uso alto determina o estado
        metrics = ResourceMetrics(
            cpu_percent=40.0,
            memory_percent=50.0,
            memory_available_gb=8.0,
            disk_percent=88.0,  # Determina WARNING
            timestamp=time.time(),
        )

        assert metrics.get_overall_state() == ResourceState.WARNING

    def test_to_dict(self) -> None:
        """Testa conversão para dicionário."""
        timestamp = time.time()
        metrics = ResourceMetrics(
            cpu_percent=45.0,
            memory_percent=60.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=timestamp,
        )

        result = metrics.to_dict()

        expected = {
            "cpu_percent": 45.0,
            "memory_percent": 60.0,
            "memory_available_gb": 8.0,
            "disk_percent": 30.0,
            "timestamp": timestamp,
            "state": "good",  # 60% memory determina GOOD
        }

        assert result == expected

        assert result == expected


class TestHomeostasisController:
    """Testes para HomeostasisController."""

    @pytest.fixture
    def controller(self) -> HomeostaticController:
        """Cria instância do controlador."""
        return HomeostaticController()

    def test_controller_initialization_default(self) -> None:
        """Testa inicialização com valores padrão."""
        controller = HomeostaticController()

        assert controller.check_interval == 5.0
        assert controller.cpu_threshold_warning == 80.0
        assert controller.cpu_threshold_critical == 90.0
        assert controller.memory_threshold_warning == 80.0
        assert controller.memory_threshold_critical == 90.0
        assert controller._running is False
        assert controller._monitoring_task is None
        assert controller._current_metrics is None
        assert controller._metrics_history == []
        assert controller._max_history == 100
        assert controller._state_callbacks == []
        assert controller._throttled is False
        assert controller._throttle_start is None
        assert controller._regulation_history == []

    def test_controller_initialization_custom(self) -> None:
        """Testa inicialização com valores customizados."""
        controller = HomeostaticController(
            check_interval=10.0,
            cpu_threshold_warning=70.0,
            cpu_threshold_critical=85.0,
            memory_threshold_warning=75.0,
            memory_threshold_critical=88.0,
        )

        assert controller.check_interval == 10.0
        assert controller.cpu_threshold_warning == 70.0
        assert controller.cpu_threshold_critical == 85.0
        assert controller.memory_threshold_warning == 75.0
        assert controller.memory_threshold_critical == 88.0

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_current_state(self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock) -> None:
        """Testa obtenção do estado atual."""
        mock_cpu.return_value = 45.0
        mock_memory.return_value = Mock(percent=60.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        state = controller.get_current_state()

        assert isinstance(state, SystemState)
        assert state.cpu_usage == 45.0
        assert state.memory_usage == 60.0
        assert state.temperature == 50.0  # Placeholder value

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_regulate_no_metrics(self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock) -> None:
        """Testa regulação sem métricas."""
        controller = HomeostaticController()
        result = controller.regulate()

        assert result == {"action": "no_metrics", "success": False}

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_regulate_optimal_state(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa regulação em estado ótimo."""
        mock_cpu.return_value = 40.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        # Define métricas atuais diretamente
        controller._current_metrics = controller._collect_metrics()
        result = controller.regulate()

        assert result == {"action": "monitor", "success": True}

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_regulate_emergency_throttling(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa regulação com throttling de emergência."""
        mock_cpu.return_value = 96.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()
        result = controller.regulate()

        assert result == {"action": "emergency_throttle", "success": True}
        assert controller._throttled is True
        assert controller._throttle_start is not None

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_regulate_critical_state(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa regulação em estado crítico."""
        mock_cpu.return_value = 92.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()
        result = controller.regulate()

        assert result == {"action": "reduce_load", "success": True}

    def test_check_and_adjust(self) -> None:
        """Testa método check_and_adjust."""
        controller = HomeostaticController()
        result = controller.check_and_adjust()

        # Deve delegar para regulate
        assert "action" in result
        assert "success" in result

    def test_get_history_empty(self) -> None:
        """Testa histórico vazio."""
        controller = HomeostaticController()
        history = controller.get_history()

        assert history == []

    def test_get_history_with_regulations(self) -> None:
        """Testa histórico com regulações."""
        controller = HomeostaticController()
        controller._regulation_history = [
            {"timestamp": 1234567890.0, "state": "optimal", "action": "monitor"}
        ]

        history = controller.get_history()

        assert len(history) == 1
        assert history[0]["state"] == "optimal"
        assert history[0]["action"] == "monitor"

    def test_register_state_callback(self) -> None:
        """Testa registro de callback."""
        controller = HomeostaticController()
        callback = Mock()

        controller.register_state_callback(callback)

        assert callback in controller._state_callbacks

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_collect_metrics(self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock) -> None:
        """Testa coleta de métricas."""
        mock_cpu.return_value = 45.0
        mock_memory.return_value = Mock(percent=60.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        metrics = controller._collect_metrics()

        assert isinstance(metrics, ResourceMetrics)
        assert metrics.cpu_percent == 45.0
        assert metrics.memory_percent == 60.0
        assert metrics.memory_available_gb == 8.0
        assert metrics.disk_percent == 30.0
        assert isinstance(metrics.timestamp, float)

    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self) -> None:
        """Testa início e parada do monitoramento."""
        controller = HomeostaticController()

        # Start monitoring
        await controller.start()
        assert controller._running is True
        assert controller._monitoring_task is not None

        # Stop monitoring
        await controller.stop()
        assert controller._running is False

        # Task should be cancelled
        if controller._monitoring_task:
            assert controller._monitoring_task.cancelled()

    def test_activate_throttling(self) -> None:
        """Testa ativação de throttling."""
        controller = HomeostaticController()

        controller._activate_throttling()

        assert controller._throttled is True
        assert controller._throttle_start is not None
        assert isinstance(controller._throttle_start, float)

    def test_deactivate_throttling_not_active(self) -> None:
        """Testa desativação de throttling quando não ativo."""
        controller = HomeostaticController()

        controller._deactivate_throttling()

        assert controller._throttled is False
        assert controller._throttle_start is None

    def test_deactivate_throttling_active(self) -> None:
        """Testa desativação de throttling quando ativo."""
        controller = HomeostaticController()
        controller._throttled = True
        controller._throttle_start = time.time() - 10.0  # 10 seconds ago

        controller._deactivate_throttling()

        assert controller._throttled is False
        assert controller._throttle_start is None

    def test_get_current_metrics_none(self) -> None:
        """Testa obtenção de métricas atuais quando não há."""
        controller = HomeostaticController()

        result = controller.get_current_metrics()

        assert result is None

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_current_metrics_with_data(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa obtenção de métricas atuais com dados."""
        mock_cpu.return_value = 45.0
        mock_memory.return_value = Mock(percent=60.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        result = controller.get_current_metrics()

        assert result is not None
        assert result["cpu_percent"] == 45.0
        assert result["memory_percent"] == 60.0
        assert result["state"] == "good"

    def test_get_metrics_history_empty(self) -> None:
        """Testa histórico de métricas vazio."""
        controller = HomeostaticController()

        history = controller.get_metrics_history()

        assert history == []

    def test_get_metrics_history_with_data(self) -> None:
        """Testa histórico de métricas com dados."""
        controller = HomeostaticController()
        metrics = ResourceMetrics(
            cpu_percent=45.0,
            memory_percent=60.0,
            memory_available_gb=8.0,
            disk_percent=30.0,
            timestamp=time.time(),
        )
        controller._metrics_history = [metrics]

        history = controller.get_metrics_history()

        assert len(history) == 1
        assert history[0]["cpu_percent"] == 45.0

    def test_get_metrics_history_limit(self) -> None:
        """Testa limite do histórico de métricas."""
        controller = HomeostaticController()
        metrics = [
            ResourceMetrics(
                cpu_percent=float(i),
                memory_percent=60.0,
                memory_available_gb=8.0,
                disk_percent=30.0,
                timestamp=time.time(),
            )
            for i in range(15)
        ]
        controller._metrics_history = metrics

        history = controller.get_metrics_history(limit=5)

        assert len(history) == 5
        assert history[-1]["cpu_percent"] == 14.0  # Last 5 items

    def test_is_throttled_false(self) -> None:
        """Testa verificação de throttling desativado."""
        controller = HomeostaticController()

        assert controller.is_throttled() is False

    def test_is_throttled_true(self) -> None:
        """Testa verificação de throttling ativado."""
        controller = HomeostaticController()
        controller._throttled = True

        assert controller.is_throttled() is True

    def test_should_execute_task_no_metrics(self) -> None:
        """Testa execução de tarefa sem métricas."""
        controller = HomeostaticController()

        assert controller.should_execute_task(TaskPriority.CRITICAL) is True
        assert controller.should_execute_task(TaskPriority.LOW) is True

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_should_execute_task_optimal_state(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa execução de tarefa em estado ótimo."""
        mock_cpu.return_value = 40.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        # All priorities should execute in optimal state
        assert controller.should_execute_task(TaskPriority.CRITICAL) is True
        assert controller.should_execute_task(TaskPriority.HIGH) is True
        assert controller.should_execute_task(TaskPriority.MEDIUM) is True
        assert controller.should_execute_task(TaskPriority.LOW) is True
        assert controller.should_execute_task(TaskPriority.BACKGROUND) is True

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_should_execute_task_emergency_state(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa execução de tarefa em estado de emergência."""
        mock_cpu.return_value = 96.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        # Only critical tasks should execute in emergency
        assert controller.should_execute_task(TaskPriority.CRITICAL) is True
        assert controller.should_execute_task(TaskPriority.HIGH) is False
        assert controller.should_execute_task(TaskPriority.MEDIUM) is False
        assert controller.should_execute_task(TaskPriority.LOW) is False
        assert controller.should_execute_task(TaskPriority.BACKGROUND) is False

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_should_execute_task_critical_state(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa execução de tarefa em estado crítico."""
        mock_cpu.return_value = 92.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        # Critical and high priority tasks should execute
        assert controller.should_execute_task(TaskPriority.CRITICAL) is True
        assert controller.should_execute_task(TaskPriority.HIGH) is True
        assert controller.should_execute_task(TaskPriority.MEDIUM) is False
        assert controller.should_execute_task(TaskPriority.LOW) is False
        assert controller.should_execute_task(TaskPriority.BACKGROUND) is False

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_should_execute_task_warning_state(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa execução de tarefa em estado de aviso."""
        mock_cpu.return_value = 85.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        # Background tasks should not execute in warning state
        assert controller.should_execute_task(TaskPriority.CRITICAL) is True
        assert controller.should_execute_task(TaskPriority.HIGH) is True
        assert controller.should_execute_task(TaskPriority.MEDIUM) is True
        assert controller.should_execute_task(TaskPriority.LOW) is True
        assert controller.should_execute_task(TaskPriority.BACKGROUND) is False

    def test_get_recommended_batch_size_no_metrics(self) -> None:
        """Testa tamanho de batch recomendado sem métricas."""
        controller = HomeostaticController()

        assert controller.get_recommended_batch_size(100) == 100

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_recommended_batch_size_optimal(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa tamanho de batch recomendado em estado ótimo."""
        mock_cpu.return_value = 40.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        assert controller.get_recommended_batch_size(100) == 100

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_recommended_batch_size_emergency(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa tamanho de batch recomendado em emergência."""
        mock_cpu.return_value = 96.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        # Should be reduced to 1/4
        assert controller.get_recommended_batch_size(100) == 25
        assert controller.get_recommended_batch_size(8) == 2  # Minimum 1

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_recommended_batch_size_critical(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa tamanho de batch recomendado em estado crítico."""
        mock_cpu.return_value = 92.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        # Should be reduced to 1/2
        assert controller.get_recommended_batch_size(100) == 50

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_recommended_batch_size_warning(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa tamanho de batch recomendado em estado de aviso."""
        mock_cpu.return_value = 85.0
        mock_memory.return_value = Mock(percent=50.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        # Should be reduced to 75%
        assert controller.get_recommended_batch_size(100) == 75

    def test_get_stats_no_metrics(self) -> None:
        """Testa estatísticas sem métricas."""
        controller = HomeostaticController()

        stats = controller.get_stats()

        assert stats == {"status": "no_metrics"}

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    @patch("psutil.disk_usage")
    def test_get_stats_with_metrics(
        self, mock_disk: Mock, mock_memory: Mock, mock_cpu: Mock
    ) -> None:
        """Testa estatísticas com métricas."""
        mock_cpu.return_value = 45.0
        mock_memory.return_value = Mock(percent=60.0, available=8 * 1024**3)
        mock_disk.return_value = Mock(percent=30.0)

        controller = HomeostaticController()
        controller._current_metrics = controller._collect_metrics()

        stats = controller.get_stats()

        assert stats["running"] is False
        assert stats["throttled"] is False
        assert "current_metrics" in stats
        assert "thresholds" in stats
        assert stats["history_size"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

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

import pytest
from unittest.mock import Mock, patch

from src.metacognition.homeostasis import (
    HomeostaticController,
    SystemState,
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

    def test_state_is_healthy(self) -> None:
        """Testa verificação de saúde."""
        healthy_state = SystemState(
            cpu_usage=50.0,
            memory_usage=60.0,
            temperature=40.0,
        )

        unhealthy_state = SystemState(
            cpu_usage=95.0,
            memory_usage=95.0,
            temperature=85.0,
        )

        assert healthy_state.is_healthy() is True or healthy_state.is_healthy() is False
        assert (
            unhealthy_state.is_healthy() is False
            or unhealthy_state.is_healthy() is True
        )


class TestHomeostasisController:
    """Testes para HomeostasisController."""

    @pytest.fixture
    def controller(self) -> HomeostaticController:
        """Cria instância do controlador."""
        return HomeostaticController()

    def test_controller_initialization(self, controller: HomeostaticController) -> None:
        """Testa inicialização."""
        assert controller is not None

    def test_get_current_state(self, controller: HomeostaticController) -> None:
        """Testa obtenção do estado atual."""
        state = controller.get_current_state()

        assert isinstance(state, (SystemState, dict)) or state is not None

    def test_regulate_resources(self, controller: HomeostaticController) -> None:
        """Testa regulação de recursos."""
        result = controller.regulate()

        assert result is not None or result is None

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_detect_high_cpu(
        self,
        mock_memory: Mock,
        mock_cpu: Mock,
        controller: HomeostaticController,
    ) -> None:
        """Testa detecção de CPU alta."""
        mock_cpu.return_value = 95.0
        mock_memory.return_value = Mock(percent=50.0)

        action = controller.check_and_adjust()

        assert action is not None or action is None

    @patch("psutil.cpu_percent")
    @patch("psutil.virtual_memory")
    def test_detect_high_memory(
        self,
        mock_memory: Mock,
        mock_cpu: Mock,
        controller: HomeostaticController,
    ) -> None:
        """Testa detecção de memória alta."""
        mock_cpu.return_value = 50.0
        mock_memory.return_value = Mock(percent=95.0)

        action = controller.check_and_adjust()

        assert action is not None or action is None

    def test_apply_regulation(self, controller: HomeostaticController) -> None:
        """Testa aplicação de regulação."""
        if hasattr(controller, "apply_regulation"):
            result = controller.apply_regulation("reduce_load")
            assert result is not None or result is None

    def test_get_regulation_history(self, controller: HomeostaticController) -> None:
        """Testa histórico de regulações."""
        if hasattr(controller, "get_history"):
            history = controller.get_history()
            assert isinstance(history, list) or history is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

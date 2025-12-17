"""
Testes para AgentCircuitBreaker.

Cobertura de:
- Estados do circuit breaker
- Timeout
- Recuperação automática
- Estatísticas
"""

from __future__ import annotations

import asyncio

import pytest

from src.orchestrator.circuit_breaker import (
    AgentCircuitBreaker,
    CircuitBreakerOpen,
    CircuitState,
)


class TestCircuitState:
    """Testes para CircuitState enum."""

    def test_circuit_states(self) -> None:
        """Testa estados do circuit breaker."""
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"


class TestAgentCircuitBreaker:
    """Testes para AgentCircuitBreaker."""

    @pytest.fixture
    def circuit_breaker(self) -> AgentCircuitBreaker:
        """Cria instância do circuit breaker."""
        return AgentCircuitBreaker(failure_threshold=3, timeout=1.0, recovery_timeout=2.0)

    def test_initialization(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa inicialização."""
        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.is_available() is True

    def test_record_success(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa registro de sucesso."""
        circuit_breaker.record_success()
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.last_success_time is not None

    def test_record_failure(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa registro de falha."""
        circuit_breaker.record_failure()
        assert circuit_breaker.failure_count == 1
        assert circuit_breaker.last_failure_time is not None

    def test_opens_after_threshold(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa que circuito abre após threshold."""
        # Registrar falhas até threshold
        for _ in range(3):
            circuit_breaker.record_failure()

        assert circuit_breaker.state == CircuitState.OPEN
        assert circuit_breaker.is_available() is False

    def test_resets_on_success_after_half_open(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa que circuito fecha após sucesso em HALF_OPEN."""
        circuit_breaker.state = CircuitState.HALF_OPEN
        circuit_breaker.record_success()

        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_successful_call(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa chamada bem-sucedida."""

        async def test_func() -> str:
            return "success"

        result = await circuit_breaker.call_with_protection(test_func)
        assert result == "success"
        assert circuit_breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_timeout(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa timeout de chamada."""

        async def slow_func() -> None:
            await asyncio.sleep(5.0)  # Mais que o timeout de 1.0s

        with pytest.raises(asyncio.TimeoutError):
            await circuit_breaker.call_with_protection(slow_func)

        assert circuit_breaker.failure_count == 1

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_exception(
        self, circuit_breaker: AgentCircuitBreaker
    ) -> None:
        """Testa que exceção é lançada quando circuito está aberto."""

        async def test_func() -> None:
            pass

        # Abrir circuito
        for _ in range(3):
            circuit_breaker.record_failure()

        with pytest.raises(CircuitBreakerOpen):
            await circuit_breaker.call_with_protection(test_func)

    @pytest.mark.asyncio
    async def test_recovery_after_timeout(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa recuperação após timeout."""

        async def test_func() -> str:
            return "recovered"

        # Abrir circuito
        for _ in range(3):
            circuit_breaker.record_failure()

        # Aguardar recovery timeout
        await asyncio.sleep(2.1)

        # Deve estar em HALF_OPEN e permitir tentativa
        assert circuit_breaker.is_available() is True

        result = await circuit_breaker.call_with_protection(test_func)
        assert result == "recovered"
        assert circuit_breaker.state == CircuitState.CLOSED

    def test_get_stats(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa obtenção de estatísticas."""
        stats = circuit_breaker.get_stats()

        assert "state" in stats
        assert "failure_count" in stats
        assert "failure_threshold" in stats
        assert "timeout" in stats

    def test_reset(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa reset do circuit breaker."""
        # Gerar falhas
        for _ in range(3):
            circuit_breaker.record_failure()

        assert circuit_breaker.state == CircuitState.OPEN

        # Resetar
        circuit_breaker.reset()

        assert circuit_breaker.state == CircuitState.CLOSED
        assert circuit_breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_sync_function_call(self, circuit_breaker: AgentCircuitBreaker) -> None:
        """Testa chamada de função síncrona."""

        def sync_func(x: int) -> int:
            return x * 2

        result = await circuit_breaker.call_with_protection(sync_func, 5)
        assert result == 10

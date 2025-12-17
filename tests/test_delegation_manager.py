"""
Testes para DelegationManager (Seção 7 da Auditoria).

Testa:
1. Delegações com timeout
2. Circuit breaker
3. Retry automático
4. Auditoria de delegações
5. Heartbeat monitoring
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator.delegation_manager import (
    AgentMetrics,
    CircuitState,
    DelegationManager,
    DelegationRecord,
    DelegationStatus,
    HeartbeatMonitor,
)


class TestDelegationManager:
    """Testes do DelegationManager."""

    @pytest.fixture
    def mock_orchestrator(self):
        """Cria mock do OrchestratorAgent."""
        mock = MagicMock()
        mock.config = {"delegation": {"timeout_seconds": 5.0}}
        return mock

    @pytest.fixture
    def delegation_manager(self, mock_orchestrator):
        """Cria DelegationManager para testes."""
        return DelegationManager(mock_orchestrator, timeout_seconds=5.0)

    @pytest.mark.asyncio
    async def test_successful_delegation(self, delegation_manager, mock_orchestrator):
        """Testa delegação bem-sucedida."""

        async def task():
            await asyncio.sleep(0.1)
            return {"result": "success"}

        result = await delegation_manager.delegate_with_protection(
            agent_name="test_agent",
            task_description="Test task",
            task_callable=task,
            timeout_seconds=5.0,
        )

        assert result == {"result": "success"}
        assert len(delegation_manager.delegation_records) == 1
        assert delegation_manager.delegation_records[0].status == DelegationStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_delegation_timeout(self, delegation_manager):
        """Testa timeout de delegação."""

        async def slow_task():
            await asyncio.sleep(10.0)  # Mais longo que timeout
            return {"result": "slow"}

        with pytest.raises(asyncio.TimeoutError):
            await delegation_manager.delegate_with_protection(
                agent_name="slow_agent",
                task_description="Slow task",
                task_callable=slow_task,
                timeout_seconds=0.1,
                max_retries=1,
            )

        # Verificar registro
        records = delegation_manager.delegation_records
        assert any(r.status == DelegationStatus.TIMEOUT for r in records)

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self, delegation_manager):
        """Testa circuit breaker abrindo após falhas."""
        call_count = 0

        async def failing_task():
            nonlocal call_count
            call_count += 1
            raise ValueError("Task failed")

        # Tentar delegar 3x
        for i in range(3):
            try:
                await delegation_manager.delegate_with_protection(
                    agent_name="failing_agent",
                    task_description=f"Failing task {i}",
                    task_callable=failing_task,
                    timeout_seconds=5.0,
                    max_retries=1,
                )
            except ValueError:
                pass

        # Circuit breaker deve estar OPEN
        assert delegation_manager.circuit_breakers.get("failing_agent") == CircuitState.OPEN

        # Próxima delegação deve falhar imediatamente
        with pytest.raises(RuntimeError):
            await delegation_manager.delegate_with_protection(
                agent_name="failing_agent",
                task_description="Should fail before even trying",
                task_callable=failing_task,
                timeout_seconds=5.0,
            )

        # Contagem de chamadas deve ser 3 (não foi executado a 4ª)
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_logic(self, delegation_manager):
        """Testa retry automático."""
        call_count = 0

        async def flaky_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("Flaky failure")
            return {"result": "finally_success"}

        result = await delegation_manager.delegate_with_protection(
            agent_name="flaky_agent",
            task_description="Flaky task",
            task_callable=flaky_task,
            timeout_seconds=5.0,
            max_retries=3,
        )

        assert result == {"result": "finally_success"}
        assert call_count == 3
        assert delegation_manager.delegation_records[-1].retry_count == 2

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self, delegation_manager):
        """Testa recuperação do circuit breaker para HALF_OPEN."""
        call_count = 0

        async def recovering_task():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise RuntimeError("Initial failures")
            return {"result": "recovery"}

        # Causar 3 falhas para abrir circuit
        for i in range(3):
            try:
                await delegation_manager.delegate_with_protection(
                    agent_name="recovering_agent",
                    task_description=f"Failing {i}",
                    task_callable=recovering_task,
                    timeout_seconds=5.0,
                    max_retries=1,
                )
            except RuntimeError:
                pass

        assert delegation_manager.circuit_breakers["recovering_agent"] == CircuitState.OPEN

        # Resetar tempo de circuit (simular passagem de tempo)
        delegation_manager.circuit_reset_times["recovering_agent"] = (
            asyncio.get_event_loop().time() - 61.0
        )

        # Agora deve transicionar para HALF_OPEN
        result = await delegation_manager.delegate_with_protection(
            agent_name="recovering_agent",
            task_description="Recovery attempt",
            task_callable=recovering_task,
            timeout_seconds=5.0,
            max_retries=1,
        )

        assert result == {"result": "recovery"}
        assert delegation_manager.circuit_breakers["recovering_agent"] == CircuitState.CLOSED

    def test_metrics_tracking(self, delegation_manager):
        """Testa rastreamento de métricas."""
        record1 = DelegationRecord(
            id="del_001",
            agent_name="test_agent",
            task_description="Task 1",
            status=DelegationStatus.SUCCESS,
            duration_seconds=1.5,
        )
        record2 = DelegationRecord(
            id="del_002",
            agent_name="test_agent",
            task_description="Task 2",
            status=DelegationStatus.SUCCESS,
            duration_seconds=2.5,
        )
        record3 = DelegationRecord(
            id="del_003",
            agent_name="test_agent",
            task_description="Task 3",
            status=DelegationStatus.FAILED,
            error_message="Some error",
        )

        delegation_manager._update_metrics(record1)
        delegation_manager._update_metrics(record2)
        delegation_manager._update_metrics(record3)

        metrics = delegation_manager.get_metrics("test_agent")
        agent_metrics = metrics["test_agent"]

        assert agent_metrics.total_delegations == 3
        assert agent_metrics.successful_delegations == 2
        assert agent_metrics.failed_delegations == 1
        # Média deve ser (1.5 + 2.5) / 2 = 2.0
        assert agent_metrics.average_duration_seconds == 2.0

    def test_get_failed_delegations(self, delegation_manager):
        """Testa obtenção de delegações falhadas."""
        for i in range(5):
            status = DelegationStatus.FAILED if i % 2 == 0 else DelegationStatus.SUCCESS
            record = DelegationRecord(
                id=f"del_{i:03d}",
                agent_name=f"agent_{i}",
                task_description=f"Task {i}",
                status=status,
            )
            delegation_manager._record_delegation(record)

        failed = delegation_manager.get_failed_delegations()
        assert len(failed) == 3

    def test_record_delegation_persistence(self, delegation_manager, tmp_path):
        """Testa persistência de registros de delegação."""
        import os

        os.makedirs("logs", exist_ok=True)

        record = DelegationRecord(
            id="del_001",
            agent_name="test_agent",
            task_description="Test task",
            status=DelegationStatus.SUCCESS,
        )

        delegation_manager._record_delegation(record)

        # Verificar que arquivo foi criado
        assert os.path.exists("logs/delegations.jsonl")

        # Limpar
        if os.path.exists("logs/delegations.jsonl"):
            os.remove("logs/delegations.jsonl")


class TestHeartbeatMonitor:
    """Testes do HeartbeatMonitor."""

    @pytest.fixture
    def mock_orchestrator_with_registry(self):
        """Cria mock do OrchestratorAgent com AgentRegistry."""
        mock = MagicMock()
        mock.registry = MagicMock()
        mock.registry.health_check_all = AsyncMock(return_value={"agent1": True, "agent2": True})
        return mock

    @pytest.fixture
    def heartbeat_monitor(self, mock_orchestrator_with_registry):
        """Cria HeartbeatMonitor para testes."""
        return HeartbeatMonitor(mock_orchestrator_with_registry, check_interval_seconds=0.1)

    @pytest.mark.asyncio
    async def test_single_health_check(self, heartbeat_monitor, mock_orchestrator_with_registry):
        """Testa single health check."""
        await heartbeat_monitor._check_all_agents()

        health = heartbeat_monitor.agent_health
        assert health["agent1"] is True
        assert health["agent2"] is True

    @pytest.mark.asyncio
    async def test_health_status_reporting(self, heartbeat_monitor):
        """Testa relatório de status de saúde."""
        heartbeat_monitor.agent_health = {"agent1": True, "agent2": False}
        heartbeat_monitor.last_check_time = {"agent1": 123456.0, "agent2": 123456.0}

        status = await heartbeat_monitor.get_health_status()

        assert status["agent_health"]["agent1"] is True
        assert status["agent_health"]["agent2"] is False
        assert "agent1" in status["last_check_time"]
        assert "timestamp" in status

    def test_is_agent_healthy(self, heartbeat_monitor):
        """Testa verificação de saúde de agente."""
        heartbeat_monitor.agent_health = {"agent1": True, "agent2": False}

        assert heartbeat_monitor.is_agent_healthy("agent1") is True
        assert heartbeat_monitor.is_agent_healthy("agent2") is False
        assert heartbeat_monitor.is_agent_healthy("unknown") is True  # Default True

    @pytest.mark.asyncio
    async def test_monitoring_with_unhealthy_agent(self, mock_orchestrator_with_registry):
        """Testa monitoramento detectando agente não saudável."""
        mock_orchestrator_with_registry.registry.health_check_all = AsyncMock(
            return_value={"agent1": True, "agent2": False}
        )

        monitor = HeartbeatMonitor(mock_orchestrator_with_registry, check_interval_seconds=0.1)

        await monitor._check_all_agents()

        assert monitor.agent_health["agent1"] is True
        assert monitor.agent_health["agent2"] is False


class TestDelegationRecord:
    """Testes para DelegationRecord."""

    def test_record_creation(self):
        """Testa criação de record."""
        record = DelegationRecord(
            id="del_001",
            agent_name="test_agent",
            task_description="Test task",
        )

        assert record.id == "del_001"
        assert record.agent_name == "test_agent"
        assert record.status == DelegationStatus.PENDING
        assert record.created_at is not None

    def test_record_status_update(self):
        """Testa atualização de status."""
        record = DelegationRecord(
            id="del_001",
            agent_name="test_agent",
            task_description="Test task",
        )

        record.status = DelegationStatus.RUNNING
        assert record.status == DelegationStatus.RUNNING

        record.status = DelegationStatus.SUCCESS
        assert record.status == DelegationStatus.SUCCESS


class TestAgentMetrics:
    """Testes para AgentMetrics."""

    def test_metrics_creation(self):
        """Testa criação de métricas."""
        metrics = AgentMetrics(name="test_agent")

        assert metrics.name == "test_agent"
        assert metrics.total_delegations == 0
        assert metrics.successful_delegations == 0
        assert metrics.circuit_breaker_state == CircuitState.CLOSED

    def test_metrics_update(self):
        """Testa atualização de métricas."""
        metrics = AgentMetrics(name="test_agent")

        metrics.total_delegations = 10
        metrics.successful_delegations = 8
        metrics.failed_delegations = 2

        assert metrics.total_delegations == 10
        assert metrics.successful_delegations == 8
        assert metrics.failed_delegations == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

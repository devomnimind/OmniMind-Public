"""
Testes para IntrospectionLoop.

Testa sistema de observabilidade interna.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.orchestrator.introspection_loop import IntrospectionLoop


@pytest.fixture
def mock_orchestrator():
    """Cria mock do OrchestratorAgent."""
    orchestrator = MagicMock()
    orchestrator.agent_registry = MagicMock()
    orchestrator.agent_registry.health_check_all = AsyncMock(
        return_value={"security": True, "code": False}
    )
    orchestrator.metrics_summary = MagicMock(
        return_value={"total_operations": 100, "failed_operations": 5}
    )
    return orchestrator


@pytest.fixture
def introspection_loop(mock_orchestrator):
    """Cria instância de IntrospectionLoop."""
    return IntrospectionLoop(mock_orchestrator, interval=0.1)


@pytest.mark.asyncio
async def test_start_stop(introspection_loop):
    """Testa início e parada do loop."""
    await introspection_loop.start()

    assert introspection_loop.running is True

    await asyncio.sleep(0.2)  # Aguardar algumas iterações

    await introspection_loop.stop()

    assert introspection_loop.running is False


@pytest.mark.asyncio
async def test_collect_metrics(introspection_loop):
    """Testa coleta de métricas."""
    metrics = await introspection_loop._collect_metrics()

    assert metrics.timestamp > 0
    assert "component_health" in metrics.__dict__
    assert "resource_usage" in metrics.__dict__
    assert metrics.error_rate >= 0


@pytest.mark.asyncio
async def test_detect_anomalies(introspection_loop):
    """Testa detecção de anomalias."""
    from src.orchestrator.introspection_loop import IntrospectionMetrics

    # Métricas com componente não saudável
    metrics = IntrospectionMetrics(
        timestamp=0,
        component_health={"security": True, "code": False},
        resource_usage={"cpu": 0.5, "memory": 0.5, "disk": 0.5},
        error_rate=0.15,  # 15% de erro
    )

    anomalies = introspection_loop._detect_anomalies(metrics)

    assert len(anomalies) > 0
    assert any("não saudáveis" in anomaly for anomaly in anomalies)
    assert any("Taxa de erro alta" in anomaly for anomaly in anomalies)


@pytest.mark.asyncio
async def test_detect_anomalies_high_cpu(introspection_loop):
    """Testa detecção de anomalia de CPU alta."""
    from src.orchestrator.introspection_loop import IntrospectionMetrics

    metrics = IntrospectionMetrics(
        timestamp=0,
        component_health={"security": True},
        resource_usage={"cpu": 0.95, "memory": 0.5, "disk": 0.5},
        error_rate=0.05,
    )

    anomalies = introspection_loop._detect_anomalies(metrics)

    assert any("CPU" in anomaly for anomaly in anomalies)


@pytest.mark.asyncio
async def test_get_latest_metrics(introspection_loop):
    """Testa obtenção de métricas mais recentes."""
    await introspection_loop.start()
    await asyncio.sleep(0.15)  # Aguardar coleta
    await introspection_loop.stop()

    latest = introspection_loop.get_latest_metrics()

    assert latest is not None
    assert latest.timestamp > 0


def test_get_metrics_history(introspection_loop):
    """Testa obtenção de histórico de métricas."""
    from src.orchestrator.introspection_loop import IntrospectionMetrics
    import time

    # Adicionar métricas simuladas
    for i in range(5):
        introspection_loop.metrics_history.append(
            IntrospectionMetrics(
                timestamp=time.time() + i,
                component_health={},
                resource_usage={},
                error_rate=0.0,
            )
        )

    history = introspection_loop.get_metrics_history(limit=3)

    assert len(history) == 3


def test_get_introspection_summary(introspection_loop):
    """Testa obtenção de resumo de introspecção."""
    summary = introspection_loop.get_introspection_summary()

    assert "running" in summary
    assert "interval" in summary
    assert "total_metrics_collected" in summary

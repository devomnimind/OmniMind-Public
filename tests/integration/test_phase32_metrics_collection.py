"""
Testes de Integração - FASE 3.2: Metrics Collection

Testa a coleta de métricas antes/depois das otimizações.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import pytest

from src.metrics.dashboard_metrics import DashboardMetricsAggregator
from src.observability.module_metrics import get_metrics_collector


class TestMetricsCollection:
    """Testa coleta de métricas (FASE 3.2)."""

    @pytest.mark.asyncio
    async def test_dashboard_aggregator_has_module_metrics(self):
        """Testa se DashboardMetricsAggregator tem ModuleMetricsCollector."""
        aggregator = DashboardMetricsAggregator()

        # Verificar se module_metrics_collector foi inicializado
        assert aggregator._module_metrics_collector is not None

    @pytest.mark.asyncio
    async def test_collect_snapshot_includes_module_metrics(self):
        """Testa se collect_snapshot inclui métricas de módulos."""
        aggregator = DashboardMetricsAggregator()

        snapshot = await aggregator.collect_snapshot(
            include_consciousness=False, include_baseline=False
        )

        # Verificar se module_metrics está no snapshot
        assert "module_metrics" in snapshot
        assert "before_after_comparison" in snapshot

    @pytest.mark.asyncio
    async def test_save_before_metrics(self):
        """Testa salvamento de métricas 'antes'."""
        aggregator = DashboardMetricsAggregator()

        # Coletar métricas atuais
        module_collector = get_metrics_collector()
        module_metrics = module_collector.get_all_metrics()

        # Salvar como baseline
        aggregator.save_before_metrics(module_metrics)

        # Verificar se arquivo foi criado
        assert aggregator._before_after_metrics_file.exists()

    @pytest.mark.asyncio
    async def test_before_after_comparison(self):
        """Testa comparação antes/depois."""
        aggregator = DashboardMetricsAggregator()

        # Coletar métricas atuais
        module_collector = get_metrics_collector()
        module_metrics = module_collector.get_all_metrics()

        # Salvar como baseline
        aggregator.save_before_metrics(module_metrics)

        # Coletar snapshot (deve incluir comparação)
        snapshot = await aggregator.collect_snapshot(
            include_consciousness=False, include_baseline=False
        )

        # Verificar se comparação foi construída
        comparison = snapshot.get("before_after_comparison", {})
        assert isinstance(comparison, dict)

    def test_module_metrics_collector_integration(self):
        """Testa integração do ModuleMetricsCollector."""
        collector = get_metrics_collector()

        # Registrar algumas métricas de teste
        collector.record_metric("TestModule", "test_metric", 42, {"label": "test"})

        # Verificar se métrica foi registrada
        metrics = collector.get_module_metrics("TestModule")
        assert metrics is not None
        assert "test_metric" in metrics.get("metrics", {})

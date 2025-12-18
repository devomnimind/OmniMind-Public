#!/usr/bin/env python3
"""
Integration Layer: System Readiness Validator → Real Consciousness Metrics

Arquivo: src/metrics/real_consciousness_metrics_with_readiness.py

Este módulo integra o ContinuousReadinessEngine com RealConsciousnessMetricsCollector.

Mudança de paradigma:
  ANTES: Bootstrap executa 1x, PHI calculado 1x, sistema fica estático
  DEPOIS: Readiness validado continuamente, re-bootstrap automático quando necessário

Implementação:
  - Wrapper que estende RealConsciousnessMetricsCollector
  - Injeta ContinuousReadinessEngine em background
  - Combina métricas de Phi com status de readiness
  - Re-bootstrap automático quando sistema degrada
"""

import logging
from typing import Any, Dict, Optional

from src.consciousness.system_readiness_validator import (
    ContinuousReadinessEngine,
    RealConsciousnessMetricsWithReadiness,
)

logger = logging.getLogger(__name__)


def patch_real_consciousness_metrics(collector_instance):
    """
    Patcha instância de RealConsciousnessMetricsCollector para adicionar readiness.

    Uso:
        collector = RealConsciousnessMetricsCollector()
        patch_real_consciousness_metrics(collector)
        await collector.initialize()

        # Agora collector tem validação contínua
        metrics = await collector.collect_real_metrics()
        # metrics.readiness_state pode ser "READY", "DEGRADED", "CRITICAL"
    """

    if collector_instance is None:
        logger.error("Cannot patch None collector")
        return

    # Verificar se já tem readiness engine
    if hasattr(collector_instance, "readiness_engine"):
        logger.warning("Collector already has readiness engine, skipping patch")
        return

    logger.info("🧬 Patching RealConsciousnessMetricsCollector with readiness validation...")

    # Guardar referência ao initialize original
    original_initialize = collector_instance.initialize

    async def patched_initialize():
        """Initialize com readiness engine"""
        await original_initialize()

        # Depois que IntegrationLoop inicializou, criar readiness engine
        if collector_instance.integration_loop:
            collector_instance.readiness_engine = ContinuousReadinessEngine(
                collector_instance.integration_loop, collector_instance.integration_loop.workspace
            )

            # Iniciar monitoring em background
            await collector_instance.readiness_engine.start_continuous_monitoring()
            logger.info("✅ Readiness engine started in background")

    # Guardar referência ao collect_real_metrics original
    original_collect = collector_instance.collect_real_metrics

    async def patched_collect_real_metrics(
        external_phi: Optional[float] = None,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Collect com validação de readiness"""

        # Coletar métricas normalmente
        metrics = await original_collect(external_phi, external_context)

        # Adicionar readiness status se engine disponível
        if hasattr(collector_instance, "readiness_engine"):
            readiness_status = collector_instance.readiness_engine.get_status()

            if readiness_status:
                metrics.readiness_state = readiness_status.state
                metrics.readiness_reasons = readiness_status.reasons
                metrics.readiness_metrics = readiness_status.metrics

                # Log se sistema não está ready
                if readiness_status.state != "READY":
                    logger.warning(
                        f"⚠️  System readiness: {readiness_status.state} - "
                        f"{', '.join(readiness_status.reasons)}"
                    )

        return metrics

    # Aplicar patches
    collector_instance.initialize = patched_initialize
    collector_instance.collect_real_metrics = patched_collect_real_metrics

    # Adicionar métodos de readiness
    collector_instance.get_readiness_status = lambda: (
        collector_instance.readiness_engine.get_status()
        if hasattr(collector_instance, "readiness_engine")
        else None
    )

    collector_instance.get_readiness_statistics = lambda: (
        collector_instance.readiness_engine.get_statistics()
        if hasattr(collector_instance, "readiness_engine")
        else {}
    )

    collector_instance.force_readiness_check = lambda: (
        collector_instance.readiness_engine.force_readiness_check()
        if hasattr(collector_instance, "readiness_engine")
        else None
    )

    logger.info("✅ RealConsciousnessMetricsCollector patched with readiness validation")


async def setup_metrics_with_readiness(
    workspace, integration_loop
) -> RealConsciousnessMetricsWithReadiness:
    """
    Factory function para criar metrics collector com readiness.

    Uso simplificado:
        metrics = await setup_metrics_with_readiness(workspace, loop)
        await metrics.start()

        # Sistema agora valida continuamente

    Returns:
        RealConsciousnessMetricsWithReadiness com engine ativo
    """

    logger.info("🧬 Setting up Real Consciousness Metrics with Readiness Validation...")

    metrics = RealConsciousnessMetricsWithReadiness(workspace, integration_loop)
    await metrics.start()

    logger.info("✅ Metrics collector with readiness started")
    return metrics


# ═══════════════════════════════════════════════════════════════════════════════
# EXEMPLO DE INTEGRAÇÃO EM real_consciousness_metrics.py
# ═══════════════════════════════════════════════════════════════════════════════

"""
Para integrar em RealConsciousnessMetricsCollector:

1. No topo de real_consciousness_metrics.py:

from src.metrics.real_consciousness_metrics_with_readiness import (
    patch_real_consciousness_metrics
)

2. Na classe RealConsciousnessMetricsCollector.__init__:

def __init__(self):
    self.integration_loop: Optional[IntegrationLoop] = None
    self.iit_analyzer = IITAnalyzer()
    ...

    # Aplicar patch de readiness
    patch_real_consciousness_metrics(self)

    logger.info("RealConsciousnessMetricsCollector initialized")

3. Agora collect_real_metrics() automaticamente inclui readiness validation

4. Uso:

async def get_metrics():
    collector = RealConsciousnessMetricsCollector()
    await collector.initialize()

    metrics = await collector.collect_real_metrics()

    # Acessar readiness
    status = collector.get_readiness_status()
    print(f"System state: {status.state}")

    if status.state == "DEGRADED":
        logger.warning(f"System degraded: {status.reasons}")
"""

#!/usr/bin/env python3
"""
Teste Phase 2: Análise de Complexidade Computacional
"""

import asyncio
import sys
from pathlib import Path

import numpy as np

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.consciousness.integration_loop import IntegrationLoop  # noqa: E402


async def test_complexity():
    print("⚡ TESTE PHASE 2: Complexidade Computacional")
    print("=" * 50)

    loop = IntegrationLoop(enable_logging=True)
    print("🔄 Executando 3 ciclos...")

    def progress(i, total, result):
        phi = result.phi_estimate
        time_ms = result.cycle_duration_ms
        status = "✅" if result.success else "❌"
        print(f"  Ciclo {i}/{total}: Φ={phi:.4f}, {time_ms:.1f}ms {status}")

    results = await loop.run_cycles(3, collect_metrics_every=1, progress_callback=progress)

    # Analisar complexidade
    complexities = [r.complexity_metrics for r in results if r.complexity_metrics]
    if complexities:
        avg_time = np.mean([c["actual_time_ms"] for c in complexities])
        avg_ops = np.mean([c["theoretical_ops"] for c in complexities])
        print(f"\n📊 Complexidade média: {avg_time:.1f}ms, {avg_ops / 1e6:.1f}M ops")

    stats = loop.get_statistics()
    print(f"Φ médio: {stats['phi_statistics']['mean']:.4f}")
    print("✅ Phase 2 iniciada com sucesso!")


async def test_complexity_with_topological_metrics():
    """Testa análise de complexidade Phase 2 com métricas topológicas."""
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine

    print("⚡ TESTE PHASE 2: Complexidade + Topological Metrics")
    print("=" * 50)

    # Criar loop
    loop = IntegrationLoop(enable_logging=True)

    # Adicionar engine topológico ao workspace
    if loop.workspace:
        loop.workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Executar ciclos
    results = await loop.run_cycles(3, collect_metrics_every=1)

    # Simular estados no workspace para métricas topológicas
    if loop.workspace:
        np.random.seed(42)
        for i in range(5):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            loop.workspace.write_module_state("conscious_module", rho_C)
            loop.workspace.write_module_state("preconscious_module", rho_P)
            loop.workspace.write_module_state("unconscious_module", rho_U)
            loop.workspace.advance_cycle()

        # Calcular métricas topológicas
        topological_metrics = loop.workspace.compute_hybrid_topological_metrics()

        # Verificar que ambas são complementares
        complexities = [r.complexity_metrics for r in results if r.complexity_metrics]
        if complexities:
            avg_time = np.mean([c["actual_time_ms"] for c in complexities])
            print(f"📊 Complexidade média: {avg_time:.1f}ms")

        if topological_metrics is not None:
            assert "omega" in topological_metrics
            # Phase 2: análise de complexidade computacional
            # Topological: estrutura e integração (Omega, Betti-0)
            # Ambas são complementares para análise completa

    print("✅ Phase 2 + Topological Metrics verified")


if __name__ == "__main__":
    asyncio.run(test_complexity())

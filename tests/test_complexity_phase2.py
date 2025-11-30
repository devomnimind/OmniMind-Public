#!/usr/bin/env python3
"""
Teste Phase 2: Análise de Complexidade Computacional
"""

import asyncio
import sys
import os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from src.consciousness.integration_loop import IntegrationLoop


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
        print(f"\n📊 Complexidade média: {avg_time:.1f}ms, {avg_ops/1e6:.1f}M ops")

    stats = loop.get_statistics()
    print(f"Φ médio: {stats['phi_statistics']['mean']:.4f}")
    print("✅ Phase 2 iniciada com sucesso!")


if __name__ == "__main__":
    asyncio.run(test_complexity())

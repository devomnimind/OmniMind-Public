#!/usr/bin/env python3
"""
Debug script para entender por que Φ está retornando 0.0
"""

import asyncio
import json

from src.consciousness.integration_loop import IntegrationLoop
from src.metrics.real_consciousness_metrics import collect_real_metrics


async def debug_metrics():
    print("\n" + "=" * 60)
    print("DEBUG: Consciousness Metrics Collection")
    print("=" * 60)

    # 1. Coletar métricas reais
    print("\n1️⃣  Coletando métricas reais...")
    metrics = await collect_real_metrics()
    print(json.dumps(metrics, indent=2, default=str))

    # 2. Debugar IntegrationLoop
    print("\n2️⃣  Debugando IntegrationLoop...")
    loop = IntegrationLoop(enable_logging=True)
    print(f"   - Workspace exists: {loop.workspace is not None}")
    print(f"   - Workspace cycle_count: {loop.workspace.cycle_count}")
    print(f"   - Workspace modules: {len(loop.workspace.get_all_modules())}")
    print(f"   - Cross-predictions: {len(loop.workspace.cross_predictions)}")

    # 3. Executar alguns ciclos
    print("\n3️⃣  Executando ciclos de integração...")
    results = await loop.run_cycles(3, collect_metrics_every=1)
    for i, result in enumerate(results):
        print(f"   - Ciclo {i+1}: phi={result.phi_estimate:.4f}, errors={result.errors_occurred}")

    # 4. Verificar dados após ciclos
    print("\n4️⃣  Estado após ciclos...")
    print(f"   - Workspace cycle_count: {loop.workspace.cycle_count}")
    print(f"   - Cross-predictions agora: {len(loop.workspace.cross_predictions)}")
    print(
        f"   - Compute phi from integrations: {loop.workspace.compute_phi_from_integrations():.4f}"
    )

    # 5. Coletar métricas novamente
    print("\n5️⃣  Coletando métricas reais novamente...")
    metrics2 = await collect_real_metrics()
    print(f"   - Phi: {metrics2['phi']:.4f}")
    print(f"   - ICI: {metrics2['ici']:.4f}")
    print(f"   - PRS: {metrics2['prs']:.4f}")
    print(f"   - Anxiety: {metrics2['anxiety']:.4f}")
    print(f"   - Flow: {metrics2['flow']:.4f}")
    print(f"   - Entropy: {metrics2['entropy']:.4f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(debug_metrics())
    asyncio.run(debug_metrics())

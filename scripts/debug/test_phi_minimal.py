#!/usr/bin/env python3
"""
Teste mínimo: 5 ciclos para validar se phi calcula sem erros de dimensão.
"""
import asyncio
import logging
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(message)s",
)

from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace


async def test():
    print("\n=== TESTE MÍNIMO: 5 ciclos ===\n")

    ws = SharedWorkspace(embedding_dim=256, max_history_size=100)
    loop = IntegrationLoop(shared_workspace=ws, enable_extended_results=True)

    for i in range(1, 6):
        try:
            result = await loop.execute_cycle(collect_metrics=True)
            print(f"✓ Ciclo {i}: phi={result.phi_estimate:.4f}")
        except Exception as e:
            print(f"✗ Ciclo {i}: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            return False

    print("\n✅ Todos os ciclos completados\n")
    return True


if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)

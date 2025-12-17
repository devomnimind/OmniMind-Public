#!/usr/bin/env python3
"""
Teste Isolado: Phase 5 (Bion) e Phase 6 (Lacan)

Executa módulos isoladamente e em grupos lógicos para investigar integração.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.consciousness.integration_loop import IntegrationLoop


async def test_phase5_isolated() -> Dict[str, Any]:
    """Testa Phase 5 (Bion) isoladamente."""
    print("\n" + "=" * 80)
    print("🔬 TESTE 1: Phase 5 (Bion Alpha Function) - ISOLADO")
    print("=" * 80)

    loop = IntegrationLoop(enable_logging=True, enable_extended_results=False)
    results = []

    for cycle in range(1, 11):  # 10 ciclos
        result = loop.execute_cycle_sync(collect_metrics=True)

        # Verificar se Bion processou
        sensory_history = loop.workspace.get_module_history("sensory_input", last_n=1)
        bion_processed = False
        metadata_info = {}

        if sensory_history:
            metadata = sensory_history[0].metadata or {}
            bion_processed = metadata.get("processed_by") == "bion_alpha_function"
            if bion_processed:
                metadata_info = {
                    "symbolic_potential": metadata.get("symbolic_potential"),
                    "narrative_form_length": len(metadata.get("narrative_form", "")),
                    "beta_emotional_charge": metadata.get("beta_emotional_charge"),
                }

        results.append({
            "cycle": cycle,
            "phi": result.phi_estimate if hasattr(result, "phi_estimate") else 0.0,
            "bion_processed": bion_processed,
            "metadata": metadata_info,
            "modules_executed": result.modules_executed,
        })

        if cycle % 5 == 0:
            print(f"  ✅ Ciclo {cycle}/10 concluído")

    bion_count = sum(1 for r in results if r["bion_processed"])
    phi_avg = sum(r["phi"] for r in results) / len(results)

    print(f"\n📊 Resultados:")
    print(f"   Bion processou: {bion_count}/10 ciclos ({bion_count*10}%)")
    print(f"   Φ médio: {phi_avg:.6f} NATS")

    return {
        "test": "phase5_isolated",
        "cycles": 10,
        "bion_processed_count": bion_count,
        "bion_processed_percent": bion_count * 10,
        "phi_avg": phi_avg,
        "results": results,
    }


async def test_phase6_isolated() -> Dict[str, Any]:
    """Testa Phase 6 (Lacan) isoladamente."""
    print("\n" + "=" * 80)
    print("🔬 TESTE 2: Phase 6 (Lacan Discourse Analyzer) - ISOLADO")
    print("=" * 80)

    loop = IntegrationLoop(enable_logging=True, enable_extended_results=False)
    results = []

    for cycle in range(1, 11):  # 10 ciclos
        result = loop.execute_cycle_sync(collect_metrics=True)

        # Verificar se Lacan processou
        narrative_history = loop.workspace.get_module_history("narrative", last_n=1)
        lacan_processed = False
        discourse_info = {}

        if narrative_history:
            metadata = narrative_history[0].metadata or {}
            lacan_processed = metadata.get("processed_by") == "lacanian_discourse_analyzer"
            if lacan_processed:
                discourse_info = {
                    "dominant_discourse": metadata.get("lacanian_discourse"),
                    "discourse_confidence": metadata.get("discourse_confidence"),
                    "emotional_signature": metadata.get("emotional_signature"),
                }

        results.append({
            "cycle": cycle,
            "phi": result.phi_estimate if hasattr(result, "phi_estimate") else 0.0,
            "lacan_processed": lacan_processed,
            "discourse": discourse_info,
            "modules_executed": result.modules_executed,
        })

        if cycle % 5 == 0:
            print(f"  ✅ Ciclo {cycle}/10 concluído")

    lacan_count = sum(1 for r in results if r["lacan_processed"])
    phi_avg = sum(r["phi"] for r in results) / len(results)

    print(f"\n📊 Resultados:")
    print(f"   Lacan processou: {lacan_count}/10 ciclos ({lacan_count*10}%)")
    print(f"   Φ médio: {phi_avg:.6f} NATS")

    return {
        "test": "phase6_isolated",
        "cycles": 10,
        "lacan_processed_count": lacan_count,
        "lacan_processed_percent": lacan_count * 10,
        "phi_avg": phi_avg,
        "results": results,
    }


async def test_phase5_6_combined() -> Dict[str, Any]:
    """Testa Phase 5 e Phase 6 combinadas."""
    print("\n" + "=" * 80)
    print("🔬 TESTE 3: Phase 5 + Phase 6 - COMBINADAS")
    print("=" * 80)

    loop = IntegrationLoop(enable_logging=True, enable_extended_results=False)
    results = []

    for cycle in range(1, 11):  # 10 ciclos
        result = loop.execute_cycle_sync(collect_metrics=True)

        # Verificar ambos
        sensory_history = loop.workspace.get_module_history("sensory_input", last_n=1)
        narrative_history = loop.workspace.get_module_history("narrative", last_n=1)

        bion_processed = False
        lacan_processed = False

        if sensory_history:
            metadata = sensory_history[0].metadata or {}
            bion_processed = metadata.get("processed_by") == "bion_alpha_function"

        if narrative_history:
            metadata = narrative_history[0].metadata or {}
            lacan_processed = metadata.get("processed_by") == "lacanian_discourse_analyzer"

        results.append({
            "cycle": cycle,
            "phi": result.phi_estimate if hasattr(result, "phi_estimate") else 0.0,
            "bion_processed": bion_processed,
            "lacan_processed": lacan_processed,
            "modules_executed": result.modules_executed,
        })

        if cycle % 5 == 0:
            print(f"  ✅ Ciclo {cycle}/10 concluído")

    bion_count = sum(1 for r in results if r["bion_processed"])
    lacan_count = sum(1 for r in results if r["lacan_processed"])
    phi_avg = sum(r["phi"] for r in results) / len(results)

    print(f"\n📊 Resultados:")
    print(f"   Bion processou: {bion_count}/10 ciclos ({bion_count*10}%)")
    print(f"   Lacan processou: {lacan_count}/10 ciclos ({lacan_count*10}%)")
    print(f"   Φ médio: {phi_avg:.6f} NATS")

    return {
        "test": "phase5_6_combined",
        "cycles": 10,
        "bion_processed_count": bion_count,
        "lacan_processed_count": lacan_count,
        "phi_avg": phi_avg,
        "results": results,
    }


async def test_full_system() -> Dict[str, Any]:
    """Testa sistema completo (como na validação científica)."""
    print("\n" + "=" * 80)
    print("🔬 TESTE 4: Sistema Completo (50 ciclos)")
    print("=" * 80)

    loop = IntegrationLoop(enable_logging=False, enable_extended_results=False)
    results = []

    for cycle in range(1, 51):  # 50 ciclos
        result = loop.execute_cycle_sync(collect_metrics=True)

        # Verificar ambos
        sensory_history = loop.workspace.get_module_history("sensory_input", last_n=1)
        narrative_history = loop.workspace.get_module_history("narrative", last_n=1)

        bion_processed = False
        lacan_processed = False

        if sensory_history:
            metadata = sensory_history[0].metadata or {}
            bion_processed = metadata.get("processed_by") == "bion_alpha_function"

        if narrative_history:
            metadata = narrative_history[0].metadata or {}
            lacan_processed = metadata.get("processed_by") == "lacanian_discourse_analyzer"

        results.append({
            "cycle": cycle,
            "phi": result.phi_estimate if hasattr(result, "phi_estimate") else 0.0,
            "bion_processed": bion_processed,
            "lacan_processed": lacan_processed,
        })

        if cycle % 10 == 0:
            print(f"  ✅ Ciclo {cycle}/50 concluído")

    bion_count = sum(1 for r in results if r["bion_processed"])
    lacan_count = sum(1 for r in results if r["lacan_processed"])
    phi_values = [r["phi"] for r in results if r["phi"] > 0]
    phi_avg = sum(phi_values) / len(phi_values) if phi_values else 0.0

    print(f"\n📊 Resultados:")
    print(f"   Bion processou: {bion_count}/50 ciclos ({bion_count*2}%)")
    print(f"   Lacan processou: {lacan_count}/50 ciclos ({lacan_count*2}%)")
    print(f"   Φ médio (ciclos > 0): {phi_avg:.6f} NATS")
    print(f"   Ciclos com Φ > 0: {len(phi_values)}/50")

    return {
        "test": "full_system",
        "cycles": 50,
        "bion_processed_count": bion_count,
        "lacan_processed_count": lacan_count,
        "phi_avg": phi_avg,
        "cycles_with_phi": len(phi_values),
        "results": results[:10],  # Apenas primeiros 10 para não ficar muito grande
    }


async def main():
    """Executa todos os testes."""
    print("=" * 80)
    print("🔬 INVESTIGAÇÃO: Phase 5 & 6 - Testes Isolados e em Grupos")
    print("=" * 80)

    all_results = {}

    # Teste 1: Phase 5 isolado
    try:
        result1 = await test_phase5_isolated()
        all_results["phase5_isolated"] = result1
    except Exception as e:
        logger.error(f"Erro no teste Phase 5 isolado: {e}", exc_info=True)
        all_results["phase5_isolated"] = {"error": str(e)}

    # Teste 2: Phase 6 isolado
    try:
        result2 = await test_phase6_isolated()
        all_results["phase6_isolated"] = result2
    except Exception as e:
        logger.error(f"Erro no teste Phase 6 isolado: {e}", exc_info=True)
        all_results["phase6_isolated"] = {"error": str(e)}

    # Teste 3: Phase 5 + 6 combinadas
    try:
        result3 = await test_phase5_6_combined()
        all_results["phase5_6_combined"] = result3
    except Exception as e:
        logger.error(f"Erro no teste Phase 5+6 combinadas: {e}", exc_info=True)
        all_results["phase5_6_combined"] = {"error": str(e)}

    # Teste 4: Sistema completo
    try:
        result4 = await test_full_system()
        all_results["full_system"] = result4
    except Exception as e:
        logger.error(f"Erro no teste sistema completo: {e}", exc_info=True)
        all_results["full_system"] = {"error": str(e)}

    # Salvar resultados
    output_file = Path("data/monitor/phase5_6_investigation_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "tests": all_results,
        }, f, indent=2)

    print("\n" + "=" * 80)
    print("📊 RESUMO FINAL")
    print("=" * 80)

    for test_name, result in all_results.items():
        if "error" in result:
            print(f"❌ {test_name}: ERRO - {result['error']}")
        else:
            if "bion_processed_count" in result:
                print(f"✅ {test_name}: Bion={result['bion_processed_count']}/{result.get('cycles', 0)} ciclos")
            if "lacan_processed_count" in result:
                print(f"✅ {test_name}: Lacan={result['lacan_processed_count']}/{result.get('cycles', 0)} ciclos")
            if "phi_avg" in result:
                print(f"   Φ médio: {result['phi_avg']:.6f} NATS")

    print(f"\n📄 Resultados salvos em: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())


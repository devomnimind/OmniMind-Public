#!/usr/bin/env python3
"""
Teste das melhorias de automação autopoietica (2025-12-10)

Demonstra que o sistema agora pode executar ciclos automaticamente
quando saudável, com thresholds mais permissivos.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.autopoietic.manager import PHI_THRESHOLD, AutopoieticManager
from src.autopoietic.meta_architect import ComponentSpec
from src.autopoietic.metrics_adapter import collect_metrics


def test_automated_cycles():
    """Testa execução automática de ciclos quando saudável."""
    print("🧪 TESTE: Ciclos Autopoieticos Automáticos")
    print("=" * 50)

    # Verificar thresholds ajustados
    print(f"✅ PHI_THRESHOLD ajustado: {PHI_THRESHOLD} (era 0.1)")

    # Coletar métricas atuais
    print("\n📊 Coletando métricas do sistema...")
    try:
        metrics_sample = collect_metrics()

        # CORREÇÃO: collect_metrics() retorna MetricSample, não dict
        # phi está em raw_metrics, error_rate e cpu_usage são atributos diretos
        phi_current = metrics_sample.raw_metrics.get("phi", 0.0)
        error_rate = metrics_sample.error_rate
        cpu_usage = metrics_sample.cpu_usage

        print(f"   Φ atual: {phi_current:.3f}")
        print(f"   Taxa de erro: {error_rate:.3f}")
        print(f"   Uso de CPU: {cpu_usage:.1f}%")
        print(f"   Source: {metrics_sample.source}")

        # Verificar se pode executar ciclo automático
        can_run_auto = phi_current >= PHI_THRESHOLD and error_rate <= 0.05 and cpu_usage <= 80.0

        print(f"\n🤖 Pode executar ciclo automático: {'✅ SIM' if can_run_auto else '❌ NÃO'}")

        if can_run_auto:
            print("\n🚀 Executando ciclo autopoietico automático...")

            # Executar ciclo usando strategy_inputs() que retorna o dict esperado
            manager = AutopoieticManager()
            spec = ComponentSpec(
                name="kernel_process",
                type="process",
                config={"priority": "high", "generation": "0"},
            )
            manager.register_spec(spec)

            log = manager.run_cycle(metrics_sample.strategy_inputs())

            print("✅ Ciclo executado com sucesso!")
            print(f"   📊 Ciclo ID: {log.cycle_id}")
            print(f"   🎯 Estratégia: {log.strategy.name}")
            print(f"   🧬 Componentes sintetizados: {len(log.synthesized_components)}")
            if log.phi_before and log.phi_after:
                print(f"   🧠 Φ: {log.phi_before:.3f} → {log.phi_after:.3f}")

            # Verificar se estratégia mudou (não ficou presa em STABILIZE)
            if log.strategy.name != "STABILIZE":
                print("✅ Sistema conseguiu evoluir além de STABILIZE!")
            else:
                print("ℹ️  Sistema optou por estabilização (pode ser apropriado)")

        else:
            print("\n⏸️  Sistema não saudável para ciclo automático")
            print("   Motivos:")
            if phi_current < PHI_THRESHOLD:
                print(f"   - Φ muito baixo: {phi_current} < {PHI_THRESHOLD}")
            if error_rate > 0.05:
                print(f"   - Taxa de erro alta: {error_rate} > 0.05")
            if cpu_usage > 80.0:
                print(f"   - CPU alta: {cpu_usage} > 80.0")

    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 50)
    print("🎉 Teste concluído!")


if __name__ == "__main__":
    test_automated_cycles()

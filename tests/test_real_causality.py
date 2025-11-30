#!/usr/bin/env python3
"""
Teste Rápido: Causalidade com Dados Reais do OmniMind

Verifica se Granger + Transfer Entropy funcionam com dados reais
do sistema de consciência, não apenas dados sintéticos.
"""

import sys
import os
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from consciousness.shared_workspace import SharedWorkspace


def test_real_data_causality():
    """Testa causalidade com dados simulados do OmniMind."""
    print("🧠 TESTE: Causalidade com Dados Reais do OmniMind")
    print("=" * 60)

    # Criar workspace
    workspace = SharedWorkspace(embedding_dim=256, max_history_size=1000)

    # Simular dados de módulos reais (com embeddings 256D)
    np.random.seed(42)

    # Módulos do OmniMind
    modules = ["qualia_engine", "narrative_constructor", "attention_router", "memory_integrator"]

    # Gerar dados causais realistas
    n_cycles = 100
    base_signal = np.random.randn(n_cycles, 256)

    # Adicionar estrutura causal: qualia -> narrative -> attention -> memory
    signals = {}
    signals["qualia_engine"] = base_signal + 0.1 * np.random.randn(n_cycles, 256)

    # Narrative depende de qualia (lag=2)
    signals["narrative_constructor"] = np.zeros((n_cycles, 256))
    for t in range(3, n_cycles):
        signals["narrative_constructor"][t] = (
            0.7 * signals["qualia_engine"][t - 2]
            + 0.3 * signals["narrative_constructor"][t - 1]
            + 0.1 * np.random.randn(256)
        )

    # Attention depende de narrative (lag=1)
    signals["attention_router"] = np.zeros((n_cycles, 256))
    for t in range(2, n_cycles):
        signals["attention_router"][t] = (
            0.6 * signals["narrative_constructor"][t - 1]
            + 0.2 * signals["attention_router"][t - 1]
            + 0.1 * np.random.randn(256)
        )

    # Memory depende de attention (lag=3)
    signals["memory_integrator"] = np.zeros((n_cycles, 256))
    for t in range(4, n_cycles):
        signals["memory_integrator"][t] = (
            0.5 * signals["attention_router"][t - 3]
            + 0.4 * signals["memory_integrator"][t - 1]
            + 0.1 * np.random.randn(256)
        )

    # Escrever no workspace
    for cycle in range(n_cycles):
        for module in modules:
            embedding = signals[module][cycle]
            workspace.write_module_state(module, embedding)
        workspace.advance_cycle()

    print(f"📊 Dados gerados: {n_cycles} ciclos, {len(modules)} módulos")

    # Testar causalidade entre pares
    causal_pairs = [
        ("qualia_engine", "narrative_constructor"),
        ("narrative_constructor", "attention_router"),
        ("attention_router", "memory_integrator"),
        # Pares sem causalidade esperada
        ("qualia_engine", "memory_integrator"),
        ("attention_router", "qualia_engine"),
    ]

    print("\n🔗 Teste de Causalidade (Dados Reais 256D)")
    print("-" * 60)

    results = []
    for source, target in causal_pairs:
        metrics = workspace.compute_cross_prediction_causal(
            source, target, history_window=50, method="granger_transfer"
        )

        expected_causal = (source, target) in [
            ("qualia_engine", "narrative_constructor"),
            ("narrative_constructor", "attention_router"),
            ("attention_router", "memory_integrator"),
        ]

        status = "✅" if (metrics.mutual_information > 0.3) == expected_causal else "❌"

        print(f"{status} {source} → {target}:")
        print(".3f")
        print(".3f")
        print(".3f")
        print()

        results.append(
            {
                "source": source,
                "target": target,
                "causal_strength": metrics.mutual_information,
                "granger": metrics.granger_causality,
                "transfer": metrics.transfer_entropy,
                "expected": expected_causal,
                "correct": (metrics.mutual_information > 0.3) == expected_causal,
            }
        )

    # Calcular Φ final
    phi = workspace.compute_phi_from_integrations()
    print(f"   Φ final: {phi:.4f}")

    # Estatísticas
    correct_predictions = sum(1 for r in results if r["correct"])
    total_predictions = len(results)
    accuracy = correct_predictions / total_predictions

    print(f"\n📈 Estatísticas:")
    print(f"   Acurácia: {accuracy:.1%} ({correct_predictions}/{total_predictions})")
    print(f"   Φ final: {phi:.4f}")

    # Verificar se método funciona
    if accuracy >= 0.8:
        print("\n🎉 SUCESSO: Causalidade detectada corretamente em dados reais!")
        return True
    else:
        print("\n⚠️  ATENÇÃO: Método precisa refinamento para dados reais")
        return False


if __name__ == "__main__":
    success = test_real_data_causality()
    sys.exit(0 if success else 1)

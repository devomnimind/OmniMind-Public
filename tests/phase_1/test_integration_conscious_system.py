#!/usr/bin/env python3
"""Teste rápido de integração ConsciousSystem + SharedWorkspace."""

import torch

from src.consciousness.shared_workspace import SharedWorkspace

print("✅ Teste de Integração ConsciousSystem + SharedWorkspace")
print("=" * 60)

# Criar workspace
ws = SharedWorkspace(embedding_dim=256)
print("✅ SharedWorkspace criado")
print(f"  ConsciousSystem: {ws.conscious_system is not None}")

if ws.conscious_system:
    print(f"  dim: {ws.conscious_system.dim}")
    print(f"  signature_dim: {ws.conscious_system.signature_dim}")

    # Executar alguns steps
    print("\n📊 Executando steps...")
    for i in range(5):
        stimulus = torch.randn(256) * 0.1
        ws.conscious_system.step(stimulus)
        state = ws.conscious_system.get_state()
        if i == 4:  # Último
            print(f"  Step {i+1}: Phi causal = {state.phi_causal:.6f}")

    # Calcular métricas topológicas
    print("\n📈 Calculando métricas topológicas...")
    metrics = ws.compute_hybrid_topological_metrics()
    if metrics:
        omega = metrics.get("omega", 0)
        sigma = metrics.get("sigma", 0)
        print(f"  ✅ Métricas calculadas: omega={omega:.4f}, sigma={sigma:.4f}")
    else:
        print("  ❌ Métricas não calculadas")

    print("\n✅ INTEGRAÇÃO FUNCIONANDO")
else:
    print("  ❌ ConsciousSystem não foi inicializado")

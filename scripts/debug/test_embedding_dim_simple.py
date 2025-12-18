#!/usr/bin/env python3
"""
Teste simples para identificar problema de dimensão de embedding.
"""

import sys
from pathlib import Path

import numpy as np

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


from src.consciousness.cycle_result_builder import LoopCycleResultBuilder
from src.consciousness.integration_loop import LoopCycleResult
from src.consciousness.shared_workspace import SharedWorkspace

print("=" * 80)
print("🧪 TESTE SIMPLES: Dimensão de Embeddings")
print("=" * 80)

# 1. Criar workspace
print("\n1️⃣  Criando workspace com embedding_dim=256...")
workspace = SharedWorkspace(embedding_dim=256, max_history_size=100)
print("✓ Workspace criado")

# 2. Simular módulos com diferentes dimensões
print("\n2️⃣  Simulando módulos com diferentes dimensões...")

# Módulo com 256 dims (correto)
embedding_256 = np.random.randn(256).astype(np.float32)
workspace.write_module_state("module_a", embedding_256)
print(f"   ✓ module_a: 256 dims")

# Módulo com 768 dims (problema!)
embedding_768 = np.random.randn(768).astype(np.float32)
workspace.write_module_state("module_b", embedding_768)
print(f"   ✓ module_b: 768 dims (será truncado para 256)")

# Módulo com 128 dims (menor)
embedding_128 = np.random.randn(128).astype(np.float32)
workspace.write_module_state("module_c", embedding_128)
print(f"   ✓ module_c: 128 dims (será padded para 256)")

# 3. Verificar normalização
print("\n3️⃣  Testando normalização de dimensões...")
try:
    builder = LoopCycleResultBuilder(workspace)
    embeddings = builder._extract_embeddings()

    print(f"   module_a normalizado: {embeddings['module_a'].shape}")
    print(f"   module_b normalizado: {embeddings['module_b'].shape}")
    print(f"   module_c normalizado: {embeddings['module_c'].shape}")

    # Verificar que todas têm 256 dims
    assert embeddings["module_a"].shape == (256,), f"module_a: {embeddings['module_a'].shape}"
    assert embeddings["module_b"].shape == (256,), f"module_b: {embeddings['module_b'].shape}"
    assert embeddings["module_c"].shape == (256,), f"module_c: {embeddings['module_c'].shape}"

    print("   ✓ Todas as embeddings normalizadas para 256 dims")
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# 4. Testar construção de resultado estendido
print("\n4️⃣  Testando construção de ExtendedLoopCycleResult...")
try:
    base_result = LoopCycleResult(
        cycle_number=1,
        cycle_duration_ms=100.0,
        modules_executed=["module_a", "module_b", "module_c"],
        phi_estimate=0.5,
    )

    extended = builder.build_from_workspace(base_result, previous_cycle=None)
    print(f"   ✓ ExtendedLoopCycleResult criado com {len(extended.modules_executed)} módulos")
    print(f"   Φ: {extended.phi_estimate}")
    print(f"   Integration strength: {extended.integration_strength}")
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

# 5. Testar cálculo de activations (onde o erro acontecia)
print("\n5️⃣  Testando cálculo de activações...")
try:
    activations = builder._calculate_activations(embeddings, previous_cycle=None)
    print(f"   ✓ Activações calculadas para {len(activations)} módulos")
    for module_name, activation in activations.items():
        print(f"     {module_name}: {activation:.4f}")
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ TODOS OS TESTES PASSARAM!")
print("=" * 80)

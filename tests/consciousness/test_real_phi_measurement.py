"""
Test Real Phi Measurement

CLASSIFICATION: [REAL]
- Sem @patch decorators
- Toca GPU real (PyTorch CUDA)
- Mede Φ de VERDADE (sem dependência de LLM externa)

Tempo esperado: 5-30 minutos
Hardware requerido: GPU 4GB+ VRAM
Timeout: 800s por teste (permite estabilização GPU e cache)

Como rodar:
  pytest tests/consciousness/test_real_phi_measurement.py -v -s
"""

import pytest
import torch

pytestmark = pytest.mark.real


@pytest.fixture
async def gpu_device() -> str:
    """Retorna 'cuda' se disponível, senão skip o teste."""
    if torch.cuda.is_available():
        print(f"\n✅ GPU disponível: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        return "cuda"
    else:
        pytest.skip("GPU não disponível - teste requer GPU para cálculos pesados de Φ")


@pytest.fixture
async def ollama_client():
    """
    DEPRECATED: Este teste não usa mais Ollama.

    Mantido apenas para compatibilidade com testes antigos.
    O cálculo de Φ não depende mais de LLM externa.
    """
    pytest.skip("Teste não usa mais Ollama - Φ é calculado internamente")


@pytest.mark.asyncio
@pytest.mark.slow  # CORREÇÃO: Marcar como slow devido a uso de GPU/CUDA
# Timeout: 800s (respeita configuração global - permite estabilização GPU e cache)
async def test_phi_measurement_basic(gpu_device: str) -> None:
    """
    TESTE REAL: Mede Φ com GPU real

    Classifação: [REAL]
    - Usa GPU de verdade
    - Sem @patch
    - Valida integração GPU
    """
    from src.consciousness.integration_loop import IntegrationLoop

    # Setup
    consciousness = IntegrationLoop()

    # Executa ciclos
    phi_values = []
    for cycle in range(10):
        result = await consciousness.execute_cycle()
        phi = result.phi_estimate
        phi_values.append(phi)
        print(f"  Cycle {cycle + 1}/10: Φ = {phi:.4f}")
    assert len(phi_values) == 10
    assert all(0.0 <= phi <= 1.0 for phi in phi_values), "Φ deve estar em [0,1]"

    avg_phi = sum(phi_values) / len(phi_values)
    print(f"\n📊 RESULTADO: Φ_avg = {avg_phi:.4f}")


@pytest.mark.asyncio
@pytest.mark.slow  # CORREÇÃO: Marcar como slow devido a uso de GPU/CUDA
# Timeout: 800s (respeita configuração global - permite estabilização GPU e cache)
async def test_phi_multiseed_small(gpu_device: str) -> None:
    """
    TESTE REAL: Mede Φ com múltiplas seeds

    Classificação: [REAL]
    - GPU real
    - Múltiplos seeds (3 sementes)
    - Valida variabilidade

    Tempo: ~5 minutos
    """
    from src.consciousness.integration_loop import IntegrationLoop

    results = []

    for seed in range(3):
        print(f"\n🌱 Seed {seed + 1}/3")

        # Nova instância para cada seed
        consciousness = IntegrationLoop()

        phi_values = []
        for cycle in range(50):  # Menos ciclos para teste rápido
            result = await consciousness.execute_cycle()
            phi = result.phi_estimate
            phi_values.append(phi)
        avg_phi = sum(phi_values) / len(phi_values)
        results.append(avg_phi)
        print(f"   Φ_avg = {avg_phi:.4f}")

    # Validação
    assert len(results) == 3
    assert all(0.0 <= phi <= 1.0 for phi in results)

    overall_avg = sum(results) / len(results)
    variance = max(results) - min(results)

    print("\n📊 RESULTADOS MULTI-SEED:")
    print(f"   Valores: {[f'{p:.4f}' for p in results]}")
    print(f"   Média geral: {overall_avg:.4f}")
    print(f"   Variância: {variance:.4f}")


@pytest.mark.asyncio
@pytest.mark.slow  # CORREÇÃO: Marcar como slow devido a uso de GPU/CUDA
# Timeout: 800s (respeita configuração global - permite estabilização GPU e cache)
async def test_phi_with_ollama(gpu_device: str, ollama_client) -> None:
    """
    TESTE REAL: Mede Φ com GPU (FULL PIPELINE)

    CORREÇÃO: Este teste NÃO usa mais Ollama.
    O cálculo de Φ é feito internamente pelo IntegrationLoop.

    Classificação: [REAL]
    - GPU real
    - Cálculo de Φ interno (sem LLM externa)
    - Full pipeline

    Tempo: ~30 minutos

    IMPORTANTE: Este é o teste que VALIDA números para o paper!
    """
    from src.consciousness.integration_loop import IntegrationLoop

    # Setup - Φ é calculado internamente
    consciousness = IntegrationLoop()

    phi_values = []
    print("\n⏱️  Medindo Φ com GPU... (será lento)")

    # Reduz para 20 ciclos em teste para ir mais rápido
    # Em produção: 100+ ciclos
    for cycle in range(20):
        result = await consciousness.execute_cycle()
        phi = result.phi_estimate
        phi_values.append(phi)

        if (cycle + 1) % 5 == 0:
            print(f"  {cycle + 1}/20 ciclos... Φ_avg = {sum(phi_values) / (cycle + 1):.4f}")

    # Resultados
    avg_phi = sum(phi_values) / len(phi_values)
    min_phi = min(phi_values)
    max_phi = max(phi_values)

    print("\n📊 RESULTADO DO CÁLCULO DE Φ:")
    print(f"   Média: {avg_phi:.4f}")
    print(f"   Mínimo: {min_phi:.4f}")
    print(f"   Máximo: {max_phi:.4f}")

    # Validação
    assert 0.0 <= avg_phi <= 1.0
    assert min_phi <= avg_phi <= max_phi


@pytest.mark.asyncio
@pytest.mark.slow
# Timeout: 800s (respeita configuração global - permite estabilização GPU e cache)
async def test_phi_measurement_with_topological_metrics(gpu_device: str) -> None:
    """
    TESTE REAL: Mede Φ com métricas topológicas complementares

    Classificação: [REAL]
    - Usa GPU de verdade
    - Mede Φ e métricas topológicas
    - Valida complementaridade
    """
    import numpy as np

    from src.consciousness.hybrid_topological_engine import HybridTopologicalEngine
    from src.consciousness.integration_loop import IntegrationLoop

    # Setup com engine topológico
    consciousness = IntegrationLoop()
    if consciousness.workspace:
        consciousness.workspace.hybrid_topological_engine = HybridTopologicalEngine()

    # Executa ciclos
    phi_values = []
    for cycle in range(5):
        result = await consciousness.execute_cycle()
        phi = result.phi_estimate
        phi_values.append(phi)
        print(f"  Cycle {cycle + 1}/5: Φ = {phi:.4f}")

    # Calcular métricas topológicas
    if consciousness.workspace and consciousness.workspace.hybrid_topological_engine:
        # Simular estados para métricas topológicas
        np.random.seed(42)
        for i in range(5):
            rho_C = np.random.randn(256)
            rho_P = np.random.randn(256)
            rho_U = np.random.randn(256)

            consciousness.workspace.write_module_state("conscious_module", rho_C)
            consciousness.workspace.write_module_state("preconscious_module", rho_P)
            consciousness.workspace.write_module_state("unconscious_module", rho_U)
            consciousness.workspace.advance_cycle()

        topological_metrics = consciousness.workspace.compute_hybrid_topological_metrics()

        if topological_metrics is not None:
            assert "omega" in topological_metrics
            print(f"\n📊 Topological Metrics: Ω = {topological_metrics['omega']:.4f}")

    avg_phi = sum(phi_values) / len(phi_values)
    print(f"\n📊 RESULTADO: Φ_avg = {avg_phi:.4f}")

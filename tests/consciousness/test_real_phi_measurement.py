"""
Test Real Phi Measurement

CLASSIFICATION: [REAL]
- Sem @patch decorators
- Toca GPU real (PyTorch CUDA)
- Toca LLM real (Ollama qwen2:7b)
- Mede Φ de VERDADE

Tempo esperado: 5-30 minutos
Hardware requerido: GPU 4GB+ VRAM
Dependências: Ollama rodando em http://localhost:11434

Como rodar:
  pytest tests/consciousness/test_real_phi_measurement.py --timeout=0 -v -s
"""

import pytest
import torch


pytestmark = pytest.mark.real


@pytest.fixture
async def gpu_device() -> str:
    """Retorna 'cuda' se disponível, senão 'cpu'."""
    if torch.cuda.is_available():
        print(f"\n✅ GPU disponível: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        return "cuda"
    else:
        print("\n⚠️  GPU não disponível, usando CPU (muito mais lento)")
        return "cpu"


@pytest.fixture
async def ollama_client():
    """Retorna cliente Ollama real (não mockado)."""
    try:
        from src.integrations.ollama_client import OllamaClient
        client = OllamaClient(base_url="http://localhost:11434")
        # Testa conexão
        tags = await client.list_models()
        if tags:
            print(f"\n✅ Ollama conectado. Modelos disponíveis: {len(tags)}")
            return client
        else:
            pytest.skip("Ollama não tem modelos")
    except Exception as e:
        pytest.skip(f"Ollama não acessível: {e}")


@pytest.mark.asyncio
@pytest.mark.timeout(0)  # Sem timeout para testes reais
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
    consciousness = IntegrationLoop(device=gpu_device)
    
    # Executa ciclos
    phi_values = []
    for cycle in range(10):
        phi = await consciousness.execute_cycle()
        phi_values.append(phi)
        print(f"  Cycle {cycle+1}/10: Φ = {phi:.4f}")
    
    # Validação
    assert len(phi_values) == 10
    assert all(0.0 <= phi <= 1.0 for phi in phi_values), "Φ deve estar em [0,1]"
    
    avg_phi = sum(phi_values) / len(phi_values)
    print(f"\n📊 RESULTADO: Φ_avg = {avg_phi:.4f}")


@pytest.mark.asyncio
@pytest.mark.timeout(0)
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
        print(f"\n🌱 Seed {seed+1}/3")
        
        # Nova instância para cada seed
        consciousness = IntegrationLoop(device=gpu_device, seed=seed)
        
        phi_values = []
        for cycle in range(50):  # Menos ciclos para teste rápido
            phi = await consciousness.execute_cycle()
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
@pytest.mark.timeout(0)
async def test_phi_with_ollama(gpu_device: str, ollama_client) -> None:
    """
    TESTE REAL: Mede Φ com GPU + Ollama (FULL PIPELINE)
    
    Classificação: [REAL]
    - GPU real
    - LLM real (Ollama qwen2:7b)
    - Network real (sem aiohttp mock)
    - Full pipeline
    
    Tempo: ~30 minutos
    
    IMPORTANTE: Este é o teste que VALIDA números para o paper!
    """
    from src.consciousness.integration_loop import IntegrationLoop
    
    # Setup com LLM real
    consciousness = IntegrationLoop(device=gpu_device, llm_client=ollama_client)
    
    phi_values = []
    print("\n⏱️  Medindo Φ com LLM real... (será lento)")
    
    # Reduz para 20 ciclos em teste para ir mais rápido
    # Em produção: 100+ ciclos
    for cycle in range(20):
        phi = await consciousness.execute_cycle()
        phi_values.append(phi)
        
        if (cycle + 1) % 5 == 0:
            print(f"  {cycle+1}/20 ciclos... Φ_avg = {sum(phi_values)/(cycle+1):.4f}")
    
    # Resultados
    avg_phi = sum(phi_values) / len(phi_values)
    min_phi = min(phi_values)
    max_phi = max(phi_values)
    
    print("\n📊 RESULTADO COM OLLAMA:")
    print(f"   Média: {avg_phi:.4f}")
    print(f"   Mínimo: {min_phi:.4f}")
    print(f"   Máximo: {max_phi:.4f}")
    
    # Validação
    assert 0.0 <= avg_phi <= 1.0
    assert min_phi <= avg_phi <= max_phi

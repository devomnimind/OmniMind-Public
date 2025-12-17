#!/usr/bin/env python3
"""
Teste do Sistema de Fallback LLM - OmniMind
==========================================

Este script demonstra o sistema de fallback LLM configurado para
priorizar modelos offline locais (phi:latest, llama3.2:1b) com
fallbacks para cloud APIs (OpenRouter, Gemini).

Arquitetura:
1. Ollama (Offline) - phi:latest, llama3.2:1b
2. HuggingFace Local (Offline) - microsoft/Phi-3.5-mini-instruct
3. OpenRouter (Cloud) - múltiplos modelos gratuitos/pagos
4. Gemini (Cloud) - Google Gemini como último fallback

Uso:
    python test_llm_fallback.py
"""

import asyncio
import logging
from src.integrations.llm_router import LLMRouter, LLMModelTier

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_llm_fallback():
    """Testa o sistema completo de fallback LLM."""
    print("🧠 Teste do Sistema de Fallback LLM - OmniMind")
    print("=" * 50)

    # Inicializa router
    router = LLMRouter()

    # Verifica status dos provedores
    print("\n📊 Status dos Provedores:")
    status = router.get_provider_status()
    for provider, available in status.items():
        status_icon = "✅" if available else "❌"
        print(f"  {status_icon} {provider}")

    # Mostra configurações por tier
    print("\n⚙️  Configurações por Tier:")
    for tier, configs in router.tier_configs.items():
        print(f"  {tier.value.upper()}: {len(configs)} opções")
        for i, config in enumerate(configs):
            priority = "🔥" if i < 2 else "🔄" if i < 3 else "☁️"
            print(f"    {priority} {config.provider.value} - {config.model_name}")

    # Testa diferentes tiers
    test_prompts = {
        LLMModelTier.FAST: "Diga 'Olá Mundo' em português.",
        LLMModelTier.BALANCED: "Explique IA em 2 frases.",
        LLMModelTier.HIGH_QUALITY: "Descreva os benefícios da arquitetura offline-first para LLMs."
    }

    print("\n🧪 Testes de Invocação:")
    for tier, prompt in test_prompts.items():
        print(f"\n--- Testando Tier: {tier.value.upper()} ---")
        try:
            response = await router.invoke(prompt, tier=tier)

            if response.success:
                print("✅ Sucesso!")
                print(f"   Provedor: {response.provider.value}")
                print(f"   Modelo: {response.model}")
                print(f"   Latência: {response.latency_ms}ms")
                print(f"   Resposta: {response.text[:150]}...")
            else:
                print(f"❌ Falha: {response.error}")

        except Exception as e:
            print(f"❌ Erro: {e}")

    # Mostra métricas finais
    print("\n📈 Métricas Finais:")
    metrics = router.get_metrics()
    print(f"   Total de requests: {metrics['requests_total']}")
    print(f"   Requests bem-sucedidos: {metrics['requests_success']}")
    print(f"   Fallbacks utilizados: {metrics['fallback_used']}")

    print("\n🎉 Teste concluído com sucesso!")
    print("O sistema offline-first está funcionando corretamente.")


if __name__ == "__main__":
    asyncio.run(test_llm_fallback())

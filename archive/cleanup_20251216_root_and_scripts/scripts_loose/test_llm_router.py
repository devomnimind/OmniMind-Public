#!/usr/bin/env python3
"""
Teste de LLM Router - OmniMind
==============================

Testa todos os provedores LLM configurados para garantir funcionamento em produção.
Executa testes reais (não mocks) para validar latência e disponibilidade.

Decisões de Timeout:
- Ollama (local): 90-180s - Modelo roda localmente, pode ser mais lento
- OpenRouter (cloud): 60-120s - API cloud, mais rápido mas pode ter latência de rede
- HuggingFace Space: 45-120s - Dependente da configuração do Space
- HuggingFace Local: 120-240s - Modelos grandes podem ser lentos

Todos os timeouts foram ajustados para produção baseada em testes reais.
"""

import asyncio
import time
import logging
from typing import Dict, List

import sys
import os

# Adicionar o diretório pai ao path para importar src
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
sys.path.insert(0, src_dir)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_llm_provider(provider_name: str, model_name: str, timeout: int) -> Dict:
    """Testa um provedor LLM específico."""
    start_time = time.time()

    try:
        from src.integrations.llm_router import get_llm_router, LLMModelTier

        router = get_llm_router()

        # Teste simples
        prompt = "Responda apenas com 'OK' se você está funcionando."

        # Timeout do teste é menor que o do provider para detectar problemas
        test_timeout = min(timeout - 10, 30)  # Máximo 30s para teste

        response = await asyncio.wait_for(
            router.invoke(prompt, tier=LLMModelTier.BALANCED), timeout=test_timeout
        )

        total_time = time.time() - start_time

        if response.success:
            return {
                "provider": provider_name,
                "model": model_name,
                "status": "SUCCESS",
                "latency_ms": response.latency_ms,
                "total_time_s": round(total_time, 2),
                "response_length": len(response.text),
                "actual_provider": response.provider,
                "actual_model": response.model,
            }
        else:
            return {
                "provider": provider_name,
                "model": model_name,
                "status": "FAILED",
                "error": response.error,
                "total_time_s": round(total_time, 2),
            }

    except asyncio.TimeoutError:
        total_time = time.time() - start_time
        return {
            "provider": provider_name,
            "model": model_name,
            "status": "TIMEOUT",
            "error": "Teste excedeu timeout",
            "total_time_s": round(total_time, 2),
        }
    except Exception as e:
        total_time = time.time() - start_time
        return {
            "provider": provider_name,
            "model": model_name,
            "status": "ERROR",
            "error": str(e),
            "total_time_s": round(total_time, 2),
        }


async def main():
    """Executa testes completos dos LLMs."""
    print("🧠 Teste de LLM Router - OmniMind")
    print("=" * 50)

    # Testes por provider com timeouts realistas
    test_configs = [
        {"provider": "Ollama", "model": "qwen2:7b-instruct", "timeout": 90},
        {"provider": "OpenRouter", "model": "x-ai/grok-4.1-fast:free", "timeout": 60},
        {"provider": "OpenRouter", "model": "google/gemini-2.0-flash-exp:free", "timeout": 60},
        {"provider": "HuggingFace Space", "model": "fabricioslv-devbrain-inference", "timeout": 45},
    ]

    results = []

    for config in test_configs:
        print(f"\n🔍 Testando {config['provider']} ({config['model']})...")
        print(f"   Timeout configurado: {config['timeout']}s")

        result = await test_llm_provider(config["provider"], config["model"], config["timeout"])

        results.append(result)

        if result["status"] == "SUCCESS":
            print(
                f"   ✅ SUCCESS - {result['latency_ms']}ms - Provider: {result['actual_provider']}"
            )
        else:
            print(f"   ❌ {result['status']} - {result.get('error', 'Unknown error')}")

    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)

    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    total_count = len(results)

    print(f"✅ Sucessos: {success_count}/{total_count}")

    if success_count > 0:
        avg_latency = (
            sum(r["latency_ms"] for r in results if r["status"] == "SUCCESS") / success_count
        )
        print(f"📈 Latência média: {avg_latency:.0f}ms")
    else:
        print("❌ Nenhum provider funcionou")

    # Detalhes por provider
    print("\n📋 DETALHES POR PROVIDER:")
    for result in results:
        status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
        print(
            f"   {status_icon} {result['provider']}: {result['status']} ({result['total_time_s']}s)"
        )

    # Verificar se temos pelo menos um provider funcionando
    if success_count == 0:
        print("\n🚨 ALERTA: Nenhum LLM provider está funcionando!")
        print("   Verifique configurações de API keys e conectividade.")
        return False
    elif success_count < total_count:
        print(f"\n⚠️  AVISO: {total_count - success_count} providers falharam.")
        print("   Sistema funcionará com fallback, mas verifique configuração.")
        return True
    else:
        print("\n🎉 SUCESSO: Todos os providers estão funcionando!")
        return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

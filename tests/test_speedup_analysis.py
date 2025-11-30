#!/usr/bin/env python3
"""
Teste de Performance Otimizada - Speedup Real da Vetorização

Este teste demonstra o verdadeiro speedup da vetorização usando:
- Muitos módulos (20-50) para mostrar benefício da paralelização
- Comparação justa: mesmo workload computacional
- Métricas detalhadas de performance
"""

import asyncio
import logging
import time
from typing import Dict, List

import numpy as np
import torch

from src.consciousness.shared_workspace import SharedWorkspace, CrossPredictionMetrics

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_real_speedup():
    """Teste de speedup real com muitos módulos."""
    logger.info("🚀 TESTE DE SPEEDUP REAL - Vetorização com Muitos Módulos")
    logger.info("=" * 80)

    # Testar com diferentes números de módulos
    module_counts = [4, 10, 20, 30]  # Escalar para ver quando compensa

    results = {}

    for n_modules in module_counts:
        logger.info(f"\n🔬 Testando com {n_modules} módulos")
        logger.info("-" * 50)

        # Criar workspace
        workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)

        # Gerar módulos dinamicamente
        modules = [f"module_{i:02d}" for i in range(n_modules)]

        # Gerar dados sintéticos com relações causais
        np.random.seed(42)
        n_timesteps = 100  # Suficiente para causalidade

        logger.info(f"📊 Gerando dados para {n_modules} módulos...")

        for module in modules:
            for t in range(n_timesteps):
                # Embedding base com sinal causal simples
                base_embedding = np.random.randn(256) * 0.1

                # Adicionar sinal causal baseado no índice do módulo
                module_idx = int(module.split("_")[1])
                causal_signal = np.sin(t * 0.05 + module_idx * 0.1) * 0.3
                base_embedding += causal_signal

                workspace.write_module_state(module, base_embedding)

        # Avançar ciclos
        for _ in range(3):
            workspace.advance_cycle()

        logger.info("✅ Dados gerados. Testando performance...")

        # TESTE: Comparação justa de performance
        history_window = 50

        # Método 1: Individual (baseline) - só módulos com histórico suficiente
        logger.info("   🔄 Executando método individual...")
        start_time = time.time()

        individual_count = 0
        # Filtrar apenas módulos com histórico suficiente (igual ao vetorizado)
        valid_modules = []
        for module in modules:
            history = workspace.get_module_history(module, history_window)
            if len(history) >= 2:
                valid_modules.append(module)

        logger.info(
            f"   📊 Usando {len(valid_modules)} módulos válidos (de {len(modules)} criados)"
        )

        for i, source in enumerate(valid_modules):
            for j, target in enumerate(valid_modules):
                if i != j:  # Não auto-predição
                    pred = workspace.compute_cross_prediction(source, target, history_window)
                    individual_count += 1

        individual_time = (time.time() - start_time) * 1000

        # Método 2: Vetorizado
        logger.info("   ⚡ Executando método vetorizado...")
        start_time = time.time()

        vectorized_predictions = workspace.compute_all_cross_predictions_vectorized(
            history_window=history_window, use_gpu=torch.cuda.is_available(), force_recompute=True
        )

        vectorized_time = (time.time() - start_time) * 1000

        # Calcular métricas
        real_speedup = individual_time / vectorized_time if vectorized_time > 0 else 1.0
        vectorized_count = (
            len(vectorized_predictions) * len(list(vectorized_predictions.values())[0])
            if vectorized_predictions
            else 0
        )

        # Verificar se mesma quantidade de predições
        if individual_count != vectorized_count:
            logger.warning(
                f"   ⚠️ Contagem diferente: individual={individual_count}, vetorizado={vectorized_count}"
            )
            logger.warning(
                f"   Módulos válidos: {len(valid_modules)}, Predições esperadas: {len(valid_modules) * (len(valid_modules) - 1)}"
            )

        # Métricas por predição
        individual_per_pred = individual_time / individual_count if individual_count > 0 else 0
        vectorized_per_pred = vectorized_time / vectorized_count if vectorized_count > 0 else 0

        logger.info("📊 Resultados:")
        logger.info(f"   Predições calculadas: {individual_count}")
        logger.info(
            f"   Individual: {individual_time:.1f}ms total ({individual_per_pred:.2f}ms/pred)"
        )
        logger.info(
            f"   Vetorizado: {vectorized_time:.1f}ms total ({vectorized_per_pred:.2f}ms/pred)"
        )
        logger.info(f"   Speedup real: {real_speedup:.2f}x")
        logger.info(f"   GPU: {'Sim' if torch.cuda.is_available() else 'Não'}")

        results[n_modules] = {
            "individual_time": individual_time,
            "vectorized_time": vectorized_time,
            "speedup": real_speedup,
            "predictions": individual_count,
            "individual_per_pred": individual_per_pred,
            "vectorized_per_pred": vectorized_per_pred,
        }

    # ANÁLISE DOS RESULTADOS
    logger.info("\n🎯 ANÁLISE DE SPEEDUP POR ESCALA")
    logger.info("=" * 80)

    logger.info("📈 Speedup por número de módulos:")
    for n_modules, data in results.items():
        speedup = data["speedup"]
        status = "✅" if speedup > 1.0 else "❌"
        logger.info(f"   {n_modules} módulos: {speedup:.2f}x {status}")

    # Encontrar ponto de equilíbrio
    break_even = None
    for n_modules in sorted(results.keys()):
        if results[n_modules]["speedup"] > 1.0:
            break_even = n_modules
            break

    if break_even:
        logger.info(
            f"\n💡 PONTO DE EQUILÍBRIO: Vetorização compensa a partir de {break_even} módulos"
        )
    else:
        logger.info(f"\n⚠️ Vetorização ainda não compensa mesmo com {max(module_counts)} módulos")

    # TESTE DE CACHE OTIMIZADO
    logger.info("\n💾 TESTE DE CACHE AVANÇADO")
    logger.info("-" * 50)

    # Usar configuração otimizada (20 módulos)
    n_modules = 20
    workspace = SharedWorkspace(embedding_dim=256, max_history_size=2000)
    modules = [f"module_{i:02d}" for i in range(n_modules)]

    # Gerar dados
    np.random.seed(42)
    for module in modules:
        for t in range(100):
            base_embedding = np.random.randn(256) * 0.1
            module_idx = int(module.split("_")[1])
            causal_signal = np.sin(t * 0.05 + module_idx * 0.1) * 0.3
            base_embedding += causal_signal
            workspace.write_module_state(module, base_embedding)

    # Teste de cache com diferentes cenários
    cache_scenarios = [
        ("Cache frio", True),  # Forçar recálculo
        ("Cache quente", False),  # Usar cache
        ("Cache invalidado", False),  # Invalidar e usar
    ]

    cache_times = {}

    for scenario_name, force_recompute in cache_scenarios:
        if scenario_name == "Cache invalidado":
            # Invalidar alguns módulos
            if workspace._vectorized_predictor is not None:
                for i in range(0, n_modules, 5):  # Invalidar 20% dos módulos
                    workspace._vectorized_predictor.invalidate_module_cache(modules[i])
        result = workspace.compute_all_cross_predictions_vectorized(
            history_window=50, force_recompute=force_recompute
        )
        elapsed = (time.time() - start_time) * 1000

        cache_times[scenario_name] = elapsed
        logger.info(f"   {scenario_name}: {elapsed:.1f}ms")

    # Calcular eficiência do cache
    cold_time = cache_times["Cache frio"]
    hot_time = cache_times["Cache quente"]
    invalidated_time = cache_times["Cache invalidado"]

    cache_speedup = cold_time / hot_time if hot_time > 0 else 1.0
    cache_overhead = invalidated_time - hot_time  # Overhead da invalidação

    logger.info("📊 Eficiência do Cache:")
    logger.info(f"   Speedup cache: {cache_speedup:.2f}x")
    logger.info(f"   Overhead invalidação: {cache_overhead:.1f}ms")

    # RECOMENDAÇÕES DE OTIMIZAÇÃO
    logger.info("\n🎯 RECOMENDAÇÕES DE OTIMIZAÇÃO")
    logger.info("=" * 80)

    recommendations = []

    if break_even and break_even <= 10:
        recommendations.append("✅ Vetorização: Boa para sistemas com 10+ módulos")
    elif break_even and break_even > 20:
        recommendations.append("⚠️ Vetorização: Otimizar overhead para compensar com menos módulos")
    else:
        recommendations.append("❌ Vetorização: Overhead muito alto, precisa otimização")

    if cache_speedup > 2.0:
        recommendations.append("✅ Cache: Excelente performance")
    elif cache_speedup > 1.5:
        recommendations.append("⚠️ Cache: Funcional, mas pode melhorar")
    else:
        recommendations.append("❌ Cache: Overhead alto, otimizar lookups")

    if torch.cuda.is_available():
        recommendations.append("✅ GPU: Disponível e sendo utilizada")
    else:
        recommendations.append("⚠️ GPU: Instalar PyTorch GPU para speedup adicional")

    for rec in recommendations:
        logger.info(f"   {rec}")

    # RESULTADO FINAL
    overall_score = 0
    if break_even and break_even <= 15:
        overall_score += 1
    if cache_speedup > 1.8:
        overall_score += 1
    if torch.cuda.is_available():
        overall_score += 1

    overall_rating = overall_score / 3

    logger.info(f"\n🏆 AVALIAÇÃO GERAL: {overall_score}/3 ({overall_rating:.0%})")

    if overall_rating >= 0.8:
        logger.info("🎉 Otimizações funcionando bem! Sistema pronto para produção.")
    elif overall_rating >= 0.6:
        logger.info("⚠️ Otimizações funcionais, mas precisam ajustes.")
    else:
        logger.info("❌ Otimizações precisam revisão significativa.")

    return {
        "results": results,
        "break_even_modules": break_even,
        "cache_speedup": cache_speedup,
        "cache_overhead": cache_overhead,
        "overall_score": overall_rating,
    }


if __name__ == "__main__":
    try:
        import torch

        result = asyncio.run(test_real_speedup())

        print("\n📊 Resumo Executivo:")
        print(f"   Ponto de equilíbrio: {result['break_even_modules']} módulos")
        print(f"   Cache speedup: {result['cache_speedup']:.2f}x")
        print(f"   Score geral: {result['overall_score']:.0%}")

    except ImportError:
        logger.error("❌ PyTorch não encontrado. Instale com: pip install torch")
        logger.info("💡 Performance limitada sem GPU")

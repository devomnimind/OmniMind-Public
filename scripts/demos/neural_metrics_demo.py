"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Demo: Neural Metrics Collector - Phase 20.

Demonstra coleta de métricas de latência e health tracking.
"""

import logging
import sys
from src.neurosymbolic.neural_component import NeuralComponent
from src.neurosymbolic.metrics_collector import get_metrics_collector

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("MetricsDemo")


def demo_metrics():
    """Demonstração de coleta de métricas."""
    logger.info("=" * 70)
    logger.info("NEURAL METRICS COLLECTOR DEMO - PHASE 20")
    logger.info("=" * 70)

    # Inicializar backends
    ollama_nc = NeuralComponent(model_name="ollama/qwen2:7b-instruct")
    hf_space_nc = NeuralComponent(model_name="hf/space")

    test_queries = [
        "What is 2+2?",
        "Explain quantum computing in 10 words",
        "What is the capital of France?",
    ]

    logger.info("\n🧪 Testing Ollama Backend...")
    for query in test_queries:
        try:
            result = ollama_nc.infer(query)
            logger.info(f"✅ Query: {query[:30]}... | Response: {result.answer[:50]}...")
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")

    logger.info("\n🧪 Testing HF Space Backend...")
    for query in test_queries[:2]:  # Apenas 2 para economizar tempo
        try:
            result = hf_space_nc.infer(query)
            logger.info(f"✅ Query: {query[:30]}... | Response: {result.answer[:50]}...")
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")

    # Exibir métricas
    logger.info("\n" + "=" * 70)
    logger.info("METRICS SUMMARY")
    logger.info("=" * 70)

    metrics = get_metrics_collector()
    metrics.log_summary()

    # Verificar health status
    logger.info("\n📊 HEALTH STATUS:")
    for backend_name in ["ollama", "hf_space", "huggingface"]:
        backend_metrics = metrics.get_backend_metrics(backend_name)
        if backend_metrics and backend_metrics.total_requests > 0:
            status = "✅ HEALTHY" if backend_metrics.is_healthy() else "❌ UNHEALTHY"
            logger.info(
                f"  {backend_name}: {status} "
                f"({backend_metrics.success_rate:.1%} success, "
                f"{backend_metrics.average_latency*1000:.0f}ms avg)"
            )

    logger.info("\n" + "=" * 70)
    logger.info("Demo completed successfully!")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        demo_metrics()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Demo failed: {e}")
        sys.exit(1)

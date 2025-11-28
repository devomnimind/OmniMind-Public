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
Demo: Neural Response Cache - Phase 21.

Demonstra cache inteligente com hit rate tracking.
"""

import logging
import sys
from src.neurosymbolic.neural_component import NeuralComponent
from src.neurosymbolic.response_cache import get_response_cache

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("CacheDemo")


def demo_cache():
    """Demonstração de cache de respostas."""
    logger.info("=" * 70)
    logger.info("NEURAL RESPONSE CACHE DEMO - PHASE 21")
    logger.info("=" * 70)

    # Inicializar component
    nc = NeuralComponent(model_name="ollama/qwen2:7b-instruct")

    test_queries = [
        "What is 2+2?",
        "What is the capital of France?",
        "What is 2+2?",  # Repetido (cache hit esperado)
        "Explain AI in 5 words",
        "What is the capital of France?",  # Repetido (cache hit esperado)
    ]

    logger.info("\n🧪 Making requests (some are duplicates)...\n")

    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n--- Request {i}/5: {query} ---")
        try:
            result = nc.infer(query)
            logger.info(f"✅ Response: {result.answer[:60]}...")
            if result.raw_output and result.raw_output.get("source") == "cache":
                logger.info(
                    f"📦 CACHE HIT! Backend: {result.raw_output.get('backend')}, "
                    f"Hits: {result.raw_output.get('hits')}"
                )
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")

    # Exibir estatísticas do cache
    logger.info("\n" + "=" * 70)
    logger.info("CACHE STATISTICS")
    logger.info("=" * 70)

    cache = get_response_cache()
    cache.log_stats()

    # Demonstrar limpeza de cache
    logger.info("\n🧹 Clearing cache...")
    cache.clear()
    cache.log_stats()

    logger.info("\n" + "=" * 70)
    logger.info("Demo completed successfully!")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        demo_cache()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Demo failed: {e}")
        sys.exit(1)

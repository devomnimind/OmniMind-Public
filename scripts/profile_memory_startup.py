#!/usr/bin/env python3
"""
Memory Profiling Script for OmniMind Startup
=============================================

Profiles memory usage during system initialization to identify
which components are loading embedding models and causing memory spikes.

Usage:
    python scripts/profile_memory_startup.py
"""

import os
import sys
import time
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [PROFILER]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_memory_mb() -> float:
    """Get current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def profile_component(name: str, import_func) -> Tuple[float, float]:
    """
    Profile memory usage of a component initialization.

    Args:
        name: Component name for logging
        import_func: Function that imports/initializes the component

    Returns:
        (memory_before_mb, memory_after_mb)
    """
    logger.info(f"📊 Profiling: {name}")

    mem_before = get_memory_mb()
    logger.info(f"  Memory before: {mem_before:.2f} MB")

    try:
        import_func()
        time.sleep(0.5)  # Allow memory to settle

        mem_after = get_memory_mb()
        delta = mem_after - mem_before

        logger.info(f"  Memory after:  {mem_after:.2f} MB")
        logger.info(f"  Delta:         {delta:.2f} MB")

        if delta > 100:
            logger.warning(f"  ⚠️  HIGH MEMORY INCREASE: {delta:.2f} MB")

        return mem_before, mem_after

    except Exception as e:
        logger.error(f"  ❌ Error profiling {name}: {e}")
        return mem_before, get_memory_mb()


def main():
    """Run memory profiling on OmniMind components."""
    logger.info("🔬 Starting OmniMind Memory Profiling")
    logger.info("=" * 60)

    results: List[Tuple[str, float, float, float]] = []

    # Baseline
    baseline = get_memory_mb()
    logger.info(f"📍 Baseline memory: {baseline:.2f} MB\n")

    # Profile 1: Safe Transformer Loader (should use cache)
    def load_safe_transformer():
        from src.embeddings.safe_transformer_loader import load_sentence_transformer_safe
        model, dim = load_sentence_transformer_safe()
        logger.info(f"    Model loaded: {model is not None}, Dim: {dim}")

    before, after = profile_component("Safe Transformer Loader (1st call)", load_safe_transformer)
    results.append(("Safe Transformer Loader (1st)", before, after, after - before))
    logger.info("")

    # Profile 2: Safe Transformer Loader (should hit cache)
    before, after = profile_component("Safe Transformer Loader (2nd call - cache)", load_safe_transformer)
    results.append(("Safe Transformer Loader (2nd)", before, after, after - before))
    logger.info("")

    # Profile 3: Semantic Memory
    def load_semantic():
        from src.memory.semantic_memory import SemanticMemory
        mem = SemanticMemory()
        logger.info(f"    SemanticMemory initialized: {len(mem.concepts)} concepts")

    before, after = profile_component("SemanticMemory", load_semantic)
    results.append(("SemanticMemory", before, after, after - before))
    logger.info("")

    # Profile 4: Procedural Memory
    def load_procedural():
        from src.memory.procedural_memory import ProceduralMemory
        mem = ProceduralMemory()
        logger.info(f"    ProceduralMemory initialized: {len(mem.skills)} skills")

    before, after = profile_component("ProceduralMemory", load_procedural)
    results.append(("ProceduralMemory", before, after, after - before))
    logger.info("")

    # Profile 5: Episodic Memory (lazy loads embedding)
    def load_episodic():
        from src.memory.episodic_memory import EpisodicMemory
        # Note: This will trigger a warning about using encrypted storage
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mem = EpisodicMemory()
            logger.info(f"    EpisodicMemory initialized")

    before, after = profile_component("EpisodicMemory (init only)", load_episodic)
    results.append(("EpisodicMemory", before, after, after - before))
    logger.info("")

    # Profile 6: Dataset Indexer
    def load_indexer():
        from src.memory.dataset_indexer import DatasetIndexer
        indexer = DatasetIndexer()
        logger.info(f"    DatasetIndexer initialized: dim={indexer.embedding_dim}")

    before, after = profile_component("DatasetIndexer", load_indexer)
    results.append(("DatasetIndexer", before, after, after - before))
    logger.info("")

    # Profile 7: Code Embeddings
    def load_code_embeddings():
        from src.embeddings.code_embeddings import OmniMindEmbeddings
        embedder = OmniMindEmbeddings()
        logger.info(f"    OmniMindEmbeddings initialized: dim={embedder.embedding_dim}")

    before, after = profile_component("OmniMindEmbeddings", load_code_embeddings)
    results.append(("OmniMindEmbeddings", before, after, after - before))
    logger.info("")

    # Summary
    logger.info("=" * 60)
    logger.info("📊 MEMORY PROFILING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"{'Component':<35} {'Before':<12} {'After':<12} {'Delta':<12}")
    logger.info("-" * 60)

    for name, before, after, delta in results:
        status = "⚠️ " if delta > 100 else "✅"
        logger.info(f"{status} {name:<33} {before:>10.2f} MB {after:>10.2f} MB {delta:>+10.2f} MB")

    logger.info("-" * 60)
    total_increase = get_memory_mb() - baseline
    logger.info(f"{'TOTAL INCREASE':<35} {baseline:>10.2f} MB {get_memory_mb():>10.2f} MB {total_increase:>+10.2f} MB")
    logger.info("=" * 60)

    # Analysis
    logger.info("\n🔍 ANALYSIS:")
    high_memory_components = [name for name, _, _, delta in results if delta > 100]

    if high_memory_components:
        logger.warning(f"⚠️  Components with high memory usage (>100MB):")
        for comp in high_memory_components:
            logger.warning(f"   - {comp}")
    else:
        logger.info("✅ No components exceeded 100MB threshold")

    # Check for cache effectiveness
    first_load = next((delta for name, _, _, delta in results if "1st" in name), 0)
    second_load = next((delta for name, _, _, delta in results if "2nd" in name), 0)

    if first_load > 100 and second_load < 10:
        logger.info(f"✅ Singleton cache is working (1st: {first_load:.2f}MB, 2nd: {second_load:.2f}MB)")
    elif first_load > 100 and second_load > 50:
        logger.warning(f"⚠️  Singleton cache may not be working (1st: {first_load:.2f}MB, 2nd: {second_load:.2f}MB)")

    logger.info("\n✅ Profiling complete. Check logs for detailed traces.")


if __name__ == "__main__":
    main()

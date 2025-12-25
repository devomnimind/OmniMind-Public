#!/usr/bin/env python3
"""
Verification script for Memory Overflow Fix.
Tests that TopologicalDeglutitionEngine is cached and reused.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

import logging

logging.basicConfig(level=logging.INFO)

def verify_caching():
    print(">>> Testing Safe Loader Caching...")
    from src.embeddings.safe_transformer_loader import load_sentence_transformer_safe, _ENGINE_CACHE

    # 1. First Load
    engine1, dim1 = load_sentence_transformer_safe(model_name="all-MiniLM-L6-v2")
    print(f"Engine 1 ID: {id(engine1)}")

    # 2. Second Load
    engine2, dim2 = load_sentence_transformer_safe(model_name="all-MiniLM-L6-v2")
    print(f"Engine 2 ID: {id(engine2)}")

    # 3. Assertions
    if engine1 is engine2:
        print("✅ SUCCESS: Engine reused (Singleton working).")
    else:
        print("❌ FAILURE: Engine re-instantiated (Memory Leak likely).")
        sys.exit(1)

    if len(_ENGINE_CACHE) > 0:
         print(f"✅ Cache verified. Keys: {list(_ENGINE_CACHE.keys())}")
    else:
         print("❌ Cache empty.")
         sys.exit(1)

def verify_solution_engine():
    print("\n>>> Testing SolutionLookupEngine Integration...")
    try:
        from src.autonomous.solution_lookup_engine import SolutionLookupEngine
        # Mocking device utils if needed, or letting it run
        sle = SolutionLookupEngine(solutions_db_path=Path("data/known_solutions.json"))
        print("✅ SolutionLookupEngine initialized successfully.")

        # Test encode manually
        emb = sle.embedder.encode("test string")
        print(f"✅ Embedder encode working. Shape: {emb.shape}")

    except Exception as e:
        print(f"❌ FAILURE in SolutionLookupEngine: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify_caching()
    verify_solution_engine()
    print("\n✅ VERIFICATION COMPLETE.")

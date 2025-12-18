#!/usr/bin/env python
"""
Test Semantic Search with Knowledge Graph

Tests semantic search functionality using the knowledge graph built from consciousness papers.

Usage:
    python scripts/test_semantic_search.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Add src to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))


def test_semantic_search() -> None:
    """Test semantic search with knowledge graph"""
    print("🔍 Testing semantic search...")

    # Load model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")

    # Load knowledge graph
    kg_file = BASE_DIR / "exports" / "knowledge_graph_compact.json"
    if not kg_file.exists():
        print(f"❌ Knowledge graph not found at {kg_file}")
        print("   Run scripts/build_semantic_knowledge_graph.py first")
        sys.exit(1)

    with open(kg_file, "r", encoding="utf-8") as f:
        kg = json.load(f)

    print("\nKnowledge graph loaded:")
    print(f"  {kg['stats']['total_papers']} papers")
    print(f"  {kg['stats']['total_concepts']} concepts")

    # Example queries
    queries = [
        "What is Phi in consciousness?",
        "How does integration relate to consciousness?",
        "Quantum effects in consciousness",
        "What is qualia and phenomenal experience?",
    ]

    print("\n" + "=" * 60)
    print("SEMANTIC SEARCH TEST")
    print("=" * 60)

    for query in queries:
        print(f"\nQuery: '{query}'")

        # Embed query
        query_embedding = model.encode(query, convert_to_numpy=True)

        # Find most similar concept
        best_concept = None
        best_sim = -1.0

        for concept in kg.get("concepts", []):
            # Embed concept
            concept_embedding = model.encode(concept, convert_to_numpy=True)
            sim = cosine_similarity([query_embedding], [concept_embedding])[0][0]

            if sim > best_sim:
                best_sim = sim
                best_concept = concept

        print(f"  → Most similar concept: '{best_concept}' (score: {best_sim:.3f})")

        # Find papers about that concept
        if best_concept and best_concept in kg.get("concept_papers", {}):
            paper_ids = kg["concept_papers"][best_concept][:3]
            total_papers = len(kg["concept_papers"][best_concept])
            print(f"  → Papers: {total_papers} total")
            for pid in paper_ids:
                if pid < len(kg.get("papers", [])):
                    paper = kg["papers"][pid]
                    print(f"      • {paper.get('title', 'Unknown')[:50]}...")

    print("\n" + "=" * 60)
    print("✅ SEMANTIC SEARCH WORKING!")
    print("=" * 60)


def main() -> None:
    """Main entry point"""
    test_semantic_search()


if __name__ == "__main__":
    main()

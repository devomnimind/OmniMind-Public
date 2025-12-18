#!/usr/bin/env python
"""
Build Semantic Knowledge Graph from Consciousness Papers

Integrates with Phase 24 Semantic Memory Layer.
Uses existing papers in Qdrant or loads from JSON.

Usage:
    python scripts/build_semantic_knowledge_graph.py
    python scripts/build_semantic_knowledge_graph.py --from-phase24
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

import numpy as np  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402
from tqdm import tqdm  # noqa: E402

# Phase 24 integration
from memory.semantic_memory_layer import get_semantic_memory  # noqa: E402


def extract_keywords(text: str) -> list[str]:
    """Extract keywords from text"""
    keywords = [
        "phi",
        "consciousness",
        "integration",
        "qualia",
        "quantum",
        "entanglement",
        "coherence",
        "information",
        "differentiation",
        "neural",
        "brain",
        "awareness",
        "experience",
        "phenomenal",
        "integrated",
    ]
    text_lower = text.lower()
    return [k for k in keywords if k in text_lower]


def load_papers_from_json() -> list[dict]:
    """Load papers from JSON file"""
    papers_file = BASE_DIR / "exports" / "consciousness_papers.json"
    if not papers_file.exists():
        return []

    with open(papers_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_papers_from_phase24(limit: int | None = None) -> list[dict]:
    """Load papers from Phase 24 Semantic Memory

    Args:
        limit: Maximum number of papers to load

    Returns:
        List of paper dictionaries
    """
    print("📚 Loading papers from Phase 24 Semantic Memory...")

    semantic_memory = get_semantic_memory()

    # Search for consciousness papers
    query = "consciousness integrated information phi qualia"
    results = semantic_memory.retrieve_similar(query, top_k=limit or 1000)

    papers = []
    for result in results:
        payload = result.get("payload", {})
        if payload.get("type") == "consciousness_paper":
            papers.append(
                {
                    "title": payload.get("title", ""),
                    "abstract": payload.get("abstract", ""),
                    "year": payload.get("year", 0),
                    "arxiv_id": payload.get("arxiv_id", ""),
                }
            )

    print(f"✅ Loaded {len(papers)} papers from Phase 24")
    return papers


def build_knowledge_graph(papers: list[dict], model: SentenceTransformer) -> dict[str, any]:
    """Build semantic knowledge graph from papers

    Args:
        papers: List of paper dictionaries
        model: SentenceTransformer model

    Returns:
        Knowledge graph dictionary
    """
    print("\n📚 Building semantic knowledge graph...")

    kg = {
        "papers": [],
        "concepts": {},
        "embeddings_index": [],
    }

    print("\nEmbedding papers...")
    for i, paper in enumerate(tqdm(papers, desc="Processing papers")):
        # Embed title + abstract
        text = paper["title"] + " " + paper["abstract"]
        embedding = model.encode(text, convert_to_numpy=True)

        # Store paper
        kg["papers"].append(
            {
                "id": i,
                "title": paper["title"],
                "abstract": paper["abstract"][:200],  # First 200 chars
                "year": paper.get("year", 0),
                "arxiv_id": paper.get("arxiv_id", ""),
                "embedding_id": i,  # Reference to embeddings_index
            }
        )

        # Store embedding
        kg["embeddings_index"].append(
            {
                "id": i,
                "embedding": embedding.tolist(),  # Convert to list for JSON
                "norm": float(np.linalg.norm(embedding)),
            }
        )

        # Extract concepts (keywords)
        concepts = extract_keywords(text)
        for concept in concepts:
            if concept not in kg["concepts"]:
                kg["concepts"][concept] = {
                    "papers": [],
                    "embedding": model.encode(concept).tolist(),
                }
            kg["concepts"][concept]["papers"].append(i)

    print("\n✅ Knowledge graph ready!")
    print(f"   {len(kg['papers'])} papers")
    print(f"   {len(kg['concepts'])} concepts")

    return kg


def save_knowledge_graph(kg: dict[str, any], output_file: Path) -> None:
    """Save knowledge graph to JSON (compact format)

    Args:
        kg: Knowledge graph dictionary
        output_file: Output file path
    """
    # Save (compact format)
    output = {
        "papers": kg["papers"],
        "concepts": list(kg["concepts"].keys()),  # Just names
        "concept_papers": {k: v["papers"] for k, v in kg["concepts"].items()},
        "stats": {
            "total_papers": len(kg["papers"]),
            "total_concepts": len(kg["concepts"]),
        },
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build semantic knowledge graph from consciousness papers"
    )
    parser.add_argument(
        "--from-phase24",
        action="store_true",
        help="Load papers from Phase 24 Semantic Memory instead of JSON",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of papers to process",
    )
    args = parser.parse_args()

    # Load model
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")

    # Load papers
    if args.from_phase24:
        papers = load_papers_from_phase24(limit=args.limit)
    else:
        papers = load_papers_from_json()
        if args.limit:
            papers = papers[: args.limit]

    if not papers:
        print("⚠️  No papers found. Run download_consciousness_papers.py first")
        print("   Or use --from-phase24 to load from Phase 24 Semantic Memory")
        sys.exit(1)

    # Build knowledge graph
    kg = build_knowledge_graph(papers, model)

    # Save
    output_file = BASE_DIR / "exports" / "knowledge_graph_compact.json"
    save_knowledge_graph(kg, output_file)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""
Download Consciousness Papers from HuggingFace

Integrates with Phase 24 Semantic Memory Layer.
Downloads papers and stores them in Qdrant via SemanticMemoryLayer.

Usage:
    python scripts/download_consciousness_papers.py
    python scripts/download_consciousness_papers.py --limit 500
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

# Phase 24 integration
from datetime import datetime, timezone  # noqa: E402

from memory.semantic_memory_layer import get_semantic_memory  # noqa: E402

try:
    from datasets import load_dataset  # noqa: E402
    from tqdm import tqdm  # noqa: E402
except ImportError:
    print("❌ Instalar: pip install datasets tqdm")
    sys.exit(1)


def download_papers(limit: int | None = None, save_json: bool = True) -> list[dict]:
    """Download consciousness papers from HuggingFace

    Args:
        limit: Maximum number of papers to download (None = all)
        save_json: Whether to save to JSON file

    Returns:
        List of paper dictionaries
    """
    print("⏳ Downloading consciousness papers from HuggingFace...")
    print("   This will take ~10-15 minutes, runs in background")

    # Load arxiv papers dataset
    try:
        papers = load_dataset("scientific_papers", "arxiv", split="train")
        print(f"✅ Loaded dataset: {len(papers)} total papers")
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return []

    # Keywords for filtering
    keywords = [
        "consciousness",
        "integrated information",
        "iit",
        "phi",
        "qualia",
        "phenomenal",
        "quantum consciousness",
        "entanglement",
        "brain",
        "neural correlates",
        "awareness",
        "experience",
    ]

    consciousness_papers = []
    count = 0

    print("\nFiltering papers...")
    total = limit if limit else len(papers)

    for paper in tqdm(papers, total=total):
        if limit and count >= limit:
            break

        # Combine title + abstract for search
        text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()

        # Check if any keyword matches
        if any(keyword in text for keyword in keywords):
            consciousness_papers.append(
                {
                    "title": paper.get("title", ""),
                    "abstract": paper.get("abstract", ""),
                    "year": paper.get("year", 0),
                    "arxiv_id": paper.get("arxiv_id", ""),
                }
            )
            count += 1

            # Progress
            if count % 100 == 0:
                print(f"   Found {count} papers so far...")

    print(f"\n✅ Found {len(consciousness_papers)} consciousness papers")

    # Save to JSON
    if save_json:
        exports_dir = BASE_DIR / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        output_file = exports_dir / "consciousness_papers.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(consciousness_papers, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved to {output_file}")  # noqa: F541

    # Show sample
    if consciousness_papers:
        print("\nSample papers:")
        for p in consciousness_papers[:3]:
            print(f"  • {p['title'][:60]}...")

    return consciousness_papers


def store_in_phase24(papers: list[dict]) -> None:
    """Store papers in Phase 24 Semantic Memory Layer

    Args:
        papers: List of paper dictionaries
    """
    print("\n📚 Storing papers in Phase 24 Semantic Memory...")

    semantic_memory = get_semantic_memory()
    stored_count = 0

    for paper in tqdm(papers, desc="Storing in Qdrant"):
        try:
            # Create episode text
            episode_text = f"{paper['title']}. {paper['abstract'][:500]}"

            # Create episode data
            episode_data = {
                "phi_value": 0.0,  # Papers don't have phi, but structure needs it
                "type": "consciousness_paper",
                "arxiv_id": paper.get("arxiv_id", ""),
                "year": paper.get("year", 0),
                "title": paper["title"],
                "abstract": paper["abstract"][:1000],  # Truncate for storage
            }

            # Store via Phase 24
            episode_id = semantic_memory.store_episode(
                episode_text=episode_text,
                episode_data=episode_data,
                timestamp=datetime.now(timezone.utc),
            )

            if episode_id:
                stored_count += 1

        except Exception as e:
            print(f"⚠️  Error storing paper '{paper.get('title', 'unknown')}': {e}")

    print(f"\n✅ Stored {stored_count}/{len(papers)} papers in Phase 24 Semantic Memory")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download consciousness papers and store in Phase 24"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of papers to download (default: all)",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Don't save to JSON file",
    )
    parser.add_argument(
        "--no-phase24",
        action="store_true",
        help="Don't store in Phase 24 Semantic Memory",
    )
    args = parser.parse_args()

    # Download papers
    papers = download_papers(limit=args.limit, save_json=not args.no_json)

    if not papers:
        print("❌ No papers downloaded")
        sys.exit(1)

    # Store in Phase 24 if requested
    if not args.no_phase24:
        store_in_phase24(papers)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()

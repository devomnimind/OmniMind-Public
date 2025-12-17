#!/usr/bin/env python
"""
Load Datasets for Phi Semantic Awareness

Loads downloaded HuggingFace datasets and integrates with Phase 24.

Usage:
    python scripts/load_datasets_for_phi.py
    python scripts/load_datasets_for_phi.py --build-index
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

try:
    from datasets import load_from_disk  # noqa: E402
    from sentence_transformers import SentenceTransformer  # noqa: E402
except ImportError:
    print("❌ Instalar: pip install datasets sentence-transformers")
    sys.exit(1)

# Phase 24 integration
from memory.semantic_memory_layer import get_semantic_memory  # noqa: E402
from datetime import datetime, timezone  # noqa: E402


class PhiDatasetLoader:
    """Loads and integrates HuggingFace datasets with Phase 24"""

    def __init__(self, data_dir: Path | None = None):
        """Initialize loader

        Args:
            data_dir: Data directory (default: data/datasets)
        """
        if data_dir is None:
            data_dir = BASE_DIR / "data" / "datasets"

        self.data_dir = Path(data_dir)
        self.semantic_memory = get_semantic_memory()
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def load_scientific_papers(self) -> dict | None:
        """Load scientific papers dataset

        Returns:
            Dataset dict or None if not found
        """
        papers_dir = self.data_dir / "scientific_papers_arxiv"
        if not papers_dir.exists():
            print(f"⚠️  Scientific papers not found at {papers_dir}")
            return None

        print(f"📚 Loading scientific papers from {papers_dir}...")
        try:
            papers = load_from_disk(str(papers_dir))
            print(f"✅ Loaded {len(papers)} papers")
            return {"papers": papers, "type": "scientific_papers"}
        except Exception as e:
            print(f"❌ Error loading papers: {e}")
            return None

    def load_dbpedia(self) -> dict | None:
        """Load DBpedia ontology dataset

        Returns:
            Dataset dict or None if not found
        """
        dbpedia_dir = self.data_dir / "dbpedia_ontology"
        if not dbpedia_dir.exists():
            print(f"⚠️  DBpedia ontology not found at {dbpedia_dir}")
            return None

        print(f"📚 Loading DBpedia ontology from {dbpedia_dir}...")
        try:
            dbpedia = load_from_disk(str(dbpedia_dir))
            total_triples = sum(len(split) for split in dbpedia.values())
            print(f"✅ Loaded {total_triples} triples")
            return {"dbpedia": dbpedia, "type": "dbpedia", "triples": total_triples}
        except Exception as e:
            print(f"❌ Error loading DBpedia: {e}")
            return None

    def load_qasper(self) -> dict | None:
        """Load QASPER dataset

        Returns:
            Dataset dict or None if not found
        """
        qasper_dir = self.data_dir / "qasper_qa"
        if not qasper_dir.exists():
            print(f"⚠️  QASPER not found at {qasper_dir}")
            return None

        print(f"📚 Loading QASPER from {qasper_dir}...")
        try:
            qasper = load_from_disk(str(qasper_dir))
            total_qa = sum(len(split) for split in qasper.values())
            print(f"✅ Loaded {total_qa} QA pairs")
            return {"qasper": qasper, "type": "qasper", "qa_pairs": total_qa}
        except Exception as e:
            print(f"❌ Error loading QASPER: {e}")
            return None

    def load_pubmed_rct(self) -> dict | None:
        """Load PubMed RCT20K dataset

        Returns:
            Dataset dict or None if not found
        """
        pubmed_dir = self.data_dir / "pubmed_rct20k"
        if not pubmed_dir.exists():
            print(f"⚠️  PubMed RCT20K not found at {pubmed_dir}")
            return None

        print(f"📚 Loading PubMed RCT20K from {pubmed_dir}...")
        try:
            pubmed = load_from_disk(str(pubmed_dir))
            total_entries = sum(len(split) for split in pubmed.values())
            print(f"✅ Loaded {total_entries} entries")
            return {
                "pubmed_rct": pubmed,
                "type": "pubmed_rct",
                "entries": total_entries,
            }
        except Exception as e:
            print(f"❌ Error loading PubMed RCT20K: {e}")
            return None

    def load_gene_ontology(self) -> dict | None:
        """Load Gene Ontology dataset

        Returns:
            Dataset dict or None if not found
        """
        gene_dir = self.data_dir / "gene_ontology"
        if not gene_dir.exists():
            print(f"⚠️  Gene Ontology not found at {gene_dir}")
            return None

        print(f"📚 Loading Gene Ontology from {gene_dir}...")
        try:
            gene_ontology = load_from_disk(str(gene_dir))
            total_entries = sum(len(split) for split in gene_ontology.values())
            print(f"✅ Loaded {total_entries} entries")
            return {
                "gene_ontology": gene_ontology,
                "type": "gene_ontology",
                "entries": total_entries,
            }
        except Exception as e:
            print(f"❌ Error loading Gene Ontology: {e}")
            return None

    def store_papers_in_phase24(self, papers_data: dict, limit: int = 100) -> int:
        """Store papers in Phase 24 Semantic Memory

        Args:
            papers_data: Papers dataset dict
            limit: Maximum papers to store (default: 100)

        Returns:
            Number of papers stored
        """
        if papers_data is None or "papers" not in papers_data:
            return 0

        papers = papers_data["papers"]
        stored = 0

        print(f"\n📚 Storing papers in Phase 24 Semantic Memory (limit: {limit})...")

        for i, paper in enumerate(papers):
            if i >= limit:
                break

            try:
                # Extract text - dataset structure: article (str), abstract (str), section_names (list)
                article = paper.get("article", "")
                abstract = paper.get("abstract", "")

                # article is a string (full text), not a dict
                # Extract first line or first 200 chars as title
                if article:
                    # Try to extract title (first line or first sentence)
                    article_lines = article.split("\n")
                    title = article_lines[0][:200] if article_lines else article[:200]
                else:
                    title = ""

                if not article and not abstract:
                    continue

                # Use article as main text, abstract as supplement
                if article:
                    episode_text = f"{title}. {article[:500]}"
                else:
                    episode_text = f"{abstract[:500]}"

                # Create episode data
                episode_data = {
                    "phi_value": 0.0,
                    "type": "scientific_paper",
                    "source": "huggingface_scientific_papers",
                    "title": title[:200] if title else "Untitled",
                    "abstract": abstract[:1000] if abstract else "",
                    "article_preview": article[:500] if article else "",
                }

                # Store via Phase 24
                episode_id = self.semantic_memory.store_episode(
                    episode_text=episode_text,
                    episode_data=episode_data,
                    timestamp=datetime.now(timezone.utc),
                )

                if episode_id:
                    stored += 1

                if (i + 1) % 10 == 0:
                    print(f"   Stored {i + 1}/{min(limit, len(papers))} papers...")

            except Exception as e:
                print(f"⚠️  Error storing paper {i}: {e}")

        print(f"✅ Stored {stored} papers in Phase 24")
        return stored

    def load_all(self) -> dict:
        """Load all available datasets

        Returns:
            Dictionary with loaded datasets
        """
        print("=" * 60)
        print("LOADING DATASETS FOR PHI")
        print("=" * 60)

        datasets = {}

        # Load each dataset
        papers = self.load_scientific_papers()
        if papers:
            datasets["scientific_papers"] = papers

        dbpedia = self.load_dbpedia()
        if dbpedia:
            datasets["dbpedia"] = dbpedia

        qasper = self.load_qasper()
        if qasper:
            datasets["qasper"] = qasper

        pubmed = self.load_pubmed_rct()
        if pubmed:
            datasets["pubmed_rct"] = pubmed

        gene_ontology = self.load_gene_ontology()
        if gene_ontology:
            datasets["gene_ontology"] = gene_ontology

        # Summary
        print("\n" + "=" * 60)
        print("LOADED DATASETS SUMMARY")
        print("=" * 60)

        for name, data in datasets.items():
            print(f"✅ {name}: {data.get('type', 'unknown')}")

        return datasets


def main() -> None:
    parser = argparse.ArgumentParser(description="Load HuggingFace datasets for Phi")
    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Build embeddings index (not yet implemented)",
    )
    parser.add_argument(
        "--store-papers",
        action="store_true",
        help="Store papers in Phase 24 Semantic Memory",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Limit papers to store (default: 100)",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Data directory (default: data/datasets)",
    )
    args = parser.parse_args()

    # Initialize loader
    data_dir = Path(args.data_dir) if args.data_dir else None
    loader = PhiDatasetLoader(data_dir=data_dir)

    # Load all datasets
    datasets = loader.load_all()

    if not datasets:
        print("\n⚠️  No datasets found. Run scripts/setup_huggingface_datasets.py first")
        sys.exit(1)

    # Store papers in Phase 24 if requested
    if args.store_papers and "scientific_papers" in datasets:
        loader.store_papers_in_phase24(datasets["scientific_papers"], limit=args.limit)

    # Build index (future feature)
    if args.build_index:
        print("\n⚠️  Build index not yet implemented")

    print("\n✅ Done!")


if __name__ == "__main__":
    main()

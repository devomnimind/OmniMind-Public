#!/usr/bin/env python
"""
Setup HuggingFace Datasets for OmniMind

Downloads and configures TIER 1 datasets:
1. armanc/scientific_papers (ArXiv) - 12 GB
2. CleverThis/dbpedia-ontology - 0.8 GB
3. allenai/qasper - Small
4. armanc/pubmed-rct20k - PubMed RCT
5. CleverThis/gene-ontology - Gene Ontology (requires login)

TIER 2 datasets (Phase 26 expansion):
6. OSS-forge/HumanVsAICode - Human vs AI code comparison
7. TuringEnterprises/Turing-Open-Reasoning - Open reasoning dataset
8. openbmb/InfLLM-V2-data-5B - Large-scale instruction data (5B)

Integrates with Phase 24 Semantic Memory.

Usage:
    python scripts/setup_huggingface_datasets.py
    python scripts/setup_huggingface_datasets.py --tier 1 --limit 10000
    python scripts/setup_huggingface_datasets.py --check-only
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

try:
    from huggingface_hub import login, whoami  # noqa: E402

    from datasets import load_dataset  # noqa: E402
except ImportError:
    print("❌ Instalar: pip install datasets huggingface_hub")
    sys.exit(1)


def check_hf_credentials() -> tuple[bool, str | None]:
    """Check if HuggingFace credentials are configured

    Returns:
        Tuple of (is_configured, token_or_error_message)
    """
    # Check environment variables
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")

    if not token:
        # Check .huggingface/token file
        hf_token_file = Path.home() / ".huggingface" / "token"
        if hf_token_file.exists():
            try:
                token = hf_token_file.read_text().strip()
            except Exception:
                pass

    if not token:
        # Check huggingface_hub cache (where huggingface-cli login saves)
        hf_cache_token = Path.home() / ".cache" / "huggingface" / "token"
        if hf_cache_token.exists():
            try:
                token = hf_cache_token.read_text().strip()
            except Exception:
                pass

    if not token:
        # Try using huggingface_hub's default token loading
        try:
            from huggingface_hub import HfFolder

            token = HfFolder.get_token()
        except Exception:
            pass

    if not token:
        return (
            False,
            "No HF_TOKEN or HUGGING_FACE_HUB_TOKEN found. "
            "Run 'huggingface-cli login' or set HF_TOKEN in .env",
        )

    # Verify token works
    try:
        user_info = whoami(token=token)  # Verify token is valid
        username = user_info.get("name", "unknown")
        return True, f"{token[:10]}... (user: {username})"
    except Exception as e:
        return False, f"Token invalid or expired: {e}"


def setup_scientific_papers(
    data_dir: Path, limit: int | None = None, token: str | None = None
) -> bool:
    """Download scientific_papers dataset (ArXiv)

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of papers (None = all)
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("1. Downloading armanc/scientific_papers (ArXiv)...")
    print("=" * 60)

    try:
        # Load dataset (with limit if specified)
        if limit:
            print(f"   Loading first {limit} papers...")
            papers = load_dataset(
                "armanc/scientific_papers",
                "arxiv",
                split=f"train[:{limit}]",
                token=token,
            )
        else:
            print("   Loading all papers (this will take time)...")
            papers = load_dataset("armanc/scientific_papers", "arxiv", token=token)

        # Save to disk
        output_dir = data_dir / "scientific_papers_arxiv"
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"   Saving {len(papers)} papers to {output_dir}...")
        papers.save_to_disk(str(output_dir))

        print(f"   ✅ Saved {len(papers)} papers")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def setup_dbpedia_ontology(data_dir: Path, token: str | None = None) -> bool:
    """Download DBpedia ontology dataset

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("2. Downloading CleverThis/dbpedia-ontology...")
    print("=" * 60)

    try:
        dbpedia = load_dataset("CleverThis/dbpedia-ontology", token=token)

        # Save to disk
        output_dir = data_dir / "dbpedia_ontology"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Count triples
        total_triples = sum(len(split) for split in dbpedia.values())

        print(f"   Saving {total_triples} triples to {output_dir}...")
        dbpedia.save_to_disk(str(output_dir))

        print(f"   ✅ Saved {total_triples} triples")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def setup_qasper(data_dir: Path, token: str | None = None) -> bool:
    """Download QASPER dataset

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("3. Downloading allenai/qasper...")
    print("=" * 60)

    try:
        qasper = load_dataset("allenai/qasper", token=token)

        # Save to disk
        output_dir = data_dir / "qasper_qa"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Count QA pairs
        total_qa = sum(len(split) for split in qasper.values())

        print(f"   Saving {total_qa} QA pairs to {output_dir}...")
        qasper.save_to_disk(str(output_dir))

        print(f"   ✅ Saved {total_qa} QA pairs")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def setup_pubmed_rct(data_dir: Path, token: str | None = None) -> bool:
    """Download PubMed RCT20K dataset

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("4. Downloading armanc/pubmed-rct20k...")
    print("=" * 60)

    try:
        pubmed = load_dataset("armanc/pubmed-rct20k", token=token)

        # Save to disk
        output_dir = data_dir / "pubmed_rct20k"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Count entries
        total_entries = sum(len(split) for split in pubmed.values())

        print(f"   Saving {total_entries} entries to {output_dir}...")
        pubmed.save_to_disk(str(output_dir))

        print(f"   ✅ Saved {total_entries} entries")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def setup_gene_ontology(data_dir: Path, token: str | None = None) -> bool:
    """Download Gene Ontology dataset

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("5. Downloading CleverThis/gene-ontology...")
    print("=" * 60)
    print("   ⚠️  Requires HuggingFace login (huggingface-cli login)")

    try:
        gene_ontology = load_dataset("CleverThis/gene-ontology", token=token)

        # Save to disk
        output_dir = data_dir / "gene_ontology"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Count entries
        total_entries = sum(len(split) for split in gene_ontology.values())

        print(f"   Saving {total_entries} entries to {output_dir}...")
        gene_ontology.save_to_disk(str(output_dir))

        print(f"   ✅ Saved {total_entries} entries")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   💡 Tip: Run 'huggingface-cli login' to access this dataset")
        return False


def setup_human_vs_ai_code(
    data_dir: Path, limit: int | None = None, token: str | None = None
) -> bool:
    """Download HumanVsAICode dataset

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all)
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("6. Downloading OSS-forge/HumanVsAICode...")
    print("=" * 60)

    try:
        if limit:
            print(f"   Loading first {limit} items...")
            dataset = load_dataset(
                "OSS-forge/HumanVsAICode",
                split=f"train[:{limit}]",
                token=token,
                trust_remote_code=True,
            )
        else:
            print("   Loading all items...")
            dataset = load_dataset(
                "OSS-forge/HumanVsAICode",
                token=token,
                trust_remote_code=True,
            )

        save_path = data_dir / "human_vs_ai_code"
        dataset.save_to_disk(str(save_path))
        print(f"✅ Saved to {save_path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def setup_turing_reasoning(
    data_dir: Path, limit: int | None = None, token: str | None = None
) -> bool:
    """Download Turing-Open-Reasoning dataset

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all)
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("7. Downloading TuringEnterprises/Turing-Open-Reasoning...")
    print("=" * 60)

    try:
        if limit:
            print(f"   Loading first {limit} items...")
            dataset = load_dataset(
                "TuringEnterprises/Turing-Open-Reasoning",
                split=f"train[:{limit}]",
                token=token,
                trust_remote_code=True,
            )
        else:
            print("   Loading all items...")
            dataset = load_dataset(
                "TuringEnterprises/Turing-Open-Reasoning",
                token=token,
                trust_remote_code=True,
            )

        save_path = data_dir / "turing_reasoning"
        dataset.save_to_disk(str(save_path))
        print(f"✅ Saved to {save_path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def setup_infllm_data(data_dir: Path, limit: int | None = None, token: str | None = None) -> bool:
    """Download InfLLM-V2-data-5B dataset

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all, WARNING: 5B is huge!)
        token: HF token for authentication

    Returns:
        True if successful
    """
    print("\n" + "=" * 60)
    print("8. Downloading openbmb/InfLLM-V2-data-5B...")
    print("=" * 60)
    print("⚠️  WARNING: This dataset is 5B items. Use --limit for testing!")

    try:
        if limit:
            print(f"   Loading first {limit} items...")
            dataset = load_dataset(
                "openbmb/InfLLM-V2-data-5B",
                split=f"train[:{limit}]",
                token=token,
                trust_remote_code=True,
            )
        else:
            print("   Loading all items (this will take VERY long time)...")
            dataset = load_dataset(
                "openbmb/InfLLM-V2-data-5B",
                token=token,
                trust_remote_code=True,
            )

        save_path = data_dir / "infllm_v2_data"
        dataset.save_to_disk(str(save_path))
        print(f"✅ Saved to {save_path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Setup HuggingFace datasets for OmniMind")
    parser.add_argument(
        "--tier",
        type=int,
        default=1,
        choices=[1, 2],
        help="Dataset tier to download (1=essential, 2=full)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of papers for scientific_papers dataset (default: all)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check credentials, don't download",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Data directory (default: data/datasets)",
    )
    args = parser.parse_args()

    # Determine data directory
    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = BASE_DIR / "data" / "datasets"

    data_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("HUGGINGFACE DATASETS SETUP - OmniMind")
    print("=" * 60)

    # Check credentials
    print("\nChecking HuggingFace credentials...")
    is_configured, token_or_error = check_hf_credentials()

    if not is_configured:
        print(f"⚠️  {token_or_error}")
        print("\nTo configure:")
        print("  1. Set HF_TOKEN or HUGGING_FACE_HUB_TOKEN in .env")
        print("  2. Or run: huggingface-cli login")
        print("  3. Or create ~/.huggingface/token with your token")
        print("\nContinuing without token (may have rate limits)...")
        token = None
    else:
        print(f"✅ Credentials OK (token: {token_or_error[:10]}...)")
        token = token_or_error

    if args.check_only:
        print("\n✅ Check complete")
        return

    # Download TIER 1 datasets
    if args.tier >= 1:
        print("\n" + "=" * 60)
        print("DOWNLOADING TIER 1 DATASETS (Essential)")
        print("=" * 60)

        results = {
            "scientific_papers": setup_scientific_papers(data_dir, limit=args.limit, token=token),
            "dbpedia": setup_dbpedia_ontology(data_dir, token=token),
            "qasper": setup_qasper(data_dir, token=token),
        }

        # Summary
        print("\n" + "=" * 60)
        print("DOWNLOAD SUMMARY")
        print("=" * 60)

        for name, success in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {name}")

        if all(results.values()):
            print("\n✅ All TIER 1 datasets downloaded successfully!")
        else:
            print("\n⚠️  Some datasets failed to download")
            sys.exit(1)

    # TIER 2: Phase 26 Expansion datasets
    if args.tier >= 2:
        print("\n" + "=" * 60)
        print("DOWNLOADING TIER 2 DATASETS (Phase 26 Expansion)")
        print("=" * 60)

        tier2_results = {
            "human_vs_ai_code": setup_human_vs_ai_code(data_dir, limit=args.limit, token=token),
            "turing_reasoning": setup_turing_reasoning(data_dir, limit=args.limit, token=token),
            "infllm_data": setup_infllm_data(data_dir, limit=args.limit, token=token),
        }

        # Summary
        print("\n" + "=" * 60)
        print("TIER 2 DOWNLOAD SUMMARY")
        print("=" * 60)

        for name, success in tier2_results.items():
            status = "✅" if success else "❌"
            print(f"{status} {name}")

        if all(tier2_results.values()):
            print("\n✅ All TIER 2 datasets downloaded successfully!")
        else:
            print("\n⚠️  Some TIER 2 datasets failed to download")

    print(f"\n💾 Datasets saved to: {data_dir}")
    print("\n✅ Setup complete!")


if __name__ == "__main__":
    main()

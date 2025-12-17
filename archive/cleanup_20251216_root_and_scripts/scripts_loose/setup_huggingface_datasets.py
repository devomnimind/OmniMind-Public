#!/usr/bin/env python
"""
Setup HuggingFace Datasets for OmniMind

Downloads and configures TIER 1 datasets:
1. ccdv/arxiv-summarization (ArXiv papers) - Alternative to armanc/scientific_papers
2. CleverThis/dbpedia-ontology - 0.8 GB
3. stanfordnlp/squad - QA dataset (Alternative to allenai/qasper)
4. armanc/pubmed-rct20k - PubMed RCT
5. CleverThis/gene-ontology - Gene Ontology (requires login)

TIER 2 datasets (Phase 26 expansion):
6. OSS-forge/HumanVsAICode - Human vs AI code comparison
7. TuringEnterprises/Turing-Open-Reasoning - Open reasoning dataset
8. openbmb/InfLLM-V2-data-5B - Large-scale instruction data (5B)

TIER 3 datasets (Benchmark & Advanced):
9. yang31210999/gptoss-0808_BenchMark-H100-d2 - GSM8K & GPQA benchmarks
10. nick007x/arxiv-papers - ArXiv papers in parquet format
11. TuringEnterprises/Turing-Open-Reasoning - Open reasoning in JSON format

Integrates with Phase 24 Semantic Memory.

Usage:
    python scripts/setup_huggingface_datasets.py
    python scripts/setup_huggingface_datasets.py --tier 1 --limit 10000
    python scripts/setup_huggingface_datasets.py --tier 3 --limit 5000
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

# Load .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.exists():
    try:
        from dotenv import load_dotenv

        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    except ImportError:
        print("⚠️  python-dotenv not installed, .env file not loaded")
    except Exception as e:
        print(f"⚠️  Error loading .env file: {e}")

try:
    from huggingface_hub import whoami  # noqa: E402  # type: ignore

    from datasets import load_dataset, load_from_disk  # noqa: E402  # type: ignore

    DATASETS_AVAILABLE = True
except ImportError:
    print("❌ Instalar: pip install datasets huggingface_hub pandas python-dotenv")
    DATASETS_AVAILABLE = False
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
        # Check if offline mode is enabled
        if os.getenv("HF_HUB_OFFLINE") == "1":
            return True, f"{token[:10]}... (offline mode)"

        user_info = whoami(token=token)  # Verify token is valid
        username = user_info.get("name", "unknown")
        return True, f"{token[:10]}... (user: {username})"
    except Exception as e:
        return False, f"Token invalid or expired: {e}"


def check_dataset_exists(data_dir: Path, dataset_name: str) -> tuple[bool, str]:
    """
    Check if a dataset already exists and is valid.

    Args:
        data_dir: Directory containing datasets
        dataset_name: Name of the dataset directory

    Returns:
        Tuple of (exists_and_valid, status_message)
    """
    dataset_path = data_dir / dataset_name

    if not dataset_path.exists():
        return False, "Dataset not found"

    # Check if it's a HuggingFace dataset directory
    dataset_info_file = dataset_path / "dataset_info.json"
    if dataset_info_file.exists():
        try:
            # Try to load the dataset to verify it's not corrupted
            if DATASETS_AVAILABLE:
                load_from_disk(str(dataset_path))
                return True, "Dataset exists and is valid"
            else:
                return True, "Dataset exists (cannot verify without datasets library)"
        except Exception as e:
            return False, f"Dataset exists but corrupted: {e}"

    # Check for other file types
    files = list(dataset_path.glob("*"))
    if files:
        return True, f"Dataset exists ({len(files)} files)"

    return False, "Dataset directory exists but is empty"


def should_download_dataset(
    data_dir: Path, dataset_name: str, force: bool = False
) -> tuple[bool, str]:
    """
    Determine if a dataset should be downloaded.

    Args:
        data_dir: Directory containing datasets
        dataset_name: Name of the dataset directory
        force: Force download even if exists

    Returns:
        Tuple of (should_download, reason)
    """
    if force:
        return True, "Forced download"

    exists, status = check_dataset_exists(data_dir, dataset_name)
    if exists:
        return False, f"Already exists: {status}"

    return True, "Dataset not found, will download"


def setup_scientific_papers(
    data_dir: Path, limit: int | None = None, token: str | None = None, force: bool = False
) -> bool:
    """Download scientific_papers dataset (ArXiv) - Using alternative dataset

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of papers (None = all)
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "arxiv_summarization"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

    print("\n" + "=" * 60)
    print("1. Downloading ccdv/arxiv-summarization (ArXiv alternative)...")
    print("=" * 60)

    try:
        # Load alternative dataset (arxiv-summarization)
        if limit:
            print(f"   Loading first {limit} papers...")
            papers = load_dataset(
                "ccdv/arxiv-summarization",
                split=f"train[:{limit}]",
                token=token,
            )
        else:
            print("   Loading all papers (this will take time)...")
            papers = load_dataset("ccdv/arxiv-summarization", split="train", token=token)

        # Save to disk
        output_dir = data_dir / dataset_name
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"   Saving {len(papers)} papers to {output_dir}...")
        papers.save_to_disk(str(output_dir))

        print(f"   ✅ Saved {len(papers)} papers")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def setup_dbpedia_ontology(data_dir: Path, token: str | None = None, force: bool = False) -> bool:
    """Download DBpedia ontology dataset

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "dbpedia_ontology"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

    print("\n" + "=" * 60)
    print("2. Downloading CleverThis/dbpedia-ontology...")
    print("=" * 60)

    try:
        dbpedia = load_dataset("CleverThis/dbpedia-ontology", token=token)

        # Save to disk
        output_dir = data_dir / dataset_name
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


def setup_qasper(data_dir: Path, token: str | None = None, force: bool = False) -> bool:
    """Download QASPER dataset - Using SQuAD alternative

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "squad_qa"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

    print("\n" + "=" * 60)
    print("3. Downloading stanfordnlp/squad (QASPER alternative)...")
    print("=" * 60)

    try:
        qasper = load_dataset("squad", token=token)

        # Save to disk
        output_dir = data_dir / dataset_name
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


def setup_pubmed_rct(data_dir: Path, token: str | None = None, force: bool = False) -> bool:
    """Download PubMed RCT20K dataset

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "pubmed_rct20k"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

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


def setup_gene_ontology(data_dir: Path, token: str | None = None, force: bool = False) -> bool:
    """Download Gene Ontology dataset

    Args:
        data_dir: Directory to save dataset
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "gene_ontology"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

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
    data_dir: Path, limit: int | None = None, token: str | None = None, force: bool = False
) -> bool:
    """Download HumanVsAICode dataset

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all)
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "human_vs_ai_code"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

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
    data_dir: Path, limit: int | None = None, token: str | None = None, force: bool = False
) -> bool:
    """Download Turing-Open-Reasoning dataset

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all)
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "turing_reasoning"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

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


def setup_infllm_data(
    data_dir: Path, limit: int | None = None, token: str | None = None, force: bool = False
) -> bool:
    """Download InfLLM-V2-data-5B dataset

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all, WARNING: 5B is huge!)
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "infllm_v2_data"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

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


def setup_gsm8k_gpqa(
    data_dir: Path, limit: int | None = None, token: str | None = None, force: bool = False
) -> bool:
    """Download GSM8K and GPQA datasets from yang31210999/gptoss-0808_BenchMark-H100-d2

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all)
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "gsm8k_gpqa_benchmark"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

    print("\n" + "=" * 60)
    print("9. Downloading yang31210999/gptoss-0808_BenchMark-H100-d2 (GSM8K & GPQA)...")
    print("=" * 60)

    try:
        # Load the dataset
        if limit:
            print(f"   Loading first {limit} items...")
            dataset = load_dataset(
                "yang31210999/gptoss-0808_BenchMark-H100-d2",
                split=f"train[:{limit}]",
                token=token,
                trust_remote_code=True,
            )
        else:
            print("   Loading all items...")
            dataset = load_dataset(
                "yang31210999/gptoss-0808_BenchMark-H100-d2",
                token=token,
                trust_remote_code=True,
            )

        save_path = data_dir / "gsm8k_gpqa_benchmark"
        dataset.save_to_disk(str(save_path))
        print(f"✅ Saved GSM8K/GPQA benchmark to {save_path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def setup_arxiv_papers(
    data_dir: Path, limit: int | None = None, token: str | None = None, force: bool = False
) -> bool:
    """Download arxiv-papers dataset from nick007x/arxiv-papers (parquet format)

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all)
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "arxiv_papers_parquet"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

    print("\n" + "=" * 60)
    print("10. Downloading nick007x/arxiv-papers (parquet)...")
    print("=" * 60)

    try:
        # Load the parquet dataset
        if limit:
            print(f"   Loading first {limit} papers...")
            dataset = load_dataset(
                "nick007x/arxiv-papers",
                split=f"train[:{limit}]",
                token=token,
                trust_remote_code=True,
            )
        else:
            print("   Loading all papers...")
            dataset = load_dataset(
                "nick007x/arxiv-papers",
                token=token,
                trust_remote_code=True,
            )

        save_path = data_dir / "arxiv_papers_parquet"
        dataset.save_to_disk(str(save_path))
        print(f"✅ Saved arxiv papers to {save_path}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def setup_turing_open_reasoning(
    data_dir: Path, limit: int | None = None, token: str | None = None, force: bool = False
) -> bool:
    """Download Turing-Open-Reasoning dataset (JSON format)

    Args:
        data_dir: Directory to save dataset
        limit: Limit number of items (None = all)
        token: HF token for authentication
        force: Force download even if exists

    Returns:
        True if successful
    """
    dataset_name = "turing_open_reasoning_json"
    should_download, reason = should_download_dataset(data_dir, dataset_name, force)

    if not should_download:
        print(f"⏭️  Skipping {dataset_name}: {reason}")
        return True

    print("\n" + "=" * 60)
    print("11. Downloading TuringEnterprises/Turing-Open-Reasoning (JSON)...")
    print("=" * 60)

    try:
        # Load the JSON dataset
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

        save_path = data_dir / "turing_open_reasoning_json"
        dataset.save_to_disk(str(save_path))
        print(f"✅ Saved Turing open reasoning to {save_path}")
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
        choices=[1, 2, 3],
        help="Dataset tier to download (1=essential, 2=expansion, 3=benchmark)",
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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if datasets already exist",
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
        print(f"✅ Credentials OK (token: {token_or_error[:10]}...)")  # type: ignore
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
            "scientific_papers": setup_scientific_papers(
                data_dir, limit=args.limit, token=token, force=args.force
            ),
            "dbpedia": setup_dbpedia_ontology(data_dir, token=token, force=args.force),
            "qasper": setup_qasper(data_dir, token=token, force=args.force),
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
            "human_vs_ai_code": setup_human_vs_ai_code(
                data_dir, limit=args.limit, token=token, force=args.force
            ),
            "turing_reasoning": setup_turing_reasoning(
                data_dir, limit=args.limit, token=token, force=args.force
            ),
            "infllm_data": setup_infllm_data(
                data_dir, limit=args.limit, token=token, force=args.force
            ),
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

    # TIER 3: Benchmark datasets (GSM8K, GPQA, ArXiv papers, Turing reasoning)
    if args.tier >= 3:
        print("\n" + "=" * 60)
        print("DOWNLOADING TIER 3 DATASETS (Benchmark & Advanced)")
        print("=" * 60)

        tier3_results = {
            "gsm8k_gpqa": setup_gsm8k_gpqa(
                data_dir, limit=args.limit, token=token, force=args.force
            ),
            "arxiv_papers": setup_arxiv_papers(
                data_dir, limit=args.limit, token=token, force=args.force
            ),
            "turing_open_reasoning": setup_turing_open_reasoning(
                data_dir, limit=args.limit, token=token, force=args.force
            ),
        }

        # Summary
        print("\n" + "=" * 60)
        print("TIER 3 DOWNLOAD SUMMARY")
        print("=" * 60)

        for name, success in tier3_results.items():
            status = "✅" if success else "❌"
            print(f"{status} {name}")

        if all(tier3_results.values()):
            print("\n✅ All TIER 3 datasets downloaded successfully!")
        else:
            print("\n⚠️  Some TIER 3 datasets failed to download")

    print(f"\n💾 Datasets saved to: {data_dir}")
    print("\n✅ Setup complete!")


if __name__ == "__main__":
    main()
    main()

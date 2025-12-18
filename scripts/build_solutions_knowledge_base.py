#!/usr/bin/env python
"""
Build Solutions Knowledge Base for Phase 26C

Extrai soluções de problemas de papers e datasets para criar
dataset local de soluções conhecidas (data/known_solutions.json).

Este dataset será usado pelo Solution Lookup Engine (Phase 26C).

Usage:
    python scripts/build_solutions_knowledge_base.py
    python scripts/build_solutions_knowledge_base.py --from-phase24
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

try:
    from sentence_transformers import SentenceTransformer  # noqa: E402

    from datasets import load_from_disk  # noqa: E402
except ImportError:
    print("❌ Instalar: pip install datasets sentence-transformers")
    sys.exit(1)

# Phase 24 integration
from memory.semantic_memory_layer import get_semantic_memory  # noqa: E402


def extract_solutions_from_papers(papers_data: dict, limit: int = 100) -> list[dict]:
    """Extrai soluções de papers científicos

    Args:
        papers_data: Dataset de papers
        limit: Limite de papers a processar

    Returns:
        Lista de soluções extraídas
    """
    if papers_data is None or "papers" not in papers_data:
        return []

    papers = papers_data["papers"]
    solutions = []

    print(f"\n📚 Extraindo soluções de {min(limit, len(papers))} papers...")

    # Keywords que indicam soluções
    solution_keywords = [
        "solution",
        "fix",
        "optimize",
        "improve",
        "resolve",
        "address",
        "mitigate",
        "reduce",
        "enhance",
        "method",
        "approach",
        "technique",
    ]

    for i, paper in enumerate(papers):
        if i >= limit:
            break

        try:
            # Extrair texto - dataset structure: article (str), abstract (str)
            article = paper.get("article", "")
            abstract = paper.get("abstract", "")

            # Extract title from first line of article
            if article:
                article_lines = article.split("\n")
                title = article_lines[0][:200] if article_lines else article[:200]
            else:
                title = ""

            if not article and not abstract:
                continue

            text = f"{title} {abstract}".lower()

            # Verificar se contém keywords de solução
            if any(keyword in text for keyword in solution_keywords):
                # Tentar extrair problema e solução
                solution = {
                    "id": f"paper_{i}",
                    "source": "scientific_papers",
                    "problem": {
                        "description": title[:200],
                        "type": "RESEARCH",  # Generic type
                    },
                    "solution": {
                        "description": abstract[:500],
                        "confidence": 0.6,  # Medium confidence (needs validation)
                    },
                    "metadata": {
                        "paper_id": i,
                        "title": title[:200],
                        "extracted_at": datetime.now(timezone.utc).isoformat(),
                    },
                }
                solutions.append(solution)

        except Exception as e:
            print(f"⚠️  Error processing paper {i}: {e}")

    print(f"✅ Extraídas {len(solutions)} soluções de papers")
    return solutions


def extract_solutions_from_qasper(qasper_data: dict) -> list[dict]:
    """Extrai patterns de QA do QASPER

    Args:
        qasper_data: Dataset QASPER

    Returns:
        Lista de soluções (QA patterns)
    """
    if qasper_data is None or "qasper" not in qasper_data:
        return []

    qasper = qasper_data["qasper"]
    solutions = []

    print(f"\n📚 Extraindo patterns de QA do QASPER...")

    for split_name, split_data in qasper.items():
        qa_count = 0
        for i, item in enumerate(split_data):
            try:
                # QASPER structure: item has 'qas' dict with 'question' (list) and 'answers' (list)
                qas_dict = item.get("qas", {})

                if not qas_dict or not isinstance(qas_dict, dict):
                    continue

                # questions e answers são listas paralelas
                questions = qas_dict.get("question", [])
                answers_list = qas_dict.get("answers", [])

                if not questions or not answers_list:
                    continue

                # Processar cada par question-answer
                for qa_idx in range(min(len(questions), len(answers_list))):
                    question = questions[qa_idx] if qa_idx < len(questions) else ""
                    answer = answers_list[qa_idx] if qa_idx < len(answers_list) else None

                    if not question:
                        continue

                    # answer pode ser dict ou lista ou string
                    if isinstance(answer, dict):
                        answer_text = answer.get("answer", "") or str(answer)[:500]
                    elif isinstance(answer, list):
                        answer_text = " ".join(str(a) for a in answer[:3])[:500]
                    elif isinstance(answer, str):
                        answer_text = answer[:500]
                    else:
                        answer_text = str(answer)[:500] if answer else ""

                    if not answer_text:
                        continue

                    # Criar solução baseada em QA pattern
                    solution = {
                        "id": f"qasper_{split_name}_{i}_{qa_idx}",
                        "source": "qasper_qa",
                        "problem": {
                            "description": str(question)[:200],
                            "type": "QA_PATTERN",
                        },
                        "solution": {
                            "description": answer_text,
                            "confidence": 0.7,  # Higher confidence (human-annotated)
                        },
                        "metadata": {
                            "split": split_name,
                            "paper_id": i,
                            "qa_idx": qa_idx,
                            "extracted_at": datetime.now(timezone.utc).isoformat(),
                        },
                    }
                    solutions.append(solution)
                    qa_count += 1

            except Exception as e:
                print(f"⚠️  Error processing QA {split_name}/{i}: {e}")

        if qa_count > 0:
            print(f"   Processed {qa_count} QA pairs from {split_name}")

    print(f"✅ Extraídas {len(solutions)} soluções de QASPER")
    return solutions


def load_solutions_from_phase24(limit: int = 100) -> list[dict]:
    """Carrega soluções já armazenadas em Phase 24

    Args:
        limit: Limite de episódios a processar

    Returns:
        Lista de soluções
    """
    print("\n📚 Carregando soluções de Phase 24 Semantic Memory...")

    semantic_memory = get_semantic_memory()

    # Buscar episódios relacionados a problemas/soluções
    query = "solution fix optimize problem resolve"
    results = semantic_memory.retrieve_similar(query, top_k=limit)

    solutions = []
    for i, result in enumerate(results):
        payload = result.get("payload", {})
        episode_text = result.get("payload", {}).get("episode_text", "")

        if not episode_text:
            continue

        solution = {
            "id": f"phase24_{i}",
            "source": "phase24_semantic_memory",
            "problem": {
                "description": episode_text[:200],
                "type": payload.get("type", "UNKNOWN"),
            },
            "solution": {
                "description": episode_text[:500],
                "confidence": 0.8,  # High confidence (already in semantic memory)
            },
            "metadata": {
                "episode_id": result.get("id"),
                "extracted_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        solutions.append(solution)

    print(f"✅ Carregadas {len(solutions)} soluções de Phase 24")
    return solutions


def save_solutions_knowledge_base(solutions: list[dict], output_file: Path) -> None:
    """Salva knowledge base de soluções

    Args:
        solutions: Lista de soluções
        output_file: Arquivo de saída
    """
    knowledge_base = {
        "version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_solutions": len(solutions),
        "sources": list(set(s["source"] for s in solutions)),
        "solutions": solutions,
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Knowledge base salva: {output_file}")
    print(f"   Total: {len(solutions)} soluções")
    print(f"   Fontes: {', '.join(knowledge_base['sources'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build solutions knowledge base for Phase 26C")
    parser.add_argument(
        "--from-phase24",
        action="store_true",
        help="Load solutions from Phase 24 Semantic Memory",
    )
    parser.add_argument(
        "--from-datasets",
        action="store_true",
        help="Extract solutions from HuggingFace datasets",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Limit papers to process (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file (default: data/known_solutions.json)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("BUILDING SOLUTIONS KNOWLEDGE BASE - Phase 26C")
    print("=" * 60)

    all_solutions = []

    # Carregar de Phase 24
    if args.from_phase24:
        solutions_phase24 = load_solutions_from_phase24(limit=args.limit)
        all_solutions.extend(solutions_phase24)

    # Extrair de datasets
    if args.from_datasets:
        data_dir = BASE_DIR / "data" / "datasets"

        # Papers
        papers_dir = data_dir / "scientific_papers_arxiv"
        if papers_dir.exists():
            try:
                papers = load_from_disk(str(papers_dir))
                papers_data = {"papers": papers}
                solutions_papers = extract_solutions_from_papers(papers_data, limit=args.limit)
                all_solutions.extend(solutions_papers)
            except Exception as e:
                print(f"⚠️  Error loading papers: {e}")

        # QASPER
        qasper_dir = data_dir / "qasper_qa"
        if qasper_dir.exists():
            try:
                qasper = load_from_disk(str(qasper_dir))
                qasper_data = {"qasper": qasper}
                solutions_qasper = extract_solutions_from_qasper(qasper_data)
                all_solutions.extend(solutions_qasper)
            except Exception as e:
                print(f"⚠️  Error loading QASPER: {e}")

    # Se nenhuma fonte especificada, usar ambas
    if not args.from_phase24 and not args.from_datasets:
        print("⚠️  Nenhuma fonte especificada. Usando --from-datasets por padrão.")
        args.from_datasets = True
        # Recursão com flag
        import subprocess

        cmd = [
            sys.executable,
            __file__,
            "--from-datasets",
            "--limit",
            str(args.limit),
        ]
        if args.output:
            cmd.extend(["--output", args.output])
        subprocess.run(cmd)
        return

    if not all_solutions:
        print("\n⚠️  Nenhuma solução encontrada!")
        print("   Execute primeiro:")
        print("   - python scripts/load_datasets_for_phi.py --store-papers")
        print("   - python scripts/build_solutions_knowledge_base.py --from-datasets")
        sys.exit(1)

    # Salvar
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = BASE_DIR / "data" / "known_solutions.json"

    save_solutions_knowledge_base(all_solutions, output_file)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()

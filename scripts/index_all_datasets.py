#!/usr/bin/env python3
"""
Script para indexar todos os datasets disponíveis no OmniMind.

Indexa datasets de data/datasets/ como knowledge base para RAG retrieval.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-08
"""

import argparse
import logging
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.memory.dataset_indexer import DatasetIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Indexa todos os datasets disponíveis."""
    parser = argparse.ArgumentParser(description="Indexar todos os datasets do OmniMind")
    parser.add_argument(
        "--datasets-dir",
        type=str,
        default="data/datasets",
        help="Diretório com datasets (default: data/datasets)",
    )
    parser.add_argument(
        "--qdrant-url",
        type=str,
        default=None,
        help="URL do Qdrant (default: http://localhost:6333 ou QDRANT_URL env)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Apenas lista datasets sem indexar",
    )
    args = parser.parse_args()

    datasets_dir = Path(args.datasets_dir)
    if not datasets_dir.exists():
        logger.error(f"Diretório de datasets não encontrado: {datasets_dir}")
        return 1

    # Inicializar DatasetIndexer
    qdrant_url = args.qdrant_url or "http://localhost:6333"
    logger.info(f"Inicializando DatasetIndexer (Qdrant: {qdrant_url})")
    indexer = DatasetIndexer(
        qdrant_url=qdrant_url,
        datasets_dir=str(datasets_dir),
    )

    if args.dry_run:
        logger.info("=== DRY RUN: Listando datasets disponíveis ===")
        dataset_paths = []
        for item in datasets_dir.iterdir():
            if item.is_dir():
                # Verificar se é dataset do HuggingFace (tem dataset_info.json)
                if (item / "dataset_info.json").exists():
                    dataset_paths.append(str(item))
                    logger.info(f"  📁 {item.name}/ (HuggingFace dataset)")
                else:
                    # Buscar arquivos dentro
                    for subitem in item.rglob("*.arrow"):
                        dataset_paths.append(str(subitem))
                        logger.info(f"  📄 {subitem.relative_to(datasets_dir)}")
            elif item.suffix in [".json", ".txt", ".arrow"]:
                dataset_paths.append(str(item))
                logger.info(f"  📄 {item.name}")

        logger.info(f"\nTotal: {len(dataset_paths)} datasets encontrados")
        return 0

    # Indexar todos os datasets
    logger.info("=== Iniciando indexação de todos os datasets ===")
    result = indexer.index_all_datasets()

    if result.get("status") == "error":
        logger.error(f"Erro na indexação: {result.get('error')}")
        return 1

    logger.info("\n=== Resultados da Indexação ===")
    logger.info(f"Total de datasets: {result.get('total_datasets', 0)}")
    logger.info(f"Datasets indexados: {result.get('indexed_datasets', 0)}")
    logger.info(f"Total de chunks: {result.get('total_chunks', 0)}")

    # Detalhes por dataset
    results = result.get("results", {})
    if results:
        logger.info("\n=== Detalhes por Dataset ===")
        for dataset_path, dataset_result in results.items():
            status = dataset_result.get("status", "unknown")
            if status == "success":
                chunks = dataset_result.get("indexed_chunks", 0)
                collection = dataset_result.get("collection_name", "unknown")
                logger.info(f"  ✅ {Path(dataset_path).name}: {chunks} chunks → {collection}")
            else:
                error = dataset_result.get("error", "unknown error")
                logger.warning(f"  ❌ {Path(dataset_path).name}: {error}")

    logger.info("\n✅ Indexação concluída!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
🚀 OmniMind Complete Project Indexing Script
============================================

Indexação completa do projeto com exclusões inteligentes:
- Exclui: node_modules, __pycache__, .git, .vscode, cache, etc.
- Índices: src/, tests/, scripts/, config/, docs/, data/, etc.
- Usar: python3 scripts/indexing/complete_project_indexing.py

Uso:
    python3 scripts/indexing/complete_project_indexing.py                    # Indexação completa
    python3 scripts/indexing/complete_project_indexing.py --quick            # Rápida (10k max files)
    python3 scripts/indexing/complete_project_indexing.py --force-all        # Força reindexação
    python3 scripts/indexing/complete_project_indexing.py --list-stats       # Ver estatísticas sem indexar
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Setup path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Logging setup
log_dir = project_root / "logs" / "indexing"
log_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = log_dir / f"complete_indexing_{timestamp}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file),
    ],
)

logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

# Diretórios e exclusões
EXCLUDE_DIRS = {
    # Build/Cache
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".node_modules",
    ".cache",
    "caches",
    "cache",
    "dist",
    "build",
    ".egg-info",
    "*.egg-info",
    # VCS
    ".git",
    ".github",
    ".gitignore",
    # IDE
    ".vscode",
    ".idea",
    ".vs",
    ".sublime-project",
    # OS
    ".DS_Store",
    ".AppleDouble",
    "__MACOSX",
    # Docker/Container
    ".docker",
    ".dockerignore",
    # Environment
    ".venv",
    "venv",
    "env",
    ".env.local",
    # Dependencies
    "vendor",
    "third_party",
    "external",
    # Temporary
    "tmp",
    "temp",
    ".temp",
    "scratch",
    # Large data dirs (to avoid indexing massive files)
    "models",
    "datasets",
    "datasets_old",
    "backups",
}

EXCLUDE_FILES = {
    # Python compiled
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    # Archive
    ".zip",
    ".tar",
    ".tar.gz",
    ".rar",
    ".7z",
    # Binary
    ".exe",
    ".dll",
    ".dylib",
    ".bin",
    ".o",
    # Media
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
    ".mp3",
    ".wav",
    ".flac",
    # Large files
    ".iso",
    ".img",
    # Logs (too large)
    ".log",
    # Dataset binary formats (too large, non-text)
    ".arrow",
    ".parquet",
    ".feather",
    ".h5",
    ".hdf5",
    ".pkl",
    ".pickle",
    ".joblib",
    ".npz",
    ".npy",
}

# Diretórios principais para indexação
MAIN_DIRS = [
    "src",  # Core code (PRIORITY)
    "tests",  # Test suite
    "scripts",  # Scripts (excluding large ones)
    "config",  # Configuration files
    "docs",  # Documentation
    "deploy",  # Deployment configs
    "web",  # Web/Frontend code
    "notebooks",  # Jupyter notebooks
    "models",  # Model configs (not weights)
    "real_evidence",  # Evidence and reports
    "data",  # Data (selective)
]

# ==================== HELPER FUNCTIONS ====================


def should_exclude_dir(dir_name: str) -> bool:
    """Verifica se diretório deve ser excluído."""
    return dir_name in EXCLUDE_DIRS or dir_name.startswith(".")


def should_exclude_file(file_path: str) -> bool:
    """Verifica se arquivo deve ser excluído."""
    file_lower = file_path.lower()

    # Verificar extensão
    for ext in EXCLUDE_FILES:
        if file_lower.endswith(ext):
            return True

    # Verificar tamanho (skip > 20MB para estabilidade GPU)
    try:
        if os.path.getsize(file_path) > 20 * 1024 * 1024:
            return True
    except:
        return True

    return False


def count_project_files() -> Tuple[int, int]:
    """Conta total de arquivos no projeto e arquivos indexáveis."""
    total = 0
    indexable = 0

    for root, dirs, files in os.walk(project_root):
        # Filter dirs in-place
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

        for file in files:
            total += 1
            file_path = os.path.join(root, file)
            if not should_exclude_file(file_path):
                indexable += 1

    return total, indexable


def collect_files_to_index() -> List[str]:
    """Coleta todos os arquivos para indexar."""
    files_to_index = []

    logger.info(f"📂 Coletando arquivos de {project_root}...")

    for main_dir in MAIN_DIRS:
        dir_path = project_root / main_dir
        if not dir_path.exists():
            logger.debug(f"  ℹ️  Diretório não encontrado: {main_dir}/")
            continue

        logger.info(f"  📁 Indexando: {main_dir}/")

        for root, dirs, files in os.walk(dir_path):
            # Filter dirs in-place to skip excluded dirs
            dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

            for file in files:
                file_path = os.path.join(root, file)

                # Skip excluded files
                if should_exclude_file(file_path):
                    continue

                files_to_index.append(file_path)

    # Sort for consistent ordering
    files_to_index.sort()

    return files_to_index


def get_project_stats() -> Dict:
    """Calcula estatísticas do projeto."""
    stats = {
        "timestamp": datetime.now().isoformat(),
        "project_root": str(project_root),
        "excluded_dirs": sorted(list(EXCLUDE_DIRS)),
        "excluded_extensions": sorted(list(EXCLUDE_FILES)),
    }

    total_files, indexable_files = count_project_files()
    stats["total_files_in_project"] = total_files
    stats["indexable_files"] = indexable_files
    stats["excluded_files"] = total_files - indexable_files

    # Size statistics
    total_size = 0
    indexable_size = 0

    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                total_size += size

                if not should_exclude_file(file_path):
                    indexable_size += size
            except:
                continue

    stats["total_size_mb"] = total_size / (1024 * 1024)
    stats["indexable_size_mb"] = indexable_size / (1024 * 1024)
    stats["excluded_size_mb"] = (total_size - indexable_size) / (1024 * 1024)

    return stats


def print_stats(stats: Dict):
    """Imprime estatísticas do projeto."""
    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS DO PROJETO OMNIMIND")
    print("=" * 70)
    print(f"Projeto: {project_root}")
    print(f"Timestamp: {stats['timestamp']}")
    print()
    print("📈 ARQUIVOS:")
    print(f"   Total no projeto:    {stats['total_files_in_project']:>8,}")
    print(f"   Indexáveis:          {stats['indexable_files']:>8,}")
    print(f"   Excluídos:           {stats['excluded_files']:>8,}")
    print(
        f"   % Indexável:         {(stats['indexable_files']/max(1,stats['total_files_in_project'])*100):>7.1f}%"
    )
    print()
    print("💾 TAMANHO:")
    print(f"   Total:               {stats['total_size_mb']:>8.1f} MB")
    print(f"   Indexável:           {stats['indexable_size_mb']:>8.1f} MB")
    print(f"   Excluído:            {stats['excluded_size_mb']:>8.1f} MB")
    print()
    print("🚫 DIRETÓRIOS EXCLUÍDOS:")
    for i, d in enumerate(stats["excluded_dirs"][:10], 1):
        print(f"   {i:2d}. {d}")
    if len(stats["excluded_dirs"]) > 10:
        print(f"   ... e {len(stats['excluded_dirs'])-10} outros")
    print()
    print("🚫 EXTENSÕES EXCLUÍDAS:")
    for i, ext in enumerate(sorted(stats["excluded_extensions"])[:15], 1):
        print(f"   {i:2d}. {ext}")
    if len(stats["excluded_extensions"]) > 15:
        print(f"   ... e {len(stats['excluded_extensions'])-15} outras")
    print()
    print("=" * 70 + "\n")


# ==================== MAIN INDEXING ====================


def run_indexing(args):
    """Executa a indexação completa."""

    logger.info("🚀 OMNIMIND - COMPLETE PROJECT INDEXING")
    logger.info("=" * 70)
    logger.info(f"Projeto: {project_root}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"GPU: {os.environ.get('CUDA_VISIBLE_DEVICES', 'auto')}")
    logger.info(f"Quick mode: {args.quick}")
    logger.info(f"Force all: {args.force_all}")
    logger.info("=" * 70)

    # Estatísticas
    logger.info("📊 Coletando estatísticas do projeto...")
    stats = get_project_stats()
    print_stats(stats)

    if args.list_stats:
        logger.info("✅ Estatísticas exibidas. Saindo (--list-stats).")

        # Salvar stats em JSON
        stats_file = log_dir / f"project_stats_{timestamp}.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        logger.info(f"📁 Stats salvas em: {stats_file}")
        return

    # Coletar arquivos
    logger.info("📂 Coletando arquivos para indexação...")
    files_to_index = collect_files_to_index()

    if args.quick:
        logger.info(f"⚡ Modo QUICK: limitando a {10000} arquivos")
        files_to_index = files_to_index[:10000]

    logger.info(f"✅ Total de arquivos para indexar: {len(files_to_index)}")

    # Importar embedding system
    try:
        from embeddings.code_embeddings import OmniMindEmbeddings
    except ImportError as e:
        logger.error(f"❌ Erro ao importar OmniMindEmbeddings: {e}")
        logger.error("Certifique-se de que o ambiente está configurado corretamente")
        sys.exit(1)

    # Verificar Qdrant
    logger.info("🔌 Verificando conexão com Qdrant...")
    try:
        import requests

        response = requests.get("http://127.0.0.1:6333/", timeout=5)
        logger.info(f"✅ Qdrant respondendo (status: {response.status_code})")
    except Exception as e:
        logger.error(f"❌ Qdrant não disponível: {e}")
        logger.error("Inicie Qdrant com:")
        logger.error("   docker run -d --name qdrant-omnimind -p 127.0.0.1:6333:6333 \\")
        logger.error("     -v $(pwd)/data/qdrant:/qdrant/storage:z qdrant/qdrant:latest")
        sys.exit(1)

    # Inicializar embeddings
    logger.info("🔧 Inicializando sistema de embeddings...")
    try:
        embeddings = OmniMindEmbeddings(
            qdrant_url="http://127.0.0.1:6333",
            collection_name="omnimind_embeddings",
            gpu_memory_threshold_mb=1000,
            batch_size_embeddings=64,
            enable_async_execution=True,
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )
        logger.info("✅ Sistema de embeddings inicializado (384 dims)")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar embeddings: {e}")
        sys.exit(1)

    # Executar indexação
    logger.info("⏳ Iniciando indexação de arquivos...")
    logger.info(f"   Arquivos: {len(files_to_index)}")
    logger.info(f"   Modelo: all-MiniLM-L6-v2 (384 dims)")
    logger.info(f"   Coleção: omnimind_embeddings")
    logger.info("")

    start_time = time.time()
    total_chunks = 0
    processed_files = 0
    skipped_files = 0

    for i, file_path in enumerate(files_to_index, 1):
        try:
            # Indexar arquivo
            chunks = embeddings.index_file(file_path)
            total_chunks += chunks
            processed_files += 1

            # Log de progresso (a cada 100 arquivos)
            if i % 100 == 0 or i == len(files_to_index):
                elapsed = time.time() - start_time
                rate = i / elapsed
                remaining = (len(files_to_index) - i) / max(rate, 0.01)

                logger.info(
                    f"   [{i:>6}/{len(files_to_index):<6}] "
                    f"Chunks: {total_chunks:>8} | "
                    f"Rate: {rate:>5.1f} files/sec | "
                    f"ETA: {remaining:>6.0f}s"
                )

        except Exception as e:
            skipped_files += 1
            if i % 500 == 0:
                logger.debug(f"   Erro ao indexar {file_path}: {e}")

    elapsed_time = time.time() - start_time

    # Resumo
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ INDEXAÇÃO COMPLETA")
    logger.info("=" * 70)
    logger.info(f"Tempo total: {elapsed_time:.1f}s")
    logger.info(f"Arquivos processados: {processed_files}")
    logger.info(f"Arquivos pulados: {skipped_files}")
    logger.info(f"Total de chunks: {total_chunks:,}")
    logger.info(f"Taxa média: {processed_files/elapsed_time:.1f} files/sec")
    logger.info("")

    # Informações do Qdrant
    try:
        info = embeddings.client.get_collection("omnimind_embeddings")
        logger.info(f"📊 Qdrant omnimind_embeddings:")
        logger.info(f"   Vetores: {info.points_count:,}")
        logger.info(f"   Dimensão: 384")
        logger.info(f"   Distância: Cosine")
    except Exception as e:
        logger.warning(f"Não foi possível verificar coleção: {e}")

    logger.info("")
    logger.info(f"📁 Log salvo em: {log_file}")
    logger.info("")
    logger.info("🎉 INDEXAÇÃO PRONTA PARA TESTES DE CONSCIÊNCIA")
    logger.info("")

    # Salvar resumo em JSON
    summary = {
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": elapsed_time,
        "files_processed": processed_files,
        "files_skipped": skipped_files,
        "total_chunks": total_chunks,
        "rate_files_per_sec": processed_files / elapsed_time,
        "log_file": str(log_file),
    }

    summary_file = log_dir / f"indexing_summary_{timestamp}.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(f"📋 Summary salvo em: {summary_file}")


# ==================== MAIN ====================


def main():
    parser = argparse.ArgumentParser(
        description="OmniMind Complete Project Indexing Script",
        epilog="Exemplos:\n"
        "  python3 scripts/indexing/complete_project_indexing.py               # Indexação completa\n"
        "  python3 scripts/indexing/complete_project_indexing.py --quick       # Rápida (10k files)\n"
        "  python3 scripts/indexing/complete_project_indexing.py --list-stats  # Ver estatísticas\n"
        "  python3 scripts/indexing/complete_project_indexing.py --force-all   # Força reindexação",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--quick", action="store_true", help="Modo QUICK: Limita a 10k arquivos para teste rápido"
    )
    parser.add_argument(
        "--force-all", action="store_true", help="Força reindexação completa (ignora checkpoints)"
    )
    parser.add_argument(
        "--list-stats",
        action="store_true",
        help="Lista estatísticas do projeto e sai (sem indexar)",
    )

    args = parser.parse_args()

    try:
        run_indexing(args)
    except KeyboardInterrupt:
        logger.info("⏹️ Indexação interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

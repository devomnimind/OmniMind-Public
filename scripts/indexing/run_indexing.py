#!/usr/bin/env python3
"""
Script para executar a indexação de embeddings do OmniMind.

Uso:
    python run_indexing.py                    # Indexação completa
    python run_indexing.py --incremental      # Indexação incremental
    python run_indexing.py --help             # Ajuda

Funcionalidades:
- Indexação completa: processa todos os arquivos
- Indexação incremental: só processa arquivos modificados
- Suporte a paralelização
- Logging detalhado
"""

import argparse
import logging
import sys
from pathlib import Path

from embeddings.code_embeddings import OmniMindEmbeddings

# Adicionar src ao path
project_root = Path(__file__).parent.parent.parent  # scripts/indexing/ -> scripts/ -> project_root
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "embedding_indexing.log", mode="a"),
    ],
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Indexação de embeddings OmniMind")
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Executar indexação incremental (só arquivos modificados)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Número máximo de workers para paralelização (padrão: 4)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Tamanho do batch para geração de embeddings (padrão: 64)",
    )
    parser.add_argument(
        "--skip-node-modules",
        action="store_true",
        help="Pular diretórios node_modules (padrão: False)",
    )
    parser.add_argument(
        "--min-file-size",
        type=int,
        default=50,
        help="Tamanho mínimo de arquivo em bytes (padrão: 50)",
    )
    parser.add_argument(
        "--qdrant-url",
        default="http://localhost:6333",
        help="URL do Qdrant (padrão: http://localhost:6333)",
    )
    parser.add_argument(
        "--collection",
        default="omnimind_embeddings",
        help="Nome da coleção Qdrant (padrão: omnimind_embeddings)",
    )
    parser.add_argument(
        "--gpu-memory-threshold",
        type=float,
        default=1000.0,
        help="Threshold de memória GPU em MB para forçar uso (padrão: 1000.0)",
    )
    parser.add_argument(
        "--force-gpu",
        action="store_true",
        help="Forçar uso de GPU mesmo com pouca memória (usa OMNIMIND_FORCE_GPU_EMBEDDINGS=true)",
    )
    parser.add_argument(
        "--disable-async",
        action="store_true",
        help="Desabilitar execução assíncrona de embeddings",
    )
    parser.add_argument(
        "--stages",
        nargs="*",
        help="""Etapas específicas para executar (ex: core_code tests docs).
Se não especificado, executa todas""",
    )
    parser.add_argument(
        "--checkpoint-file",
        default=".omnimind_embedding_checkpoint.json",
        help="""Arquivo de checkpoint para salvar progresso
(padrão: .omnimind_embedding_checkpoint.json)""",
    )
    parser.add_argument(
        "--reset-checkpoint",
        action="store_true",
        help="Resetar checkpoint e começar do início",
    )
    parser.add_argument(
        "--list-stages",
        action="store_true",
        help="Listar todas as etapas disponíveis e sair",
    )
    parser.add_argument(
        "--cycle-min",
        type=int,
        help="Número mínimo do ciclo para filtrar arquivos integration_loop_cycle_*.json",
    )
    parser.add_argument(
        "--cycle-max",
        type=int,
        help="Número máximo do ciclo para filtrar arquivos integration_loop_cycle_*.json",
    )
    parser.add_argument(
        "--no-mark-complete",
        action="store_true",
        help="Não marcar a etapa como concluída (para processamento em lotes)",
    )

    args = parser.parse_args()

    # Listar etapas se solicitado
    if args.list_stages:
        print("📋 Etapas disponíveis para indexação:")
        stages_info = {
            "core_code": "Código Principal (src/)",
            "tests": "Testes (tests/)",
            "scripts": "Scripts (scripts/)",
            "configs": "Configurações (config/)",
            "datasets": "Datasets (datasets/)",
            "deploy": "Deploy (deploy/)",
            "docs": "Documentação (docs/)",
            "archive": "Arquivo (archive/)",
            "logs_main": "Logs Principais (logs/)",
            "node_modules_main": "Node Modules Principais (limitado)",
            "data_core": "Dados Core (data/, exceto módulos massivos)",
            "data_reports": "Relatórios (reports/)",
            "kernel_files": "Arquivos Kernel (kernel_ai/, quantum_ai/, etc.)",
            "system_metadata": "Metadados do Sistema",
            "data_modules": "Módulos de Dados (data/reports/modules/ - massivo)",
            "exports": "Exports (exports/)",
            "tmp": "Temporários (tmp/)",
        }
        for stage, desc in stages_info.items():
            print(f"  {stage}: {desc}")
        print(
            "\n💡 Ordem recomendada: core_code tests scripts configs datasets deploy "
            "docs archive logs_main node_modules_main data_core data_reports "
            "kernel_files system_metadata data_modules exports tmp"
        )
        return

    # Resetar checkpoint se solicitado
    if args.reset_checkpoint:
        checkpoint_path = project_root / args.checkpoint_file
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            logger.info(f"🗑️ Checkpoint resetado: {checkpoint_path}")
        else:
            logger.info("ℹ️ Nenhum checkpoint encontrado para resetar")

    # Configurar filtros de arquivo
    skip_patterns = []
    if args.skip_node_modules:
        skip_patterns.append("node_modules")
        logger.info("🚫 Pulando diretórios node_modules")

    # Configurar variável de ambiente se forçado
    if args.force_gpu:
        import os

        os.environ["OMNIMIND_FORCE_GPU_EMBEDDINGS"] = "true"
        logger.info("🔧 GPU forçado via OMNIMIND_FORCE_GPU_EMBEDDINGS=true")

    try:
        logger.info("🚀 Iniciando sistema de embeddings OmniMind")
        logger.info(f"Modo: {'Incremental' if args.incremental else 'Completo'}")
        logger.info(f"Workers: {args.max_workers}")
        logger.info(f"Batch size: {args.batch_size}")
        logger.info(f"GPU threshold: {args.gpu_memory_threshold}MB")
        logger.info(f"Min file size: {args.min_file_size} bytes")
        logger.info(f"Qdrant: {args.qdrant_url}")
        logger.info(f"Coleção: {args.collection}")
        logger.info(f"Checkpoint: {args.checkpoint_file}")

        if args.stages:
            logger.info(f"Etapas: {', '.join(args.stages)}")
        else:
            logger.info("Etapas: Todas (com checkpointing)")

        # Verificar se Qdrant está rodando
        import requests

        try:
            # Tentar endpoint de saúde do Qdrant (pode ser /healthz ou /)
            health_endpoints = [f"{args.qdrant_url}/healthz", f"{args.qdrant_url}/"]
            qdrant_ok = False

            for endpoint in health_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code in [200, 404]:  # 404 é aceitável para alguns endpoints
                        qdrant_ok = True
                        break
                except Exception:
                    continue

            if not qdrant_ok:
                logger.error("Qdrant não está respondendo em nenhum endpoint de saúde")
                logger.error("Certifique-se de que o Qdrant está rodando:")
                logger.error("  docker-compose -f deploy/docker-compose.yml up -d qdrant")
                sys.exit(1)

        except Exception as e:
            logger.error(f"Erro ao conectar com Qdrant: {e}")
            logger.error("Certifique-se de que o Qdrant está rodando:")
            logger.error("  docker-compose -f deploy/docker-compose.yml up -d qdrant")
            sys.exit(1)

        # Inicializar sistema de embeddings
        embeddings = OmniMindEmbeddings(
            qdrant_url=args.qdrant_url,
            collection_name=args.collection,
            gpu_memory_threshold_mb=args.gpu_memory_threshold,
            batch_size_embeddings=args.batch_size,
            enable_async_execution=not args.disable_async,
        )

        # Executar indexação
        logger.info(f"📁 Indexando projeto: {project_root}")
        results = embeddings.index_omnimind_project(
            str(project_root),
            max_workers=args.max_workers,
            incremental=args.incremental,
            skip_patterns=skip_patterns,
            min_file_size=args.min_file_size,
            stages=args.stages,
            checkpoint_file=args.checkpoint_file,
            cycle_min=args.cycle_min,
            cycle_max=args.cycle_max,
            no_mark_complete=args.no_mark_complete,
        )

        # Calcular estatísticas
        total_chunks = 0
        total_files = 0
        for stage_name, stage_results in results.items():
            if isinstance(stage_results, dict):
                stage_chunks = sum(stage_results.values())
                stage_files = len(stage_results)
                total_chunks += stage_chunks
                total_files += stage_files
                logger.info(f"📊 {stage_name}: {stage_files} arquivos, {stage_chunks} chunks")

        logger.info("✅ Indexação concluída!")
        logger.info(f"📈 Total: {total_files} arquivos processados, {total_chunks} chunks criados")

        # Mostrar estatísticas da coleção
        stats = embeddings.get_stats()
        logger.info(f"📊 Estatísticas da coleção: {stats}")

        # Exemplo de busca
        logger.info("🔍 Testando busca semântica...")
        test_queries = [
            "função principal do sistema",
            "configuração do kernel",
            "processamento de dados",
        ]

        for query in test_queries:
            results = embeddings.search(query, top_k=2)
            if results:
                logger.info(
                    f"  Query: '{query}' -> Top result: {results[0]['file_path']} "
                    f"(score: {results[0]['score']:.3f})"
                )

    except KeyboardInterrupt:
        logger.info("⏹️ Indexação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro durante indexação: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

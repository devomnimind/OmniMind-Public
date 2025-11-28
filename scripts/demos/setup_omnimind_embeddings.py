#!/usr/bin/env python3
"""
Script de configuração completa do sistema de embeddings OmniMind

Indexa todo o projeto: código, documentação, papers, auditoria, configurações.
"""

import os
import sys
import logging
from pathlib import Path

# Forçar uso de CPU para evitar problemas de memória GPU
os.environ["CUDA_VISIBLE_DEVICES"] = ""

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from embeddings.code_embeddings import OmniMindEmbeddings, ContentType

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    try:
        import sentence_transformers
        import qdrant_client

        logger.info("✅ Dependências verificadas: sentence_transformers, qdrant_client")
        return True
    except ImportError as e:
        logger.error(f"❌ Dependência faltando: {e}")
        return False


def check_qdrant():
    """Verifica se o Qdrant está rodando."""
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient("http://localhost:6333")
        # Tentar fazer uma operação simples
        collections = client.get_collections()
        logger.info("✅ Qdrant está rodando e acessível")
        return True
    except Exception as e:
        logger.error(f"❌ Qdrant não está acessível: {e}")
        logger.error("💡 Certifique-se de que o Qdrant está rodando na porta 6333")
        return False


def index_omnimind_project():
    """Indexa todo o projeto OmniMind."""
    project_root = Path(__file__).parent

    logger.info("🚀 Iniciando indexação completa do projeto OmniMind")
    logger.info(f"📂 Projeto: {project_root}")

    # Inicializar sistema de embeddings
    embeddings = OmniMindEmbeddings()

    # Indexar projeto completo
    results = embeddings.index_omnimind_project(str(project_root))

    # Calcular estatísticas
    total_files = 0
    total_chunks = 0

    for category, category_results in results.items():
        category_files = len([f for f in category_results.values() if f > 0])
        category_chunks = sum(category_results.values())
        total_files += category_files
        total_chunks += category_chunks

        logger.info(f"📊 {category}: {category_files} arquivos, {category_chunks} chunks")

    logger.info(f"✅ Indexação concluída: {total_files} arquivos, {total_chunks} chunks")

    # Mostrar estatísticas finais
    stats = embeddings.get_stats()
    logger.info("📈 Estatísticas finais:")
    for key, value in stats.items():
        logger.info(f"   {key}: {value}")

    return results


def test_search():
    """Testa buscas em diferentes tipos de conteúdo."""
    logger.info("🔍 Testando buscas semânticas...")

    embeddings = OmniMindEmbeddings()

    # Testes de busca
    test_queries = [
        ("sistema de embeddings", None),
        ("consciência estrutural", None),
        ("função de busca", [ContentType.CODE]),
        ("documentação de arquitetura", [ContentType.DOCUMENTATION]),
        ("auditoria de segurança", [ContentType.AUDIT]),
    ]

    for query, content_types in test_queries:
        logger.info(f"\n🔎 Busca: '{query}'")
        if content_types:
            type_names = [ct.value for ct in content_types]
            logger.info(f"   Filtros: {type_names}")

        results = embeddings.search(query, top_k=3, content_types=content_types)

        for i, result in enumerate(results, 1):
            logger.info(f"   {i}. [{result['content_type']}] {result['file_path']}")
            logger.info(f"      Score: {result['score']:.3f}")
            logger.info(f"      Conteúdo: {result['content'][:100]}...")
            if i < len(results):
                logger.info("")


def main():
    """Função principal."""
    logger.info("🤖 Configuração do Sistema de Embeddings OmniMind")
    logger.info("=" * 60)

    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)

    # Verificar Qdrant
    if not check_qdrant():
        sys.exit(1)

    # Indexar projeto
    try:
        results = index_omnimind_project()
    except Exception as e:
        logger.error(f"❌ Erro durante indexação: {e}")
        sys.exit(1)

    # Testar buscas
    try:
        test_search()
    except Exception as e:
        logger.error(f"❌ Erro durante testes: {e}")
        sys.exit(1)

    logger.info("\n🎉 Configuração concluída com sucesso!")
    logger.info("\n💡 Para usar o sistema:")
    logger.info("   from src.embeddings.code_embeddings import OmniMindEmbeddings")
    logger.info("   embeddings = OmniMindEmbeddings()")
    logger.info("   results = embeddings.search('sua consulta aqui')")


if __name__ == "__main__":
    main()

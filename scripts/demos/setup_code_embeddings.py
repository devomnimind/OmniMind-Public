#!/usr/bin/env python3
"""
Script de Configuração Inicial do Sistema de Embeddings de Código

Este script configura e inicializa o sistema de embeddings locais para busca
semântica no código fonte do projeto OmniMind.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    import importlib.util

    deps = ["sentence_transformers", "qdrant_client"]
    for dep in deps:
        if importlib.util.find_spec(dep) is None:
            logger.error(f"✗ Dependência faltando: {dep}")
            logger.error("Execute: pip install sentence-transformers qdrant-client")
            return False

    logger.info("✓ Todas as dependências estão instaladas")
    return True


def check_qdrant():
    """Verifica se Qdrant está rodando."""
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url="http://localhost:6333")
        # Tentar fazer uma operação simples
        client.get_collections()
        logger.info("✓ Qdrant está rodando na porta 6333")
        return True
    except Exception as e:
        logger.error(f"✗ Erro ao conectar com Qdrant: {e}")
        logger.error(
            "Certifique-se de que Qdrant está rodando: docker run -p 6333:6333 qdrant/qdrant"
        )
        return False


def get_model_info():
    """Retorna informações sobre o modelo usado."""
    from sentence_transformers import SentenceTransformer

    model_name = "all-MiniLM-L6-v2"
    try:
        model = SentenceTransformer(model_name)
        dim = model.get_sentence_embedding_dimension()
        logger.info(f"✓ Modelo: {model_name} (dimensão: {dim})")
        return model_name, dim
    except Exception as e:
        logger.error(f"✗ Erro ao carregar modelo {model_name}: {e}")
        return None, None


def index_codebase(embeddings_system, directories):
    """Indexa os diretórios especificados."""
    total_files = 0
    total_chunks = 0

    for directory in directories:
        if not os.path.exists(directory):
            logger.warning(f"Diretório não encontrado: {directory}")
            continue

        logger.info(f"Indexando: {directory}")
        results = embeddings_system.index_directory(directory)

        dir_files = len([f for f, c in results.items() if c > 0])
        dir_chunks = sum(results.values())

        logger.info(f"  {directory}: {dir_files} arquivos, {dir_chunks} chunks")

        total_files += dir_files
        total_chunks += dir_chunks

    return total_files, total_chunks


def main():
    """Função principal de configuração."""
    print("🚀 Configuração Inicial do Sistema de Embeddings de Código")
    print("=" * 60)

    # 1. Verificar dependências
    print("\n1. Verificando dependências...")
    if not check_dependencies():
        sys.exit(1)

    # 2. Verificar Qdrant
    print("\n2. Verificando Qdrant...")
    if not check_qdrant():
        sys.exit(1)

    # 3. Verificar modelo
    print("\n3. Verificando modelo de embeddings...")
    model_name, embedding_dim = get_model_info()
    if not model_name:
        sys.exit(1)

    # 4. Inicializar sistema
    print("\n4. Inicializando sistema de embeddings...")
    try:
        from embeddings.code_embeddings import CodeEmbeddings

        embeddings = CodeEmbeddings(model_name=model_name, collection_name="code_embeddings")
        logger.info("✓ Sistema inicializado com sucesso")
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar sistema: {e}")
        sys.exit(1)

    # 5. Indexar codebase
    print("\n5. Indexando codebase...")
    directories_to_index = ["src", "tests", "scripts"]

    total_files, total_chunks = index_codebase(embeddings, directories_to_index)

    # 6. Estatísticas finais
    print("\n6. Estatísticas finais:")
    stats = embeddings.get_stats()
    print(f"   Coleção: {stats['collection_name']}")
    print(f"   Dimensão vetorial: {stats['vector_dim']}")
    print(f"   Modelo: {stats['model']}")
    print(f"   Arquivos indexados: {total_files}")
    print(f"   Total de chunks: {total_chunks}")

    # 7. Teste de busca
    print("\n7. Teste de busca semântica...")
    test_queries = ["sistema de embeddings", "conexão com banco de dados", "função de busca"]

    for query in test_queries:
        results = embeddings.search(query, top_k=1)
        if results:
            result = results[0]
            print(f"   '{query}' -> {result['file_path']} (score: {result['score']:.3f})")
        else:
            print(f"   '{query}' -> Nenhum resultado")

    print("\n✅ Configuração concluída com sucesso!")
    print("\nPara usar o sistema:")
    print("from src.embeddings.code_embeddings import CodeEmbeddings")
    print("embeddings = CodeEmbeddings()")
    print("results = embeddings.search('sua query aqui')")


if __name__ == "__main__":
    main()

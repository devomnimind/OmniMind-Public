#!/usr/bin/env python3
"""
Script de demonstração do sistema de embeddings OmniMind.
Mostra como usar o sistema para consultas semânticas no projeto.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.embeddings.code_embeddings import OmniMindEmbeddings, ContentType

def demo_search():
    """Demonstra buscas semânticas no projeto OmniMind."""
    print("🚀 Demonstrando sistema de embeddings OmniMind\n")

    # Inicializar sistema
    embeddings = OmniMindEmbeddings()

    # Exemplos de consultas
    queries = [
        ("sistema de consciência", None),
        ("documentação de arquitetura", [ContentType.DOCUMENTATION]),
        ("funções de busca", [ContentType.CODE]),
        ("auditoria de segurança", [ContentType.AUDIT]),
        ("papers sobre consciência estrutural", [ContentType.PAPER]),
    ]

    for query, content_types in queries:
        print(f"\n🔍 Consulta: '{query}'")
        if content_types:
            print(f"   Filtros: {content_types}")

        results = embeddings.search(query, content_types=content_types, top_k=3)

        for i, result in enumerate(results, 1):
            print(f"\n   {i}. [{result['content_type']}] {result['file_path']}")
            print(".3f")
            print(f"      Conteúdo: {result['content'][:100]}...")

if __name__ == "__main__":
    demo_search()
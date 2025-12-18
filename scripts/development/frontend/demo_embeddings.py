#!/usr/bin/env python3
"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Script de demonstração do sistema de embeddings OmniMind.
Mostra como usar o sistema para consultas semânticas no projeto.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.embeddings.code_embeddings import ContentType, OmniMindEmbeddings


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

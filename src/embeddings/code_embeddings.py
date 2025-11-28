import os
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

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
Sistema de Embeddings Locais do OmniMind

Gera embeddings semânticos para múltiplos tipos de conteúdo:
- Código fonte
- Documentação técnica
- Papers científicos
- Arquivos de configuração
- Relatórios de auditoria

Armazena no Qdrant para busca semântica abrangente do projeto.
"""


logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Tipos de conteúdo suportados."""

    CODE = "code"
    DOCUMENTATION = "documentation"
    PAPER = "paper"
    CONFIG = "config"
    AUDIT = "audit"


@dataclass
class ContentChunk:
    """Chunk de conteúdo com metadados."""

    file_path: str
    start_line: int
    end_line: int
    content: str
    content_type: ContentType
    language: str
    title: Optional[str] = None
    section: Optional[str] = None
    function_name: Optional[str] = None
    class_name: Optional[str] = None


class OmniMindEmbeddings:
    """
    Sistema de embeddings abrangente para o projeto OmniMind.

    Indexa múltiplos tipos de conteúdo: código, documentação, papers,
    configurações e relatórios de auditoria.
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "omnimind_embeddings",
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size_code: int = 100,  # linhas para código
        chunk_size_docs: int = 50,  # linhas para documentos
        overlap: int = 20,  # sobreposição entre chunks
    ):
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.model_name = model_name
        self.chunk_size_code = chunk_size_code
        self.chunk_size_docs = chunk_size_docs
        self.overlap = overlap

        # Inicializar modelo
        logger.info(f"Carregando modelo: {model_name}")
        self.model = SentenceTransformer(
            model_name, device="cpu"
        )  # Forçar CPU para evitar problemas de memória
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Modelo carregado. Dimensões: {self.embedding_dim}")

        # Inicializar Qdrant
        self.client = QdrantClient(qdrant_url)

        # Criar coleção se não existir
        self._ensure_collection()

        # Inicializar cliente Qdrant
        self.client = QdrantClient(url=qdrant_url)

        # Carregar modelo de embeddings
        logger.info(f"Carregando modelo de embeddings: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

        # Garantir que a coleção existe
        self._ensure_collection()

    def _ensure_collection(self):
        """Cria coleção se não existir."""
        try:
            collections = self.client.get_collections().collections or []
            collection_names = [info.name for info in collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qmodels.VectorParams(
                        size=self.embedding_dim, distance=qmodels.Distance.COSINE
                    ),
                )
                logger.info(f"Coleção criada: {self.collection_name} (dim={self.embedding_dim})")
        except Exception as exc:
            logger.error(f"Erro ao criar coleção: {exc}")

    def _chunk_file(self, file_path: str) -> List[ContentChunk]:
        """Divide arquivo em chunks baseado no tipo de conteúdo."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            if not lines:
                return []

            # Determinar tipo de conteúdo e tamanho de chunk
            content_type = self._detect_content_type(file_path)
            chunk_size = (
                self.chunk_size_code if content_type == ContentType.CODE else self.chunk_size_docs
            )

            chunks = []
            i = 0

            while i < len(lines):
                # Calcular fim do chunk
                end = min(i + chunk_size, len(lines))

                # Extrair conteúdo
                content = "".join(lines[i:end])

                # Detectar linguagem/tipo
                language = self._detect_language(file_path)

                # Criar chunk
                chunk = ContentChunk(
                    file_path=file_path,
                    start_line=i + 1,  # 1-indexed
                    end_line=end,
                    content=content,
                    content_type=content_type,
                    language=language,
                )

                chunks.append(chunk)

                # Avançar com sobreposição
                i += chunk_size - self.overlap

            return chunks

        except Exception as exc:
            logger.error(f"Erro ao processar arquivo {file_path}: {exc}")
            return []

    def _detect_content_type(self, file_path: str) -> ContentType:
        """Detecta tipo de conteúdo baseado no caminho do arquivo."""
        path = Path(file_path)

        # Verificar se é documentação
        if any(part in str(path) for part in ["docs/", "papers/", "audit/", "README", "ROADMAP"]):
            if "papers/" in str(path):
                return ContentType.PAPER
            elif "audit/" in str(path):
                return ContentType.AUDIT
            else:
                return ContentType.DOCUMENTATION

        # Verificar se é configuração
        if any(
            part in str(path)
            for part in ["config/", ".yaml", ".yml", ".toml", ".json", ".ini", ".cfg"]
        ):
            return ContentType.CONFIG

        # Default: código
        return ContentType.CODE

    def _detect_language(self, file_path: str) -> str:
        """Detecta linguagem baseada na extensão."""
        ext = Path(file_path).suffix.lower()
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "config",
            ".sh": "bash",
            ".sql": "sql",
        }
        return mapping.get(ext, "unknown")

    def index_file(self, file_path: str) -> int:
        """Indexa um arquivo de qualquer tipo suportado."""
        logger.info(f"Indexando arquivo: {file_path}")

        # Verificar se arquivo existe
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return 0

        # Dividir em chunks
        chunks = self._chunk_file(file_path)
        if not chunks:
            logger.warning(f"Nenhum chunk gerado para {file_path}")
            return 0

        # Gerar embeddings e armazenar
        points = []
        for chunk in chunks:
            # Gerar embedding
            embedding = self.model.encode(chunk.content, normalize_embeddings=True)

            # Criar ID único baseado no conteúdo
            content_hash = hashlib.sha256(chunk.content.encode()).hexdigest()[:16]
            point_id = int(content_hash, 16)

            # Payload com metadados
            payload = {
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "content": chunk.content[:1000],  # Limitar tamanho
                "content_type": chunk.content_type.value,
                "language": chunk.language,
                "function_name": chunk.function_name,
                "class_name": chunk.class_name,
                "title": chunk.title,
                "section": chunk.section,
            }

            points.append(
                qmodels.PointStruct(id=point_id, vector=embedding.tolist(), payload=payload)
            )

        # Upsert no Qdrant
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)
            logger.info(f"Indexado {len(points)} chunks de {file_path}")
            return len(points)

        return 0

    def index_directory(
        self, directory: str, extensions: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """Indexa todos os arquivos suportados em um diretório."""
        if extensions is None:
            # Extensões para código
            extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"]

        results = {}
        directory_path = Path(directory)

        for ext in extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    count = self.index_file(str(file_path))
                    results[str(file_path)] = count

        return results

    def index_omnimind_project(self, project_root: str) -> Dict[str, Dict[str, int]]:
        """
        Indexa todo o projeto OmniMind: código, documentação, papers, auditoria, etc.
        """
        project_path = Path(project_root)
        results = {}

        logger.info("🚀 Iniciando indexação completa do projeto OmniMind")

        # 1. Indexar código fonte (src/, tests/, scripts/)
        logger.info("📁 Indexando código fonte...")
        code_dirs = ["src", "tests", "scripts"]
        for dir_name in code_dirs:
            dir_path = project_path / dir_name
            if dir_path.exists():
                logger.info(f"  Indexando {dir_name}...")
                results[dir_name] = self.index_directory(str(dir_path))

        # 2. Indexar documentação
        logger.info("📄 Indexando documentação...")
        docs_dirs = ["docs", "papers", "audit"]
        for dir_name in docs_dirs:
            dir_path = project_path / dir_name
            if dir_path.exists():
                logger.info(f"  Indexando {dir_name}...")
                results[dir_name] = self._index_docs_directory(str(dir_path))

        # 3. Indexar arquivos raiz importantes
        logger.info("📋 Indexando arquivos raiz...")
        root_files = [
            "README.md",
            "ROADMAP.md",
            "ROADMAP_PHASE_23_FUNDING.md",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
        ]
        results["root_docs"] = {}
        for filename in root_files:
            file_path = project_path / filename
            if file_path.exists():
                count = self.index_file(str(file_path))
                results["root_docs"][str(file_path)] = count

        # 4. Indexar configurações importantes
        logger.info("⚙️ Indexando configurações...")
        config_files = ["pyproject.toml", "pytest.ini", "mypy.ini", "sonar-project.properties"]
        results["configs"] = {}
        for filename in config_files:
            file_path = project_path / filename
            if file_path.exists():
                count = self.index_file(str(file_path))
                results["configs"][str(file_path)] = count

        return results

    def _index_docs_directory(self, directory: str) -> Dict[str, int]:
        """Indexa diretório de documentação (suporta .md, .txt, etc.)"""
        results = {}
        directory_path = Path(directory)

        # Extensões de documentação
        doc_extensions = [".md", ".txt", ".rst", ".adoc"]

        for ext in doc_extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    count = self.index_file(str(file_path))
                    results[str(file_path)] = count

        return results

    def search(
        self, query: str, top_k: int = 5, content_types: Optional[List[ContentType]] = None
    ) -> List[Dict[str, Any]]:
        """Busca semântica no conteúdo indexado."""
        # Gerar embedding da query
        query_embedding = self.model.encode(query, normalize_embeddings=True)

        # Filtro por tipo de conteúdo se especificado
        query_filter = None
        if content_types:
            content_type_values = [ct.value for ct in content_types]
            query_filter = qmodels.Filter(
                must=[
                    qmodels.FieldCondition(
                        key="content_type", match=qmodels.MatchAny(any=content_type_values)
                    )
                ]
            )

        # Buscar no Qdrant
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_embedding.tolist(),
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        # Formatar resultados
        results = []
        for point in search_result.points:
            payload = point.payload or {}
            results.append(
                {
                    "score": float(point.score),
                    "file_path": payload.get("file_path", ""),
                    "start_line": payload.get("start_line", 0),
                    "end_line": payload.get("end_line", 0),
                    "content": payload.get("content", ""),
                    "content_type": payload.get("content_type", ""),
                    "language": payload.get("language", ""),
                }
            )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Estatísticas da coleção."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "collection_name": self.collection_name,
                "vector_dim": self.embedding_dim,
                "total_chunks": collection_info.points_count,
                "model": self.model_name,
            }
        except Exception as exc:
            logger.error(f"Erro ao obter stats: {exc}")
            return {"error": str(exc)}


if __name__ == "__main__":
    # Exemplo de uso
    import sys

    if len(sys.argv) < 2:
        print("Uso: python code_embeddings.py <diretório>")
        sys.exit(1)

    directory = sys.argv[1]

    # Inicializar sistema
    embeddings = OmniMindEmbeddings()

    # Indexar diretório
    print(f"Indexando código em: {directory}")
    results = embeddings.index_directory(directory)

    total_chunks = sum(results.values())
    print(f"Total de chunks indexados: {total_chunks}")

    # Mostrar stats
    stats = embeddings.get_stats()
    print(f"Stats: {stats}")

    # Exemplo de busca
    query = "função para conectar banco de dados"
    results = embeddings.search(query, top_k=3)
    print(f"\nBusca por: '{query}'")
    for result in results:
        print(f"Score: {result['score']:.3f}")
        print(f"Arquivo: {result['file_path']}:{result['start_line']}-{result['end_line']}")
        print(f"Conteúdo: {result['content'][:200]}...")
        print("-" * 50)

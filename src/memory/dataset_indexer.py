"""
Dataset Indexer - Indexação de Datasets como Knowledge Base para RAG

Indexa datasets de `data/datasets/` como memória de modelos (knowledge base)
para uso em RAG retrieval quando agentes falham ou precisam de conhecimento profundo.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

try:
    from datasets import load_from_disk, load_dataset  # type: ignore[attr-defined]

    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False

    # Stubs para quando datasets não está disponível
    def load_from_disk(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        raise ImportError("datasets library not available")

    def load_dataset(*args: Any, **kwargs: Any) -> Any:  # type: ignore[misc]
        raise ImportError("datasets library not available")

    logger.warning("HuggingFace datasets não disponível. Indexação de .arrow limitada.")


@dataclass
class DatasetChunk:
    """Chunk de dataset indexado."""

    content: str
    source: str  # Nome do dataset
    chunk_id: str
    metadata: Dict[str, Any]
    chunk_type: str  # "section", "qa_pair", "code_example", "entity", etc.


class DatasetIndexer:
    """
    Indexa datasets como knowledge base para RAG.

    Características:
    - Chunking inteligente baseado no tipo de dataset
    - Metadata rica (source, type, timestamp, dataset_name)
    - Incremental indexing
    - Integração com Qdrant para RAG retrieval
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        embedding_model: Optional[SentenceTransformer] = None,
        datasets_dir: str = "data/datasets",
    ):
        """
        Inicializa DatasetIndexer.

        Args:
            qdrant_url: URL do Qdrant
            embedding_model_name: Nome do modelo de embeddings
            embedding_model: Modelo opcional (reutilizar)
            datasets_dir: Diretório com datasets
        """
        self.qdrant_url = qdrant_url
        self.embedding_model_name = embedding_model_name
        self.datasets_dir = Path(datasets_dir)

        # Inicializar modelo de embeddings
        if embedding_model is not None:
            self.embedding_model = embedding_model
            self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        else:
            logger.info(f"Carregando modelo de embeddings: {embedding_model_name}")
            self.embedding_model = SentenceTransformer(embedding_model_name, device="cpu")
            self.embedding_dim = int(self.embedding_model.get_sentence_embedding_dimension() or 384)
            logger.info(f"Modelo carregado. Dimensões: {self.embedding_dim}")

        # Inicializar Qdrant
        self.client = QdrantClient(url=qdrant_url)

        # Mapeamento de datasets para coleções
        self.dataset_collections: Dict[str, str] = {
            "scientific_papers_arxiv": "scientific_papers_kb",
            "qasper_qa": "qa_knowledge_kb",
            "human_vs_ai_code": "code_examples_kb",
            "dbpedia_ontology": "ontology_knowledge_kb",
            "turing_reasoning": "reasoning_patterns_kb",
            "infllm_v2_data": "training_examples_kb",
        }

        # Status de indexação
        self.indexed_datasets: Dict[str, bool] = {}

        logger.info(f"DatasetIndexer inicializado: datasets_dir={datasets_dir}")

    def _detect_dataset_type(self, dataset_path: Path) -> str:
        """
        Detecta tipo de dataset automaticamente.

        Args:
            dataset_path: Caminho do dataset

        Returns:
            Tipo do dataset
        """
        dataset_name = dataset_path.name.lower()

        if "arxiv" in dataset_name or "paper" in dataset_name:
            return "scientific_papers"
        elif "qa" in dataset_name or "qasper" in dataset_name:
            return "qa"
        elif "code" in dataset_name:
            return "code_examples"
        elif "ontology" in dataset_name or "dbpedia" in dataset_name:
            return "ontology"
        elif "reasoning" in dataset_name or "turing" in dataset_name:
            return "reasoning"
        elif "train" in dataset_name or "infllm" in dataset_name:
            return "training_examples"
        else:
            return "generic"

    def _chunk_by_type(
        self, content: str, dataset_type: str, chunk_size: int = 500
    ) -> List[DatasetChunk]:
        """
        Chunking inteligente baseado no tipo de dataset.

        Args:
            content: Conteúdo a ser chunkado
            dataset_type: Tipo do dataset
            chunk_size: Tamanho do chunk (caracteres ou linhas)

        Returns:
            Lista de chunks
        """
        chunks: List[DatasetChunk] = []

        if dataset_type == "scientific_papers":
            # Chunking por seção (abstract, introduction, methods, results)
            sections = content.split("\n\n")  # Assumindo que seções são separadas por linha dupla
            for i, section in enumerate(sections):
                if len(section.strip()) > 50:  # Ignorar seções muito pequenas
                    chunks.append(
                        DatasetChunk(
                            content=section.strip(),
                            source="scientific_papers_arxiv",
                            chunk_id=f"paper_section_{i}",
                            metadata={"section_index": i, "type": "section"},
                            chunk_type="section",
                        )
                    )

        elif dataset_type == "qa":
            # Chunking por Q&A pair
            # Assumindo formato: Q: ... A: ...
            qa_pairs = content.split("Q:")
            for i, pair in enumerate(qa_pairs[1:], 1):  # Pular primeiro (pode ser vazio)
                if "A:" in pair:
                    parts = pair.split("A:", 1)
                    question = parts[0].strip()
                    answer = parts[1].strip() if len(parts) > 1 else ""
                    chunk_content = f"Q: {question}\nA: {answer}"
                    chunks.append(
                        DatasetChunk(
                            content=chunk_content,
                            source="qasper_qa",
                            chunk_id=f"qa_pair_{i}",
                            metadata={"question": question, "answer": answer},
                            chunk_type="qa_pair",
                        )
                    )

        elif dataset_type == "code_examples":
            # Chunking por exemplo de código
            # Assumindo que exemplos são separados por marcadores ou linhas vazias
            examples = content.split("\n\n\n")  # Três linhas vazias como separador
            for i, example in enumerate(examples):
                if len(example.strip()) > 100:
                    chunks.append(
                        DatasetChunk(
                            content=example.strip(),
                            source="human_vs_ai_code",
                            chunk_id=f"code_example_{i}",
                            metadata={"example_index": i},
                            chunk_type="code_example",
                        )
                    )

        else:
            # Chunking genérico por tamanho
            words = content.split()
            current_chunk = []
            current_size = 0
            chunk_id = 0

            for word in words:
                current_chunk.append(word)
                current_size += len(word) + 1  # +1 para espaço

                if current_size >= chunk_size:
                    chunk_content = " ".join(current_chunk)
                    chunks.append(
                        DatasetChunk(
                            content=chunk_content,
                            source="generic",
                            chunk_id=f"chunk_{chunk_id}",
                            metadata={"chunk_index": chunk_id},
                            chunk_type="generic",
                        )
                    )
                    current_chunk = []
                    current_size = 0
                    chunk_id += 1

            # Último chunk
            if current_chunk:
                chunk_content = " ".join(current_chunk)
                chunks.append(
                    DatasetChunk(
                        content=chunk_content,
                        source="generic",
                        chunk_id=f"chunk_{chunk_id}",
                        metadata={"chunk_index": chunk_id},
                        chunk_type="generic",
                    )
                )

        return chunks

    def _ensure_collection(self, collection_name: str) -> None:
        """Garante que coleção existe no Qdrant."""
        try:
            collections = self.client.get_collections()
            collection_names = (
                [c.name for c in collections.collections] if collections.collections else []
            )

            if collection_name not in collection_names:
                self.client.create_collection(  # type: ignore[attr-defined]
                    collection_name=collection_name,
                    vectors_config={  # type: ignore[dict-item]
                        "size": self.embedding_dim,  # type: ignore[dict-item]
                        "distance": "Cosine",  # type: ignore[dict-item]
                    },
                )
                logger.info(f"Coleção criada: {collection_name}")
        except Exception as e:
            logger.error(f"Erro ao criar coleção {collection_name}: {e}")

    def index_dataset(
        self,
        dataset_path: str,
        collection_name: Optional[str] = None,
        chunk_size: int = 500,
        dataset_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Indexa um dataset como knowledge base.

        Args:
            dataset_path: Caminho do dataset
            collection_name: Nome da coleção (default: baseado no nome do dataset)
            chunk_size: Tamanho do chunk
            dataset_type: Tipo do dataset (default: auto-detecta)

        Returns:
            Estatísticas de indexação
        """
        dataset_path_obj = Path(dataset_path)
        if not dataset_path_obj.exists():
            logger.error(f"Dataset não encontrado: {dataset_path}")
            return {"status": "error", "error": "Dataset not found"}

        # Detectar tipo se não fornecido
        if dataset_type is None:
            dataset_type = self._detect_dataset_type(dataset_path_obj)

        # Determinar nome da coleção
        if collection_name is None:
            dataset_name = dataset_path_obj.stem
            collection_name = self.dataset_collections.get(dataset_name, f"{dataset_name}_kb")

        logger.info(f"Indexando dataset: {dataset_path} → {collection_name} (tipo: {dataset_type})")

        # Garantir que coleção existe
        self._ensure_collection(collection_name)

        # Ler conteúdo do dataset
        try:
            if dataset_path_obj.suffix == ".json":
                with open(dataset_path_obj, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Converter para string (simplificado)
                    content = json.dumps(data, indent=2)
            elif dataset_path_obj.suffix == ".txt":
                with open(dataset_path_obj, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                # Tentar ler como texto genérico
                with open(dataset_path_obj, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
        except Exception as e:
            logger.error(f"Erro ao ler dataset {dataset_path}: {e}")
            return {"status": "error", "error": str(e)}

        # Chunking
        chunks = self._chunk_by_type(content, dataset_type, chunk_size)
        logger.info(f"Dataset chunkado em {len(chunks)} chunks")

        # Gerar embeddings e indexar
        indexed_count = 0
        for i, chunk in enumerate(chunks):
            try:
                # Gerar embedding
                embedding = self.embedding_model.encode(
                    chunk.content, normalize_embeddings=True
                ).tolist()

                # Preparar payload
                payload = {
                    "content": chunk.content,
                    "source": chunk.source,
                    "chunk_id": chunk.chunk_id,
                    "chunk_type": chunk.chunk_type,
                    "metadata": chunk.metadata,
                }

                # Indexar no Qdrant
                self.client.upsert(  # type: ignore[attr-defined]
                    collection_name=collection_name,
                    points=[  # type: ignore[list-item]
                        {  # type: ignore[list-item]
                            "id": i,
                            "vector": embedding,
                            "payload": payload,
                        }
                    ],
                )

                indexed_count += 1

            except Exception as e:
                logger.warning(f"Erro ao indexar chunk {i}: {e}")

        # Atualizar status
        self.indexed_datasets[dataset_path] = True

        logger.info(f"Dataset indexado: {indexed_count}/{len(chunks)} chunks")

        return {
            "status": "success",
            "dataset_path": dataset_path,
            "collection_name": collection_name,
            "dataset_type": dataset_type,
            "total_chunks": len(chunks),
            "indexed_chunks": indexed_count,
        }

    def get_indexed_datasets(self) -> List[str]:
        """Lista datasets indexados."""
        return list(self.indexed_datasets.keys())

    def index_all_datasets(self, datasets_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Indexa todos os datasets disponíveis.

        Args:
            datasets_dir: Diretório com datasets (default: self.datasets_dir)

        Returns:
            Estatísticas de indexação
        """
        datasets_dir_path = Path(datasets_dir) if datasets_dir else self.datasets_dir

        if not datasets_dir_path.exists():
            logger.error(f"Diretório de datasets não encontrado: {datasets_dir_path}")
            return {"status": "error", "error": "Datasets directory not found"}

        results: Dict[str, Any] = {}
        total_chunks = 0

        # Encontrar todos os datasets
        dataset_files = []
        for item in datasets_dir_path.iterdir():
            if item.is_file() and item.suffix in [".json", ".txt", ".arrow"]:
                dataset_files.append(item)
            elif item.is_dir():
                # Buscar arquivos dentro do diretório
                for subitem in item.rglob("*"):
                    if subitem.is_file() and subitem.suffix in [".json", ".txt"]:
                        dataset_files.append(subitem)

        logger.info(f"Encontrados {len(dataset_files)} datasets para indexar")

        # Indexar cada dataset
        for dataset_file in dataset_files:
            try:
                result = self.index_dataset(str(dataset_file))
                results[str(dataset_file)] = result
                if result.get("status") == "success":
                    total_chunks += result.get("indexed_chunks", 0)
            except Exception as e:
                logger.error(f"Erro ao indexar {dataset_file}: {e}")
                results[str(dataset_file)] = {"status": "error", "error": str(e)}

        return {
            "status": "success",
            "total_datasets": len(dataset_files),
            "indexed_datasets": len([r for r in results.values() if r.get("status") == "success"]),
            "total_chunks": total_chunks,
            "results": results,
        }

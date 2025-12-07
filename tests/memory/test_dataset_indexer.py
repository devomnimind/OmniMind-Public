"""
Testes para DatasetIndexer.

Autor: Fabrício da Silva + assistência de IA
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.memory.dataset_indexer import DatasetIndexer


class TestDatasetIndexer:
    """Testes para DatasetIndexer."""

    def test_init(self):
        """Testa inicialização."""
        indexer = DatasetIndexer()
        assert indexer.datasets_dir == Path("data/datasets")
        assert len(indexer.dataset_collections) > 0

    def test_detect_dataset_type(self):
        """Testa detecção automática de tipo de dataset."""
        indexer = DatasetIndexer()

        # Testar diferentes tipos
        assert indexer._detect_dataset_type(Path("scientific_papers_arxiv")) == "scientific_papers"
        assert indexer._detect_dataset_type(Path("qasper_qa")) == "qa"
        assert indexer._detect_dataset_type(Path("human_vs_ai_code")) == "code_examples"
        assert indexer._detect_dataset_type(Path("dbpedia_ontology")) == "ontology"

    def test_chunk_by_type_scientific_papers(self):
        """Testa chunking de papers científicos."""
        indexer = DatasetIndexer()
        content = (
            "Abstract\n\n"
            "This is a longer abstract section with enough content to pass "
            "the validation threshold of 50 characters.\n\n"
            "Introduction\n\n"
            "This is the introduction section with sufficient text content "
            "to be considered a valid chunk for indexing purposes.\n\n"
            "Methods\n\n"
            "Methods section here with enough details and information to "
            "meet the minimum chunk size requirements."
        )

        chunks = indexer._chunk_by_type(content, "scientific_papers", chunk_size=500)

        assert len(chunks) > 0
        assert all(chunk.chunk_type == "section" for chunk in chunks)
        assert all(chunk.source == "scientific_papers_arxiv" for chunk in chunks)

    def test_chunk_by_type_qa(self):
        """Testa chunking de Q&A."""
        indexer = DatasetIndexer()
        content = (
            "Q: What is AI?\nA: Artificial Intelligence.\n\nQ: What is ML?\nA: Machine Learning."
        )

        chunks = indexer._chunk_by_type(content, "qa", chunk_size=500)

        assert len(chunks) > 0
        assert all(chunk.chunk_type == "qa_pair" for chunk in chunks)
        assert all("Q:" in chunk.content and "A:" in chunk.content for chunk in chunks)

    def test_chunk_by_type_generic(self):
        """Testa chunking genérico."""
        indexer = DatasetIndexer()
        content = " ".join(["word"] * 1000)  # 1000 palavras

        chunks = indexer._chunk_by_type(content, "generic", chunk_size=100)

        assert len(chunks) > 0
        assert all(chunk.chunk_type == "generic" for chunk in chunks)

    @patch("src.memory.dataset_indexer.QdrantClient")
    def test_ensure_collection(self, mock_qdrant_client):
        """Testa criação de coleção."""
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client

        # Mock collections
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client.get_collections.return_value = mock_collections

        indexer = DatasetIndexer()
        indexer.client = mock_client

        indexer._ensure_collection("test_collection")

        mock_client.create_collection.assert_called_once()

    def test_get_indexed_datasets(self):
        """Testa obtenção de datasets indexados."""
        indexer = DatasetIndexer()
        indexer.indexed_datasets["dataset1"] = True
        indexer.indexed_datasets["dataset2"] = True

        indexed = indexer.get_indexed_datasets()

        assert len(indexed) == 2
        assert "dataset1" in indexed
        assert "dataset2" in indexed

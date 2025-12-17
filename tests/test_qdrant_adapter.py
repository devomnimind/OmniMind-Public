from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.integrations.qdrant_adapter import (
    QdrantAdapter,
    QdrantAdapterError,
    QdrantConfig,
)


def test_qdrant_config_from_text_extracts_url_and_api_key() -> None:
    sample = 'qdrant_client = QdrantClient(\n    url="https://host:6333",\n    api_key="secret"\n)'
    config = QdrantConfig.from_text(sample)
    assert config is not None
    assert config.url == "https://host:6333"
    assert config.api_key == "secret"


def test_qdrant_upsert_vectors_requires_matching_lengths() -> None:
    config = QdrantConfig(url="http://localhost:6333")
    mock_client = MagicMock()
    mock_client.upsert.return_value = {"status": "ok"}
    with patch("src.integrations.qdrant_adapter.QdrantClient", return_value=mock_client):
        adapter = QdrantAdapter(config)
        with pytest.raises(QdrantAdapterError):
            adapter.upsert_vectors("cluster", [[0.1]], [1, 2])


def test_qdrant_search_calls_client_with_query_vector() -> None:
    config = QdrantConfig(url="http://localhost:6333")
    mock_client = MagicMock()
    fake_hit = MagicMock()
    fake_hit.dict.return_value = {"score": 1}
    mock_client.search.return_value = [fake_hit]
    with patch("src.integrations.qdrant_adapter.QdrantClient", return_value=mock_client):
        adapter = QdrantAdapter(config)
        results = adapter.search_vectors("cluster", [0.3, 0.7], top=3)
    assert isinstance(results, list)
    mock_client.search.assert_called()


def test_qdrant_list_collections_returns_names() -> None:
    config = QdrantConfig(url="http://localhost:6333")
    mock_client = MagicMock()
    fake_response = MagicMock()
    fake_collection = MagicMock()
    fake_collection.name = "example"
    fake_response.collections = [fake_collection]
    mock_client.get_collections.return_value = fake_response
    with patch("src.integrations.qdrant_adapter.QdrantClient", return_value=mock_client):
        adapter = QdrantAdapter(config)
        names = adapter.list_collections()
    assert names == ["example"]
